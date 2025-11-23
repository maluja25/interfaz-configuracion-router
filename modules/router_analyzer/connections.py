import platform
import subprocess
import time
import socket
import asyncio
from typing import Dict, Any, List
import re

try:
    import serial  # type: ignore
except Exception:
    serial = None  # type: ignore

try:
    import paramiko  # type: ignore
except Exception:
    paramiko = None  # type: ignore

try:
    import telnetlib3 as telnet3  # type: ignore
except Exception:
    telnet3 = None  # type: ignore

# Comandos por vendor para deshabilitar paginación
try:
    from .vendor_commands import DISABLE_PAGING  # type: ignore
except Exception:
    DISABLE_PAGING = {
        "huawei": ["screen-length 0 temporary"],
        "cisco": ["terminal length 0"],
        "juniper": ["set cli screen-length 0"],
    }

def _sanitize_output(text: str) -> str:
    """Limpia artefactos comunes de CLI: ANSI, paginación y backspaces.

    - Elimina secuencias ANSI (\x1b[...)
    - Resuelve backspaces (\b) aplicando borrado sobre un buffer
    - Quita textos de paginación como '--More--' y '---- More ----'
    """
    if not text:
        return ""
    # Quitar ANSI escape sequences
    text = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", text)
    # Resolver backspaces aplicando borrado
    buf: List[str] = []
    for ch in text:
        if ch == "\b":
            if buf:
                buf.pop()
        else:
            buf.append(ch)
    text = "".join(buf)
    # Quitar indicadores de paginación
    text = text.replace("--More--", "").replace("--more--", "")
    text = text.replace("---- More ----", "")
    return text


def _vendor_from_prompt(prompt: str) -> str:
    """Inferencia de fabricante basada en una sola línea de prompt.

    Reglas heurísticas simples:
    - Si aparecen palabras clave ('huawei', 'vrp', 'quidway') => Huawei
    - Si el prompt contiene 'usuario@host' con '>', '#', o '%' => Juniper
    - Si el prompt está entre '<...>' o '[...]' => Huawei (estilo VRP)
    - Si contiene '#', sin '@' => Cisco (modo privilegiado)
    - Si contiene '>', sin '@' => Cisco (modo exec)
    - En caso contrario => desconocido
    """
    t = _sanitize_output(prompt or "").strip()
    if not t:
        return "desconocido"
    low = t.lower()

    # Palabras clave explícitas
    if ("huawei" in low) or ("vrp" in low) or ("quidway" in low):
        return "huawei"

    # Estilo Juniper: user@host>, user@host#, user@host%
    if "@" in t and (">" in t or "#" in t or "%" in t):
        return "juniper"

    # Estilo Huawei VRP: <Huawei> o [Huawei] (o cualquier nombre entre <> o [])
    if re.search(r"[<\[][^>\]]+[>\]]", t):
        return "huawei"

    # Cisco típico: '#' privilegios, '>' modo exec (sin '@')
    if "#" in t and "@" not in t:
        return "cisco"
    if ">" in t and "@" not in t:
        return "cisco"

    return "desconocido"


# -------- Clases de conexión con manejo de paginación ---------
class SSHConnection:
    def __init__(self, connection_data: Dict[str, Any]):
        self.connection_data = connection_data
        self.host = connection_data.get("hostname", "")
        self.port = int(connection_data.get("port", 22) or 22)
        self.username = connection_data.get("username", "")
        self.password = connection_data.get("password", "")
        self.fast = bool(connection_data.get("fast_mode"))
        self.paging_disabled = bool(connection_data.get("paging_disabled"))
        self.verbose = bool(connection_data.get("verbose"))
        self.vendor = (connection_data.get("vendor_hint") or "").lower()

    def _disable_paging_once(self, client: Any) -> None:
        if self.paging_disabled:
            return
        try:
            vendor = (self.vendor or self.connection_data.get("vendor_hint") or "").lower()
            cmds = DISABLE_PAGING.get(vendor, []) if vendor else []
            for p_cmd in cmds:
                try:
                    _in, _out, _err = client.exec_command(p_cmd, timeout=3 if self.fast else 5)
                    _ = _out.read().decode(errors="ignore")
                    _ = _err.read().decode(errors="ignore")
                except Exception:
                    pass
        except Exception:
            pass
        self.paging_disabled = True
        self.connection_data["paging_disabled"] = True

    def run(self, cmd: str) -> str:
        if not self.host or paramiko is None:
            return ""
        try:
            cmd_timeout = 1.8 if self.fast else 3
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(self.host, port=self.port, username=self.username or None, password=self.password or None,
                           look_for_keys=False, allow_agent=False, timeout=cmd_timeout)
            # Deshabilitar paginación solo si es necesario (comandos largos)
            if bool(self.connection_data.get("need_paging_disabled")):
                self._disable_paging_once(client)
            # Ejecutar comando
            stdin, stdout, stderr = client.exec_command(cmd, timeout=cmd_timeout)
            out = stdout.read().decode(errors="ignore") + stderr.read().decode(errors="ignore")
            client.close()
            return _sanitize_output(out)
        except Exception as e:
            print(f"[SSH] Error ejecutando '{cmd}': {e}")
            return ""

    def run_batch(self, commands: List[str]) -> List[str]:
        """Ejecuta múltiples comandos reutilizando una sola sesión SSH.

        Minimiza handshakes y reduce la latencia total.
        """
        outputs: List[str] = []
        if not self.host or paramiko is None:
            return outputs
        try:
            # Establecer cliente y abrir shell interactivo para batch
            cmd_timeout = 4 if self.fast else 6
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(self.host, port=self.port, username=self.username or None, password=self.password or None,
                           look_for_keys=False, allow_agent=False, timeout=cmd_timeout)

            chan = client.invoke_shell()
            # Pequeña espera para recibir prompt inicial
            time.sleep(0.20 if self.fast else 0.30)

            def _looks_like_prompt(line: str) -> bool:
                t = (line or "").strip()
                if not t:
                    return False
                if re.search(r"[<\[][^^\]>]+[>\]]\s*$", t):
                    return True
                if ("@" in t) and (t.endswith("#") or t.endswith(">") or t.endswith("%")):
                    return True
                if (t.endswith("#") or t.endswith(">")) and ("@" not in t):
                    return True
                return False

            def _read_until_idle(idle_window: float, hard_timeout: float) -> str:
                start = time.time()
                last = start
                buf = ""
                carry = ""
                while True:
                    now = time.time()
                    if (now - start) > hard_timeout:
                        break
                    if (now - last) > idle_window:
                        break
                    try:
                        if chan.recv_ready():
                            part = chan.recv(512).decode(errors="ignore")
                        else:
                            part = ""
                    except Exception:
                        part = ""
                    if part:
                        last = now
                        low = part.lower()
                        if "--more--" in low or " ---- more ---- " in low or "---- more ----" in low:
                            try:
                                chan.send(" ")
                            except Exception:
                                pass
                            time.sleep(0.08 if self.fast else 0.12)
                            part = part.replace("--More--", "").replace("--more--", "").replace("---- More ----", "")
                        buf += part
                        carry += part
                        while "\n" in carry:
                            line, carry = carry.split("\n", 1)
                            if self.verbose:
                                print(f"[SSH] {line}")
                    else:
                        time.sleep(0.06 if self.fast else 0.1)
                if carry and self.verbose:
                    print(f"[SSH] {carry}")
                return buf

            def _strip_echo_and_prompt(text: str, cmd: str) -> str:
                t = text.replace("\r", "")
                lines = t.splitlines()
                c = (cmd or "").strip().lower()
                out_lines: List[str] = []
                skipped_echo = False
                for ln in lines:
                    if not skipped_echo and c and ln.strip().lower().startswith(c):
                        skipped_echo = True
                        continue
                    out_lines.append(ln)
                while out_lines and not out_lines[-1].strip():
                    out_lines.pop()
                if out_lines and _looks_like_prompt(out_lines[-1]):
                    out_lines.pop()
                return "\n".join(out_lines)

            def _disable_paging_shell() -> None:
                if self.paging_disabled:
                    return
                try:
                    vendor = (self.vendor or self.connection_data.get("vendor_hint") or "").lower()
                    cmds = DISABLE_PAGING.get(vendor, []) if vendor else []
                    for p_cmd in cmds:
                        try:
                            chan.send(p_cmd + "\n")
                            time.sleep(0.18 if self.fast else 0.28)
                            _ = _read_until_idle(idle_window=0.6 if self.fast else 0.8, hard_timeout=1.2 if self.fast else 1.6)
                        except Exception:
                            pass
                    # Drenar restos
                    _ = _read_until_idle(idle_window=0.5 if self.fast else 0.7, hard_timeout=1.0 if self.fast else 1.2)
                except Exception:
                    pass
                self.paging_disabled = True
                self.connection_data["paging_disabled"] = True

            # Deshabilitar paginación si hay comandos largos o está solicitado
            long_in_batch = any(any(t in (c or "").lower() for t in ("running-config", "current-configuration", "show configuration")) for c in commands)
            if bool(self.connection_data.get("need_paging_disabled")) or long_in_batch:
                _disable_paging_shell()

            # Ejecutar comandos en el shell
            for cmd in commands:
                try:
                    chan.send("\n")
                    time.sleep(0.10 if self.fast else 0.15)
                    chan.send(cmd + "\n")
                    time.sleep(0.12 if self.fast else 0.2)
                    idle = 0.8 if self.fast else 1.1
                    is_long = any(s in (cmd or "").lower() for s in ("running-config", "current-configuration", "show configuration"))
                    hard = ((16.0 if self.fast else 20.0) if is_long else (8.0 if self.fast else 10.0))
                    raw = _read_until_idle(idle_window=idle, hard_timeout=hard)
                    outputs.append(_strip_echo_and_prompt(_sanitize_output(raw), cmd))
                except Exception as e:
                    print(f"[SSH] Error ejecutando '{cmd}' en batch: {e}")
                    outputs.append("")

            try:
                chan.close()
            except Exception:
                pass
            try:
                client.close()
            except Exception:
                pass
            return outputs
        except Exception as e:
            print(f"[SSH] Error en run_batch: {e}")
            return outputs


class TelnetConnection:
    def __init__(self, connection_data: Dict[str, Any], vendor: str = ""):
        self.connection_data = connection_data
        self.host = connection_data.get("hostname", "")
        self.port = int(connection_data.get("port", 23) or 23)
        self.username = connection_data.get("username", "")
        self.password = connection_data.get("password", "")
        self.fast = bool(connection_data.get("fast_mode"))
        self.paging_disabled = bool(connection_data.get("paging_disabled"))
        self.vendor = vendor.lower() if vendor else ""
        self.verbose = bool(connection_data.get("verbose"))

    async def _read_for(self, reader: Any, seconds: float = 1.0) -> str:
        end = time.monotonic() + seconds
        buf = ""
        while time.monotonic() < end:
            try:
                part = await asyncio.wait_for(reader.read(256), timeout=0.20 if self.fast else 0.25)
            except Exception:
                part = ""
            if part:
                buf += part
            else:
                await asyncio.sleep(0.06 if self.fast else 0.1)
        return buf

    async def _disable_paging_once(self, reader: Any, writer: Any) -> None:
        if self.paging_disabled:
            return
        try:
            ven = self.vendor or (self.connection_data.get("vendor_hint") or "").lower()
            cmds = DISABLE_PAGING.get(ven, []) if ven else []
            for p_cmd in cmds:
                try:
                    writer.write(p_cmd + "\r\n")
                    await asyncio.sleep(0.18 if self.fast else 0.28)
                    _ = await self._read_for(reader, 0.9 if self.fast else 1.2)
                except Exception:
                    pass
            # Drenar posibles restos para que no contaminen el siguiente comando
            _ = await self._read_for(reader, 0.5 if self.fast else 0.7)
        except Exception:
            pass
        self.paging_disabled = True
        self.connection_data["paging_disabled"] = True

    def _looks_like_prompt(self, line: str) -> bool:
        t = (line or "").strip()
        if not t:
            return False
        if re.search(r"[<\[][^^\]>]+[>\]]\s*$", t):
            return True
        if ("@" in t) and (t.endswith("#") or t.endswith(">") or t.endswith("%")):
            return True
        if (t.endswith("#") or t.endswith(">")) and ("@" not in t):
            return True
        return False

    async def _read_until_idle(self, reader: Any, writer: Any, idle_window: float, hard_timeout: float) -> str:
        start = time.monotonic()
        last = start
        buf = ""
        carry = ""
        while True:
            if (time.monotonic() - start) > hard_timeout:
                break
            if (time.monotonic() - last) > idle_window:
                break
            try:
                part = await asyncio.wait_for(reader.read(512), timeout=0.25)
            except Exception:
                part = ""
            if part:
                last = time.monotonic()
                low = part.lower()
                if "--more--" in low or " ---- more ---- " in low or "---- more ----" in low:
                    try:
                        writer.write(" ")
                    except Exception:
                        pass
                    await asyncio.sleep(0.08 if self.fast else 0.12)
                    part = part.replace("--More--", "").replace("--more--", "").replace("---- More ----", "")
                buf += part
                carry += part
                while "\n" in carry:
                    line, carry = carry.split("\n", 1)
                    if self.verbose:
                        print(f"[Telnet3] {line}")
            else:
                await asyncio.sleep(0.06 if self.fast else 0.1)
        if carry and self.verbose:
            print(f"[Telnet3] {carry}")
        return buf

    def _strip_echo_and_prompt(self, text: str, cmd: str) -> str:
        t = text.replace("\r", "")
        lines = t.splitlines()
        # quitar eco del comando
        c = (cmd or "").strip().lower()
        out_lines: List[str] = []
        skipped_echo = False
        for ln in lines:
            if not skipped_echo and c and ln.strip().lower().startswith(c):
                skipped_echo = True
                continue
            out_lines.append(ln)
        # quitar prompt final si lo hay
        while out_lines and not out_lines[-1].strip():
            out_lines.pop()
        if out_lines and self._looks_like_prompt(out_lines[-1]):
            out_lines.pop()
        return "\n".join(out_lines)

    async def _run_async(self, cmd: str) -> str:
        if not self.host or telnet3 is None:
            return ""
        reader, writer = await telnet3.open_connection(host=self.host, port=self.port, encoding="utf8", shell=None)

        # Autenticación si el servidor lo solicita
        banner = await self._read_for(reader, 0.6 if self.fast else 0.7)
        low = banner.lower()
        if any(x in low for x in ("username:", "user name:", "login:")):
            if not self.username:
                if self.verbose:
                    print("[Telnet3] Autenticación requerida, falta 'username'.")
                try:
                    writer.close()
                except Exception:
                    pass
                return ""
            writer.write(self.username + "\r\n")
            await asyncio.sleep(0.25 if self.fast else 0.35)
            after_user = await self._read_for(reader, 0.6 if self.fast else 0.7)
            low2 = (banner + after_user).lower()
            if ("password:" in low2 or "pass word:" in low2):
                if not self.password:
                    if self.verbose:
                        print("[Telnet3] Se solicitó password, pero no fue provisto.")
                    try:
                        writer.close()
                    except Exception:
                        pass
                    return ""
                writer.write(self.password + "\r\n")
                await asyncio.sleep(0.4 if self.fast else 0.5)
                _ = await self._read_for(reader, 0.8 if self.fast else 0.9)

        # Asegurar prompt y modo enable para Cisco
        writer.write("\r\n")
        await asyncio.sleep(0.10 if self.fast else 0.18)
        prompt_text = await self._read_for(reader, 0.5 if self.fast else 0.6)
        if self.vendor == "cisco":
            snapshot = (banner + prompt_text).lower()
            if "#" not in snapshot:
                writer.write("\r\n")
                await asyncio.sleep(0.1)
                writer.write("enable\r\n")
                await asyncio.sleep(0.3)
                resp = await self._read_for(reader, 0.8)
                if "password" in resp.lower():
                    en_pw = self.connection_data.get("enable_password") or self.password
                    if en_pw:
                        writer.write(en_pw + "\r\n")
                        await asyncio.sleep(0.6)
                        _ = await self._read_for(reader, 1.0)

        # Evaluar si el comando es largo y si necesitamos deshabilitar paginación
        long_cmd = any(s in cmd.lower() for s in (
            "running-config", "current-configuration", "show configuration"
        ))
        need_paging_disabled = bool(self.connection_data.get("need_paging_disabled"))
        if need_paging_disabled or long_cmd:
            await self._disable_paging_once(reader, writer)
            _ = await self._read_for(reader, 0.3 if self.fast else 0.5)

        # Enviar comando y leer salida con manejo de '--More--'
        writer.write("\r\n")
        await asyncio.sleep(0.1 if self.fast else 0.15)
        writer.write(cmd + "\r\n")
        await asyncio.sleep(0.12 if self.fast else 0.2)
        idle = 0.8 if self.fast else 1.1
        hard = (8.0 if self.fast else 10.0) if not long_cmd else (16.0 if self.fast else 20.0)
        raw = await self._read_until_idle(reader, writer, idle_window=idle, hard_timeout=hard)
        try:
            writer.close()
        except Exception:
            pass
        cleaned = _sanitize_output(raw)
        return self._strip_echo_and_prompt(cleaned, cmd)

    def run(self, cmd: str) -> str:
        try:
            return asyncio.run(self._run_async(cmd))
        except Exception as e:
            print(f"[Telnet3] Error ejecutando '{cmd}': {e}")
            return ""

    async def _run_batch_async(self, commands: List[str]) -> List[str]:
        outputs: List[str] = []
        if not self.host or telnet3 is None:
            return outputs
        reader, writer = await telnet3.open_connection(host=self.host, port=self.port, encoding="utf8", shell=None)

        # Autenticación si el servidor lo solicita
        banner = await self._read_for(reader, 0.8)
        low = banner.lower()
        if any(x in low for x in ("username:", "user name:", "login:")):
            if not self.username:
                if self.verbose:
                    print("[Telnet3] Autenticación requerida, falta 'username'.")
                try:
                    writer.close()
                except Exception:
                    pass
                return outputs
            writer.write(self.username + "\r\n")
            await asyncio.sleep(0.4)
            after_user = await self._read_for(reader, 0.8)
            low2 = (banner + after_user).lower()
            if ("password:" in low2 or "pass word:" in low2):
                if not self.password:
                    if self.verbose:
                        print("[Telnet3] Se solicitó password, pero no fue provisto.")
                    try:
                        writer.close()
                    except Exception:
                        pass
                    return outputs
                writer.write(self.password + "\r\n")
                await asyncio.sleep(0.45 if self.fast else 0.55)
                _ = await self._read_for(reader, 0.8 if self.fast else 0.9)

        # Asegurar prompt y modo enable para Cisco
        writer.write("\r\n")
        await asyncio.sleep(0.10 if self.fast else 0.18)
        prompt_text = await self._read_for(reader, 0.5 if self.fast else 0.6)
        if self.vendor == "cisco":
            snapshot = (banner + prompt_text).lower()
            if "#" not in snapshot:
                writer.write("\r\n")
                await asyncio.sleep(0.1)
                writer.write("enable\r\n")
                await asyncio.sleep(0.3)
                resp = await self._read_for(reader, 0.8)
                if "password" in resp.lower():
                    en_pw = self.connection_data.get("enable_password") or self.password
                    if en_pw:
                        writer.write(en_pw + "\r\n")
                        await asyncio.sleep(0.6)
                        _ = await self._read_for(reader, 1.0)

        # Evaluar si hay comandos largos
        long_in_batch = any(any(s in (c or "").lower() for s in ("running-config", "current-configuration", "show configuration")) for c in commands)
        need_paging_disabled = bool(self.connection_data.get("need_paging_disabled"))
        if need_paging_disabled or long_in_batch:
            await self._disable_paging_once(reader, writer)
            _ = await self._read_for(reader, 0.3 if self.fast else 0.5)

        # Ejecutar cada comando con manejo de '--More--'
        for cmd in commands:
            try:
                writer.write("\r\n")
                await asyncio.sleep(0.1 if self.fast else 0.15)
                writer.write(cmd + "\r\n")
                await asyncio.sleep(0.12 if self.fast else 0.2)
                idle = 0.8 if self.fast else 1.1
                # Extender timeout duro para comandos largos (running-config / current-configuration / show configuration)
                is_long = any(s in (cmd or "").lower() for s in ("running-config", "current-configuration", "show configuration"))
                hard = ((16.0 if self.fast else 20.0) if is_long else (8.0 if self.fast else 10.0))
                raw = await self._read_until_idle(reader, writer, idle_window=idle, hard_timeout=hard)
                cleaned = _sanitize_output(raw)
                outputs.append(self._strip_echo_and_prompt(cleaned, cmd))
            except Exception as e:
                print(f"[Telnet3] Error ejecutando '{cmd}' en batch: {e}")
                outputs.append("")

        try:
            writer.close()
        except Exception:
            pass
        return outputs

    def run_batch(self, commands: List[str]) -> List[str]:
        try:
            return asyncio.run(self._run_batch_async(commands))
        except Exception as e:
            print(f"[Telnet3] Error en run_batch: {e}")
            return []


class SerialConnection:
    def __init__(self, connection_data: Dict[str, Any]):
        self.connection_data = connection_data
        self.port = connection_data.get("port", "")
        self.username = connection_data.get("username", "")
        self.password = connection_data.get("password", "")
        self.baudrate = int(connection_data.get("baudrate", 9600) or 9600)
        self.fast = bool(connection_data.get("fast_mode"))

    def _read_chunk(self, ser: Any, duration: float = 0.8) -> str:
        end = time.time() + duration
        buf = ""
        while time.time() < end:
            try:
                data = ser.read(512)
            except Exception:
                data = b""
            if data:
                buf += data.decode(errors="ignore")
            else:
                time.sleep(0.06 if self.fast else 0.1)
        return buf

    def run(self, cmd: str) -> str:
        if not self.port or serial is None:
            return ""
        try:
            with serial.Serial(port=self.port, baudrate=self.baudrate, timeout=1.0 if self.fast else 1.5) as ser:
                try:
                    ser.reset_input_buffer()
                    ser.reset_output_buffer()
                except Exception:
                    pass
                time.sleep(0.15 if self.fast else 0.2)
                ser.write(b"\r")
                time.sleep(0.4 if self.fast else 0.6)

                # Autenticación si el equipo la solicita
                welcome = self._read_chunk(ser, 0.7 if self.fast else 1.0).lower()
                if any(x in welcome for x in ("username:", "user name:", "login:", "login authentication")):
                    if self.username:
                        ser.write((self.username + "\r").encode())
                        time.sleep(0.4 if self.fast else 0.6)
                        _ = self._read_chunk(ser, 0.8 if self.fast else 1.0)
                    if self.password:
                        ser.write((self.password + "\r").encode())
                        time.sleep(0.8 if self.fast else 1.0)
                        _ = self._read_chunk(ser, 0.9 if self.fast else 1.2)

                # Enviar comando
                ser.write((cmd + "\r").encode())
                long_cmd = any(s in cmd.lower() for s in (
                    "running-config", "current-configuration", "show configuration"
                ))
                time.sleep((0.8 if self.fast else 1.2) if long_cmd else (1.0 if self.fast else 1.5))

                out = ""
                idle_loops = 0
                # Leer continuamente; si aparece '--More--', enviar espacio
                # y continuar acumulando hasta que no haya más datos.
                while True:
                    part = self._read_chunk(ser, 0.8 if self.fast else 1.0)
                    if part:
                        low = part.lower()
                        if "--more--" in low or "---- more ----" in low or " more " in low:
                            try:
                                ser.write(b" ")
                            except Exception:
                                pass
                            time.sleep(0.08 if self.fast else 0.12)
                            # Limpiar artefactos
                            part = part.replace("--More--", "").replace("--more--", "").replace("---- More ----", "")
                            idle_loops = 0
                        out += part
                        idle_loops = 0
                    else:
                        idle_loops += 1
                        if idle_loops >= (6 if self.fast else 8):
                            break
                        time.sleep(0.06 if self.fast else 0.1)

                return _sanitize_output(out)
        except Exception as e:
            print(f"[Serial] Error ejecutando '{cmd}': {e}")
            return ""

def ping_host(hostname: str, count: int = 2, timeout_ms: int = 1000) -> bool:
    if not hostname:
        return False
    system = platform.system().lower()
    if "windows" in system:
        cmd = ["ping", "-n", str(count), "-w", str(timeout_ms), hostname]
    else:
        timeout_s = max(1, int(timeout_ms / 1000))
        cmd = ["ping", "-c", str(count), "-W", str(timeout_s), hostname]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        return result.returncode == 0
    except Exception:
        return False


def quick_tcp_check(host: str, port: int, timeout_s: float = 0.7) -> bool:
    """Conexión TCP rápida para verificar alcanzabilidad del servicio.

    Es más veloz que invocar utilidades del sistema como 'ping' y suficiente
    para confirmar si el puerto objetivo está disponible.
    """
    if not host or not port:
        return False
    try:
        with socket.create_connection((host, port), timeout=timeout_s):
            return True
    except Exception:
        return False


def check_serial_port(port: str, baudrate: int = 9600, timeout: float = 1.0, *, verbose: bool = False, fast: bool = False) -> bool:
    """Intenta abrir un puerto serial y reporta diagnóstico opcional.

    - Devuelve True si pudo abrir y cerrar el puerto correctamente.
    - Con ``verbose=True`` imprime el motivo del fallo y sugiere puertos disponibles.
    """
    if not port:
        if verbose:
            print("[Serial] No se proporcionó un puerto (ej. COM3/COM7).")
        return False
    if serial is None:
        if verbose:
            print("[Serial] pyserial no está instalado. Instala con: pip install pyserial")
        return False
    try:
        ser = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
        # Pequeña espera para estabilizar
        time.sleep(0.08 if fast else 0.12)
        ok = bool(ser.is_open)
        try:
            ser.close()
        except Exception:
            pass
        if ok and verbose:
            print(f"[Serial] Puerto {port} abierto correctamente a {baudrate} baudios.")
        return ok
    except Exception as e:
        if verbose:
            print(f"[Serial] No se pudo abrir {port} @ {baudrate}: {e}")
            # Intentar listar puertos disponibles para ayudar al usuario
            try:
                from serial.tools import list_ports  # type: ignore
                ports = list(list_ports.comports())
                if ports:
                    listado = ", ".join(p.device for p in ports)
                    print(f"[Serial] Puertos detectados: {listado}")
                else:
                    print("[Serial] No se detectan puertos seriales en el sistema.")
            except Exception as le:
                print(f"[Serial] No se pudo listar puertos: {le}")
        return False


# -------- SSH ---------
def run_ssh_command(connection_data: Dict[str, Any], cmd: str) -> str:
    return SSHConnection(connection_data).run(cmd)


# -------- Telnet (telnetlib3) ---------
def run_telnet_command(connection_data: Dict[str, Any], cmd: str, vendor: str = "") -> str:
    return TelnetConnection(connection_data, vendor).run(cmd)


# -------- Serial ---------
def run_serial_command(connection_data: Dict[str, Any], cmd: str) -> str:
    return SerialConnection(connection_data).run(cmd)


# ---- Ejecutores en lote ----
def run_ssh_commands_batch(connection_data: Dict[str, Any], cmds: List[str]) -> List[str]:
    return SSHConnection(connection_data).run_batch(cmds)


def run_telnet_commands_batch(connection_data: Dict[str, Any], cmds: List[str], vendor: str = "") -> List[str]:
    return TelnetConnection(connection_data, vendor).run_batch(cmds)


def run_serial_commands_batch(connection_data: Dict[str, Any], cmds: List[str]) -> List[str]:
    outputs: List[str] = []
    sc = SerialConnection(connection_data)
    for c in cmds:
        outputs.append(sc.run(c))
    return outputs


# -------- Vendor detection ---------
def detect_vendor_ssh(connection_data: Dict[str, Any]) -> str:
    host = connection_data.get("hostname", "")
    port = int(connection_data.get("port", 22) or 22)
    username = connection_data.get("username", "")
    password = connection_data.get("password", "")
    fast = bool(connection_data.get("fast_mode"))
    verbose = bool(connection_data.get("verbose"))
    if not host or paramiko is None:
        return "desconocido"
    try:
        if verbose:
            print(f"[SSH] Conectando a {host}:{port} para leer prompt...")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, port=port, username=username or None, password=password or None,
                       look_for_keys=False, allow_agent=False, timeout=3 if fast else 5)
        chan = client.invoke_shell()
        time.sleep(0.2 if fast else 0.3)
        try:
            chan.send("\n")
        except Exception:
            pass
        time.sleep(0.4 if fast else 0.6)
        buf = ""
        end = time.time() + (0.9 if fast else 1.2)
        while time.time() < end:
            try:
                if chan.recv_ready():
                    part = chan.recv(512).decode(errors="ignore")
                else:
                    part = ""
            except Exception:
                part = ""
            if part:
                buf += part
            else:
                time.sleep(0.08 if fast else 0.12)
        if verbose:
            print("[SSH] Salida inicial/prompt:")
            for line in buf.splitlines()[:20]:
                print(f"[SSH] {line}")
        prompt_line = ""
        for pl in reversed(buf.splitlines()):
            pl = pl.strip()
            if pl:
                prompt_line = pl
                break
        vendor = _vendor_from_prompt(prompt_line)
        try:
            client.close()
        except Exception:
            pass
        return vendor
    except Exception as e:
        print(f"[SSH] Error en detección de vendor: {e}")
        return "desconocido"


def detect_vendor_telnet(connection_data: Dict[str, Any]) -> str:
    host = connection_data.get("hostname", "")
    port = int(connection_data.get("port", 23) or 23)
    username = connection_data.get("username", "")
    password = connection_data.get("password", "")
    fast = bool(connection_data.get("fast_mode"))
    verbose = bool(connection_data.get("verbose"))
    if not host or telnet3 is None:
        return "desconocido"
    try:
        async def _detect() -> str:
            if verbose:
                print(f"[Telnet3] Conectando a {host}:{port}...")
            reader, writer = await telnet3.open_connection(host=host, port=port, encoding="utf8", shell=None)

            async def _read_for(seconds: float = 1.0) -> str:
                end = time.monotonic() + seconds
                buf = ""
                while time.monotonic() < end:
                    try:
                        part = await asyncio.wait_for(reader.read(1024), timeout=0.20 if fast else 0.25)
                    except Exception:
                        part = ""
                    if part:
                        buf += part
                    else:
                        await asyncio.sleep(0.06 if fast else 0.1)
                return buf

            out_all = await _read_for(0.9 if fast else 1.2)
            if verbose:
                print("[Telnet3] Bienvenida/prompt:")
                for line in out_all.splitlines()[:20]:
                    print(f"[Telnet3] {line}")

            async def _clear_more(text: str) -> str:
                tries = 12
                accum = text
                while tries > 0 and "---- More ----" in accum:
                    writer.write(" ")
                    await asyncio.sleep(0.15)
                    accum += await _read_for(0.6)
                    tries -= 1
                return accum

            out_all = await _clear_more(out_all)
            low = out_all.lower()
            if any(p in low for p in ("username:", "user name:", "login:")):
                if not username:
                    if verbose:
                        print("[Telnet3] Autenticación requerida, pero falta 'username'.")
                    try:
                        writer.close()
                    except Exception:
                        pass
                    return "desconocido"
                writer.write(username + "\r\n")
                await asyncio.sleep(0.2 if fast else 0.3)
                out_all += await _read_for(0.6 if fast else 0.8)
                low = out_all.lower()
                if ("password:" in low or "pass word:" in low):
                    if not password:
                        if verbose:
                            print("[Telnet3] Se solicitó password, pero no fue provisto.")
                        try:
                            writer.close()
                        except Exception:
                            pass
                        return "desconocido"
                writer.write(password + "\r\n")
                await asyncio.sleep(0.4 if fast else 0.6)
                out_all += await _read_for(0.8 if fast else 1.0)

            writer.write("\r\n")
            await asyncio.sleep(0.15 if fast else 0.2)
            out_all += await _read_for(0.6 if fast else 0.8)
            out_all = await _clear_more(out_all)

            prompt_text = ""
            for pl in reversed(out_all.splitlines()):
                pl = pl.strip()
                if pl:
                    prompt_text = pl
                    break
            vendor_found = _vendor_from_prompt(prompt_text)

            try:
                writer.close()
            except Exception:
                pass
            return vendor_found

        return asyncio.run(_detect())
    except Exception as e:
        if verbose:
            print(f"[Telnet3] Error en detección de vendor: {e}")
        return "desconocido"


def detect_vendor_serial(connection_data: Dict[str, Any]) -> str:
    port = connection_data.get("port", "")
    username = connection_data.get("username", "")
    password = connection_data.get("password", "")
    baudrate = int(connection_data.get("baudrate", 9600) or 9600)
    fast = bool(connection_data.get("fast_mode"))
    verbose = bool(connection_data.get("verbose"))
    if not port or serial is None:
        return "desconocido"
    try:
        if verbose:
            print(f"[Serial] Leyendo prompt en {port}...")
        with serial.Serial(port=port, baudrate=baudrate, timeout=1.0 if fast else 1.5) as ser:
            try:
                ser.reset_input_buffer()
                ser.reset_output_buffer()
            except Exception:
                pass
            time.sleep(0.15 if fast else 0.2)
            ser.write(b"\r")
            time.sleep(0.4 if fast else 0.6)

            def _read_chunk(duration: float = 0.8) -> str:
                end = time.time() + duration
                buf = ""
                while time.time() < end:
                    try:
                        data = ser.read(512)
                    except Exception:
                        data = b""
                    if data:
                        buf += data.decode(errors="ignore")
                    else:
                        time.sleep(0.1)
                return buf

            # Intentar autenticación si el equipo la solicita
            welcome = _read_chunk(0.7 if fast else 1.0)
            wl = welcome.lower()
            for _ in range(3):
                if any(x in wl for x in ("username:", "user name:", "login:", "login authentication")):
                    if username:
                        print(f"[Serial] Respondiendo usuario")
                        ser.write((username + "\r").encode())
                        time.sleep(0.4 if fast else 0.6)
                        resp = _read_chunk(0.9 if fast else 1.2)
                        wl = resp.lower()
                    else:
                        break
                if "password:" in wl:
                    if password:
                        print(f"[Serial] Respondiendo contraseña")
                        ser.write((password + "\r").encode())
                        time.sleep(0.9 if fast else 1.2)
                        resp = _read_chunk(1.1 if fast else 1.5)
                        wl = resp.lower()
                    else:
                        break
                # Si ya no vemos prompts de login, salir
                if not any(x in wl for x in ("username:", "user name:", "login:", "password:")):
                    break

            # Leer prompt final tras un retorno de carro
            ser.write(b"\r")
            time.sleep(0.5 if fast else 0.7)
            out = _read_chunk(1.0 if fast else 1.3)
            if verbose:
                print("[Serial] Salida inicial/prompt:")
                for line in out.splitlines()[:20]:
                    print(f"[Serial] {line}")
            prompt_text = ""
            for pl in reversed(out.splitlines()):
                pl = pl.strip()
                if pl:
                    prompt_text = pl
                    break
            return _vendor_from_prompt(prompt_text)
    except Exception as e:
        if verbose:
            print(f"[Serial] Error en detección de vendor: {e}")
        return "desconocido"
    except Exception as e:
        print(f"[Serial] Error en detección de vendor: {e}")
        return "desconocido"
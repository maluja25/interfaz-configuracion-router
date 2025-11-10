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

    def _disable_paging_once(self, client: Any) -> None:
        if self.paging_disabled:
            return
        try:
            # Huawei: deshabilitar paginación en VTY; ignorar errores
            stdin, stdout, stderr = client.exec_command("screen-length 0 temporary", timeout=3 if self.fast else 5)
            _ = stdout.read().decode(errors="ignore")
            err = stderr.read().decode(errors="ignore").lower()
            # Cisco opcional: terminal length 0
            # Ejecutamos también para mayor compatibilidad; ignorar errores
            stdin2, stdout2, stderr2 = client.exec_command("terminal length 0", timeout=3 if self.fast else 5)
            _ = stdout2.read().decode(errors="ignore")
            err2 = stderr2.read().decode(errors="ignore").lower()
            # Ignorar mensajes como "must be VTY" o "VTY"
            _ = err, err2
        except Exception:
            pass
        self.paging_disabled = True
        self.connection_data["paging_disabled"] = True

    def run(self, cmd: str) -> str:
        if not self.host or paramiko is None:
            return ""
        try:
            cmd_timeout = 3 if self.fast else 5
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(self.host, port=self.port, username=self.username or None, password=self.password or None,
                           look_for_keys=False, allow_agent=False, timeout=cmd_timeout)
            # Deshabilitar paginación una sola vez por sesión
            self._disable_paging_once(client)
            # Ejecutar comando
            stdin, stdout, stderr = client.exec_command(cmd, timeout=cmd_timeout)
            out = stdout.read().decode(errors="ignore") + stderr.read().decode(errors="ignore")
            client.close()
            return _sanitize_output(out)
        except Exception as e:
            print(f"[SSH] Error ejecutando '{cmd}': {e}")
            return ""


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
            # Huawei: VTY
            writer.write("screen-length 0 temporary\r")
            await asyncio.sleep(0.15 if self.fast else 0.25)
            _ = await self._read_for(reader, 0.6 if self.fast else 0.8)
            # Cisco opcional
            writer.write("terminal length 0\r")
            await asyncio.sleep(0.15 if self.fast else 0.25)
            _ = await self._read_for(reader, 0.6 if self.fast else 0.8)
        except Exception:
            pass
        self.paging_disabled = True
        self.connection_data["paging_disabled"] = True

    async def _run_async(self, cmd: str) -> str:
        if not self.host or telnet3 is None:
            return ""
        reader, writer = await telnet3.open_connection(host=self.host, port=self.port, encoding="utf8", shell=None)

        # Autenticación si el servidor lo solicita
        banner = await self._read_for(reader, 0.8)
        low = banner.lower()
        if any(x in low for x in ("username:", "user name:", "login:")):
            if not self.username:
                print("[Telnet3] Autenticación requerida, falta 'username'.")
                try:
                    writer.close()
                except Exception:
                    pass
                return ""
            writer.write(self.username + "\r\n")
            await asyncio.sleep(0.4)
            after_user = await self._read_for(reader, 0.8)
            low2 = (banner + after_user).lower()
            if ("password:" in low2 or "pass word:" in low2):
                if not self.password:
                    print("[Telnet3] Se solicitó password, pero no fue provisto.")
                    try:
                        writer.close()
                    except Exception:
                        pass
                    return ""
                writer.write(self.password + "\r\n")
                await asyncio.sleep(0.6)
                _ = await self._read_for(reader, 1.0)

        # Asegurar prompt y modo enable para Cisco
        writer.write("\r")
        await asyncio.sleep(0.12 if self.fast else 0.2)
        prompt_text = await self._read_for(reader, 0.6)
        if self.vendor == "cisco":
            snapshot = (banner + prompt_text).lower()
            if "#" not in snapshot:
                writer.write("\r")
                await asyncio.sleep(0.1)
                writer.write("enable\r")
                await asyncio.sleep(0.3)
                resp = await self._read_for(reader, 0.8)
                if "password" in resp.lower():
                    en_pw = self.connection_data.get("enable_password") or self.password
                    if en_pw:
                        writer.write(en_pw + "\r")
                        await asyncio.sleep(0.6)
                        _ = await self._read_for(reader, 1.0)

        # Deshabilitar paginación una sola vez por sesión
        await self._disable_paging_once(reader, writer)

        # Enviar comando y leer salida con manejo de '--More--'
        writer.write("\r")
        await asyncio.sleep(0.1 if self.fast else 0.15)
        writer.write(cmd + "\r")
        await asyncio.sleep(0.12 if self.fast else 0.2)
        long_cmd = any(s in cmd.lower() for s in (
            "running-config", "current-configuration", "show configuration"
        ))
        end = time.monotonic() + ((3.5 if self.fast else 6.0) if long_cmd else (1.2 if self.fast else 1.8))
        out = ""
        carry = ""
        while time.monotonic() < end:
            try:
                part = await asyncio.wait_for(reader.read(256), timeout=0.20 if self.fast else 0.25)
            except Exception:
                part = ""
            if part:
                lower = part.lower()
                if "--more--" in lower or " ---- more ---- " in lower or "---- more ----" in lower:
                    try:
                        writer.write(" ")
                    except Exception:
                        pass
                    await asyncio.sleep(0.08 if self.fast else 0.12)
                    end = time.monotonic() + (2.0 if self.fast else 3.0)
                    part = part.replace("--More--", "").replace("--more--", "").replace("---- More ----", "")
                out += part
                carry += part
                while "\n" in carry:
                    line, carry = carry.split("\n", 1)
                    print(f"[Telnet3] {line}")
            else:
                await asyncio.sleep(0.06 if self.fast else 0.1)
        if carry:
            print(f"[Telnet3] {carry}")
        try:
            writer.close()
        except Exception:
            pass
        return _sanitize_output(out)

    def run(self, cmd: str) -> str:
        try:
            return asyncio.run(self._run_async(cmd))
        except Exception as e:
            print(f"[Telnet3] Error ejecutando '{cmd}': {e}")
            return ""


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


def check_serial_port(port: str, baudrate: int = 9600, timeout: float = 1.0) -> bool:
    if not port or serial is None:
        return False
    try:
        with serial.Serial(port=port, baudrate=baudrate, timeout=timeout) as ser:
            time.sleep(0.1)
            return ser.is_open
    except Exception:
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


# -------- Vendor detection ---------
def detect_vendor_ssh(connection_data: Dict[str, Any]) -> str:
    host = connection_data.get("hostname", "")
    port = int(connection_data.get("port", 22) or 22)
    username = connection_data.get("username", "")
    password = connection_data.get("password", "")
    fast = bool(connection_data.get("fast_mode"))
    if not host:
        return "desconocido"
    try:
        print(f"[SSH] Conectando a {host}:{port} para leer versión...")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, port=port, username=username or None, password=password or None,
                       look_for_keys=False, allow_agent=False, timeout=3 if fast else 5)
        vendor = "desconocido"
        cached_output = ""
        # Probar primero 'show version' para Cisco/Juniper; luego Huawei
        for cmd in ("show version", "display version"):
            print(f"[SSH] Ejecutando: {cmd}")
            try:
                stdin, stdout, stderr = client.exec_command(cmd, timeout=3 if fast else 5)
                out = stdout.read().decode(errors="ignore") + stderr.read().decode(errors="ignore")
                if out:
                    cached_output = out
                for line in out.splitlines()[:20]:
                    print(f"[SSH] {line}")
                low = out.lower()
                if "huawei" in low or "vrp" in low:
                    if cached_output:
                        connection_data["cached_version_output"] = cached_output
                    vendor = "huawei"
                    break
                if "cisco" in low or "ios" in low:
                    if cached_output:
                        connection_data["cached_version_output"] = cached_output
                    vendor = "cisco"
                    break
                if "junos" in low or "juniper" in low:
                    if cached_output:
                        connection_data["cached_version_output"] = cached_output
                    vendor = "juniper"
                    break
            except Exception as e:
                print(f"[SSH] Error ejecutando {cmd}: {e}")
                continue
        try:
            client.close()
        except Exception:
            pass
        # Si no hubo coincidencia pero tenemos salida, cachearla igualmente
        if vendor == "desconocido" and cached_output:
            connection_data["cached_version_output"] = cached_output
        return vendor
    except Exception as e:
        print(f"[SSH] Error en detección de vendor: {e}")
        try:
            sock = socket.create_connection((host, port), timeout=2 if fast else 3)
            banner = sock.recv(128).decode(errors="ignore")
            print(f"[SSH] Banner: {banner.strip()}")
            sock.close()
            l = banner.lower()
            if "huawei" in l:
                return "huawei"
            if "cisco" in l:
                return "cisco"
            if "junos" in l or "juniper" in l:
                return "juniper"
        except Exception:
            pass
        return "desconocido"


def detect_vendor_telnet(connection_data: Dict[str, Any]) -> str:
    host = connection_data.get("hostname", "")
    port = int(connection_data.get("port", 23) or 23)
    username = connection_data.get("username", "")
    password = connection_data.get("password", "")
    fast = bool(connection_data.get("fast_mode"))
    if not host or telnet3 is None:
        return "desconocido"
    try:
        async def _detect() -> str:
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
            for l in out_all.splitlines()[-10:]:
                print(f"[Telnet3] {l}")

            async def _send_and_stream(cmd: str, delay: float = 0.2, read_sec: float = 1.2) -> str:
                print(f"[Telnet3] Ejecutando: {cmd}")
                writer.write("\r")
                await asyncio.sleep(0.15)
                writer.write(cmd + "\r")
                await asyncio.sleep(delay)
                end = time.monotonic() + read_sec
                out_cmd = ""
                carry = ""
                while time.monotonic() < end:
                    try:
                        part = await asyncio.wait_for(reader.read(256), timeout=0.25)
                    except Exception:
                        part = ""
                    if part:
                        out_cmd += part
                        carry += part
                        while "\n" in carry:
                            line, carry = carry.split("\n", 1)
                            print(f"[Telnet3] {line}")
                    else:
                        await asyncio.sleep(0.1)
                if carry:
                    print(f"[Telnet3] {carry}")
                return out_cmd

            await _send_and_stream("terminal length 0", delay=0.15 if fast else 0.2, read_sec=0.6 if fast else 0.8)
            prompt_text = ""
            for pl in reversed(out_all.splitlines()):
                if pl.strip():
                    prompt_text = pl.strip()
                    break
            if prompt_text and prompt_text.endswith(">"):
                writer.write("enable\r")
                await asyncio.sleep(0.4 if fast else 0.6)
                en_resp = await _read_for(0.8 if fast else 1.0)
                if "password" in en_resp.lower():
                    en_pw = connection_data.get("enable_password") or password
                    if en_pw:
                        writer.write(en_pw + "\r")
                        await asyncio.sleep(0.4 if fast else 0.6)
                        _ = await _read_for(0.8 if fast else 1.0)
            vendor_found = "desconocido"
            for cmd in ("show version", "display version"):
                buf = await _send_and_stream(cmd)
                out_all += "\n" + buf
                low_loop = buf.lower()
                # Detectar rápidamente para evitar comandos inválidos
                if "huawei" in low_loop or "vrp" in low_loop:
                    vendor_found = "huawei"
                    break
                if "cisco" in low_loop or "ios" in low_loop:
                    vendor_found = "cisco"
                    connection_data["paging_disabled"] = True
                    break
                if "junos" in low_loop or "juniper" in low_loop:
                    vendor_found = "juniper"
                    break

            try:
                writer.close()
            except Exception:
                pass

            low = out_all.lower()
            # Cachear salida de versión para evitar repetir en el análisis
            if out_all:
                connection_data["cached_version_output"] = out_all
            if vendor_found != "desconocido":
                return vendor_found
            if "huawei" in low or "vrp" in low:
                return "huawei"
            if "cisco" in low or "ios" in low:
                connection_data["paging_disabled"] = True
                return "cisco"
            if "junos" in low or "juniper" in low:
                return "juniper"
            return "desconocido"

        return asyncio.run(_detect())
    except Exception as e:
        print(f"[Telnet3] Error en detección de vendor: {e}")
        return "desconocido"


def detect_vendor_serial(connection_data: Dict[str, Any]) -> str:
    port = connection_data.get("port", "")
    username = connection_data.get("username", "")
    password = connection_data.get("password", "")
    baudrate = int(connection_data.get("baudrate", 9600) or 9600)
    fast = bool(connection_data.get("fast_mode"))
    if not port or serial is None:
        return "desconocido"
    try:
        print(f"[Serial] Probando versión en {port}...")
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

            out_all = ""
            for cmd in ("display version\r", "show version\r"):
                print(f"[Serial] Ejecutando: {cmd.strip()}")
                ser.write(cmd.encode())
                time.sleep(0.9 if fast else 1.2)
                buf = _read_chunk(1.1 if fast else 1.5)
                out_all += "\n" + buf
                print(f"[Serial] Resultado {cmd.strip()}:")
                for line in buf.splitlines()[:20]:
                    print(f"[Serial] {line}")
                low = out_all.lower()
                if "huawei" in low or "vrp" in low:
                    connection_data["cached_version_output"] = out_all
                    return "huawei"
                if "cisco" in low or "ios" in low:
                    connection_data["cached_version_output"] = out_all
                    return "cisco"
                if "junos" in low or "juniper" in low:
                    connection_data["cached_version_output"] = out_all
                    return "juniper"
        # Cachear salida si no hubo coincidencia
        if out_all:
            connection_data["cached_version_output"] = out_all
        return "desconocido"
    except Exception as e:
        print(f"[Serial] Error en detección de vendor: {e}")
        return "desconocido"
import platform
import subprocess
import time
import socket
import asyncio
from typing import Dict, Any

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
    host = connection_data.get("hostname", "")
    port = int(connection_data.get("port", 22) or 22)
    username = connection_data.get("username", "")
    password = connection_data.get("password", "")
    if not host or paramiko is None:
        return ""
    try:
        cmd_timeout = 3 if connection_data.get("fast_mode") else 5
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, port=port, username=username or None, password=password or None,
                       look_for_keys=False, allow_agent=False, timeout=cmd_timeout)
        stdin, stdout, stderr = client.exec_command(cmd, timeout=cmd_timeout)
        out = stdout.read().decode(errors="ignore") + stderr.read().decode(errors="ignore")
        client.close()
        return out
    except Exception as e:
        print(f"[SSH] Error ejecutando '{cmd}': {e}")
        return ""


# -------- Telnet (telnetlib3) ---------
def run_telnet_command(connection_data: Dict[str, Any], cmd: str, vendor: str = "") -> str:
    host = connection_data.get("hostname", "")
    port = int(connection_data.get("port", 23) or 23)
    username = connection_data.get("username", "")
    password = connection_data.get("password", "")
    if not host or telnet3 is None:
        return ""
    try:
        async def _exec() -> str:
            reader, writer = await telnet3.open_connection(host=host, port=port, encoding="utf8", shell=None)

            fast = bool(connection_data.get("fast_mode"))

            async def _read_for(seconds: float = 1.0) -> str:
                end = time.monotonic() + seconds
                buf = ""
                while time.monotonic() < end:
                    try:
                        part = await asyncio.wait_for(reader.read(256), timeout=0.20 if fast else 0.25)
                    except Exception:
                        part = ""
                    if part:
                        buf += part
                    else:
                        await asyncio.sleep(0.06 if fast else 0.1)
                return buf

            banner = await _read_for(0.8)
            low = banner.lower()
            # Autenticación si el servidor lo solicita
            if any(x in low for x in ("username:", "user name:", "login:")):
                if not username:
                    print("[Telnet3] Autenticación requerida, falta 'username'.")
                    try:
                        writer.close()
                    except Exception:
                        pass
                    return ""
                writer.write(username + "\r\n")
                await asyncio.sleep(0.4)
                after_user = await _read_for(0.8)
                low2 = (banner + after_user).lower()
                if ("password:" in low2 or "pass word:" in low2):
                    if not password:
                        print("[Telnet3] Se solicitó password, pero no fue provisto.")
                        try:
                            writer.close()
                        except Exception:
                            pass
                        return ""
                    writer.write(password + "\r\n")
                    await asyncio.sleep(0.6)
                    _ = await _read_for(1.0)

            # Asegurar prompt antes de enviar comando
            writer.write("\r")
            await asyncio.sleep(0.12 if fast else 0.2)
            prompt_text = await _read_for(0.6)

            # Si es Cisco, entrar a modo privilegiado con 'enable'
            if vendor.lower() == "cisco":
                snapshot = (banner + prompt_text).lower()
                if "#" not in snapshot:
                    writer.write("\r")
                    await asyncio.sleep(0.1)
                    writer.write("enable\r")
                    await asyncio.sleep(0.3)
                    resp = await _read_for(0.8)
                    if "password" in resp.lower():
                        en_pw = connection_data.get("enable_password") or password
                        if en_pw:
                            writer.write(en_pw + "\r")
                            await asyncio.sleep(0.6)
                            resp += await _read_for(1.0)
                    writer.write("terminal length 0\r")
                    await asyncio.sleep(0.2)
                    _ = await _read_for(0.6)

            # Enviar comando y leer salida
            writer.write("\r")
            await asyncio.sleep(0.1 if fast else 0.15)
            writer.write(cmd + "\r")
            await asyncio.sleep(0.12 if fast else 0.2)
            end = time.monotonic() + (1.2 if fast else 1.8)
            out = ""
            carry = ""
            while time.monotonic() < end:
                try:
                    part = await asyncio.wait_for(reader.read(256), timeout=0.20 if fast else 0.25)
                except Exception:
                    part = ""
                if part:
                    out += part
                    carry += part
                    while "\n" in carry:
                        line, carry = carry.split("\n", 1)
                        print(f"[Telnet3] {line}")
                else:
                    await asyncio.sleep(0.06 if fast else 0.1)
            if carry:
                print(f"[Telnet3] {carry}")
            try:
                writer.close()
            except Exception:
                pass
            return out

        return asyncio.run(_exec())
    except Exception as e:
        print(f"[Telnet3] Error ejecutando '{cmd}': {e}")
        return ""


# -------- Serial ---------
def run_serial_command(connection_data: Dict[str, Any], cmd: str) -> str:
    port = connection_data.get("port", "")
    username = connection_data.get("username", "")
    password = connection_data.get("password", "")
    baudrate = int(connection_data.get("baudrate", 9600) or 9600)
    fast = bool(connection_data.get("fast_mode"))
    if not port or serial is None:
        return ""
    try:
        with serial.Serial(port=port, baudrate=baudrate, timeout=1.0 if fast else 1.5) as ser:
            ser.reset_input_buffer()
            ser.reset_output_buffer()
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
                        time.sleep(0.06 if fast else 0.1)
                return buf

            welcome = _read_chunk(0.7 if fast else 1.0).lower()
            if any(x in welcome for x in ("username:", "user name:", "login:", "login authentication")):
                if username:
                    ser.write((username + "\r").encode())
                    time.sleep(0.4 if fast else 0.6)
                    _ = _read_chunk(0.8 if fast else 1.0)
                if password:
                    ser.write((password + "\r").encode())
                    time.sleep(0.8 if fast else 1.0)
                    _ = _read_chunk(0.9 if fast else 1.2)

            ser.write((cmd + "\r").encode())
            time.sleep(1.0 if fast else 1.5)
            out = _read_chunk(1.4 if fast else 2.0)
            return out
    except Exception as e:
        print(f"[Serial] Error ejecutando '{cmd}': {e}")
        return ""


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
        for cmd in ("display version", "show version"):
            print(f"[SSH] Ejecutando: {cmd}")
            try:
                stdin, stdout, stderr = client.exec_command(cmd, timeout=3 if fast else 5)
                out = stdout.read().decode(errors="ignore") + stderr.read().decode(errors="ignore")
                for line in out.splitlines()[:20]:
                    print(f"[SSH] {line}")
                low = out.lower()
                if "huawei" in low or "vrp" in low:
                    vendor = "huawei"
                    break
                if "cisco" in low or "ios" in low:
                    vendor = "cisco"
                    break
                if "junos" in low or "juniper" in low:
                    vendor = "juniper"
                    break
            except Exception as e:
                print(f"[SSH] Error ejecutando {cmd}: {e}")
                continue
        try:
            client.close()
        except Exception:
            pass
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
            for cmd in ("display version", "show version"):
                buf = await _send_and_stream(cmd)
                out_all += "\n" + buf

            try:
                writer.close()
            except Exception:
                pass

            low = out_all.lower()
            if "huawei" in low or "vrp" in low:
                return "huawei"
            if "cisco" in low or "ios" in low:
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
                    return "huawei"
                if "cisco" in low or "ios" in low:
                    return "cisco"
                if "junos" in low or "juniper" in low:
                    return "juniper"
        return "desconocido"
    except Exception as e:
        print(f"[Serial] Error en detección de vendor: {e}")
        return "desconocido"
"""
RouterAnalyzer simplificado
---------------------------

Este módulo ofrece una versión mínima y sencilla del analizador:
- Si el protocolo es SSH o Telnet, valida conectividad haciendo ping a la IP.
- Si el protocolo es Serial, valida que se pueda abrir el puerto.

La API conserva los métodos usados por la aplicación:
- RouterAnalyzer(connection_data)
- connect() -> bool
- analyze_router() -> Dict
- parse_analysis_data(analysis_data) -> Dict

No ejecuta comandos de router ni detecta fabricante; devuelve estructuras
vacías para que la UI siga funcionando sin errores.
"""

from typing import Dict, Any, List
import platform
import subprocess
import time
import socket

try:
    import serial  # type: ignore
except Exception:
    serial = None  # type: ignore

try:
    import paramiko  # type: ignore
except Exception:
    paramiko = None  # type: ignore

try:
    import telnetlib3 # type: ignore
except Exception:
    telnetlib = None  # type: ignore


class RouterAnalyzer:
    def __init__(self, connection_data: Dict[str, Any]):
        self.connection_data = connection_data or {}
        self.is_connected: bool = False
        self.protocol: str = self.connection_data.get("protocol", "SSH2")
        self.device_type: str = "generic"
        self.last_check_details: List[str] = []

    # --- Utilidades internas -------------------------------------------------
    @staticmethod
    def _ping_host(hostname: str, count: int = 2, timeout_ms: int = 1000) -> bool:
        """Realiza ping al host y retorna True si hay respuesta.

        En Windows usa `ping -n`, en Unix-like `ping -c`.
        """
        if not hostname:
            return False

        system = platform.system().lower()
        if "windows" in system:
            cmd = ["ping", "-n", str(count), "-w", str(timeout_ms), hostname]
        else:
            # timeout en segundos para Unix
            timeout_s = max(1, int(timeout_ms / 1000))
            cmd = ["ping", "-c", str(count), "-W", str(timeout_s), hostname]

        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            return result.returncode == 0
        except Exception:
            return False

    @staticmethod
    def _check_serial_port(port: str, baudrate: int = 9600, timeout: float = 1.0) -> bool:
        """Intenta abrir el puerto serial y lo cierra de inmediato si tiene éxito."""
        if not port:
            return False
        if serial is None:
            return False
        try:
            with serial.Serial(port=port, baudrate=baudrate, timeout=timeout) as ser:
                # Espera breve para estabilizar apertura
                time.sleep(0.1)
                return ser.is_open
        except Exception:
            return False

    # --- API pública ---------------------------------------------------------
    def connect(self) -> bool:
        """Valida conectividad según protocolo elegido.

        - SSH/Telnet: hace ping al hostname.
        - Serial: intenta abrir el puerto indicado.
        """
        self.last_check_details.clear()

        proto = self.protocol
        if proto in ("SSH2", "Telnet"):
            hostname = self.connection_data.get("hostname", "")
            ok = self._ping_host(hostname)
            self.is_connected = ok
            self.last_check_details.append(f"ping {hostname}: {'ok' if ok else 'fail'}")
            self.device_type = "network"
            return ok

        if proto == "Serial":
            port = self.connection_data.get("port", "")
            ok = self._check_serial_port(port)
            self.is_connected = ok
            self.last_check_details.append(f"serial open {port}: {'ok' if ok else 'fail'}")
            self.device_type = "serial"
            return ok

        # Protocolos desconocidos: marcar como no conectado
        self.is_connected = False
        self.last_check_details.append(f"unsupported protocol: {proto}")
        self.device_type = "generic"
        return False

    def analyze_router(self) -> Dict[str, Any]:
        """Devuelve un reporte mínimo del análisis.

        No se ejecutan comandos; solo se reportan las verificaciones hechas.
        """
        target = self.connection_data.get("hostname") if self.protocol != "Serial" else self.connection_data.get("port")
        print(f"[Analyzer] Protocolo: {self.protocol} | Destino: {target}")
        vendor = "desconocido"
        if self.is_connected:
            vendor = self.detect_vendor()
            print(f"[Analyzer] Vendor detectado: {vendor}")
        else:
            print("[Analyzer] No conectado; se omite detección de vendor")
        # Si el vendor es Huawei, obtener interfaces
        data: Dict[str, Any] = {}
        if vendor == "huawei" and self.is_connected:
            try:
                print("[Analyzer] Ejecutando 'display ip interface brief' para listar interfaces...")
                raw = self._get_huawei_ip_interface_brief()
                if raw:
                    # Mostrar algunas líneas
                    for line in raw.splitlines()[:30]:
                        print(f"[Huawei] {line}")
                    self.last_check_details.append("display ip interface brief")
                    data["huawei_ip_int_brief"] = raw
                else:
                    print("[Analyzer] No se obtuvo salida de interfaces.")
            except Exception as e:
                print(f"[Analyzer] Error obteniendo interfaces Huawei: {e}")
        return {
            "device_type": self.device_type,
            "protocol": self.protocol,
            "target": target,
            "connected": self.is_connected,
            "vendor": vendor,
            "commands_executed": list(self.last_check_details),
            "data": data,
        }

    def parse_analysis_data(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parsea datos mínimos del análisis para la UI.

        Si el vendor es Huawei y existe la salida de 'display ip interface brief',
        la parsea en una lista de interfaces.
        """
        interfaces: List[Dict[str, Any]] = []
        try:
            if analysis_data.get("vendor") == "huawei":
                text = analysis_data.get("data", {}).get("huawei_ip_int_brief", "")
                if text:
                    interfaces = self._parse_huawei_ip_interface_brief(text)
                    print(f"[Analyzer] Interfaces Huawei parseadas: {len(interfaces)}")
        except Exception as e:
            print(f"[Analyzer] Error al parsear interfaces: {e}")
        return {
            "interfaces": interfaces,
            "vrfs": [],
            "vlans": [],
            "routing_protocols": {
                "ospf": {"enabled": False, "config": ""},
                "eigrp": {"enabled": False, "config": ""},
                "bgp": {"enabled": False, "config": ""},
                "rip": {"enabled": False, "config": ""},
            },
            "static_routes": [],
            "dhcp_pools": [],
            "neighbors": {},
        }

    # --- Detección básica de vendor -----------------------------------------
    def detect_vendor(self) -> str:
        """Intento simple de detectar vendor leyendo versiones.

        SSH/Telnet: intenta ejecutar 'display version' y 'show version'.
        Serial: envía los mismos comandos al puerto.
        Imprime lo que lee a la consola.
        """
        proto = self.protocol
        if proto == "SSH2" and paramiko is not None:
            return self._detect_vendor_ssh()
        if proto == "Telnet" and telnetlib is not None:
            return self._detect_vendor_telnet()
        if proto == "Serial" and serial is not None:
            return self._detect_vendor_serial()
        print("[Analyzer] Vendor: desconocido (módulos no disponibles)")
        return "desconocido"

    def _detect_vendor_ssh(self) -> str:
        host = self.connection_data.get("hostname", "")
        port = int(self.connection_data.get("port", 22) or 22)
        username = self.connection_data.get("username", "")
        password = self.connection_data.get("password", "")
        if not host:
            return "desconocido"
        try:
            print(f"[SSH] Conectando a {host}:{port} para leer versión...")
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(host, port=port, username=username or None, password=password or None,
                           look_for_keys=False, allow_agent=False, timeout=5)
            vendor = "desconocido"
            for cmd in ("display version", "show version"):
                print(f"[SSH] Ejecutando: {cmd}")
                try:
                    stdin, stdout, stderr = client.exec_command(cmd, timeout=5)
                    out = stdout.read().decode(errors="ignore") + stderr.read().decode(errors="ignore")
                    # Mostrar algunas líneas en consola
                    for line in out.splitlines()[:20]:
                        print(f"[SSH] {line}")
                    low = out.lower()
                    if "huawei" in low or "vrp" in low:
                        vendor = "huawei"
                        break
                    if "cisco" in low or "ios" in low:
                        vendor = "cisco"
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
            # Intentar obtener banner del servidor SSH
            try:
                sock = socket.create_connection((host, port), timeout=3)
                banner = sock.recv(128).decode(errors="ignore")
                print(f"[SSH] Banner: {banner.strip()}")
                sock.close()
                l = banner.lower()
                if "huawei" in l:
                    return "huawei"
                if "cisco" in l:
                    return "cisco"
            except Exception:
                pass
            return "desconocido"

    def _detect_vendor_telnet(self) -> str:
        host = self.connection_data.get("hostname", "")
        port = int(self.connection_data.get("port", 23) or 23)
        username = self.connection_data.get("username", "")
        password = self.connection_data.get("password", "")
        if not host:
            return "desconocido"
        try:
            print(f"[Telnet] Conectando a {host}:{port}...")
            tn = telnetlib.Telnet(host, port, timeout=5)
            out_all = ""
            try:
                # Leer bienvenida/prompt
                data = tn.read_until(b"login:", timeout=1)
                out_all += data.decode(errors="ignore")
                print("[Telnet] Bienvenida/prompt:")
                for line in out_all.splitlines()[:20]:
                    print(f"[Telnet] {line}")

                # Intentar autenticación si hay credenciales
                if username:
                    tn.write((username + "\r\n").encode())
                    time.sleep(0.2)
                    tn.write((password + "\r\n").encode())
                    time.sleep(0.5)

                for cmd in ("display version", "show version"):
                    tn.write((cmd + "\r\n").encode())
                    time.sleep(1.0)
                    buf = tn.read_very_eager().decode(errors="ignore")
                    out_all += "\n" + buf
                    print(f"[Telnet] {cmd} output:")
                    for line in buf.splitlines()[:20]:
                        print(f"[Telnet] {line}")
            finally:
                try:
                    tn.close()
                except Exception:
                    pass
            low = out_all.lower()
            if "huawei" in low or "vrp" in low:
                return "huawei"
            if "cisco" in low or "ios" in low:
                return "cisco"
            return "desconocido"
        except Exception as e:
            print(f"[Telnet] Error en detección de vendor: {e}")
            return "desconocido"

    def _detect_vendor_serial(self) -> str:
        port = self.connection_data.get("port", "")
        username = self.connection_data.get("username", "")
        password = self.connection_data.get("password", "")
        if not port or serial is None:
            return "desconocido"
        try:
            print(f"[Serial] Probando versión en {port}...")
            with serial.Serial(port=port, baudrate=9600, timeout=1.0) as ser:
                # Limpiar buffers y provocar prompt
                try:
                    ser.reset_input_buffer()
                    ser.reset_output_buffer()
                except Exception:
                    pass
                time.sleep(0.2)
                ser.write(b"\r")
                time.sleep(0.6)

                out_all = ""

                def _read_chunk(duration: float = 0.8) -> str:
                    end = time.time() + duration
                    buf = ""
                    while time.time() < end:
                        try:
                            data = ser.read(512)
                        except Exception:
                            data = b""
                        if data:
                            part = data.decode(errors="ignore")
                            buf += part
                        else:
                            time.sleep(0.1)
                    return buf

                # Leer bienvenida/prompt inicial
                buf = _read_chunk(1.0)
                out_all += buf
                if buf:
                    print("[Serial] Bienvenida/prompt inicial:")
                    for line in buf.splitlines()[:20]:
                        print(f"[Serial] {line}")

                # Detectar si se requiere login y enviar credenciales
                low = out_all.lower()
                login_prompts = ("username:", "user name:", "login:", "login authentication")
                if any(p in low for p in login_prompts):
                    if not username or not password:
                        print("[Serial] Autenticación requerida, pero faltan credenciales (usuario/clave).")
                        return "desconocido"
                    print("[Serial] Detectado prompt de usuario; enviando usuario...")
                    ser.write((username + "\r").encode())
                    time.sleep(0.6)
                    buf = _read_chunk(1.2)
                    out_all += buf
                    print("[Serial] Detectado prompt de password; enviando password...")
                    ser.write((password + "\r").encode())
                    time.sleep(1.2)
                    buf = _read_chunk(1.5)
                    out_all += buf
                    for line in buf.splitlines()[:20]:
                        print(f"[Serial] {line}")

                # Ejecutar comandos de versión tras autenticación (si corresponde)
                for cmd in ("display version\r", "show version\r"):
                    print(f"[Serial] Ejecutando: {cmd.strip()}")
                    ser.write(cmd.encode())
                    time.sleep(1.2)
                    buf = _read_chunk(1.5)
                    out_all += "\n" + buf
                    print(f"[Serial] Resultado {cmd.strip()}:")
                    for line in buf.splitlines()[:20]:
                        print(f"[Serial] {line}")
                    low = out_all.lower()
                    if "huawei" in low or "vrp" in low:
                        return "huawei"
                    if "cisco" in low or "ios" in low:
                        return "cisco"
            return "desconocido"
        except Exception as e:
            print(f"[Serial] Error en detección de vendor: {e}")
            return "desconocido"

    # --- Ejecución de comandos según protocolo -------------------------------
    def _run_ssh(self, cmd: str) -> str:
        host = self.connection_data.get("hostname", "")
        port = int(self.connection_data.get("port", 22) or 22)
        username = self.connection_data.get("username", "")
        password = self.connection_data.get("password", "")
        if not host or paramiko is None:
            return ""
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(host, port=port, username=username or None, password=password or None,
                           look_for_keys=False, allow_agent=False, timeout=5)
            stdin, stdout, stderr = client.exec_command(cmd, timeout=5)
            out = stdout.read().decode(errors="ignore") + stderr.read().decode(errors="ignore")
            client.close()
            return out
        except Exception as e:
            print(f"[SSH] Error ejecutando '{cmd}': {e}")
            return ""

    def _run_telnet(self, cmd: str) -> str:
        host = self.connection_data.get("hostname", "")
        port = int(self.connection_data.get("port", 23) or 23)
        username = self.connection_data.get("username", "")
        password = self.connection_data.get("password", "")
        if not host or telnetlib is None:
            return ""
        try:
            tn = telnetlib.Telnet(host, port, timeout=5)
            # Autenticación simple si hay credenciales
            time.sleep(0.3)
            if username:
                tn.write((username + "\r\n").encode())
                time.sleep(0.3)
                tn.write((password + "\r\n").encode())
                time.sleep(0.6)
            tn.write((cmd + "\r\n").encode())
            time.sleep(1.2)
            out = tn.read_very_eager().decode(errors="ignore")
            tn.close()
            return out
        except Exception as e:
            print(f"[Telnet] Error ejecutando '{cmd}': {e}")
            return ""

    def _run_serial(self, cmd: str) -> str:
        port = self.connection_data.get("port", "")
        username = self.connection_data.get("username", "")
        password = self.connection_data.get("password", "")
        if not port or serial is None:
            return ""
        try:
            with serial.Serial(port=port, baudrate=9600, timeout=1.0) as ser:
                # Provocar prompt y autenticar si es necesario
                ser.reset_input_buffer()
                ser.reset_output_buffer()
                time.sleep(0.2)
                ser.write(b"\r")
                time.sleep(0.6)

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

                welcome = _read_chunk(1.0).lower()
                if any(x in welcome for x in ("username:", "user name:", "login:", "login authentication")):
                    if username:
                        ser.write((username + "\r").encode())
                        time.sleep(0.6)
                        _ = _read_chunk(1.0)
                    if password:
                        ser.write((password + "\r").encode())
                        time.sleep(1.0)
                        _ = _read_chunk(1.2)

                ser.write((cmd + "\r").encode())
                time.sleep(1.5)
                out = _read_chunk(2.0)
                return out
        except Exception as e:
            print(f"[Serial] Error ejecutando '{cmd}': {e}")
            return ""

    def _get_huawei_ip_interface_brief(self) -> str:
        cmd = "display ip interface brief"
        if self.protocol == "SSH2":
            return self._run_ssh(cmd)
        if self.protocol == "Telnet":
            return self._run_telnet(cmd)
        if self.protocol == "Serial":
            return self._run_serial(cmd)
        return ""

    # --- Parsing de Huawei ---------------------------------------------------
    def _parse_huawei_ip_interface_brief(self, text: str) -> List[Dict[str, Any]]:
        import re

        def cidr_to_mask(cidr: int) -> str:
            try:
                cidr = int(cidr)
                mask = (0xffffffff << (32 - cidr)) & 0xffffffff
                return ".".join(str((mask >> (8 * i)) & 0xff) for i in [3, 2, 1, 0])
            except Exception:
                return ""

        def is_ip(token: str) -> bool:
            return bool(re.match(r"^\d{1,3}(?:\.\d{1,3}){3}$", token))

        def parse_line(line: str) -> Dict[str, Any]:
            s = line.strip()
            if not s:
                return {}
            # Ignorar encabezados y separadores
            lower = s.lower()
            skip_keywords = [
                "display ip interface brief",
                "interface", "address", "mask", "protocol", "physical",
                "copyright", "vrp", "bytes", "login", "username:", "password:",
                "the password is not safe", "user login", "access type:", "ip-address :",
                "the number of interface", "-------", "----"
            ]
            # Leyendas típicas: *down, ^down, (l), (s), (E)
            legend_patterns = [r"^\*down", r"^\^down", r"^\(l\)", r"^\(s\)", r"^\(e\)"]
            if any(k in lower for k in skip_keywords):
                return {}
            if any(re.match(p, lower) for p in legend_patterns):
                return {}
            if lower.startswith("<huawei>"):
                return {}

            tokens = s.split()
            if len(tokens) < 2:
                return {}
            name = tokens[0]
            ip_address = ""
            mask = ""
            state = "down"
            # Tipo: prefijo alfabético del nombre
            mtype = re.match(r"^([A-Za-z-]+)", name)
            itype = mtype.group(1) if mtype else "Ethernet"

            # Buscar IP y máscara
            for i, t in enumerate(tokens[1:]):
                if t.lower() == "unassigned":
                    ip_address = ""
                    mask = ""
                    break
                m = re.match(r"^(\d{1,3}(?:\.\d{1,3}){3})/(\d{1,2})$", t)
                if m:
                    ip_address = m.group(1)
                    mask = cidr_to_mask(int(m.group(2)))
                    # intentar leer estados (physical/protocol) en los tokens restantes
                    rest = tokens[i+2:]
                    states = [rt.lower() for rt in rest if re.match(r"^(up|down)(\(s\))?$", rt.lower())]
                    if states:
                        # Usar estado físico si hay dos; caso contrario usar el único
                        state = states[-2] if len(states) >= 2 else states[-1]
                        state = "up" if state.startswith("up") else "down"
                    break
                if is_ip(t) and i+2 <= len(tokens[1:]) and is_ip(tokens[1:][i+1]):
                    ip_address = t
                    mask = tokens[1:][i+1]
                    rest = tokens[i+3:]
                    states = [rt.lower() for rt in rest if re.match(r"^(up|down)(\(s\))?$", rt.lower())]
                    if states:
                        state = states[-2] if len(states) >= 2 else states[-1]
                        state = "up" if state.startswith("up") else "down"
                    break
            if not ip_address and not mask:
                # Posibles líneas sin IP; buscar estado
                states = [rt.lower() for rt in tokens if re.match(r"^(up|down)(\(s\))?$", rt.lower())]
                if states:
                    state = states[-2] if len(states) >= 2 else states[-1]
                    state = "up" if state.startswith("up") else "down"
            return {
                "name": name,
                "type": itype,
                "ip_address": ip_address or "",
                "mask": mask or "",
                "status": state,
                "description": "",
            }

        interfaces: List[Dict[str, Any]] = []
        for line in text.splitlines():
            parsed = parse_line(line)
            if parsed:
                interfaces.append(parsed)
        # Remover posibles duplicados por eco de comandos
        unique = []
        seen = set()
        for it in interfaces:
            key = (it["name"], it["ip_address"], it["mask"])
            if key in seen:
                continue
            seen.add(key)
            unique.append(it)
        return unique
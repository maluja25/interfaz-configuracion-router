from typing import Dict, Any, List
from .analyzer_core import analyze, fetch_running_config as _fetch_running_config
from .connections import ping_host, check_serial_port
from .vendor_commands import DISABLE_PAGING, VERSION_COMMAND, INTERFACES_BRIEF, RUNNING_CONFIG
from .parsers import (
    parse_huawei_version,
    parse_huawei_ip_interface_brief,
    parse_cisco_version,
    parse_cisco_ip_interface_brief,
    parse_juniper_version,
    parse_juniper_interfaces_terse,
    parse_huawei_ospf_config,
    parse_huawei_bgp_config,
    parse_huawei_bgp_peer,
    parse_huawei_ospf_peer,
)


def run_analysis(connection_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fachada simple para la GUI.
    Uso: from modules.router_analyzer.router_analyzer import run_analysis
    """
    return analyze(connection_data)


def fetch_running_config(connection_data: Dict[str, Any]) -> str:
    """Fachada para obtener la configuración en ejecución del dispositivo."""
    return _fetch_running_config(connection_data)


class RouterAnalyzer:
    """Fachada compatible que mantiene la API usada por la GUI.

    Métodos:
    - connect() -> bool
    - analyze_router() -> Dict[str, Any]
    - parse_analysis_data(analysis_data) -> Dict[str, Any]
    """

    def __init__(self, connection_data: Dict[str, Any]):
        self.connection_data = connection_data or {}
        self.protocol: str = self.connection_data.get("protocol", "SSH2")
        self.device_type: str = "generic"
        self.is_connected: bool = False
        self.vendor: str = "desconocido"
        self.last_check_details: List[str] = []

    def connect(self) -> bool:
        """Conectar de forma simplificada: ping para SSH/Telnet, abrir puerto para Serial."""
        try:
            verbose = bool(self.connection_data.get("verbose"))
            if self.protocol == "Serial":
                port = self.connection_data.get("port", "")
                baudrate = int(self.connection_data.get("baudrate", 9600) or 9600)
                if verbose:
                    print(f"[CLI] Abriendo puerto serial {port} @ {baudrate}…", flush=True)
                ok = check_serial_port(port, baudrate=baudrate, timeout=1.0)
                self.is_connected = bool(ok)
                if verbose:
                    print(f"[CLI] Serial {'OK' if self.is_connected else 'ERROR'}", flush=True)
                return self.is_connected
            host = self.connection_data.get("hostname", "")
            if verbose:
                print(f"[CLI] Haciendo ping a {host}…", flush=True)
            ok = ping_host(host) if host else False
            self.is_connected = bool(ok)
            if verbose:
                print(f"[CLI] Ping {'OK' if self.is_connected else 'ERROR'}", flush=True)
            return self.is_connected
        except Exception:
            self.is_connected = False
            return False

    def analyze_router(self) -> Dict[str, Any]:
        """Ejecuta análisis modular y devuelve estructura compatible con la GUI actual."""
        from datetime import datetime
        verbose = bool(self.connection_data.get("verbose"))

        target = self.connection_data.get("hostname") if self.protocol != "Serial" else self.connection_data.get("port")
        if verbose:
            print(f"[CLI] Analizando router en {target} via {self.protocol}…", flush=True)
        result = analyze(self.connection_data)
        if verbose:
            print("[CLI] Análisis terminado, compilando resumen…", flush=True)
        vendor = (result.get("raw", {}).get("vendor") or "desconocido").lower()
        self.vendor = vendor

        # Registrar comandos ejecutados según vendor
        ven_key = vendor.lower()
        cmds = []
        cmds.extend(DISABLE_PAGING.get(ven_key, []))
        vcmd = VERSION_COMMAND.get(ven_key, "")
        icmd = INTERFACES_BRIEF.get(ven_key, "")
        rcfg = RUNNING_CONFIG.get(ven_key, "")
        if vcmd:
            cmds.append(vcmd)
        if icmd:
            cmds.append(icmd)
        if rcfg:
            cmds.append(rcfg)
        self.last_check_details = cmds

        # Mapear datos crudos por vendor para compatibilidad con parse_analysis_data
        raw_version = result.get("raw", {}).get("version", "")
        raw_ifaces = result.get("raw", {}).get("interfaces", "")
        raw_running = result.get("raw", {}).get("running_config", "")
        data: Dict[str, Any] = {}
        if ven_key == "huawei":
            data["huawei_version"] = raw_version
            data["huawei_ip_int_brief"] = raw_ifaces
            data["huawei_running_config"] = raw_running
        elif ven_key == "cisco":
            data["cisco_show_version"] = raw_version
            data["cisco_ip_int_brief"] = raw_ifaces
            data["cisco_running_config"] = raw_running
        elif ven_key == "juniper":
            data["juniper_show_version"] = raw_version
            data["juniper_interfaces_terse"] = raw_ifaces
            data["juniper_running_config"] = raw_running

        return {
            "device_type": self.device_type,
            "protocol": self.protocol,
            "target": target,
            "connected": self.is_connected,
            "vendor": vendor,
            "commands_executed": list(self.last_check_details),
            "data": data,
            # Campos esperados por el dashboard
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "hostname": self.connection_data.get("hostname", "N/A"),
        }

    def get_running_config(self) -> str:
        """Obtiene la configuración en ejecución utilizando los datos de conexión actuales."""
        return _fetch_running_config(self.connection_data)

    def parse_analysis_data(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parsea los datos del análisis en la misma estructura que la GUI espera."""
        interfaces: List[Dict[str, Any]] = []
        device_info: Dict[str, Any] = {}
        routing_protocols: Dict[str, Any] = {
            "ospf": {"enabled": False, "config": "", "process_id": "", "networks": []},
            "bgp": {"enabled": False, "config": "", "as_number": "", "neighbors": []},
        }
        # Valores por defecto para claves usadas por la UI
        vrfs: List[Dict[str, Any]] = []
        static_routes: List[Dict[str, Any]] = []
        cpu_usage: str = "N/A"
        memory_usage: str = "N/A"
        storage_usage: str = "N/A"

        vendor = (analysis_data.get("vendor") or "desconocido").lower()
        data = analysis_data.get("data", {})
        running_cfg: str = ""
        try:
            if vendor == "huawei":
                h_ver = data.get("huawei_version", "")
                if h_ver:
                    device_info = parse_huawei_version(h_ver)
                h_text = data.get("huawei_ip_int_brief", "")
                if h_text:
                    interfaces = parse_huawei_ip_interface_brief(h_text)
                running_cfg = data.get("huawei_running_config", "")
                # OSPF/BGP: si están presentes, parsearlos
                ospf_cfg = data.get("huawei_ospf_config", "")
                if ospf_cfg:
                    parsed_ospf = parse_huawei_ospf_config(ospf_cfg)
                    routing_protocols["ospf"].update(parsed_ospf)
                    has_valid_ospf = bool(parsed_ospf.get("process_id")) or bool(parsed_ospf.get("networks"))
                    routing_protocols["ospf"]["config"] = ospf_cfg if has_valid_ospf else ""
                    routing_protocols["ospf"]["enabled"] = has_valid_ospf
                bgp_cfg = data.get("huawei_bgp_config", "")
                if bgp_cfg:
                    parsed_bgp = parse_huawei_bgp_config(bgp_cfg)
                    routing_protocols["bgp"].update(parsed_bgp)
                    has_valid_bgp = bool(parsed_bgp.get("as_number")) or bool(parsed_bgp.get("neighbors"))
                    routing_protocols["bgp"]["config"] = bgp_cfg if has_valid_bgp else ""
                    routing_protocols["bgp"]["enabled"] = has_valid_bgp
                bgp_peer = data.get("huawei_bgp_peer", "")
                if bgp_peer:
                    parsed_bgp_peers = parse_huawei_bgp_peer(bgp_peer)
                    known_ips = {n.get("ip") for n in routing_protocols["bgp"]["neighbors"]}
                    for p in parsed_bgp_peers:
                        if p.get("ip") and p["ip"] not in known_ips:
                            routing_protocols["bgp"]["neighbors"].append({
                                "ip": p.get("ip"),
                                "remote_as": p.get("as", ""),
                            })
                ospf_peer = data.get("huawei_ospf_peer", "")
                if ospf_peer:
                    _ = parse_huawei_ospf_peer(ospf_peer)
            elif vendor == "cisco":
                c_ver = data.get("cisco_show_version", "")
                if c_ver:
                    device_info = parse_cisco_version(c_ver)
                c_text = data.get("cisco_ip_int_brief", "")
                if c_text:
                    interfaces = parse_cisco_ip_interface_brief(c_text)
                running_cfg = data.get("cisco_running_config", "")
            elif vendor == "juniper":
                j_ver = data.get("juniper_show_version", "")
                if j_ver:
                    device_info = parse_juniper_version(j_ver)
                j_text = data.get("juniper_interfaces_terse", "")
                if j_text:
                    interfaces = parse_juniper_interfaces_terse(j_text)
                running_cfg = data.get("juniper_running_config", "")
        except Exception:
            pass

        # Construir 'neighbors' en el formato que usa el dashboard
        neighbors = {
            "ospf": routing_protocols.get("ospf", {}).get("networks", []) if routing_protocols.get("ospf", {}).get("enabled") else [],
            "bgp": routing_protocols.get("bgp", {}).get("neighbors", []) if routing_protocols.get("bgp", {}).get("enabled") else [],
        }

        return {
            "interfaces": interfaces,
            "routing_protocols": routing_protocols,
            "device_info": device_info,
            # Claves adicionales que el dashboard consulta
            "neighbors": neighbors,
            "vrfs": vrfs,
            "static_routes": static_routes,
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "storage_usage": storage_usage,
            "running_config": running_cfg,
        }
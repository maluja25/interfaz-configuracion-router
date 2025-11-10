from typing import Dict, Any
from .connections import (
    detect_vendor_ssh,
    detect_vendor_telnet,
    detect_vendor_serial,
    run_ssh_command,
    run_telnet_command,
    run_serial_command,
)
from .vendor_commands import DISABLE_PAGING, VERSION_COMMAND, INTERFACES_BRIEF, RUNNING_CONFIG
from .parsers import (
    parse_huawei_version,
    parse_huawei_ip_interface_brief,
    parse_cisco_version,
    parse_cisco_ip_interface_brief,
    parse_juniper_version,
    parse_juniper_interfaces_terse,
)


def _detect_vendor(connection_data: Dict[str, Any]) -> str:
    proto = connection_data.get("protocol", "SSH2")
    verbose = bool(connection_data.get("verbose"))
    if verbose:
        print(f"[CLI] Detectando fabricante via {proto}…", flush=True)
    # Permitir sugerencia de vendor para saltar detección y acelerar
    vendor_hint = (connection_data.get("vendor_hint") or "").strip().lower()
    if vendor_hint in ("huawei", "cisco", "juniper"):
        if verbose:
            print(f"[CLI] Usando pista de fabricante: {vendor_hint}", flush=True)
        return vendor_hint
    if proto == "SSH2":
        ven = detect_vendor_ssh(connection_data)
        if verbose:
            print(f"[CLI] Fabricante detectado: {ven}", flush=True)
        return ven
    if proto == "Telnet":
        ven = detect_vendor_telnet(connection_data)
        if verbose:
            print(f"[CLI] Fabricante detectado: {ven}", flush=True)
        return ven
    if proto == "Serial":
        ven = detect_vendor_serial(connection_data)
        if verbose:
            print(f"[CLI] Fabricante detectado: {ven}", flush=True)
        return ven
    return "unknown"


def _run_command(connection_data: Dict[str, Any], command: str, vendor: str) -> str:
    proto = connection_data.get("protocol", "SSH2")
    if proto == "SSH2":
        return run_ssh_command(connection_data, command)
    if proto == "Telnet":
        return run_telnet_command(connection_data, command, vendor=vendor)
    if proto == "Serial":
        return run_serial_command(connection_data, command)
    return ""


def analyze(connection_data: Dict[str, Any]) -> Dict[str, Any]:
    verbose = bool(connection_data.get("verbose"))
    vendor = _detect_vendor(connection_data)
    ven_key = vendor.lower()

    # Disable paging (only if not already disabled)
    if not bool(connection_data.get("paging_disabled")):
        for cmd in DISABLE_PAGING.get(ven_key, []):
            if verbose:
                print(f"[CLI] Deshabilitando paginación: '{cmd}'", flush=True)
            _run_command(connection_data, cmd, ven_key)
        # Marcar como deshabilitada para evitar repeticiones en futuras llamadas
        connection_data["paging_disabled"] = True

    # Collect raw outputs
    version_cmd = VERSION_COMMAND.get(ven_key, "")
    iface_cmd = INTERFACES_BRIEF.get(ven_key, "")
    cfg_cmd = RUNNING_CONFIG.get(ven_key, "")
    raw_version = ""
    if version_cmd:
        cached_ver = connection_data.get("cached_version_output")
        if isinstance(cached_ver, str) and cached_ver.strip():
            if verbose:
                print("[CLI] Usando salida de versión cacheada.", flush=True)
            raw_version = cached_ver
        else:
            if verbose:
                print(f"[CLI] Ejecutando comando versión: '{version_cmd}'", flush=True)
            raw_version = _run_command(connection_data, version_cmd, ven_key)
    if verbose and iface_cmd:
        print(f"[CLI] Ejecutando comando interfaces: '{iface_cmd}'", flush=True)
    raw_ifaces = _run_command(connection_data, iface_cmd, ven_key) if iface_cmd else ""

    # Prefetch running configuration to have it ready for saving
    raw_running = ""
    if cfg_cmd:
        if verbose:
            print(f"[CLI] Ejecutando comando configuración: '{cfg_cmd}'", flush=True)
        raw_running = _run_command(connection_data, cfg_cmd, ven_key)

    parsed: Dict[str, Any] = {"device_info": {}, "interfaces": []}
    if ven_key == "huawei":
        parsed["device_info"] = parse_huawei_version(raw_version)
        parsed["interfaces"] = parse_huawei_ip_interface_brief(raw_ifaces)
    elif ven_key == "cisco":
        parsed["device_info"] = parse_cisco_version(raw_version)
        parsed["interfaces"] = parse_cisco_ip_interface_brief(raw_ifaces)
    elif ven_key == "juniper":
        parsed["device_info"] = parse_juniper_version(raw_version)
        parsed["interfaces"] = parse_juniper_interfaces_terse(raw_ifaces)

    parsed["device_info"]["vendor"] = vendor.title() if vendor != "unknown" else "Unknown"
    parsed["raw"] = {
        "version": raw_version,
        "interfaces": raw_ifaces,
        "vendor": vendor,
        "running_config": raw_running,
    }
    if verbose:
        print("[CLI] Parseo completado.", flush=True)
    return parsed


def fetch_running_config(connection_data: Dict[str, Any]) -> str:
    """Obtiene la configuración en ejecución del dispositivo según el vendor.

    Respeta el flag 'paging_disabled' para no repetir el comando de deshabilitar paginación.
    Usa 'vendor_hint' si está presente para saltar la detección.
    """
    verbose = bool(connection_data.get("verbose"))
    vendor = _detect_vendor(connection_data)
    ven_key = vendor.lower()

    if not bool(connection_data.get("paging_disabled")):
        for cmd in DISABLE_PAGING.get(ven_key, []):
            if verbose:
                print(f"[CLI] Deshabilitando paginación: '{cmd}'", flush=True)
            _run_command(connection_data, cmd, ven_key)
        connection_data["paging_disabled"] = True

    cfg_cmd = RUNNING_CONFIG.get(ven_key, "")
    if not cfg_cmd:
        if verbose:
            print(f"[CLI] No hay comando de configuración para vendor '{ven_key}'.", flush=True)
        return ""
    if verbose:
        print(f"[CLI] Obteniendo configuración: '{cfg_cmd}'", flush=True)
    return _run_command(connection_data, cfg_cmd, ven_key)
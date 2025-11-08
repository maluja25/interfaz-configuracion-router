from typing import Dict, Any
from .connections import (
    detect_vendor_ssh,
    detect_vendor_telnet,
    detect_vendor_serial,
    run_ssh_command,
    run_telnet_command,
    run_serial_command,
)
from .vendor_commands import DISABLE_PAGING, VERSION_COMMAND, INTERFACES_BRIEF
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
    # Permitir sugerencia de vendor para saltar detección y acelerar
    vendor_hint = (connection_data.get("vendor_hint") or "").strip().lower()
    if vendor_hint in ("huawei", "cisco", "juniper"):
        return vendor_hint
    if proto == "SSH2":
        return detect_vendor_ssh(connection_data)
    if proto == "Telnet":
        return detect_vendor_telnet(connection_data)
    if proto == "Serial":
        return detect_vendor_serial(connection_data)
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
    vendor = _detect_vendor(connection_data)
    ven_key = vendor.lower()

    # Disable paging
    for cmd in DISABLE_PAGING.get(ven_key, []):
        _run_command(connection_data, cmd, ven_key)

    # Collect raw outputs
    version_cmd = VERSION_COMMAND.get(ven_key, "")
    iface_cmd = INTERFACES_BRIEF.get(ven_key, "")
    raw_version = _run_command(connection_data, version_cmd, ven_key) if version_cmd else ""
    raw_ifaces = _run_command(connection_data, iface_cmd, ven_key) if iface_cmd else ""

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
    }
    return parsed
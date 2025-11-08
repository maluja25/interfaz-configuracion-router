from typing import Dict, Any, List
from .connections import run_ssh_command, run_telnet_command, run_serial_command


def _exec(connection_data: Dict[str, Any], commands: List[str], vendor: str = "") -> List[str]:
    proto = connection_data.get("protocol", "SSH2")
    outputs: List[str] = []
    for cmd in commands:
        if proto == "SSH2":
            outputs.append(run_ssh_command(connection_data, cmd))
        elif proto == "Telnet":
            outputs.append(run_telnet_command(connection_data, cmd, vendor=vendor))
        elif proto == "Serial":
            outputs.append(run_serial_command(connection_data, cmd))
    return outputs


def set_interface_ip(connection_data: Dict[str, Any], vendor: str, interface: str, ip: str, mask: str) -> List[str]:
    vendor = (vendor or "").lower()
    if vendor == "cisco":
        cmds = [
            "configure terminal",
            f"interface {interface}",
            f"ip address {ip} {mask}",
            "no shutdown",
            "end",
            "write memory",
        ]
        return _exec(connection_data, cmds, vendor)
    if vendor == "huawei":
        cmds = [
            f"interface {interface}",
            f"ip address {ip} {mask}",
            "undo shutdown",
            "quit",
            "save",
        ]
        return _exec(connection_data, cmds, vendor)
    if vendor == "juniper":
        cmds = [
            f"configure",
            f"set interfaces {interface} unit 0 family inet address {ip}/{mask}",
            "commit",
            "exit",
        ]
        return _exec(connection_data, cmds, vendor)
    return []


def shutdown_interface(connection_data: Dict[str, Any], vendor: str, interface: str) -> List[str]:
    vendor = (vendor or "").lower()
    if vendor == "cisco":
        cmds = ["configure terminal", f"interface {interface}", "shutdown", "end", "write memory"]
        return _exec(connection_data, cmds, vendor)
    if vendor == "huawei":
        cmds = [f"interface {interface}", "shutdown", "quit", "save"]
        return _exec(connection_data, cmds, vendor)
    if vendor == "juniper":
        cmds = ["configure", f"set interfaces {interface} disable", "commit", "exit"]
        return _exec(connection_data, cmds, vendor)
    return []


def no_shutdown_interface(connection_data: Dict[str, Any], vendor: str, interface: str) -> List[str]:
    vendor = (vendor or "").lower()
    if vendor == "cisco":
        cmds = ["configure terminal", f"interface {interface}", "no shutdown", "end", "write memory"]
        return _exec(connection_data, cmds, vendor)
    if vendor == "huawei":
        cmds = [f"interface {interface}", "undo shutdown", "quit", "save"]
        return _exec(connection_data, cmds, vendor)
    if vendor == "juniper":
        cmds = ["configure", f"delete interfaces {interface} disable", "commit", "exit"]
        return _exec(connection_data, cmds, vendor)
    return []


def add_static_route(connection_data: Dict[str, Any], vendor: str, network: str, mask: str, via: str) -> List[str]:
    vendor = (vendor or "").lower()
    if vendor == "cisco":
        cmds = ["configure terminal", f"ip route {network} {mask} {via}", "end", "write memory"]
        return _exec(connection_data, cmds, vendor)
    if vendor == "huawei":
        cmds = [f"ip route-static {network} {mask} {via}", "save"]
        return _exec(connection_data, cmds, vendor)
    if vendor == "juniper":
        cmds = ["configure", f"set routing-options static route {network}/{mask} next-hop {via}", "commit", "exit"]
        return _exec(connection_data, cmds, vendor)
    return []
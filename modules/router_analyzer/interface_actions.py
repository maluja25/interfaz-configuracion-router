from typing import Dict, Any, List
from .connections import (
    run_ssh_command,
    run_telnet_command,
    run_serial_command,
    run_ssh_commands_batch,
    run_telnet_commands_batch,
    run_serial_commands_batch,
    run_telnet_commands_script,
)


def _exec(connection_data: Dict[str, Any], commands: List[str], vendor: str = "") -> List[str]:
    proto = connection_data.get("protocol", "SSH2")
    verbose = bool(connection_data.get("verbose"))
    if verbose:
        try:
            print(f"[CMD] Proto={proto} Vendor={vendor} Comandos={commands}")
        except Exception:
            pass
    if proto == "SSH2":
        return run_ssh_commands_batch(connection_data, commands)
    if proto == "Telnet":
        if bool(connection_data.get("send_script")):
            return run_telnet_commands_script(connection_data, commands, vendor=vendor)
        return run_telnet_commands_batch(connection_data, commands, vendor=vendor)
    if proto == "Serial":
        return run_serial_commands_batch(connection_data, commands)
    outputs: List[str] = []
    for cmd in commands:
        outputs.append(run_ssh_command(connection_data, cmd))
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

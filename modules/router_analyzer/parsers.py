import re
from typing import Dict, Any, List


# ---------------- Huawei Parsers -----------------

def parse_huawei_ip_interface_brief(text: str) -> List[Dict[str, Any]]:
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
        lower = s.lower()
        skip_keywords = [
            "display ip interface brief",
            "interface", "address", "mask", "protocol", "physical",
            "copyright", "vrp", "bytes", "login", "username:", "password:",
            "the password is not safe", "user login", "access type:", "ip-address :",
            "the number of interface", "-------", "----"
        ]
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
        mtype = re.match(r"^([A-Za-z-]+)", name)
        itype = mtype.group(1) if mtype else "Ethernet"

        # IP/Máscara en formato CIDR: 1.2.3.4/24
        for t in tokens[1:]:
            m = re.match(r"^(\d{1,3}(?:\.\d{1,3}){3})\/(\d{1,2})$", t)
            if m:
                ip_address = m.group(1)
                mask = cidr_to_mask(int(m.group(2)))
                break
        # IP y máscara separadas en columnas recientes
        if not ip_address:
            for i, t in enumerate(tokens):
                if is_ip(t):
                    ip_address = t
                    mask = tokens[1:][i+1] if (i+1) < len(tokens[1:]) else ""
                    break
        # Estados en columnas al final
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
    unique = []
    seen = set()
    for it in interfaces:
        key = (it["name"], it["ip_address"], it["mask"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(it)
    return unique


def parse_huawei_version(text: str) -> Dict[str, Any]:
    import re
    di: Dict[str, Any] = {
        "model": "N/A",
        "firmware": "N/A",
        "uptime": "N/A",
        "serial": "N/A",
        "architecture": "N/A",
        "ram_memory": "N/A",
        "flash_memory": "N/A",
        "ethernet_ports": "N/A",
        "wic_slots": "N/A",
        "protocols": "N/A",
    }

    m = re.search(r"VRP.*Version\s+([\d\.]+)\s*\(([^)]+)\)", text, re.IGNORECASE)
    if m:
        version = m.group(1)
        build = m.group(2)
        di["firmware"] = f"VRP {version} ({build})"
        di["architecture"] = "VRP"

    m2 = re.search(r"Board\s+Type\s*:\s*(\S+)", text, re.IGNORECASE)
    if m2:
        di["model"] = m2.group(1)
    else:
        m2b = re.search(r"Huawei\s+(\S+)\s+Router\s+uptime", text, re.IGNORECASE)
        if m2b:
            di["model"] = m2b.group(1)

    mu = re.search(r"uptime\s+is\s+(.+)", text, re.IGNORECASE)
    if mu:
        di["uptime"] = mu.group(1).strip()

    mr = re.search(r"SDRAM\s+Memory\s+Size\s*:\s*(\d+)\s*M\s*bytes", text, re.IGNORECASE)
    if mr:
        di["ram_memory"] = f"{mr.group(1)} MB"

    mf0 = re.search(r"Flash\s+0\s+Memory\s+Size\s*:\s*(\d+)\s*M\s*bytes", text, re.IGNORECASE)
    mf1 = re.search(r"Flash\s+1\s+Memory\s+Size\s*:\s*(\d+)\s*M\s*bytes", text, re.IGNORECASE)
    flashes = []
    if mf0:
        flashes.append(f"Flash0 {mf0.group(1)} MB")
    if mf1:
        flashes.append(f"Flash1 {mf1.group(1)} MB")
    if flashes:
        di["flash_memory"] = ", ".join(flashes)

    ms = re.search(r"\bSN\s*:\s*(\S+)|Serial\s+Number\s*:\s*(\S+)", text, re.IGNORECASE)
    if ms:
        di["serial"] = ms.group(1) or ms.group(2)

    if di["architecture"] != "N/A":
        di["protocols"] = di["architecture"]

    return di


# ---------------- Cisco Parsers -----------------

def parse_cisco_ip_interface_brief(text: str) -> List[Dict[str, Any]]:
    import re
    interfaces: List[Dict[str, Any]] = []

    def infer_type(name: str) -> str:
        m = re.match(r"^([A-Za-z-]+)", name)
        return m.group(1) if m else "Ethernet"

    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        l = s.lower()
        if any(k in l for k in [
            "interface", "ip-address", "ok?", "method", "status", "protocol",
            "show ip interface brief", "copyright",
        ]):
            continue
        parts = re.split(r"\s+", s)
        if len(parts) < 3:
            continue
        name = parts[0]
        ipaddr = parts[1] if parts[1].lower() != "unassigned" else ""
        status = "down"
        if len(parts) >= 6:
            st = parts[-2].lower()
            pr = parts[-1].lower()
            status = "up" if (st.startswith("up") and pr.startswith("up")) else ("down")
        interfaces.append({
            "name": name,
            "type": infer_type(name),
            "ip_address": ipaddr,
            "mask": "",
            "status": status,
            "description": "",
        })
    return interfaces


def parse_cisco_version(text: str) -> Dict[str, Any]:
    import re
    di: Dict[str, Any] = {
        "model": "N/A",
        "firmware": "N/A",
        "uptime": "N/A",
        "serial": "N/A",
        "architecture": "IOS",
        "ram_memory": "N/A",
        "flash_memory": "N/A",
        "ethernet_ports": "N/A",
    }

    mv = re.search(r"Cisco IOS Software,\s*([\w\-\.]+)", text)
    if mv:
        di["firmware"] = mv.group(1)

    mu = re.search(r"uptime\s+is\s+(.+)", text, re.IGNORECASE)
    if mu:
        di["uptime"] = mu.group(1).strip()

    mm = re.search(r"[Cc]isco\s+(\S+)\s+processor", text)
    if mm:
        di["model"] = mm.group(1)

    rm = re.search(r"(\d+)\s+Kbytes of memory", text, re.IGNORECASE)
    if rm:
        di["ram_memory"] = f"{rm.group(1)} KB"

    fm = re.search(r"(\d+)\s+Kbytes of flash", text, re.IGNORECASE)
    if fm:
        di["flash_memory"] = f"{fm.group(1)} KB"

    pe = re.search(r"(\d+)\s+Ethernet interfaces", text, re.IGNORECASE)
    if pe:
        di["ethernet_ports"] = pe.group(1)

    return di


# ---------------- Huawei OSPF/BGP Parsers -----------------

def parse_huawei_ospf_config(text: str) -> Dict[str, Any]:
    import re
    result: Dict[str, Any] = {"process_id": "", "networks": []}
    m = re.search(r"\bospf\s+(\d+)\b", text, re.IGNORECASE)
    if not m:
        m = re.search(r"OSPF\s+Process\s+(\d+)", text, re.IGNORECASE)
    if m:
        result["process_id"] = m.group(1)
    for area_match in re.finditer(r"area\s+([\d\.]+)\s*\n([\s\S]*?)(?=\n\s*area\s+|\Z)", text, re.IGNORECASE):
        area_id = area_match.group(1)
        body = area_match.group(2)
        for net_m in re.finditer(r"network\s+(\d{1,3}(?:\.\d{1,3}){3})\s+(\d{1,3}(?:\.\d{1,3}){3})", body, re.IGNORECASE):
            result["networks"].append({
                "network": net_m.group(1),
                "wildcard": net_m.group(2),
                "area": area_id,
            })
    return result


def parse_huawei_bgp_config(text: str) -> Dict[str, Any]:
    import re
    result: Dict[str, Any] = {"as_number": "", "neighbors": []}
    m = re.search(r"\bbgp\s+(\d+)\b", text, re.IGNORECASE)
    if m:
        result["as_number"] = m.group(1)
    for nm in re.finditer(r"peer\s+(\d{1,3}(?:\.\d{1,3}){3})\s+as-number\s+(\d+)", text, re.IGNORECASE):
        result["neighbors"].append({"ip": nm.group(1), "remote_as": nm.group(2)})
    return result


def parse_huawei_bgp_peer(text: str) -> List[Dict[str, Any]]:
    import re
    peers: List[Dict[str, Any]] = []
    for line in text.splitlines():
        m = re.match(r"\s*(\d{1,3}(?:\.\d{1,3}){3})\s+\d+\s+(\d+)\s+\d+\s+\d+\s+\d+\s+(\S+)\s+(\S+)\s+(\d+)", line)
        if m:
            peers.append({
                "ip": m.group(1),
                "as": m.group(2),
                "updown": m.group(3),
                "state": m.group(4),
                "pref_rcv": m.group(5),
            })
    return peers


def parse_huawei_ospf_peer(text: str) -> List[Dict[str, Any]]:
    import re
    peers: List[Dict[str, Any]] = []
    current_area = ""
    current_iface = ""
    for line in text.splitlines():
        la = line.strip()
        am = re.search(r"Area\s+([\d\.]+)\s+interface\s+(\d{1,3}(?:\.\d{1,3}){3})\([^\)]*\)'s neighbors", la, re.IGNORECASE)
        if am:
            current_area = am.group(1)
            current_iface = am.group(2)
            continue
        nm = re.search(r"Router ID:\s+(\d{1,3}(?:\.\d{1,3}){3})\s+Address:\s+(\d{1,3}(?:\.\d{1,3}){3})", la, re.IGNORECASE)
        if nm:
            router_id = nm.group(1)
            addr = nm.group(2)
            state = ""
            sm = re.search(r"State:\s+(\w+)", la, re.IGNORECASE)
            if sm:
                state = sm.group(1)
            peers.append({
                "router_id": router_id,
                "address": addr,
                "state": state,
                "area": current_area,
                "interface": current_iface,
            })
    return peers


# ---------------- Juniper Parsers -----------------

def parse_juniper_interfaces_terse(text: str) -> List[Dict[str, Any]]:
    interfaces: List[Dict[str, Any]] = []
    for line in text.splitlines():
        # Typical: ge-0/0/0 up up inet 192.168.1.1/24
        m = re.match(r"^(\S+)\s+(up|down)\s+(up|down).*?(\d+\.\d+\.\d+\.\d+\/\d+)?", line.strip())
        if m:
            name, phys, proto, ip_cidr = m.groups()
            interfaces.append({
                "name": name,
                "ip": ip_cidr or "N/A",
                "status": f"{phys}/{proto}",
            })
    return interfaces


def parse_juniper_version(text: str) -> Dict[str, Any]:
    info: Dict[str, Any] = {"vendor": "Juniper"}
    m = re.search(r"JUNOS\s+([\w\.-]+)", text)
    if m:
        info["firmware"] = m.group(1)
    return info
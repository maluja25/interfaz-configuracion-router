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

    def is_interface_name(name: str) -> bool:
        # Tipos comunes de interfaces en Huawei
        return bool(re.match(
            r"^(?:Ethernet|GigabitEthernet|XGigabitEthernet|Eth\-Trunk|Vlanif|LoopBack|MEth|GE|FE|Serial|Tunnel|Dialer|Virtual\-Template|NULL)\S*",
            name
        ))

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
        # Filtrar leyendas que algunos equipos imprimen antes de la tabla
        legend_patterns = [
            r"^\*down",
            r"^\^down",
            r"^\(l\)", r"^\(s\)", r"^\(e\)",
            r"^(?:down|up|inactive)\s*:",
            r"^\(d\)\s*:?.*",
            r"^\(u\)\s*:?.*",
        ]
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
        # Evitar capturar líneas como "down:" o "(d):" como interfaces
        if ":" in name or not is_interface_name(name):
            return {}
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

    # Versión VRP (soporta variantes comunes de 'display version')
    m = re.search(r"VRP\s*\(R\)\s*Software,\s*Version\s*([\w\.\-]+)\s*\(([^)]+)\)", text, re.IGNORECASE | re.DOTALL)
    if not m:
        m = re.search(r"VRP.*Version\s+([\w\.\-]+)\s*\(([^)]+)\)", text, re.IGNORECASE | re.DOTALL)
    if m:
        version = m.group(1)
        build = m.group(2)
        di["firmware"] = f"VRP {version} ({build})"
        di["architecture"] = "VRP"
    else:
        # Variante sin paréntesis, p.ej. "Version: V200R003C00"
        mv = re.search(r"Version\s*[:]?\s*([Vv]?[0-9][\w\.\-]+)", text, re.IGNORECASE)
        if mv:
            di["firmware"] = mv.group(1)
        # Si aparece 'Huawei Versatile Routing Platform' inferir arquitectura
        if re.search(r"Versatile\s+Routing\s+Platform", text, re.IGNORECASE) or re.search(r"\bVRP\b", text, re.IGNORECASE):
            di["architecture"] = "VRP"

    # Modelo del dispositivo (múltiples variantes)
    m2 = re.search(r"Board\s+Type\s*:\s*(\S+)", text, re.IGNORECASE)
    if m2:
        di["model"] = m2.group(1)
    else:
        for pat in [
            r"Huawei\s+(\S+)\s+Router\s+uptime",
            r"Device\s+Model\s*:\s*(\S+)",
            r"Product\s+Name\s*:\s*(\S+)",
            r"Model\s*:\s*(\S+)",
            r"Device\s+Type\s*:\s*(\S+)",
        ]:
            m2b = re.search(pat, text, re.IGNORECASE)
            if m2b:
                di["model"] = m2b.group(1)
                break

    # Uptime
    mu = re.search(r"uptime\s+is\s+(.+)", text, re.IGNORECASE)
    if mu:
        di["uptime"] = mu.group(1).strip()
    else:
        mu2 = re.search(r"Router\s+uptime\s+is\s+(.+)", text, re.IGNORECASE)
        if mu2:
            di["uptime"] = mu2.group(1).strip()

    # Memoria RAM
    mr = re.search(r"SDRAM\s+Memory\s+Size\s*:\s*(\d+)\s*M\s*bytes", text, re.IGNORECASE)
    if mr:
        di["ram_memory"] = f"{mr.group(1)} MB"
    else:
        # Permitir 'Memory Size: 512 MB' o 'Mbytes'
        mr2 = re.search(r"Memory\s+Size\s*:\s*(\d+)\s*(?:M\s*bytes|MB)", text, re.IGNORECASE)
        if mr2:
            di["ram_memory"] = f"{mr2.group(1)} MB"
        else:
            mr3 = re.search(r"DRAM\s+Memory\s+Size\s*:\s*(\d+)\s*(?:M\s*bytes|MB)", text, re.IGNORECASE)
            if mr3:
                di["ram_memory"] = f"{mr3.group(1)} MB"

    # Memoria flash
    mf0 = re.search(r"Flash\s+0\s+Memory\s+Size\s*:\s*(\d+)\s*(?:M\s*bytes|MB)", text, re.IGNORECASE)
    mf1 = re.search(r"Flash\s+1\s+Memory\s+Size\s*:\s*(\d+)\s*(?:M\s*bytes|MB)", text, re.IGNORECASE)
    flashes = []
    if mf0:
        flashes.append(f"Flash0 {mf0.group(1)} MB")
    if mf1:
        flashes.append(f"Flash1 {mf1.group(1)} MB")
    if not flashes:
        mf = re.search(r"Flash\s+Memory\s+Size\s*:\s*(\d+)\s*(?:M\s*bytes|MB)", text, re.IGNORECASE)
        if mf:
            flashes.append(f"Flash {mf.group(1)} MB")
    if not flashes:
        # Algunas plataformas imprimen simplemente "Flash: 64MB"
        mf2 = re.search(r"Flash\s*:\s*(\d+)\s*MB", text, re.IGNORECASE)
        if mf2:
            flashes.append(f"Flash {mf2.group(1)} MB")
    if flashes:
        di["flash_memory"] = ", ".join(flashes)

    # Número de serie
    ms = re.search(r"\bSN\s*:\s*(\S+)|Serial\s+Number\s*:\s*(\S+)|Device\s+Serial\s+Number\s*:\s*(\S+)|Serial\s*No\.?\s*:\s*(\S+)", text, re.IGNORECASE)
    if ms:
        # group(4) para "Serial No.:"
        di["serial"] = ms.group(1) or ms.group(2) or ms.group(3) or ms.group(4)

    if di["architecture"] != "N/A":
        di["protocols"] = di["architecture"]

    return di


# ---------------- Huawei Static Routes -----------------

def parse_huawei_static_routes(text: str) -> List[Dict[str, Any]]:
    """Extrae rutas estáticas desde la salida filtrada de Huawei.

    Entrada típica:
    <Huawei>display current-configuration | include ip route-static
     ip route-static 10.10.10.0 255.255.255.0 10.20.20.5
     <Huawei>

    Soporta variantes con "vpn-instance" y máscara en CIDR.
    Devuelve una lista de dicts con claves: dest, mask, next_hop, distance.
    Captura opcional de 'preference <n>' como distancia.
    """
    routes: List[Dict[str, Any]] = []

    def cidr_to_mask(cidr: str) -> str:
        try:
            n = int(cidr)
            mask = (0xffffffff << (32 - n)) & 0xffffffff
            return ".".join(str((mask >> (8 * i)) & 0xff) for i in [3, 2, 1, 0])
        except Exception:
            return ""

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        low = line.lower()
        if low.startswith("<huawei>") or "display current-configuration" in low:
            continue
        # Buscar patrón principal: ip route-static [vpn-instance VRF] dest mask|cidr next-hop
        m = re.search(
            r"ip\s+route-static\s+(?:vpn-instance\s+\S+\s+)?"  # opcional VRF
            r"(\d{1,3}(?:\.\d{1,3}){3})\s+"                     # destino
            r"((?:\d{1,3}(?:\.\d{1,3}){3})|\d{1,2})\s+"       # máscara o CIDR
            r"(\d{1,3}(?:\.\d{1,3}){3})(?:\s+preference\s+(\d{1,3}))?",  # siguiente salto y preferencia
            line,
            re.IGNORECASE,
        )
        if not m:
            continue
        dest = m.group(1)
        mask_or_cidr = m.group(2)
        next_hop = m.group(3)
        dist = (m.group(4) or "") if m.lastindex and m.lastindex >= 4 else ""
        mask = mask_or_cidr if "." in mask_or_cidr else cidr_to_mask(mask_or_cidr)
        routes.append({
            "dest": dest,
            "mask": mask,
            "next_hop": next_hop,
            "distance": dist,
        })

    # Eliminar duplicados básicos
    unique: List[Dict[str, Any]] = []
    seen = set()
    for r in routes:
        key = (r["dest"], r["mask"], r["next_hop"])  # distancia no se considera
        if key in seen:
            continue
        seen.add(key)
        unique.append(r)
    return unique


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

def parse_cisco_interface_section(text: str) -> List[Dict[str, Any]]:
    import re
    results: List[Dict[str, Any]] = []
    for m in re.finditer(r"(?mis)^\s*interface\s+(\S+)\s*([\s\S]*?)(?=^\s*interface\s+\S+|\Z)", text):
        name = m.group(1)
        blk = m.group(2) or ""
        ip = ""
        mask = ""
        ni = re.search(r"(?mi)^\s*no\s+ip\s+address\b", blk)
        if not ni:
            mm = re.search(r"(?mi)^\s*ip\s+address\s+(\d{1,3}(?:\.\d{1,3}){3})\s+(\d{1,3}(?:\.\d{1,3}){3})\b", blk)
            if mm:
                ip = mm.group(1)
                mask = mm.group(2)
        tmatch = re.match(r"^([A-Za-z-]+)", name)
        itype = tmatch.group(1) if tmatch else "Ethernet"
        results.append({"name": name, "type": itype, "ip_address": ip, "mask": mask})
    return results


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

    # Firmware/versión: extraer familia y versión si está disponible
    mv = re.search(r"Cisco IOS Software,\s*([^,\n]+).*?Version\s*([\w\.\(\)]+)", text, re.IGNORECASE | re.DOTALL)
    if mv:
        fam, ver = mv.group(1).strip(), mv.group(2).strip()
        di["firmware"] = f"{fam} {ver}".strip()
    else:
        mv2 = re.search(r"Cisco IOS Software,\s*([\w\-\.]+)", text)
        if mv2:
            di["firmware"] = mv2.group(1)

    mu = re.search(r"uptime\s+is\s+(.+)", text, re.IGNORECASE)
    if mu:
        di["uptime"] = mu.group(1).strip()

    # Modelo: múltiples patrones (varía entre plataformas)
    model_patterns = [
        r"[Cc]isco\s+(\S+)\s+processor",                # Cisco 2911 (revision ...) processor
        r"[Mm]odel\s+number\s*:\s*([A-Za-z0-9\-_/]+)",  # Model number: WS-C2960X-24TS-L
        r"[Pp]ID\s*:\s*([A-Za-z0-9\-_/]+)",             # PID: WS-C2960X-24TS-L
        r"[Cc]isco\s+([A-Za-z0-9\-_/]+)\s*\(",          # Cisco C9300L-24T-4X (...
        r"[Cc]hassis\s+[Tt]ype\s*:\s*([A-Za-z0-9\-_/]+)",
        r"[Hh]ardware\s*:\s*([A-Za-z0-9\-_/]+)",
    ]
    for pat in model_patterns:
        mm = re.search(pat, text)
        if mm:
            di["model"] = mm.group(1)
            break

    # Memoria RAM
    rm = re.search(r"(\d+)\s+Kbytes of memory", text, re.IGNORECASE)
    if rm:
        di["ram_memory"] = f"{rm.group(1)} KB"
    else:
        rm2 = re.search(r"([0-9]+)[ ]?[Kk]\s*bytes of memory", text)
        if rm2:
            di["ram_memory"] = f"{rm2.group(1)} KB"

    # Memoria flash
    fm = re.search(r"(\d+)\s+Kbytes of flash", text, re.IGNORECASE)
    if fm:
        di["flash_memory"] = f"{fm.group(1)} KB"
    else:
        fm2 = re.search(r"([0-9]+)[ ]?[Kk]\s*bytes of flash", text)
        if fm2:
            di["flash_memory"] = f"{fm2.group(1)} KB"

    # Puertos Ethernet (Fast/Gigabit)
    pe = re.search(r"(\d+)\s+(?:Gigabit|Fast)?\s*Ethernet interfaces", text, re.IGNORECASE)
    if pe:
        di["ethernet_ports"] = pe.group(1)

    return di


def parse_cisco_static_routes(text: str) -> List[Dict[str, Any]]:
    """Extrae rutas estáticas desde 'show running-config | sec ip route'.

    Soporta formas comunes:
      ip route <dest> <mask> <next-hop> [distance]
      ip route vrf <VRF> <dest> <mask> <next-hop> [distance]
      ip route <dest> <mask> <ifname> <next-hop> [distance]  (captura next-hop)
    """
    routes: List[Dict[str, Any]] = []

    def is_ip(s: str) -> bool:
        return bool(re.match(r"^\d{1,3}(?:\.\d{1,3}){3}$", s))

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        low = line.lower()
        if low.startswith("cisco#") or "show running-config" in low:
            continue
        if not low.startswith("ip route"):
            continue

        parts = re.split(r"\s+", line)
        # Buscar patrón con o sin 'vrf'
        try:
            idx = 2  # posición del destino
            if parts[2].lower() == "vrf" and len(parts) >= 4:
                idx = 4
            dest = parts[idx]
            mask = parts[idx + 1]
            next_tok = parts[idx + 2] if len(parts) > idx + 2 else ""
            # Capturar next-hop IP; si hay interfaz seguida de IP, tomar la IP
            next_hop = ""
            distance = ""
            if is_ip(next_tok):
                next_hop = next_tok
                if len(parts) > idx + 3 and re.match(r"^\d{1,3}$", parts[idx + 3]):
                    distance = parts[idx + 3]
            else:
                # Posible forma: ip route dest mask <ifname> <ip> [dist]
                if len(parts) > idx + 3 and is_ip(parts[idx + 3]):
                    next_hop = parts[idx + 3]
                    if len(parts) > idx + 4 and re.match(r"^\d{1,3}$", parts[idx + 4]):
                        distance = parts[idx + 4]
            if not next_hop:
                # No soportamos rutas solo con interfaz sin IP
                continue
            routes.append({
                "dest": dest,
                "mask": mask,
                "next_hop": next_hop,
                "distance": distance,
            })
        except Exception:
            continue

    # Deduplicar
    unique: List[Dict[str, Any]] = []
    seen = set()
    for r in routes:
        key = (r["dest"], r["mask"], r["next_hop"], r.get("distance", ""))
        if key in seen:
            continue
        seen.add(key)
        unique.append(r)
    return unique


# ---------------- Cisco OSPF/BGP Config Parsers -----------------

def parse_cisco_ospf_config(text: str) -> Dict[str, Any]:
    """Parsea TODOS los procesos OSPF en un running-config de Cisco.

    Devuelve un diccionario con claves de compatibilidad (process_id, router_id,
    networks) basadas en el primer proceso encontrado y una lista completa en
    'processes' con cada bloque `router ospf <pid>`.
    """
    result: Dict[str, Any] = {"process_id": "", "networks": [], "router_id": "", "processes": []}

    # Encontrar bloques 'router ospf <pid>' y su contenido hasta el siguiente bloque
    # o final del texto.
    for match in re.finditer(r"(?mi)^router\s+ospf\s+(\d+)\b([\s\S]*?)(?=^router\s+ospf\s+\d+\b|\Z)", text):
        pid = match.group(1)
        block = match.group(2)
        # router-id dentro del bloque
        rid_m = re.search(r"router-id\s+(\d{1,3}(?:\.\d{1,3}){3})", block, re.IGNORECASE)
        rid = rid_m.group(1) if rid_m else ""
        # networks dentro del bloque
        nets: List[Dict[str, Any]] = []
        for nm in re.finditer(r"(?i)network\s+(\d{1,3}(?:\.\d{1,3}){3})\s+(\d{1,3}(?:\.\d{1,3}){3})\s+area\s+([\d\.]+)", block):
            nets.append({
                "network": nm.group(1),
                "wildcard": nm.group(2),
                "area": nm.group(3),
            })
        result["processes"].append({
            "process_id": pid,
            "router_id": rid,
            "networks": nets,
        })

    # Compatibilidad: usar el primer proceso (si existe) para rellenar claves planas
    if result["processes"]:
        first = result["processes"][0]
        result["process_id"] = first.get("process_id", "")
        result["router_id"] = first.get("router_id", "")
        result["networks"] = first.get("networks", [])

    return result


def parse_cisco_bgp_config(text: str) -> Dict[str, Any]:
    """Extrae AS, vecinos y VRFs de 'show running-config' Cisco.

    Devuelve:
    - as_number: AS global
    - router_id: router-id global si se define
    - neighbors: lista de vecinos (global/VRF, mezcla)
    - global: {networks: [...], neighbors: [...], config_text: str}
    - vrfs: [{name, router_id, networks: [...], neighbors: [...], config_text: str}]
    """
    result: Dict[str, Any] = {
        "as_number": "",
        "router_id": "",
        "neighbors": [],
        "global": {"networks": [], "neighbors": [], "config_text": ""},
        "vrfs": [],
    }

    # AS global y router-id
    m = re.search(r"(?mi)^\s*router\s+bgp\s+(\d+)\b", text)
    if m:
        result["as_number"] = m.group(1)
    rid = re.search(r"(?mi)^\s*bgp\s+router-id\s+(\d{1,3}(?:\.\d{1,3}){3})\b", text)
    if rid:
        result["router_id"] = rid.group(1)

    # Bloque global address-family ipv4
    gblk_m = re.search(r"(?mis)^\s*address-family\s+ipv4\b([\s\S]*?)^\s*exit-address-family\b", text)
    if gblk_m:
        gblk = gblk_m.group(1)
        result["global"]["config_text"] = gblk.strip()
        # networks
        for nm in re.finditer(r"(?mi)^\s*network\s+(\d{1,3}(?:\.\d{1,3}){3})\s+mask\s+(\d{1,3}(?:\.\d{1,3}){3})\b", gblk):
            result["global"]["networks"].append({"prefix": nm.group(1), "mask": nm.group(2)})
        # neighbors en global
        for nb in re.finditer(r"(?mi)^\s*neighbor\s+(\d{1,3}(?:\.\d{1,3}){3})\s+remote-as\s+(\d+)\b", gblk):
            item = {"ip": nb.group(1), "remote_as": nb.group(2)}
            result["global"]["neighbors"].append(item)
            result["neighbors"].append(item)

    # VRFs: bloques 'address-family ipv4 vrf <NAME>'
    for mvrf in re.finditer(r"(?mis)^\s*address-family\s+ipv4\s+vrf\s+(\S+)\b([\s\S]*?)^\s*exit-address-family\b", text):
        name = mvrf.group(1)
        body = mvrf.group(2)
        vrf: Dict[str, Any] = {"name": name, "router_id": "", "networks": [], "neighbors": [], "config_text": body.strip()}
        rid2 = re.search(r"(?mi)^\s*bgp\s+router-id\s+(\d{1,3}(?:\.\d{1,3}){3})\b", body)
        if rid2:
            vrf["router_id"] = rid2.group(1)
        for nm in re.finditer(r"(?mi)^\s*network\s+(\d{1,3}(?:\.\d{1,3}){3})\s+mask\s+(\d{1,3}(?:\.\d{1,3}){3})\b", body):
            vrf["networks"].append({"prefix": nm.group(1), "mask": nm.group(2)})
        for nb in re.finditer(r"(?mi)^\s*neighbor\s+(\d{1,3}(?:\.\d{1,3}){3})\s+remote-as\s+(\d+)\b", body):
            item = {"ip": nb.group(1), "remote_as": nb.group(2)}
            vrf["neighbors"].append(item)
            result["neighbors"].append(item)
        result["vrfs"].append(vrf)

    # Vecinos globales en otros lugares (fallback)
    for nm in re.finditer(r"(?mi)^\s*neighbor\s+(\d{1,3}(?:\.\d{1,3}){3})\s+remote-as\s+(\d+)\b", text):
        item = {"ip": nm.group(1), "remote_as": nm.group(2)}
        # evitar duplicados
        if item not in result["neighbors"]:
            result["neighbors"].append(item)

    return result


# ---------------- Cisco OSPF/BGP Operational Parsers -----------------

def parse_cisco_ospf_neighbor(text: str) -> List[Dict[str, Any]]:
    """Parsea 'show ip ospf neighbor' de Cisco.

    Devuelve una lista de dicts con: router_id, address, state, area (vacío), interface.
    """
    peers: List[Dict[str, Any]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.lower().startswith("neighbor id"):
            continue
        # Formato típico: <RID> <Pri> <State> <Dead> <Address> <Interface>
        m = re.match(
            r"^(?P<rid>\d{1,3}(?:\.\d{1,3}){3})\s+\d+\s+(?P<state>\S+)\s+(?P<dead>\S+)\s+(?P<addr>\d{1,3}(?:\.\d{1,3}){3})\s+(?P<intf>\S+)$",
            line
        )
        if m:
            peers.append({
                "router_id": m.group("rid"),
                "address": m.group("addr"),
                "state": m.group("state"),
                "dead_time": m.group("dead"),
                "area": "",  # 'show ip ospf neighbor' no muestra área directamente
                "interface": m.group("intf"),
            })
    return peers


def parse_cisco_bgp_summary(text: str) -> List[Dict[str, Any]]:
    """Parsea 'show ip bgp summary' y devuelve lista de peers con columnas completas.

    Columnas: Neighbor, V, AS, MsgRcvd, MsgSent, TblVer, InQ, OutQ, Up/Down, State/PfxRcd.
    Mantiene compatibilidad con claves usadas previamente: ip, as, updown, state, pref_rcv.
    """
    peers: List[Dict[str, Any]] = []
    if re.search(r"BGP\s+not\s+active", text or "", re.IGNORECASE):
        return peers
    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        # Saltar encabezados
        if re.match(r"(?i)^neighbor\b", line):
            continue
        # Formato estándar IOS
        m = re.match(
            r"^(?P<ip>\d{1,3}(?:\.\d{1,3}){3})\s+"  # Neighbor
            r"(?P<v>\d+)\s+"                          # V
            r"(?P<as>\d+)\s+"                         # AS
            r"(?P<msg_rcvd>\d+)\s+"                   # MsgRcvd
            r"(?P<msg_sent>\d+)\s+"                   # MsgSent
            r"(?P<tblver>\S+)\s+"                     # TblVer (puede ser número o '-')
            r"(?P<inq>\d+)\s+"                        # InQ
            r"(?P<outq>\d+)\s+"                       # OutQ
            r"(?P<updown>\S+)\s+"                     # Up/Down
            r"(?P<statepfx>\S+)\s*$",                 # State/PfxRcd
            line
        )
        if not m:
            # Variantes: algunos IOS muestran espacios múltiples o caracteres especiales
            continue
        statepfx = m.group("statepfx")
        state = statepfx
        pref = ""
        if re.match(r"^\d+$", statepfx):
            pref = statepfx
            state = "Established"
        peers.append({
            "ip": m.group("ip"),
            "v": m.group("v"),
            "as": m.group("as"),
            "msg_rcvd": m.group("msg_rcvd"),
            "msg_sent": m.group("msg_sent"),
            "tblver": m.group("tblver"),
            "inq": m.group("inq"),
            "outq": m.group("outq"),
            "updown": m.group("updown"),
            "state": state,
            "pref_rcv": pref,
        })
    return peers


# ---------------- Huawei OSPF/BGP Parsers -----------------

def parse_huawei_ospf_config(text: str) -> Dict[str, Any]:
    """Parsea TODOS los procesos OSPF en una configuración Huawei (VRP).

    Devuelve un dict que mantiene compatibilidad hacia atrás:
    - 'process_id', 'router_id', 'networks' con el primer proceso encontrado
    - 'processes': lista con todos los procesos detectados
    """
    import re

    out: Dict[str, Any] = {
        "process_id": "",
        "router_id": "",
        "networks": [],
        "processes": [],
    }

    # Bloques 'ospf <pid>' hasta el siguiente 'ospf <pid>' o fin
    for m in re.finditer(r"(?mi)^\s*ospf\s+(\d+)\b([\s\S]*?)(?=^\s*ospf\s+\d+\b|\Z)", text):
        pid = m.group(1)
        blk = m.group(2) or ""
        proc: Dict[str, Any] = {
            "process_id": pid,
            "router_id": "",
            "networks": [],
        }

        # router-id dentro del bloque
        rid = re.search(r"(?mi)router[- ]id\s+(\d{1,3}(?:\.\d{1,3}){3})", blk)
        if rid:
            proc["router_id"] = rid.group(1)

        # Áreas y sus redes
        for am in re.finditer(r"(?mi)^\s*area\s+([\d\.]+)\b([\s\S]*?)(?=^\s*area\s+[\d\.]+\b|\Z)", blk):
            area_id = am.group(1)
            body = am.group(2) or ""
            for nm in re.finditer(r"(?mi)^\s*network\s+(\d{1,3}(?:\.\d{1,3}){3})\s+(\d{1,3}(?:\.\d{1,3}){3})\b", body):
                proc["networks"].append({
                    "network": nm.group(1),
                    "wildcard": nm.group(2),
                    "area": area_id,
                })

        out["processes"].append(proc)

    # Compatibilidad: si no se detectaron bloques explícitos, intentar heurísticas
    if not out["processes"]:
        # Intento con variante "OSPF Process <pid>"
        m = re.search(r"OSPF\s+Process\s+(\d+)", text, re.IGNORECASE)
        if m:
            pid = m.group(1)
            proc = {"process_id": pid, "router_id": "", "networks": []}
            rid = re.search(r"router[- ]id\s+(\d{1,3}(?:\.\d{1,3}){3})", text, re.IGNORECASE)
            if rid:
                proc["router_id"] = rid.group(1)
            for am in re.finditer(r"area\s+([\d\.]+)\s*\n([\s\S]*?)(?=\n\s*area\s+|\Z)", text, re.IGNORECASE):
                area_id = am.group(1)
                body = am.group(2) or ""
                for nm in re.finditer(r"network\s+(\d{1,3}(?:\.\d{1,3}){3})\s+(\d{1,3}(?:\.\d{1,3}){3})", body, re.IGNORECASE):
                    proc["networks"].append({
                        "network": nm.group(1),
                        "wildcard": nm.group(2),
                        "area": area_id,
                    })
            out["processes"].append(proc)

    # Poblar claves planas con el primer proceso para UI antigua
    if out["processes"]:
        out["process_id"] = out["processes"][0].get("process_id", "")
        out["router_id"] = out["processes"][0].get("router_id", "")
        out["networks"] = out["processes"][0].get("networks", [])

    return out


def parse_huawei_bgp_config(text: str) -> Dict[str, Any]:
    """Parsea BGP VRP: AS, vecinos, global y VRFs.

    Devuelve:
    - as_number, router_id
    - neighbors: lista combinada
    - global: {networks: [...], imports: [...], neighbors: [...], config_text: str}
    - vrfs: [{name, networks: [...], imports: [...], neighbors: [...], config_text: str}]
    """
    import re
    result: Dict[str, Any] = {
        "as_number": "",
        "router_id": "",
        "neighbors": [],
        "global": {"networks": [], "imports": [], "neighbors": [], "config_text": ""},
        "vrfs": [],
    }

    m = re.search(r"(?mi)^\s*bgp\s+(\d+)\b", text)
    if m:
        result["as_number"] = m.group(1)
    rid = re.search(r"(?mi)^\s*bgp\s+router-id\s+(\d{1,3}(?:\.\d{1,3}){3})\b", text)
    if rid:
        result["router_id"] = rid.group(1)

    # Bloque global 'ipv4-family unicast'
    gblk_m = re.search(r"(?mis)^\s*ipv4-family\s+unicast\b([\s\S]*?)(?=^\s*ipv4-family\b|\Z)", text)
    if gblk_m:
        gblk = gblk_m.group(1)
        result["global"]["config_text"] = gblk.strip()
        for nm in re.finditer(r"(?mi)^\s*network\s+(\d{1,3}(?:\.\d{1,3}){3})\s+(\d{1,3}(?:\.\d{1,3}){3})\b", gblk):
            result["global"]["networks"].append({"prefix": nm.group(1), "mask": nm.group(2)})
        for im in re.finditer(r"(?mi)^\s*import-route\s+(\S+)(?:\s+(\d+))?", gblk):
            proto = im.group(1)
            pid = im.group(2) or ""
            result["global"]["imports"].append({"protocol": proto, "process": pid})
        for nb in re.finditer(r"(?mi)^\s*peer\s+(\d{1,3}(?:\.\d{1,3}){3})\s+as-number\s+(\d+)\b", gblk):
            item = {"ip": nb.group(1), "remote_as": nb.group(2)}
            result["global"]["neighbors"].append(item)
            result["neighbors"].append(item)

    # VRFs: 'ipv4-family vpnv4 vpn-instance <NAME>'
    for mvrf in re.finditer(r"(?mis)^\s*ipv4-family\s+vpnv4\s+vpn-instance\s+(\S+)\b([\s\S]*?)(?=^\s*ipv4-family\b|\Z)", text):
        name = mvrf.group(1)
        body = mvrf.group(2)
        vrf: Dict[str, Any] = {"name": name, "networks": [], "imports": [], "neighbors": [], "config_text": body.strip()}
        for nm in re.finditer(r"(?mi)^\s*network\s+(\d{1,3}(?:\.\d{1,3}){3})\s+(\d{1,3}(?:\.\d{1,3}){3})\b", body):
            vrf["networks"].append({"prefix": nm.group(1), "mask": nm.group(2)})
        for im in re.finditer(r"(?mi)^\s*redistribute\s+(\S+)|^\s*import-route\s+(\S+)(?:\s+(\d+))?", body):
            # Captura 'redistribute static' y 'import-route ospf 1'
            if im.group(1):
                vrf["imports"].append({"protocol": im.group(1), "process": ""})
            else:
                proto = im.group(2)
                pid = im.group(3) or ""
                vrf["imports"].append({"protocol": proto, "process": pid})
        for nb in re.finditer(r"(?mi)^\s*peer\s+(\d{1,3}(?:\.\d{1,3}){3})\s+as-number\s+(\d+)\b", body):
            item = {"ip": nb.group(1), "remote_as": nb.group(2)}
            vrf["neighbors"].append(item)
            result["neighbors"].append(item)
        result["vrfs"].append(vrf)

    # Vecinos definidos fuera de bloques (fallback)
    for nm in re.finditer(r"(?mi)^\s*peer\s+(\d{1,3}(?:\.\d{1,3}){3})\s+as-number\s+(\d+)\b", text):
        item = {"ip": nm.group(1), "remote_as": nm.group(2)}
        if item not in result["neighbors"]:
            result["neighbors"].append(item)
    return result


def parse_huawei_bgp_peer(text: str) -> List[Dict[str, Any]]:
    """Parsea 'display bgp peer' de Huawei.

    Intenta capturar las columnas estándar: Neighbor, V, AS, MsgRcvd, MsgSent,
    TblVer, InQ, OutQ, Up/Down, State/PfxRcd. En plataformas que no muestran
    TblVer/InQ/OutQ, esas columnas se devuelven vacías.
    """
    import re
    peers: List[Dict[str, Any]] = []
    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        # Saltar encabezados
        if re.match(r"(?i)^peer\b|^neighbor\b", line):
            continue
        # Variante completa con TblVer/InQ/OutQ
        m = re.match(
            r"^(?P<ip>\d{1,3}(?:\.\d{1,3}){3})\s+"     # Neighbor
            r"(?P<v>\d+)\s+"                             # V
            r"(?P<as>\d+)\s+"                            # AS
            r"(?P<msg_rcvd>\d+)\s+"                      # MsgRcvd
            r"(?P<msg_sent>\d+)\s+"                      # MsgSent
            r"(?P<tblver>\d+)\s+"                        # TblVer
            r"(?P<inq>\d+)\s+"                           # InQ
            r"(?P<outq>\d+)\s+"                          # OutQ
            r"(?P<updown>\S+)\s+"                        # Up/Down
            r"(?P<statepfx>\S+)\s*$",                    # State/PfxRcd
            line
        )
        if not m:
            # Variante sin TblVer/InQ/OutQ (común en algunos VRP)
            m = re.match(
                r"^(?P<ip>\d{1,3}(?:\.\d{1,3}){3})\s+"   # Neighbor
                r"(?P<v>\d+)\s+"                           # V
                r"(?P<as>\d+)\s+"                          # AS
                r"(?P<msg_rcvd>\d+)\s+"                    # MsgRcvd
                r"(?P<msg_sent>\d+)\s+"                    # MsgSent
                r"(?P<updown>\S+)\s+"                      # Up/Down
                r"(?P<statepfx>\S+)\s*$",                  # State/PfxRcd
                line
            )
        if not m:
            continue
        statepfx = m.group("statepfx")
        state = statepfx
        pref = ""
        if re.match(r"^\d+$", statepfx):
            pref = statepfx
            state = "Established"
        peers.append({
            "ip": m.group("ip"),
            "v": m.groupdict().get("v", ""),
            "as": m.group("as"),
            "msg_rcvd": m.groupdict().get("msg_rcvd", ""),
            "msg_sent": m.groupdict().get("msg_sent", ""),
            "tblver": m.groupdict().get("tblver", ""),
            "inq": m.groupdict().get("inq", ""),
            "outq": m.groupdict().get("outq", ""),
            "updown": m.group("updown"),
            "state": state,
            "pref_rcv": pref,
        })
    return peers


def parse_huawei_ospf_peer(text: str) -> List[Dict[str, Any]]:
    import re
    peers: List[Dict[str, Any]] = []
    current_area = ""
    current_iface_ip = ""
    current_iface_name = ""
    last_peer: Dict[str, Any] | None = None

    for line in text.splitlines():
        la = line.strip()
        # Eliminar prefijos como "[Telnet3]" si existen
        s = re.sub(r"^\[[^\]]+\]\s*", "", la)
        if not la:
            continue

        # Ejemplo: "Area 0.0.0.0 interface 10.10.10.2 (Eth1/0/1)'s neighbors"
        am = re.search(r"Area\s+([\d\.]+)\s+interface\s+(\d{1,3}(?:\.\d{1,3}){3})\s*\(([^\)]+)\)'s neighbors", s, re.IGNORECASE)
        if am:
            current_area = am.group(1)
            current_iface_ip = am.group(2)
            current_iface_name = am.group(3)
            last_peer = None
            continue

        # Inicio de bloque de vecino
        nm = re.search(r"Router ID:\s+(\d{1,3}(?:\.\d{1,3}){3})\s+Address:\s+(\d{1,3}(?:\.\d{1,3}){3})", s, re.IGNORECASE)
        if nm:
            last_peer = {
                "router_id": nm.group(1),
                "address": nm.group(2),
                "state": "",
                "dead_time": "",
                "area": current_area,
                # Priorizar nombre de interfaz si está disponible; si no, usar IP
                "interface": current_iface_name or current_iface_ip,
            }
            peers.append(last_peer)
            continue

        # Línea de estado (suele venir inmediatamente después)
        sm = re.search(r"State:\s*([A-Za-z]+)", s, re.IGNORECASE)
        if sm and last_peer is not None:
            last_peer["state"] = sm.group(1)
            continue

        # Línea de dead timer
        dm = re.search(r"Dead\s+timer\s+due\s+in\s+(\d+)\s+sec", s, re.IGNORECASE)
        if dm and last_peer is not None:
            last_peer["dead_time"] = f"{dm.group(1)} sec"
            continue

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

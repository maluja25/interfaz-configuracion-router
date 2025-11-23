from typing import Dict, Any
from .connections import (
    detect_vendor_ssh,
    detect_vendor_telnet,
    detect_vendor_serial,
    run_ssh_command,
    run_telnet_command,
    run_serial_command,
    run_ssh_commands_batch,
    run_telnet_commands_batch,
    run_serial_commands_batch,
)
from .vendor_commands import (
    DISABLE_PAGING,
    VERSION_COMMAND,
    INTERFACES_BRIEF,
    RUNNING_CONFIG,
    STATIC_ROUTES,
    OSPF_NEIGHBORS,
    BGP_PEERS_SUMMARY,
    OSPF_CONFIG_SECTION,
)
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
    # Permitir sugerencia de vendor para saltar detección y acelerar
    vendor_hint = (connection_data.get("vendor_hint") or "").strip().lower()
    if vendor_hint in ("huawei", "cisco", "juniper"):
        if verbose:
            # Evitar mensaje previo de "Detectando..." si ya hay pista
            print(f"[CLI] Usando pista de fabricante: {vendor_hint}", flush=True)
        return vendor_hint
    if verbose:
        print(f"[CLI] Detectando fabricante via {proto}…", flush=True)
    if proto == "SSH2":
        ven = detect_vendor_ssh(connection_data)
        if verbose:
            print(f"[CLI] Fabricante detectado: {ven}", flush=True)
        if ven in ("huawei", "cisco", "juniper"):
            connection_data["vendor_hint"] = ven
        return ven
    if proto == "Telnet":
        ven = detect_vendor_telnet(connection_data)
        if verbose:
            print(f"[CLI] Fabricante detectado: {ven}", flush=True)
        if ven in ("huawei", "cisco", "juniper"):
            connection_data["vendor_hint"] = ven
        return ven
    if proto == "Serial":
        ven = detect_vendor_serial(connection_data)
        if verbose:
            print(f"[CLI] Fabricante detectado: {ven}", flush=True)
        if ven in ("huawei", "cisco", "juniper"):
            connection_data["vendor_hint"] = ven
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
    # Usar modo rápido para reducir comandos pesados (como running-config)
    fast = bool(connection_data.get("fast_mode"))
    # Prefetch de running-config: por defecto habilitado si ya tenemos vendor_hint
    # para evitar una segunda conexión/comando posterior.
    _prefetch_flag = connection_data.get("prefetch_running_config", None)
    if _prefetch_flag is None:
        prefetch_running = bool((connection_data.get("vendor_hint") or "").strip())
    else:
        prefetch_running = bool(_prefetch_flag)

    def infer_vendor_from_text(text: str) -> str:
        low = (text or "").lower()
        if ("huawei" in low) or ("vrp" in low):
            return "huawei"
        if ("cisco" in low) or ("ios" in low):
            return "cisco"
        if ("juniper" in low) or ("junos" in low):
            return "juniper"
        return "desconocido"

    vendor = _detect_vendor(connection_data)
    ven_key = vendor.lower()

    # Indicar a las conexiones si necesitan deshabilitar paginación.
    # Las conexiones batch ejecutarán los comandos de deshabilitar cuando haga falta.
    connection_data["need_paging_disabled"] = prefetch_running

    # Ejecutar comandos en lote para reducir conexiones
    raw_version = ""
    raw_ifaces = ""
    raw_running = ""
    raw_static_routes = ""
    raw_ospf_peers = ""
    raw_bgp_summary = ""
    raw_ospf_cfg = ""

    cached_ver = connection_data.get("cached_version_output")
    if isinstance(cached_ver, str) and cached_ver.strip():
        if verbose:
            print("[CLI] Usando salida de versión cacheada.", flush=True)
        raw_version = cached_ver
        if vendor in ("desconocido", "unknown"):
            vendor = infer_vendor_from_text(raw_version)
            ven_key = vendor.lower()

    cmds: list[str] = []
    labels: list[str] = []
    if ven_key in ("huawei", "cisco", "juniper"):
        vcmd = VERSION_COMMAND.get(ven_key) or ("display version" if ven_key == "huawei" else "show version")
        icmd = INTERFACES_BRIEF.get(ven_key) or (
            "display ip interface brief" if ven_key == "huawei" else (
                "show interfaces terse" if ven_key == "juniper" else "show ip interface brief"
            )
        )
        if not raw_version:
            cmds.append(vcmd); labels.append("version")
        cmds.append(icmd); labels.append("interfaces")
        if prefetch_running:
            rcfg = RUNNING_CONFIG.get(ven_key) or (
                "display current-configuration" if ven_key == "huawei" else (
                    "show configuration" if ven_key == "juniper" else "show running-config"
                )
            )
            cmds.append(rcfg); labels.append("running")
        # Añadir consulta de rutas estáticas para Huawei
        sroute = STATIC_ROUTES.get(ven_key)
        if sroute and ven_key == "huawei":
            cmds.append(sroute); labels.append("static_routes")
        # Vecinos OSPF y resumen/peers BGP
        ospf_cmd = OSPF_NEIGHBORS.get(ven_key)
        if ospf_cmd:
            cmds.append(ospf_cmd); labels.append("ospf_peers")
        bgp_cmd = BGP_PEERS_SUMMARY.get(ven_key)
        if bgp_cmd:
            cmds.append(bgp_cmd); labels.append("bgp_summary")
        # Sección de configuración OSPF (requerimiento Telnet3: Cisco)
        # Ejecutar siempre que exista el comando para el vendor.
        ocmd = OSPF_CONFIG_SECTION.get(ven_key)
        if ocmd:
            cmds.append(ocmd); labels.append("ospf_cfg")
    else:
        if not raw_version:
            cmds.extend(["display version", "show version"]) ; labels.extend(["version","version"])
        cmds.extend(["display ip interface brief", "show ip interface brief", "show interfaces terse"]) ; labels.extend(["interfaces","interfaces","interfaces"])
        if prefetch_running:
            cmds.extend(["display current-configuration", "show running-config", "show configuration"]) ; labels.extend(["running","running","running"])
        # Intentar sección OSPF con variantes comunes
        cmds.extend(["display current-configuration | section include ospf", "show running-config | sec ospf"]) ; labels.extend(["ospf_cfg","ospf_cfg"])

    if cmds:
        proto = connection_data.get("protocol", "SSH2")
        if proto == "SSH2":
            outs = run_ssh_commands_batch(connection_data, cmds)
        elif proto == "Telnet":
            outs = run_telnet_commands_batch(connection_data, cmds, vendor=ven_key)
        elif proto == "Serial":
            outs = run_serial_commands_batch(connection_data, cmds)
        else:
            outs = []

        # Tomar la primera salida válida por categoría respetando el orden de preferencia
        for out, tag in zip(outs, labels):
            if not out or not out.strip():
                continue
            if tag == "version" and not raw_version:
                raw_version = out
                connection_data["cached_version_output"] = raw_version
                if vendor in ("desconocido", "unknown"):
                    vendor = infer_vendor_from_text(raw_version)
                    ven_key = vendor.lower()
            elif tag == "interfaces" and not raw_ifaces:
                raw_ifaces = out
            elif tag == "running" and not raw_running:
                raw_running = out
            elif tag == "static_routes" and not raw_static_routes:
                raw_static_routes = out
            elif tag == "ospf_peers" and not raw_ospf_peers:
                raw_ospf_peers = out
            elif tag == "bgp_summary" and not raw_bgp_summary:
                raw_bgp_summary = out
            elif tag == "ospf_cfg" and not raw_ospf_cfg:
                raw_ospf_cfg = out

    # Parsear según vendor (si sigue desconocido, intentar heurística básica Huawei/Cisco/Juniper)
    parsed: Dict[str, Any] = {"device_info": {}, "interfaces": []}
    v_for_parse = vendor.lower()
    if v_for_parse == "huawei":
        parsed["device_info"] = parse_huawei_version(raw_version)
        parsed["interfaces"] = parse_huawei_ip_interface_brief(raw_ifaces)
    elif v_for_parse == "cisco":
        parsed["device_info"] = parse_cisco_version(raw_version)
        parsed["interfaces"] = parse_cisco_ip_interface_brief(raw_ifaces)
    elif v_for_parse == "juniper":
        parsed["device_info"] = parse_juniper_version(raw_version)
        parsed["interfaces"] = parse_juniper_interfaces_terse(raw_ifaces)
    else:
        # Heurística: intentar Huawei y Cisco si hay pistas en raw_version
        guess = infer_vendor_from_text(raw_version)
        if guess == "huawei":
            parsed["device_info"] = parse_huawei_version(raw_version)
            parsed["interfaces"] = parse_huawei_ip_interface_brief(raw_ifaces)
            vendor = "huawei"
        elif guess == "cisco":
            parsed["device_info"] = parse_cisco_version(raw_version)
            parsed["interfaces"] = parse_cisco_ip_interface_brief(raw_ifaces)
            vendor = "cisco"
        elif guess == "juniper":
            parsed["device_info"] = parse_juniper_version(raw_version)
            parsed["interfaces"] = parse_juniper_interfaces_terse(raw_ifaces)
            vendor = "juniper"

    parsed["device_info"]["vendor"] = vendor.title() if vendor != "unknown" else "Unknown"
    parsed["analysis_profile"] = "fast" if fast else "full"
    parsed["raw"] = {
        "version": raw_version,
        "interfaces": raw_ifaces,
        "vendor": vendor,
        "running_config": raw_running,
        "static_routes": raw_static_routes,
        "ospf_peers": raw_ospf_peers,
        "bgp_summary": raw_bgp_summary,
        "ospf_config_section": raw_ospf_cfg,
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
from typing import Dict, List


DISABLE_PAGING: Dict[str, List[str]] = {
    "huawei": ["screen-length 0 temporary"],
    "cisco": ["terminal length 0"],
    "juniper": ["set cli screen-length 0"],
}


VERSION_COMMAND: Dict[str, str] = {
    "huawei": "display version",
    "cisco": "show version",
    "juniper": "show version",
}


INTERFACES_BRIEF: Dict[str, str] = {
    "huawei": "display ip interface brief",
    "cisco": "show ip interface brief",
    "juniper": "show interfaces terse",
}

# Comando para obtener la configuración en ejecución por fabricante
RUNNING_CONFIG: Dict[str, str] = {
    "huawei": "display current-configuration",
    "cisco": "show running-config",
    "juniper": "show configuration",
}

INTERFACE_CONFIG_SECTION: Dict[str, str] = {
    "cisco": "show running-config | sec interface",
}

# Comandos para obtener rutas estáticas por fabricante (filtradas)
STATIC_ROUTES: Dict[str, str] = {
    "huawei": "display current-configuration | include ip route-static",
    # Referencias opcionales para otros vendors (no usados en este requerimiento)
    "cisco": "show running-config | sec ip route",
    "juniper": "show configuration | display set | match 'set routing-options static route'",
}

# Comandos para vecinos OSPF por fabricante
OSPF_NEIGHBORS: Dict[str, str] = {
    "huawei": "display ospf peer",
    "cisco": "show ip ospf neighbor",
    "juniper": "show ospf neighbor",
}

# Comandos para resumen/peers de BGP por fabricante
BGP_PEERS_SUMMARY: Dict[str, str] = {
    "huawei": "display bgp peer",
    "cisco": "show ip bgp summary",
    "juniper": "show bgp summary",
}

# Comandos para obtener solo la sección de OSPF en running-config
OSPF_CONFIG_SECTION: Dict[str, str] = {
    "cisco": "show running-config | sec ospf",
    # En Huawei puede variar según modelo
    "huawei": "display current-configuration | section include ospf",
}

# Comandos para obtener solo la sección de BGP en la configuración por fabricante
BGP_CONFIG_SECTION: Dict[str, str] = {
    # Cisco: filtra el bloque de BGP
    "cisco": "show running-config | sec bgp",
    # Huawei VRP: algunas versiones usan 'section include', otras 'sec inc'
    "huawei": "display current-configuration | section include bgp",
    # Juniper no aplica directamente; se omite
}

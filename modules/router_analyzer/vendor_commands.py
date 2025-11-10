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
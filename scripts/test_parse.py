import sys
import os

# Add the parent directory to sys.path to allow module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.router_analyzer import RouterAnalyzer

# Simular datos de conexión mínimos
conn = {'protocol': 'SSH2', 'hostname': '192.0.2.1'}
ra = RouterAnalyzer(conn)
ra.is_connected = True

# Construir análisis simulado con datos brutos mínimos (Cisco-like)
analysis = {
    'device_type': 'generic',
    'protocol': 'SSH2',
    'target': '192.0.2.1',
    'connected': True,
    'vendor': 'cisco',
    'commands_executed': ['terminal length 0', 'show version', 'show ip interface brief'],
    'data': {
        'cisco_show_version': (
            'Cisco IOS Software, C2900 Software (C2900-UNIVERSALK9-M), Version 15.2(2)E\n'
            'Router uptime is 32 minutes\n'
            'Cisco 2911 (revision 1.0) processor with 524288K/131072K bytes of memory.\n'
            '512 Kbytes of flash'
        ),
        'cisco_ip_int_brief': (
            'Interface              IP-Address      OK? Method Status                Protocol\n'
            'Ethernet0/0           192.168.127.129 YES manual up                    up\n'
            'Ethernet0/1           unassigned      YES manual down                  down\n'
            'Ethernet0/2           unassigned      YES manual down                  down\n'
            'Ethernet0/3           unassigned      YES manual down                  down\n'
            'Loopback0             10.10.20.1      YES manual up                    up\n'
        ),
    }
}

parsed = ra.parse_analysis_data(analysis)
print('keys:', sorted(parsed.keys()))
print('device_info:', parsed.get('device_info'))
print('interfaces_count:', len(parsed.get('interfaces', [])))
print('neighbors:', parsed.get('neighbors'))
print('routing_protocols:', parsed.get('routing_protocols'))

# ---- Huawei sample test ----
from modules.router_analyzer.parsers import parse_huawei_version, parse_huawei_ip_interface_brief

huawei_version_sample = (
    'Huawei Versatile Routing Platform Software\n'
    'Version: V200R003C00\n'
    'Board Type : AR1220\n'
    'Router uptime is 1 week, 2 days, 03 hours, 12 minutes\n'
    'SDRAM Memory Size : 512 M bytes\n'
    'Flash 0 Memory Size : 64 M bytes\n'
    'Serial No.: 210231A12345ABCD\n'
)

huawei_if_brief_sample = (
    'Interface                         IP Address/Mask      Physical  Protocol\n'
    'GigabitEthernet0/0/0             192.168.1.1/24       up        up\n'
    'GigabitEthernet0/0/1             0.0.0.0/0            down      down\n'
    'Vlanif10                         10.10.10.1/24        up        up\n'
)

print('\n--- Huawei parse smoke test ---')
print('device_info:', parse_huawei_version(huawei_version_sample))
print('interfaces:', parse_huawei_ip_interface_brief(huawei_if_brief_sample))

# ---- Prompt vendor detection smoke tests ----
from modules.router_analyzer.connections import _vendor_from_prompt

print('\n--- Prompt vendor detection smoke tests ---')
samples = {
    'cisco_enable': 'Router#',
    'cisco_exec': 'Switch>',
    'juniper_operational': 'lab@mx480>',
    'huawei_angle': '<Huawei>',
    'huawei_square': '[Huawei]',
}
for name, sample in samples.items():
    print(name, '->', _vendor_from_prompt(sample))

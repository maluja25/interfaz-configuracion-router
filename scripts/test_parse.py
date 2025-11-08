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

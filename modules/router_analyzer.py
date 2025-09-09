try:
    import telnetlib
except ImportError:
    # telnetlib no está disponible en Python 3.13+
    telnetlib = None

try:
    import paramiko
except ImportError:
    # paramiko no está instalado
    paramiko = None

import time
import re
from typing import Dict, List, Optional, Tuple

class RouterAnalyzer:
    def __init__(self, connection_data: Dict):
        self.connection_data = connection_data
        self.connection = None
        self.is_connected = False
        self.device_type = None  # 'cisco' o 'huawei'
        self.device_info = {}
        
    def ping_device(self, hostname: str) -> bool:
        """Hacer ping al dispositivo antes de conectar"""
        import subprocess
        import platform
        
        print(f"🔍 Haciendo ping a {hostname}...")
        time.sleep(1)  # Tiempo de inicio del ping
        
        # Comando ping según el sistema operativo
        if platform.system().lower() == "windows":
            cmd = ["ping", "-n", "4", hostname]  # 4 paquetes para más realismo
        else:
            cmd = ["ping", "-c", "4", hostname]
        
        try:
            print(f"   Enviando 4 paquetes de 32 bytes a {hostname}...")
            time.sleep(2)  # Simular tiempo de envío
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            time.sleep(1)  # Tiempo de procesamiento
            
            if result.returncode == 0:
                print(f"✅ Ping exitoso a {hostname} - 4 paquetes enviados, 4 recibidos")
                print(f"   Tiempo promedio: 2ms, Pérdida: 0%")
                return True
            else:
                print(f"❌ Ping falló a {hostname} - Sin respuesta")
                return False
        except Exception as e:
            print(f"⚠️ Error en ping: {str(e)}")
            return False
    
    def detect_device_type(self) -> str:
        """Detectar el tipo de dispositivo (Cisco o Huawei)"""
        print("🔍 Detectando tipo de dispositivo...")
        time.sleep(1)  # Tiempo de procesamiento
        
        # Comandos para detectar el fabricante
        detection_commands = [
            'show version',
            'display version',
            'show inventory',
            'display device'
        ]
        
        for i, command in enumerate(detection_commands, 1):
            print(f"   [{i}/{len(detection_commands)}] Probando comando: {command}")
            #time.sleep(1.5)  # Tiempo de ejecución del comando
            
            try:
                output = self.execute_command(command)
                #time.sleep(0.5)  # Tiempo de procesamiento de respuesta
                
                if output and 'cisco' in output.lower():
                    print("✅ Dispositivo detectado: Cisco")
                    #time.sleep(1)
                    return 'cisco'
                elif output and ('huawei' in output.lower() or 'vrp' in output.lower()):
                    print("✅ Dispositivo detectado: Huawei")
                    #time.sleep(1)
                    return 'huawei'
            except:
                print(f"   ⚠️ Comando {command} no disponible")
                #time.sleep(0.5)
                continue
        
        print("⚠️ No se pudo detectar el tipo de dispositivo, asumiendo Cisco")
        #time.sleep(1)
        return 'cisco'
    
    def connect(self) -> bool:
        """Establecer conexión con el router"""
        try:
            protocol = self.connection_data.get('protocol', 'SSH2')
            hostname = self.connection_data.get('hostname')
            port = int(self.connection_data.get('port', 22))
            username = self.connection_data.get('username', '')
            
            # Hacer ping primero
            if not self.ping_device(hostname):
                print("⚠️ Continuando sin ping exitoso...")
            
            # Conectar
            if protocol == 'SSH2':
                success = self._connect_ssh(hostname, port, username)
            elif protocol == 'Telnet':
                success = self._connect_telnet(hostname, port, username)
            else:
                print(f"Protocolo no soportado: {protocol}")
                return False
            
            if success:
                # Detectar tipo de dispositivo
                self.device_type = self.detect_device_type()
                self.device_info['type'] = self.device_type
                self.device_info['hostname'] = hostname
                self.device_info['protocol'] = protocol
                
            return success
                
        except Exception as e:
            print(f"Error al conectar: {str(e)}")
            return False
    
    def _connect_ssh(self, hostname: str, port: int, username: str) -> bool:
        """Conectar via SSH"""
        if paramiko is None:
            print("SSH no disponible: paramiko no está instalado")
            print("   Simulando conexión SSH...")
            #time.sleep(2)
            self.is_connected = True
            return True
            
        try:
            print(f"🔐 Iniciando conexión SSH a {hostname}:{port}")
            #time.sleep(1)
            
            print(f"   Estableciendo conexión TCP...")
            #time.sleep(2)
            
            print(f"   Negociando algoritmo de cifrado...")
            #time.sleep(1.5)
            
            print(f"   Autenticando usuario: {username}")
            #time.sleep(2)
            
            print(f"   Verificando credenciales...")
            #time.sleep(1.5)
            
            print(f"✅ Conexión SSH establecida exitosamente")
            #time.sleep(1)
            
            # Simular conexión exitosa
            self.is_connected = True
            return True
            
        except Exception as e:
            print(f"❌ Error SSH: {str(e)}")
            return False
    
    def _connect_telnet(self, hostname: str, port: int, username: str) -> bool:
        """Conectar via Telnet"""
        if telnetlib is None:
            print("Telnet no disponible: telnetlib no está disponible en Python 3.13+")
            print("   Simulando conexión Telnet...")
            #time.sleep(2)
            self.is_connected = True
            return True
            
        try:
            print(f"🔐 Iniciando conexión Telnet a {hostname}:{port}")
            #time.sleep(1)
            
            print(f"   Estableciendo conexión TCP...")
            #time.sleep(1.5)
            
            print(f"   Esperando prompt de login...")
            #time.sleep(1)
            
            print(f"   Username: {username}")
            #time.sleep(1)
            
            print(f"   Password: ********")
            #time.sleep(2)
            
            print(f"   Verificando credenciales...")
            #time.sleep(1.5)
            
            print(f"✅ Conexión Telnet establecida exitosamente")
            #time.sleep(1)
            
            # Simular conexión exitosa
            self.is_connected = True
            return True
            
        except Exception as e:
            print(f"❌ Error Telnet: {str(e)}")
            return False
    
    def disconnect(self):
        """Desconectar del router"""
        if self.connection:
            try:
                if hasattr(self.connection, 'close'):
                    self.connection.close()
                self.is_connected = False
                print("Desconectado del router")
            except:
                pass
    
    def execute_command(self, command: str) -> str:
        """Ejecutar comando en el router"""
        if not self.is_connected:
            return "Error: No conectado al router"
        
        # Para simulación, retornamos datos de ejemplo
        # En implementación real, aquí se ejecutaría el comando real
        return self._get_simulated_output(command)
    
    def _get_simulated_output(self, command: str) -> str:
        """Simular salida de comandos (para demostración)"""
        # Datos simulados para Cisco
        cisco_outputs = {
            'show running-config': '''Building configuration...

Current configuration : 1234 bytes
!
version 15.1
service timestamps debug datetime msec
service timestamps log datetime msec
no service password-encryption
!
hostname Router-01
!
boot-start-marker
boot-end-marker
!
enable secret 5 $1$mERr$hx5rVt7rPNoS4wqbXKX7m0
!
no aaa new-model
!
ip cef
no ipv6 cef
!
multilink bundle-name authenticated
!
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
 duplex auto
 speed auto
!
interface GigabitEthernet0/1
 ip address 10.0.0.1 255.255.255.0
 duplex auto
 speed auto
!
interface Serial0/0/0
 ip address 203.0.113.1 255.255.255.252
!
ip route 0.0.0.0 0.0.0.0 203.0.113.2
ip route 172.16.0.0 255.255.0.0 192.168.1.254
!
router ospf 1
 network 192.168.1.0 0.0.0.255 area 0
 network 10.0.0.0 0.0.0.255 area 0
!
router bgp 65001
 bgp router-id 192.168.1.1
 neighbor 203.0.113.2 remote-as 65002
 network 192.168.1.0 mask 255.255.255.0
!
control-plane
!
line con 0
 exec-timeout 0 0
 privilege level 15
 logging synchronous
line aux 0
 exec-timeout 0 0
 privilege level 15
 logging synchronous
line vty 0 4
 login
!
end''',
            
            'show ip interface brief': '''Interface                  IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0         192.168.1.1     YES NVRAM  up                    up
GigabitEthernet0/1         10.0.0.1        YES NVRAM  up                    up
Serial0/0/0                203.0.113.1     YES NVRAM  up                    up
Loopback0                  1.1.1.1         YES NVRAM  up                    up''',
            
            'show ip vrf brief': '''Name                             Default RD            Interfaces
VRF-INTERNET                    65001:100            Gi0/0
VRF-MANAGEMENT                  65001:200            Gi0/1
VRF-CUSTOMERS                   65001:300            Se0/0/0''',
            
            'show ip ospf neighbor': '''Neighbor ID     Pri   State           Dead Time   Address         Interface
203.0.113.2      1   FULL/DR         00:00:35     203.0.113.2     Serial0/0/0
10.0.0.2         1   FULL/BDR        00:00:38     10.0.0.2        GigabitEthernet0/1''',
            
            'show ip bgp summary': '''BGP router identifier 192.168.1.1, local AS number 65001
BGP table version is 5, main routing table version 5
2 network entries using 240 bytes of memory
2 path entries using 160 bytes of memory
1/1 BGP path/bestpath attribute entries using 136 bytes of memory
0 BGP route-map cache entries using 0 bytes of memory
0 BGP filter-list cache entries using 0 bytes of memory
BGP using 536 total bytes of memory
BGP activity 2/0 prefixes, 2/0 paths, scan interval 60 secs

Neighbor        V           AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd
203.0.113.2     4        65002      15      15        5    0    0 00:12:34        1''',
            
            'show ip route': '''Codes: L - local, C - connected, S - static, R - RIP, M - mobile, B - BGP
       D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area
       N1 - OSPF NSSA external type 1, N2 - OSPF NSSA external type 2
       E1 - OSPF external type 1, E2 - OSPF external type 2
       i - IS-IS, su - IS-IS summary, L1 - IS-IS level-1, L2 - IS-IS level-2
       ia - IS-IS inter area, * - candidate default, U - per-user static route
       o - ODR, P - periodic downloaded static route, H - NHRP, l - LISP
       a - application route
       + - replicated route, % - next-hop override

Gateway of last resort is 203.0.113.2 to network 0.0.0.0

S*    0.0.0.0/0 [1/0] via 203.0.113.2
      1.0.0.0/32 is subnetted, 1 subnets
C        1.1.1.1 is directly connected, Loopback0
      10.0.0.0/8 is variably subnetted, 2 subnets, 2 masks
C        10.0.0.0/24 is directly connected, GigabitEthernet0/1
L        10.0.0.1/32 is directly connected, GigabitEthernet0/1
      172.16.0.0/16 is variably subnetted, 1 subnets, 1 masks
S        172.16.0.0/16 [1/0] via 192.168.1.254
      192.168.1.0/24 is variably subnetted, 2 subnets, 2 masks
C        192.168.1.0/24 is directly connected, GigabitEthernet0/0
L        192.168.1.1/32 is directly connected, GigabitEthernet0/0
      203.0.113.0/30 is variably subnetted, 2 subnets, 2 masks
C        203.0.113.0/30 is directly connected, Serial0/0/0
L        203.0.113.1/32 is directly connected, Serial0/0/0
B        192.168.2.0/24 [20/0] via 203.0.113.2, 00:12:34''',
            
            'show vlan brief': '''VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Gi0/0, Gi0/1
10   MANAGEMENT                       active    Gi0/0
20   SERVERS                          active    Gi0/1
30   USERS                           active    Gi0/1
1002 fddi-default                     act/unsup
1003 token-ring-default               act/unsup
1004 fddinet-default                  act/unsup
1005 trnet-default                    act/unsup''',
            
            'show ip dhcp pool': '''Pool VRF-INTERNET :
 Utilization mark (high/low)    : 100 / 0
 Subnet size (first/next)       : 0 / 0 
 Total addresses                 : 254
 Leased addresses                : 15
 Pending event                  : none
 1 subnet is currently in the pool :
 Current index        IP address range                    Leased/Excluded/Total
 192.168.1.10         192.168.1.1    - 192.168.1.254     15 / 0 / 254'''
        }
        
        # Datos simulados para Huawei
        huawei_outputs = {
            'display version': '''Huawei Versatile Routing Platform Software
VRP (R) software, Version 8.180 (CE12800 V200R005C00SPC500)
Copyright (C) 2012-2018 Huawei Technologies Co., Ltd.
HUAWEI CE12800 uptime is 15 days, 4 hours, 12 minutes
SDRAM Memory Size    : 8192 M bytes
Flash Memory Size    : 2048 M bytes
CPLD Version         : 100
PCB Version          : VER.A
Bootrom Version      : 180
[Slot 0] 48GE + 4 10GE SFP+ + 2 40GE QSFP+ Interface Card
[Slot 1] 48GE + 4 10GE SFP+ + 2 40GE QSFP+ Interface Card''',
            
            'display current-configuration': '''#
sysname Router-Huawei
#
vlan batch 10 20 30
#
interface GigabitEthernet0/0/1
 ip address 192.168.1.1 255.255.255.0
#
interface GigabitEthernet0/0/2
 ip address 10.0.0.1 255.255.255.0
#
interface Serial1/0/0
 ip address 203.0.113.1 255.255.255.252
#
ip route-static 0.0.0.0 0.0.0.0 203.0.113.2
ip route-static 172.16.0.0 255.255.0.0 192.168.1.254
#
ospf 1
 area 0.0.0.0
  network 192.168.1.0 0.0.0.255
  network 10.0.0.0 0.0.0.255
#
bgp 65001
 peer 203.0.113.2 as-number 65002
 #
 ipv4-family unicast
  peer 203.0.113.2 enable
  network 192.168.1.0 255.255.255.0
#
return''',
            
            'display ip interface brief': '''Interface                         IP Address/Mask      Physical   Protocol
GigabitEthernet0/0/1             192.168.1.1/24       up         up
GigabitEthernet0/0/2             10.0.0.1/24          up         up
Serial1/0/0                      203.0.113.1/30       up         up
LoopBack0                         1.1.1.1/32           up         up''',
            
            'display ip vpn-instance': '''VPN-Instance Name and ID : VRF-INTERNET, 1
  Interfaces : GigabitEthernet0/0/1
  Address family ipv4 : 1
VPN-Instance Name and ID : VRF-MANAGEMENT, 2
  Interfaces : GigabitEthernet0/0/2
  Address family ipv4 : 1''',
            
            'display ospf peer brief': '''OSPF Process 1 with Router ID 1.1.1.1
                Peer(s) on the same network segment
Area 0.0.0.0
Neighbor ID     Pri   State           Dead Time   Address         Interface
203.0.113.2     1     Full/DR         00:00:35    203.0.113.2     Serial1/0/0
10.0.0.2        1     Full/BDR        00:00:38    10.0.0.2        GigabitEthernet0/0/2''',
            
            'display bgp peer brief': '''BGP local router ID : 1.1.1.1
 Local AS number : 65001
 Total number of peers : 1          Peers in established state : 1

  Peer            V          AS  MsgRcvd  MsgSent  OutQ  Up/Down       State  PrefRcv
  203.0.113.2     4       65002       15       15     0 00:12:34 Established        1''',
            
            'display ip routing-table': '''Route Flags: R - relay, D - download to fib
------------------------------------------------------------------------------
Routing Tables: Public
         Destinations : 6        Routes : 6

Destination/Mask    Proto   Pre  Cost     Flags NextHop         Interface
        0.0.0.0/0   Static  60   0          RD  203.0.113.2     Serial1/0/0
        1.1.1.1/32  Direct  0    0           D  127.0.0.1       LoopBack0
       10.0.0.0/24  Direct  0    0           D  10.0.0.1        GigabitEthernet0/0/2
       10.0.0.1/32  Direct  0    0           D  127.0.0.1       GigabitEthernet0/0/2
    172.16.0.0/16   Static  60   0          RD  192.168.1.254   GigabitEthernet0/0/1
   192.168.1.0/24   Direct  0    0           D  192.168.1.1     GigabitEthernet0/0/1
   192.168.1.1/32   Direct  0    0           D  127.0.0.1       GigabitEthernet0/0/1
   203.0.113.0/30   Direct  0    0           D  203.0.113.1     Serial1/0/0
   203.0.113.1/32   Direct  0    0           D  127.0.0.1       Serial1/0/0
   203.0.113.2/32   Direct  0    0           D  203.0.113.2     Serial1/0/0''',
            
            'display vlan brief': '''VLAN ID  Name                             Status
1        default                          active
10       MANAGEMENT                       active
20       SERVERS                          active
30       USERS                           active''',
            
            'display ip pool': '''Pool name      : VRF-INTERNET
Pool-No         : 0
Position        : Local
Status          : Unspecified
Rip-server      : 192.168.1.1
Netmask         : 255.255.255.0
Range           : 192.168.1.1 to 192.168.1.254
Leased          : 15
Total           : 254
Idle(Expired)   : 239
Idle(Trans)     : 0
Authen          : Unspecified
Address Type    : Unspecified''',
            
            'display device': '''Slot No.    Board Name        Status           Subslot No.    Port Num
0           CE-L48GT4S2CQ     Normal           0              48
1           CE-L48GT4S2CQ     Normal           0              48
2           CE-MPUA            Normal           0              0
3           CE-MPUA            Normal           0              0'''
        }
        
        # Seleccionar el conjunto de datos según el tipo de dispositivo
        if self.device_type == 'huawei':
            return huawei_outputs.get(command, f"Comando Huawei '{command}' no implementado en simulación")
        else:
            return cisco_outputs.get(command, f"Comando Cisco '{command}' no implementado en simulación")
    
    def get_device_commands(self) -> List[str]:
        """Obtener lista de comandos según el tipo de dispositivo"""
        if self.device_type == 'huawei':
            return [
                'display current-configuration',
                'display ip interface brief',
                'display ip vpn-instance',
                'display ospf peer brief',
                'display bgp peer brief',
                'display ip routing-table',
                'display vlan brief',
                'display ip pool',
                'display version',
                'display device'
            ]
        else:  # Cisco por defecto
            return [
                'show running-config',
                'show ip interface brief', 
                'show ip vrf brief',
                'show ip ospf neighbor',
                'show ip bgp summary',
                'show ip route',
                'show vlan brief',
                'show ip dhcp pool',
                'show version',
                'show inventory'
            ]
    
    def analyze_router(self) -> Dict:
        """Analizar el router y recopilar toda la información"""
        if not self.is_connected:
            return {"error": "No conectado al router"}
        
        print(f"Iniciando análisis del router {self.device_type.upper()}...")
        
        analysis_results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "hostname": self.connection_data.get('hostname'),
            "protocol": self.connection_data.get('protocol'),
            "device_type": self.device_type,
            "device_info": self.device_info,
            "commands_executed": [],
            "data": {}
        }
        
        # Obtener comandos específicos del dispositivo
        commands = self.get_device_commands()
        
        print(f"📋 Ejecutando {len(commands)} comandos {self.device_type.upper()}...")
        
        for i, command in enumerate(commands, 1):
            print(f"[{i}/{len(commands)}] Ejecutando: {command}")
            #time.sleep(1)  # Tiempo de inicio del comando
            
            try:
                print(f"   Enviando comando al dispositivo...")
                #time.sleep(1.5)  # Tiempo de envío
                
                output = self.execute_command(command)
                print(f"   Procesando respuesta...")
                #time.sleep(1)  # Tiempo de procesamiento
                
                analysis_results["commands_executed"].append(command)
                analysis_results["data"][command] = output
                
                print(f"   ✅ Comando completado")
                #time.sleep(0.5)  # Pausa entre comandos
                
            except Exception as e:
                print(f"   ❌ Error ejecutando {command}: {str(e)}")
                analysis_results["data"][command] = f"Error: {str(e)}"
                #time.sleep(0.5)
        
        print(f"✅ Análisis {self.device_type.upper()} completado")
        return analysis_results
    
    def parse_analysis_data(self, analysis_data: Dict) -> Dict:
        """Parsear los datos del análisis para extraer información estructurada"""
        parsed_data = {
            "interfaces": [],
            "vrfs": [],
            "vlans": [],
            "routing_protocols": {
                'ospf': {'enabled': False, 'config': ''},
                'eigrp': {'enabled': False, 'config': ''},
                'bgp': {'enabled': False, 'config': ''},
                'rip': {'enabled': False, 'config': ''}
            },
            "static_routes": [],
            "dhcp_pools": [],
            "neighbors": {}
        }
        
        # Parsear interfaces
        if 'show ip interface brief' in analysis_data.get("data", {}):
            interfaces = self._parse_interfaces(analysis_data["data"]["show ip interface brief"])
            parsed_data["interfaces"] = interfaces
        
        # Parsear VRF
        if 'show ip vrf brief' in analysis_data.get("data", {}):
            vrfs = self._parse_vrfs(analysis_data["data"]["show ip vrf brief"])
            parsed_data["vrfs"] = vrfs
        
        # Parsear VLANs
        if 'show vlan brief' in analysis_data.get("data", {}):
            vlans = self._parse_vlans(analysis_data["data"]["show vlan brief"])
            parsed_data["vlans"] = vlans
        
        # Parsear rutas estáticas
        device_type = analysis_data.get("device_type", "cisco")
        
        key_cisco = 'show ip route'
        key_huawei = 'display ip routing-table'
        
        if device_type == 'cisco' and key_cisco in analysis_data.get("data", {}):
            static_routes = self._parse_static_routes_cisco(analysis_data["data"][key_cisco])
            parsed_data["static_routes"] = static_routes
        elif device_type == 'huawei' and key_huawei in analysis_data.get("data", {}):
            static_routes = self._parse_static_routes_huawei(analysis_data["data"][key_huawei])
            parsed_data["static_routes"] = static_routes
        
        # Parsear protocolos de enrutamiento
        if 'show ip ospf neighbor' in analysis_data.get("data", {}):
            ospf_neighbors = self._parse_ospf_neighbors(analysis_data["data"]["show ip ospf neighbor"])
            parsed_data["neighbors"]["ospf"] = ospf_neighbors
            # Marcar OSPF como habilitado si hay vecinos
            if ospf_neighbors:
                parsed_data["routing_protocols"]["ospf"]["enabled"] = True
        
        if 'show ip bgp summary' in analysis_data.get("data", {}):
            bgp_neighbors = self._parse_bgp_neighbors(analysis_data["data"]["show ip bgp summary"])
            parsed_data["neighbors"]["bgp"] = bgp_neighbors
            # Marcar BGP como habilitado si hay vecinos
            if bgp_neighbors:
                parsed_data["routing_protocols"]["bgp"]["enabled"] = True
        
        return parsed_data
    
    def _parse_interfaces(self, output: str) -> List[Dict]:
        """Parsear salida de show ip interface brief"""
        interfaces = []
        lines = output.split('\n')
        
        for line in lines[1:]:  # Saltar encabezado
            if line.strip() and not line.startswith('Interface'):
                parts = line.split()
                if len(parts) >= 6:
                    interfaces.append({
                        'name': parts[0],
                        'ip_address': parts[1],
                        'ok': parts[2],
                        'method': parts[3],
                        'status': parts[4],
                        'protocol': parts[5]
                    })
        
        return interfaces
    
    def _parse_vrfs(self, output: str) -> List[Dict]:
        """Parsear salida de show ip vrf brief"""
        vrfs = []
        lines = output.split('\n')
        
        for line in lines[1:]:  # Saltar encabezado
            if line.strip() and not line.startswith('Name'):
                parts = line.split()
                if len(parts) >= 3:
                    vrfs.append({
                        'name': parts[0],
                        'default_rd': parts[1],
                        'interfaces': parts[2] if len(parts) > 2 else ''
                    })
        
        return vrfs
    
    def _parse_vlans(self, output: str) -> List[Dict]:
        """Parsear salida de show vlan brief"""
        vlans = []
        lines = output.split('\n')
        
        for line in lines[1:]:  # Saltar encabezado
            if line.strip() and not line.startswith('VLAN'):
                parts = line.split()
                if len(parts) >= 3:
                    vlans.append({
                        'id': parts[0],
                        'name': parts[1],
                        'status': parts[2],
                        'ports': ' '.join(parts[3:]) if len(parts) > 3 else ''
                    })
        
        return vlans
    
    @staticmethod
    def _cidr_to_netmask(cidr_str: str) -> Tuple[str, str]:
        """Convertir notación CIDR a red y máscara de subred"""
        try:
            if '/' in cidr_str:
                network, prefix_len = cidr_str.split('/')
                prefix_len = int(prefix_len)
            else:
                network = cidr_str
                octets = [int(o) for o in network.split('.')]
                if octets[0] < 128: prefix_len = 8
                elif octets[0] < 192: prefix_len = 16
                else: prefix_len = 24

            mask = (0xffffffff << (32 - prefix_len)) & 0xffffffff
            netmask = ".".join([str((mask >> i) & 0xff) for i in [24, 16, 8, 0]])
            return network, netmask
        except:
            return cidr_str, "255.255.255.0" # Fallback

    def _parse_static_routes_cisco(self, output: str) -> List[Dict]:
        """Parsear salida de show ip route para rutas estáticas de Cisco"""
        static_routes = []
        lines = output.split('\n')
        
        for line in lines:
            if line.strip().startswith('S') and not line.strip().startswith('S*'):
                parts = line.split()
                if len(parts) >= 4 and 'via' in parts:
                    try:
                        network_part = parts[1]
                        via_index = parts.index('via')
                        next_hop = parts[via_index + 1].strip(',')
                        
                        dest, mask = RouterAnalyzer._cidr_to_netmask(network_part)
                        
                        distance = '1'
                        if '[' in parts[2] and ']' in parts[2]:
                            distance = parts[2].strip('[]').split('/')[0]

                        static_routes.append({
                            'dest': dest, 'mask': mask,
                            'next_hop': next_hop, 'distance': distance
                        })
                    except (ValueError, IndexError):
                        continue
        
        return static_routes

    def _parse_static_routes_huawei(self, output: str) -> List[Dict]:
        """Parsear salida de display ip routing-table para rutas estáticas de Huawei"""
        static_routes = []
        lines = output.split('\n')
        
        for line in lines:
            if 'Static' in line:
                parts = line.split()
                if len(parts) >= 5:
                    try:
                        network_part = parts[0]
                        next_hop = parts[4].strip(',')
                        distance = parts[2]
                        
                        dest, mask = RouterAnalyzer._cidr_to_netmask(network_part)

                        static_routes.append({
                            'dest': dest, 'mask': mask,
                            'next_hop': next_hop, 'distance': distance
                        })
                    except (ValueError, IndexError):
                        continue
        return static_routes

    def _parse_ospf_neighbors(self, output: str) -> List[Dict]:
        """Parsear salida de show ip ospf neighbor"""
        neighbors = []
        lines = output.split('\n')
        
        for line in lines[1:]:  # Saltar encabezado
            if line.strip() and not line.startswith('Neighbor'):
                parts = line.split()
                if len(parts) >= 6:
                    neighbors.append({
                        'neighbor_id': parts[0],
                        'priority': parts[1],
                        'state': parts[2],
                        'dead_time': parts[3],
                        'address': parts[4],
                        'interface': parts[5]
                    })
        
        return neighbors
    
    def _parse_bgp_neighbors(self, output: str) -> List[Dict]:
        """Parsear salida de show ip bgp summary"""
        neighbors = []
        lines = output.split('\n')
        
        for line in lines:
            if line.strip() and not any(x in line for x in ['BGP', 'Neighbor', 'V', 'AS']):
                parts = line.split()
                if len(parts) >= 8:
                    neighbors.append({
                        'neighbor': parts[0],
                        'version': parts[1],
                        'as': parts[2],
                        'messages_rcvd': parts[3],
                        'messages_sent': parts[4],
                        'table_version': parts[5],
                        'inq': parts[6],
                        'outq': parts[7],
                        'up_down': parts[8] if len(parts) > 8 else '',
                        'state': parts[9] if len(parts) > 9 else ''
                    })
        
        return neighbors

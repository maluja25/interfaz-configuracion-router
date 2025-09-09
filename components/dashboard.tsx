import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Progress } from "./ui/progress";
import { Activity, Cpu, HardDrive, Network, Router, Users, Globe, Settings } from "lucide-react";

export function Dashboard() {
  const deviceInfo = {
    model: "Cisco ISR4331",
    firmware: "IOS XE 16.09.04",
    uptime: "15 días, 4 horas",
    serialNumber: "FDO24280234"
  };

  const systemStats = {
    cpuUsage: 35,
    memoryUsage: 62,
    storageUsage: 28,
    temperature: 45
  };

  const networkStats = {
    activeConnections: 45,
    wiredConnections: 45,
    wirelessConnections: 0,
    totalBandwidth: "1 Gbps",
    currentUsage: "245 Mbps"
  };

  const interfaceStatus = [
    { name: "GigabitEthernet0/0/1", type: "Ethernet", status: "Activa", ip: "192.168.1.1", speed: "1 Gbps" },
    { name: "GigabitEthernet0/0/2", type: "Ethernet", status: "Activa", ip: "10.0.0.1", speed: "1 Gbps" },
    { name: "Serial0/1/0", type: "Serial", status: "Activa", ip: "203.0.113.2", speed: "1544 Kbps" },
    { name: "GigabitEthernet0/0/3", type: "Ethernet", status: "Inactiva", ip: "N/A", speed: "1 Gbps" },
    { name: "Loopback0", type: "Loopback", status: "Activa", ip: "1.1.1.1", speed: "N/A" }
  ];

  return (
    <div className="space-y-6">
      {/* Device Info */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Modelo</CardTitle>
            <Router className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{deviceInfo.model}</div>
            <p className="text-xs text-muted-foreground">Firmware {deviceInfo.firmware}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tiempo Activo</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{deviceInfo.uptime}</div>
            <p className="text-xs text-muted-foreground">Sin interrupciones</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Conexiones</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{networkStats.activeConnections}</div>
            <p className="text-xs text-muted-foreground">Conexiones Ethernet</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Ancho de Banda</CardTitle>
            <Network className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{networkStats.currentUsage}</div>
            <p className="text-xs text-muted-foreground">de {networkStats.totalBandwidth} total</p>
          </CardContent>
        </Card>
      </div>

      {/* System Performance */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Rendimiento del Sistema</CardTitle>
            <CardDescription>Estado actual de los recursos del dispositivo</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">CPU</span>
                <span className="text-sm text-muted-foreground">{systemStats.cpuUsage}%</span>
              </div>
              <Progress value={systemStats.cpuUsage} className="h-2" />
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Memoria RAM</span>
                <span className="text-sm text-muted-foreground">{systemStats.memoryUsage}%</span>
              </div>
              <Progress value={systemStats.memoryUsage} className="h-2" />
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Almacenamiento</span>
                <span className="text-sm text-muted-foreground">{systemStats.storageUsage}%</span>
              </div>
              <Progress value={systemStats.storageUsage} className="h-2" />
            </div>

            <div className="flex items-center justify-between pt-2">
              <span className="text-sm font-medium">Temperatura</span>
              <Badge variant="secondary">{systemStats.temperature}°C</Badge>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Estado de Interfaces</CardTitle>
            <CardDescription>Estado actual de todas las interfaces de red</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {interfaceStatus.map((interface_, index) => (
                <div key={index} className="flex items-center justify-between p-3 rounded-lg border">
                  <div className="flex items-center gap-3">
                    {interface_.type === "Serial" ? (
                      <Activity className="h-4 w-4 text-green-500" />
                    ) : interface_.type === "Loopback" ? (
                      <Settings className="h-4 w-4 text-purple-500" />
                    ) : (
                      <Globe className="h-4 w-4 text-blue-500" />
                    )}
                    <div>
                      <p className="font-medium">{interface_.name}</p>
                      <p className="text-sm text-muted-foreground">{interface_.ip}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <Badge variant="outline" className="mb-1">
                      {interface_.status}
                    </Badge>
                    <p className="text-xs text-muted-foreground">{interface_.speed}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Información del Dispositivo</CardTitle>
          <CardDescription>Detalles técnicos del router</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <p><span className="font-medium">Número de Serie:</span> {deviceInfo.serialNumber}</p>
              <p><span className="font-medium">Versión de Firmware:</span> {deviceInfo.firmware}</p>
              <p><span className="font-medium">Arquitectura:</span> x86_64</p>
              <p><span className="font-medium">Memoria:</span> 4 GB DDR4</p>
            </div>
            <div className="space-y-2">
              <p><span className="font-medium">Almacenamiento:</span> 8 GB eUSB</p>
              <p><span className="font-medium">Puertos Ethernet:</span> 3x Gigabit</p>
              <p><span className="font-medium">Ranuras WIC:</span> 2x WIC/VWIC/HWIC</p>
              <p><span className="font-medium">Protocolo:</span> IPv4/IPv6</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
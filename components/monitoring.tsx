import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { Badge } from "./ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Progress } from "./ui/progress";
import { ScrollArea } from "./ui/scroll-area";
import { 
  Monitor, 
  Activity, 
  HardDrive, 
  Network, 
  RefreshCw, 
  Download,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Cpu,
  MemoryStick,
  Clock
} from "lucide-react";
import { toast } from "sonner@2.0.3";

export function Monitoring() {
  const [selectedInterface, setSelectedInterface] = useState("all");
  const [autoRefresh, setAutoRefresh] = useState(true);

  const interfaceStats = [
    {
      name: "GigabitEthernet0/0/1",
      status: "up",
      inOctets: "2,453,892,114",
      outOctets: "1,892,337,445",
      inPackets: "3,445,221",
      outPackets: "2,887,334",
      inErrors: "0",
      outErrors: "0",
      crcErrors: "0",
      collisions: "0",
      utilization: 35,
      bandwidth: "1000 Mbps"
    },
    {
      name: "GigabitEthernet0/0/2",
      status: "up",
      inOctets: "1,234,567,890",
      outOctets: "987,654,321",
      inPackets: "1,876,543",
      outPackets: "1,543,210",
      inErrors: "2",
      outErrors: "0",
      crcErrors: "1",
      collisions: "0",
      utilization: 22,
      bandwidth: "1000 Mbps"
    },
    {
      name: "Serial0/1/0",
      status: "up",
      inOctets: "445,782,361",
      outOctets: "523,891,247",
      inPackets: "892,445",
      outPackets: "934,567",
      inErrors: "0",
      outErrors: "0",
      crcErrors: "0",
      collisions: "0",
      utilization: 78,
      bandwidth: "1544 Kbps"
    },
    {
      name: "GigabitEthernet0/0/3",
      status: "down",
      inOctets: "0",
      outOctets: "0",
      inPackets: "0",
      outPackets: "0",
      inErrors: "0",
      outErrors: "0",
      crcErrors: "0",
      collisions: "0",
      utilization: 0,
      bandwidth: "1000 Mbps"
    }
  ];

  const systemLogs = [
    { timestamp: "2024-01-15 14:35:12", level: "info", source: "kernel", message: "Interface GigabitEthernet0/0/1 is up" },
    { timestamp: "2024-01-15 14:33:45", level: "warning", source: "ospf", message: "OSPF neighbor 192.168.1.2 down" },
    { timestamp: "2024-01-15 14:32:18", level: "error", source: "bgp", message: "BGP session with 203.0.113.10 closed" },
    { timestamp: "2024-01-15 14:30:55", level: "info", source: "dhcp", message: "DHCP lease assigned to 192.168.1.101" },
    { timestamp: "2024-01-15 14:28:32", level: "warning", source: "memory", message: "Memory usage above 80%" },
    { timestamp: "2024-01-15 14:25:14", level: "info", source: "acl", message: "Access list 101 permit applied" },
    { timestamp: "2024-01-15 14:22:47", level: "error", source: "interface", message: "CRC error detected on Serial0/1/0" },
    { timestamp: "2024-01-15 14:20:23", level: "info", source: "routing", message: "Static route 0.0.0.0/0 installed" }
  ];

  const systemResources = {
    cpu: {
      usage: 45,
      processes: [
        { name: "OSPF Hello", usage: 12.3 },
        { name: "BGP Scanner", usage: 8.7 },
        { name: "IP Input", usage: 6.2 },
        { name: "DHCP Server", usage: 4.1 }
      ]
    },
    memory: {
      total: "512 MB",
      used: "387 MB",
      free: "125 MB",
      usage: 75.6,
      pools: [
        { name: "Processor", used: "145 MB", total: "256 MB" },
        { name: "I/O", used: "89 MB", total: "128 MB" },
        { name: "Driver", used: "153 MB", total: "128 MB" }
      ]
    },
    storage: {
      flash: { used: "89 MB", total: "256 MB", usage: 34.7 },
      nvram: { used: "142 KB", total: "512 KB", usage: 27.7 }
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "up":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "down":
        return <XCircle className="h-4 w-4 text-red-500" />;
      case "admin-down":
        return <XCircle className="h-4 w-4 text-gray-500" />;
      default:
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "up":
        return <Badge variant="default">UP</Badge>;
      case "down":
        return <Badge variant="destructive">DOWN</Badge>;
      case "admin-down":
        return <Badge variant="secondary">ADMIN DOWN</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const getLevelIcon = (level: string) => {
    switch (level) {
      case "error":
        return <XCircle className="h-4 w-4 text-red-500" />;
      case "warning":
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      case "info":
        return <CheckCircle className="h-4 w-4 text-blue-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-400" />;
    }
  };

  const handleRefresh = () => {
    toast.success("Datos actualizados");
  };

  const handleExportLogs = () => {
    toast.success("Logs exportados correctamente");
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2>Monitoreo del Sistema</h2>
          <p className="text-muted-foreground">Supervisión en tiempo real del router y sus interfaces</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={handleRefresh} className="flex items-center gap-2">
            <RefreshCw className="h-4 w-4" />
            Actualizar
          </Button>
          <Button variant="outline" onClick={handleExportLogs} className="flex items-center gap-2">
            <Download className="h-4 w-4" />
            Exportar
          </Button>
        </div>
      </div>

      <Tabs defaultValue="interfaces" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="interfaces" className="flex items-center gap-2">
            <Network className="h-4 w-4" />
            Interfaces
          </TabsTrigger>
          <TabsTrigger value="system" className="flex items-center gap-2">
            <Cpu className="h-4 w-4" />
            Sistema
          </TabsTrigger>
          <TabsTrigger value="logs" className="flex items-center gap-2">
            <Activity className="h-4 w-4" />
            Logs
          </TabsTrigger>
          <TabsTrigger value="resources" className="flex items-center gap-2">
            <HardDrive className="h-4 w-4" />
            Recursos
          </TabsTrigger>
        </TabsList>

        <TabsContent value="interfaces" className="space-y-4">
          <div className="flex items-center gap-4 mb-4">
            <Label htmlFor="interface-filter">Filtrar por interfaz:</Label>
            <Select value={selectedInterface} onValueChange={setSelectedInterface}>
              <SelectTrigger className="w-48">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todas las interfaces</SelectItem>
                {interfaceStats.map((iface) => (
                  <SelectItem key={iface.name} value={iface.name}>{iface.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Interfaces Activas</CardTitle>
                <CheckCircle className="h-4 w-4 text-green-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{interfaceStats.filter(i => i.status === "up").length}</div>
                <p className="text-xs text-muted-foreground">de {interfaceStats.length} interfaces</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Errores CRC</CardTitle>
                <AlertTriangle className="h-4 w-4 text-yellow-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-yellow-600">
                  {interfaceStats.reduce((sum, i) => sum + parseInt(i.crcErrors), 0)}
                </div>
                <p className="text-xs text-muted-foreground">errores detectados</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Utilización Promedio</CardTitle>
                <Monitor className="h-4 w-4 text-blue-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-600">
                  {Math.round(interfaceStats.reduce((sum, i) => sum + i.utilization, 0) / interfaceStats.length)}%
                </div>
                <p className="text-xs text-muted-foreground">uso de ancho de banda</p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Estadísticas de Interfaces</CardTitle>
              <CardDescription>Estado detallado y estadísticas de tráfico</CardDescription>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[400px]">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Interfaz</TableHead>
                      <TableHead>Estado</TableHead>
                      <TableHead>Utilización</TableHead>
                      <TableHead>Paquetes In</TableHead>
                      <TableHead>Paquetes Out</TableHead>
                      <TableHead>Errores In</TableHead>
                      <TableHead>Errores Out</TableHead>
                      <TableHead>CRC Errors</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {interfaceStats
                      .filter(iface => selectedInterface === "all" || iface.name === selectedInterface)
                      .map((iface) => (
                      <TableRow key={iface.name}>
                        <TableCell className="flex items-center gap-2">
                          {getStatusIcon(iface.status)}
                          <span className="font-mono text-sm">{iface.name}</span>
                        </TableCell>
                        <TableCell>{getStatusBadge(iface.status)}</TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <Progress value={iface.utilization} className="w-16 h-2" />
                            <span className="text-sm">{iface.utilization}%</span>
                          </div>
                        </TableCell>
                        <TableCell className="font-mono text-sm">{iface.inPackets}</TableCell>
                        <TableCell className="font-mono text-sm">{iface.outPackets}</TableCell>
                        <TableCell className="font-mono text-sm">
                          <span className={iface.inErrors !== "0" ? "text-red-600" : ""}>{iface.inErrors}</span>
                        </TableCell>
                        <TableCell className="font-mono text-sm">
                          <span className={iface.outErrors !== "0" ? "text-red-600" : ""}>{iface.outErrors}</span>
                        </TableCell>
                        <TableCell className="font-mono text-sm">
                          <span className={iface.crcErrors !== "0" ? "text-yellow-600" : ""}>{iface.crcErrors}</span>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="system" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Cpu className="h-5 w-5" />
                  CPU
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Uso General</span>
                    <span>{systemResources.cpu.usage}%</span>
                  </div>
                  <Progress value={systemResources.cpu.usage} className="h-2" />
                </div>
                
                <div className="space-y-2">
                  <h4 className="font-medium">Procesos Principales</h4>
                  {systemResources.cpu.processes.map((process, index) => (
                    <div key={index} className="flex justify-between text-sm">
                      <span>{process.name}</span>
                      <span>{process.usage}%</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MemoryStick className="h-5 w-5" />
                  Memoria
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Uso Total</span>
                    <span>{systemResources.memory.usage}%</span>
                  </div>
                  <Progress value={systemResources.memory.usage} className="h-2" />
                  <div className="flex justify-between text-sm text-muted-foreground">
                    <span>Usado: {systemResources.memory.used}</span>
                    <span>Total: {systemResources.memory.total}</span>
                  </div>
                </div>

                <div className="space-y-2">
                  <h4 className="font-medium">Pools de Memoria</h4>
                  {systemResources.memory.pools.map((pool, index) => (
                    <div key={index} className="space-y-1">
                      <div className="flex justify-between text-sm">
                        <span>{pool.name}</span>
                        <span>{pool.used} / {pool.total}</span>
                      </div>
                      <Progress 
                        value={(parseInt(pool.used) / parseInt(pool.total)) * 100} 
                        className="h-1" 
                      />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <HardDrive className="h-5 w-5" />
                  Almacenamiento
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div>
                    <div className="flex justify-between text-sm font-medium">
                      <span>Flash Memory</span>
                      <span>{systemResources.storage.flash.usage}%</span>
                    </div>
                    <Progress value={systemResources.storage.flash.usage} className="h-2 mt-1" />
                    <div className="flex justify-between text-xs text-muted-foreground mt-1">
                      <span>Usado: {systemResources.storage.flash.used}</span>
                      <span>Total: {systemResources.storage.flash.total}</span>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-sm font-medium">
                      <span>NVRAM</span>
                      <span>{systemResources.storage.nvram.usage}%</span>
                    </div>
                    <Progress value={systemResources.storage.nvram.usage} className="h-2 mt-1" />
                    <div className="flex justify-between text-xs text-muted-foreground mt-1">
                      <span>Usado: {systemResources.storage.nvram.used}</span>
                      <span>Total: {systemResources.storage.nvram.total}</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="logs" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Logs del Sistema en Tiempo Real</CardTitle>
              <CardDescription>Eventos y mensajes del sistema ordenados cronológicamente</CardDescription>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[500px]">
                <div className="space-y-2">
                  {systemLogs.map((log, index) => (
                    <div key={index} className="border rounded-lg p-3 space-y-1">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          {getLevelIcon(log.level)}
                          <span className="font-mono text-sm text-muted-foreground">{log.timestamp}</span>
                          <Badge variant="outline">{log.source}</Badge>
                        </div>
                        <Badge variant={
                          log.level === "error" ? "destructive" :
                          log.level === "warning" ? "secondary" : "default"
                        }>
                          {log.level.toUpperCase()}
                        </Badge>
                      </div>
                      <p className="text-sm">{log.message}</p>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="resources" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Historial de Uso de CPU</CardTitle>
                <CardDescription>Tendencia de uso de CPU en las últimas horas</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Promedio 1 min:</span>
                    <span>45%</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Promedio 5 min:</span>
                    <span>38%</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Promedio 15 min:</span>
                    <span>42%</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Máximo 24h:</span>
                    <span>89%</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Estadísticas de Red</CardTitle>
                <CardDescription>Resumen del tráfico de todas las interfaces</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Total Paquetes In:</span>
                    <span>6,214,209</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Total Paquetes Out:</span>
                    <span>5,365,111</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Total Errores:</span>
                    <span className="text-red-600">2</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Colisiones:</span>
                    <span>0</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
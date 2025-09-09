import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { Badge } from "./ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { ScrollArea } from "./ui/scroll-area";
import { 
  FileText, 
  Download, 
  Trash2, 
  Search, 
  Filter, 
  RefreshCw, 
  AlertTriangle,
  Info,
  CheckCircle,
  XCircle,
  Clock
} from "lucide-react";
import { toast } from "sonner@2.0.3";

export function SystemLogs() {
  const [selectedLogType, setSelectedLogType] = useState("all");
  const [selectedLevel, setSelectedLevel] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");

  const systemLogs = [
    { 
      id: 1, 
      timestamp: "2024-01-15 14:30:25", 
      level: "info", 
      category: "system", 
      source: "kernel", 
      message: "Sistema iniciado correctamente", 
      details: "Bootloader cargado, drivers inicializados" 
    },
    { 
      id: 2, 
      timestamp: "2024-01-15 14:28:15", 
      level: "warning", 
      category: "network", 
      source: "dhcp", 
      message: "Pool de IPs DHCP al 85%", 
      details: "Quedan 15 direcciones IP disponibles de 100" 
    },
    { 
      id: 3, 
      timestamp: "2024-01-15 14:25:42", 
      level: "error", 
      category: "security", 
      source: "firewall", 
      message: "Intento de acceso bloqueado", 
      details: "IP: 203.0.113.45 intentó acceder al puerto 22" 
    },
    { 
      id: 4, 
      timestamp: "2024-01-15 14:22:18", 
      level: "info", 
      category: "wifi", 
      source: "hostapd", 
      message: "Cliente conectado a WiFi", 
      details: "MAC: AA:BB:CC:DD:EE:FF conectado a SSID: RouterWiFi" 
    },
    { 
      id: 5, 
      timestamp: "2024-01-15 14:20:33", 
      level: "debug", 
      category: "qos", 
      source: "tc", 
      message: "Regla QoS aplicada", 
      details: "Límite de ancho de banda aplicado a 192.168.1.101" 
    },
    { 
      id: 6, 
      timestamp: "2024-01-15 14:18:07", 
      level: "warning", 
      category: "system", 
      source: "temperature", 
      message: "Temperatura elevada detectada", 
      details: "CPU a 78°C, ventiladores a máxima velocidad" 
    },
    { 
      id: 7, 
      timestamp: "2024-01-15 14:15:55", 
      level: "info", 
      category: "vlan", 
      source: "bridge", 
      message: "VLAN 100 configurada", 
      details: "Puerto 3 asignado a VLAN 100 (IoT)" 
    },
    { 
      id: 8, 
      timestamp: "2024-01-15 14:12:30", 
      level: "error", 
      category: "network", 
      source: "wan", 
      message: "Pérdida de conectividad WAN", 
      details: "Timeout en gateway 203.0.113.1, intentando reconexión" 
    }
  ];

  const connectionLogs = [
    { id: 1, timestamp: "2024-01-15 14:30:15", device: "MacBook Pro", mac: "AA:BB:CC:DD:EE:FF", ip: "192.168.1.101", action: "Conectado", interface: "WiFi" },
    { id: 2, timestamp: "2024-01-15 14:28:42", device: "iPhone 12", mac: "11:22:33:44:55:66", ip: "192.168.1.102", action: "Desconectado", interface: "WiFi" },
    { id: 3, timestamp: "2024-01-15 14:25:18", device: "Smart TV", mac: "77:88:99:AA:BB:CC", ip: "192.168.1.103", action: "Conectado", interface: "Ethernet" },
    { id: 4, timestamp: "2024-01-15 14:22:55", device: "Tablet iPad", mac: "DD:EE:FF:11:22:33", ip: "192.168.1.104", action: "Conectado", interface: "WiFi" },
    { id: 5, timestamp: "2024-01-15 14:20:30", device: "Gaming Console", mac: "44:55:66:77:88:99", ip: "192.168.1.105", action: "Desconectado", interface: "Ethernet" }
  ];

  const securityLogs = [
    { id: 1, timestamp: "2024-01-15 14:29:45", event: "Intento de acceso bloqueado", severity: "high", source: "203.0.113.45", target: "22/TCP", action: "BLOCKED" },
    { id: 2, timestamp: "2024-01-15 14:26:12", event: "Usuario VPN conectado", severity: "low", source: "john_doe", target: "VPN Server", action: "ALLOWED" },
    { id: 3, timestamp: "2024-01-15 14:23:38", event: "Posible escaneo de puertos", severity: "medium", source: "192.168.1.150", target: "Multiple ports", action: "MONITORED" },
    { id: 4, timestamp: "2024-01-15 14:21:05", event: "Regla de firewall aplicada", severity: "low", source: "Firewall", target: "80/TCP", action: "ALLOWED" },
    { id: 5, timestamp: "2024-01-15 14:18:22", event: "Detección de malware", severity: "high", source: "192.168.1.120", target: "malware.exe", action: "QUARANTINED" }
  ];

  const filteredSystemLogs = systemLogs.filter(log => {
    const matchesType = selectedLogType === "all" || log.category === selectedLogType;
    const matchesLevel = selectedLevel === "all" || log.level === selectedLevel;
    const matchesSearch = searchTerm === "" || 
      log.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.source.toLowerCase().includes(searchTerm.toLowerCase());
    
    return matchesType && matchesLevel && matchesSearch;
  });

  const getLevelIcon = (level: string) => {
    switch (level) {
      case "error":
        return <XCircle className="h-4 w-4 text-red-500" />;
      case "warning":
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      case "info":
        return <CheckCircle className="h-4 w-4 text-blue-500" />;
      case "debug":
        return <Info className="h-4 w-4 text-gray-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-400" />;
    }
  };

  const getLevelBadge = (level: string) => {
    switch (level) {
      case "error":
        return <Badge variant="destructive">Error</Badge>;
      case "warning":
        return <Badge className="bg-yellow-100 text-yellow-800">Warning</Badge>;
      case "info":
        return <Badge variant="default">Info</Badge>;
      case "debug":
        return <Badge variant="outline">Debug</Badge>;
      default:
        return <Badge variant="secondary">{level}</Badge>;
    }
  };

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case "high":
        return <Badge variant="destructive">Alta</Badge>;
      case "medium":
        return <Badge className="bg-yellow-100 text-yellow-800">Media</Badge>;
      case "low":
        return <Badge variant="default">Baja</Badge>;
      default:
        return <Badge variant="outline">{severity}</Badge>;
    }
  };

  const handleExportLogs = () => {
    toast.success("Logs exportados correctamente");
  };

  const handleClearLogs = () => {
    toast.success("Logs limpiados correctamente");
  };

  const handleRefreshLogs = () => {
    toast.success("Logs actualizados");
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2>Logs del Sistema</h2>
          <p className="text-muted-foreground">Monitorea eventos del sistema, conexiones y seguridad</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={handleRefreshLogs} className="flex items-center gap-2">
            <RefreshCw className="h-4 w-4" />
            Actualizar
          </Button>
          <Button variant="outline" onClick={handleExportLogs} className="flex items-center gap-2">
            <Download className="h-4 w-4" />
            Exportar
          </Button>
          <Button variant="outline" onClick={handleClearLogs} className="flex items-center gap-2">
            <Trash2 className="h-4 w-4" />
            Limpiar
          </Button>
        </div>
      </div>

      <Tabs defaultValue="system" className="space-y-4">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="system" className="flex items-center gap-2">
            <FileText className="h-4 w-4" />
            Sistema
          </TabsTrigger>
          <TabsTrigger value="connections" className="flex items-center gap-2">
            <CheckCircle className="h-4 w-4" />
            Conexiones
          </TabsTrigger>
          <TabsTrigger value="security" className="flex items-center gap-2">
            <AlertTriangle className="h-4 w-4" />
            Seguridad
          </TabsTrigger>
        </TabsList>

        <TabsContent value="system" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Filtros de Logs del Sistema</CardTitle>
              <CardDescription>
                Filtra los logs por categoría, nivel y contenido
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-4">
                <div className="flex-1 min-w-[200px]">
                  <Label htmlFor="search">Buscar</Label>
                  <div className="relative">
                    <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="search"
                      placeholder="Buscar en logs..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-8"
                    />
                  </div>
                </div>
                
                <div className="min-w-[120px]">
                  <Label htmlFor="log-type">Categoría</Label>
                  <Select value={selectedLogType} onValueChange={setSelectedLogType}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Todas</SelectItem>
                      <SelectItem value="system">Sistema</SelectItem>
                      <SelectItem value="network">Red</SelectItem>
                      <SelectItem value="security">Seguridad</SelectItem>
                      <SelectItem value="wifi">WiFi</SelectItem>
                      <SelectItem value="qos">QoS</SelectItem>
                      <SelectItem value="vlan">VLAN</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="min-w-[120px]">
                  <Label htmlFor="log-level">Nivel</Label>
                  <Select value={selectedLevel} onValueChange={setSelectedLevel}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Todos</SelectItem>
                      <SelectItem value="error">Error</SelectItem>
                      <SelectItem value="warning">Warning</SelectItem>
                      <SelectItem value="info">Info</SelectItem>
                      <SelectItem value="debug">Debug</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Logs del Sistema ({filteredSystemLogs.length})</CardTitle>
              <CardDescription>
                Eventos y mensajes del sistema en tiempo real
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[500px]">
                <div className="space-y-2">
                  {filteredSystemLogs.map((log) => (
                    <div key={log.id} className="border rounded-lg p-4 space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          {getLevelIcon(log.level)}
                          <span className="font-mono text-sm text-muted-foreground">
                            {log.timestamp}
                          </span>
                          {getLevelBadge(log.level)}
                          <Badge variant="outline">{log.source}</Badge>
                        </div>
                        <Badge variant="secondary">{log.category}</Badge>
                      </div>
                      <p className="font-medium">{log.message}</p>
                      <p className="text-sm text-muted-foreground">{log.details}</p>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="connections" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Logs de Conexiones</CardTitle>
              <CardDescription>
                Historial de conexiones y desconexiones de dispositivos
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Fecha y Hora</TableHead>
                    <TableHead>Dispositivo</TableHead>
                    <TableHead>MAC Address</TableHead>
                    <TableHead>IP Asignada</TableHead>
                    <TableHead>Acción</TableHead>
                    <TableHead>Interfaz</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {connectionLogs.map((log) => (
                    <TableRow key={log.id}>
                      <TableCell className="font-mono text-sm">{log.timestamp}</TableCell>
                      <TableCell className="font-medium">{log.device}</TableCell>
                      <TableCell className="font-mono">{log.mac}</TableCell>
                      <TableCell>{log.ip}</TableCell>
                      <TableCell>
                        <Badge variant={log.action === "Conectado" ? "default" : "secondary"}>
                          {log.action}
                        </Badge>
                      </TableCell>
                      <TableCell>{log.interface}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="security" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Logs de Seguridad</CardTitle>
              <CardDescription>
                Eventos relacionados con seguridad, firewall y accesos
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Fecha y Hora</TableHead>
                    <TableHead>Evento</TableHead>
                    <TableHead>Severidad</TableHead>
                    <TableHead>Origen</TableHead>
                    <TableHead>Destino</TableHead>
                    <TableHead>Acción</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {securityLogs.map((log) => (
                    <TableRow key={log.id}>
                      <TableCell className="font-mono text-sm">{log.timestamp}</TableCell>
                      <TableCell className="font-medium">{log.event}</TableCell>
                      <TableCell>{getSeverityBadge(log.severity)}</TableCell>
                      <TableCell className="font-mono">{log.source}</TableCell>
                      <TableCell>{log.target}</TableCell>
                      <TableCell>
                        <Badge variant={
                          log.action === "BLOCKED" ? "destructive" :
                          log.action === "ALLOWED" ? "default" :
                          "outline"
                        }>
                          {log.action}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Stats Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total de Logs</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{systemLogs.length}</div>
            <p className="text-xs text-muted-foreground">eventos registrados</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Errores</CardTitle>
            <XCircle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {systemLogs.filter(log => log.level === "error").length}
            </div>
            <p className="text-xs text-muted-foreground">eventos de error</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Advertencias</CardTitle>
            <AlertTriangle className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">
              {systemLogs.filter(log => log.level === "warning").length}
            </div>
            <p className="text-xs text-muted-foreground">advertencias</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Eventos de Seguridad</CardTitle>
            <AlertTriangle className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{securityLogs.length}</div>
            <p className="text-xs text-muted-foreground">eventos de seguridad</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Slider } from "./ui/slider";
import { Switch } from "./ui/switch";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { Badge } from "./ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Progress } from "./ui/progress";
import { Zap, Settings, BarChart3, Users, Save } from "lucide-react";
import { toast } from "sonner@2.0.3";

export function QoSConfig() {
  const [qosEnabled, setQosEnabled] = useState(true);
  const [totalBandwidth, setTotalBandwidth] = useState(1000); // Mbps
  
  const [trafficShaping, setTrafficShaping] = useState([
    { id: 1, name: "Alta Prioridad", priority: "high", bandwidth: 40, protocol: "VoIP/Gaming", color: "bg-red-500" },
    { id: 2, name: "Media Prioridad", priority: "medium", bandwidth: 35, protocol: "Video Streaming", color: "bg-yellow-500" },
    { id: 3, name: "Baja Prioridad", priority: "low", bandwidth: 25, protocol: "Navegación Web", color: "bg-green-500" }
  ]);

  const [applicationRules, setApplicationRules] = useState([
    { id: 1, name: "Netflix", type: "Video Streaming", priority: "medium", bandwidth: "50 Mbps", status: "Activa" },
    { id: 2, name: "Zoom", type: "Videoconferencia", priority: "high", bandwidth: "20 Mbps", status: "Activa" },
    { id: 3, name: "Steam", type: "Gaming", priority: "high", bandwidth: "100 Mbps", status: "Activa" },
    { id: 4, name: "YouTube", type: "Video Streaming", priority: "medium", bandwidth: "30 Mbps", status: "Activa" },
    { id: 5, name: "Torrent", type: "P2P", priority: "low", bandwidth: "10 Mbps", status: "Activa" }
  ]);

  const [deviceLimits, setDeviceLimits] = useState([
    { id: 1, device: "MacBook Pro", ip: "192.168.1.101", upload: 50, download: 200, priority: "high" },
    { id: 2, device: "Smart TV", ip: "192.168.1.102", upload: 10, download: 100, priority: "medium" },
    { id: 3, device: "Tablet iPad", ip: "192.168.1.103", upload: 20, download: 80, priority: "medium" },
    { id: 4, device: "Servidor NAS", ip: "192.168.1.30", upload: 100, download: 300, priority: "high" }
  ]);

  const [currentUsage, setCurrentUsage] = useState({
    high: 25,
    medium: 45,
    low: 15
  });

  const handleSaveQoS = () => {
    toast.success("Configuración QoS guardada correctamente");
  };

  const handleUpdateBandwidth = (id: number, newBandwidth: number) => {
    setTrafficShaping(prev => prev.map(rule => 
      rule.id === id ? { ...rule, bandwidth: newBandwidth } : rule
    ));
  };

  const handleDeviceLimitChange = (id: number, field: string, value: string | number) => {
    setDeviceLimits(prev => prev.map(device => 
      device.id === id ? { ...device, [field]: value } : device
    ));
  };

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case "high":
        return <Badge className="bg-red-100 text-red-800">Alta</Badge>;
      case "medium":
        return <Badge className="bg-yellow-100 text-yellow-800">Media</Badge>;
      case "low":
        return <Badge className="bg-green-100 text-green-800">Baja</Badge>;
      default:
        return <Badge variant="outline">{priority}</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2>Configuración QoS</h2>
          <p className="text-muted-foreground">Control de calidad de servicio y gestión del ancho de banda</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Label htmlFor="qos-toggle">QoS Habilitado</Label>
            <Switch
              id="qos-toggle"
              checked={qosEnabled}
              onCheckedChange={setQosEnabled}
            />
          </div>
        </div>
      </div>

      {qosEnabled && (
        <Tabs defaultValue="bandwidth" className="space-y-4">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="bandwidth" className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              Ancho de Banda
            </TabsTrigger>
            <TabsTrigger value="applications" className="flex items-center gap-2">
              <Zap className="h-4 w-4" />
              Aplicaciones
            </TabsTrigger>
            <TabsTrigger value="devices" className="flex items-center gap-2">
              <Users className="h-4 w-4" />
              Dispositivos
            </TabsTrigger>
            <TabsTrigger value="monitoring" className="flex items-center gap-2">
              <Settings className="h-4 w-4" />
              Monitoreo
            </TabsTrigger>
          </TabsList>

          <TabsContent value="bandwidth" className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Configuración de Ancho de Banda</CardTitle>
                  <CardDescription>
                    Define el ancho de banda total disponible
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="total-bandwidth">Ancho de Banda Total (Mbps)</Label>
                    <Input
                      id="total-bandwidth"
                      type="number"
                      value={totalBandwidth}
                      onChange={(e) => setTotalBandwidth(parseInt(e.target.value))}
                    />
                  </div>
                  
                  <div className="space-y-4">
                    <h4>Distribución por Prioridad</h4>
                    {trafficShaping.map((rule) => (
                      <div key={rule.id} className="space-y-3 p-4 border rounded-lg">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div className={`w-3 h-3 rounded-full ${rule.color}`}></div>
                            <div>
                              <p className="font-medium">{rule.name}</p>
                              <p className="text-sm text-muted-foreground">{rule.protocol}</p>
                            </div>
                          </div>
                          <span className="font-medium">{rule.bandwidth}%</span>
                        </div>
                        <div className="space-y-2">
                          <Slider
                            value={[rule.bandwidth]}
                            onValueChange={(value) => handleUpdateBandwidth(rule.id, value[0])}
                            max={100}
                            step={5}
                            className="w-full"
                          />
                          <div className="flex justify-between text-sm text-muted-foreground">
                            <span>0%</span>
                            <span>{Math.round(totalBandwidth * rule.bandwidth / 100)} Mbps</span>
                            <span>100%</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Uso Actual del Ancho de Banda</CardTitle>
                  <CardDescription>
                    Monitor en tiempo real del tráfico por prioridad
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">Alta Prioridad</span>
                        <span className="text-sm text-muted-foreground">{currentUsage.high}%</span>
                      </div>
                      <Progress value={currentUsage.high} className="h-2" />
                      <p className="text-xs text-muted-foreground">
                        {Math.round(totalBandwidth * currentUsage.high / 100)} Mbps de {Math.round(totalBandwidth * 40 / 100)} Mbps disponibles
                      </p>
                    </div>

                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">Media Prioridad</span>
                        <span className="text-sm text-muted-foreground">{currentUsage.medium}%</span>
                      </div>
                      <Progress value={currentUsage.medium} className="h-2" />
                      <p className="text-xs text-muted-foreground">
                        {Math.round(totalBandwidth * currentUsage.medium / 100)} Mbps de {Math.round(totalBandwidth * 35 / 100)} Mbps disponibles
                      </p>
                    </div>

                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">Baja Prioridad</span>
                        <span className="text-sm text-muted-foreground">{currentUsage.low}%</span>
                      </div>
                      <Progress value={currentUsage.low} className="h-2" />
                      <p className="text-xs text-muted-foreground">
                        {Math.round(totalBandwidth * currentUsage.low / 100)} Mbps de {Math.round(totalBandwidth * 25 / 100)} Mbps disponibles
                      </p>
                    </div>
                  </div>

                  <div className="pt-4 border-t">
                    <div className="flex justify-between items-center">
                      <span className="font-medium">Uso Total</span>
                      <span className="font-medium">{currentUsage.high + currentUsage.medium + currentUsage.low}%</span>
                    </div>
                    <Progress value={currentUsage.high + currentUsage.medium + currentUsage.low} className="h-3 mt-2" />
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="flex justify-end">
              <Button onClick={handleSaveQoS} className="flex items-center gap-2">
                <Save className="h-4 w-4" />
                Guardar Configuración de Ancho de Banda
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="applications" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Reglas por Aplicación</CardTitle>
                <CardDescription>
                  Configura prioridades y límites específicos para aplicaciones
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Aplicación</TableHead>
                      <TableHead>Tipo</TableHead>
                      <TableHead>Prioridad</TableHead>
                      <TableHead>Límite de Ancho de Banda</TableHead>
                      <TableHead>Estado</TableHead>
                      <TableHead>Acciones</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {applicationRules.map((rule) => (
                      <TableRow key={rule.id}>
                        <TableCell className="font-medium">{rule.name}</TableCell>
                        <TableCell>{rule.type}</TableCell>
                        <TableCell>{getPriorityBadge(rule.priority)}</TableCell>
                        <TableCell>{rule.bandwidth}</TableCell>
                        <TableCell>
                          <Badge variant="outline" className="text-green-600">
                            {rule.status}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Button variant="outline" size="sm">
                            Editar
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="devices" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Límites por Dispositivo</CardTitle>
                <CardDescription>
                  Configura límites de ancho de banda específicos para cada dispositivo
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Dispositivo</TableHead>
                      <TableHead>Dirección IP</TableHead>
                      <TableHead>Subida (Mbps)</TableHead>
                      <TableHead>Bajada (Mbps)</TableHead>
                      <TableHead>Prioridad</TableHead>
                      <TableHead>Acciones</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {deviceLimits.map((device) => (
                      <TableRow key={device.id}>
                        <TableCell className="font-medium">{device.device}</TableCell>
                        <TableCell className="font-mono">{device.ip}</TableCell>
                        <TableCell>
                          <Input
                            type="number"
                            value={device.upload}
                            onChange={(e) => handleDeviceLimitChange(device.id, "upload", parseInt(e.target.value))}
                            className="w-20"
                          />
                        </TableCell>
                        <TableCell>
                          <Input
                            type="number"
                            value={device.download}
                            onChange={(e) => handleDeviceLimitChange(device.id, "download", parseInt(e.target.value))}
                            className="w-20"
                          />
                        </TableCell>
                        <TableCell>
                          <Select
                            value={device.priority}
                            onValueChange={(value) => handleDeviceLimitChange(device.id, "priority", value)}
                          >
                            <SelectTrigger className="w-24">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="high">Alta</SelectItem>
                              <SelectItem value="medium">Media</SelectItem>
                              <SelectItem value="low">Baja</SelectItem>
                            </SelectContent>
                          </Select>
                        </TableCell>
                        <TableCell>
                          <Button variant="outline" size="sm">
                            Aplicar
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="monitoring" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Tráfico Total</CardTitle>
                  <BarChart3 className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">845 Mbps</div>
                  <p className="text-xs text-muted-foreground">
                    de {totalBandwidth} Mbps total
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Dispositivos Activos</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{deviceLimits.length}</div>
                  <p className="text-xs text-muted-foreground">
                    dispositivos conectados
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Reglas Activas</CardTitle>
                  <Settings className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{applicationRules.filter(rule => rule.status === "Activa").length}</div>
                  <p className="text-xs text-muted-foreground">
                    de {applicationRules.length} reglas totales
                  </p>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Estadísticas de Tráfico en Tiempo Real</CardTitle>
                <CardDescription>
                  Monitor del uso de ancho de banda por categoría
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="text-center p-4 border rounded-lg">
                      <div className="text-lg font-bold text-red-600">{Math.round(totalBandwidth * currentUsage.high / 100)} Mbps</div>
                      <p className="text-sm text-muted-foreground">Alta Prioridad</p>
                      <Progress value={currentUsage.high} className="mt-2 h-2" />
                    </div>
                    <div className="text-center p-4 border rounded-lg">
                      <div className="text-lg font-bold text-yellow-600">{Math.round(totalBandwidth * currentUsage.medium / 100)} Mbps</div>
                      <p className="text-sm text-muted-foreground">Media Prioridad</p>
                      <Progress value={currentUsage.medium} className="mt-2 h-2" />
                    </div>
                    <div className="text-center p-4 border rounded-lg">
                      <div className="text-lg font-bold text-green-600">{Math.round(totalBandwidth * currentUsage.low / 100)} Mbps</div>
                      <p className="text-sm text-muted-foreground">Baja Prioridad</p>
                      <Progress value={currentUsage.low} className="mt-2 h-2" />
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}

      {!qosEnabled && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Zap className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium mb-2">QoS Deshabilitado</h3>
            <p className="text-muted-foreground text-center max-w-md">
              El control de calidad de servicio está deshabilitado. Actívalo para gestionar el ancho de banda y priorizar el tráfico de red.
            </p>
            <Button
              onClick={() => setQosEnabled(true)}
              className="mt-4"
            >
              Habilitar QoS
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
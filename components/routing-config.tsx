import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Switch } from "./ui/switch";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { Badge } from "./ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "./ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Route, Plus, Edit, Trash2, Save, Network, Globe } from "lucide-react";
import { toast } from "sonner@2.0.3";

export function RoutingConfig() {
  const [routingProtocols, setRoutingProtocols] = useState({
    ospf: { enabled: false, processId: "1", routerId: "1.1.1.1" },
    eigrp: { enabled: false, as: "100" },
    bgp: { enabled: false, as: "65001", routerId: "1.1.1.1" },
    rip: { enabled: false, version: "2" }
  });

  const [staticRoutes, setStaticRoutes] = useState([
    { id: 1, network: "0.0.0.0", mask: "0.0.0.0", gateway: "203.0.113.1", interface: "Serial0/1/0", distance: "1", description: "Ruta por defecto" },
    { id: 2, network: "172.16.0.0", mask: "255.255.0.0", gateway: "192.168.1.254", interface: "GigabitEthernet0/0/1", distance: "1", description: "Red remota" },
    { id: 3, network: "10.10.0.0", mask: "255.255.0.0", gateway: "10.0.0.254", interface: "GigabitEthernet0/0/2", distance: "1", description: "Red servidores remotos" }
  ]);

  const [ospfAreas, setOspfAreas] = useState([
    { id: 1, areaId: "0", type: "Standard", networks: ["192.168.1.0 0.0.0.255", "10.0.0.0 0.0.0.255"] },
    { id: 2, areaId: "1", type: "Stub", networks: ["172.16.0.0 0.0.255.255"] }
  ]);

  const [bgpNeighbors, setBgpNeighbors] = useState([
    { id: 1, ip: "203.0.113.10", remoteAs: "65002", description: "ISP Principal" },
    { id: 2, ip: "203.0.113.20", remoteAs: "65003", description: "ISP Backup" }
  ]);

  const [newStaticRoute, setNewStaticRoute] = useState({
    network: "",
    mask: "",
    gateway: "",
    interface: "",
    distance: "1",
    description: ""
  });

  const [isAddingRoute, setIsAddingRoute] = useState(false);

  const handleProtocolToggle = (protocol: string, enabled: boolean) => {
    setRoutingProtocols(prev => ({
      ...prev,
      [protocol]: { ...prev[protocol], enabled }
    }));
    toast.success(`${protocol.toUpperCase()} ${enabled ? 'habilitado' : 'deshabilitado'}`);
  };

  const handleProtocolConfig = (protocol: string, config: any) => {
    setRoutingProtocols(prev => ({
      ...prev,
      [protocol]: { ...prev[protocol], ...config }
    }));
  };

  const handleAddStaticRoute = () => {
    if (newStaticRoute.network && newStaticRoute.mask && (newStaticRoute.gateway || newStaticRoute.interface)) {
      setStaticRoutes(prev => [...prev, {
        id: prev.length + 1,
        ...newStaticRoute
      }]);
      setNewStaticRoute({ network: "", mask: "", gateway: "", interface: "", distance: "1", description: "" });
      setIsAddingRoute(false);
      toast.success("Ruta estática agregada correctamente");
    }
  };

  const handleDeleteRoute = (id: number) => {
    setStaticRoutes(prev => prev.filter(route => route.id !== id));
    toast.success("Ruta estática eliminada");
  };

  const getProtocolBadge = (enabled: boolean) => {
    return (
      <Badge variant={enabled ? "default" : "secondary"}>
        {enabled ? "Habilitado" : "Deshabilitado"}
      </Badge>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2>Protocolos de Enrutamiento</h2>
          <p className="text-muted-foreground">Configura protocolos dinámicos y rutas estáticas</p>
        </div>
      </div>

      <Tabs defaultValue="protocols" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="protocols" className="flex items-center gap-2">
            <Route className="h-4 w-4" />
            Protocolos
          </TabsTrigger>
          <TabsTrigger value="static" className="flex items-center gap-2">
            <Network className="h-4 w-4" />
            Rutas Estáticas
          </TabsTrigger>
          <TabsTrigger value="ospf" className="flex items-center gap-2">
            <Globe className="h-4 w-4" />
            OSPF
          </TabsTrigger>
          <TabsTrigger value="bgp" className="flex items-center gap-2">
            <Route className="h-4 w-4" />
            BGP
          </TabsTrigger>
        </TabsList>

        <TabsContent value="protocols" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* OSPF Configuration */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  OSPF (Open Shortest Path First)
                  {getProtocolBadge(routingProtocols.ospf.enabled)}
                </CardTitle>
                <CardDescription>Protocolo de estado de enlace para redes internas</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label>Habilitar OSPF</Label>
                  <Switch
                    checked={routingProtocols.ospf.enabled}
                    onCheckedChange={(checked) => handleProtocolToggle('ospf', checked)}
                  />
                </div>
                
                {routingProtocols.ospf.enabled && (
                  <div className="space-y-3">
                    <div className="space-y-2">
                      <Label htmlFor="ospf-process">Process ID</Label>
                      <Input
                        id="ospf-process"
                        value={routingProtocols.ospf.processId}
                        onChange={(e) => handleProtocolConfig('ospf', { processId: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="ospf-router-id">Router ID</Label>
                      <Input
                        id="ospf-router-id"
                        placeholder="1.1.1.1"
                        value={routingProtocols.ospf.routerId}
                        onChange={(e) => handleProtocolConfig('ospf', { routerId: e.target.value })}
                      />
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* EIGRP Configuration */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  EIGRP (Enhanced Interior Gateway Routing Protocol)
                  {getProtocolBadge(routingProtocols.eigrp.enabled)}
                </CardTitle>
                <CardDescription>Protocolo propietario de Cisco</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label>Habilitar EIGRP</Label>
                  <Switch
                    checked={routingProtocols.eigrp.enabled}
                    onCheckedChange={(checked) => handleProtocolToggle('eigrp', checked)}
                  />
                </div>
                
                {routingProtocols.eigrp.enabled && (
                  <div className="space-y-2">
                    <Label htmlFor="eigrp-as">Autonomous System</Label>
                    <Input
                      id="eigrp-as"
                      value={routingProtocols.eigrp.as}
                      onChange={(e) => handleProtocolConfig('eigrp', { as: e.target.value })}
                    />
                  </div>
                )}
              </CardContent>
            </Card>

            {/* BGP Configuration */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  BGP (Border Gateway Protocol)
                  {getProtocolBadge(routingProtocols.bgp.enabled)}
                </CardTitle>
                <CardDescription>Protocolo para enrutamiento entre dominios</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label>Habilitar BGP</Label>
                  <Switch
                    checked={routingProtocols.bgp.enabled}
                    onCheckedChange={(checked) => handleProtocolToggle('bgp', checked)}
                  />
                </div>
                
                {routingProtocols.bgp.enabled && (
                  <div className="space-y-3">
                    <div className="space-y-2">
                      <Label htmlFor="bgp-as">AS Number</Label>
                      <Input
                        id="bgp-as"
                        value={routingProtocols.bgp.as}
                        onChange={(e) => handleProtocolConfig('bgp', { as: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="bgp-router-id">Router ID</Label>
                      <Input
                        id="bgp-router-id"
                        placeholder="1.1.1.1"
                        value={routingProtocols.bgp.routerId}
                        onChange={(e) => handleProtocolConfig('bgp', { routerId: e.target.value })}
                      />
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* RIP Configuration */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  RIP (Routing Information Protocol)
                  {getProtocolBadge(routingProtocols.rip.enabled)}
                </CardTitle>
                <CardDescription>Protocolo de vector distancia simple</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label>Habilitar RIP</Label>
                  <Switch
                    checked={routingProtocols.rip.enabled}
                    onCheckedChange={(checked) => handleProtocolToggle('rip', checked)}
                  />
                </div>
                
                {routingProtocols.rip.enabled && (
                  <div className="space-y-2">
                    <Label htmlFor="rip-version">Versión</Label>
                    <Select 
                      value={routingProtocols.rip.version} 
                      onValueChange={(value) => handleProtocolConfig('rip', { version: value })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="1">RIP v1</SelectItem>
                        <SelectItem value="2">RIP v2</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="static" className="space-y-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Rutas Estáticas</CardTitle>
                <CardDescription>Configura rutas estáticas para redes específicas</CardDescription>
              </div>
              <Dialog open={isAddingRoute} onOpenChange={setIsAddingRoute}>
                <DialogTrigger asChild>
                  <Button className="flex items-center gap-2">
                    <Plus className="h-4 w-4" />
                    Agregar Ruta
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Nueva Ruta Estática</DialogTitle>
                    <DialogDescription>Configura una nueva ruta estática</DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="network">Red de Destino</Label>
                        <Input
                          id="network"
                          placeholder="192.168.2.0"
                          value={newStaticRoute.network}
                          onChange={(e) => setNewStaticRoute(prev => ({ ...prev, network: e.target.value }))}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="mask">Máscara de Subred</Label>
                        <Input
                          id="mask"
                          placeholder="255.255.255.0"
                          value={newStaticRoute.mask}
                          onChange={(e) => setNewStaticRoute(prev => ({ ...prev, mask: e.target.value }))}
                        />
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="gateway">Next Hop (Gateway)</Label>
                        <Input
                          id="gateway"
                          placeholder="192.168.1.1"
                          value={newStaticRoute.gateway}
                          onChange={(e) => setNewStaticRoute(prev => ({ ...prev, gateway: e.target.value }))}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="interface">Interfaz de Salida</Label>
                        <Select value={newStaticRoute.interface} onValueChange={(value) => setNewStaticRoute(prev => ({ ...prev, interface: value }))}>
                          <SelectTrigger>
                            <SelectValue placeholder="Seleccionar interfaz" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="GigabitEthernet0/0/1">GigabitEthernet0/0/1</SelectItem>
                            <SelectItem value="GigabitEthernet0/0/2">GigabitEthernet0/0/2</SelectItem>
                            <SelectItem value="Serial0/1/0">Serial0/1/0</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="distance">Distancia Administrativa</Label>
                        <Input
                          id="distance"
                          type="number"
                          value={newStaticRoute.distance}
                          onChange={(e) => setNewStaticRoute(prev => ({ ...prev, distance: e.target.value }))}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="description">Descripción</Label>
                        <Input
                          id="description"
                          placeholder="Descripción de la ruta"
                          value={newStaticRoute.description}
                          onChange={(e) => setNewStaticRoute(prev => ({ ...prev, description: e.target.value }))}
                        />
                      </div>
                    </div>
                    <div className="flex justify-end gap-2">
                      <Button variant="outline" onClick={() => setIsAddingRoute(false)}>
                        Cancelar
                      </Button>
                      <Button onClick={handleAddStaticRoute}>
                        Agregar Ruta
                      </Button>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Red de Destino</TableHead>
                    <TableHead>Máscara</TableHead>
                    <TableHead>Next Hop</TableHead>
                    <TableHead>Interfaz</TableHead>
                    <TableHead>Distancia</TableHead>
                    <TableHead>Descripción</TableHead>
                    <TableHead>Acciones</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {staticRoutes.map((route) => (
                    <TableRow key={route.id}>
                      <TableCell className="font-mono">{route.network}</TableCell>
                      <TableCell className="font-mono">{route.mask}</TableCell>
                      <TableCell className="font-mono">{route.gateway}</TableCell>
                      <TableCell>{route.interface}</TableCell>
                      <TableCell>{route.distance}</TableCell>
                      <TableCell>{route.description}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Button variant="outline" size="sm">
                            <Edit className="h-3 w-3" />
                          </Button>
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => handleDeleteRoute(route.id)}
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="ospf" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Áreas OSPF</CardTitle>
              <CardDescription>Configuración de áreas OSPF y redes anunciadas</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Área ID</TableHead>
                    <TableHead>Tipo de Área</TableHead>
                    <TableHead>Redes Anunciadas</TableHead>
                    <TableHead>Acciones</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {ospfAreas.map((area) => (
                    <TableRow key={area.id}>
                      <TableCell className="font-mono">{area.areaId}</TableCell>
                      <TableCell>
                        <Badge variant={area.type === "Standard" ? "default" : "secondary"}>
                          {area.type}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="space-y-1">
                          {area.networks.map((network, index) => (
                            <div key={index} className="font-mono text-sm">{network}</div>
                          ))}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Button variant="outline" size="sm">
                          <Edit className="h-3 w-3" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="bgp" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Vecinos BGP</CardTitle>
              <CardDescription>Configuración de peers BGP</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>IP del Vecino</TableHead>
                    <TableHead>AS Remoto</TableHead>
                    <TableHead>Descripción</TableHead>
                    <TableHead>Estado</TableHead>
                    <TableHead>Acciones</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {bgpNeighbors.map((neighbor) => (
                    <TableRow key={neighbor.id}>
                      <TableCell className="font-mono">{neighbor.ip}</TableCell>
                      <TableCell>{neighbor.remoteAs}</TableCell>
                      <TableCell>{neighbor.description}</TableCell>
                      <TableCell>
                        <Badge variant="default">Established</Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Button variant="outline" size="sm">
                            <Edit className="h-3 w-3" />
                          </Button>
                          <Button variant="outline" size="sm">
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Configuration Preview */}
      <Card>
        <CardHeader>
          <CardTitle>Vista Previa de Configuración</CardTitle>
          <CardDescription>Comandos que se ejecutarán en el router</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="bg-black text-green-400 p-4 rounded-lg font-mono text-sm space-y-1">
            <div className="text-gray-500"># Configuración de protocolos de enrutamiento</div>
            
            {routingProtocols.ospf.enabled && (
              <div className="space-y-1">
                <div>router ospf {routingProtocols.ospf.processId}</div>
                <div className="ml-4">router-id {routingProtocols.ospf.routerId}</div>
                <div className="ml-4">exit</div>
              </div>
            )}

            {routingProtocols.bgp.enabled && (
              <div className="space-y-1">
                <div>router bgp {routingProtocols.bgp.as}</div>
                <div className="ml-4">bgp router-id {routingProtocols.bgp.routerId}</div>
                <div className="ml-4">exit</div>
              </div>
            )}

            {staticRoutes.map((route) => (
              <div key={route.id}>
                ip route {route.network} {route.mask} {route.gateway || route.interface} {route.distance}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
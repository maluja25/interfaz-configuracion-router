import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { Badge } from "./ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "./ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { ScrollArea } from "./ui/scroll-area";
import { 
  Layers, 
  Plus, 
  Edit, 
  Trash2, 
  Save, 
  Network, 
  Route,
  Settings,
  Activity,
  Eye,
  Globe
} from "lucide-react";
import { toast } from "sonner@2.0.3";

export function VRFConfig() {
  const [vrfs, setVrfs] = useState([
    {
      id: 1,
      name: "CUSTOMER_A",
      rd: "65001:100",
      rtImport: ["65001:100", "65001:999"],
      rtExport: ["65001:100"],
      description: "Cliente A - Red Corporativa",
      interfaces: ["GigabitEthernet0/0/1.100", "Serial0/1/0"],
      status: "active",
      routes: [
        { network: "10.100.0.0/24", nextHop: "10.100.0.1", type: "connected" },
        { network: "172.16.100.0/24", nextHop: "10.100.0.254", type: "static" }
      ]
    },
    {
      id: 2,
      name: "CUSTOMER_B",
      rd: "65001:200",
      rtImport: ["65001:200", "65001:999"],
      rtExport: ["65001:200"],
      description: "Cliente B - Red Privada",
      interfaces: ["GigabitEthernet0/0/2.200"],
      status: "active",
      routes: [
        { network: "10.200.0.0/24", nextHop: "10.200.0.1", type: "connected" },
        { network: "192.168.200.0/24", nextHop: "10.200.0.254", type: "ospf" }
      ]
    },
    {
      id: 3,
      name: "MGMT",
      rd: "65001:999",
      rtImport: ["65001:999"],
      rtExport: ["65001:999"],
      description: "Red de Administración",
      interfaces: ["Loopback1"],
      status: "active",
      routes: [
        { network: "192.168.255.0/24", nextHop: "192.168.255.1", type: "connected" }
      ]
    },
    {
      id: 4,
      name: "INTERNET",
      rd: "65001:300",
      rtImport: ["65001:300"],
      rtExport: ["65001:300"],
      description: "Acceso a Internet compartido",
      interfaces: ["Serial0/1/1"],
      status: "inactive",
      routes: []
    }
  ]);

  const [newVrf, setNewVrf] = useState({
    name: "",
    rd: "",
    rtImport: "",
    rtExport: "",
    description: ""
  });

  const [isAddingVrf, setIsAddingVrf] = useState(false);
  const [selectedVrf, setSelectedVrf] = useState(null);
  const [isViewingDetails, setIsViewingDetails] = useState(false);

  const availableInterfaces = [
    "GigabitEthernet0/0/1",
    "GigabitEthernet0/0/2", 
    "GigabitEthernet0/0/3",
    "Serial0/1/0",
    "Serial0/1/1",
    "Loopback1",
    "Loopback2"
  ];

  const handleAddVrf = () => {
    if (newVrf.name && newVrf.rd) {
      const vrf = {
        id: vrfs.length + 1,
        ...newVrf,
        rtImport: newVrf.rtImport ? newVrf.rtImport.split(',').map(rt => rt.trim()) : [],
        rtExport: newVrf.rtExport ? newVrf.rtExport.split(',').map(rt => rt.trim()) : [],
        interfaces: [],
        status: "inactive",
        routes: []
      };
      
      setVrfs(prev => [...prev, vrf]);
      setNewVrf({ name: "", rd: "", rtImport: "", rtExport: "", description: "" });
      setIsAddingVrf(false);
      toast.success("VRF creada correctamente");
    }
  };

  const handleDeleteVrf = (id: number) => {
    setVrfs(prev => prev.filter(vrf => vrf.id !== id));
    toast.success("VRF eliminada correctamente");
  };

  const handleToggleStatus = (id: number) => {
    setVrfs(prev => prev.map(vrf => 
      vrf.id === id 
        ? { ...vrf, status: vrf.status === "active" ? "inactive" : "active" }
        : vrf
    ));
  };

  const getStatusBadge = (status: string) => {
    return (
      <Badge variant={status === "active" ? "default" : "secondary"}>
        {status === "active" ? "Activa" : "Inactiva"}
      </Badge>
    );
  };

  const getRouteTypeBadge = (type: string) => {
    const variants = {
      connected: "default",
      static: "secondary", 
      ospf: "outline",
      bgp: "destructive"
    };
    
    return (
      <Badge variant={variants[type] || "outline"}>
        {type.toUpperCase()}
      </Badge>
    );
  };

  const handleViewDetails = (vrf) => {
    setSelectedVrf(vrf);
    setIsViewingDetails(true);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2>Configuración de VRF</h2>
          <p className="text-muted-foreground">Virtual Routing and Forwarding - Gestión de instancias de enrutamiento</p>
        </div>
        <Dialog open={isAddingVrf} onOpenChange={setIsAddingVrf}>
          <DialogTrigger asChild>
            <Button className="flex items-center gap-2">
              <Plus className="h-4 w-4" />
              Nueva VRF
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Crear Nueva VRF</DialogTitle>
              <DialogDescription>Configura una nueva instancia de enrutamiento virtual</DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="vrf-name">Nombre de la VRF</Label>
                <Input
                  id="vrf-name"
                  placeholder="CUSTOMER_C"
                  value={newVrf.name}
                  onChange={(e) => setNewVrf(prev => ({ ...prev, name: e.target.value }))}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="vrf-rd">Route Distinguisher (RD)</Label>
                <Input
                  id="vrf-rd"
                  placeholder="65001:400"
                  value={newVrf.rd}
                  onChange={(e) => setNewVrf(prev => ({ ...prev, rd: e.target.value }))}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="vrf-rt-import">Route Target Import (separados por coma)</Label>
                <Input
                  id="vrf-rt-import"
                  placeholder="65001:400, 65001:999"
                  value={newVrf.rtImport}
                  onChange={(e) => setNewVrf(prev => ({ ...prev, rtImport: e.target.value }))}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="vrf-rt-export">Route Target Export (separados por coma)</Label>
                <Input
                  id="vrf-rt-export"
                  placeholder="65001:400"
                  value={newVrf.rtExport}
                  onChange={(e) => setNewVrf(prev => ({ ...prev, rtExport: e.target.value }))}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="vrf-description">Descripción</Label>
                <Input
                  id="vrf-description"
                  placeholder="Descripción de la VRF"
                  value={newVrf.description}
                  onChange={(e) => setNewVrf(prev => ({ ...prev, description: e.target.value }))}
                />
              </div>
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setIsAddingVrf(false)}>
                  Cancelar
                </Button>
                <Button onClick={handleAddVrf}>
                  Crear VRF
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total VRFs</CardTitle>
            <Layers className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{vrfs.length}</div>
            <p className="text-xs text-muted-foreground">instancias configuradas</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">VRFs Activas</CardTitle>
            <Activity className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {vrfs.filter(vrf => vrf.status === "active").length}
            </div>
            <p className="text-xs text-muted-foreground">en funcionamiento</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Interfaces Asignadas</CardTitle>
            <Network className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">
              {vrfs.reduce((total, vrf) => total + vrf.interfaces.length, 0)}
            </div>
            <p className="text-xs text-muted-foreground">interfaces en VRFs</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Rutas</CardTitle>
            <Route className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              {vrfs.reduce((total, vrf) => total + vrf.routes.length, 0)}
            </div>
            <p className="text-xs text-muted-foreground">rutas en todas las VRFs</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Lista de VRFs</CardTitle>
          <CardDescription>Instancias de enrutamiento virtual configuradas</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nombre</TableHead>
                <TableHead>RD</TableHead>
                <TableHead>Estado</TableHead>
                <TableHead>Interfaces</TableHead>
                <TableHead>Rutas</TableHead>
                <TableHead>Descripción</TableHead>
                <TableHead>Acciones</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {vrfs.map((vrf) => (
                <TableRow key={vrf.id}>
                  <TableCell className="font-mono font-medium">{vrf.name}</TableCell>
                  <TableCell className="font-mono text-sm">{vrf.rd}</TableCell>
                  <TableCell>{getStatusBadge(vrf.status)}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <span>{vrf.interfaces.length}</span>
                      <Badge variant="outline" className="text-xs">
                        interfaces
                      </Badge>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <span>{vrf.routes.length}</span>
                      <Badge variant="outline" className="text-xs">
                        rutas
                      </Badge>
                    </div>
                  </TableCell>
                  <TableCell className="max-w-xs truncate">{vrf.description}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleViewDetails(vrf)}
                      >
                        <Eye className="h-3 w-3" />
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleToggleStatus(vrf.id)}
                      >
                        {vrf.status === "active" ? "Desactivar" : "Activar"}
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleDeleteVrf(vrf.id)}
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

      {/* VRF Details Dialog */}
      <Dialog open={isViewingDetails} onOpenChange={setIsViewingDetails}>
        <DialogContent className="max-w-4xl max-h-[80vh]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Layers className="h-5 w-5" />
              Detalles de VRF: {selectedVrf?.name}
            </DialogTitle>
            <DialogDescription>
              Información detallada de la instancia de enrutamiento virtual
            </DialogDescription>
          </DialogHeader>
          
          {selectedVrf && (
            <Tabs defaultValue="general" className="space-y-4">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="general">General</TabsTrigger>
                <TabsTrigger value="interfaces">Interfaces</TabsTrigger>
                <TabsTrigger value="routes">Tabla de Rutas</TabsTrigger>
                <TabsTrigger value="rt">Route Targets</TabsTrigger>
              </TabsList>

              <TabsContent value="general" className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-base">Información Básica</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div className="flex justify-between">
                        <span className="font-medium">Nombre:</span>
                        <span className="font-mono">{selectedVrf.name}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="font-medium">Route Distinguisher:</span>
                        <span className="font-mono">{selectedVrf.rd}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="font-medium">Estado:</span>
                        {getStatusBadge(selectedVrf.status)}
                      </div>
                      <div className="flex justify-between">
                        <span className="font-medium">Descripción:</span>
                        <span className="text-sm">{selectedVrf.description}</span>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="text-base">Estadísticas</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div className="flex justify-between">
                        <span className="font-medium">Interfaces:</span>
                        <Badge>{selectedVrf.interfaces.length}</Badge>
                      </div>
                      <div className="flex justify-between">
                        <span className="font-medium">Rutas:</span>
                        <Badge>{selectedVrf.routes.length}</Badge>
                      </div>
                      <div className="flex justify-between">
                        <span className="font-medium">RT Import:</span>
                        <Badge>{selectedVrf.rtImport.length}</Badge>
                      </div>
                      <div className="flex justify-between">
                        <span className="font-medium">RT Export:</span>
                        <Badge>{selectedVrf.rtExport.length}</Badge>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>

              <TabsContent value="interfaces" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Interfaces Asignadas</CardTitle>
                    <CardDescription>Interfaces que pertenecen a esta VRF</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {selectedVrf.interfaces.length > 0 ? (
                      <div className="space-y-2">
                        {selectedVrf.interfaces.map((iface, index) => (
                          <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                            <div className="flex items-center gap-2">
                              <Network className="h-4 w-4 text-blue-500" />
                              <span className="font-mono">{iface}</span>
                            </div>
                            <Badge variant="outline">Asignada</Badge>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-8 text-muted-foreground">
                        No hay interfaces asignadas a esta VRF
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="routes" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Tabla de Enrutamiento</CardTitle>
                    <CardDescription>Rutas disponibles en esta VRF</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {selectedVrf.routes.length > 0 ? (
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Red</TableHead>
                            <TableHead>Next Hop</TableHead>
                            <TableHead>Tipo</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {selectedVrf.routes.map((route, index) => (
                            <TableRow key={index}>
                              <TableCell className="font-mono">{route.network}</TableCell>
                              <TableCell className="font-mono">{route.nextHop}</TableCell>
                              <TableCell>{getRouteTypeBadge(route.type)}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    ) : (
                      <div className="text-center py-8 text-muted-foreground">
                        No hay rutas configuradas en esta VRF
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="rt" className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-base">Route Target Import</CardTitle>
                      <CardDescription>RTs que esta VRF puede importar</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {selectedVrf.rtImport.map((rt, index) => (
                          <div key={index} className="flex items-center gap-2">
                            <Globe className="h-4 w-4 text-green-500" />
                            <span className="font-mono">{rt}</span>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="text-base">Route Target Export</CardTitle>
                      <CardDescription>RTs que esta VRF puede exportar</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {selectedVrf.rtExport.map((rt, index) => (
                          <div key={index} className="flex items-center gap-2">
                            <Route className="h-4 w-4 text-blue-500" />
                            <span className="font-mono">{rt}</span>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>
            </Tabs>
          )}
        </DialogContent>
      </Dialog>

      {/* Configuration Commands Preview */}
      <Card>
        <CardHeader>
          <CardTitle>Comandos de Configuración VRF</CardTitle>
          <CardDescription>Vista previa de los comandos para configurar las VRFs</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="bg-black text-green-400 p-4 rounded-lg font-mono text-sm space-y-1">
            <div className="text-gray-500"># Configuración de VRFs</div>
            {vrfs.filter(vrf => vrf.status === "active").map((vrf) => (
              <div key={vrf.id} className="space-y-1">
                <div>vrf definition {vrf.name}</div>
                <div className="ml-4">rd {vrf.rd}</div>
                {vrf.rtImport.map((rt, index) => (
                  <div key={index} className="ml-4">route-target import {rt}</div>
                ))}
                {vrf.rtExport.map((rt, index) => (
                  <div key={index} className="ml-4">route-target export {rt}</div>
                ))}
                <div className="ml-4">address-family ipv4</div>
                <div className="ml-4">exit-address-family</div>
                <div className="ml-4">exit</div>
                <div className="text-gray-500 text-xs"># Asignación de interfaces para {vrf.name}</div>
                {vrf.interfaces.map((iface, index) => (
                  <div key={index} className="space-y-1">
                    <div>interface {iface}</div>
                    <div className="ml-4">vrf forwarding {vrf.name}</div>
                    <div className="ml-4">exit</div>
                  </div>
                ))}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
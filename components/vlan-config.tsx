import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { Badge } from "./ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "./ui/dialog";
import { Checkbox } from "./ui/checkbox";
import { Plus, Edit, Trash2, Network, Save } from "lucide-react";
import { toast } from "sonner@2.0.3";

export function VLANConfig() {
  const [vlans, setVlans] = useState([
    { id: 1, vlanId: 10, name: "Administración", description: "Red administrativa", subnet: "192.168.10.0/24", ports: ["1", "2"] },
    { id: 2, vlanId: 20, name: "Invitados", description: "Red para invitados", subnet: "192.168.20.0/24", ports: ["3", "4"] },
    { id: 3, vlanId: 30, name: "Servidores", description: "Red de servidores", subnet: "192.168.30.0/24", ports: ["5"] },
    { id: 4, vlanId: 100, name: "IoT", description: "Dispositivos IoT", subnet: "192.168.100.0/24", ports: ["WiFi"] }
  ]);

  const [portConfig, setPortConfig] = useState([
    { port: "1", mode: "access", vlan: "10", description: "Puerto administrativo" },
    { port: "2", mode: "access", vlan: "10", description: "Puerto administrativo" },
    { port: "3", mode: "access", vlan: "20", description: "Puerto invitados" },
    { port: "4", mode: "trunk", vlan: "1,10,20", description: "Trunk principal" },
    { port: "5", mode: "access", vlan: "30", description: "Puerto servidores" }
  ]);

  const [newVlan, setNewVlan] = useState({
    vlanId: "",
    name: "",
    description: "",
    subnet: "",
    ports: []
  });

  const [isAddingVlan, setIsAddingVlan] = useState(false);
  const [isEditingPort, setIsEditingPort] = useState(false);
  const [editingPort, setEditingPort] = useState(null);

  const availablePorts = ["1", "2", "3", "4", "5", "WiFi"];

  const handleAddVlan = () => {
    if (newVlan.vlanId && newVlan.name && newVlan.subnet) {
      setVlans(prev => [...prev, {
        id: prev.length + 1,
        vlanId: parseInt(newVlan.vlanId),
        name: newVlan.name,
        description: newVlan.description,
        subnet: newVlan.subnet,
        ports: newVlan.ports
      }]);
      setNewVlan({ vlanId: "", name: "", description: "", subnet: "", ports: [] });
      setIsAddingVlan(false);
      toast.success("VLAN creada correctamente");
    }
  };

  const handleDeleteVlan = (id: number) => {
    setVlans(prev => prev.filter(vlan => vlan.id !== id));
    toast.success("VLAN eliminada correctamente");
  };

  const handlePortConfigChange = (port: string, field: string, value: string) => {
    setPortConfig(prev => prev.map(config => 
      config.port === port 
        ? { ...config, [field]: value }
        : config
    ));
  };

  const handleSavePortConfig = () => {
    toast.success("Configuración de puertos guardada");
  };

  const getVlanBadgeColor = (vlanId: number) => {
    const colors = ["default", "secondary", "destructive", "outline"];
    return colors[vlanId % colors.length];
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2>Configuración VLAN</h2>
          <p className="text-muted-foreground">Administra las redes virtuales y la segmentación de red</p>
        </div>
        <Dialog open={isAddingVlan} onOpenChange={setIsAddingVlan}>
          <DialogTrigger asChild>
            <Button className="flex items-center gap-2">
              <Plus className="h-4 w-4" />
              Crear VLAN
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Nueva VLAN</DialogTitle>
              <DialogDescription>
                Crear una nueva red virtual local (VLAN)
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="vlan-id">ID de VLAN</Label>
                  <Input
                    id="vlan-id"
                    type="number"
                    placeholder="100"
                    value={newVlan.vlanId}
                    onChange={(e) => setNewVlan(prev => ({ ...prev, vlanId: e.target.value }))}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="vlan-name">Nombre</Label>
                  <Input
                    id="vlan-name"
                    placeholder="Mi VLAN"
                    value={newVlan.name}
                    onChange={(e) => setNewVlan(prev => ({ ...prev, name: e.target.value }))}
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="vlan-description">Descripción</Label>
                <Input
                  id="vlan-description"
                  placeholder="Descripción de la VLAN"
                  value={newVlan.description}
                  onChange={(e) => setNewVlan(prev => ({ ...prev, description: e.target.value }))}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="vlan-subnet">Subred</Label>
                <Input
                  id="vlan-subnet"
                  placeholder="192.168.100.0/24"
                  value={newVlan.subnet}
                  onChange={(e) => setNewVlan(prev => ({ ...prev, subnet: e.target.value }))}
                />
              </div>
              <div className="space-y-3">
                <Label>Puertos Asignados</Label>
                <div className="grid grid-cols-3 gap-2">
                  {availablePorts.map(port => (
                    <div key={port} className="flex items-center space-x-2">
                      <Checkbox
                        id={`port-${port}`}
                        checked={newVlan.ports.includes(port)}
                        onCheckedChange={(checked) => {
                          if (checked) {
                            setNewVlan(prev => ({ ...prev, ports: [...prev.ports, port] }));
                          } else {
                            setNewVlan(prev => ({ ...prev, ports: prev.ports.filter(p => p !== port) }));
                          }
                        }}
                      />
                      <Label htmlFor={`port-${port}`} className="text-sm">
                        Puerto {port}
                      </Label>
                    </div>
                  ))}
                </div>
              </div>
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setIsAddingVlan(false)}>
                  Cancelar
                </Button>
                <Button onClick={handleAddVlan}>
                  Crear VLAN
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* VLANs List */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Network className="h-5 w-5" />
              VLANs Configuradas
            </CardTitle>
            <CardDescription>
              Lista de todas las redes virtuales configuradas
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {vlans.map((vlan) => (
                <div key={vlan.id} className="border rounded-lg p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Badge variant={getVlanBadgeColor(vlan.vlanId)}>
                        VLAN {vlan.vlanId}
                      </Badge>
                      <div>
                        <h4 className="font-medium">{vlan.name}</h4>
                        <p className="text-sm text-muted-foreground">{vlan.description}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button variant="outline" size="sm">
                        <Edit className="h-3 w-3" />
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleDeleteVlan(vlan.id)}
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                  <div className="text-sm space-y-1">
                    <p><span className="font-medium">Subred:</span> {vlan.subnet}</p>
                    <p><span className="font-medium">Puertos:</span> {vlan.ports.join(", ")}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Port Configuration */}
        <Card>
          <CardHeader>
            <CardTitle>Configuración de Puertos</CardTitle>
            <CardDescription>
              Configura el modo y VLAN de cada puerto
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Puerto</TableHead>
                  <TableHead>Modo</TableHead>
                  <TableHead>VLAN</TableHead>
                  <TableHead>Descripción</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {portConfig.map((config) => (
                  <TableRow key={config.port}>
                    <TableCell className="font-medium">Puerto {config.port}</TableCell>
                    <TableCell>
                      <Select
                        value={config.mode}
                        onValueChange={(value) => handlePortConfigChange(config.port, "mode", value)}
                      >
                        <SelectTrigger className="w-24">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="access">Access</SelectItem>
                          <SelectItem value="trunk">Trunk</SelectItem>
                        </SelectContent>
                      </Select>
                    </TableCell>
                    <TableCell>
                      <Input
                        value={config.vlan}
                        onChange={(e) => handlePortConfigChange(config.port, "vlan", e.target.value)}
                        className="w-20"
                      />
                    </TableCell>
                    <TableCell>
                      <Input
                        value={config.description}
                        onChange={(e) => handlePortConfigChange(config.port, "description", e.target.value)}
                        className="w-full"
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            <div className="flex justify-end">
              <Button onClick={handleSavePortConfig} className="flex items-center gap-2">
                <Save className="h-4 w-4" />
                Guardar Configuración de Puertos
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* VLAN Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Resumen de VLANs</CardTitle>
          <CardDescription>
            Vista general del estado de las VLANs
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="text-center p-4 border rounded-lg">
              <div className="text-2xl font-bold">{vlans.length}</div>
              <p className="text-sm text-muted-foreground">VLANs Totales</p>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <div className="text-2xl font-bold">{portConfig.filter(p => p.mode === "access").length}</div>
              <p className="text-sm text-muted-foreground">Puertos Access</p>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <div className="text-2xl font-bold">{portConfig.filter(p => p.mode === "trunk").length}</div>
              <p className="text-sm text-muted-foreground">Puertos Trunk</p>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <div className="text-2xl font-bold">{availablePorts.length}</div>
              <p className="text-sm text-muted-foreground">Puertos Totales</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
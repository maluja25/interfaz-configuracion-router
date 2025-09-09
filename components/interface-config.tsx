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
import { Network, Edit, Save, Plus, Trash2, Settings, Activity } from "lucide-react";
import { toast } from "sonner@2.0.3";

export function InterfaceConfig() {
  const [interfaces, setInterfaces] = useState([
    { 
      id: 1, 
      name: "GigabitEthernet0/0/1", 
      type: "Ethernet", 
      ip: "192.168.1.1", 
      mask: "255.255.255.0", 
      status: "up", 
      description: "LAN Principal",
      duplex: "full",
      speed: "1000"
    },
    { 
      id: 2, 
      name: "GigabitEthernet0/0/2", 
      type: "Ethernet", 
      ip: "10.0.0.1", 
      mask: "255.255.255.0", 
      status: "up", 
      description: "Red Servidores",
      duplex: "full",
      speed: "1000"
    },
    { 
      id: 3, 
      name: "Serial0/1/0", 
      type: "Serial", 
      ip: "203.0.113.2", 
      mask: "255.255.255.252", 
      status: "up", 
      description: "WAN Principal",
      duplex: "full",
      speed: "1544"
    },
    { 
      id: 4, 
      name: "GigabitEthernet0/0/3", 
      type: "Ethernet", 
      ip: "", 
      mask: "", 
      status: "down", 
      description: "Sin configurar",
      duplex: "auto",
      speed: "auto"
    },
    { 
      id: 5, 
      name: "Loopback0", 
      type: "Loopback", 
      ip: "1.1.1.1", 
      mask: "255.255.255.255", 
      status: "up", 
      description: "Router ID",
      duplex: "N/A",
      speed: "N/A"
    }
  ]);

  const [editingInterface, setEditingInterface] = useState(null);
  const [isEditing, setIsEditing] = useState(false);

  const [formData, setFormData] = useState({
    ip: "",
    mask: "",
    description: "",
    status: "up",
    duplex: "auto",
    speed: "auto"
  });

  const handleEdit = (interface_) => {
    setEditingInterface(interface_);
    setFormData({
      ip: interface_.ip,
      mask: interface_.mask,
      description: interface_.description,
      status: interface_.status,
      duplex: interface_.duplex,
      speed: interface_.speed
    });
    setIsEditing(true);
  };

  const handleSave = () => {
    if (editingInterface) {
      setInterfaces(prev => prev.map(iface => 
        iface.id === editingInterface.id 
          ? { ...iface, ...formData }
          : iface
      ));
      setIsEditing(false);
      setEditingInterface(null);
      toast.success(`Interfaz ${editingInterface.name} configurada correctamente`);
    }
  };

  const handleToggleStatus = (id: number) => {
    setInterfaces(prev => prev.map(iface => 
      iface.id === id 
        ? { ...iface, status: iface.status === "up" ? "down" : "up" }
        : iface
    ));
  };

  const getStatusBadge = (status: string) => {
    return (
      <Badge variant={status === "up" ? "default" : "secondary"}>
        {status === "up" ? "UP" : "DOWN"}
      </Badge>
    );
  };

  const getInterfaceTypeIcon = (type: string) => {
    switch (type) {
      case "Ethernet":
        return <Network className="h-4 w-4 text-blue-500" />;
      case "Serial":
        return <Activity className="h-4 w-4 text-green-500" />;
      case "Loopback":
        return <Settings className="h-4 w-4 text-purple-500" />;
      default:
        return <Network className="h-4 w-4 text-gray-500" />;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2>Configuración de Interfaces</h2>
          <p className="text-muted-foreground">Administra las interfaces de red del router</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Interface Statistics */}
        <Card>
          <CardHeader>
            <CardTitle>Resumen de Interfaces</CardTitle>
            <CardDescription>Estado general de las interfaces</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span>Total de Interfaces</span>
              <Badge variant="outline">{interfaces.length}</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span>Interfaces Activas</span>
              <Badge variant="default">{interfaces.filter(i => i.status === "up").length}</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span>Interfaces Inactivas</span>
              <Badge variant="secondary">{interfaces.filter(i => i.status === "down").length}</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span>Sin Configurar</span>
              <Badge variant="outline">{interfaces.filter(i => !i.ip).length}</Badge>
            </div>
          </CardContent>
        </Card>

        {/* Interface List */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Lista de Interfaces</CardTitle>
            <CardDescription>Configuración detallada de cada interfaz</CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Interfaz</TableHead>
                  <TableHead>Tipo</TableHead>
                  <TableHead>Dirección IP</TableHead>
                  <TableHead>Máscara</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead>Descripción</TableHead>
                  <TableHead>Acciones</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {interfaces.map((interface_) => (
                  <TableRow key={interface_.id}>
                    <TableCell className="flex items-center gap-2">
                      {getInterfaceTypeIcon(interface_.type)}
                      <span className="font-mono text-sm">{interface_.name}</span>
                    </TableCell>
                    <TableCell>{interface_.type}</TableCell>
                    <TableCell className="font-mono">{interface_.ip || "N/A"}</TableCell>
                    <TableCell className="font-mono">{interface_.mask || "N/A"}</TableCell>
                    <TableCell>{getStatusBadge(interface_.status)}</TableCell>
                    <TableCell>{interface_.description}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleEdit(interface_)}
                        >
                          <Edit className="h-3 w-3" />
                        </Button>
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleToggleStatus(interface_.id)}
                        >
                          {interface_.status === "up" ? "Desactivar" : "Activar"}
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>

      {/* Configuration Dialog */}
      <Dialog open={isEditing} onOpenChange={setIsEditing}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Configurar Interfaz</DialogTitle>
            <DialogDescription>
              Configura los parámetros de la interfaz {editingInterface?.name}
            </DialogDescription>
          </DialogHeader>
          
          <Tabs defaultValue="ip" className="space-y-4">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="ip">Configuración IP</TabsTrigger>
              <TabsTrigger value="physical">Configuración Física</TabsTrigger>
            </TabsList>

            <TabsContent value="ip" className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="ip">Dirección IP</Label>
                  <Input
                    id="ip"
                    placeholder="192.168.1.1"
                    value={formData.ip}
                    onChange={(e) => setFormData(prev => ({ ...prev, ip: e.target.value }))}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="mask">Máscara de Subred</Label>
                  <Input
                    id="mask"
                    placeholder="255.255.255.0"
                    value={formData.mask}
                    onChange={(e) => setFormData(prev => ({ ...prev, mask: e.target.value }))}
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="description">Descripción</Label>
                <Input
                  id="description"
                  placeholder="Descripción de la interfaz"
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Estado de la Interfaz</Label>
                  <p className="text-sm text-muted-foreground">
                    Activar o desactivar la interfaz
                  </p>
                </div>
                <Switch
                  checked={formData.status === "up"}
                  onCheckedChange={(checked) => setFormData(prev => ({ 
                    ...prev, 
                    status: checked ? "up" : "down" 
                  }))}
                />
              </div>
            </TabsContent>

            <TabsContent value="physical" className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="duplex">Modo Duplex</Label>
                  <Select value={formData.duplex} onValueChange={(value) => setFormData(prev => ({ ...prev, duplex: value }))}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="auto">Auto</SelectItem>
                      <SelectItem value="full">Full Duplex</SelectItem>
                      <SelectItem value="half">Half Duplex</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="speed">Velocidad</Label>
                  <Select value={formData.speed} onValueChange={(value) => setFormData(prev => ({ ...prev, speed: value }))}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="auto">Auto</SelectItem>
                      <SelectItem value="10">10 Mbps</SelectItem>
                      <SelectItem value="100">100 Mbps</SelectItem>
                      <SelectItem value="1000">1 Gbps</SelectItem>
                      <SelectItem value="10000">10 Gbps</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label>Información de la Interfaz</Label>
                <div className="grid grid-cols-2 gap-4 p-4 border rounded-lg bg-muted/50">
                  <div>
                    <p className="text-sm font-medium">Nombre:</p>
                    <p className="text-sm text-muted-foreground font-mono">{editingInterface?.name}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium">Tipo:</p>
                    <p className="text-sm text-muted-foreground">{editingInterface?.type}</p>
                  </div>
                </div>
              </div>
            </TabsContent>
          </Tabs>

          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setIsEditing(false)}>
              Cancelar
            </Button>
            <Button onClick={handleSave} className="flex items-center gap-2">
              <Save className="h-4 w-4" />
              Guardar Configuración
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Configuration Commands Preview */}
      <Card>
        <CardHeader>
          <CardTitle>Comandos de Configuración</CardTitle>
          <CardDescription>
            Vista previa de los comandos que se ejecutarán en el router
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="bg-black text-green-400 p-4 rounded-lg font-mono text-sm space-y-1">
            <div className="text-gray-500"># Configuración de interfaces activas</div>
            {interfaces.filter(i => i.ip && i.status === "up").map((interface_) => (
              <div key={interface_.id} className="space-y-1">
                <div>interface {interface_.name}</div>
                <div className="ml-4">ip address {interface_.ip} {interface_.mask}</div>
                <div className="ml-4">description {interface_.description}</div>
                <div className="ml-4">no shutdown</div>
                <div className="ml-4">exit</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
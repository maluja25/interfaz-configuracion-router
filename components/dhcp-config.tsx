import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Switch } from "./ui/switch";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { Badge } from "./ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "./ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Plus, Trash2, Edit, Save, Users, Clock, Settings } from "lucide-react";
import { toast } from "sonner@2.0.3";

export function DHCPConfig() {
  const [dhcpSettings, setDHCPSettings] = useState({
    enabled: true,
    startIP: "192.168.1.100",
    endIP: "192.168.1.200",
    leaseTime: "24",
    gateway: "192.168.1.1",
    dns1: "8.8.8.8",
    dns2: "8.8.4.4"
  });

  const [reservations, setReservations] = useState([
    { id: 1, hostname: "Servidor-Principal", mac: "AA:BB:CC:DD:EE:FF", ip: "192.168.1.10", description: "Servidor web" },
    { id: 2, hostname: "Impresora-Oficina", mac: "11:22:33:44:55:66", ip: "192.168.1.20", description: "Impresora HP LaserJet" },
    { id: 3, hostname: "NAS-Storage", mac: "77:88:99:AA:BB:CC", ip: "192.168.1.30", description: "Almacenamiento de red" }
  ]);

  const [activeLeases, setActiveLeases] = useState([
    { hostname: "MacBook-Pro", mac: "AB:CD:EF:12:34:56", ip: "192.168.1.101", lease: "12h 30m", type: "Dinámica" },
    { hostname: "iPhone-12", mac: "12:34:56:78:90:AB", ip: "192.168.1.102", lease: "18h 45m", type: "Dinámica" },
    { hostname: "Windows-PC", mac: "56:78:90:AB:CD:EF", ip: "192.168.1.103", lease: "6h 15m", type: "Dinámica" },
    { hostname: "Servidor-Principal", mac: "AA:BB:CC:DD:EE:FF", ip: "192.168.1.10", lease: "Permanente", type: "Reservada" },
    { hostname: "Smart-TV", mac: "CD:EF:12:34:56:78", ip: "192.168.1.104", lease: "23h 10m", type: "Dinámica" }
  ]);

  const [newReservation, setNewReservation] = useState({
    hostname: "",
    mac: "",
    ip: "",
    description: ""
  });

  const [isAddingReservation, setIsAddingReservation] = useState(false);

  const handleSaveSettings = () => {
    toast.success("Configuración DHCP guardada correctamente");
  };

  const handleAddReservation = () => {
    if (newReservation.hostname && newReservation.mac && newReservation.ip) {
      setReservations(prev => [...prev, {
        id: prev.length + 1,
        ...newReservation
      }]);
      setNewReservation({ hostname: "", mac: "", ip: "", description: "" });
      setIsAddingReservation(false);
      toast.success("Reserva DHCP agregada correctamente");
    }
  };

  const handleDeleteReservation = (id: number) => {
    setReservations(prev => prev.filter(res => res.id !== id));
    toast.success("Reserva DHCP eliminada correctamente");
  };

  const handleReleaseIP = (ip: string) => {
    setActiveLeases(prev => prev.filter(lease => lease.ip !== ip));
    toast.success(`IP ${ip} liberada correctamente`);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2>Configuración DHCP</h2>
          <p className="text-muted-foreground">Administra el servidor DHCP y las asignaciones de IP</p>
        </div>
      </div>

      <Tabs defaultValue="settings" className="space-y-4">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="settings" className="flex items-center gap-2">
            <Settings className="h-4 w-4" />
            Configuración
          </TabsTrigger>
          <TabsTrigger value="reservations" className="flex items-center gap-2">
            <Users className="h-4 w-4" />
            Reservas
          </TabsTrigger>
          <TabsTrigger value="leases" className="flex items-center gap-2">
            <Clock className="h-4 w-4" />
            Concesiones Activas
          </TabsTrigger>
        </TabsList>

        <TabsContent value="settings" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Configuración del Servidor DHCP</CardTitle>
              <CardDescription>
                Configura los parámetros generales del servidor DHCP
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Servidor DHCP Habilitado</Label>
                  <p className="text-sm text-muted-foreground">
                    Asigna automáticamente direcciones IP a los dispositivos
                  </p>
                </div>
                <Switch
                  checked={dhcpSettings.enabled}
                  onCheckedChange={(checked) => setDHCPSettings(prev => ({ ...prev, enabled: checked }))}
                />
              </div>

              {dhcpSettings.enabled && (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="start-ip">IP Inicial del Pool</Label>
                      <Input
                        id="start-ip"
                        value={dhcpSettings.startIP}
                        onChange={(e) => setDHCPSettings(prev => ({ ...prev, startIP: e.target.value }))}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="end-ip">IP Final del Pool</Label>
                      <Input
                        id="end-ip"
                        value={dhcpSettings.endIP}
                        onChange={(e) => setDHCPSettings(prev => ({ ...prev, endIP: e.target.value }))}
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="lease-time">Tiempo de Concesión (horas)</Label>
                      <Input
                        id="lease-time"
                        type="number"
                        value={dhcpSettings.leaseTime}
                        onChange={(e) => setDHCPSettings(prev => ({ ...prev, leaseTime: e.target.value }))}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="gateway">Puerta de Enlace</Label>
                      <Input
                        id="gateway"
                        value={dhcpSettings.gateway}
                        onChange={(e) => setDHCPSettings(prev => ({ ...prev, gateway: e.target.value }))}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="dns1">Servidor DNS Primario</Label>
                      <Input
                        id="dns1"
                        value={dhcpSettings.dns1}
                        onChange={(e) => setDHCPSettings(prev => ({ ...prev, dns1: e.target.value }))}
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="dns2">Servidor DNS Secundario</Label>
                    <Input
                      id="dns2"
                      value={dhcpSettings.dns2}
                      onChange={(e) => setDHCPSettings(prev => ({ ...prev, dns2: e.target.value }))}
                      className="max-w-md"
                    />
                  </div>
                </div>
              )}

              <div className="flex justify-end">
                <Button onClick={handleSaveSettings} className="flex items-center gap-2">
                  <Save className="h-4 w-4" />
                  Guardar Configuración
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="reservations" className="space-y-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Reservas DHCP</CardTitle>
                <CardDescription>
                  Asigna direcciones IP específicas a dispositivos por su MAC
                </CardDescription>
              </div>
              <Dialog open={isAddingReservation} onOpenChange={setIsAddingReservation}>
                <DialogTrigger asChild>
                  <Button className="flex items-center gap-2">
                    <Plus className="h-4 w-4" />
                    Agregar Reserva
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Nueva Reserva DHCP</DialogTitle>
                    <DialogDescription>
                      Crea una nueva reserva de IP para un dispositivo específico
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="new-hostname">Nombre del Dispositivo</Label>
                      <Input
                        id="new-hostname"
                        placeholder="Mi-Dispositivo"
                        value={newReservation.hostname}
                        onChange={(e) => setNewReservation(prev => ({ ...prev, hostname: e.target.value }))}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="new-mac">Dirección MAC</Label>
                      <Input
                        id="new-mac"
                        placeholder="AA:BB:CC:DD:EE:FF"
                        value={newReservation.mac}
                        onChange={(e) => setNewReservation(prev => ({ ...prev, mac: e.target.value }))}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="new-ip">Dirección IP</Label>
                      <Input
                        id="new-ip"
                        placeholder="192.168.1.50"
                        value={newReservation.ip}
                        onChange={(e) => setNewReservation(prev => ({ ...prev, ip: e.target.value }))}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="new-description">Descripción (opcional)</Label>
                      <Input
                        id="new-description"
                        placeholder="Descripción del dispositivo"
                        value={newReservation.description}
                        onChange={(e) => setNewReservation(prev => ({ ...prev, description: e.target.value }))}
                      />
                    </div>
                    <div className="flex justify-end gap-2">
                      <Button variant="outline" onClick={() => setIsAddingReservation(false)}>
                        Cancelar
                      </Button>
                      <Button onClick={handleAddReservation}>
                        Agregar Reserva
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
                    <TableHead>Nombre</TableHead>
                    <TableHead>Dirección MAC</TableHead>
                    <TableHead>IP Reservada</TableHead>
                    <TableHead>Descripción</TableHead>
                    <TableHead>Acciones</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {reservations.map((reservation) => (
                    <TableRow key={reservation.id}>
                      <TableCell className="font-medium">{reservation.hostname}</TableCell>
                      <TableCell className="font-mono">{reservation.mac}</TableCell>
                      <TableCell>{reservation.ip}</TableCell>
                      <TableCell className="text-muted-foreground">{reservation.description}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Button variant="outline" size="sm">
                            <Edit className="h-3 w-3" />
                          </Button>
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => handleDeleteReservation(reservation.id)}
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

        <TabsContent value="leases" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Concesiones Activas</CardTitle>
              <CardDescription>
                Dispositivos que actualmente tienen una dirección IP asignada
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Nombre</TableHead>
                    <TableHead>Dirección MAC</TableHead>
                    <TableHead>IP Asignada</TableHead>
                    <TableHead>Tiempo Restante</TableHead>
                    <TableHead>Tipo</TableHead>
                    <TableHead>Acciones</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {activeLeases.map((lease, index) => (
                    <TableRow key={index}>
                      <TableCell className="font-medium">{lease.hostname}</TableCell>
                      <TableCell className="font-mono">{lease.mac}</TableCell>
                      <TableCell>{lease.ip}</TableCell>
                      <TableCell>{lease.lease}</TableCell>
                      <TableCell>
                        <Badge variant={lease.type === "Reservada" ? "default" : "secondary"}>
                          {lease.type}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {lease.type === "Dinámica" && (
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => handleReleaseIP(lease.ip)}
                          >
                            Liberar IP
                          </Button>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
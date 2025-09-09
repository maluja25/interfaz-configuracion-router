import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Switch } from "./ui/switch";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { Badge } from "./ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "./ui/dialog";
import { Shield, Lock, Eye, EyeOff, Plus, Trash2, AlertTriangle, Save } from "lucide-react";
import { toast } from "sonner@2.0.3";

export function SecurityConfig() {
  const [firewallEnabled, setFirewallEnabled] = useState(true);
  const [intrustionDetection, setIntrusionDetection] = useState(true);
  const [ddosProtection, setDdosProtection] = useState(true);
  
  const [firewallRules, setFirewallRules] = useState([
    { id: 1, name: "Bloquear Torrent", source: "Any", destination: "Any", port: "6881-6889", protocol: "TCP", action: "DENY", status: "Activa" },
    { id: 2, name: "Permitir SSH", source: "192.168.1.0/24", destination: "192.168.1.10", port: "22", protocol: "TCP", action: "ALLOW", status: "Activa" },
    { id: 3, name: "Bloquear Malware", source: "Any", destination: "blacklist.db", port: "Any", protocol: "Any", action: "DENY", status: "Activa" },
    { id: 4, name: "Permitir HTTP/HTTPS", source: "Any", destination: "Any", port: "80,443", protocol: "TCP", action: "ALLOW", status: "Activa" }
  ]);

  const [accessControl, setAccessControl] = useState([
    { id: 1, device: "MacBook Pro", mac: "AA:BB:CC:DD:EE:FF", timeRestriction: "Siempre", access: "Permitido", parentalControl: false },
    { id: 2, device: "iPhone Kids", mac: "11:22:33:44:55:66", timeRestriction: "08:00-20:00", access: "Restringido", parentalControl: true },
    { id: 3, device: "Smart TV", mac: "77:88:99:AA:BB:CC", timeRestriction: "Siempre", access: "Permitido", parentalControl: false },
    { id: 4, device: "Gaming Console", mac: "DD:EE:FF:11:22:33", timeRestriction: "16:00-22:00", access: "Restringido", parentalControl: true }
  ]);

  const [vpnConfig, setVpnConfig] = useState({
    enabled: false,
    protocol: "OpenVPN",
    port: "1194",
    encryption: "AES-256",
    authentication: "SHA-256"
  });

  const [newRule, setNewRule] = useState({
    name: "",
    source: "",
    destination: "",
    port: "",
    protocol: "TCP",
    action: "ALLOW"
  });

  const [isAddingRule, setIsAddingRule] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleSaveFirewall = () => {
    toast.success("Configuración de firewall guardada");
  };

  const handleSaveAccessControl = () => {
    toast.success("Control de acceso guardado");
  };

  const handleSaveVPN = () => {
    toast.success("Configuración VPN guardada");
  };

  const handleAddRule = () => {
    if (newRule.name && newRule.source && newRule.destination) {
      setFirewallRules(prev => [...prev, {
        id: prev.length + 1,
        ...newRule,
        status: "Activa"
      }]);
      setNewRule({ name: "", source: "", destination: "", port: "", protocol: "TCP", action: "ALLOW" });
      setIsAddingRule(false);
      toast.success("Regla de firewall agregada");
    }
  };

  const handleDeleteRule = (id: number) => {
    setFirewallRules(prev => prev.filter(rule => rule.id !== id));
    toast.success("Regla de firewall eliminada");
  };

  const handleToggleAccess = (id: number) => {
    setAccessControl(prev => prev.map(device => 
      device.id === id 
        ? { ...device, access: device.access === "Permitido" ? "Bloqueado" : "Permitido" }
        : device
    ));
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2>Configuración de Seguridad</h2>
          <p className="text-muted-foreground">Administra firewall, control de acceso y VPN</p>
        </div>
        <div className="flex items-center gap-4">
          <Badge variant={firewallEnabled ? "default" : "secondary"} className="flex items-center gap-1">
            <Shield className="h-3 w-3" />
            Firewall {firewallEnabled ? "Activo" : "Inactivo"}
          </Badge>
        </div>
      </div>

      <Tabs defaultValue="firewall" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="firewall" className="flex items-center gap-2">
            <Shield className="h-4 w-4" />
            Firewall
          </TabsTrigger>
          <TabsTrigger value="access" className="flex items-center gap-2">
            <Lock className="h-4 w-4" />
            Control de Acceso
          </TabsTrigger>
          <TabsTrigger value="vpn" className="flex items-center gap-2">
            <Eye className="h-4 w-4" />
            VPN
          </TabsTrigger>
          <TabsTrigger value="advanced" className="flex items-center gap-2">
            <AlertTriangle className="h-4 w-4" />
            Avanzado
          </TabsTrigger>
        </TabsList>

        <TabsContent value="firewall" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Estado del Firewall</CardTitle>
                <CardDescription>Configuración general de seguridad</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Firewall Habilitado</Label>
                    <p className="text-sm text-muted-foreground">Protección de red activa</p>
                  </div>
                  <Switch
                    checked={firewallEnabled}
                    onCheckedChange={setFirewallEnabled}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Detección de Intrusiones</Label>
                    <p className="text-sm text-muted-foreground">IDS/IPS activo</p>
                  </div>
                  <Switch
                    checked={intrustionDetection}
                    onCheckedChange={setIntrusionDetection}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Protección DDoS</Label>
                    <p className="text-sm text-muted-foreground">Filtrado de ataques</p>
                  </div>
                  <Switch
                    checked={ddosProtection}
                    onCheckedChange={setDdosProtection}
                  />
                </div>

                <Button onClick={handleSaveFirewall} className="w-full">
                  <Save className="h-4 w-4 mr-2" />
                  Guardar Configuración
                </Button>
              </CardContent>
            </Card>

            <Card className="lg:col-span-2">
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Reglas de Firewall</CardTitle>
                  <CardDescription>Configura reglas de filtrado de tráfico</CardDescription>
                </div>
                <Dialog open={isAddingRule} onOpenChange={setIsAddingRule}>
                  <DialogTrigger asChild>
                    <Button className="flex items-center gap-2">
                      <Plus className="h-4 w-4" />
                      Agregar Regla
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Nueva Regla de Firewall</DialogTitle>
                      <DialogDescription>
                        Crear una nueva regla de filtrado de tráfico
                      </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="rule-name">Nombre de la Regla</Label>
                        <Input
                          id="rule-name"
                          placeholder="Mi Regla"
                          value={newRule.name}
                          onChange={(e) => setNewRule(prev => ({ ...prev, name: e.target.value }))}
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="rule-source">Origen</Label>
                          <Input
                            id="rule-source"
                            placeholder="192.168.1.0/24 o Any"
                            value={newRule.source}
                            onChange={(e) => setNewRule(prev => ({ ...prev, source: e.target.value }))}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="rule-destination">Destino</Label>
                          <Input
                            id="rule-destination"
                            placeholder="192.168.1.10 o Any"
                            value={newRule.destination}
                            onChange={(e) => setNewRule(prev => ({ ...prev, destination: e.target.value }))}
                          />
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="rule-port">Puerto</Label>
                          <Input
                            id="rule-port"
                            placeholder="80, 443, 1000-2000"
                            value={newRule.port}
                            onChange={(e) => setNewRule(prev => ({ ...prev, port: e.target.value }))}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="rule-protocol">Protocolo</Label>
                          <Select value={newRule.protocol} onValueChange={(value) => setNewRule(prev => ({ ...prev, protocol: value }))}>
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="TCP">TCP</SelectItem>
                              <SelectItem value="UDP">UDP</SelectItem>
                              <SelectItem value="ICMP">ICMP</SelectItem>
                              <SelectItem value="Any">Cualquiera</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="rule-action">Acción</Label>
                        <Select value={newRule.action} onValueChange={(value) => setNewRule(prev => ({ ...prev, action: value }))}>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="ALLOW">Permitir</SelectItem>
                            <SelectItem value="DENY">Denegar</SelectItem>
                            <SelectItem value="DROP">Descartar</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="flex justify-end gap-2">
                        <Button variant="outline" onClick={() => setIsAddingRule(false)}>
                          Cancelar
                        </Button>
                        <Button onClick={handleAddRule}>
                          Agregar Regla
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
                      <TableHead>Origen</TableHead>
                      <TableHead>Destino</TableHead>
                      <TableHead>Puerto</TableHead>
                      <TableHead>Acción</TableHead>
                      <TableHead>Estado</TableHead>
                      <TableHead>Acciones</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {firewallRules.map((rule) => (
                      <TableRow key={rule.id}>
                        <TableCell className="font-medium">{rule.name}</TableCell>
                        <TableCell className="font-mono text-sm">{rule.source}</TableCell>
                        <TableCell className="font-mono text-sm">{rule.destination}</TableCell>
                        <TableCell>{rule.port}</TableCell>
                        <TableCell>
                          <Badge variant={rule.action === "ALLOW" ? "default" : "destructive"}>
                            {rule.action}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">{rule.status}</Badge>
                        </TableCell>
                        <TableCell>
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => handleDeleteRule(rule.id)}
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="access" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Control de Acceso de Dispositivos</CardTitle>
              <CardDescription>
                Administra el acceso a Internet y restricciones de tiempo para cada dispositivo
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Dispositivo</TableHead>
                    <TableHead>Dirección MAC</TableHead>
                    <TableHead>Restricción de Tiempo</TableHead>
                    <TableHead>Estado de Acceso</TableHead>
                    <TableHead>Control Parental</TableHead>
                    <TableHead>Acciones</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {accessControl.map((device) => (
                    <TableRow key={device.id}>
                      <TableCell className="font-medium">{device.device}</TableCell>
                      <TableCell className="font-mono">{device.mac}</TableCell>
                      <TableCell>{device.timeRestriction}</TableCell>
                      <TableCell>
                        <Badge variant={device.access === "Permitido" ? "default" : "destructive"}>
                          {device.access}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Switch
                          checked={device.parentalControl}
                          onCheckedChange={(checked) => {
                            setAccessControl(prev => prev.map(d => 
                              d.id === device.id ? { ...d, parentalControl: checked } : d
                            ));
                          }}
                        />
                      </TableCell>
                      <TableCell>
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleToggleAccess(device.id)}
                        >
                          {device.access === "Permitido" ? "Bloquear" : "Permitir"}
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              <div className="flex justify-end mt-4">
                <Button onClick={handleSaveAccessControl} className="flex items-center gap-2">
                  <Save className="h-4 w-4" />
                  Guardar Control de Acceso
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="vpn" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Configuración VPN</CardTitle>
                <CardDescription>
                  Configura el servidor VPN para acceso remoto seguro
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Servidor VPN Habilitado</Label>
                    <p className="text-sm text-muted-foreground">Permitir conexiones remotas</p>
                  </div>
                  <Switch
                    checked={vpnConfig.enabled}
                    onCheckedChange={(checked) => setVpnConfig(prev => ({ ...prev, enabled: checked }))}
                  />
                </div>

                {vpnConfig.enabled && (
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="vpn-protocol">Protocolo VPN</Label>
                      <Select value={vpnConfig.protocol} onValueChange={(value) => setVpnConfig(prev => ({ ...prev, protocol: value }))}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="OpenVPN">OpenVPN</SelectItem>
                          <SelectItem value="WireGuard">WireGuard</SelectItem>
                          <SelectItem value="L2TP/IPSec">L2TP/IPSec</SelectItem>
                          <SelectItem value="PPTP">PPTP</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="vpn-port">Puerto</Label>
                        <Input
                          id="vpn-port"
                          value={vpnConfig.port}
                          onChange={(e) => setVpnConfig(prev => ({ ...prev, port: e.target.value }))}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="vpn-encryption">Cifrado</Label>
                        <Select value={vpnConfig.encryption} onValueChange={(value) => setVpnConfig(prev => ({ ...prev, encryption: value }))}>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="AES-256">AES-256</SelectItem>
                            <SelectItem value="AES-128">AES-128</SelectItem>
                            <SelectItem value="ChaCha20">ChaCha20</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="vpn-auth">Autenticación</Label>
                      <Select value={vpnConfig.authentication} onValueChange={(value) => setVpnConfig(prev => ({ ...prev, authentication: value }))}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="SHA-256">SHA-256</SelectItem>
                          <SelectItem value="SHA-1">SHA-1</SelectItem>
                          <SelectItem value="MD5">MD5</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                )}

                <Button onClick={handleSaveVPN} className="w-full">
                  <Save className="h-4 w-4 mr-2" />
                  Guardar Configuración VPN
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Usuarios VPN</CardTitle>
                <CardDescription>
                  Administra los usuarios con acceso VPN
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-4">
                  <div className="border rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">admin</p>
                        <p className="text-sm text-muted-foreground">Administrador principal</p>
                      </div>
                      <Badge variant="default">Activo</Badge>
                    </div>
                  </div>

                  <div className="border rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">john_doe</p>
                        <p className="text-sm text-muted-foreground">Usuario remoto</p>
                      </div>
                      <Badge variant="secondary">Conectado</Badge>
                    </div>
                  </div>

                  <div className="border rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">mobile_user</p>
                        <p className="text-sm text-muted-foreground">Dispositivo móvil</p>
                      </div>
                      <Badge variant="outline">Desconectado</Badge>
                    </div>
                  </div>
                </div>

                <Button className="w-full">
                  <Plus className="h-4 w-4 mr-2" />
                  Agregar Usuario VPN
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="advanced" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Configuración Avanzada</CardTitle>
                <CardDescription>
                  Opciones de seguridad adicionales
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Bloqueo Geográfico</Label>
                      <p className="text-sm text-muted-foreground">Bloquear tráfico de países específicos</p>
                    </div>
                    <Switch defaultChecked={false} />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Filtro de Contenido</Label>
                      <p className="text-sm text-muted-foreground">Bloquear sitios web maliciosos</p>
                    </div>
                    <Switch defaultChecked={true} />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Protección Anti-Phishing</Label>
                      <p className="text-sm text-muted-foreground">Detectar y bloquear ataques de phishing</p>
                    </div>
                    <Switch defaultChecked={true} />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Análisis de Malware</Label>
                      <p className="text-sm text-muted-foreground">Escanear archivos descargados</p>
                    </div>
                    <Switch defaultChecked={false} />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Registros de Seguridad</CardTitle>
                <CardDescription>
                  Eventos de seguridad recientes
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center gap-3 p-3 border rounded-lg">
                    <AlertTriangle className="h-4 w-4 text-yellow-500" />
                    <div className="flex-1">
                      <p className="text-sm font-medium">Intento de conexión bloqueado</p>
                      <p className="text-xs text-muted-foreground">IP: 203.0.113.45 - hace 2 minutos</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 p-3 border rounded-lg">
                    <Shield className="h-4 w-4 text-green-500" />
                    <div className="flex-1">
                      <p className="text-sm font-medium">Regla de firewall aplicada</p>
                      <p className="text-xs text-muted-foreground">Puerto 22 - hace 5 minutos</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 p-3 border rounded-lg">
                    <AlertTriangle className="h-4 w-4 text-red-500" />
                    <div className="flex-1">
                      <p className="text-sm font-medium">Posible ataque DDoS detectado</p>
                      <p className="text-xs text-muted-foreground">Múltiples IPs - hace 10 minutos</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 p-3 border rounded-lg">
                    <Lock className="h-4 w-4 text-blue-500" />
                    <div className="flex-1">
                      <p className="text-sm font-medium">Usuario VPN conectado</p>
                      <p className="text-xs text-muted-foreground">john_doe - hace 15 minutos</p>
                    </div>
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
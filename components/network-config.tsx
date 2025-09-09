import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Switch } from "./ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Badge } from "./ui/badge";
import { Separator } from "./ui/separator";
import { Alert, AlertDescription } from "./ui/alert";
import { Globe, Wifi, Cable, Settings, Save, RefreshCw } from "lucide-react";
import { toast } from "sonner@2.0.3";

export function NetworkConfig() {
  const [wanConfig, setWanConfig] = useState({
    type: "dhcp",
    ip: "",
    subnet: "",
    gateway: "",
    dns1: "",
    dns2: ""
  });

  const [lanConfig, setLanConfig] = useState({
    ip: "192.168.1.1",
    subnet: "255.255.255.0",
    dhcpEnabled: true,
    dhcpStart: "192.168.1.100",
    dhcpEnd: "192.168.1.200"
  });

  const [wifiConfig, setWifiConfig] = useState({
    ssid: "RouterWiFi",
    password: "",
    channel: "auto",
    bandwidth: "80",
    security: "wpa2",
    hidden: false,
    guestNetwork: false,
    guestSSID: "RouterWiFi-Guest",
    guestPassword: ""
  });

  const handleSaveWAN = () => {
    toast.success("Configuración WAN guardada correctamente");
  };

  const handleSaveLAN = () => {
    toast.success("Configuración LAN guardada correctamente");
  };

  const handleSaveWiFi = () => {
    toast.success("Configuración WiFi guardada correctamente");
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2>Configuración de Red</h2>
          <p className="text-muted-foreground">Administra las configuraciones de WAN, LAN y WiFi</p>
        </div>
        <Button variant="outline" className="flex items-center gap-2">
          <RefreshCw className="h-4 w-4" />
          Reiniciar Red
        </Button>
      </div>

      <Tabs defaultValue="wan" className="space-y-4">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="wan" className="flex items-center gap-2">
            <Globe className="h-4 w-4" />
            WAN
          </TabsTrigger>
          <TabsTrigger value="lan" className="flex items-center gap-2">
            <Cable className="h-4 w-4" />
            LAN
          </TabsTrigger>
          <TabsTrigger value="wifi" className="flex items-center gap-2">
            <Wifi className="h-4 w-4" />
            WiFi
          </TabsTrigger>
        </TabsList>

        <TabsContent value="wan" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Configuración WAN</CardTitle>
              <CardDescription>
                Configura la conexión a Internet del router
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="wan-type">Tipo de Conexión</Label>
                <Select value={wanConfig.type} onValueChange={(value) => setWanConfig(prev => ({ ...prev, type: value }))}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="dhcp">DHCP Automático</SelectItem>
                    <SelectItem value="static">IP Estática</SelectItem>
                    <SelectItem value="pppoe">PPPoE</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {wanConfig.type === "static" && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="wan-ip">Dirección IP</Label>
                    <Input
                      id="wan-ip"
                      placeholder="203.0.113.1"
                      value={wanConfig.ip}
                      onChange={(e) => setWanConfig(prev => ({ ...prev, ip: e.target.value }))}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="wan-subnet">Máscara de Subred</Label>
                    <Input
                      id="wan-subnet"
                      placeholder="255.255.255.0"
                      value={wanConfig.subnet}
                      onChange={(e) => setWanConfig(prev => ({ ...prev, subnet: e.target.value }))}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="wan-gateway">Puerta de Enlace</Label>
                    <Input
                      id="wan-gateway"
                      placeholder="203.0.113.1"
                      value={wanConfig.gateway}
                      onChange={(e) => setWanConfig(prev => ({ ...prev, gateway: e.target.value }))}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="wan-dns1">DNS Primario</Label>
                    <Input
                      id="wan-dns1"
                      placeholder="8.8.8.8"
                      value={wanConfig.dns1}
                      onChange={(e) => setWanConfig(prev => ({ ...prev, dns1: e.target.value }))}
                    />
                  </div>
                </div>
              )}

              <Alert>
                <Settings className="h-4 w-4" />
                <AlertDescription>
                  Los cambios en la configuración WAN pueden interrumpir temporalmente la conectividad a Internet.
                </AlertDescription>
              </Alert>

              <div className="flex justify-end">
                <Button onClick={handleSaveWAN} className="flex items-center gap-2">
                  <Save className="h-4 w-4" />
                  Guardar Configuración WAN
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="lan" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Configuración LAN</CardTitle>
              <CardDescription>
                Configura la red local del router
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="lan-ip">Dirección IP del Router</Label>
                  <Input
                    id="lan-ip"
                    value={lanConfig.ip}
                    onChange={(e) => setLanConfig(prev => ({ ...prev, ip: e.target.value }))}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="lan-subnet">Máscara de Subred</Label>
                  <Input
                    id="lan-subnet"
                    value={lanConfig.subnet}
                    onChange={(e) => setLanConfig(prev => ({ ...prev, subnet: e.target.value }))}
                  />
                </div>
              </div>

              <Separator />

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Servidor DHCP</Label>
                    <p className="text-sm text-muted-foreground">
                      Asigna automáticamente direcciones IP a los dispositivos
                    </p>
                  </div>
                  <Switch
                    checked={lanConfig.dhcpEnabled}
                    onCheckedChange={(checked) => setLanConfig(prev => ({ ...prev, dhcpEnabled: checked }))}
                  />
                </div>

                {lanConfig.dhcpEnabled && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="dhcp-start">IP Inicial del Pool</Label>
                      <Input
                        id="dhcp-start"
                        value={lanConfig.dhcpStart}
                        onChange={(e) => setLanConfig(prev => ({ ...prev, dhcpStart: e.target.value }))}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="dhcp-end">IP Final del Pool</Label>
                      <Input
                        id="dhcp-end"
                        value={lanConfig.dhcpEnd}
                        onChange={(e) => setLanConfig(prev => ({ ...prev, dhcpEnd: e.target.value }))}
                      />
                    </div>
                  </div>
                )}
              </div>

              <div className="flex justify-end">
                <Button onClick={handleSaveLAN} className="flex items-center gap-2">
                  <Save className="h-4 w-4" />
                  Guardar Configuración LAN
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="wifi" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Configuración WiFi</CardTitle>
              <CardDescription>
                Configura las redes inalámbricas del router
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <h4 className="font-medium">Red WiFi Principal</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="wifi-ssid">Nombre de Red (SSID)</Label>
                    <Input
                      id="wifi-ssid"
                      value={wifiConfig.ssid}
                      onChange={(e) => setWifiConfig(prev => ({ ...prev, ssid: e.target.value }))}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="wifi-password">Contraseña</Label>
                    <Input
                      id="wifi-password"
                      type="password"
                      value={wifiConfig.password}
                      onChange={(e) => setWifiConfig(prev => ({ ...prev, password: e.target.value }))}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="wifi-security">Seguridad</Label>
                    <Select value={wifiConfig.security} onValueChange={(value) => setWifiConfig(prev => ({ ...prev, security: value }))}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="wpa3">WPA3</SelectItem>
                        <SelectItem value="wpa2">WPA2</SelectItem>
                        <SelectItem value="wpa">WPA</SelectItem>
                        <SelectItem value="none">Abierta</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="wifi-channel">Canal</Label>
                    <Select value={wifiConfig.channel} onValueChange={(value) => setWifiConfig(prev => ({ ...prev, channel: value }))}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="auto">Automático</SelectItem>
                        <SelectItem value="1">Canal 1</SelectItem>
                        <SelectItem value="6">Canal 6</SelectItem>
                        <SelectItem value="11">Canal 11</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Red Oculta</Label>
                    <p className="text-sm text-muted-foreground">
                      No transmitir el nombre de la red
                    </p>
                  </div>
                  <Switch
                    checked={wifiConfig.hidden}
                    onCheckedChange={(checked) => setWifiConfig(prev => ({ ...prev, hidden: checked }))}
                  />
                </div>
              </div>

              <Separator />

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Red de Invitados</Label>
                    <p className="text-sm text-muted-foreground">
                      Crear una red separada para invitados
                    </p>
                  </div>
                  <Switch
                    checked={wifiConfig.guestNetwork}
                    onCheckedChange={(checked) => setWifiConfig(prev => ({ ...prev, guestNetwork: checked }))}
                  />
                </div>

                {wifiConfig.guestNetwork && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="guest-ssid">SSID de Invitados</Label>
                      <Input
                        id="guest-ssid"
                        value={wifiConfig.guestSSID}
                        onChange={(e) => setWifiConfig(prev => ({ ...prev, guestSSID: e.target.value }))}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="guest-password">Contraseña de Invitados</Label>
                      <Input
                        id="guest-password"
                        type="password"
                        value={wifiConfig.guestPassword}
                        onChange={(e) => setWifiConfig(prev => ({ ...prev, guestPassword: e.target.value }))}
                      />
                    </div>
                  </div>
                )}
              </div>

              <div className="flex justify-end">
                <Button onClick={handleSaveWiFi} className="flex items-center gap-2">
                  <Save className="h-4 w-4" />
                  Guardar Configuración WiFi
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
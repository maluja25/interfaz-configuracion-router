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
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "./ui/dialog";
import { 
  Terminal, 
  Play, 
  History, 
  HelpCircle, 
  Copy, 
  Save,
  Search,
  BookOpen,
  FileText
} from "lucide-react";
import { toast } from "sonner@2.0.3";

export function CommandInterface() {
  const [currentCommand, setCurrentCommand] = useState("");
  const [commandHistory, setCommandHistory] = useState([
    { id: 1, command: "show ip route", timestamp: "14:35:25", status: "success" },
    { id: 2, command: "show interfaces brief", timestamp: "14:32:10", status: "success" },
    { id: 3, command: "configure terminal", timestamp: "14:30:45", status: "success" },
    { id: 4, command: "show running-config", timestamp: "14:28:30", status: "success" }
  ]);

  const [commandOutput, setCommandOutput] = useState([
    "Router#show ip route",
    "Codes: L - local, C - connected, S - static, R - RIP, M - mobile, B - BGP",
    "       D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area",
    "       N1 - OSPF NSSA external type 1, N2 - OSPF NSSA external type 2",
    "       E1 - OSPF external type 1, E2 - OSPF external type 2",
    "",
    "Gateway of last resort is 203.0.113.1 to network 0.0.0.0",
    "",
    "S*    0.0.0.0/0 [1/0] via 203.0.113.1",
    "C     192.168.1.0/24 is directly connected, GigabitEthernet0/0/1",
    "L     192.168.1.1/32 is directly connected, GigabitEthernet0/0/1",
    "C     10.0.0.0/24 is directly connected, GigabitEthernet0/0/2",
    "L     10.0.0.1/32 is directly connected, GigabitEthernet0/0/2",
    "Router#"
  ]);

  const commonCommands = [
    {
      category: "Información del Sistema",
      commands: [
        { 
          command: "show version", 
          description: "Muestra información del hardware y software del router",
          usage: "show version",
          example: "Router#show version"
        },
        { 
          command: "show running-config", 
          description: "Muestra la configuración actual en memoria",
          usage: "show running-config",
          example: "Router#show running-config"
        },
        { 
          command: "show startup-config", 
          description: "Muestra la configuración guardada en NVRAM",
          usage: "show startup-config",
          example: "Router#show startup-config"
        }
      ]
    },
    {
      category: "Interfaces",
      commands: [
        { 
          command: "show interfaces", 
          description: "Muestra estadísticas detalladas de todas las interfaces",
          usage: "show interfaces [interface-name]",
          example: "Router#show interfaces GigabitEthernet0/0/1"
        },
        { 
          command: "show interfaces brief", 
          description: "Muestra un resumen de todas las interfaces",
          usage: "show interfaces brief",
          example: "Router#show interfaces brief"
        },
        { 
          command: "show ip interface brief", 
          description: "Muestra el estado IP de las interfaces",
          usage: "show ip interface brief",
          example: "Router#show ip interface brief"
        }
      ]
    },
    {
      category: "Enrutamiento",
      commands: [
        { 
          command: "show ip route", 
          description: "Muestra la tabla de enrutamiento IP",
          usage: "show ip route [network]",
          example: "Router#show ip route 192.168.1.0"
        },
        { 
          command: "show ip protocols", 
          description: "Muestra información de los protocolos de enrutamiento",
          usage: "show ip protocols",
          example: "Router#show ip protocols"
        },
        { 
          command: "show ip ospf database", 
          description: "Muestra la base de datos OSPF",
          usage: "show ip ospf database",
          example: "Router#show ip ospf database"
        },
        { 
          command: "show ip bgp summary", 
          description: "Muestra un resumen de las sesiones BGP",
          usage: "show ip bgp summary",
          example: "Router#show ip bgp summary"
        }
      ]
    },
    {
      category: "Configuración",
      commands: [
        { 
          command: "configure terminal", 
          description: "Entra al modo de configuración global",
          usage: "configure terminal",
          example: "Router#configure terminal\nRouter(config)#"
        },
        { 
          command: "interface [interface-name]", 
          description: "Entra al modo de configuración de interfaz",
          usage: "interface interface-name",
          example: "Router(config)#interface GigabitEthernet0/0/1\nRouter(config-if)#"
        },
        { 
          command: "copy running-config startup-config", 
          description: "Guarda la configuración actual en NVRAM",
          usage: "copy running-config startup-config",
          example: "Router#copy running-config startup-config"
        },
        { 
          command: "write memory", 
          description: "Comando alternativo para guardar configuración",
          usage: "write memory",
          example: "Router#write memory"
        }
      ]
    },
    {
      category: "Diagnóstico",
      commands: [
        { 
          command: "ping", 
          description: "Prueba de conectividad ICMP",
          usage: "ping ip-address",
          example: "Router#ping 8.8.8.8"
        },
        { 
          command: "traceroute", 
          description: "Muestra la ruta hacia un destino",
          usage: "traceroute ip-address",
          example: "Router#traceroute 8.8.8.8"
        },
        { 
          command: "show processes cpu", 
          description: "Muestra el uso de CPU por procesos",
          usage: "show processes cpu",
          example: "Router#show processes cpu"
        },
        { 
          command: "show memory", 
          description: "Muestra información de memoria del sistema",
          usage: "show memory",
          example: "Router#show memory"
        }
      ]
    }
  ];

  const [selectedCategory, setSelectedCategory] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");

  const executeCommand = () => {
    if (!currentCommand.trim()) return;

    const newHistoryItem = {
      id: commandHistory.length + 1,
      command: currentCommand,
      timestamp: new Date().toLocaleTimeString(),
      status: "success"
    };

    setCommandHistory(prev => [newHistoryItem, ...prev]);
    
    // Simulate command execution
    const simulatedOutput = [
      `Router#${currentCommand}`,
      "Command executed successfully",
      "Output would appear here...",
      "Router#"
    ];
    
    setCommandOutput(simulatedOutput);
    setCurrentCommand("");
    toast.success("Comando ejecutado correctamente");
  };

  const copyCommand = (command: string) => {
    navigator.clipboard.writeText(command);
    toast.success("Comando copiado al portapapeles");
  };

  const filteredCommands = commonCommands.filter(category => {
    if (selectedCategory !== "all" && category.category !== selectedCategory) return false;
    if (searchTerm === "") return true;
    return category.commands.some(cmd => 
      cmd.command.toLowerCase().includes(searchTerm.toLowerCase()) ||
      cmd.description.toLowerCase().includes(searchTerm.toLowerCase())
    );
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2>Interfaz de Comandos</h2>
          <p className="text-muted-foreground">Ejecuta comandos directamente en el router</p>
        </div>
      </div>

      <Tabs defaultValue="terminal" className="space-y-4">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="terminal" className="flex items-center gap-2">
            <Terminal className="h-4 w-4" />
            Terminal
          </TabsTrigger>
          <TabsTrigger value="commands" className="flex items-center gap-2">
            <BookOpen className="h-4 w-4" />
            Comandos Comunes
          </TabsTrigger>
          <TabsTrigger value="history" className="flex items-center gap-2">
            <History className="h-4 w-4" />
            Historial
          </TabsTrigger>
        </TabsList>

        <TabsContent value="terminal" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Ejecutar Comando</CardTitle>
                <CardDescription>Ingresa comandos de Cisco IOS</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="command-input">Comando</Label>
                  <div className="flex gap-2">
                    <Input
                      id="command-input"
                      placeholder="show ip route"
                      value={currentCommand}
                      onChange={(e) => setCurrentCommand(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          executeCommand();
                        }
                      }}
                      className="font-mono"
                    />
                    <Button onClick={executeCommand} className="flex items-center gap-2">
                      <Play className="h-4 w-4" />
                      Ejecutar
                    </Button>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Comandos Rápidos</Label>
                  <div className="flex flex-wrap gap-2">
                    {["show ip route", "show interfaces brief", "show running-config", "ping 8.8.8.8"].map((cmd) => (
                      <Button
                        key={cmd}
                        variant="outline"
                        size="sm"
                        onClick={() => setCurrentCommand(cmd)}
                        className="font-mono text-xs"
                      >
                        {cmd}
                      </Button>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Salida del Comando</CardTitle>
                <CardDescription>Resultado de la ejecución</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="bg-black text-green-400 p-4 rounded-lg font-mono text-sm">
                  <ScrollArea className="h-[300px]">
                    {commandOutput.map((line, index) => (
                      <div key={index} className="whitespace-pre-wrap">
                        {line}
                      </div>
                    ))}
                  </ScrollArea>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="commands" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Referencia de Comandos</CardTitle>
              <CardDescription>Comandos comunes de Cisco IOS con descripción y ejemplos</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-4">
                <div className="flex-1">
                  <Label htmlFor="search-commands">Buscar comando</Label>
                  <div className="relative">
                    <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="search-commands"
                      placeholder="Buscar comando o descripción..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-8"
                    />
                  </div>
                </div>
                <div className="min-w-[200px]">
                  <Label htmlFor="category-filter">Categoría</Label>
                  <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Todas las categorías</SelectItem>
                      {commonCommands.map((category) => (
                        <SelectItem key={category.category} value={category.category}>
                          {category.category}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <ScrollArea className="h-[500px]">
                <div className="space-y-6">
                  {filteredCommands.map((category) => (
                    <div key={category.category}>
                      <h3 className="font-medium text-lg mb-3">{category.category}</h3>
                      <div className="space-y-3">
                        {category.commands.map((cmd, index) => (
                          <Card key={index} className="border-l-4 border-l-blue-500">
                            <CardContent className="p-4 space-y-2">
                              <div className="flex items-center justify-between">
                                <h4 className="font-mono font-medium">{cmd.command}</h4>
                                <div className="flex gap-2">
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => copyCommand(cmd.command)}
                                  >
                                    <Copy className="h-3 w-3" />
                                  </Button>
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => setCurrentCommand(cmd.command)}
                                  >
                                    Usar
                                  </Button>
                                </div>
                              </div>
                              <p className="text-sm text-muted-foreground">{cmd.description}</p>
                              <div className="space-y-1">
                                <p className="text-xs font-medium">Uso:</p>
                                <code className="text-xs bg-muted p-1 rounded">{cmd.usage}</code>
                              </div>
                              <div className="space-y-1">
                                <p className="text-xs font-medium">Ejemplo:</p>
                                <code className="text-xs bg-muted p-1 rounded block">{cmd.example}</code>
                              </div>
                            </CardContent>
                          </Card>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="history" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Historial de Comandos</CardTitle>
              <CardDescription>Comandos ejecutados recientemente</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Hora</TableHead>
                    <TableHead>Comando</TableHead>
                    <TableHead>Estado</TableHead>
                    <TableHead>Acciones</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {commandHistory.map((item) => (
                    <TableRow key={item.id}>
                      <TableCell className="font-mono text-sm">{item.timestamp}</TableCell>
                      <TableCell className="font-mono">{item.command}</TableCell>
                      <TableCell>
                        <Badge variant={item.status === "success" ? "default" : "destructive"}>
                          {item.status === "success" ? "Éxito" : "Error"}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setCurrentCommand(item.command)}
                          >
                            Repetir
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => copyCommand(item.command)}
                          >
                            <Copy className="h-3 w-3" />
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

      {/* Quick Reference Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <HelpCircle className="h-5 w-5" />
            Referencia Rápida
          </CardTitle>
          <CardDescription>Comandos básicos para comenzar</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="space-y-2">
              <h4 className="font-medium">Navegación</h4>
              <div className="space-y-1 text-sm">
                <p><code>enable</code> - Modo privilegiado</p>
                <p><code>configure terminal</code> - Modo configuración</p>
                <p><code>exit</code> - Salir del modo actual</p>
                <p><code>end</code> - Volver al modo privilegiado</p>
              </div>
            </div>
            
            <div className="space-y-2">
              <h4 className="font-medium">Información</h4>
              <div className="space-y-1 text-sm">
                <p><code>show version</code> - Info del sistema</p>
                <p><code>show ip route</code> - Tabla de rutas</p>
                <p><code>show interfaces</code> - Estado interfaces</p>
                <p><code>show running-config</code> - Configuración</p>
              </div>
            </div>
            
            <div className="space-y-2">
              <h4 className="font-medium">Guardar</h4>
              <div className="space-y-1 text-sm">
                <p><code>copy run start</code> - Guardar config</p>
                <p><code>write memory</code> - Guardar (alternativo)</p>
                <p><code>show startup-config</code> - Ver config guardada</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
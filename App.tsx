import { useState } from "react";
import { Sidebar, SidebarContent, SidebarHeader, SidebarMenu, SidebarMenuItem, SidebarMenuButton, SidebarProvider, SidebarTrigger } from "./components/ui/sidebar";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { Badge } from "./components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { Button } from "./components/ui/button";
import { 
  Network, 
  Router, 
  Settings, 
  Activity, 
  FileText, 
  Globe,
  Route,
  Monitor,
  Terminal,
  CheckCircle,
  Layers
} from "lucide-react";
import { InterfaceConfig } from "./components/interface-config";
import { DHCPConfig } from "./components/dhcp-config";
import { VLANConfig } from "./components/vlan-config";
import { RoutingConfig } from "./components/routing-config";
import { VRFConfig } from "./components/vrf-config";
import { Monitoring } from "./components/monitoring";
import { CommandInterface } from "./components/command-interface";
import { Dashboard } from "./components/dashboard";

export default function App() {
  const [activeSection, setActiveSection] = useState("dashboard");

  const menuItems = [
    {
      title: "Dashboard",
      icon: Activity,
      id: "dashboard"
    },
    {
      title: "Configuración de Interfaces",
      icon: Network,
      id: "interfaces"
    },
    {
      title: "Protocolos de Enrutamiento",
      icon: Route,
      id: "routing"
    },
    {
      title: "VRF",
      icon: Layers,
      id: "vrf"
    },
    {
      title: "DHCP",
      icon: Globe,
      id: "dhcp"
    },
    {
      title: "VLAN",
      icon: Router,
      id: "vlan"
    },
    {
      title: "Monitoreo",
      icon: Monitor,
      id: "monitoring"
    },
    {
      title: "Interfaz de Comandos",
      icon: Terminal,
      id: "commands"
    }
  ];

  const renderContent = () => {
    switch (activeSection) {
      case "dashboard":
        return <Dashboard />;
      case "interfaces":
        return <InterfaceConfig />;
      case "routing":
        return <RoutingConfig />;
      case "vrf":
        return <VRFConfig />;
      case "dhcp":
        return <DHCPConfig />;
      case "vlan":
        return <VLANConfig />;
      case "monitoring":
        return <Monitoring />;
      case "commands":
        return <CommandInterface />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <SidebarProvider>
      <div className="flex h-screen w-full">
        <Sidebar className="border-r">
          <SidebarHeader className="p-4">
            <div className="flex items-center gap-2">
              <Router className="h-6 w-6" />
              <span className="font-semibold">Router Manager</span>
            </div>
          </SidebarHeader>
          <SidebarContent>
            <SidebarMenu>
              {menuItems.map((item) => (
                <SidebarMenuItem key={item.id}>
                  <SidebarMenuButton
                    onClick={() => setActiveSection(item.id)}
                    isActive={activeSection === item.id}
                    className="w-full justify-start"
                  >
                    <item.icon className="h-4 w-4" />
                    <span>{item.title}</span>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarContent>
        </Sidebar>
        
        <div className="flex-1 flex flex-col">
          <header className="border-b bg-background px-6 py-3 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <SidebarTrigger />
              <h1 className="font-semibold">
                {menuItems.find(item => item.id === activeSection)?.title || "Dashboard"}
              </h1>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="flex items-center gap-1">
                <CheckCircle className="h-3 w-3 text-green-500" />
                Conectado
              </Badge>
              <Badge variant="secondary">192.168.1.1</Badge>
            </div>
          </header>
          
          <main className="flex-1 overflow-auto p-6">
            {renderContent()}
          </main>
        </div>
      </div>
    </SidebarProvider>
  );
}
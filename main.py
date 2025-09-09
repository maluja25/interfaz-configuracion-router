#!/usr/bin/env python3
"""
Router Manager - Aplicación de gestión de routers industriales
Versión Python con tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
from modules.dashboard import DashboardFrame
from modules.interface_config import InterfaceConfigFrame
from modules.routing_config import RoutingConfigFrame
from modules.vrf_config import VRFConfigFrame
from modules.dhcp_config import DHCPConfigFrame
from modules.vlan_config import VLANConfigFrame
from modules.monitoring import MonitoringFrame
from modules.command_interface import CommandInterfaceFrame

class RouterManagerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Router Manager")
        self.root.geometry("1400x900")
        self.root.configure(bg='#ffffff')
        
        # Variables de estado
        self.current_section = tk.StringVar(value="dashboard")
        self.router_status = "Conectado"
        self.router_ip = "192.168.1.1"
        
        # Datos compartidos entre módulos
        self.shared_data = {
            'interfaces': [],
            'vrfs': [],
            'vlans': [],
            'dhcp_pools': [],
            'routing_protocols': {},
            'static_routes': [],
            'command_history': []
        }
        
        # Configurar estilos
        self.setup_styles()
        
        # Crear la interfaz
        self.setup_ui()
        
    def setup_styles(self):
        """Configurar estilos personalizados"""
        style = ttk.Style()
        
        # Configurar tema
        style.theme_use('clam')
        
        # Colores principales
        primary_color = "#030213"
        secondary_color = "#f3f3f5"
        accent_color = "#e9ebef"
        
        # Estilo para botones de navegación
        style.configure("Sidebar.TButton",
                       background=secondary_color,
                       foreground=primary_color,
                       borderwidth=0,
                       focuscolor="none",
                       relief="flat",
                       padding=(15, 10))
        
        style.map("Sidebar.TButton",
                 background=[('active', accent_color),
                           ('pressed', accent_color)])
        
        # Estilo para botón activo
        style.configure("SidebarActive.TButton",
                       background=primary_color,
                       foreground="white",
                       borderwidth=0,
                       focuscolor="none",
                       relief="flat",
                       padding=(15, 10))
        
        # Estilo para frames principales
        style.configure("Card.TFrame",
                       background="white",
                       relief="solid",
                       borderwidth=1)
        
        # Estilo para interruptor (toggle switch)
        style.configure("Switch.TCheckbutton",
                       indicatorforeground="white",
                       indicatormargin=-10,
                       indicatordiameter=20,
                       fieldbackground="lightgray",
                       padding=5)
        style.map("Switch.TCheckbutton",
                  fieldbackground=[("selected", primary_color), ("!selected", "lightgray")],
                  indicatorforeground=[("selected", "white"), ("!selected", "white")])
        
    def setup_ui(self):
        """Configurar la interfaz principal"""
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#ffffff')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear sidebar
        self.create_sidebar(main_frame)
        
        # Crear área de contenido
        self.create_content_area(main_frame)
        
    def create_sidebar(self, parent):
        """Crear la barra lateral de navegación"""
        # Frame del sidebar
        sidebar_frame = tk.Frame(parent, bg='#f8f9fa', width=250)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        sidebar_frame.pack_propagate(False)
        
        # Header del sidebar
        header_frame = tk.Frame(sidebar_frame, bg='#f8f9fa')
        header_frame.pack(fill=tk.X, padx=15, pady=20)
        
        title_label = tk.Label(header_frame, 
                              text="🔧 Router Manager",
                              font=("Arial", 16, "bold"),
                              bg='#f8f9fa',
                              fg='#030213')
        title_label.pack(anchor=tk.W)
        
        # Elementos del menú
        menu_items = [
            ("📊", "Dashboard", "dashboard"),
            ("🌐", "Configuración de Interfaces", "interfaces"),
            ("🔀", "Protocolos de Enrutamiento", "routing"),
            ("📚", "VRF", "vrf"),
            ("🏠", "DHCP", "dhcp"),
            ("🏷️", "VLAN", "vlan"),
            ("📈", "Monitoreo", "monitoring"),
            ("💻", "Interfaz de Comandos", "commands")
        ]
        
        self.nav_buttons = {}
        
        for icon, title, section_id in menu_items:
            btn_frame = tk.Frame(sidebar_frame, bg='#f8f9fa')
            btn_frame.pack(fill=tk.X, padx=10, pady=2)
            
            button = tk.Button(btn_frame,
                              text=f"{icon} {title}",
                              command=lambda s=section_id: self.change_section(s),
                              bg='#f8f9fa',
                              fg='#030213',
                              font=("Arial", 10),
                              relief=tk.FLAT,
                              anchor=tk.W,
                              padx=15,
                              pady=10,
                              cursor="hand2")
            button.pack(fill=tk.X)
            
            self.nav_buttons[section_id] = button
            
        # Actualizar botón activo inicial
        self.update_active_button("dashboard")
        
    def create_content_area(self, parent):
        """Crear el área de contenido principal"""
        # Frame del contenido
        content_frame = tk.Frame(parent, bg='#ffffff')
        content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Header superior
        self.create_header(content_frame)
        
        # Área principal de contenido
        self.content_container = tk.Frame(content_frame, bg='#ffffff')
        self.content_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Inicializar frames de contenido
        self.init_content_frames()
        
        # Mostrar frame inicial
        self.show_section("dashboard")
        
    def create_header(self, parent):
        """Crear el header superior"""
        header_frame = tk.Frame(parent, bg='#ffffff', height=60)
        header_frame.pack(fill=tk.X, padx=20, pady=(10, 0))
        header_frame.pack_propagate(False)
        
        # Título de la sección actual
        self.section_title = tk.Label(header_frame,
                                     text="Dashboard",
                                     font=("Arial", 18, "bold"),
                                     bg='#ffffff',
                                     fg='#030213')
        self.section_title.pack(side=tk.LEFT, pady=15)
        
        # Estado de conexión
        status_frame = tk.Frame(header_frame, bg='#ffffff')
        status_frame.pack(side=tk.RIGHT, pady=15)
        
        # Badge de estado
        status_badge = tk.Label(status_frame,
                               text=f"✅ {self.router_status}",
                               font=("Arial", 10),
                               bg='#e8f5e8',
                               fg='#2d5016',
                               padx=10,
                               pady=5)
        status_badge.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Badge de IP
        ip_badge = tk.Label(status_frame,
                           text=self.router_ip,
                           font=("Arial", 10),
                           bg='#f3f3f5',
                           fg='#030213',
                           padx=10,
                           pady=5)
        ip_badge.pack(side=tk.RIGHT)
        
    def init_content_frames(self):
        """Inicializar todos los frames de contenido"""
        self.content_frames = {}
        
        # Dashboard
        self.content_frames["dashboard"] = DashboardFrame(self.content_container, self.shared_data)
        
        # Configuración de Interfaces
        self.content_frames["interfaces"] = InterfaceConfigFrame(self.content_container, self.shared_data)
        
        # Protocolos de Enrutamiento
        self.content_frames["routing"] = RoutingConfigFrame(self.content_container, self.shared_data)
        
        # VRF
        self.content_frames["vrf"] = VRFConfigFrame(self.content_container, self.shared_data)
        
        # DHCP
        self.content_frames["dhcp"] = DHCPConfigFrame(self.content_container, self.shared_data)
        
        # VLAN
        self.content_frames["vlan"] = VLANConfigFrame(self.content_container, self.shared_data)
        
        # Monitoreo
        self.content_frames["monitoring"] = MonitoringFrame(self.content_container, self.shared_data)
        
        # Interfaz de Comandos
        self.content_frames["commands"] = CommandInterfaceFrame(self.content_container, self.shared_data)
        
    def change_section(self, section_id):
        """Cambiar a una sección específica"""
        self.current_section.set(section_id)
        self.update_active_button(section_id)
        self.show_section(section_id)
        
        # Actualizar título del header
        section_titles = {
            "dashboard": "Dashboard",
            "interfaces": "Configuración de Interfaces",
            "routing": "Protocolos de Enrutamiento",
            "vrf": "VRF",
            "dhcp": "DHCP",
            "vlan": "VLAN",
            "monitoring": "Monitoreo",
            "commands": "Interfaz de Comandos"
        }
        self.section_title.config(text=section_titles.get(section_id, "Router Manager"))
        
    def update_active_button(self, active_section):
        """Actualizar el estilo del botón activo"""
        for section_id, button in self.nav_buttons.items():
            if section_id == active_section:
                button.config(bg='#030213', fg='white')
            else:
                button.config(bg='#f8f9fa', fg='#030213')
                
    def show_section(self, section_id):
        """Mostrar la sección seleccionada"""
        # Ocultar todos los frames
        for frame in self.content_frames.values():
            frame.pack_forget()
            
        # Mostrar el frame seleccionado
        if section_id in self.content_frames:
            self.content_frames[section_id].pack(fill=tk.BOTH, expand=True)
            # Refrescar el contenido del frame
            if hasattr(self.content_frames[section_id], 'refresh'):
                self.content_frames[section_id].refresh()
                
    def run(self):
        """Ejecutar la aplicación"""
        # Centrar ventana
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (900 // 2)
        self.root.geometry(f"1400x900+{x}+{y}")
        
        # Configurar el cierre de la aplicación
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Iniciar loop principal
        self.root.mainloop()
        
    def on_closing(self):
        """Manejar el cierre de la aplicación"""
        if messagebox.askokcancel("Salir", "¿Deseas cerrar Router Manager?"):
            self.root.destroy()

if __name__ == "__main__":
    app = RouterManagerApp()
    app.run()
#!/usr/bin/env python3
"""
Router Manager - Aplicación de gestión de routers industriales

Esta aplicación proporciona una interfaz gráfica para la configuración y
monitoreo de routers industriales, permitiendo gestionar interfaces,
protocolos de enrutamiento, VRFs y más.

Autor: Universidad
Versión: 1.0.0
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple

# Importaciones de módulos de la aplicación
from modules.auth_dialog import AuthDialog
from modules.dashboard import DashboardFrame
from modules.interface_config import InterfaceConfigFrame
from modules.routing_config import RoutingConfigFrame
from modules.monitoring import MonitoringFrame
from modules.command_interface import CommandInterfaceFrame

# Constantes de la aplicación
APP_TITLE = "Router Manager"
APP_WIDTH = 1400
APP_HEIGHT = 900

# Colores de la aplicación
COLOR_PRIMARY = "#030213"
COLOR_SECONDARY = "#f3f3f5"
COLOR_ACCENT = "#e9ebef"
COLOR_WHITE = "#ffffff"
COLOR_SIDEBAR_BG = "#f8f9fa"

class RouterManagerApp:
    """Clase principal de la aplicación Router Manager.
    
    Esta clase gestiona la interfaz gráfica principal y coordina
    la interacción entre los diferentes módulos de la aplicación.
    """
    
    def __init__(self, connection_data: Optional[Dict[str, Any]] = None):
        """Inicializa la aplicación Router Manager.
        
        Args:
            connection_data: Datos de conexión al router (opcional)
        """
        # Configuración de la ventana principal
        self.root = tk.Tk()
        self.root.title(APP_TITLE)
        self.root.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.root.configure(bg=COLOR_WHITE)
        
        # Variables de estado
        self.current_section = tk.StringVar(value="dashboard")
        self.connection_data = connection_data or {}
        self.router_status = "Conectado" if connection_data else "Desconectado"
        self.router_ip = connection_data.get('hostname', '192.168.1.1') if connection_data else "No configurado"
        
        # Diccionarios para almacenar referencias a widgets
        self.nav_buttons: Dict[str, tk.Button] = {}
        self.content_frames: Dict[str, tk.Frame] = {}
        
        # Datos compartidos entre módulos
        self.shared_data = {
            'interfaces': [],
            'vrfs': [],
            'routing_protocols': {
                'ospf': {
                    'enabled': False, 
                    'process_id': '1',
                    'networks': [],
                    'config': ''
                },
                'eigrp': {
                    'enabled': False, 
                    'as_number': '100',
                    'networks': [],
                    'config': ''
                },
                'bgp': {
                    'enabled': False, 
                    'as_number': '65000',
                    'neighbors': [],
                    'config': ''
                },
                'rip': {
                    'enabled': False, 
                    'version': '2',
                    'networks': [],
                    'config': ''
                }
            },
            'static_routes': [],
            'command_history': [],
            'analysis_data': {},
            'parsed_data': {}
        }
        
        # Cargar datos del análisis si están disponibles
        if connection_data:
            # Cargar análisis crudo para la sección "Información del Análisis"
            if 'analysis_data' in connection_data:
                self.shared_data['analysis_data'] = connection_data.get('analysis_data', {})
            # Cargar datos parseados y propagar claves usadas por módulos
            if 'parsed_data' in connection_data:
                self.shared_data['parsed_data'] = connection_data['parsed_data']
                self.shared_data['interfaces'] = connection_data['parsed_data'].get('interfaces', [])
                self.shared_data['vrfs'] = connection_data['parsed_data'].get('vrfs', [])
                self.shared_data['routing_protocols'] = connection_data['parsed_data'].get('routing_protocols', self.shared_data['routing_protocols'])
                self.shared_data['static_routes'] = connection_data['parsed_data'].get('static_routes', [])
        
        # Configurar estilos
        self.setup_styles()
        
        # Crear la interfaz
        self.setup_ui()
        
    def setup_styles(self) -> None:
        """Configura los estilos personalizados para la aplicación.
        
        Define los estilos para botones, frames y otros widgets utilizando
        el tema 'clam' como base y aplicando los colores de la aplicación.
        """
        style = ttk.Style()
        
        # Configurar tema base
        style.theme_use('clam')
        
        # Estilo para botones de navegación
        style.configure("Sidebar.TButton",
                       background=COLOR_SECONDARY,
                       foreground=COLOR_PRIMARY,
                       borderwidth=0,
                       focuscolor="none",
                       relief="flat",
                       padding=(15, 10))
        
        style.map("Sidebar.TButton",
                 background=[('active', COLOR_ACCENT),
                           ('pressed', COLOR_ACCENT)])
        
        # Estilo para botón activo en la barra lateral
        style.configure("SidebarActive.TButton",
                       background=COLOR_PRIMARY,
                       foreground=COLOR_WHITE,
                       borderwidth=0,
                       focuscolor="none",
                       relief="flat",
                       padding=(15, 10))
        
        # Estilo para frames de tipo tarjeta
        style.configure("Card.TFrame",
                       background=COLOR_WHITE,
                       relief="solid",
                       borderwidth=1)
        
        # Estilo para interruptores (toggle switches)
        style.configure("Switch.TCheckbutton",
                       indicatorforeground=COLOR_WHITE,
                       indicatormargin=-10,
                       indicatordiameter=20,
                       fieldbackground="lightgray",
                       padding=5)
        
        style.map("Switch.TCheckbutton",
                  fieldbackground=[("selected", COLOR_PRIMARY), ("!selected", "lightgray")],
                  indicatorforeground=[("selected", COLOR_WHITE), ("!selected", COLOR_WHITE)])
                  
        # Estilo para botón primario (acción principal)
        style.configure("Primary.TButton",
                       background=COLOR_PRIMARY,
                       foreground=COLOR_WHITE,
                       borderwidth=1,
                       focuscolor=COLOR_PRIMARY,
                       relief="solid",
                       padding=(10, 5))
                       
        style.map("Primary.TButton",
                 background=[('active', '#1976d2'), ('pressed', '#0d47a1')],
                 foreground=[('active', COLOR_WHITE), ('pressed', COLOR_WHITE)])
        
        # Estilo para botón secundario (acción secundaria)
        style.configure("Secondary.TButton",
                       background="#f5f5f5",
                       foreground="#333333",
                       borderwidth=1,
                       focuscolor="#e0e0e0",
                       relief="solid",
                       padding=(10, 5))
                       
        style.map("Secondary.TButton",
                 background=[('active', '#e0e0e0'), ('pressed', '#bdbdbd')],
                 foreground=[('active', '#333333'), ('pressed', '#333333')])
        
    def setup_ui(self) -> None:
        """Configura la interfaz principal de la aplicación.
        
        Crea el frame principal, la barra lateral y el área de contenido.
        """
        # Frame principal
        main_frame = tk.Frame(self.root, bg=COLOR_WHITE)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear sidebar
        self.create_sidebar(main_frame)
        
        # Crear área de contenido
        self.create_content_area(main_frame)
        
    def create_sidebar(self, parent: tk.Frame) -> None:
        """Crea la barra lateral de navegación.
        
        Configura el panel lateral con el título de la aplicación y
        los botones de navegación para las diferentes secciones.
        
        Args:
            parent: Frame padre donde se colocará la barra lateral
        """
        # Definir ancho de la barra lateral
        SIDEBAR_WIDTH = 250
        
        # Frame del sidebar
        sidebar_frame = tk.Frame(parent, bg=COLOR_SIDEBAR_BG, width=SIDEBAR_WIDTH)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        sidebar_frame.pack_propagate(False)  # Mantener ancho fijo
        
        # Header del sidebar
        header_frame = tk.Frame(sidebar_frame, bg=COLOR_SIDEBAR_BG)
        header_frame.pack(fill=tk.X, padx=15, pady=20)
        
        # Título de la aplicación
        title_label = tk.Label(
            header_frame, 
            text="🔧 Router Manager",
            font=("Arial", 16, "bold"),
            bg=COLOR_SIDEBAR_BG,
            fg=COLOR_PRIMARY
        )
        title_label.pack(anchor=tk.W)
        
        # Definir elementos del menú
        menu_items: List[Tuple[str, str, str]] = [
            ("📊", "Dashboard", "dashboard"),
            ("🌐", "Configuración de Interfaces", "interfaces"),
            ("🔀", "Protocolos de Enrutamiento", "routing"),
            ("📈", "Monitoreo", "monitoring"),
            ("💻", "Interfaz de Comandos", "commands")
        ]
        
        # Crear botones de navegación
        for icon, title, section_id in menu_items:
            btn_frame = tk.Frame(sidebar_frame, bg=COLOR_SIDEBAR_BG)
            btn_frame.pack(fill=tk.X, padx=10, pady=2)
            
            button = tk.Button(
                btn_frame,
                text=f"{icon} {title}",
                command=lambda s=section_id: self.change_section(s),
                bg=COLOR_SIDEBAR_BG,
                fg=COLOR_PRIMARY,
                font=("Arial", 10),
                relief=tk.FLAT,
                anchor=tk.W,
                padx=15,
                pady=10,
                cursor="hand2"
            )
            button.pack(fill=tk.X)
            
            # Guardar referencia al botón
            self.nav_buttons[section_id] = button
            
        # Actualizar botón activo inicial
        self.update_active_button("dashboard")
        
    def create_content_area(self, parent: tk.Frame) -> None:
        """Crea el área de contenido principal de la aplicación.
        
        Configura el frame principal de contenido, el header superior,
        y los diferentes frames para cada sección de la aplicación.
        
        Args:
            parent: Frame padre donde se colocará el área de contenido
        """
        # Frame del contenido
        content_frame = tk.Frame(parent, bg=COLOR_WHITE)
        content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Header superior
        self.create_header(content_frame)
        
        # Área principal de contenido
        self.content_container = tk.Frame(content_frame, bg=COLOR_WHITE)
        self.content_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Inicializar frames de contenido
        self.init_content_frames()
        
        # Mostrar frame inicial
        self.show_section("dashboard")
        
    def create_header(self, parent: tk.Frame) -> None:
        """Crea el header superior de la aplicación.
        
        Configura el encabezado con el título de la sección actual y
        los indicadores de estado de conexión, IP y protocolo.
        
        Args:
            parent: Frame padre donde se colocará el header
        """
        # Definir constantes para el header
        HEADER_HEIGHT = 60
        HEADER_PADDING_X = 20
        HEADER_PADDING_Y = (10, 0)
        BADGE_PADDING_X = 10
        BADGE_PADDING_Y = 5
        BADGE_FONT = ("Arial", 10)
        TITLE_FONT = ("Arial", 18, "bold")
        TITLE_PADDING_Y = 15
        
        # Colores para los badges
        STATUS_COLOR_BG = '#e8f5e8'
        STATUS_COLOR_FG = '#2d5016'
        IP_COLOR_BG = '#f3f3f5'
        PROTOCOL_COLOR_BG = '#e3f2fd'
        PROTOCOL_COLOR_FG = '#1976d2'
        
        # Frame del header
        header_frame = tk.Frame(parent, bg=COLOR_WHITE, height=HEADER_HEIGHT)
        header_frame.pack(fill=tk.X, padx=HEADER_PADDING_X, pady=HEADER_PADDING_Y)
        header_frame.pack_propagate(False)  # Mantener altura fija
        
        # Título de la sección actual
        self.section_title = tk.Label(
            header_frame,
            text="Dashboard",
            font=TITLE_FONT,
            bg=COLOR_WHITE,
            fg=COLOR_PRIMARY
        )
        self.section_title.pack(side=tk.LEFT, pady=TITLE_PADDING_Y)
        
        # Estado de conexión
        status_frame = tk.Frame(header_frame, bg=COLOR_WHITE)
        status_frame.pack(side=tk.RIGHT, pady=TITLE_PADDING_Y)
        
        # Badge de estado
        status_badge = tk.Label(
            status_frame,
            text=f"✅ {self.router_status}",
            font=BADGE_FONT,
            bg=STATUS_COLOR_BG,
            fg=STATUS_COLOR_FG,
            padx=BADGE_PADDING_X,
            pady=BADGE_PADDING_Y
        )
        status_badge.pack(side=tk.RIGHT, padx=(BADGE_PADDING_X, 0))
        
        # Badge de IP
        ip_badge = tk.Label(
            status_frame,
            text=self.router_ip,
            font=BADGE_FONT,
            bg=IP_COLOR_BG,
            fg=COLOR_PRIMARY,
            padx=BADGE_PADDING_X,
            pady=BADGE_PADDING_Y
        )
        ip_badge.pack(side=tk.RIGHT)
        
        # Badge de protocolo (si hay datos de conexión)
        if self.connection_data:
            protocol = self.connection_data.get('protocol', 'SSH2')
            protocol_badge = tk.Label(
                status_frame,
                text=f"📡 {protocol}",
                font=BADGE_FONT,
                bg=PROTOCOL_COLOR_BG,
                fg=PROTOCOL_COLOR_FG,
                padx=BADGE_PADDING_X,
                pady=BADGE_PADDING_Y
            )
            protocol_badge.pack(side=tk.RIGHT, padx=(0, BADGE_PADDING_X))
        
    def init_content_frames(self) -> None:
        """Inicializa todos los frames de contenido de la aplicación.
        
        Crea las instancias de los diferentes frames para cada sección
        de la aplicación y los almacena en el diccionario content_frames.
        """
        # Reiniciar diccionario de frames
        self.content_frames = {}
        
        # Dashboard - Panel principal con resumen
        self.content_frames["dashboard"] = DashboardFrame(
            self.content_container, 
            self.shared_data
        )
        
        # Configuración de Interfaces - Gestión de interfaces de red
        self.content_frames["interfaces"] = InterfaceConfigFrame(
            self.content_container, 
            self.shared_data
        )
        
        # Protocolos de Enrutamiento - Configuración de protocolos
        self.content_frames["routing"] = RoutingConfigFrame(
            self.content_container, 
            self.shared_data
        )
        
        # VRF eliminado
        
        # Monitoreo - Estadísticas y estado del router
        self.content_frames["monitoring"] = MonitoringFrame(
            self.content_container, 
            self.shared_data
        )
        
        # Interfaz de Comandos - Terminal para comandos directos
        self.content_frames["commands"] = CommandInterfaceFrame(
            self.content_container, 
            self.shared_data
        )
        
    def change_section(self, section_id: str) -> None:
        """Cambia a la sección específica de la aplicación.
        
        Actualiza la sección actual, el botón activo y muestra el contenido
        correspondiente a la sección seleccionada.
        
        Args:
            section_id: Identificador de la sección a mostrar
        """
        # Actualizar variable de estado
        self.current_section.set(section_id)
        
        # Actualizar botón activo y mostrar sección
        self.update_active_button(section_id)
        self.show_section(section_id)
        
        # Definir títulos de las secciones
        section_titles: Dict[str, str] = {
            "dashboard": "Dashboard",
            "interfaces": "Configuración de Interfaces",
            "routing": "Protocolos de Enrutamiento",
            "monitoring": "Monitoreo",
            "commands": "Interfaz de Comandos"
        }
        
        # Actualizar título del header
        self.section_title.config(text=section_titles.get(section_id, APP_TITLE))
        
    def update_active_button(self, active_section: str) -> None:
        """Actualiza el estilo del botón de navegación activo.
        
        Cambia el color de fondo y texto del botón seleccionado para
        destacarlo visualmente como activo.
        
        Args:
            active_section: Identificador de la sección activa
        """
        # Definir colores para botones activos e inactivos
        ACTIVE_BG = COLOR_PRIMARY
        ACTIVE_FG = COLOR_WHITE
        
        for section_id, button in self.nav_buttons.items():
            if section_id == active_section:
                button.config(bg=ACTIVE_BG, fg=ACTIVE_FG)
            else:
                button.config(bg=COLOR_SIDEBAR_BG, fg=COLOR_PRIMARY)
                
    def show_section(self, section_id: str) -> None:
        """Muestra la sección seleccionada en el área de contenido.
        
        Oculta todos los frames y muestra solo el correspondiente a la
        sección seleccionada, refrescando su contenido si es necesario.
        
        Args:
            section_id: Identificador de la sección a mostrar
        """
        # Ocultar todos los frames
        for frame in self.content_frames.values():
            frame.pack_forget()
            
        # Mostrar el frame seleccionado si existe
        if section_id in self.content_frames:
            self.content_frames[section_id].pack(fill=tk.BOTH, expand=True)
            
            # Refrescar el contenido del frame si tiene método refresh
            if hasattr(self.content_frames[section_id], 'refresh'):
                self.content_frames[section_id].refresh()
                
    def run(self) -> None:
        """Ejecuta la aplicación principal.
        
        Centra la ventana en la pantalla, configura el manejo del cierre
        de la aplicación e inicia el bucle principal de eventos.
        """
        # Centrar ventana en la pantalla
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (APP_WIDTH // 2)
        y = (self.root.winfo_screenheight() // 2) - (APP_HEIGHT // 2)
        self.root.geometry(f"{APP_WIDTH}x{APP_HEIGHT}+{x}+{y}")
        
        # Configurar el manejo del cierre de la aplicación
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Iniciar bucle principal de eventos
        self.root.mainloop()
        
    def on_closing(self) -> None:
        """Maneja el evento de cierre de la aplicación.
        
        Muestra un diálogo de confirmación antes de cerrar la aplicación.
        """
        EXIT_TITLE = "Salir"
        EXIT_MESSAGE = f"¿Deseas cerrar {APP_TITLE}?"
        
        if messagebox.askokcancel(EXIT_TITLE, EXIT_MESSAGE):
            self.root.destroy()

    def on_connection_success(self, parsed_data: Dict[str, Any]):
        """Maneja el éxito de la conexión y actualiza la UI."""
        self.shared_data['parsed_data'] = parsed_data

        # Propagar datos clave a nivel superior para que los módulos de UI los usen
        if isinstance(parsed_data, dict):
            # Interfaces
            if 'interfaces' in parsed_data:
                self.shared_data['interfaces'] = parsed_data.get('interfaces', [])
            # VRFs
            if 'vrfs' in parsed_data:
                self.shared_data['vrfs'] = parsed_data.get('vrfs', [])
            # Protocolos
            if 'routing_protocols' in parsed_data:
                self.shared_data['routing_protocols'] = parsed_data.get('routing_protocols', self.shared_data['routing_protocols'])
            # Rutas estáticas
            if 'static_routes' in parsed_data:
                self.shared_data['static_routes'] = parsed_data.get('static_routes', [])
        
        # Actualizar el dashboard
        if "dashboard" in self.content_frames:
            dashboard_frame = self.content_frames["dashboard"]
            if hasattr(dashboard_frame, 'update_dashboard_data'):
                dashboard_frame.update_dashboard_data()

def main() -> None:
    """Función principal de la aplicación Router Manager.
    
    Muestra el diálogo de autenticación para conectarse al router,
    procesa los datos de conexión y lanza la aplicación principal.
    Si el usuario cancela la conexión, la aplicación termina.
    """
    # Mostrar diálogo de autenticación
    auth_dialog = AuthDialog()
    connection_data = auth_dialog.show()
    
    # Si se canceló la conexión, salir
    if connection_data is None:
        print("Conexión cancelada por el usuario")
        return
    
    # Iniciar aplicación principal
    app = RouterManagerApp(connection_data)

    # Reutilizar el análisis ya realizado en el diálogo de autenticación.
    # Evita ejecutar un segundo análisis.
    try:
        target = connection_data.get('hostname') or connection_data.get('port')
        messagebox.showinfo("Conexión exitosa", f"Conectado a {target} via {connection_data.get('protocol')}")
    except:
        pass

    # Si el análisis ya está disponible, actualizar la UI con esos datos.
    if 'parsed_data' in connection_data:
        app.on_connection_success(connection_data['parsed_data'])
    else:
        # Fallback: solo si por alguna razón no se obtuvo análisis, ejecutar uno.
        try:
            from modules.router_analyzer import RouterAnalyzer
            analyzer = RouterAnalyzer(connection_data)
            if analyzer.connect():
                analysis_data = analyzer.analyze_router()
                parsed_data = analyzer.parse_analysis_data(analysis_data)
                # Guardar en connection_data por consistencia
                connection_data['analysis_data'] = analysis_data
                connection_data['parsed_data'] = parsed_data
                app.on_connection_success(parsed_data)
            else:
                messagebox.showerror("Error de Conexión", "No se pudo conectar al router.")
        except Exception as e:
            messagebox.showerror("Error de Análisis", f"No se pudo analizar el router: {e}")

    # Iniciar la aplicación
    app.run()

if __name__ == "__main__":
    main()
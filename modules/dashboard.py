import tkinter as tk
from tkinter import ttk
from datetime import datetime

class DashboardFrame(tk.Frame):
    def __init__(self, parent, shared_data):
        super().__init__(parent, bg='#ffffff')
        self.shared_data = shared_data
        
        # Datos del dispositivo (se actualizarán desde shared_data)
        self.device_info = {}
        
        # Estadísticas de red (se actualizarán desde shared_data)
        self.network_stats = {}
        
        # Estado de interfaces (se actualizarán desde shared_data)
        self.interface_status = []
        
        self.create_widgets()
        self.update_dashboard_data()  # Cargar datos iniciales
        
    def update_dashboard_data(self):
        """Actualizar los datos del dashboard desde shared_data"""
        parsed_data = self.shared_data.get('parsed_data', {})
        
        # Actualizar información del dispositivo
        self.device_info = {
            "model": parsed_data.get('device_info', {}).get('model', 'N/A'),
            "firmware": parsed_data.get('device_info', {}).get('firmware', 'N/A'),
            "uptime": parsed_data.get('device_info', {}).get('uptime', 'N/A'),
            "serial": parsed_data.get('device_info', {}).get('serial', 'N/A')
        }
        
        # Actualizar estadísticas de red
        self.network_stats = {
            "active_connections": len(parsed_data.get('neighbors', {}).get('bgp', [])) + len(parsed_data.get('neighbors', {}).get('ospf', [])),
            "cpu_usage": parsed_data.get('cpu_usage', 'N/A'),
            "memory_usage": parsed_data.get('memory_usage', 'N/A'),
            "storage_usage": parsed_data.get('storage_usage', 'N/A')
        }
        
        # Actualizar estado de interfaces
        self.interface_status = parsed_data.get('interfaces', [])
        
        # Volver a crear los widgets para reflejar los nuevos datos
        for widget in self.winfo_children():
            widget.destroy()
        self.create_widgets()
        
    def create_widgets(self):
        """Crear los widgets del dashboard"""
        # Título principal
        title_frame = tk.Frame(self, bg='#ffffff')
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(title_frame,
                              text="Dashboard del Router",
                              font=("Arial", 20, "bold"),
                              bg='#ffffff',
                              fg='#030213')
        title_label.pack(anchor=tk.W)
        
        subtitle_label = tk.Label(title_frame,
                                 text="Resumen del estado y configuración del dispositivo",
                                 font=("Arial", 12),
                                 bg='#ffffff',
                                 fg='#666666')
        subtitle_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Frame principal con scroll
        main_canvas = tk.Canvas(self, bg='#ffffff')
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas, bg='#ffffff')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Grid de estadísticas principales
        self.create_stats_grid(scrollable_frame)
        
        # Información del dispositivo
        self.create_device_info(scrollable_frame)
        
        # Estado de interfaces
        self.create_interface_status(scrollable_frame)
        
        # Información del análisis
        self.create_analysis_info(scrollable_frame)
        
        # Configurar scroll con rueda del mouse
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def create_stats_grid(self, parent):
        """Crear grid de estadísticas principales"""
        stats_frame = tk.Frame(parent, bg='#ffffff')
        stats_frame.pack(fill=tk.X, pady=(0, 30))
        
        # Configurar grid
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        stats_frame.grid_columnconfigure(2, weight=1)
        stats_frame.grid_columnconfigure(3, weight=1)
        
        # Estadísticas
        stats = [
            ("📊 CPU", self.network_stats.get("cpu_usage", "0%"), "Uso actual del procesador"),
            ("💾 Memoria", self.network_stats.get("memory_usage", "0%"), "Memoria RAM utilizada"),
            ("💽 Almacenamiento", self.network_stats.get("storage_usage", "0%"), "Espacio usado en flash"),
            ("🌐 Conexiones", str(self.network_stats.get("active_connections", 0)), "Conexiones activas")
        ]
        
        for i, (title, value, description) in enumerate(stats):
            card = self.create_stat_card(stats_frame, title, value, description)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            
    def create_stat_card(self, parent, title, value, description):
        """Crear una tarjeta de estadística"""
        card = tk.Frame(parent, bg='white', relief=tk.SOLID, borderwidth=1)
        
        # Título
        title_label = tk.Label(card,
                              text=title,
                              font=("Arial", 12, "bold"),
                              bg='white',
                              fg='#030213')
        title_label.pack(pady=(15, 5))
        
        # Valor
        value_label = tk.Label(card,
                              text=value,
                              font=("Arial", 24, "bold"),
                              bg='white',
                              fg='#0066cc')
        value_label.pack()
        
        # Descripción
        desc_label = tk.Label(card,
                             text=description,
                             font=("Arial", 10),
                             bg='white',
                             fg='#666666')
        desc_label.pack(pady=(5, 15))
        
        return card
        
    def create_device_info(self, parent):
        """Crear sección de información del dispositivo"""
        device_frame = tk.Frame(parent, bg='#ffffff')
        device_frame.pack(fill=tk.X, pady=(0, 30))
        
        # Configurar grid para dos columnas
        device_frame.grid_columnconfigure(0, weight=1)
        device_frame.grid_columnconfigure(1, weight=1)
        
        # Información básica
        info_card = tk.Frame(device_frame, bg='white', relief=tk.SOLID, borderwidth=1)
        info_card.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        
        info_title = tk.Label(info_card,
                             text="🔧 Información del Dispositivo",
                             font=("Arial", 14, "bold"),
                             bg='white',
                             fg='#030213')
        info_title.pack(pady=(15, 10))
        
        info_items = [
            ("Modelo:", self.device_info.get("model", "N/A")),
            ("Firmware:", self.device_info.get("firmware", "N/A")),
            ("Tiempo activo:", self.device_info.get("uptime", "N/A")),
            ("Número de serie:", self.device_info.get("serial", "N/A"))
        ]
        
        for label, value in info_items:
            item_frame = tk.Frame(info_card, bg='white')
            item_frame.pack(fill=tk.X, padx=20, pady=2)
            
            tk.Label(item_frame, text=label, font=("Arial", 10, "bold"),
                    bg='white', fg='#030213').pack(side=tk.LEFT)
            tk.Label(item_frame, text=value, font=("Arial", 10),
                    bg='white', fg='#666666').pack(side=tk.RIGHT)
        
        # Especificaciones técnicas
        specs_card = tk.Frame(device_frame, bg='white', relief=tk.SOLID, borderwidth=1)
        specs_card.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        
        specs_title = tk.Label(specs_card,
                              text="⚙️ Especificaciones Técnicas",
                              font=("Arial", 14, "bold"),
                              bg='white',
                              fg='#030213')
        specs_title.pack(pady=(15, 10))
        
        # Obtener parsed_data de shared_data
        parsed_data = self.shared_data.get('parsed_data', {})
        device_info = parsed_data.get('device_info', {})
        
        specs_items = [
            ("Arquitectura:", device_info.get('architecture', 'N/A')),
            ("Memoria RAM:", device_info.get('ram_memory', 'N/A')),
            ("Memoria Flash:", device_info.get('flash_memory', 'N/A')),
            ("Puertos Ethernet:", device_info.get('ethernet_ports', 'N/A')),
            ("Ranuras WIC:", device_info.get('wic_slots', 'N/A')),
            ("Protocolo:", device_info.get('protocols', 'N/A'))
        ]
        
        for label, value in specs_items:
            item_frame = tk.Frame(specs_card, bg='white')
            item_frame.pack(fill=tk.X, padx=20, pady=2)
            
            tk.Label(item_frame, text=label, font=("Arial", 10, "bold"),
                    bg='white', fg='#030213').pack(side=tk.LEFT)
            tk.Label(item_frame, text=value, font=("Arial", 10),
                    bg='white', fg='#666666').pack(side=tk.RIGHT)
        
        # Espaciado final
        tk.Frame(info_card, height=15, bg='white').pack()
        tk.Frame(specs_card, height=15, bg='white').pack()
        
    def create_interface_status(self, parent):
        """Crear tabla de estado de interfaces"""
        interface_frame = tk.Frame(parent, bg='#ffffff')
        interface_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = tk.Label(interface_frame,
                              text="🌐 Estado de Interfaces",
                              font=("Arial", 16, "bold"),
                              bg='#ffffff',
                              fg='#030213')
        title_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Frame para la tabla
        table_frame = tk.Frame(interface_frame, bg='white', relief=tk.SOLID, borderwidth=1)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear Treeview para la tabla
        columns = ('Interfaz', 'IP', 'Estado', 'Protocolo', 'Método')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=8)
        
        # Configurar columnas
        tree.heading('Interfaz', text='Interfaz')
        tree.heading('IP', text='Dirección IP')
        tree.heading('Estado', text='Estado')
        tree.heading('Protocolo', text='Protocolo')
        tree.heading('Método', text='Método')
        
        tree.column('Interfaz', width=200)
        tree.column('IP', width=150)
        tree.column('Estado', width=100)
        tree.column('Protocolo', width=100)
        tree.column('Método', width=100)
        
        # Insertar datos de las interfaces
        for interface in self.interface_status:
            tree.insert('', tk.END, values=(
                interface.get('name', 'N/A'),
                interface.get('ip_address', 'N/A'),
                interface.get('status', 'N/A'),
                interface.get('protocol', 'N/A'),
                interface.get('method', 'N/A')
            ))
        
        # Scrollbar para la tabla
        table_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=table_scrollbar.set)
        
        # Empaquetar tabla y scrollbar
        tree.pack(side='left', fill='both', expand=True)
        table_scrollbar.pack(side='right', fill='y')
    
    def create_analysis_info(self, parent):
        """Crear sección de información del análisis"""
        analysis_frame = tk.Frame(parent, bg='#ffffff')
        analysis_frame.pack(fill=tk.X, pady=(30, 0))
        
        # Título
        title_label = tk.Label(analysis_frame,
                              text="📊 Información del Análisis",
                              font=("Arial", 16, "bold"),
                              bg='#ffffff',
                              fg='#030213')
        title_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Frame para mostrar información del análisis
        info_frame = tk.Frame(analysis_frame, bg='white', relief=tk.SOLID, borderwidth=1)
        info_frame.pack(fill=tk.X)
        
        # Obtener datos del análisis
        analysis_data = self.shared_data.get('analysis_data', {})
        parsed_data = self.shared_data.get('parsed_data', {})
        
        if analysis_data:
            # Mostrar información del análisis
            info_text = f"Análisis realizado: {analysis_data.get('timestamp', 'N/A')}\n"
            info_text += f"Hostname: {analysis_data.get('hostname', 'N/A')}\n"
            info_text += f"Protocolo: {analysis_data.get('protocol', 'N/A')}\n"
            info_text += f"Comandos ejecutados: {len(analysis_data.get('commands_executed', []))}\n\n"
            
            # Información de VRF
            vrfs = parsed_data.get('vrfs', [])
            if vrfs:
                info_text += f"VRFs encontradas: {len(vrfs)}\n"
                for vrf in vrfs[:3]:  # Mostrar solo los primeros 3
                    info_text += f"  - {vrf.get('name', 'N/A')}\n"
            
            # Información de VLANs
            vlans = parsed_data.get('vlans', [])
            if vlans:
                info_text += f"\nVLANs encontradas: {len(vlans)}\n"
                for vlan in vlans[:3]:  # Mostrar solo las primeras 3
                    info_text += f"  - VLAN {vlan.get('id', 'N/A')}: {vlan.get('name', 'N/A')}\n"
            
            # Información de protocolos
            neighbors = parsed_data.get('neighbors', {})
            if neighbors.get('ospf'):
                info_text += f"\nVecinos OSPF: {len(neighbors['ospf'])}\n"
            if neighbors.get('bgp'):
                info_text += f"Vecinos BGP: {len(neighbors['bgp'])}\n"
            
            # Rutas estáticas
            static_routes = parsed_data.get('static_routes', [])
            if static_routes:
                info_text += f"\nRutas estáticas: {len(static_routes)}\n"
                for route in static_routes[:3]:  # Mostrar solo las primeras 3
                    info_text += f"  - {route.get('network', 'N/A')} via {route.get('via', 'N/A')}\n"
        else:
            info_text = "No hay datos de análisis disponibles.\nConecta al router para realizar un análisis automático."
        
        # Crear widget de texto para mostrar la información
        text_widget = tk.Text(info_frame, height=12, wrap=tk.WORD, font=("Courier", 9),
                             bg='#f8f9fa', fg='#030213', relief=tk.FLAT, padx=15, pady=15)
        text_widget.insert(tk.END, info_text)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
    def refresh(self):
        """Refrescar los datos del dashboard"""
        # Aquí se pueden actualizar los datos desde el dispositivo real
        pass
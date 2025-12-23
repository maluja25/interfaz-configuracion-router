import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
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
                              text="Información del Router",
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
        
        # Contenedor principal SIN scroll: todo el contenido se organiza y ajusta
        content_frame = tk.Frame(self, bg='#ffffff')
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Grid de estadísticas principales deshabilitado

        # Información del dispositivo
        self.create_device_info(content_frame)

        # Estado de interfaces removido: esta funcionalidad está en el módulo de Configuración de Interfaces

        # Configuración del router
        self.create_running_config_section(content_frame)
        
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
    
    def create_running_config_section(self, parent):
        """Crear la sección de Configuración del Router con botón para obtener y guardar."""
        cfg_frame = tk.Frame(parent, bg='#ffffff')
        # Expandir verticalmente para ocupar el espacio sobrante cuando la ventana está maximizada
        cfg_frame.pack(fill=tk.BOTH, expand=True, pady=(30, 0))

        # Cabecera con título a la izquierda y botón a la derecha
        header = tk.Frame(cfg_frame, bg='#ffffff')
        header.pack(fill=tk.X, pady=(0, 10))

        title_label = tk.Label(header,
                               text="🧾 Configuración del Router",
                               font=("Arial", 16, "bold"),
                               bg='#ffffff',
                               fg='#030213')
        title_label.pack(side=tk.LEFT)

        fetch_btn = ttk.Button(header,
                               text="Guardar configuración",
                               command=self.on_save_config)
        fetch_btn.pack(side=tk.RIGHT)

        # Contenedor para texto con borde
        text_container = tk.Frame(cfg_frame, bg='white', relief=tk.SOLID, borderwidth=1)
        text_container.pack(fill=tk.BOTH, expand=True)

        # Área de texto con scroll para mostrar la configuración
        self.running_config_text = ScrolledText(
            text_container,
            height=14,
            font=("Consolas", 9),
            wrap=tk.NONE,
            bg="#f8f9fa",
            fg="#030213",
            relief=tk.FLAT,
            padx=15,
            pady=15,
        )
        self.running_config_text.pack(fill=tk.BOTH, expand=True)
        # Permitir desplazamiento con la rueda SOLO dentro del área de configuración
        try:
            def _on_text_mousewheel(event):
                # Desplazar el texto sin propagar el evento al canvas
                self.running_config_text.yview_scroll(int(-1*(event.delta/120)), "units")
                return "break"
            self.running_config_text.bind("<MouseWheel>", _on_text_mousewheel)
        except Exception:
            pass

        # Mostrar configuración si ya está en shared_data
        existing_cfg = self.shared_data.get('running_config', '')
        if existing_cfg:
            self.running_config_text.insert(tk.END, existing_cfg)
        else:
            self.running_config_text.insert(tk.END, "La configuración se cargará automáticamente tras el análisis.")
        self.running_config_text.config(state=tk.DISABLED)

    def on_save_config(self):
        """Guarda la configuración ya precargada como archivo .txt."""
        try:
            conn = self.shared_data.get('connection_data', {})
            cfg_text = self.shared_data.get('running_config', '')
            if not cfg_text:
                messagebox.showwarning("Sin configuración", "La configuración aún no está disponible.")
                return
            # Mostrar y guardar
            self.running_config_text.config(state=tk.NORMAL)
            self.running_config_text.delete("1.0", tk.END)
            self.running_config_text.insert(tk.END, cfg_text)
            self.running_config_text.config(state=tk.DISABLED)
            self.save_config_to_file(cfg_text, conn)
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar la configuración: {e}")

    def save_config_to_file(self, cfg_text: str, conn: dict):
        """Pregunta ubicación y guarda la configuración en un archivo .txt."""
        hostname = conn.get('hostname') or conn.get('port') or 'router'
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        default_name = f"config_{hostname}_{ts}.txt"
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=default_name,
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Guardar configuración"
        )
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(cfg_text or "")
                messagebox.showinfo("Guardado", f"Configuración guardada en:\n{path}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo: {e}")

    def refresh(self):
        """Refrescar los datos del dashboard"""
        # Aquí se pueden actualizar los datos desde el dispositivo real
        pass
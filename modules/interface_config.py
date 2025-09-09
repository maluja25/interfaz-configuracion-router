import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class InterfaceConfigFrame(tk.Frame):
    def __init__(self, parent, shared_data):
        super().__init__(parent, bg='#ffffff')
        self.shared_data = shared_data
        
        # Inicializar datos de interfaces si no existen
        if 'interfaces' not in self.shared_data or not self.shared_data['interfaces']:
            self.shared_data['interfaces'] = [
                {
                    'id': 1,
                    'name': 'GigabitEthernet0/0/1',
                    'type': 'Ethernet',
                    'ip': '192.168.1.1',
                    'mask': '255.255.255.0',
                    'status': 'up',
                    'description': 'LAN Principal',
                    'duplex': 'full',
                    'speed': '1000'
                },
                {
                    'id': 2,
                    'name': 'GigabitEthernet0/0/2',
                    'type': 'Ethernet',
                    'ip': '10.0.0.1',
                    'mask': '255.255.255.0',
                    'status': 'up',
                    'description': 'Red Servidores',
                    'duplex': 'full',
                    'speed': '1000'
                },
                {
                    'id': 3,
                    'name': 'Serial0/1/0',
                    'type': 'Serial',
                    'ip': '203.0.113.2',
                    'mask': '255.255.255.252',
                    'status': 'up',
                    'description': 'WAN Principal',
                    'duplex': 'full',
                    'speed': '1544'
                },
                {
                    'id': 4,
                    'name': 'GigabitEthernet0/0/3',
                    'type': 'Ethernet',
                    'ip': '',
                    'mask': '',
                    'status': 'down',
                    'description': 'Sin configurar',
                    'duplex': 'auto',
                    'speed': 'auto'
                },
                {
                    'id': 5,
                    'name': 'Loopback0',
                    'type': 'Loopback',
                    'ip': '1.1.1.1',
                    'mask': '255.255.255.255',
                    'status': 'up',
                    'description': 'Router ID',
                    'duplex': 'N/A',
                    'speed': 'N/A'
                }
            ]
        
        self.create_widgets()
        
    def create_widgets(self):
        """Crear los widgets de configuración de interfaces"""
        # Título
        title_frame = tk.Frame(self, bg='#ffffff')
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(title_frame,
                              text="Configuración de Interfaces",
                              font=("Arial", 20, "bold"),
                              bg='#ffffff',
                              fg='#030213')
        title_label.pack(anchor=tk.W)
        
        subtitle_label = tk.Label(title_frame,
                                 text="Administra las interfaces de red del router",
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
        
        # Estadísticas de interfaces
        self.create_interface_stats(scrollable_frame)
        
        # Lista de interfaces
        self.create_interface_list(scrollable_frame)
        
        # Vista previa de comandos
        self.create_command_preview(scrollable_frame)
        
        # Configurar scroll
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def create_interface_stats(self, parent):
        """Crear estadísticas de interfaces"""
        stats_frame = tk.Frame(parent, bg='#ffffff')
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Calcular estadísticas
        interfaces = self.shared_data.get('interfaces', [])
        total = len(interfaces)
        active = len([i for i in interfaces if i.get('status', '').lower() == 'up'])
        inactive = len([i for i in interfaces if i.get('status', '').lower() == 'down'])
        unconfigured = len([i for i in interfaces if not i.get('ip_address', '')])
        
        # Grid de estadísticas
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        stats_frame.grid_columnconfigure(2, weight=1)
        stats_frame.grid_columnconfigure(3, weight=1)
        
        stats = [
            ("📊 Total de Interfaces", str(total), "#0066cc"),
            ("✅ Interfaces Activas", str(active), "#28a745"),
            ("❌ Interfaces Inactivas", str(inactive), "#dc3545"),
            ("⚠️ Sin Configurar", str(unconfigured), "#ffc107")
        ]
        
        for i, (title, value, color) in enumerate(stats):
            card = self.create_stat_card(stats_frame, title, value, color)
            card.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            
    def create_stat_card(self, parent, title, value, color):
        """Crear tarjeta de estadística"""
        card = tk.Frame(parent, bg='white', relief=tk.SOLID, borderwidth=1)
        
        title_label = tk.Label(card, text=title, font=("Arial", 10, "bold"),
                              bg='white', fg='#030213')
        title_label.pack(pady=(10, 5))
        
        value_label = tk.Label(card, text=value, font=("Arial", 18, "bold"),
                              bg='white', fg=color)
        value_label.pack()
        
        tk.Frame(card, height=10, bg='white').pack()
        
        return card
        
    def create_interface_list(self, parent):
        """Crear lista de interfaces"""
        list_frame = tk.Frame(parent, bg='#ffffff')
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Título y botón de agregar
        header_frame = tk.Frame(list_frame, bg='#ffffff')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(header_frame,
                              text="🌐 Lista de Interfaces",
                              font=("Arial", 16, "bold"),
                              bg='#ffffff',
                              fg='#030213')
        title_label.pack(side=tk.LEFT)
        
        # Frame para la tabla
        table_frame = tk.Frame(list_frame, bg='white', relief=tk.SOLID, borderwidth=1)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear Treeview
        columns = ('Interfaz', 'Tipo', 'IP', 'Máscara', 'Estado', 'Descripción')
        self.interface_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        
        # Configurar columnas
        for col in columns:
            self.interface_tree.heading(col, text=col)
            self.interface_tree.column(col, width=120)
        
        # Scrollbar
        tree_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.interface_tree.yview)
        self.interface_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # Botones de acción
        button_frame = tk.Frame(table_frame, bg='white')
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        edit_btn = tk.Button(button_frame, text="✏️ Editar", command=self.edit_interface,
                            bg='#007bff', fg='white', font=("Arial", 10))
        edit_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        toggle_btn = tk.Button(button_frame, text="🔄 Cambiar Estado", command=self.toggle_interface,
                              bg='#28a745', fg='white', font=("Arial", 10))
        toggle_btn.pack(side=tk.LEFT)
        
        # Empaquetar
        self.interface_tree.pack(side='left', fill='both', expand=True)
        tree_scrollbar.pack(side='right', fill='y')
        
        # Cargar datos
        self.refresh_interface_list()
        
    def refresh_interface_list(self):
        """Refrescar la lista de interfaces"""
        # Limpiar tabla
        for item in self.interface_tree.get_children():
            self.interface_tree.delete(item)
            
        # Agregar interfaces
        for interface in self.shared_data['interfaces']:
            status_text = "UP" if interface.get('status', '').lower() == 'up' else "DOWN"
            self.interface_tree.insert('', tk.END, values=(
                interface.get('name', 'N/A'),
                interface.get('type', 'Ethernet'),  # Tipo por defecto
                interface.get('ip_address', 'N/A'),
                interface.get('mask', 'N/A'),
                status_text,
                interface.get('description', 'N/A')
            ), tags=(interface.get('status', 'down'),))
        
        # Configurar tags para colores
        self.interface_tree.tag_configure('up', foreground='#28a745')
        self.interface_tree.tag_configure('down', foreground='#dc3545')
        
    def edit_interface(self):
        """Editar interfaz seleccionada"""
        selection = self.interface_tree.selection()
        if not selection:
            messagebox.showwarning("Selección", "Por favor selecciona una interfaz para editar")
            return
            
        # Obtener datos de la interfaz
        item = self.interface_tree.item(selection[0])
        interface_name = item['values'][0]
        
        # Buscar la interfaz en los datos
        interface = next((i for i in self.shared_data['interfaces'] if i.get('name') == interface_name), None)
        if interface:
            self.open_edit_dialog(interface)
            
    def open_edit_dialog(self, interface):
        """Abrir diálogo de edición"""
        dialog = tk.Toplevel(self)
        dialog.title(f"Configurar {interface.get('name', 'N/A')}")
        dialog.geometry("500x600")
        dialog.configure(bg='#ffffff')
        dialog.transient(self)
        dialog.grab_set()
        
        # Centrar ventana
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (600 // 2)
        dialog.geometry(f"500x600+{x}+{y}")
        
        # Variables para el formulario
        ip_var = tk.StringVar(value=interface.get('ip_address', ''))
        mask_var = tk.StringVar(value=interface.get('mask', ''))
        desc_var = tk.StringVar(value=interface.get('description', ''))
        status_var = tk.StringVar(value=interface.get('status', 'down'))
        duplex_var = tk.StringVar(value=interface.get('duplex', 'auto'))
        speed_var = tk.StringVar(value=interface.get('speed', 'auto'))
        
        # Título
        title_label = tk.Label(dialog, text=f"Configurar {interface.get('name', 'N/A')}",
                              font=("Arial", 16, "bold"), bg='#ffffff', fg='#030213')
        title_label.pack(pady=20)
        
        # Notebook para pestañas
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Pestaña de configuración IP
        ip_frame = tk.Frame(notebook, bg='#ffffff')
        notebook.add(ip_frame, text="Configuración IP")
        
        # Campos IP
        tk.Label(ip_frame, text="Dirección IP:", font=("Arial", 12, "bold"),
                bg='#ffffff', fg='#030213').pack(anchor=tk.W, pady=(20, 5))
        ip_entry = tk.Entry(ip_frame, textvariable=ip_var, font=("Arial", 12), width=30)
        ip_entry.pack(anchor=tk.W, pady=(0, 15))
        
        tk.Label(ip_frame, text="Máscara de Subred:", font=("Arial", 12, "bold"),
                bg='#ffffff', fg='#030213').pack(anchor=tk.W, pady=(0, 5))
        mask_entry = tk.Entry(ip_frame, textvariable=mask_var, font=("Arial", 12), width=30)
        mask_entry.pack(anchor=tk.W, pady=(0, 15))
        
        tk.Label(ip_frame, text="Descripción:", font=("Arial", 12, "bold"),
                bg='#ffffff', fg='#030213').pack(anchor=tk.W, pady=(0, 5))
        desc_entry = tk.Entry(ip_frame, textvariable=desc_var, font=("Arial", 12), width=30)
        desc_entry.pack(anchor=tk.W, pady=(0, 15))
        
        # Estado
        status_frame = tk.Frame(ip_frame, bg='#ffffff')
        status_frame.pack(anchor=tk.W, pady=(10, 0))
        
        tk.Label(status_frame, text="Estado de la Interfaz:", font=("Arial", 12, "bold"),
                bg='#ffffff', fg='#030213').pack(side=tk.LEFT)
        
        status_combo = ttk.Combobox(status_frame, textvariable=status_var, 
                                   values=['up', 'down'], state='readonly', width=10)
        status_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Pestaña física
        physical_frame = tk.Frame(notebook, bg='#ffffff')
        notebook.add(physical_frame, text="Configuración Física")
        
        tk.Label(physical_frame, text="Modo Duplex:", font=("Arial", 12, "bold"),
                bg='#ffffff', fg='#030213').pack(anchor=tk.W, pady=(20, 5))
        duplex_combo = ttk.Combobox(physical_frame, textvariable=duplex_var,
                                   values=['auto', 'full', 'half'], state='readonly', width=15)
        duplex_combo.pack(anchor=tk.W, pady=(0, 15))
        
        tk.Label(physical_frame, text="Velocidad:", font=("Arial", 12, "bold"),
                bg='#ffffff', fg='#030213').pack(anchor=tk.W, pady=(0, 5))
        speed_combo = ttk.Combobox(physical_frame, textvariable=speed_var,
                                  values=['auto', '10', '100', '1000', '10000'], state='readonly', width=15)
        speed_combo.pack(anchor=tk.W, pady=(0, 15))
        
        # Información de la interfaz
        info_frame = tk.LabelFrame(physical_frame, text="Información", bg='#ffffff', fg='#030213')
        info_frame.pack(fill=tk.X, pady=(20, 0))
        
        tk.Label(info_frame, text=f"Nombre: {interface.get('name', 'N/A')}", font=("Arial", 10),
                bg='#ffffff', fg='#666666').pack(anchor=tk.W, padx=10, pady=5)
        tk.Label(info_frame, text=f"Tipo: {interface.get('type', 'Ethernet')}", font=("Arial", 10),
                bg='#ffffff', fg='#666666').pack(anchor=tk.W, padx=10, pady=5)
        
        # Botones
        button_frame = tk.Frame(dialog, bg='#ffffff')
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        def save_changes():
            interface['ip_address'] = ip_var.get()
            interface['mask'] = mask_var.get()
            interface['description'] = desc_var.get()
            interface['status'] = status_var.get()
            interface['duplex'] = duplex_var.get()
            interface['speed'] = speed_var.get()
            
            self.refresh_interface_list()
            messagebox.showinfo("Éxito", f"Interfaz {interface.get('name', 'N/A')} configurada correctamente")
            dialog.destroy()
        
        cancel_btn = tk.Button(button_frame, text="Cancelar", command=dialog.destroy,
                              bg='#6c757d', fg='white', font=("Arial", 12), width=10)
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        save_btn = tk.Button(button_frame, text="💾 Guardar", command=save_changes,
                            bg='#28a745', fg='white', font=("Arial", 12), width=10)
        save_btn.pack(side=tk.RIGHT)
        
    def toggle_interface(self):
        """Cambiar estado de la interfaz"""
        selection = self.interface_tree.selection()
        if not selection:
            messagebox.showwarning("Selección", "Por favor selecciona una interfaz")
            return
            
        item = self.interface_tree.item(selection[0])
        interface_name = item['values'][0]
        
        interface = next((i for i in self.shared_data['interfaces'] if i.get('name') == interface_name), None)
        if interface:
            new_status = 'down' if interface.get('status', 'down') == 'up' else 'up'
            interface['status'] = new_status
            self.refresh_interface_list()
            messagebox.showinfo("Estado", f"Interfaz {interface_name} {'activada' if new_status == 'up' else 'desactivada'}")
            
    def create_command_preview(self, parent):
        """Crear vista previa de comandos"""
        preview_frame = tk.Frame(parent, bg='#ffffff')
        preview_frame.pack(fill=tk.X, pady=(20, 0))
        
        title_label = tk.Label(preview_frame,
                              text="💻 Comandos de Configuración",
                              font=("Arial", 16, "bold"),
                              bg='#ffffff',
                              fg='#030213')
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        subtitle_label = tk.Label(preview_frame,
                                 text="Vista previa de los comandos que se ejecutarán en el router",
                                 font=("Arial", 12),
                                 bg='#ffffff',
                                 fg='#666666')
        subtitle_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Terminal frame
        terminal_frame = tk.Frame(preview_frame, bg='black')
        terminal_frame.pack(fill=tk.X)
        
        # Texto del terminal
        terminal_text = tk.Text(terminal_frame, bg='black', fg='#00ff00',
                               font=("Consolas", 10), height=15, wrap=tk.WORD)
        terminal_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Generar comandos
        commands = ["# Configuración de interfaces activas"]
        for interface in self.shared_data['interfaces']:
            if interface.get('ip_address') and interface.get('status') == 'up':
                commands.extend([
                    f"interface {interface.get('name', 'N/A')}",
                    f"  ip address {interface.get('ip_address', '')} {interface.get('mask', '')}",
                    f"  description {interface.get('description', '')}",
                    "  no shutdown",
                    "  exit"
                ])
        
        terminal_text.insert(tk.END, "\n".join(commands))
        terminal_text.config(state=tk.DISABLED)
        
    def refresh(self):
        """Refrescar la vista"""
        self.refresh_interface_list()
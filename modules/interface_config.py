import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from modules.router_analyzer.interface_actions import shutdown_interface, no_shutdown_interface
import threading
from modules.router_analyzer.connections import run_telnet_command, run_ssh_command, run_serial_command, run_telnet_commands_batch
from modules.router_analyzer.vendor_commands import INTERFACES_BRIEF, INTERFACE_CONFIG_SECTION
from modules.router_analyzer.parsers import (
    parse_cisco_ip_interface_brief,
    parse_huawei_ip_interface_brief,
    parse_juniper_interfaces_terse,
)

class InterfaceConfigFrame(tk.Frame):
    def __init__(self, parent, shared_data):
        super().__init__(parent, bg='#ffffff')
        self.shared_data = shared_data
        # Configuración responsive: porcentajes por columna de la tabla
        self._column_percentages = {
            'Interfaz': 0.18,
            'IP': 0.18,
            'Máscara': 0.13,
            'VRF': 0.12,
            'Estado': 0.08,
            'Acción': 0.11,
            'Descripción': 0.13
        }
        self._state_buttons = {}
        
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
        # Título (centrado)
        title_frame = tk.Frame(self, bg='#ffffff')
        title_frame.pack(anchor='n', fill=tk.X, pady=(0, 10))

        title_label = tk.Label(title_frame,
                               text="Configuración de Interfaces",
                               font=("Arial", 20, "bold"),
                               bg='#ffffff',
                               fg='#030213')
        title_label.pack(anchor=tk.CENTER)

        subtitle_label = tk.Label(title_frame,
                                  text="Administra las interfaces de red del router",
                                  font=("Arial", 12),
                                  bg='#ffffff',
                                  fg='#666666')
        subtitle_label.pack(anchor=tk.CENTER, pady=(5, 0))

        # Frame principal con scroll y contenedor centrado
        main_canvas = tk.Canvas(self, bg='#ffffff', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas, bg='#ffffff')
        # Actualizar región de scroll cuando cambie el tamaño del contenido
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        self._canvas_window = main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        # Anclar el ancho del contenido al ancho del canvas (evita espacio vacío en pantalla completa)
        def _bind_canvas_width(event):
            try:
                main_canvas.itemconfig(self._canvas_window, width=event.width)
            except Exception:
                pass
        main_canvas.bind('<Configure>', _bind_canvas_width)
        main_canvas.configure(yscrollcommand=scrollbar.set)

        # Contenedor de contenido centrado
        content_frame = tk.Frame(scrollable_frame, bg='#ffffff')
        # Permitir que el contenido se expanda verticalmente cuando haya espacio disponible
        # y añadir margen lateral para separar la scrollbar de los rectángulos
        content_frame.pack(anchor='n', fill=tk.BOTH, expand=True, padx=12)

        # (Se elimina la sección de estadísticas para simplificar la vista)
        # self.create_interface_stats(content_frame)

        # Lista de interfaces
        self.create_interface_list(content_frame)

        # Vista previa de comandos
        self.create_command_preview(content_frame)

        # Configurar scroll: activar desplazamiento con rueda en el área general
        def _on_mousewheel(event):
            try:
                direction = -1 if event.delta > 0 else 1
                main_canvas.yview_scroll(direction, "units")
            except Exception:
                pass
            return "break"
        # Enlazar a contenedores relevantes para evitar conflictos con otros módulos
        for _w in (main_canvas, scrollable_frame, content_frame):
            try:
                _w.bind("<MouseWheel>", _on_mousewheel)
            except Exception:
                pass

        main_canvas.pack(side="left", fill="both", expand=True)
        # Mostrar la barra vertical externa para navegar en pantallas pequeñas
        scrollbar.pack(side="right", fill="y")
        
    def create_interface_stats(self, parent):
        """Crear estadísticas de interfaces"""
        stats_frame = tk.Frame(parent, bg='#ffffff')
        stats_frame.pack(anchor='n', fill=tk.X, pady=(0, 10))
        
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
            card.grid(row=0, column=i, padx=8, pady=8, sticky="ew")
            
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
        list_frame.pack(anchor='n', fill=tk.X, pady=(0, 10))
        
        # Título y botón de agregar
        header_frame = tk.Frame(list_frame, bg='#ffffff')
        header_frame.pack(anchor='n', fill=tk.X, pady=(0, 8))
        
        title_label = tk.Label(header_frame,
                              text="🌐 Lista de Interfaces",
                              font=("Arial", 16, "bold"),
                              bg='#ffffff',
                              fg='#030213')
        title_label.pack(side=tk.LEFT)
        
        # Frame para la tabla
        table_frame = tk.Frame(list_frame, bg='white')
        table_frame.pack(anchor='n', fill=tk.BOTH, expand=True, padx=12)
        
        # Estilo para el Treeview
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Treeview", 
                        rowheight=28, 
                        font=("Arial", 10), 
                        background="white", 
                        fieldbackground="white",
                        borderwidth=1,
                        relief="solid")
                        
        style.configure("Treeview.Heading", 
                        font=("Arial", 11, "bold"), 
                        background="#EAEAEA", 
                        relief="solid",
                        borderwidth=1)

        style.map('Treeview',
                  background=[('selected', '#007bff')],
                  foreground=[('selected', 'white')])

        # Crear Treeview
        columns = ('Interfaz', 'IP', 'Máscara', 'VRF', 'Estado', 'Acción', 'Descripción')
        self.interface_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        
        # Configurar columnas (responsive por porcentaje)
        for col in columns:
            self.interface_tree.heading(col, text=col)
            self.interface_tree.column(col, anchor='center', stretch=True)

        # Redimensionar columnas por porcentaje cuando cambie el tamaño del Treeview
        self._columns = columns
        def _resize_tree_columns(total_width):
            try:
                available = max(0, total_width - 20)  # espacio para bordes/scrollbar
                for col in self._columns:
                    pct = self._column_percentages.get(col, 1/len(self._columns))
                    w = max(60, int(available * pct))
                    self.interface_tree.column(col, width=w)
            except Exception:
                pass
        self.interface_tree.bind('<Configure>', lambda e: (_resize_tree_columns(e.width), self._update_state_buttons_positions()))
        
        # Scrollbar
        tree_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.interface_tree.yview)
        def _on_tree_scroll(*args):
            try:
                tree_scrollbar.set(*args)
            except Exception:
                pass
            self._update_state_buttons_positions()
        self.interface_tree.configure(yscrollcommand=_on_tree_scroll)
        
        # Botones de acción
        button_frame = tk.Frame(table_frame, bg='white')
        button_frame.pack(anchor='n', fill=tk.X, pady=8)
        
        edit_btn = tk.Button(button_frame, text="✏️ Editar", command=self.edit_interface,
                            bg='#007bff', fg='white', font=("Arial", 10))
        edit_btn.pack(side=tk.LEFT, padx=8)
        
        toggle_btn = tk.Button(button_frame, text="🔄 Cambiar Estado", command=self.toggle_interface,
                              bg='#28a745', fg='white', font=("Arial", 10))
        toggle_btn.pack(side=tk.LEFT, padx=8)
        
        # Empaquetar
        self.interface_tree.pack(side='left', fill='both', expand=True)
        tree_scrollbar.pack(side='right', fill='y')
        # Permitir desplazamiento con la rueda SOLO dentro de la tabla
        try:
            def _on_tree_mousewheel(event):
                direction = -1 if event.delta > 0 else 1
                self.interface_tree.yview_scroll(direction, "units")
                return "break"
            self.interface_tree.bind("<MouseWheel>", _on_tree_mousewheel)
        except Exception:
            pass
        
        # Cargar datos
        self.refresh_interface_list()
        self._rebuild_state_buttons()
        self._update_state_buttons_positions()
        
    def refresh_interface_list(self):
        """Refrescar la lista de interfaces"""
        # Limpiar tabla
        for item in self.interface_tree.get_children():
            self.interface_tree.delete(item)
        for _btn in list(self._state_buttons.values()):
            try:
                _btn.destroy()
            except Exception:
                pass
        self._state_buttons = {}
            
        # Agregar interfaces
        # Ordenar por estado (UP primero) y nombre
        sorted_interfaces = sorted(
            self.shared_data['interfaces'],
            key=lambda i: (
                0 if str(i.get('status', 'down')).lower() == 'up' else 1,
                str(i.get('name', ''))
            )
        )
        for interface in sorted_interfaces:
            status_text = "UP" if interface.get('status', '').lower() == 'up' else "DOWN"
            item_id = self.interface_tree.insert('', tk.END, values=(
                interface.get('name', 'N/A'),
                interface.get('ip_address') or interface.get('ip', 'N/A'),
                interface.get('mask', 'N/A'),
                interface.get('vrf', ''),
                status_text,
                "",
                interface.get('description', 'N/A')
            ), tags=(interface.get('status', 'down'),))
            try:
                self._create_state_button(item_id, interface.get('name', 'N/A'), interface.get('status', 'down'))
            except Exception:
                pass
        
        # Configurar tags para colores
        self.interface_tree.tag_configure('up', background='#d4edda', foreground='#155724')
        self.interface_tree.tag_configure('down', background='#f8d7da', foreground='#721c24')
        self.interface_tree.tag_configure('oddrow', background='#f2f2f2')
        self._update_state_buttons_positions()
        
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
        # Se elimina el campo de 'Tipo' en la configuración de interfaz
        
        # Botones
        button_frame = tk.Frame(dialog, bg='#ffffff')
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        def save_changes():
            name = interface.get('name', 'N/A')
            ip_val = ip_var.get().strip()
            mask_val = mask_var.get().strip()
            status_val = status_var.get().strip().lower() or 'up'
            try:
                conn = self.shared_data.get('connection_data', {}) or {}
                vendor = (conn.get('vendor_hint') or conn.get('vendor') or 'cisco').lower()
                conn_fast = dict(conn)
                conn_fast['fast_mode'] = True
                conn_fast['send_script'] = True
                conn_fast['verbose'] = True
                cmds_preview = []
                resp = []
                if vendor == 'cisco':
                    status_cmd = "shutdown" if status_val == "down" else "no shutdown"
                    cmds_preview = [
                        "configure terminal",
                        f"interface {name}",
                        f"ip address {ip_val} {mask_val}",
                        status_cmd,
                        "end",
                        "write memory",
                    ]
                    from modules.router_analyzer.interface_actions import set_interface_ip
                    resp = set_interface_ip(conn_fast, vendor, name, ip_val, mask_val, status_val)  # type: ignore
                elif vendor == 'huawei':
                    status_cmd = "shutdown" if status_val == "down" else "undo shutdown"
                    cmds_preview = [
                        f"interface {name}",
                        f"ip address {ip_val} {mask_val}",
                        status_cmd,
                        "quit",
                    ]
                    from modules.router_analyzer.interface_actions import set_interface_ip
                    resp = set_interface_ip(conn_fast, vendor, name, ip_val, mask_val, status_val)  # type: ignore
                elif vendor == 'juniper':
                    status_cmd = f"set interfaces {name} disable" if status_val == "down" else ""
                    cmds_preview = [
                        "configure",
                        f"set interfaces {name} unit 0 family inet address {ip_val}/{mask_val}",
                    ]
                    if status_cmd:
                        cmds_preview.append(status_cmd)
                    cmds_preview.extend(["commit", "exit"])
                    from modules.router_analyzer.interface_actions import set_interface_ip
                    resp = set_interface_ip(conn_fast, vendor, name, ip_val, mask_val, status_val)  # type: ignore
                try:
                    out_text = "\n".join(resp or [])
                    lines = [ln for ln in out_text.splitlines() if ln.strip()]
                    errors = []
                    ospf_alerts = []
                    for ln in lines:
                        l = ln.lower()
                        if ("bad mask" in l) or ("invalid input detected" in l) or ("conflicts with" in l) or ("overlaps" in l):
                            errors.append(ln)
                        if ("%ospf-" in l) or (("ospf" in l) and (("adj" in l) or ("neighbor" in l))):
                            ospf_alerts.append(ln)
                    if errors:
                        messagebox.showerror("Error de configuración", "\n".join(errors))
                        return
                    if ospf_alerts:
                        try:
                            messagebox.showwarning("Aviso OSPF", "\n".join(ospf_alerts))
                        except Exception:
                            pass
                except Exception:
                    pass
                try:
                    self._refresh_interfaces_only()
                except Exception:
                    pass
                try:
                    if hasattr(self, "terminal_text") and self.terminal_text.winfo_exists():
                        hostn = "CISCO" if vendor == "cisco" else "ROUTER"
                        conv_lines = []
                        if vendor == "cisco":
                            conv_lines = [
                                f"{hostn}#configure terminal",
                                "Enter configuration commands, one per line.  End with CNTL/Z.",
                                f"{hostn}(config)#",
                                f"{hostn}(config)#interface {name}",
                                f"{hostn}(config-if)#",
                                f"{hostn}(config-if)#ip address {ip_val} {mask_val}",
                                f"{hostn}(config-if)#" + status_cmd,
                                f"{hostn}(config-if)#end",
                                f"{hostn}#",
                                f"{hostn}#write memory",
                            ]
                        else:
                            conv_lines = cmds_preview
                        self.terminal_text.config(state=tk.NORMAL)
                        self.terminal_text.delete("1.0", tk.END)
                        self.terminal_text.insert(tk.END, "\n".join(conv_lines))
                        self.terminal_text.config(state=tk.DISABLED)
                except Exception:
                    pass
                interface['ip_address'] = ip_val
                interface['mask'] = mask_val
                interface['description'] = desc_var.get()
                interface['status'] = status_val
                interface['duplex'] = duplex_var.get()
                interface['speed'] = speed_var.get()
                self.refresh_interface_list()
                messagebox.showinfo("Éxito", f"Interfaz {name} configurada correctamente")
                dialog.destroy()
            except Exception:
                self.refresh_interface_list()
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
            current_status = interface.get('status', 'down')
            target_action = 'off' if current_status == 'up' else 'on'
            if self._confirm_state_change(interface_name, target_action):
                self._execute_interface_action(interface_name, target_action)
                self.refresh_interface_list()
                new_status = 'up' if target_action == 'on' else 'down'
                messagebox.showinfo("Estado", f"Interfaz {interface_name} {'activada' if new_status == 'up' else 'desactivada'}")
            
    def create_command_preview(self, parent):
        """Crear vista previa de comandos"""
        preview_frame = tk.Frame(parent, bg='#ffffff')
        # Hacer que el panel de comandos aproveche el espacio vertical disponible
        preview_frame.pack(anchor='n', fill=tk.BOTH, expand=True, pady=(10, 0), padx=12)
        
        title_label = tk.Label(preview_frame,
                              text="💻 Comandos de Configuración",
                              font=("Arial", 16, "bold"),
                              bg='#ffffff',
                              fg='#030213')
        title_label.pack(anchor=tk.CENTER, pady=(0, 10))
        
        subtitle_label = tk.Label(preview_frame,
                                 text="Vista previa de los comandos que se ejecutarán en el router",
                                 font=("Arial", 12),
                                 bg='#ffffff',
                                 fg='#666666')
        subtitle_label.pack(anchor=tk.CENTER, pady=(0, 10))
        
        # Terminal frame
        terminal_frame = tk.Frame(preview_frame, bg='black')
        terminal_frame.pack(anchor='n', fill=tk.BOTH, expand=True, pady=(0, 8))
        
        # Texto del terminal
        terminal_text = tk.Text(terminal_frame, bg='black', fg='#00ff00',
                                font=("Consolas", 10), height=15, wrap=tk.WORD)
        terminal_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.terminal_text = terminal_text
        # Permitir desplazamiento con la rueda SOLO dentro de la terminal
        try:
            def _on_terminal_mousewheel(event):
                direction = -1 if event.delta > 0 else 1
                terminal_text.yview_scroll(direction, "units")
                return "break"
            terminal_text.bind("<MouseWheel>", _on_terminal_mousewheel)
        except Exception:
            pass
        terminal_text.config(state=tk.DISABLED)
        
    def refresh(self):
        """Refrescar la vista"""
        self.refresh_interface_list()
        self._rebuild_state_buttons()
        self._update_state_buttons_positions()

    def _create_state_button(self, item_id: str, interface_name: str, status: str):
        txt = "OFF" if str(status).lower() == "up" else "ON"
        bg = "#dc3545" if txt == "OFF" else "#28a745"
        btn = tk.Button(self.interface_tree, text=txt, bg=bg, fg="white", font=("Arial", 9, "bold"), relief="solid", bd=1, cursor="hand2",
                        command=lambda: self._on_state_button_clicked(interface_name, status))
        self._state_buttons[item_id] = btn
        return btn

    def _on_state_button_clicked(self, interface_name: str, status: str):
        action = 'off' if str(status).lower() == 'up' else 'on'
        if not self._confirm_state_change(interface_name, action):
            return
        target_item = None
        for item_id in self.interface_tree.get_children():
            item = self.interface_tree.item(item_id)
            vals = item.get('values', [])
            if vals and vals[0] == interface_name:
                target_item = item_id
                break
        if target_item:
            btn = self._state_buttons.get(target_item)
            if btn and btn.winfo_exists():
                try:
                    btn.config(state="disabled")
                except Exception:
                    pass
        def _worker():
            try:
                self._execute_interface_action(interface_name, action)
                self._refresh_interfaces_only()
            finally:
                def _ui_update():
                    self.refresh_interface_list()
                    self._rebuild_state_buttons()
                    self._update_state_buttons_positions()
                    try:
                        conn = self.shared_data.get('connection_data', {}) or {}
                        vendor = (conn.get('vendor_hint') or conn.get('vendor') or 'cisco').lower()
                        if hasattr(self, "terminal_text") and self.terminal_text.winfo_exists():
                            hostn = "CISCO" if vendor == "cisco" else "ROUTER"
                            if vendor == "cisco":
                                s_cmd = "shutdown" if action == "off" else "no shutdown"
                                lines = [
                                    f"{hostn}#configure terminal",
                                    "Enter configuration commands, one per line.  End with CNTL/Z.",
                                    f"{hostn}(config)#",
                                    f"{hostn}(config)#interface {interface_name}",
                                    f"{hostn}(config-if)#",
                                    f"{hostn}(config-if)#" + s_cmd,
                                    f"{hostn}(config-if)#end",
                                    f"{hostn}#",
                                    f"{hostn}#write memory",
                                ]
                            else:
                                lines = [action]
                            self.terminal_text.config(state=tk.NORMAL)
                            self.terminal_text.delete("1.0", tk.END)
                            self.terminal_text.insert(tk.END, "\n".join(lines))
                            self.terminal_text.config(state=tk.DISABLED)
                    except Exception:
                        pass
                try:
                    self.after(0, _ui_update)
                except Exception:
                    _ui_update()
        threading.Thread(target=_worker, daemon=True).start()

    def _rebuild_state_buttons(self):
        for item_id in self.interface_tree.get_children():
            item = self.interface_tree.item(item_id)
            vals = item.get('values', [])
            if len(vals) >= 7:
                name = vals[0]
                estado = str(vals[4]).strip().upper()
                status = 'up' if estado == 'UP' else 'down'
                btn = self._state_buttons.get(item_id)
                if not btn or not btn.winfo_exists():
                    self._create_state_button(item_id, name, status)
                else:
                    txt = "OFF" if status == "up" else "ON"
                    bg = "#dc3545" if txt == "OFF" else "#28a745"
                    btn.config(text=txt, bg=bg, command=lambda n=name, s=status: self._on_state_button_clicked(n, s))

    def _update_state_buttons_positions(self):
        if not self._columns or 'Acción' not in self._columns:
            return
        col_index = self._columns.index('Acción')
        for item_id, btn in list(self._state_buttons.items()):
            try:
                bbox = self.interface_tree.bbox(item_id, column=col_index)
            except Exception:
                bbox = None
            if not bbox:
                try:
                    btn.place_forget()
                except Exception:
                    pass
                continue
            x, y, w, h = bbox
            bw = 56
            bh = max(20, h - 6) if h else 22
            bx = x + (w - bw) // 2
            by = y + (h - bh) // 2 if h else y
            try:
                btn.place(x=bx, y=by, width=bw, height=bh)
            except Exception:
                pass

    def _update_row_after_toggle(self, interface_name: str, new_status: str):
        target_item = None
        for item_id in self.interface_tree.get_children():
            item = self.interface_tree.item(item_id)
            vals = item.get('values', [])
            if vals and vals[0] == interface_name:
                target_item = item_id
                break
        if not target_item:
            return
        item = self.interface_tree.item(target_item)
        vals = list(item.get('values', []))
        if len(vals) >= 7:
            vals[4] = "UP" if new_status == 'up' else "DOWN"
            self.interface_tree.item(target_item, values=vals, tags=(new_status,))
            btn = self._state_buttons.get(target_item)
            if btn and btn.winfo_exists():
                txt = "OFF" if new_status == 'up' else "ON"
                bg = "#dc3545" if txt == "OFF" else "#28a745"
                btn.config(text=txt, bg=bg, command=lambda n=interface_name, s=new_status: self._on_state_button_clicked(n, s))
        for i in self.shared_data.get('interfaces', []):
            if i.get('name') == interface_name:
                i['status'] = new_status
                break

    def _refresh_interfaces_only(self) -> None:
        conn = self.shared_data.get('connection_data', {}) or {}
        vendor = (conn.get('vendor_hint') or conn.get('vendor') or '').lower()
        cmd = INTERFACES_BRIEF.get(vendor, "")
        if not cmd:
            try:
                proto_probe = (conn.get('protocol') or '').strip()
                if proto_probe == 'Telnet':
                    vendor = 'cisco'
                    cmd = INTERFACES_BRIEF.get(vendor, "")
                else:
                    return
            except Exception:
                return
        raw = ""
        sec_raw = ""
        try:
            conn_fast = dict(conn)
            conn_fast['fast_mode'] = True
            conn_fast['verbose'] = True
            conn_fast['vendor_hint'] = vendor or 'cisco'
            proto = conn_fast.get('protocol', 'SSH2')
            sec_cmd = INTERFACE_CONFIG_SECTION.get('cisco', '')
            if proto == 'Telnet':
                out = run_telnet_commands_batch(conn_fast, [cmd] + ([sec_cmd] if sec_cmd else []), vendor='cisco')
                raw = (out[0] if out else "")
                sec_raw = (out[1] if sec_cmd and len(out) > 1 else "")
            elif proto == 'Serial':
                raw = run_serial_command(conn_fast, cmd)
                if sec_cmd:
                    sec_raw = run_serial_command(conn_fast, sec_cmd)
            else:
                raw = run_ssh_command(conn_fast, cmd)
                if sec_cmd:
                    sec_raw = run_ssh_command(conn_fast, sec_cmd)
        except Exception:
            raw = ""
            sec_raw = ""
        interfaces = []
        try:
            if (vendor == 'cisco') or (proto == 'Telnet'):
                interfaces = parse_cisco_ip_interface_brief(raw or "")
                if not interfaces and vendor == 'huawei':
                    interfaces = parse_huawei_ip_interface_brief(raw or "")
                if not interfaces and vendor == 'juniper':
                    interfaces = parse_juniper_interfaces_terse(raw or "")
            else:
                if vendor == 'huawei':
                    interfaces = parse_huawei_ip_interface_brief(raw or "")
                elif vendor == 'juniper':
                    interfaces = parse_juniper_interfaces_terse(raw or "")
        except Exception:
            interfaces = []
        try:
            from modules.router_analyzer.parsers import parse_cisco_interface_section
            if sec_raw:
                sec_list = parse_cisco_interface_section(sec_raw or "")
                mask_map = {i['name']: i for i in sec_list}
                merged = []
                for it in interfaces or []:
                    mi = mask_map.get(it['name'], {})
                    merged.append({
                        **it,
                        "ip_address": it.get("ip_address") or mi.get("ip_address", ""),
                        "mask": mi.get("mask", it.get("mask", "")),
                        "vrf": mi.get("vrf", it.get("vrf", "")),
                    })
                interfaces = merged or interfaces
        except Exception:
            pass
        if interfaces:
            self.shared_data['interfaces'] = interfaces

    def _confirm_state_change(self, interface_name: str, action: str) -> bool:
        dlg = tk.Toplevel(self)
        dlg.title("⚠️ Confirmación de cambio de estado")
        dlg.transient(self)
        dlg.grab_set()
        dlg.configure(bg="#ffffff")
        dlg.geometry("460x200")
        dlg.update_idletasks()
        x = (dlg.winfo_screenwidth() // 2) - (460 // 2)
        y = (dlg.winfo_screenheight() // 2) - (200 // 2)
        dlg.geometry(f"460x200+{x}+{y}")
        tk.Label(dlg, text="⚠️ Confirmación de cambio de estado", font=("Arial", 13, "bold"), bg="#ffffff", fg="#333333").pack(anchor="w", padx=20, pady=(16, 6))
        verbo = "APAGAR" if action == "off" else "ENCENDER"
        tk.Label(dlg, text=f"¿Estás seguro que deseas {verbo} la interfaz {interface_name}?\nEsta acción puede generar pérdida de conectividad.", font=("Arial", 11), bg="#ffffff", fg="#555555", justify="left").pack(anchor="w", padx=20, pady=(4, 12))
        btns = tk.Frame(dlg, bg="#ffffff")
        btns.pack(fill="x", padx=20, pady=(8, 0))
        result = {"ok": False}
        def _ok():
            result["ok"] = True
            dlg.destroy()
        def _cancel():
            result["ok"] = False
            dlg.destroy()
        tk.Button(btns, text="✖ Cancelar", bg="#dc3545", fg="white", font=("Arial", 11, "bold"), width=12, command=_cancel, cursor="hand2", relief="solid", bd=1).pack(side="right")
        tk.Button(btns, text="✔ Confirmar", bg="#28a745", fg="white", font=("Arial", 11, "bold"), width=12, command=_ok, cursor="hand2", relief="solid", bd=1).pack(side="right", padx=(0,10))
        dlg.wait_window(dlg)
        return bool(result.get("ok"))

    def _execute_interface_action(self, interface_name: str, action: str) -> None:
        iface = next((i for i in self.shared_data.get('interfaces', []) if i.get('name') == interface_name), None)
        if not iface:
            return
        conn = self.shared_data.get('connection_data', {}) or {}
        vendor = (conn.get('vendor_hint') or conn.get('vendor') or '').lower()
        conn_fast = dict(conn)
        conn_fast['fast_mode'] = True
        conn_fast['verbose'] = True
        conn_fast['send_script'] = True
        try:
            if action == 'off':
                shutdown_interface(conn_fast, vendor, interface_name)
            else:
                no_shutdown_interface(conn_fast, vendor, interface_name)
        except Exception:
            pass

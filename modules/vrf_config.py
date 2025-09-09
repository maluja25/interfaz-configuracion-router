import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class VRFConfigFrame(tk.Frame):
    def __init__(self, parent, shared_data):
        super().__init__(parent, bg='#ffffff')
        self.shared_data = shared_data
        
        # Asegurar que la lista de VRFs existe en shared_data
        if 'vrfs' not in self.shared_data:
            self.shared_data['vrfs'] = []
        
        self.create_widgets()
        
    def create_widgets(self):
        """Crear los widgets de configuración de VRF"""
        # Título
        title_frame = tk.Frame(self, bg='#ffffff')
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(title_frame,
                              text="Configuración de VRF",
                              font=("Arial", 20, "bold"),
                              bg='#ffffff',
                              fg='#030213')
        title_label.pack(anchor=tk.W)
        
        subtitle_label = tk.Label(title_frame,
                                 text="Virtual Routing and Forwarding - Gestión de instancias de enrutamiento",
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
        
        # Estadísticas de VRF
        self.create_vrf_stats(scrollable_frame)
        
        # Lista de VRFs
        self.create_vrf_list(scrollable_frame)
        
        # Vista previa de comandos
        self.create_command_preview(scrollable_frame)
        
        # Configurar scroll
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def create_vrf_stats(self, parent):
        """Crear estadísticas de VRF"""
        stats_frame = tk.Frame(parent, bg='#ffffff')
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Calcular estadísticas
        vrfs = self.shared_data.get('vrfs', [])
        total = len(vrfs)
        # Como 'show ip vrf brief' no muestra estado, asumimos que todas las VRF listadas están activas
        active = total
        
        # Contar interfaces asignadas a través de todas las VRF
        total_interfaces = 0
        for vrf in vrfs:
            # La salida del parser junta las interfaces en un solo string
            if vrf.get('interfaces'):
                total_interfaces += len(vrf['interfaces'].split())

        # El número de rutas no está en 'show ip vrf brief', así que lo marcamos como N/A
        total_routes = "N/A"
        
        # Grid de estadísticas
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        stats_frame.grid_columnconfigure(2, weight=1)
        stats_frame.grid_columnconfigure(3, weight=1)
        
        stats = [
            ("📚 Total VRFs", str(total), "#0066cc"),
            ("✅ VRFs Activas", str(active), "#28a745"),
            ("🌐 Interfaces Asignadas", str(total_interfaces), "#6f42c1"),
            ("🔀 Total Rutas", total_routes, "#fd7e14")
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
        
    def create_vrf_list(self, parent):
        """Crear lista de VRFs"""
        list_frame = tk.Frame(parent, bg='#ffffff')
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Título y botón de agregar
        header_frame = tk.Frame(list_frame, bg='#ffffff')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(header_frame,
                              text="📚 Lista de VRFs",
                              font=("Arial", 16, "bold"),
                              bg='#ffffff',
                              fg='#030213')
        title_label.pack(side=tk.LEFT)
        
        add_btn = tk.Button(header_frame, text="➕ Nueva VRF", command=self.add_vrf,
                           bg='#007bff', fg='white', font=("Arial", 10))
        add_btn.pack(side=tk.RIGHT)
        
        # Frame para la tabla
        table_frame = tk.Frame(list_frame, bg='white', relief=tk.SOLID, borderwidth=1)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear Treeview
        columns = ('Nombre', 'RD', 'Estado', 'Interfaces', 'Rutas', 'Descripción')
        self.vrf_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=8)
        
        # Configurar columnas
        self.vrf_tree.heading('Nombre', text='Nombre')
        self.vrf_tree.heading('RD', text='RD')
        self.vrf_tree.heading('Estado', text='Estado')
        self.vrf_tree.heading('Interfaces', text='Interfaces')
        self.vrf_tree.heading('Rutas', text='Rutas')
        self.vrf_tree.heading('Descripción', text='Descripción')
        
        self.vrf_tree.column('Nombre', width=120)
        self.vrf_tree.column('RD', width=120)
        self.vrf_tree.column('Estado', width=80)
        self.vrf_tree.column('Interfaces', width=80)
        self.vrf_tree.column('Rutas', width=80)
        self.vrf_tree.column('Descripción', width=200)
        
        # Scrollbar
        tree_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.vrf_tree.yview)
        self.vrf_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # Botones de acción
        button_frame = tk.Frame(table_frame, bg='white')
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        view_btn = tk.Button(button_frame, text="👁️ Ver Detalles", command=self.view_vrf_details,
                            bg='#17a2b8', fg='white', font=("Arial", 10), state=tk.DISABLED)
        view_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        toggle_btn = tk.Button(button_frame, text="🔄 Cambiar Estado", command=self.toggle_vrf,
                              bg='#28a745', fg='white', font=("Arial", 10), state=tk.DISABLED)
        toggle_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        delete_btn = tk.Button(button_frame, text="🗑️ Eliminar", command=self.delete_vrf,
                              bg='#dc3545', fg='white', font=("Arial", 10))
        delete_btn.pack(side=tk.LEFT)
        
        # Empaquetar
        self.vrf_tree.pack(side='left', fill='both', expand=True)
        tree_scrollbar.pack(side='right', fill='y')
        
        # Cargar datos
        self.refresh_vrf_list()
        
    def refresh_vrf_list(self):
        """Refrescar la lista de VRFs"""
        # Limpiar tabla
        for item in self.vrf_tree.get_children():
            self.vrf_tree.delete(item)
            
        # Agregar VRFs
        for vrf in self.shared_data.get('vrfs', []):
            # Como el estado no está disponible, lo marcamos como 'Activa'
            status_text = "Activa"
            
            # Contar interfaces
            num_interfaces = 0
            if vrf.get('interfaces'):
                num_interfaces = len(vrf.get('interfaces', '').split())

            self.vrf_tree.insert('', tk.END, values=(
                vrf.get('name', 'N/A'),
                vrf.get('default_rd', 'N/A'),
                status_text,
                num_interfaces,
                "N/A",  # Rutas no disponibles
                vrf.get('description', '') # Descripción no viene del parser
            ), tags=('active',))
        
        # Configurar tags para colores
        self.vrf_tree.tag_configure('active', foreground='#28a745')
        self.vrf_tree.tag_configure('inactive', foreground='#dc3545')
        
    def add_vrf(self):
        """Agregar nueva VRF"""
        dialog = tk.Toplevel(self)
        dialog.title("Nueva VRF")
        dialog.geometry("400x500")
        dialog.configure(bg='#ffffff')
        dialog.transient(self)
        dialog.grab_set()
        
        # Centrar ventana
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (500 // 2)
        dialog.geometry(f"400x500+{x}+{y}")
        
        # Variables del formulario
        name_var = tk.StringVar()
        rd_var = tk.StringVar()
        rt_import_var = tk.StringVar()
        rt_export_var = tk.StringVar()
        desc_var = tk.StringVar()
        
        # Título
        title_label = tk.Label(dialog, text="Crear Nueva VRF",
                              font=("Arial", 16, "bold"), bg='#ffffff', fg='#030213')
        title_label.pack(pady=20)
        
        # Formulario
        form_frame = tk.Frame(dialog, bg='#ffffff')
        form_frame.pack(fill=tk.BOTH, expand=True, padx=30)
        
        # Campos del formulario
        fields = [
            ("Nombre de la VRF:", name_var, "CUSTOMER_C"),
            ("Route Distinguisher (RD):", rd_var, "65001:400"),
            ("Route Target Import:", rt_import_var, "65001:400, 65001:999"),
            ("Route Target Export:", rt_export_var, "65001:400"),
            ("Descripción:", desc_var, "Descripción de la VRF")
        ]
        
        for label_text, var, placeholder in fields:
            tk.Label(form_frame, text=label_text, font=("Arial", 12, "bold"),
                    bg='#ffffff', fg='#030213').pack(anchor=tk.W, pady=(10, 5))
            entry = tk.Entry(form_frame, textvariable=var, font=("Arial", 11), width=40)
            entry.pack(anchor=tk.W, pady=(0, 10))
            entry.insert(0, placeholder if label_text.startswith("Descripción") else "")
        
        # Botones
        button_frame = tk.Frame(dialog, bg='#ffffff')
        button_frame.pack(fill=tk.X, padx=30, pady=20)
        
        def save_vrf():
            if not name_var.get() or not rd_var.get():
                messagebox.showerror("Error", "Nombre y RD son obligatorios")
                return
                
            new_vrf = {
                'id': len(self.shared_data['vrfs']) + 1,
                'name': name_var.get(),
                'rd': rd_var.get(),
                'rt_import': [rt.strip() for rt in rt_import_var.get().split(',') if rt.strip()],
                'rt_export': [rt.strip() for rt in rt_export_var.get().split(',') if rt.strip()],
                'description': desc_var.get(),
                'interfaces': [],
                'status': 'inactive',
                'routes': []
            }
            
            self.shared_data['vrfs'].append(new_vrf)
            self.refresh_vrf_list()
            messagebox.showinfo("Éxito", "VRF creada correctamente")
            dialog.destroy()
        
        cancel_btn = tk.Button(button_frame, text="Cancelar", command=dialog.destroy,
                              bg='#6c757d', fg='white', font=("Arial", 12), width=10)
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        save_btn = tk.Button(button_frame, text="💾 Crear VRF", command=save_vrf,
                            bg='#28a745', fg='white', font=("Arial", 12), width=12)
        save_btn.pack(side=tk.RIGHT)
        
    def view_vrf_details(self):
        """Ver detalles de una VRF"""
        messagebox.showinfo("Función no disponible", 
                            "La visualización de detalles aún no está implementada con datos en vivo.")
        # selection = self.vrf_tree.selection()
        # if not selection:
        #     messagebox.showwarning("Selección", "Por favor selecciona una VRF para ver detalles")
        #     return
            
        # item = self.vrf_tree.item(selection[0])
        # vrf_name = item['values'][0]
        
        # vrf = next((v for v in self.shared_data['vrfs'] if v['name'] == vrf_name), None)
        # if vrf:
        #     self.open_vrf_details_dialog(vrf)
            
    def open_vrf_details_dialog(self, vrf):
        """Abrir diálogo de detalles de VRF"""
        dialog = tk.Toplevel(self)
        dialog.title(f"Detalles de VRF: {vrf['name']}")
        dialog.geometry("700x600")
        dialog.configure(bg='#ffffff')
        dialog.transient(self)
        dialog.grab_set()
        
        # Centrar ventana
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (700 // 2)
        y = (dialog.winfo_screenheight() // 2) - (600 // 2)
        dialog.geometry(f"700x600+{x}+{y}")
        
        # Título
        title_label = tk.Label(dialog, text=f"📚 Detalles de VRF: {vrf['name']}",
                              font=("Arial", 16, "bold"), bg='#ffffff', fg='#030213')
        title_label.pack(pady=20)
        
        # Notebook para pestañas
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Pestaña General
        general_frame = tk.Frame(notebook, bg='#ffffff')
        notebook.add(general_frame, text="General")
        
        info_frame = tk.LabelFrame(general_frame, text="Información Básica", bg='#ffffff', fg='#030213')
        info_frame.pack(fill=tk.X, padx=20, pady=20)
        
        info_items = [
            ("Nombre:", vrf['name']),
            ("Route Distinguisher:", vrf['rd']),
            ("Estado:", "Activa" if vrf['status'] == 'active' else "Inactiva"),
            ("Descripción:", vrf['description'])
        ]
        
        for label, value in info_items:
            item_frame = tk.Frame(info_frame, bg='#ffffff')
            item_frame.pack(fill=tk.X, padx=10, pady=5)
            tk.Label(item_frame, text=label, font=("Arial", 11, "bold"),
                    bg='#ffffff', fg='#030213').pack(side=tk.LEFT)
            tk.Label(item_frame, text=value, font=("Arial", 11),
                    bg='#ffffff', fg='#666666').pack(side=tk.RIGHT)
        
        # Estadísticas
        stats_frame = tk.LabelFrame(general_frame, text="Estadísticas", bg='#ffffff', fg='#030213')
        stats_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        stats_items = [
            ("Interfaces:", str(len(vrf['interfaces']))),
            ("Rutas:", str(len(vrf['routes']))),
            ("RT Import:", str(len(vrf['rt_import']))),
            ("RT Export:", str(len(vrf['rt_export'])))
        ]
        
        for label, value in stats_items:
            item_frame = tk.Frame(stats_frame, bg='#ffffff')
            item_frame.pack(fill=tk.X, padx=10, pady=5)
            tk.Label(item_frame, text=label, font=("Arial", 11, "bold"),
                    bg='#ffffff', fg='#030213').pack(side=tk.LEFT)
            tk.Label(item_frame, text=value, font=("Arial", 11),
                    bg='#ffffff', fg='#666666').pack(side=tk.RIGHT)
        
        # Pestaña Interfaces
        interfaces_frame = tk.Frame(notebook, bg='#ffffff')
        notebook.add(interfaces_frame, text="Interfaces")
        
        if vrf['interfaces']:
            for interface in vrf['interfaces']:
                iface_frame = tk.Frame(interfaces_frame, bg='white', relief=tk.SOLID, borderwidth=1)
                iface_frame.pack(fill=tk.X, padx=20, pady=10)
                tk.Label(iface_frame, text=f"🌐 {interface}", font=("Arial", 12),
                        bg='white', fg='#030213').pack(pady=10)
        else:
            tk.Label(interfaces_frame, text="No hay interfaces asignadas a esta VRF",
                    font=("Arial", 12), bg='#ffffff', fg='#666666').pack(expand=True)
        
        # Pestaña Rutas
        routes_frame = tk.Frame(notebook, bg='#ffffff')
        notebook.add(routes_frame, text="Tabla de Rutas")
        
        if vrf['routes']:
            # Crear tabla de rutas
            routes_tree = ttk.Treeview(routes_frame, columns=('Red', 'Next Hop', 'Tipo'), show='headings', height=10)
            routes_tree.heading('Red', text='Red')
            routes_tree.heading('Next Hop', text='Next Hop')
            routes_tree.heading('Tipo', text='Tipo')
            
            for route in vrf['routes']:
                routes_tree.insert('', tk.END, values=(
                    route['network'],
                    route['next_hop'],
                    route['type'].upper()
                ))
            
            routes_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        else:
            tk.Label(routes_frame, text="No hay rutas configuradas en esta VRF",
                    font=("Arial", 12), bg='#ffffff', fg='#666666').pack(expand=True)
        
        # Pestaña Route Targets
        rt_frame = tk.Frame(notebook, bg='#ffffff')
        notebook.add(rt_frame, text="Route Targets")
        
        # RT Import
        import_frame = tk.LabelFrame(rt_frame, text="Route Target Import", bg='#ffffff', fg='#030213')
        import_frame.pack(fill=tk.X, padx=20, pady=20)
        
        for rt in vrf['rt_import']:
            tk.Label(import_frame, text=f"🌍 {rt}", font=("Arial", 11),
                    bg='#ffffff', fg='#28a745').pack(anchor=tk.W, padx=10, pady=2)
        
        # RT Export
        export_frame = tk.LabelFrame(rt_frame, text="Route Target Export", bg='#ffffff', fg='#030213')
        export_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        for rt in vrf['rt_export']:
            tk.Label(export_frame, text=f"🔀 {rt}", font=("Arial", 11),
                    bg='#ffffff', fg='#007bff').pack(anchor=tk.W, padx=10, pady=2)
        
        # Botón cerrar
        close_btn = tk.Button(dialog, text="Cerrar", command=dialog.destroy,
                             bg='#6c757d', fg='white', font=("Arial", 12), width=10)
        close_btn.pack(pady=(0, 20))
        
    def toggle_vrf(self):
        """Cambiar estado de VRF"""
        messagebox.showinfo("Función no disponible", 
                            "El cambio de estado de VRF no es aplicable con los datos actuales.")
        # selection = self.vrf_tree.selection()
        # if not selection:
        #     messagebox.showwarning("Selección", "Por favor selecciona una VRF")
        #     return
            
        # item = self.vrf_tree.item(selection[0])
        # vrf_name = item['values'][0]
        
        # vrf = next((v for v in self.shared_data['vrfs'] if v['name'] == vrf_name), None)
        # if vrf:
        #     new_status = 'inactive' if vrf['status'] == 'active' else 'active'
        #     vrf['status'] = new_status
        #     self.refresh_vrf_list()
        #     status_text = "activada" if new_status == 'active' else "desactivada"
        #     messagebox.showinfo("Estado", f"VRF {vrf_name} {status_text}")
            
    def delete_vrf(self):
        """Eliminar VRF"""
        selection = self.vrf_tree.selection()
        if not selection:
            messagebox.showwarning("Selección", "Por favor selecciona una VRF para eliminar")
            return
            
        item = self.vrf_tree.item(selection[0])
        vrf_name = item['values'][0]
        
        if messagebox.askyesno("Confirmar", f"¿Estás seguro de eliminar la VRF {vrf_name}?"):
            self.shared_data['vrfs'] = [v for v in self.shared_data['vrfs'] if v['name'] != vrf_name]
            self.refresh_vrf_list()
            messagebox.showinfo("Éxito", f"VRF {vrf_name} eliminada")
            
    def create_command_preview(self, parent):
        """Crear vista previa de comandos VRF"""
        preview_frame = tk.Frame(parent, bg='#ffffff')
        preview_frame.pack(fill=tk.X, pady=(20, 0))
        
        title_label = tk.Label(preview_frame,
                              text="💻 Comandos de Configuración VRF",
                              font=("Arial", 16, "bold"),
                              bg='#ffffff',
                              fg='#030213')
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        subtitle_label = tk.Label(preview_frame,
                                 text="Vista previa de los comandos para configurar las VRFs",
                                 font=("Arial", 12),
                                 bg='#ffffff',
                                 fg='#666666')
        subtitle_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Terminal frame
        terminal_frame = tk.Frame(preview_frame, bg='black')
        terminal_frame.pack(fill=tk.X)
        
        # Texto del terminal
        terminal_text = tk.Text(terminal_frame, bg='black', fg='#00ff00',
                               font=("Consolas", 10), height=20, wrap=tk.WORD)
        terminal_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Generar comandos
        commands = ["# Configuración de VRFs"]
        for vrf in self.shared_data.get('vrfs', []):
            # Asumimos que todas las VRF detectadas deben ser configuradas (están activas)
            commands.extend([
                f"vrf definition {vrf.get('name', 'N/A')}",
                f"  rd {vrf.get('default_rd', 'N/A')}"
            ])
            
            # Los RTs y las interfaces no se obtienen de 'show ip vrf brief', 
            # así que esta parte no generará comandos adicionales con los datos actuales.
            # Se deja la lógica por si se implementa un parsing más detallado en el futuro.
            
            for rt in vrf.get('rt_import', []):
                commands.append(f"  route-target import {rt}")
                
            for rt in vrf.get('rt_export', []):
                commands.append(f"  route-target export {rt}")
                
            commands.extend([
                "  address-family ipv4",
                "  exit-address-family",
                "  exit",
                f"# Asignación de interfaces para {vrf.get('name', 'N/A')}"
            ])
            
            # La salida del parser junta las interfaces en un solo string
            interfaces_str = vrf.get('interfaces', '')
            if interfaces_str:
                for interface in interfaces_str.split():
                    commands.extend([
                        f"interface {interface}",
                        f"  vrf forwarding {vrf.get('name', 'N/A')}",
                        "  exit"
                    ])
            commands.append("")
        
        terminal_text.insert(tk.END, "\n".join(commands))
        terminal_text.config(state=tk.DISABLED)
        
    def refresh(self):
        """Refrescar la vista"""
        self.refresh_vrf_list()
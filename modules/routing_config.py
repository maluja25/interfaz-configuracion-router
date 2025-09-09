import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class RoutingConfigFrame(tk.Frame):
    def __init__(self, parent, shared_data):
        super().__init__(parent)
        self.shared_data = shared_data
        
        self.configure(bg='#ffffff')
        self.pack(fill=tk.BOTH, expand=True)

        # Frame principal con padding
        main_frame = ttk.Frame(self, style="Card.TFrame", padding=(20, 20))
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título y subtítulo
        title = ttk.Label(main_frame, text="Protocolos de Enrutamiento", font=("Arial", 18, "bold"), background="white")
        title.pack(anchor="w")
        
        subtitle = ttk.Label(main_frame, text="Configura protocolos dinámicos y rutas estáticas", font=("Arial", 10), background="white")
        subtitle.pack(anchor="w", pady=(0, 20))

        # Pestañas de navegación
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        protocols_tab = ttk.Frame(notebook, style="Card.TFrame")
        static_routes_tab = ttk.Frame(notebook, style="Card.TFrame")
        
        notebook.add(protocols_tab, text="  Protocolos  ")
        notebook.add(static_routes_tab, text="  Rutas Estáticas  ")

        self.create_protocols_tab(protocols_tab)
        self.create_static_routes_tab(static_routes_tab)

        self.create_preview_section(main_frame)
        self.refresh_routes_table() # Cargar rutas existentes al iniciar
        self.update_preview()
        
    def create_protocols_tab(self, parent):
        """Crea el contenido de la pestaña de Protocolos."""
        protocols_frame = ttk.Frame(parent, style="Card.TFrame")
        protocols_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        protocols = [
            ("OSPF (Open Shortest Path First)", "Protocolo de estado de enlace para redes internas"),
            ("EIGRP (Enhanced Interior Gateway Routing Protocol)", "Protocolo propietario de Cisco"),
            ("BGP (Border Gateway Protocol)", "Protocolo para enrutamiento entre dominios"),
            ("RIP (Routing Information Protocol)", "Protocolo de enrutamiento de vector distancia simple")
        ]

        num_rows = (len(protocols) + 1) // 2

        # Crear tarjetas en dos columnas
        for i, (name, desc) in enumerate(protocols):
            row, col = divmod(i, 2)
            card = self.create_protocol_card(protocols_frame, name, desc)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        protocols_frame.grid_columnconfigure(0, weight=1)
        protocols_frame.grid_columnconfigure(1, weight=1)
        for i in range(num_rows):
            protocols_frame.grid_rowconfigure(i, weight=1)

    def create_protocol_card(self, parent, name, description):
        """Crea una tarjeta individual para un protocolo."""
        card_frame = tk.Frame(parent, bg="white", bd=1, relief="solid", highlightbackground="#e0e0e0", highlightthickness=1)
        
        content_frame = tk.Frame(card_frame, bg="white", padx=15, pady=15)
        content_frame.pack(fill="both", expand=True)
        
        header_frame = tk.Frame(content_frame, bg="white")
        header_frame.pack(fill="x")

        protocol_name_short = name.split(" ")[0]

        name_label = tk.Label(header_frame, text=name, font=("Arial", 11, "bold"), bg="white", anchor="w")
        name_label.pack(side="left", fill="x")

        status_badge = tk.Label(header_frame, text="Deshabilitado", font=("Arial", 9), bg='#f3f3f5', fg='#030213', padx=8, pady=4)
        status_badge.pack(side="right")
        
        desc_label = tk.Label(content_frame, text=description, font=("Arial", 9), bg="white", justify="left", anchor="w")
        desc_label.pack(fill="x", pady=(5, 10))

        def update_wraplength(event):
            desc_label.config(wraplength=max(1, event.width - 10))
        
        content_frame.bind("<Configure>", update_wraplength)

        separator = ttk.Separator(content_frame, orient='horizontal')
        separator.pack(fill='x', pady=5)
        
        footer_frame = tk.Frame(content_frame, bg="white")
        footer_frame.pack(fill="x", pady=(5, 0))

        enable_label = tk.Label(footer_frame, text=f"Habilitar {protocol_name_short}", font=("Arial", 10), bg="white")
        enable_label.pack(side="left")

        # Usamos un Checkbutton como interruptor
        toggle_var = tk.BooleanVar()
        toggle_button = ttk.Checkbutton(footer_frame, variable=toggle_var, style="Switch.TCheckbutton")
        toggle_button.pack(side="right")
        
        return card_frame

    def create_static_routes_tab(self, parent):
        """Crea el contenido de la pestaña de Rutas Estáticas."""
        # Frame principal para la pestaña
        static_routes_frame = ttk.Frame(parent, style="Card.TFrame")
        static_routes_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # 1. Formulario para agregar nueva ruta
        form_frame = ttk.Frame(static_routes_frame, style="Card.TFrame", padding=(15, 15))
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        form_title = ttk.Label(form_frame, text="Añadir Nueva Ruta Estática", font=("Arial", 12, "bold"), background="white")
        form_title.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 10))

        # Entradas del formulario
        ttk.Label(form_frame, text="Red de Destino:", background="white").grid(row=1, column=0, sticky="w", padx=(0, 5))
        self.dest_net_entry = ttk.Entry(form_frame)
        self.dest_net_entry.grid(row=1, column=1, sticky="ew", padx=5)

        ttk.Label(form_frame, text="Máscara de Subred:", background="white").grid(row=2, column=0, sticky="w", padx=(0, 5))
        self.subnet_mask_entry = ttk.Entry(form_frame)
        self.subnet_mask_entry.grid(row=2, column=1, sticky="ew", padx=5)

        ttk.Label(form_frame, text="Siguiente Salto:", background="white").grid(row=1, column=2, sticky="w", padx=(15, 5))
        self.next_hop_entry = ttk.Entry(form_frame)
        self.next_hop_entry.grid(row=1, column=3, sticky="ew", padx=5)
        
        ttk.Label(form_frame, text="Distancia (opcional):", background="white").grid(row=2, column=2, sticky="w", padx=(15, 5))
        self.distance_entry = ttk.Entry(form_frame)
        self.distance_entry.grid(row=2, column=3, sticky="ew", padx=5)

        add_button = ttk.Button(form_frame, text="Añadir Ruta", command=self.add_static_route)
        add_button.grid(row=3, column=3, sticky="e", pady=(10, 0))

        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_columnconfigure(3, weight=1)

        # 2. Tabla de rutas estáticas
        table_frame = ttk.Frame(static_routes_frame, style="Card.TFrame", padding=(15, 15))
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        table_title = ttk.Label(table_frame, text="Rutas Estáticas Configuradas", font=("Arial", 12, "bold"), background="white")
        table_title.pack(anchor="w", pady=(0, 10))

        columns = ("destino", "mascara", "siguiente_salto", "distancia")
        self.routes_table = ttk.Treeview(table_frame, columns=columns, show="headings")

        # Configurar encabezados
        self.routes_table.heading("destino", text="Red de Destino")
        self.routes_table.heading("mascara", text="Máscara de Subred")
        self.routes_table.heading("siguiente_salto", text="Siguiente Salto")
        self.routes_table.heading("distancia", text="Distancia")
        
        # Configurar columnas
        self.routes_table.column("destino", width=150)
        self.routes_table.column("mascara", width=150)
        self.routes_table.column("siguiente_salto", width=150)
        self.routes_table.column("distancia", width=100)

        self.routes_table.pack(fill=tk.BOTH, expand=True)

        # Botón para eliminar ruta seleccionada
        delete_button = ttk.Button(table_frame, text="Eliminar Ruta Seleccionada", command=self.delete_static_route)
        delete_button.pack(pady=(10, 0), anchor="e")


    def add_static_route(self):
        """Añade una nueva ruta estática a la tabla y a los datos compartidos."""
        dest = self.dest_net_entry.get()
        mask = self.subnet_mask_entry.get()
        next_hop = self.next_hop_entry.get()
        distance = self.distance_entry.get()

        if not dest or not mask or not next_hop:
            messagebox.showwarning("Campos incompletos", "Los campos Red, Máscara y Siguiente Salto son obligatorios.")
            return

        new_route = {
            'dest': dest,
            'mask': mask,
            'next_hop': next_hop,
            'distance': distance
        }

        self.shared_data['static_routes'].append(new_route)
        
        self.refresh_routes_table()
        self.update_preview()

        # Limpiar campos de entrada
        self.dest_net_entry.delete(0, tk.END)
        self.subnet_mask_entry.delete(0, tk.END)
        self.next_hop_entry.delete(0, tk.END)
        self.distance_entry.delete(0, tk.END)

    def delete_static_route(self):
        """Elimina la ruta estática seleccionada de la tabla."""
        selected_items = self.routes_table.selection()
        if not selected_items:
            messagebox.showwarning("Ninguna selección", "Por favor, selecciona al menos una ruta para eliminar.")
            return

        # Confirmación
        if not messagebox.askyesno("Confirmar eliminación", "¿Estás seguro de que quieres eliminar las rutas seleccionadas?"):
            return

        for item in selected_items:
            item_values = self.routes_table.item(item, 'values')
            
            # Encontrar y eliminar la ruta de shared_data
            route_to_delete = None
            for route in self.shared_data['static_routes']:
                # Comparar valores para encontrar la coincidencia
                if (route['dest'] == item_values[0] and
                    route['mask'] == item_values[1] and
                    route['next_hop'] == item_values[2] and
                    route.get('distance', '') == item_values[3]):
                    route_to_delete = route
                    break
            
            if route_to_delete:
                self.shared_data['static_routes'].remove(route_to_delete)

        self.refresh_routes_table()
        self.update_preview()

    def refresh_routes_table(self):
        """Limpia y vuelve a cargar la tabla de rutas estáticas."""
        # Limpiar tabla
        for item in self.routes_table.get_children():
            self.routes_table.delete(item)
        
        # Llenar con datos actualizados
        for route in self.shared_data.get('static_routes', []):
            self.routes_table.insert("", tk.END, values=(
                route['dest'],
                route['mask'],
                route['next_hop'],
                route.get('distance', '')
            ))

    def create_preview_section(self, parent):
        """Crea la sección de vista previa de configuración."""
        preview_frame = tk.Frame(parent, bg="white", pady=20)
        preview_frame.pack(fill="x", side="bottom")

        title = tk.Label(preview_frame, text="Vista Previa de Configuración", font=("Arial", 12, "bold"), bg="white", anchor="w")
        title.pack(fill="x")
        
        subtitle = tk.Label(preview_frame, text="Comandos que se ejecutarán en el router", font=("Arial", 9), bg="white", anchor="w")
        subtitle.pack(fill="x", pady=(0, 10))
        
        text_frame = tk.Frame(preview_frame, bg="#030213", bd=0)
        text_frame.pack(fill="both", expand=True)

        preview_text = tk.Text(text_frame, height=6, bg="#030213", fg="white", font=("Courier", 10), relief="flat", padx=15, pady=15, insertbackground="white")
        preview_text.pack(fill="both", expand=True)
        
        # Guardar referencia al widget de texto
        self.preview_text = preview_text

        # Insertar texto de ejemplo inicial
        self.update_preview()
        self.preview_text.config(state="disabled")

    def update_preview(self):
        """Actualiza la vista previa con la configuración actual."""
        self.preview_text.config(state="normal")
        self.preview_text.delete("1.0", tk.END)
        
        commands = "# Configuración de protocolos de enrutamiento\n"
        
        # Aquí se agregarán los comandos de las rutas estáticas
        static_routes = self.shared_data.get('static_routes', [])
        if not static_routes:
            commands += "# No hay rutas estáticas configuradas.\n"
        else:
            for route in static_routes:
                command = f"ip route {route['dest']} {route['mask']} {route['next_hop']}"
                if route.get('distance'):
                    command += f" {route['distance']}"
                commands += command + "\n"

        self.preview_text.insert("1.0", commands)
        self.preview_text.config(state="disabled")

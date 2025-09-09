import tkinter as tk
from tkinter import ttk

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
        label = ttk.Label(parent, text="Aquí se configurarán las rutas estáticas.", font=("Arial", 12))
        label.pack(pady=20, padx=20)

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
        
        # Insertar texto de ejemplo
        commands = (
            "# Configuración de protocolos de enrutamiento\n"
            "ip route 0.0.0.0 0.0.0.0 203.0.113.1\n"
            "ip route 172.16.0.0 255.255.0.0 192.168.1.254 1\n"
            "ip route 10.10.0.0 255.255.0.0 10.0.0.254 1"
        )
        preview_text.insert("1.0", commands)
        preview_text.config(state="disabled")

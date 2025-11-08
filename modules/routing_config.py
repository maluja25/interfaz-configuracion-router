import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import re
from typing import Dict, List, Any, Optional, Tuple

# Constantes para la configuración de protocolos de enrutamiento (solo OSPF y BGP)
PROTOCOL_OSPF = 'ospf'
PROTOCOL_BGP = 'bgp'

# Constantes para los estados de los protocolos
ENABLED = 'enabled'
CONFIG = 'config'

# Constantes para los campos de rutas estáticas
DEST = 'dest'
MASK = 'mask'
NEXT_HOP = 'next_hop'
DISTANCE = 'distance'

# Constantes para colores y estilos
COLOR_WHITE = '#ffffff'
COLOR_ENABLED = '#4CAF50'  # Verde más intenso para mejor visibilidad
COLOR_DISABLED = '#f3f3f5'
TEXT_ENABLED = 'Habilitado'
TEXT_DISABLED = 'Deshabilitado'
FG_ENABLED = '#ffffff'  # Texto blanco para mejor contraste
FG_DISABLED = '#030213'
COLOR_CARD_BORDER = '#e0e0e0'
COLOR_CARD_HEADER = '#f9f9f9'  # Color de fondo para el encabezado
COLOR_SWITCH_ACTIVE = '#4CAF50'  # Color para el switch activo

class RoutingConfigFrame(tk.Frame):
    """Frame para la configuración de protocolos de enrutamiento y rutas estáticas.
    
    Esta clase gestiona la interfaz de usuario para configurar protocolos de enrutamiento
    dinámicos (OSPF y BGP) y rutas estáticas.
    """
    
    def __init__(self, parent: tk.Widget, shared_data: Dict[str, Any]) -> None:
        """Inicializa el frame de configuración de enrutamiento.
        
        Args:
            parent: Widget padre donde se colocará este frame
            shared_data: Diccionario con datos compartidos entre módulos
        """
        super().__init__(parent)
        self.shared_data = shared_data
        
        # Inicializar estructura de datos para protocolos de enrutamiento si no existe
        if 'routing_protocols' not in self.shared_data:
            self.shared_data['routing_protocols'] = {}
            
        # Asegurar que los protocolos soportados estén inicializados
        for protocol in [PROTOCOL_OSPF, PROTOCOL_BGP]:
            if protocol not in self.shared_data['routing_protocols']:
                self.shared_data['routing_protocols'][protocol] = {ENABLED: False, CONFIG: ''}
            else:
                # Asegurar que existan las claves necesarias
                if ENABLED not in self.shared_data['routing_protocols'][protocol]:
                    self.shared_data['routing_protocols'][protocol][ENABLED] = False
                if CONFIG not in self.shared_data['routing_protocols'][protocol]:
                    self.shared_data['routing_protocols'][protocol][CONFIG] = ''
        
        # Variables para controlar el estado de los protocolos
        self.protocol_vars = self._initialize_protocol_variables()
        
        # Referencias a los widgets de configuración
        self.config_widgets = {}
        
        # Inicializar estructura de datos para rutas estáticas si no existe
        if 'static_routes' not in self.shared_data:
            self.shared_data['static_routes'] = []
        
        self.configure(bg=COLOR_WHITE)
        self.pack(fill=tk.BOTH, expand=True)
        
        # Diccionario para badges de estado por protocolo
        self.status_badges: Dict[str, tk.Label] = {}

        # Inicializar la interfaz de usuario
        self._setup_ui()

    def _initialize_protocol_variables(self) -> Dict[str, tk.BooleanVar]:
        """Inicializa las variables de control para los protocolos de enrutamiento.
        
        Returns:
            Diccionario con las variables de control para cada protocolo
        """
        return {
            PROTOCOL_OSPF: tk.BooleanVar(value=self.shared_data['routing_protocols'][PROTOCOL_OSPF][ENABLED]),
            PROTOCOL_BGP: tk.BooleanVar(value=self.shared_data['routing_protocols'][PROTOCOL_BGP][ENABLED])
        }
    
    def _setup_ui(self) -> None:
        """Configura la interfaz de usuario del módulo de enrutamiento."""
        # Frame principal con padding
        main_frame = ttk.Frame(self, style="Card.TFrame", padding=(20, 20))
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título y subtítulo
        title = ttk.Label(main_frame, text="Enrutamiento", font=("Arial", 18, "bold"), background="white")
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
        
    def create_protocols_tab(self, parent: ttk.Frame) -> None:
        """Crea el contenido de la pestaña de Protocolos.
        
        Organiza los protocolos de enrutamiento en una cuadrícula de tarjetas,
        cada una con información y controles para un protocolo específico.
        
        Args:
            parent: Frame padre donde se colocarán los elementos
        """
        protocols_frame = ttk.Frame(parent, style="Card.TFrame")
        protocols_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Definición de los protocolos disponibles con su información (solo OSPF y BGP)
        protocols = [
            ("OSPF (Open Shortest Path First)", "Protocolo de estado de enlace para redes internas", PROTOCOL_OSPF),
            ("BGP (Border Gateway Protocol)", "Protocolo para enrutamiento entre dominios", PROTOCOL_BGP)
        ]

        # Calcular el número de filas necesarias para la cuadrícula
        num_rows = (len(protocols) + 1) // 2

        # Crear tarjetas en dos columnas
        for i, (name, desc, protocol_id) in enumerate(protocols):
            row, col = divmod(i, 2)  # Distribuir en 2 columnas
            card = self.create_protocol_card(protocols_frame, name, desc, protocol_id)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        # Configurar el comportamiento de redimensionamiento de la cuadrícula
        protocols_frame.grid_columnconfigure(0, weight=1)
        protocols_frame.grid_columnconfigure(1, weight=1)
        for i in range(num_rows):
            protocols_frame.grid_rowconfigure(i, weight=1)

    def create_protocol_card(self, parent: tk.Widget, name: str, description: str, protocol_id: str) -> tk.Frame:
        """Crea una tarjeta individual para un protocolo de enrutamiento.
        
        Args:
            parent: Widget padre donde se colocará la tarjeta
            name: Nombre completo del protocolo
            description: Descripción del protocolo
            protocol_id: Identificador del protocolo (ospf, bgp)
            
        Returns:
            Frame que contiene la tarjeta del protocolo
            
        Raises:
            KeyError: Si el protocol_id no existe en self.protocol_vars
        """
        # Validar que el protocolo exista
        if protocol_id not in self.protocol_vars:
            raise KeyError(f"Protocolo no reconocido: {protocol_id}")
            
        # Crear el frame principal de la tarjeta con sombra y bordes redondeados
        card_frame = tk.Frame(parent, bg=COLOR_WHITE, bd=1, relief="solid", 
                             highlightbackground=COLOR_CARD_BORDER, highlightthickness=1)
        
        # Frame para el encabezado con color de fondo diferente
        header_frame = tk.Frame(card_frame, bg=COLOR_CARD_HEADER, padx=15, pady=10)
        header_frame.pack(fill="x")
        
        # Extraer el nombre corto del protocolo (primera palabra)
        protocol_name_short = name.split(" ")[0]
        
        # Crear la sección de encabezado en el header_frame y guardar badge
        _name_label, _status_badge = self._create_card_header(header_frame, name, protocol_id)
        self.status_badges[protocol_id] = _status_badge
        
        # Frame para el contenido con padding
        content_frame = tk.Frame(card_frame, bg=COLOR_WHITE, padx=15, pady=15)
        content_frame.pack(fill="both", expand=True)
        
        # Crear la sección de descripción
        desc_label = self._create_description_section(content_frame, description)
        
        # Crear la sección del interruptor con estilo mejorado
        self._create_toggle_section(content_frame, protocol_name_short, protocol_id)
        
        # Separador antes del área de configuración
        separator = ttk.Separator(content_frame, orient='horizontal')
        separator.pack(fill='x', pady=10)
        
        # Crear la sección de configuración
        self._create_config_section(content_frame, protocol_name_short, protocol_id)
        
        return card_frame

    def resync_protocol_states(self) -> None:
        """Sincroniza los switches y badges con shared_data tras análisis."""
        try:
            for protocol_id, var in self.protocol_vars.items():
                target_state = bool(self.shared_data.get('routing_protocols', {})
                                    .get(protocol_id, {})
                                    .get(ENABLED, False))
                var.set(target_state)
                self.toggle_protocol(protocol_id, self.status_badges.get(protocol_id))
        except Exception as e:
            print(f"Error al sincronizar estados de protocolos: {e}")
        
    def _create_card_header(self, parent: tk.Frame, name: str, protocol_id: str) -> Tuple[tk.Label, tk.Label]:
        """Crea la sección de encabezado de la tarjeta de protocolo.
        
        Args:
            parent: Frame padre
            name: Nombre completo del protocolo
            protocol_id: Identificador del protocolo
            
        Returns:
            Tupla con las etiquetas de nombre y estado
        """
        header_frame = tk.Frame(parent, bg=COLOR_CARD_HEADER)
        header_frame.pack(fill="x")

        # Icono para el protocolo (usando emoji como placeholder)
        protocol_icons = {
            PROTOCOL_OSPF: "🌐",
            PROTOCOL_BGP: "🌍",
        }
        
        icon = protocol_icons.get(protocol_id, "🔀")
        
        # Frame para el título con icono
        title_frame = tk.Frame(header_frame, bg=COLOR_CARD_HEADER)
        title_frame.pack(side="left", fill="x")
        
        # Icono del protocolo
        icon_label = tk.Label(title_frame, text=icon, font=("Arial", 16), 
                             bg=COLOR_CARD_HEADER, anchor="w")
        icon_label.pack(side="left", padx=(0, 5))

        # Etiqueta con el nombre del protocolo
        name_label = tk.Label(title_frame, text=name, font=("Arial", 12, "bold"), 
                             bg=COLOR_CARD_HEADER, anchor="w")
        name_label.pack(side="left", fill="x")

        # Badge de estado con estilo mejorado
        status_badge = tk.Label(header_frame, text=TEXT_DISABLED, font=("Arial", 10, "bold"), 
                              bg=COLOR_DISABLED, fg=FG_DISABLED, padx=10, pady=5,
                              borderwidth=1, relief="solid")
        status_badge.pack(side="right", padx=10)
        
        # Actualizar el estado inicial del badge
        if self.protocol_vars[protocol_id].get():
            status_badge.config(text=TEXT_ENABLED, bg=COLOR_ENABLED, fg=FG_ENABLED)
        else:
            status_badge.config(text=TEXT_DISABLED, bg=COLOR_DISABLED, fg=FG_DISABLED)
            
        return name_label, status_badge
    
    def _create_description_section(self, parent: tk.Frame, description: str) -> tk.Label:
        """Crea la sección de descripción de la tarjeta de protocolo.
        
        Args:
            parent: Frame padre
            description: Descripción del protocolo
            
        Returns:
            Etiqueta de descripción
        """
        desc_label = tk.Label(parent, text=description, font=("Arial", 9), 
                            bg=COLOR_WHITE, justify="left", anchor="w")
        desc_label.pack(fill="x", pady=(5, 10))

        # Función para ajustar el ancho del texto cuando se redimensiona
        def update_wraplength(event):
            desc_label.config(wraplength=max(1, event.width - 10))
        
        parent.bind("<Configure>", update_wraplength)
        
        return desc_label
    
    def _create_toggle_section(self, parent: tk.Frame, protocol_name_short: str, protocol_id: str) -> None:
        """Crea la sección del interruptor de activación del protocolo.
        
        Args:
            parent: Frame padre
            protocol_name_short: Nombre corto del protocolo
            protocol_id: Identificador del protocolo
        """
        # Frame para el interruptor de activación con estilo destacado
        toggle_frame = tk.Frame(parent, bg=COLOR_WHITE, padx=5, pady=10)
        toggle_frame.pack(fill="x", pady=(10, 10))
        
        # Crear un subframe con borde y fondo para destacar el área del switch
        switch_container = tk.Frame(toggle_frame, bg="#f5f5f5", bd=1, relief="solid", 
                                  highlightbackground="#e0e0e0", highlightthickness=1)
        switch_container.pack(fill="x", pady=5, ipady=8)

        # Etiqueta para el interruptor con estilo mejorado
        enable_label = tk.Label(switch_container, text=f"Habilitar {protocol_name_short}", 
                               font=("Arial", 11, "bold"), bg="#f5f5f5")
        enable_label.pack(side="left", padx=15)

        # Buscar el badge de estado en el frame padre
        status_badge = None
        # Buscar en el frame de encabezado (ahora está en un nivel superior)
        for widget in parent.master.winfo_children()[0].winfo_children():
            if isinstance(widget, tk.Label) and widget.cget("text") in [TEXT_ENABLED, TEXT_DISABLED]:
                status_badge = widget
                break

        # Crear un frame contenedor para el botón de encendido/apagado personalizado
        toggle_container = tk.Frame(switch_container, bg="#f5f5f5")
        toggle_container.pack(side="right", padx=15)
        
        # Crear un botón personalizado tipo encendido/apagado
        toggle_width = 60
        toggle_height = 26
        
        # Canvas para dibujar el botón personalizado
        toggle_canvas = tk.Canvas(toggle_container, width=toggle_width, height=toggle_height, 
                                bg="#f5f5f5", highlightthickness=0)
        toggle_canvas.pack()
        
        # Función para actualizar la apariencia del botón según el estado
        def update_toggle_appearance():
            toggle_canvas.delete("all")
            is_on = self.protocol_vars[protocol_id].get()
            
            # Dibujar el fondo del botón (redondeado)
            if is_on:
                bg_color = COLOR_SWITCH_ACTIVE
                circle_x = toggle_width - 16
                text = "ON"
                text_x = 15
            else:
                bg_color = "#cccccc"
                circle_x = 16
                text = "OFF"
                text_x = toggle_width - 20
            
            # Crear el rectángulo redondeado para el fondo usando arcos y líneas
            radius = 12
            # Coordenadas
            x1, y1 = 2, 2
            x2, y2 = toggle_width-2, toggle_height-2
            
            # Dibujar los cuatro arcos de las esquinas
            toggle_canvas.create_arc(x1, y1, x1 + 2*radius, y1 + 2*radius, 
                                    start=90, extent=90, fill=bg_color, outline=bg_color)
            toggle_canvas.create_arc(x2 - 2*radius, y1, x2, y1 + 2*radius, 
                                    start=0, extent=90, fill=bg_color, outline=bg_color)
            toggle_canvas.create_arc(x1, y2 - 2*radius, x1 + 2*radius, y2, 
                                    start=180, extent=90, fill=bg_color, outline=bg_color)
            toggle_canvas.create_arc(x2 - 2*radius, y2 - 2*radius, x2, y2, 
                                    start=270, extent=90, fill=bg_color, outline=bg_color)
            
            # Dibujar los rectángulos para conectar los arcos
            toggle_canvas.create_rectangle(x1 + radius, y1, x2 - radius, y2, 
                                         fill=bg_color, outline=bg_color)
            toggle_canvas.create_rectangle(x1, y1 + radius, x2, y2 - radius, 
                                         fill=bg_color, outline=bg_color)
            
            # Crear el círculo indicador
            toggle_canvas.create_oval(
                circle_x-10, 3, 
                circle_x+10, toggle_height-3, 
                fill="white", outline="#e0e0e0", width=1
            )
            
            # Añadir texto ON/OFF
            toggle_canvas.create_text(
                text_x, toggle_height//2, 
                text=text, fill="white", 
                font=("Arial", 9, "bold")
            )
        
        # Función para manejar el clic en el botón
        def toggle_switch(event=None):
            # Cambiar el estado de la variable
            current_state = self.protocol_vars[protocol_id].get()
            self.protocol_vars[protocol_id].set(not current_state)
            
            # Actualizar la apariencia
            update_toggle_appearance()
            
            # Llamar a la función de toggle del protocolo
            self.toggle_protocol(protocol_id, status_badge)
        
        # Vincular eventos de clic
        toggle_canvas.bind("<Button-1>", toggle_switch)
        
        # Configurar la apariencia inicial
        update_toggle_appearance()
        
        # Crear un Checkbutton oculto para mantener la funcionalidad original
        # pero no mostrarlo visualmente
        hidden_toggle = ttk.Checkbutton(
            toggle_container, 
            variable=self.protocol_vars[protocol_id],
            command=update_toggle_appearance,
            style="Invisible.TCheckbutton"
        )
        
        # Configurar un estilo invisible para el checkbutton oculto
        style = ttk.Style()
        style.configure("Invisible.TCheckbutton", 
                      indicatorsize=0,
                      background="#f5f5f5")
        
        # Mantener el estilo original del Switch para compatibilidad
        style.configure("Switch.TCheckbutton",
                       indicatorsize=25,
                       indicatormargin=-12,
                       indicatordiameter=25,
                       fieldbackground="lightgray",
                       padding=8)
        
        style.map("Switch.TCheckbutton",
                  fieldbackground=[("selected", COLOR_SWITCH_ACTIVE), ("!selected", "lightgray")],
                  indicatorforeground=[("selected", COLOR_WHITE), ("!selected", COLOR_WHITE)])
    
    def _create_config_section(self, parent: tk.Frame, protocol_name_short: str, protocol_id: str) -> None:
        """Crea la sección de configuración del protocolo.
        
        Args:
            parent: Frame padre
            protocol_name_short: Nombre corto del protocolo
            protocol_id: Identificador del protocolo
        """
        # Frame para la configuración del protocolo con borde y fondo para destacarlo
        config_frame = tk.Frame(parent, bg=COLOR_WHITE, bd=1, relief="solid", 
                              highlightbackground="#e0e0e0", highlightthickness=1)
        config_frame.pack(fill="x", pady=(5, 0), expand=True)
        
        # Frame para el encabezado de la sección de configuración
        config_header = tk.Frame(config_frame, bg="#f0f0f0", padx=10, pady=5)
        config_header.pack(fill="x")
        
        # Etiqueta para la sección de configuración con icono
        config_icon = tk.Label(config_header, text="⚙️", font=("Arial", 12), bg="#f0f0f0")
        config_icon.pack(side="left", padx=(0, 5))
        
        config_label = tk.Label(config_header, text=f"Configuración de {protocol_name_short}", 
                              font=("Arial", 11, "bold"), bg="#f0f0f0")
        config_label.pack(side="left")
        
        # Frame para el contenido de la configuración
        config_content = tk.Frame(config_frame, bg=COLOR_WHITE, padx=10, pady=10)
        config_content.pack(fill="both", expand=True)
        
        # Área de texto para la configuración con estilo mejorado
        config_text = scrolledtext.ScrolledText(
            config_content, 
            height=6, 
            width=30, 
            font=("Consolas", 9),
            bd=1,
            relief="solid",
            padx=5,
            pady=5,
            bg="#fafafa"
        )
        config_text.pack(fill="both", expand=True)
        
        # Cargar configuración existente si hay
        if self.shared_data['routing_protocols'][protocol_id][CONFIG]:
            config_text.insert("1.0", self.shared_data['routing_protocols'][protocol_id][CONFIG])
        else:
            # Texto de ayuda si no hay configuración
            placeholder = f"# Ingrese la configuración para {protocol_name_short} aquí\n"
            config_text.insert("1.0", placeholder)
        
        # Guardar referencia al widget de configuración
        self.config_widgets[protocol_id] = config_text
        
        # Frame para los botones
        button_frame = tk.Frame(config_content, bg=COLOR_WHITE)
        button_frame.pack(fill="x", pady=(10, 0))
        
        # Botón para limpiar la configuración
        clear_btn = ttk.Button(
            button_frame, 
            text="Limpiar", 
            command=lambda t=config_text: t.delete("1.0", tk.END),
            style="Secondary.TButton"
        )
        clear_btn.pack(side="left")
        
        # Botón para guardar la configuración
        save_btn = ttk.Button(
            button_frame, 
            text="Guardar Configuración", 
            command=lambda p=protocol_id: self.save_protocol_config(p),
            style="Primary.TButton"
        )
        save_btn.pack(side="right")
        
        # Establecer el estado inicial del área de configuración según el estado del interruptor
        if not self.protocol_vars[protocol_id].get():
            config_text.config(state="disabled")
            save_btn.config(state="disabled")
            clear_btn.config(state="disabled")
        
    def toggle_protocol(self, protocol_id: str, status_badge: Optional[tk.Label] = None) -> None:
        """Activa o desactiva un protocolo de enrutamiento.
        
        Actualiza el estado del protocolo en shared_data, actualiza la interfaz visual
        y regenera la vista previa de configuración.
        
        Args:
            protocol_id: Identificador del protocolo a activar/desactivar
            status_badge: Etiqueta que muestra el estado del protocolo (opcional)
            
        Raises:
            KeyError: Si el protocol_id no existe en self.protocol_vars o self.shared_data
            AttributeError: Si status_badge no es un widget válido
        """
        try:
            # Verificar que el protocolo exista
            if protocol_id not in self.protocol_vars:
                raise KeyError(f"Protocolo no reconocido: {protocol_id}")
                
            # Obtener el estado actual del interruptor
            is_enabled = self.protocol_vars[protocol_id].get()
            
            # Actualizar el estado en shared_data
            self.shared_data['routing_protocols'][protocol_id][ENABLED] = is_enabled
            
            # Actualizar el badge de estado si se proporcionó
            if status_badge is not None:
                if is_enabled:
                    status_badge.config(text=TEXT_ENABLED, bg=COLOR_ENABLED, fg=FG_ENABLED)
                else:
                    status_badge.config(text=TEXT_DISABLED, bg=COLOR_DISABLED, fg=FG_DISABLED)
            
            # Habilitar o deshabilitar el área de configuración
            self._update_config_widget_state(protocol_id, is_enabled)
            
            # Actualizar la vista previa
            self.update_preview()
            
        except (KeyError, AttributeError) as e:
            messagebox.showerror("Error", f"Error al cambiar el estado del protocolo: {str(e)}")
    
    def _update_config_widget_state(self, protocol_id: str, is_enabled: bool) -> None:
        """Actualiza el estado de los widgets de configuración según el estado del protocolo.
        
        Args:
            protocol_id: Identificador del protocolo
            is_enabled: Estado de activación del protocolo
        """
        if protocol_id in self.config_widgets:
            # Cambiar el estado del área de texto
            widget_state = "normal" if is_enabled else "disabled"
            self.config_widgets[protocol_id].config(state=widget_state)
            
            # Cambiar el estado de los botones relacionados
            # Buscar el frame de contenido (parent del área de texto)
            content_frame = self.config_widgets[protocol_id].master
            
            # Buscar el frame de botones dentro del frame de contenido
            for child in content_frame.winfo_children():
                if isinstance(child, tk.Frame):
                    # Actualizar el estado de todos los botones en el frame de botones
                    for button in child.winfo_children():
                        if isinstance(button, ttk.Button):
                            button.config(state=widget_state)
        
    def save_protocol_config(self, protocol_id: str) -> bool:
        """Guarda la configuración de un protocolo de enrutamiento.
        
        Obtiene el texto del área de configuración, lo valida y lo guarda en shared_data.
        
        Args:
            protocol_id: Identificador del protocolo
            
        Returns:
            True si la configuración se guardó correctamente, False en caso contrario
            
        Raises:
            KeyError: Si el protocol_id no existe en self.config_widgets
        """
        try:
            # Verificar que el widget de configuración exista
            if protocol_id not in self.config_widgets:
                raise KeyError(f"No se encontró el widget de configuración para {protocol_id}")
                
            # Obtener el texto de configuración
            config_text = self.config_widgets[protocol_id].get("1.0", tk.END).strip()
            
            # Validar la configuración según el protocolo
            validation_result = self._validate_protocol_config(protocol_id, config_text)
            if not validation_result[0]:
                messagebox.showwarning("Advertencia", validation_result[1])
                return False
                
            # Guardar la configuración en shared_data
            self.shared_data['routing_protocols'][protocol_id][CONFIG] = config_text
            
            # Mostrar mensaje de éxito
            messagebox.showinfo(
                "Configuración Guardada", 
                f"La configuración del protocolo {protocol_id.upper()} ha sido guardada."
            )
            
            # Actualizar la vista previa
            self.update_preview()
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar la configuración: {str(e)}")
            return False
    
    def _validate_protocol_config(self, protocol_id: str, config_text: str) -> Tuple[bool, str]:
        """Valida la configuración de un protocolo según reglas específicas.
        
        Args:
            protocol_id: Identificador del protocolo
            config_text: Texto de configuración a validar
            
        Returns:
            Tupla con (es_válido, mensaje_error)
        """
        # Si no hay configuración, es válido (configuración vacía)
        if not config_text:
            return True, ""
            
        # Validaciones específicas por protocolo
        if protocol_id == PROTOCOL_OSPF:
            # Verificar que la configuración de OSPF contenga al menos una definición de área
            if not re.search(r'(network\s+[\d\.]+\s+[\d\.]+\s+area\s+\d+)', config_text):
                return False, "La configuración de OSPF debe incluir al menos una definición de red y área."
                
        elif protocol_id == PROTOCOL_BGP:
            # Verificar que la configuración de BGP contenga un número de sistema autónomo
            if not re.search(r'router\s+bgp\s+\d+', config_text):
                return False, "La configuración de BGP debe incluir un número de sistema autónomo."
                
        # Por defecto, considerar válida la configuración
        return True, ""

    def create_static_routes_tab(self, parent: ttk.Frame) -> None:
        """Crea el contenido de la pestaña de Rutas Estáticas.
        
        Organiza la interfaz para gestionar rutas estáticas con un formulario
        para añadir nuevas rutas y una tabla para visualizar y eliminar las existentes.
        
        Args:
            parent: Frame padre donde se colocarán los elementos
        """
        # Frame principal para la pestaña
        static_routes_frame = ttk.Frame(parent, style="Card.TFrame")
        static_routes_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Crear el formulario para añadir rutas
        self._create_static_route_form(static_routes_frame)
        
        # Crear la tabla de rutas estáticas
        self._create_static_routes_table(static_routes_frame)
    
    def _create_static_route_form(self, parent: ttk.Frame) -> None:
        """Crea el formulario para añadir nuevas rutas estáticas.
        
        Args:
            parent: Frame padre donde se colocará el formulario
        """
        # Frame para el formulario
        form_frame = ttk.Frame(parent, style="Card.TFrame", padding=(15, 15))
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Título del formulario
        form_title = ttk.Label(
            form_frame, 
            text="Añadir Nueva Ruta Estática", 
            font=("Arial", 12, "bold"), 
            background="white"
        )
        form_title.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 10))

        # Campos del formulario - Primera columna
        ttk.Label(form_frame, text="Red de Destino:", background="white").grid(
            row=1, column=0, sticky="w", padx=(0, 5)
        )
        self.dest_net_entry = ttk.Entry(form_frame)
        self.dest_net_entry.grid(row=1, column=1, sticky="ew", padx=5)

        ttk.Label(form_frame, text="Máscara de Subred:", background="white").grid(
            row=2, column=0, sticky="w", padx=(0, 5)
        )
        self.subnet_mask_entry = ttk.Entry(form_frame)
        self.subnet_mask_entry.grid(row=2, column=1, sticky="ew", padx=5)

        # Campos del formulario - Segunda columna
        ttk.Label(form_frame, text="Siguiente Salto:", background="white").grid(
            row=1, column=2, sticky="w", padx=(15, 5)
        )
        self.next_hop_entry = ttk.Entry(form_frame)
        self.next_hop_entry.grid(row=1, column=3, sticky="ew", padx=5)
        
        ttk.Label(form_frame, text="Distancia (opcional):", background="white").grid(
            row=2, column=2, sticky="w", padx=(15, 5)
        )
        self.distance_entry = ttk.Entry(form_frame)
        self.distance_entry.grid(row=2, column=3, sticky="ew", padx=5)

        # Botón para añadir ruta
        add_button = ttk.Button(
            form_frame, 
            text="Añadir Ruta", 
            command=self.add_static_route
        )
        add_button.grid(row=3, column=3, sticky="e", pady=(10, 0))

        # Configurar el comportamiento de redimensionamiento
        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_columnconfigure(3, weight=1)
    
    def _create_static_routes_table(self, parent: ttk.Frame) -> None:
        """Crea la tabla para visualizar y gestionar rutas estáticas.
        
        Args:
            parent: Frame padre donde se colocará la tabla
        """
        # Frame para la tabla
        table_frame = ttk.Frame(parent, style="Card.TFrame", padding=(15, 15))
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Título de la tabla
        table_title = ttk.Label(
            table_frame, 
            text="Rutas Estáticas Configuradas", 
            font=("Arial", 12, "bold"), 
            background="white"
        )
        table_title.pack(anchor="w", pady=(0, 10))

        # Definir columnas de la tabla
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

        # Añadir la tabla al frame
        self.routes_table.pack(fill=tk.BOTH, expand=True)

        # Botón para eliminar ruta seleccionada
        delete_button = ttk.Button(
            table_frame, 
            text="Eliminar Ruta Seleccionada", 
            command=self.delete_static_route
        )
        delete_button.pack(pady=(10, 0), anchor="e")


    def add_static_route(self) -> None:
        """Añade una nueva ruta estática a la tabla y al shared_data.
        
        Valida los campos obligatorios, formatea los datos y actualiza
        tanto la tabla visual como los datos compartidos. Limpia el formulario
        después de añadir la ruta y actualiza la vista previa.
        """
        try:
            # Obtener y validar valores del formulario
            dest = self.dest_net_entry.get().strip()
            mask = self.subnet_mask_entry.get().strip()
            next_hop = self.next_hop_entry.get().strip()
            distance = self.distance_entry.get().strip()
            
            # Validar campos obligatorios
            if not dest or not mask or not next_hop:
                messagebox.showwarning("Campos incompletos", "Los campos Red, Máscara y Siguiente Salto son obligatorios.")
                return
            
            # Validar formato de IP (opcional, se puede implementar)
            
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
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al añadir ruta: {str(e)}")
            
    def _validate_ip_format(self, ip_address: str) -> bool:
        """Valida que una cadena tenga formato de dirección IP.
        
        Args:
            ip_address: La dirección IP a validar
            
        Returns:
            True si el formato es válido, False en caso contrario
        """
        ip_pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
        match = re.match(ip_pattern, ip_address)
        
        if not match:
            return False
            
        # Validar que cada octeto esté entre 0 y 255
        for octet in match.groups():
            if int(octet) > 255:
                return False
                
        return True

    def delete_static_route(self) -> None:
        """Elimina la ruta estática seleccionada de la tabla."""
        selected_items = self.routes_table.selection()
        if not selected_items:
            messagebox.showwarning("Ninguna selección", "Por favor, selecciona al menos una ruta para eliminar.")
            return

        # Confirmación
        if not messagebox.askyesno("Confirmar eliminación", "¿Estás seguro de que quieres eliminar las rutas seleccionadas?"):
            return

        try:
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
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar ruta: {str(e)}")

    def refresh_routes_table(self) -> None:
        """Limpia y vuelve a cargar la tabla de rutas estáticas."""
        try:
            # Limpiar tabla
            for item in self.routes_table.get_children():
                self.routes_table.delete(item)
            
            # Llenar con datos actualizados
            for route in self.shared_data.get('static_routes', []):
                self.routes_table.insert("", tk.END, values=(
                    route.get('dest', ''),
                    route.get('mask', ''),
                    route.get('next_hop', ''),
                    route.get('distance', '')
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar tabla de rutas: {str(e)}")

    def create_preview_section(self, parent: ttk.Frame) -> None:
        """Crea la sección de vista previa de comandos.
        
        Configura un área de texto con desplazamiento para mostrar los comandos
        de configuración generados a partir de los ajustes actuales.
        
        Args:
            parent: Frame padre donde se colocará la sección de vista previa
        """
        # Crear frame contenedor con estilo de tarjeta
        preview_frame = ttk.Frame(parent, style="Card.TFrame", padding=(15, 15))
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título de la sección
        preview_title = ttk.Label(
            preview_frame, 
            text="Vista Previa de Comandos", 
            font=("Arial", 12, "bold"), 
            background=COLOR_WHITE
        )
        preview_title.pack(anchor="w", pady=(0, 10))
        
        # Área de texto con desplazamiento para mostrar los comandos
        self.preview_text = scrolledtext.ScrolledText(
            preview_frame, 
            wrap=tk.WORD, 
            height=10,
            font=("Consolas", 10)  # Fuente monoespaciada para mejor visualización de comandos
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        self.preview_text.config(state=tk.DISABLED)  # Solo lectura
        
        # Botón para copiar comandos al portapapeles
        copy_button = ttk.Button(
            preview_frame,
            text="Copiar Comandos",
            command=self._copy_commands_to_clipboard
        )
        copy_button.pack(pady=(10, 0), anchor="e")
        
        # Actualizar la vista previa inicial
        self.update_preview()

    def _copy_commands_to_clipboard(self) -> None:
        """Copia los comandos actuales al portapapeles del sistema."""
        try:
            # Obtener el contenido actual
            commands_text = self.preview_text.get(1.0, tk.END).strip()
            if not commands_text or commands_text.startswith("# No hay"):
                messagebox.showinfo("Información", "No hay comandos para copiar.")
                return
                
            # Copiar al portapapeles
            self.clipboard_clear()
            self.clipboard_append(commands_text)
            
            messagebox.showinfo("Éxito", "Comandos copiados al portapapeles.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron copiar los comandos: {str(e)}")

    def update_preview(self) -> None:
        """Actualiza la vista previa de comandos basada en la configuración actual.
        
        Genera y muestra los comandos de configuración para los protocolos de
        enrutamiento habilitados y las rutas estáticas configuradas.
        """
        try:
            # Habilitar edición del área de texto
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete(1.0, tk.END)
            
            commands = []
            
            # Generar comandos para protocolos de enrutamiento
            protocol_commands = self._generate_protocol_commands()
            if protocol_commands:
                commands.extend(protocol_commands)
            
            # Generar comandos para rutas estáticas
            static_route_commands = self._generate_static_route_commands()
            if static_route_commands:
                commands.extend(static_route_commands)
            
            # Mostrar comandos en el área de texto
            if commands:
                self.preview_text.insert(tk.END, "\n".join(commands))
            else:
                self.preview_text.insert(tk.END, "# No hay configuración de enrutamiento definida")
                
            # Volver a modo solo lectura
            self.preview_text.config(state=tk.DISABLED)
        except Exception as e:
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, f"# Error al generar vista previa: {str(e)}")
            self.preview_text.config(state=tk.DISABLED)
            print(f"Error en update_preview: {str(e)}")
    
    def _generate_protocol_commands(self) -> List[str]:
        """Genera los comandos para los protocolos de enrutamiento habilitados.
        
        Returns:
            Lista de comandos para los protocolos configurados
        """
        commands = []
        
        try:
            # Verificar que existan los datos de protocolos
            if 'routing_protocols' not in self.shared_data:
                return commands
                
            # Generar comandos para cada protocolo habilitado
            for protocol_id, var in self.protocol_vars.items():
                if not var.get():
                    continue  # Protocolo deshabilitado
                    
                # Verificar que el protocolo exista en shared_data
                if protocol_id not in self.shared_data['routing_protocols']:
                    continue
                    
                protocol_data = self.shared_data['routing_protocols'][protocol_id]
                
                # Generar comandos según el tipo de protocolo
                if protocol_id == PROTOCOL_OSPF:
                    commands.append(f"router ospf {protocol_data.get('process_id', '1')}")
                    for network in protocol_data.get('networks', []):
                        if network.get('network') and network.get('wildcard') and network.get('area'):
                            commands.append(f"  network {network['network']} {network['wildcard']} area {network['area']}")
                
                elif protocol_id == PROTOCOL_BGP:
                    commands.append(f"router bgp {protocol_data.get('as_number', '1')}")
                    for neighbor in protocol_data.get('neighbors', []):
                        if neighbor.get('ip') and neighbor.get('remote_as'):
                            commands.append(f"  neighbor {neighbor['ip']} remote-as {neighbor['remote_as']}")
        except Exception as e:
            print(f"Error al generar comandos de protocolos: {str(e)}")
            
        return commands
    
    def _generate_static_route_commands(self) -> List[str]:
        """Genera los comandos para las rutas estáticas configuradas.
        
        Returns:
            Lista de comandos para las rutas estáticas
        """
        commands = []
        
        try:
            # Verificar que existan rutas estáticas
            if 'static_routes' not in self.shared_data or not self.shared_data['static_routes']:
                return commands
                
            # Generar comando para cada ruta estática
            for route in self.shared_data['static_routes']:
                # Verificar que la ruta tenga los campos requeridos
                if not route.get('dest') or not route.get('mask') or not route.get('next_hop'):
                    continue
                    
                cmd = f"ip route {route['dest']} {route['mask']} {route['next_hop']}"  
                if route.get('distance'):
                    cmd += f" {route['distance']}"
                commands.append(cmd)
        except Exception as e:
            print(f"Error al generar comandos de rutas estáticas: {str(e)}")
            
        return commands

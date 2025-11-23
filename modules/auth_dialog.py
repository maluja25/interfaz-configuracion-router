import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys
import time

# Añadir el directorio modules al path para poder importar router_analyzer
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from router_analyzer.router_analyzer import RouterAnalyzer

class AuthDialog:
    def __init__(self, verbose: bool = False):
        self.root = tk.Tk()
        self.root.title("Router Manager - Conexión")
        self.root.resizable(True, True)
        self.root.configure(bg='#f8f9fa')
        self.root.protocol("WM_DELETE_WINDOW", self.cancel_connection)
        # Flag de salida verbosa (permitido desde CLI)
        self.verbose = bool(verbose)
        
        # Variables de conexión
        self.connection_data = None
        self.saved_credentials = self.load_saved_credentials()
        
        # Centrar ventana
        self.center_window()
        
        # Crear la interfaz
        self.setup_ui()
        
    def center_window(self):
        """Centrar la ventana en la pantalla y ajustar tamaño dinámicamente"""
        self.root.update_idletasks()
        
        # Obtener el tamaño requerido por el contenido
        width = self.root.winfo_reqwidth()
        height = self.root.winfo_reqheight()
        
        # Asegurar un tamaño mínimo
        width = max(width, 500)
        height = max(height, 400)
        
        # Limitar el tamaño máximo para que no exceda la pantalla
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        width = min(width, screen_width - 100)
        height = min(height, screen_height - 100)
        
        # Centrar la ventana
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#f8f9fa')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_label = tk.Label(main_frame, 
                              text="🔧 Router Manager",
                              font=("Arial", 18, "bold"),
                              bg='#f8f9fa',
                              fg='#030213')
        title_label.pack(pady=(0, 10))
        
        subtitle_label = tk.Label(main_frame,
                                 text="Configurar conexión al router",
                                 font=("Arial", 10),
                                 bg='#f8f9fa',
                                 fg='#666666')
        subtitle_label.pack(pady=(0, 20))
        
        # Frame de configuración
        config_frame = tk.Frame(main_frame, bg='white', relief='solid', bd=1)
        config_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Padding interno
        inner_frame = tk.Frame(config_frame, bg='white', padx=20, pady=20)
        inner_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configuración de conexión
        self.create_connection_config(inner_frame)
        
        # Opciones de sesión
        self.create_session_options(inner_frame)
        
        # Botones
        self.create_buttons(main_frame)
        
        # Ajustar tamaño después de crear todos los elementos
        self.root.after(100, self.adjust_window_size)
        
    def adjust_window_size(self):
        """Ajustar el tamaño de la ventana dinámicamente"""
        self.root.update_idletasks()
        
        # Obtener el tamaño requerido por el contenido
        width = self.root.winfo_reqwidth()
        height = self.root.winfo_reqheight()
        
        # Añadir un poco de padding extra
        width += 40
        height += 40
        
        # Asegurar un tamaño mínimo
        width = max(width, 500)
        height = max(height, 400)
        
        # Limitar el tamaño máximo para que no exceda la pantalla
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        width = min(width, screen_width - 100)
        height = min(height, screen_height - 100)
        
        # Centrar la ventana
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        
        # Aplicar el nuevo tamaño
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
    def create_connection_config(self, parent):
        """Crear la sección de configuración de conexión"""
        # Frame principal con grid para mejor organización
        self.main_config_frame = tk.Frame(parent, bg='white')
        self.main_config_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Primera fila: Protocolo y Hostname
        row1_frame = tk.Frame(self.main_config_frame, bg='white')
        row1_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Protocolo
        protocol_frame = tk.Frame(row1_frame, bg='white')
        protocol_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        protocol_label = tk.Label(protocol_frame, text="Protocolo:", bg='white', anchor=tk.W)
        protocol_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.protocol_var = tk.StringVar(value="SSH2")
        protocol_cb = ttk.Combobox(protocol_frame, textvariable=self.protocol_var, 
                                   values=["SSH2", "Telnet", "Serial"], state="readonly", width=10)
        protocol_cb.pack(side=tk.LEFT)
        protocol_cb.bind("<<ComboboxSelected>>", self.on_protocol_change)
        
        # Puerto (para Serial)
        self.serial_port_label = tk.Label(protocol_frame, text="Puerto:", bg='white', anchor=tk.W)
        self.serial_port_var = tk.StringVar(value="COM7")
        self.serial_port_entry = tk.Entry(protocol_frame, textvariable=self.serial_port_var, width=10)
        # Baudios (para Serial)
        self.baudrate_label = tk.Label(protocol_frame, text="Baudios:", bg='white', anchor=tk.W)
        self.baudrate_var = tk.StringVar(value="9600")
        self.baudrate_entry = tk.Entry(protocol_frame, textvariable=self.baudrate_var, width=8)

        # Hostname
        self.hostname_frame = tk.Frame(row1_frame, bg='white')
        self.hostname_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.hostname_label = tk.Label(self.hostname_frame, text="Hostname:", font=("Arial", 10, "bold"), bg='white')
        self.hostname_label.pack(anchor=tk.W)
        self.hostname_var = tk.StringVar(value="192.168.1.1")
        self.hostname_entry = ttk.Entry(self.hostname_frame, textvariable=self.hostname_var, width=20)
        self.hostname_entry.pack(anchor=tk.W, pady=(2, 0))

        # (Eliminado) Selector de fabricante: ahora siempre se autodetecta
        
        # Segunda fila: Puerto
        self.port_frame = tk.Frame(self.main_config_frame, bg='white')
        self.port_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.net_port_label = tk.Label(self.port_frame, text="Puerto:", font=("Arial", 10, "bold"), bg='white')
        self.net_port_label.pack(anchor=tk.W)
        self.port_var = tk.StringVar(value="22")
        self.net_port_entry = ttk.Entry(self.port_frame, textvariable=self.port_var, width=10)
        self.net_port_entry.pack(anchor=tk.W, pady=(2, 0))
        
        # Credenciales
        self.cred_frame = tk.Frame(self.main_config_frame, bg='white')
        self.cred_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(self.cred_frame, text="Credenciales:", font=("Arial", 10, "bold"), bg='white').pack(anchor=tk.W)
        
        # Frame para radio buttons y campos
        cred_options_frame = tk.Frame(self.cred_frame, bg='white')
        cred_options_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Usuario y contraseña
        user_frame = tk.Frame(cred_options_frame, bg='white')
        user_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 20))
        
        self.use_username = tk.BooleanVar(value=True)
        user_radio = tk.Radiobutton(user_frame, text="Usuario:", variable=self.use_username, 
                                   value=True, bg='white', command=self.toggle_credentials)
        user_radio.pack(anchor=tk.W)
        
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(user_frame, textvariable=self.username_var, width=18)
        username_entry.pack(anchor=tk.W, pady=(2, 0))

        tk.Label(user_frame, text="Contraseña:", bg='white').pack(anchor=tk.W, pady=(8, 0))
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(user_frame, textvariable=self.password_var, width=18, show='*')
        self.password_entry.pack(anchor=tk.W, pady=(2, 0))
        
        # Credenciales guardadas
        saved_frame = tk.Frame(cred_options_frame, bg='white')
        saved_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        saved_radio = tk.Radiobutton(saved_frame, text="Credenciales guardadas:", 
                                    variable=self.use_username, value=False, bg='white', 
                                    command=self.toggle_credentials)
        saved_radio.pack(anchor=tk.W)
        
        self.saved_creds_var = tk.StringVar()
        self.saved_combo = ttk.Combobox(saved_frame, textvariable=self.saved_creds_var, 
                                  values=list(self.saved_credentials.keys()), 
                                  state="readonly", width=18)
        self.saved_combo.pack(anchor=tk.W, pady=(2, 0))
        # Al seleccionar credencial guardada, rellenar automáticamente el Hostname
        try:
            self.saved_combo.bind("<<ComboboxSelected>>", self.on_saved_credential_selected)
        except Exception:
            pass
        
        # Métodos de autenticación
        self.auth_frame = tk.LabelFrame(self.main_config_frame, text="Métodos de Autenticación", 
                                  font=("Arial", 10, "bold"), bg='white')
        self.auth_frame.pack(fill=tk.X, pady=(10, 0))
        
        auth_inner = tk.Frame(self.auth_frame, bg='white')
        auth_inner.pack(fill=tk.X, padx=10, pady=8)
        
        self.auth_methods = {
            'password': tk.BooleanVar(value=True),
            'public_key': tk.BooleanVar(value=True),
            'keyboard_interactive': tk.BooleanVar(value=True)
        }
        
        auth_items = [
            ('password', 'Contraseña'),
            ('public_key', 'Clave Pública'),
            ('keyboard_interactive', 'Interactivo por Teclado')
        ]
        
        # Organizar en una sola fila
        for i, (key, label) in enumerate(auth_items):
            cb = tk.Checkbutton(auth_inner, text=label, variable=self.auth_methods[key], 
                               bg='white', anchor=tk.W)
            cb.pack(side=tk.LEFT, padx=(0, 20))
            
    def create_session_options(self, parent):
        """Crear las opciones de sesión"""
        options_frame = tk.Frame(parent, bg='white')
        options_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.session_options = {
            'show_on_startup': tk.BooleanVar(value=False),
            'save_session': tk.BooleanVar(value=False),
            'open_in_tab': tk.BooleanVar(value=True)
        }

        # Modo rápido
        self.fast_mode_var = tk.BooleanVar(value=True)
        fast_cb = tk.Checkbutton(options_frame, text='Acelerar análisis (modo rápido)',
                                 variable=self.fast_mode_var, bg='white', anchor=tk.W)
        fast_cb.pack(side=tk.LEFT, padx=(0, 20))

        options = [
            ('show_on_startup', 'Mostrar conexión rápida al iniciar'),
            ('save_session', 'Guardar sesión'),
            ('open_in_tab', 'Abrir en nueva pestaña')
        ]
        
        # Organizar en una sola fila para ahorrar espacio
        for i, (key, label) in enumerate(options):
            cb = tk.Checkbutton(options_frame, text=label, variable=self.session_options[key], 
                               bg='white', anchor=tk.W)
            cb.pack(side=tk.LEFT, padx=(0, 20))
            
    def create_buttons(self, parent):
        """Crear los botones de acción"""
        button_frame = tk.Frame(parent, bg='#f8f9fa')
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Botón Cancelar
        cancel_btn = tk.Button(button_frame, text="Cancelar", 
                              command=self.cancel_connection,
                              bg='#6c757d', fg='white', font=("Arial", 10),
                              relief=tk.FLAT, padx=20, pady=8)
        cancel_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Botón Conectar
        connect_btn = tk.Button(button_frame, text="Conectar", 
                               command=self.connect,
                               bg='#007bff', fg='white', font=("Arial", 10, "bold"),
                               relief=tk.FLAT, padx=20, pady=8)
        connect_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Botón Guardar Credenciales
        save_btn = tk.Button(button_frame, text="Guardar Credenciales", 
                            command=self.save_credentials,
                            bg='#28a745', fg='white', font=("Arial", 10),
                            relief=tk.FLAT, padx=15, pady=8)
        save_btn.pack(side=tk.LEFT)
        
    def on_protocol_change(self, event=None):
        """Cambiar el puerto cuando se cambia el protocolo"""
        protocol = self.protocol_var.get()
        if protocol == "SSH2":
            self.port_var.set("22")
            # Ocultar controles de puerto serial
            self.serial_port_label.pack_forget()
            self.serial_port_entry.pack_forget()
            self.baudrate_label.pack_forget()
            self.baudrate_entry.pack_forget()
            # Mostrar campo de hostname y puerto de red
            self.port_frame.pack_forget()
            self.port_frame.pack(fill=tk.X, pady=(0, 10), before=self.cred_frame)
            if not self.hostname_frame.winfo_ismapped():
                self.hostname_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        elif protocol == "Telnet":
            self.port_var.set("23")
            # Ocultar controles de puerto serial
            self.serial_port_label.pack_forget()
            self.serial_port_entry.pack_forget()
            self.baudrate_label.pack_forget()
            self.baudrate_entry.pack_forget()
            # Mostrar campo de hostname y puerto de red
            self.port_frame.pack_forget()
            self.port_frame.pack(fill=tk.X, pady=(0, 10), before=self.cred_frame)
            if not self.hostname_frame.winfo_ismapped():
                self.hostname_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        elif protocol == "Serial":
            self.serial_port_var.set("COM7")
            # Mostrar controles de puerto serial
            self.serial_port_label.pack(side=tk.LEFT, padx=(10, 5))
            self.serial_port_entry.pack(side=tk.LEFT)
            self.baudrate_label.pack(side=tk.LEFT, padx=(10, 5))
            self.baudrate_entry.pack(side=tk.LEFT)
            # Ocultar campo de hostname y puerto de red
            if self.port_frame.winfo_ismapped():
                self.port_frame.pack_forget()
            if self.hostname_frame.winfo_ismapped():
                self.hostname_frame.pack_forget()

    def on_saved_credential_selected(self, event=None):
        """Al elegir una credencial guardada, aplicar protocolo, host y puerto."""
        try:
            sel = self.saved_creds_var.get()
            cred = self.saved_credentials.get(sel, {})
            if not cred:
                return
            proto = cred.get('protocol', self.protocol_var.get())
            # Aplicar protocolo y ajustar UI
            if proto:
                self.protocol_var.set(proto)
                try:
                    self.on_protocol_change()
                except Exception:
                    pass
            # Host y puertos según protocolo
            if proto == 'Serial':
                sp = cred.get('port', '')
                if sp:
                    try:
                        self.serial_port_var.set(sp)
                    except Exception:
                        pass
                bd = cred.get('baudrate', '')
                if bd:
                    self.baudrate_var.set(str(bd))
            else:
                host = cred.get('hostname', '')
                if host:
                    self.hostname_var.set(host)
                p = cred.get('port', '')
                if p:
                    self.port_var.set(str(p))
        except Exception:
            pass

    def toggle_credentials(self):
        """Alternar entre usuario y credenciales guardadas"""
        if self.use_username.get():
            self.username_var.set("")
        else:
            self.saved_creds_var.set("")
            
    def load_saved_credentials(self):
        """Cargar credenciales guardadas desde archivo"""
        try:
            if os.path.exists('saved_credentials.json'):
                with open('saved_credentials.json', 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}
        
    def save_credentials(self):
        """Guardar credenciales incluyendo puerto y permitiendo usuario/contraseña vacíos."""
        protocol = self.protocol_var.get()
        # Validación mínima: host para SSH/Telnet; puerto serial para Serial
        if protocol != 'Serial' and not self.hostname_var.get():
            messagebox.showwarning("Error", "Por favor ingresa el hostname")
            return
        if protocol == 'Serial' and not self.serial_port_var.get():
            messagebox.showwarning("Error", "Por favor ingresa el puerto serial (ej. COM7)")
            return

        # Clave legible y única: host:puerto (o COM + baudrate para Serial), o host_usuario si hay usuario
        hostname = self.hostname_var.get().strip()
        if protocol == 'Serial':
            port_value = self.serial_port_var.get().strip()
        else:
            # Mantener tipo int para puertos de red
            port_value = self.port_var.get()
        username = self.username_var.get().strip()
        cred_name = f"{hostname}_{username}" if username else (f"{hostname}:{port_value}" if hostname else f"{protocol}:{port_value}")

        credentials = {
            'hostname': hostname,
            'port': port_value,
            'protocol': protocol,
            'username': username,
            'password': self.password_var.get(),
            'auth_methods': {k: v.get() for k, v in self.auth_methods.items()},
            'fast_mode': self.fast_mode_var.get(),
            # Traer running-config en el batch inicial para evitar una segunda pasada
            'prefetch_running_config': True,
            'baudrate': self.baudrate_var.get() if protocol == 'Serial' else ''
        }

        self.saved_credentials[cred_name] = credentials

        try:
            with open('saved_credentials.json', 'w') as f:
                json.dump(self.saved_credentials, f, indent=2)
            # Actualizar combo sin reiniciar el diálogo
            try:
                self.saved_combo['values'] = list(self.saved_credentials.keys())
                self.saved_creds_var.set(cred_name)
            except Exception:
                pass
            messagebox.showinfo("Éxito", "Credenciales guardadas correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
            
    def connect(self):
        """Establecer conexión y analizar router"""
        # Validar campos requeridos
        protocol = self.protocol_var.get()
        if protocol == "Serial":
            if not self.serial_port_var.get():
                messagebox.showerror("Error", "Por favor ingresa el puerto serial (ej. COM7)")
                return
        else:
            if not self.hostname_var.get():
                messagebox.showerror("Error", "Por favor ingresa el hostname")
                return
            
        if self.use_username.get():
            # Permitir Telnet sin usuario/contraseña
            if protocol != "Telnet" and not self.username_var.get():
                messagebox.showerror("Error", "Por favor ingresa el nombre de usuario")
                return
            if protocol != "Telnet" and not self.password_var.get():
                messagebox.showerror("Error", "Por favor ingresa la contraseña")
                return
            
        if not self.use_username.get() and not self.saved_creds_var.get():
            messagebox.showerror("Error", "Por favor selecciona credenciales guardadas")
            return
            
        # Preparar datos de conexión
        self.connection_data = {
            'protocol': protocol,
            'hostname': self.hostname_var.get() if protocol != "Serial" else "",
            'port': self.serial_port_var.get() if protocol == "Serial" else self.port_var.get(),
            'use_username': self.use_username.get(),
            'username': self.username_var.get(),
            'password': self.password_var.get() if self.use_username.get() else '',
            'saved_credentials': self.saved_creds_var.get(),
            'auth_methods': {k: v.get() for k, v in self.auth_methods.items()},
            'session_options': {k: v.get() for k, v in self.session_options.items()},
            'fast_mode': self.fast_mode_var.get(),
            # Traer running-config en el batch inicial para evitar segunda pasada
            'prefetch_running_config': True,
            'baudrate': self.baudrate_var.get() if protocol == 'Serial' else '',
            'verbose': self.verbose,
        }
        
        # Si usa credenciales guardadas, fusionar sin sobrescribir protocolo/objetivo actual
        if not self.use_username.get() and self.saved_creds_var.get():
            saved_cred = self.saved_credentials.get(self.saved_creds_var.get())
            if saved_cred:
                # Preservar selección actual del usuario
                selected_protocol = self.connection_data.get('protocol', 'SSH2')
                selected_hostname = self.connection_data.get('hostname', '')
                selected_port = self.connection_data.get('port', '')
                selected_baudrate = self.connection_data.get('baudrate', '')

                # Copiar solo campos de credenciales/ajustes no críticos
                for key in ('username', 'password', 'auth_methods', 'session_options', 'fast_mode', 'prefetch_running_config'):
                    if key in saved_cred:
                        if key == 'prefetch_running_config':
                            # No bajar el valor por defecto (True). Solo activar si credencial lo tenía en True.
                            if bool(saved_cred.get(key)):
                                self.connection_data[key] = True
                        else:
                            self.connection_data[key] = saved_cred[key]

                # Restaurar siempre la selección actual del usuario para evitar inconsistencias
                self.connection_data['protocol'] = selected_protocol
                self.connection_data['hostname'] = selected_hostname if selected_protocol != 'Serial' else ''
                self.connection_data['port'] = selected_port
                self.connection_data['baudrate'] = selected_baudrate if selected_protocol == 'Serial' else ''
                # Mantener el valor de prefetch según credenciales guardadas o por defecto (True)
        
        # Mostrar ventana de análisis
        self.show_analysis_window()
    
    def show_analysis_window(self):
        """Mostrar ventana de análisis del router"""
        # Crear ventana de análisis
        analysis_window = tk.Toplevel(self.root)
        analysis_window.title("Analizando Router...")
        analysis_window.geometry("500x300")
        analysis_window.resizable(False, False)
        analysis_window.configure(bg='#f8f9fa')
        
        # Centrar ventana
        analysis_window.transient(self.root)
        analysis_window.grab_set()
        
        x = (analysis_window.winfo_screenwidth() // 2) - (500 // 2)
        y = (analysis_window.winfo_screenheight() // 2) - (300 // 2)
        analysis_window.geometry(f"500x300+{x}+{y}")
        
        # Frame principal
        main_frame = tk.Frame(analysis_window, bg='#f8f9fa')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_label = tk.Label(main_frame, 
                              text="🔍 Analizando Router",
                              font=("Arial", 16, "bold"),
                              bg='#f8f9fa',
                              fg='#030213')
        title_label.pack(pady=(0, 20))
        
        # Información de conexión
        target_info = self.connection_data['hostname'] if self.connection_data['protocol'] != 'Serial' else self.connection_data['port']
        info_label = tk.Label(main_frame,
                             text=f"Conectando a {target_info} via {self.connection_data['protocol']}",
                             font=("Arial", 10),
                             bg='#f8f9fa',
                             fg='#666666')
        info_label.pack(pady=(0, 20))
        
        # Barra de progreso
        progress_frame = tk.Frame(main_frame, bg='#f8f9fa')
        progress_frame.pack(fill=tk.X, pady=(0, 20))
        
        progress_label = tk.Label(progress_frame, text="Ejecutando comandos...", 
                                 font=("Arial", 10), bg='#f8f9fa')
        progress_label.pack()
        
        progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        progress_bar.pack(fill=tk.X, pady=(10, 0))
        progress_bar.start()
        
        # Lista de comandos
        commands_frame = tk.Frame(main_frame, bg='#f8f9fa')
        commands_frame.pack(fill=tk.BOTH, expand=True)
        
        commands_label = tk.Label(commands_frame, text="Comandos ejecutándose:", 
                                 font=("Arial", 10, "bold"), bg='#f8f9fa')
        commands_label.pack(anchor=tk.W)
        
        commands_listbox = tk.Listbox(commands_frame, height=8, font=("Courier", 9))
        commands_listbox.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Comandos a ejecutar (se determinarán dinámicamente según el dispositivo)
        commands = [
            'Comandos de detección de dispositivo',
            'Comandos específicos del fabricante',
            'Análisis de configuración',
            'Recopilación de datos'
        ]
        
        # Iniciar análisis en un hilo separado
        self.start_analysis(analysis_window, commands_listbox, commands, progress_bar)
    
    def start_analysis(self, window, listbox, commands, progress_bar):
        """Iniciar el análisis del router"""
        try:
            # Crear analizador
            analyzer = RouterAnalyzer(self.connection_data)
            fast = bool(self.connection_data.get('fast_mode', True))
            def _sleep_short(default_s: float = 0.2):
                try:
                    if fast:
                        time.sleep(0.02)
                    else:
                        time.sleep(default_s)
                except Exception:
                    pass
            
            # Mostrar inicio del análisis
            listbox.insert(tk.END, "🚀 Iniciando análisis del router...")
            window.update()
            _sleep_short()
            
            # Simular conexión con tiempos realistas
            if analyzer.connect():
                listbox.insert(tk.END, "✅ Conectado al router exitosamente")
                window.update()
                _sleep_short()

                # Detectar fabricante inmediatamente (conect().vendor_hint ya está establecido)
                listbox.insert(tk.END, "🔎 Detectando fabricante...")
                window.update()
                _sleep_short()
                vendor_label = (analyzer.vendor or self.connection_data.get('vendor_hint') or 'Desconocido').upper()
                listbox.insert(tk.END, f"📊 Dispositivo detectado: {vendor_label}")
                window.update()
                _sleep_short()

                # Mostrar progreso de comandos específicos del fabricante
                listbox.insert(tk.END, "📋 Ejecutando comandos de análisis...")
                window.update()
                _sleep_short()

                # Ejecutar análisis real (usará vendor_hint para comandos del vendor)
                analysis_data = analyzer.analyze_router()
                parsed_data = analyzer.parse_analysis_data(analysis_data)
                
                listbox.insert(tk.END, f"📈 Comandos ejecutados: {len(analysis_data.get('commands_executed', []))}")
                window.update()
                _sleep_short()
                
                listbox.insert(tk.END, f"🔍 Interfaces encontradas: {len(parsed_data.get('interfaces', []))}")
                window.update()
                _sleep_short()
                
                listbox.insert(tk.END, f"🌐 VRFs encontradas: {len(parsed_data.get('vrfs', []))}")
                window.update()
                _sleep_short()
                
                # Análisis completado
                listbox.insert(tk.END, "")
                listbox.insert(tk.END, "✅ Análisis completado exitosamente")
                window.update()
                
                # Guardar datos en connection_data
                self.connection_data['analysis_data'] = analysis_data
                self.connection_data['parsed_data'] = parsed_data
                
                # Detener la barra de progreso antes de cerrar la ventana
                try:
                    progress_bar.stop()
                except Exception:
                    pass
                
                # Cerrar ventana de análisis después de 1 segundo
                window.after(300, lambda: self.close_analysis_window(window))
                
            else:
                listbox.insert(tk.END, "❌ Error al conectar al router")
                window.update()
                try:
                    time.sleep(0.5 if fast else 1.5)
                except Exception:
                    pass
                try:
                    progress_bar.stop()
                except Exception:
                    pass
                window.after(500 if fast else 1500, lambda: self.close_analysis_window(window))
                
        except Exception as e:
            listbox.insert(tk.END, f"❌ Error: {str(e)}")
            window.update()
            try:
                time.sleep(0.5 if fast else 1.5)
            except Exception:
                pass
            try:
                progress_bar.stop()
            except Exception:
                pass
            window.after(500 if fast else 1500, lambda: self.close_analysis_window(window))
    
    def close_analysis_window(self, window):
        """Cerrar ventana de análisis y continuar"""
        window.destroy()
        self.root.quit()
        
    def cancel_connection(self):
        """Cancelar conexión"""
        self.connection_data = None
        self.root.quit()
        
    def show(self):
        """Mostrar el diálogo y retornar los datos de conexión"""
        self.root.mainloop()
        try:
            if self.root:
                self.root.destroy()
        except tk.TclError:
            pass
        return self.connection_data

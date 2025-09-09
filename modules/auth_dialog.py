import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys
import time

# Añadir el directorio modules al path para poder importar router_analyzer
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from router_analyzer import RouterAnalyzer

class AuthDialog:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Router Manager - Conexión")
        self.root.resizable(True, True)
        self.root.configure(bg='#f8f9fa')
        
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
        main_config_frame = tk.Frame(parent, bg='white')
        main_config_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Primera fila: Protocolo y Hostname
        row1_frame = tk.Frame(main_config_frame, bg='white')
        row1_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Protocolo
        protocol_frame = tk.Frame(row1_frame, bg='white')
        protocol_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        tk.Label(protocol_frame, text="Protocolo:", font=("Arial", 10, "bold"), bg='white').pack(anchor=tk.W)
        self.protocol_var = tk.StringVar(value="SSH2")
        protocol_combo = ttk.Combobox(protocol_frame, textvariable=self.protocol_var, 
                                     values=["SSH2", "Telnet"], state="readonly", width=15)
        protocol_combo.pack(anchor=tk.W, pady=(2, 0))
        protocol_combo.bind('<<ComboboxSelected>>', self.on_protocol_change)
        
        # Hostname
        hostname_frame = tk.Frame(row1_frame, bg='white')
        hostname_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        tk.Label(hostname_frame, text="Hostname:", font=("Arial", 10, "bold"), bg='white').pack(anchor=tk.W)
        self.hostname_var = tk.StringVar(value="192.168.1.1")
        hostname_entry = ttk.Entry(hostname_frame, textvariable=self.hostname_var, width=20)
        hostname_entry.pack(anchor=tk.W, pady=(2, 0))
        
        # Segunda fila: Puerto
        port_frame = tk.Frame(main_config_frame, bg='white')
        port_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(port_frame, text="Puerto:", font=("Arial", 10, "bold"), bg='white').pack(anchor=tk.W)
        self.port_var = tk.StringVar(value="22")
        port_entry = ttk.Entry(port_frame, textvariable=self.port_var, width=10)
        port_entry.pack(anchor=tk.W, pady=(2, 0))
        
        # Credenciales
        cred_frame = tk.Frame(main_config_frame, bg='white')
        cred_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(cred_frame, text="Credenciales:", font=("Arial", 10, "bold"), bg='white').pack(anchor=tk.W)
        
        # Frame para radio buttons y campos
        cred_options_frame = tk.Frame(cred_frame, bg='white')
        cred_options_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Usuario
        user_frame = tk.Frame(cred_options_frame, bg='white')
        user_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 20))
        
        self.use_username = tk.BooleanVar(value=True)
        user_radio = tk.Radiobutton(user_frame, text="Usuario:", variable=self.use_username, 
                                   value=True, bg='white', command=self.toggle_credentials)
        user_radio.pack(anchor=tk.W)
        
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(user_frame, textvariable=self.username_var, width=18)
        username_entry.pack(anchor=tk.W, pady=(2, 0))
        
        # Credenciales guardadas
        saved_frame = tk.Frame(cred_options_frame, bg='white')
        saved_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        saved_radio = tk.Radiobutton(saved_frame, text="Credenciales guardadas:", 
                                    variable=self.use_username, value=False, bg='white', 
                                    command=self.toggle_credentials)
        saved_radio.pack(anchor=tk.W)
        
        self.saved_creds_var = tk.StringVar()
        saved_combo = ttk.Combobox(saved_frame, textvariable=self.saved_creds_var, 
                                  values=list(self.saved_credentials.keys()), 
                                  state="readonly", width=18)
        saved_combo.pack(anchor=tk.W, pady=(2, 0))
        
        # Métodos de autenticación
        auth_frame = tk.LabelFrame(main_config_frame, text="Métodos de Autenticación", 
                                  font=("Arial", 10, "bold"), bg='white')
        auth_frame.pack(fill=tk.X, pady=(10, 0))
        
        auth_inner = tk.Frame(auth_frame, bg='white')
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
        elif protocol == "Telnet":
            self.port_var.set("23")
    
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
        """Guardar las credenciales actuales"""
        if not self.username_var.get():
            messagebox.showwarning("Error", "Por favor ingresa un nombre de usuario")
            return
            
        cred_name = f"{self.hostname_var.get()}_{self.username_var.get()}"
        
        credentials = {
            'hostname': self.hostname_var.get(),
            'port': self.port_var.get(),
            'protocol': self.protocol_var.get(),
            'username': self.username_var.get(),
            'auth_methods': {k: v.get() for k, v in self.auth_methods.items()}
        }
        
        self.saved_credentials[cred_name] = credentials
        
        try:
            with open('saved_credentials.json', 'w') as f:
                json.dump(self.saved_credentials, f, indent=2)
            messagebox.showinfo("Éxito", "Credenciales guardadas correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
            
    def connect(self):
        """Establecer conexión y analizar router"""
        # Validar campos requeridos
        if not self.hostname_var.get():
            messagebox.showerror("Error", "Por favor ingresa el hostname")
            return
            
        if self.use_username.get() and not self.username_var.get():
            messagebox.showerror("Error", "Por favor ingresa el nombre de usuario")
            return
            
        if not self.use_username.get() and not self.saved_creds_var.get():
            messagebox.showerror("Error", "Por favor selecciona credenciales guardadas")
            return
            
        # Preparar datos de conexión
        self.connection_data = {
            'protocol': self.protocol_var.get(),
            'hostname': self.hostname_var.get(),
            'port': self.port_var.get(),
            'use_username': self.use_username.get(),
            'username': self.username_var.get(),
            'saved_credentials': self.saved_creds_var.get(),
            'auth_methods': {k: v.get() for k, v in self.auth_methods.items()},
            'session_options': {k: v.get() for k, v in self.session_options.items()}
        }
        
        # Si usa credenciales guardadas, cargar los datos
        if not self.use_username.get() and self.saved_creds_var.get():
            saved_cred = self.saved_credentials.get(self.saved_creds_var.get())
            if saved_cred:
                self.connection_data.update(saved_cred)
        
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
        info_label = tk.Label(main_frame,
                             text=f"Conectando a {self.connection_data['hostname']} via {self.connection_data['protocol']}",
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
            
            # Mostrar inicio del análisis
            listbox.insert(tk.END, "🚀 Iniciando análisis del router...")
            window.update()
            time.sleep(1)
            
            # Simular conexión con tiempos realistas
            if analyzer.connect():
                listbox.insert(tk.END, "✅ Conectado al router exitosamente")
                window.update()
                time.sleep(1)
                
                # Mostrar progreso de comandos
                listbox.insert(tk.END, "📋 Ejecutando comandos de análisis...")
                window.update()
                time.sleep(1)
                
                # Ejecutar análisis real
                analysis_data = analyzer.analyze_router()
                parsed_data = analyzer.parse_analysis_data(analysis_data)
                
                # Mostrar resultados
                listbox.insert(tk.END, f"📊 Dispositivo detectado: {analysis_data.get('device_type', 'Desconocido').upper()}")
                window.update()
                time.sleep(1)
                
                listbox.insert(tk.END, f"📈 Comandos ejecutados: {len(analysis_data.get('commands_executed', []))}")
                window.update()
                time.sleep(1)
                
                listbox.insert(tk.END, f"🔍 Interfaces encontradas: {len(parsed_data.get('interfaces', []))}")
                window.update()
                time.sleep(1)
                
                listbox.insert(tk.END, f"🌐 VRFs encontradas: {len(parsed_data.get('vrfs', []))}")
                window.update()
                time.sleep(1)
                
                # Análisis completado
                listbox.insert(tk.END, "")
                listbox.insert(tk.END, "✅ Análisis completado exitosamente")
                window.update()
                
                # Guardar datos en connection_data
                self.connection_data['analysis_data'] = analysis_data
                self.connection_data['parsed_data'] = parsed_data
                
                # Cerrar ventana de análisis después de 3 segundos
                window.after(3000, lambda: self.close_analysis_window(window))
                
            else:
                listbox.insert(tk.END, "❌ Error al conectar al router")
                window.update()
                time.sleep(2)
                window.after(2000, lambda: self.close_analysis_window(window))
                
        except Exception as e:
            listbox.insert(tk.END, f"❌ Error: {str(e)}")
            window.update()
            time.sleep(2)
            window.after(2000, lambda: self.close_analysis_window(window))
    
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
        self.root.destroy()
        return self.connection_data

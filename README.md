# Router Manager - Interfaz de Configuración

Aplicación de gestión de routers industriales desarrollada en Python con tkinter.

## 🛠️ Instalación

### Prerrequisitos
- Python 3.8 o superior
- pip (incluido con Python)

### Configuración del Entorno

1. **Clonar o descargar el proyecto**
   ```bash
   cd "Interfaz de Configuración de Router"
   ```

2. **Crear y activar entorno virtual**
   
   **En Windows (usando el archivo batch):**
   ```bash
   activate_env.bat
   ```
   
   **En Windows (manualmente):**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
   
   **En macOS/Linux:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Uso

### Ejecutar la aplicación
```bash
python main.py
```

### Características principales
- ✅ Interfaz gráfica intuitiva con tkinter
- 🌐 Configuración de interfaces de red
- 🔀 Gestión de enrutamiento (OSPF, BGP)
- 📚 Configuración de VRF (Virtual Routing and Forwarding)
- 📈 Monitoreo en tiempo real
- 💻 Interfaz de comandos integrada
- 🔐 Conexión SSH y Telnet

### Estructura del proyecto
```
├── main.py                 # Aplicación principal
├── modules/                # Módulos de la aplicación
│   ├── auth_dialog.py      # Diálogo de autenticación
│   ├── dashboard.py        # Panel principal
│   ├── interface_config.py # Configuración de interfaces
│   ├── routing_config.py   # Enrutamiento
│   ├── monitoring.py       # Monitoreo del sistema
│   └── command_interface.py # Interfaz de comandos
├── requirements.txt        # Dependencias del proyecto
├── activate_env.bat        # Script de activación (Windows)
└── README.md              # Este archivo
```

## 📋 Dependencias principales

- **paramiko**: Para conexiones SSH seguras
- **tkinter**: Interfaz gráfica (incluido con Python)
- **telnetlib3**: Para conexiones Telnet

## 📝 Notas

- La aplicación incluye datos de simulación para demostración
- Para uso en producción, configure las credenciales de acceso apropiadas
- Asegúrese de que el router objetivo tenga SSH o Telnet habilitado

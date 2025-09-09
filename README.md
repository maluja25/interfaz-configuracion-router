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
- 🔀 Gestión de protocolos de enrutamiento (OSPF, BGP)
- 📚 Configuración de VRF (Virtual Routing and Forwarding)
- 🏠 Gestión de servicios DHCP
- 🏷️ Configuración de VLANs
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
│   ├── routing_config.py   # Protocolos de enrutamiento
│   ├── vrf_config.py       # Configuración VRF
│   ├── dhcp_config.py      # Configuración DHCP
│   ├── vlan_config.py      # Configuración VLAN
│   ├── monitoring.py       # Monitoreo del sistema
│   ├── command_interface.py # Interfaz de comandos
│   └── router_analyzer.py  # Analizador de configuración
├── requirements.txt        # Dependencias del proyecto
├── activate_env.bat        # Script de activación (Windows)
└── README.md              # Este archivo
```

## 📋 Dependencias principales

- **paramiko**: Para conexiones SSH seguras
- **tkinter**: Interfaz gráfica (incluido con Python)
- **telnetlib**: Para conexiones Telnet (incluido con Python)

### Dependencias de desarrollo (opcionales)
- **pytest**: Para pruebas unitarias
- **black**: Formateador de código Python
- **flake8**: Linter para calidad de código
- **colorlog**: Logging con colores
- **pyyaml**: Manejo de archivos de configuración

## 🔧 Desarrollo

### Formatear código
```bash
black .
```

### Verificar calidad del código
```bash
flake8 .
```

### Ejecutar pruebas
```bash
pytest
```

## 📝 Notas

- La aplicación incluye datos de simulación para demostración
- Para uso en producción, configure las credenciales de acceso apropiadas
- Asegúrese de que el router objetivo tenga SSH o Telnet habilitado

## 🎯 Funcionalidades por módulo

### Dashboard
- Vista general del estado del router
- Estadísticas de interfaces
- Información de protocolos de enrutamiento

### Configuración de Interfaces
- Gestión de interfaces físicas y virtuales
- Configuración de direcciones IP
- Estados administrativos

### Protocolos de Enrutamiento
- Configuración OSPF
- Configuración BGP
- Rutas estáticas

### VRF (Virtual Routing and Forwarding)
- Creación y gestión de VRFs
- Asignación de interfaces a VRFs
- Configuración de Route Distinguishers

### DHCP
- Configuración de pools DHCP
- Gestión de reservas
- Opciones DHCP personalizadas

### VLANs
- Creación y configuración de VLANs
- Asignación a interfaces
- Configuración de trunk y access ports

### Monitoreo
- Estadísticas en tiempo real
- Logs del sistema
- Utilización de recursos

### Interfaz de Comandos
- Ejecución de comandos CLI
- Historial de comandos
- Análisis de salidas

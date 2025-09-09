import tkinter as tk
from tkinter import ttk, messagebox
import random
from datetime import datetime, timedelta

class MonitoringFrame(tk.Frame):
    def __init__(self, parent, shared_data):
        super().__init__(parent, bg='#ffffff')
        self.shared_data = shared_data
        
        # Datos de monitoreo simulados
        self.interface_stats = [
            {
                'name': 'GigabitEthernet0/0/1',
                'status': 'up',
                'in_octets': '2,453,892,114',
                'out_octets': '1,892,337,445',
                'in_packets': '3,445,221',
                'out_packets': '2,887,334',
                'in_errors': '0',
                'out_errors': '0',
                'crc_errors': '0',
                'collisions': '0',
                'utilization': 35,
                'bandwidth': '1000 Mbps'
            },
            {
                'name': 'GigabitEthernet0/0/2',
                'status': 'up',
                'in_octets': '1,234,567,890',
                'out_octets': '987,654,321',
                'in_packets': '1,876,543',
                'out_packets': '1,543,210',
                'in_errors': '2',
                'out_errors': '0',
                'crc_errors': '1',
                'collisions': '0',
                'utilization': 22,
                'bandwidth': '1000 Mbps'
            },
            {
                'name': 'Serial0/1/0',
                'status': 'up',
                'in_octets': '445,782,361',
                'out_octets': '523,891,247',
                'in_packets': '892,445',
                'out_packets': '934,567',
                'in_errors': '0',
                'out_errors': '0',
                'crc_errors': '0',
                'collisions': '0',
                'utilization': 78,
                'bandwidth': '1544 Kbps'
            },
            {
                'name': 'GigabitEthernet0/0/3',
                'status': 'down',
                'in_octets': '0',
                'out_octets': '0',
                'in_packets': '0',
                'out_packets': '0',
                'in_errors': '0',
                'out_errors': '0',
                'crc_errors': '0',
                'collisions': '0',
                'utilization': 0,
                'bandwidth': '1000 Mbps'
            }
        ]
        
        self.system_logs = [
            {'timestamp': '2024-01-15 14:35:12', 'level': 'info', 'source': 'kernel', 'message': 'Interface GigabitEthernet0/0/1 is up'},
            {'timestamp': '2024-01-15 14:33:45', 'level': 'warning', 'source': 'ospf', 'message': 'OSPF neighbor 192.168.1.2 down'},
            {'timestamp': '2024-01-15 14:32:18', 'level': 'error', 'source': 'bgp', 'message': 'BGP session with 203.0.113.10 closed'},
            {'timestamp': '2024-01-15 14:30:55', 'level': 'info', 'source': 'dhcp', 'message': 'DHCP lease assigned to 192.168.1.101'},
            {'timestamp': '2024-01-15 14:28:32', 'level': 'warning', 'source': 'memory', 'message': 'Memory usage above 80%'},
            {'timestamp': '2024-01-15 14:25:14', 'level': 'info', 'source': 'acl', 'message': 'Access list 101 permit applied'},
            {'timestamp': '2024-01-15 14:22:47', 'level': 'error', 'source': 'interface', 'message': 'CRC error detected on Serial0/1/0'},
            {'timestamp': '2024-01-15 14:20:23', 'level': 'info', 'source': 'routing', 'message': 'Static route 0.0.0.0/0 installed'}
        ]
        
        self.system_resources = {
            'cpu': {
                'usage': 45,
                'avg_1min': 45,
                'avg_5min': 38,
                'avg_15min': 42,
                'max_24h': 89,
                'processes': [
                    {'name': 'OSPF Hello', 'usage': 12.3},
                    {'name': 'BGP Scanner', 'usage': 8.7},
                    {'name': 'IP Input', 'usage': 6.2},
                    {'name': 'DHCP Server', 'usage': 4.1}
                ]
            },
            'memory': {
                'total': 512,
                'used': 387,
                'free': 125,
                'usage': 75.6,
                'pools': [
                    {'name': 'Processor', 'used': 145, 'total': 256},
                    {'name': 'I/O', 'used': 89, 'total': 128},
                    {'name': 'Driver', 'used': 153, 'total': 128}
                ]
            },
            'storage': {
                'flash': {'used': 89, 'total': 256, 'usage': 34.7},
                'nvram': {'used': 142, 'total': 512, 'usage': 27.7}
            }
        }
        
        self.create_widgets()
        
    def create_widgets(self):
        """Crear los widgets de monitoreo"""
        # Título
        title_frame = tk.Frame(self, bg='#ffffff')
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(title_frame,
                              text="Monitoreo del Sistema",
                              font=("Arial", 20, "bold"),
                              bg='#ffffff',
                              fg='#030213')
        title_label.pack(side=tk.LEFT)
        
        # Botones de control
        control_frame = tk.Frame(title_frame, bg='#ffffff')
        control_frame.pack(side=tk.RIGHT)
        
        refresh_btn = tk.Button(control_frame, text="🔄 Actualizar", command=self.refresh_data,
                               bg='#007bff', fg='white', font=("Arial", 10))
        refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        export_btn = tk.Button(control_frame, text="📥 Exportar", command=self.export_logs,
                              bg='#28a745', fg='white', font=("Arial", 10))
        export_btn.pack(side=tk.LEFT)
        
        subtitle_label = tk.Label(self,
                                 text="Supervisión en tiempo real del router y sus interfaces",
                                 font=("Arial", 12),
                                 bg='#ffffff',
                                 fg='#666666')
        subtitle_label.pack(anchor=tk.W, pady=(5, 20))
        
        # Notebook para pestañas
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Crear pestañas
        self.create_interfaces_tab()
        self.create_system_tab()
        self.create_logs_tab()
        self.create_resources_tab()
        
    def create_interfaces_tab(self):
        """Crear pestaña de interfaces"""
        interfaces_frame = tk.Frame(self.notebook, bg='#ffffff')
        self.notebook.add(interfaces_frame, text="🌐 Interfaces")
        
        # Estadísticas principales
        stats_frame = tk.Frame(interfaces_frame, bg='#ffffff')
        stats_frame.pack(fill=tk.X, pady=(10, 20))
        
        # Grid de estadísticas
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        stats_frame.grid_columnconfigure(2, weight=1)
        
        active_interfaces = len([i for i in self.interface_stats if i['status'] == 'up'])
        total_errors = sum(int(i['crc_errors']) for i in self.interface_stats)
        avg_utilization = sum(i['utilization'] for i in self.interface_stats) // len(self.interface_stats)
        
        stats = [
            ("✅ Interfaces Activas", f"{active_interfaces}/{len(self.interface_stats)}", "#28a745"),
            ("⚠️ Errores CRC", str(total_errors), "#ffc107"),
            ("📊 Utilización Promedio", f"{avg_utilization}%", "#007bff")
        ]
        
        for i, (title, value, color) in enumerate(stats):
            card = self.create_stat_card(stats_frame, title, value, color)
            card.grid(row=0, column=i, padx=10, pady=5, sticky="ew")
        
        # Filtro de interfaces
        filter_frame = tk.Frame(interfaces_frame, bg='#ffffff')
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(filter_frame, text="Filtrar por interfaz:", font=("Arial", 12),
                bg='#ffffff', fg='#030213').pack(side=tk.LEFT, padx=(0, 10))
        
        self.interface_filter = ttk.Combobox(filter_frame, state='readonly', width=25)
        self.interface_filter['values'] = ['Todas las interfaces'] + [i['name'] for i in self.interface_stats]
        self.interface_filter.set('Todas las interfaces')
        self.interface_filter.pack(side=tk.LEFT)
        
        # Tabla de estadísticas de interfaces
        table_frame = tk.Frame(interfaces_frame, bg='white', relief=tk.SOLID, borderwidth=1)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Crear Treeview
        columns = ('Interfaz', 'Estado', 'Utilización', 'Paquetes In', 'Paquetes Out', 'Errores In', 'Errores Out', 'CRC Errors')
        self.interfaces_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=12)
        
        # Configurar columnas
        for col in columns:
            self.interfaces_tree.heading(col, text=col)
            self.interfaces_tree.column(col, width=100)
        
        # Cargar datos
        self.refresh_interfaces_table()
        
        # Scrollbar
        tree_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.interfaces_tree.yview)
        self.interfaces_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.interfaces_tree.pack(side='left', fill='both', expand=True)
        tree_scrollbar.pack(side='right', fill='y')
        
    def create_system_tab(self):
        """Crear pestaña de sistema"""
        system_frame = tk.Frame(self.notebook, bg='#ffffff')
        self.notebook.add(system_frame, text="💻 Sistema")
        
        # Frame principal con scroll
        main_canvas = tk.Canvas(system_frame, bg='#ffffff')
        scrollbar = ttk.Scrollbar(system_frame, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas, bg='#ffffff')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Grid para recursos del sistema
        scrollable_frame.grid_columnconfigure(0, weight=1)
        scrollable_frame.grid_columnconfigure(1, weight=1)
        scrollable_frame.grid_columnconfigure(2, weight=1)
        
        # CPU
        cpu_frame = tk.LabelFrame(scrollable_frame, text="🖥️ CPU", bg='#ffffff', fg='#030213')
        cpu_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        tk.Label(cpu_frame, text=f"Uso General: {self.system_resources['cpu']['usage']}%",
                font=("Arial", 12, "bold"), bg='#ffffff', fg='#030213').pack(pady=10)
        
        # Barra de progreso para CPU
        cpu_progress = ttk.Progressbar(cpu_frame, length=200, mode='determinate')
        cpu_progress['value'] = self.system_resources['cpu']['usage']
        cpu_progress.pack(pady=(0, 15))
        
        tk.Label(cpu_frame, text="Procesos Principales:", font=("Arial", 11, "bold"),
                bg='#ffffff', fg='#030213').pack()
        
        for process in self.system_resources['cpu']['processes']:
            process_frame = tk.Frame(cpu_frame, bg='#ffffff')
            process_frame.pack(fill=tk.X, padx=10, pady=2)
            tk.Label(process_frame, text=process['name'], font=("Arial", 10),
                    bg='#ffffff', fg='#666666').pack(side=tk.LEFT)
            tk.Label(process_frame, text=f"{process['usage']}%", font=("Arial", 10),
                    bg='#ffffff', fg='#666666').pack(side=tk.RIGHT)
        
        # Memoria
        memory_frame = tk.LabelFrame(scrollable_frame, text="💾 Memoria", bg='#ffffff', fg='#030213')
        memory_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        tk.Label(memory_frame, text=f"Uso Total: {self.system_resources['memory']['usage']:.1f}%",
                font=("Arial", 12, "bold"), bg='#ffffff', fg='#030213').pack(pady=10)
        
        # Barra de progreso para memoria
        mem_progress = ttk.Progressbar(memory_frame, length=200, mode='determinate')
        mem_progress['value'] = self.system_resources['memory']['usage']
        mem_progress.pack(pady=(0, 10))
        
        tk.Label(memory_frame, text=f"Usado: {self.system_resources['memory']['used']} MB",
                font=("Arial", 10), bg='#ffffff', fg='#666666').pack()
        tk.Label(memory_frame, text=f"Total: {self.system_resources['memory']['total']} MB",
                font=("Arial", 10), bg='#ffffff', fg='#666666').pack(pady=(0, 10))
        
        tk.Label(memory_frame, text="Pools de Memoria:", font=("Arial", 11, "bold"),
                bg='#ffffff', fg='#030213').pack()
        
        for pool in self.system_resources['memory']['pools']:
            pool_frame = tk.Frame(memory_frame, bg='#ffffff')
            pool_frame.pack(fill=tk.X, padx=10, pady=2)
            tk.Label(pool_frame, text=pool['name'], font=("Arial", 10),
                    bg='#ffffff', fg='#666666').pack(side=tk.LEFT)
            tk.Label(pool_frame, text=f"{pool['used']}/{pool['total']} MB", font=("Arial", 10),
                    bg='#ffffff', fg='#666666').pack(side=tk.RIGHT)
        
        # Almacenamiento
        storage_frame = tk.LabelFrame(scrollable_frame, text="💽 Almacenamiento", bg='#ffffff', fg='#030213')
        storage_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        
        # Flash Memory
        flash_frame = tk.Frame(storage_frame, bg='#ffffff')
        flash_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(flash_frame, text="Flash Memory", font=("Arial", 11, "bold"),
                bg='#ffffff', fg='#030213').pack()
        tk.Label(flash_frame, text=f"{self.system_resources['storage']['flash']['usage']:.1f}%",
                font=("Arial", 10), bg='#ffffff', fg='#666666').pack()
        
        flash_progress = ttk.Progressbar(flash_frame, length=150, mode='determinate')
        flash_progress['value'] = self.system_resources['storage']['flash']['usage']
        flash_progress.pack(pady=5)
        
        tk.Label(flash_frame, text=f"{self.system_resources['storage']['flash']['used']}/{self.system_resources['storage']['flash']['total']} MB",
                font=("Arial", 9), bg='#ffffff', fg='#666666').pack()
        
        # NVRAM
        nvram_frame = tk.Frame(storage_frame, bg='#ffffff')
        nvram_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(nvram_frame, text="NVRAM", font=("Arial", 11, "bold"),
                bg='#ffffff', fg='#030213').pack()
        tk.Label(nvram_frame, text=f"{self.system_resources['storage']['nvram']['usage']:.1f}%",
                font=("Arial", 10), bg='#ffffff', fg='#666666').pack()
        
        nvram_progress = ttk.Progressbar(nvram_frame, length=150, mode='determinate')
        nvram_progress['value'] = self.system_resources['storage']['nvram']['usage']
        nvram_progress.pack(pady=5)
        
        tk.Label(nvram_frame, text=f"{self.system_resources['storage']['nvram']['used']}/{self.system_resources['storage']['nvram']['total']} KB",
                font=("Arial", 9), bg='#ffffff', fg='#666666').pack()
        
        # Historial de CPU
        history_frame = tk.LabelFrame(scrollable_frame, text="📈 Historial de CPU", bg='#ffffff', fg='#030213')
        history_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        cpu_data = self.system_resources['cpu']
        history_items = [
            ("Promedio 1 min:", f"{cpu_data['avg_1min']}%"),
            ("Promedio 5 min:", f"{cpu_data['avg_5min']}%"),
            ("Promedio 15 min:", f"{cpu_data['avg_15min']}%"),
            ("Máximo 24h:", f"{cpu_data['max_24h']}%")
        ]
        
        for label, value in history_items:
            item_frame = tk.Frame(history_frame, bg='#ffffff')
            item_frame.pack(fill=tk.X, padx=10, pady=5)
            tk.Label(item_frame, text=label, font=("Arial", 11),
                    bg='#ffffff', fg='#030213').pack(side=tk.LEFT)
            tk.Label(item_frame, text=value, font=("Arial", 11),
                    bg='#ffffff', fg='#666666').pack(side=tk.RIGHT)
        
        # Estadísticas de red
        network_frame = tk.LabelFrame(scrollable_frame, text="🌐 Estadísticas de Red", bg='#ffffff', fg='#030213')
        network_frame.grid(row=1, column=2, padx=10, pady=10, sticky="ew")
        
        total_in = sum(int(i['in_packets'].replace(',', '')) for i in self.interface_stats)
        total_out = sum(int(i['out_packets'].replace(',', '')) for i in self.interface_stats)
        total_errors = sum(int(i['in_errors']) + int(i['out_errors']) for i in self.interface_stats)
        
        network_items = [
            ("Total Paquetes In:", f"{total_in:,}"),
            ("Total Paquetes Out:", f"{total_out:,}"),
            ("Total Errores:", str(total_errors)),
            ("Colisiones:", "0")
        ]
        
        for label, value in network_items:
            item_frame = tk.Frame(network_frame, bg='#ffffff')
            item_frame.pack(fill=tk.X, padx=10, pady=5)
            tk.Label(item_frame, text=label, font=("Arial", 11),
                    bg='#ffffff', fg='#030213').pack(side=tk.LEFT)
            color = '#dc3545' if 'Errores' in label and value != '0' else '#666666'
            tk.Label(item_frame, text=value, font=("Arial", 11),
                    bg='#ffffff', fg=color).pack(side=tk.RIGHT)
        
        # Configurar scroll
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def create_logs_tab(self):
        """Crear pestaña de logs"""
        logs_frame = tk.Frame(self.notebook, bg='#ffffff')
        self.notebook.add(logs_frame, text="📋 Logs")
        
        # Título
        title_label = tk.Label(logs_frame,
                              text="Logs del Sistema en Tiempo Real",
                              font=("Arial", 16, "bold"),
                              bg='#ffffff',
                              fg='#030213')
        title_label.pack(pady=(10, 5))
        
        subtitle_label = tk.Label(logs_frame,
                                 text="Eventos y mensajes del sistema ordenados cronológicamente",
                                 font=("Arial", 12),
                                 bg='#ffffff',
                                 fg='#666666')
        subtitle_label.pack(pady=(0, 20))
        
        # Frame de logs con scroll
        logs_canvas = tk.Canvas(logs_frame, bg='#ffffff')
        logs_scrollbar = ttk.Scrollbar(logs_frame, orient="vertical", command=logs_canvas.yview)
        self.logs_scrollable_frame = tk.Frame(logs_canvas, bg='#ffffff')
        
        self.logs_scrollable_frame.bind(
            "<Configure>",
            lambda e: logs_canvas.configure(scrollregion=logs_canvas.bbox("all"))
        )
        
        logs_canvas.create_window((0, 0), window=self.logs_scrollable_frame, anchor="nw")
        logs_canvas.configure(yscrollcommand=logs_scrollbar.set)
        
        # Mostrar logs
        self.refresh_logs()
        
        # Configurar scroll
        def _on_mousewheel_logs(event):
            logs_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        logs_canvas.bind_all("<MouseWheel>", _on_mousewheel_logs)
        
        logs_canvas.pack(side="left", fill="both", expand=True, padx=(10, 0))
        logs_scrollbar.pack(side="right", fill="y", padx=(0, 10))
        
    def create_resources_tab(self):
        """Crear pestaña de recursos"""
        resources_frame = tk.Frame(self.notebook, bg='#ffffff')
        self.notebook.add(resources_frame, text="📊 Recursos")
        
        # Resumen de rendimiento
        summary_frame = tk.LabelFrame(resources_frame, text="Resumen de Rendimiento", bg='#ffffff', fg='#030213')
        summary_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Grid para métricas
        summary_frame.grid_columnconfigure(0, weight=1)
        summary_frame.grid_columnconfigure(1, weight=1)
        summary_frame.grid_columnconfigure(2, weight=1)
        summary_frame.grid_columnconfigure(3, weight=1)
        
        metrics = [
            ("🖥️ CPU", f"{self.system_resources['cpu']['usage']}%"),
            ("💾 Memoria", f"{self.system_resources['memory']['usage']:.1f}%"),
            ("💽 Flash", f"{self.system_resources['storage']['flash']['usage']:.1f}%"),
            ("⚡ NVRAM", f"{self.system_resources['storage']['nvram']['usage']:.1f}%")
        ]
        
        for i, (label, value) in enumerate(metrics):
            metric_frame = tk.Frame(summary_frame, bg='#ffffff')
            metric_frame.grid(row=0, column=i, padx=20, pady=20)
            
            tk.Label(metric_frame, text=label, font=("Arial", 14),
                    bg='#ffffff', fg='#030213').pack()
            tk.Label(metric_frame, text=value, font=("Arial", 20, "bold"),
                    bg='#ffffff', fg='#007bff').pack()
        
        # Gráfico simulado de tendencias
        chart_frame = tk.LabelFrame(resources_frame, text="Tendencias de Uso", bg='#ffffff', fg='#030213')
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Simulación simple de gráfico con texto
        chart_text = tk.Text(chart_frame, bg='#f8f9fa', fg='#030213', font=("Consolas", 10), height=15)
        chart_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Datos simulados para gráfico
        chart_data = """
CPU Usage (Last 24 hours)
========================
00:00 |████████████████████████████████████████ 40%
04:00 |████████████████████████████████████ 36%
08:00 |████████████████████████████████████████████████ 50%
12:00 |███████████████████████████████████████████████████████ 59%
16:00 |████████████████████████████████████████████ 44%
20:00 |██████████████████████████████████████ 38%

Memory Usage Trend
==================
Available: 125 MB
Used:      387 MB
Peak:      421 MB (14:30)
Average:   365 MB

Interface Utilization
====================
GigE0/0/1: ████████████████████ 35%
GigE0/0/2: ████████████ 22%
Serial0/1: ████████████████████████████████████████ 78%
GigE0/0/3: (down)
        """
        
        chart_text.insert(tk.END, chart_data)
        chart_text.config(state=tk.DISABLED)
        
    def create_stat_card(self, parent, title, value, color):
        """Crear tarjeta de estadística"""
        card = tk.Frame(parent, bg='white', relief=tk.SOLID, borderwidth=1)
        
        title_label = tk.Label(card, text=title, font=("Arial", 10, "bold"),
                              bg='white', fg='#030213')
        title_label.pack(pady=(10, 5))
        
        value_label = tk.Label(card, text=value, font=("Arial", 16, "bold"),
                              bg='white', fg=color)
        value_label.pack()
        
        tk.Frame(card, height=10, bg='white').pack()
        
        return card
        
    def refresh_interfaces_table(self):
        """Refrescar tabla de interfaces"""
        # Limpiar tabla
        for item in self.interfaces_tree.get_children():
            self.interfaces_tree.delete(item)
            
        # Agregar datos
        for interface in self.interface_stats:
            status_text = "UP" if interface['status'] == 'up' else "DOWN"
            self.interfaces_tree.insert('', tk.END, values=(
                interface['name'],
                status_text,
                f"{interface['utilization']}%",
                interface['in_packets'],
                interface['out_packets'],
                interface['in_errors'],
                interface['out_errors'],
                interface['crc_errors']
            ), tags=(interface['status'],))
        
        # Configurar colores
        self.interfaces_tree.tag_configure('up', foreground='#28a745')
        self.interfaces_tree.tag_configure('down', foreground='#dc3545')
        
    def refresh_logs(self):
        """Refrescar logs"""
        # Limpiar frame de logs
        for widget in self.logs_scrollable_frame.winfo_children():
            widget.destroy()
            
        # Agregar logs
        for log in self.system_logs:
            log_frame = tk.Frame(self.logs_scrollable_frame, bg='white', relief=tk.SOLID, borderwidth=1)
            log_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # Header del log
            header_frame = tk.Frame(log_frame, bg='white')
            header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
            
            # Icono y timestamp
            icon = "❌" if log['level'] == 'error' else "⚠️" if log['level'] == 'warning' else "ℹ️"
            tk.Label(header_frame, text=f"{icon} {log['timestamp']}", font=("Arial", 10),
                    bg='white', fg='#666666').pack(side=tk.LEFT)
            
            # Source badge
            source_color = '#dc3545' if log['level'] == 'error' else '#ffc107' if log['level'] == 'warning' else '#007bff'
            tk.Label(header_frame, text=log['source'].upper(), font=("Arial", 9),
                    bg=source_color, fg='white', padx=5, pady=2).pack(side=tk.LEFT, padx=(10, 0))
            
            # Level badge
            level_color = '#dc3545' if log['level'] == 'error' else '#ffc107' if log['level'] == 'warning' else '#28a745'
            tk.Label(header_frame, text=log['level'].upper(), font=("Arial", 9),
                    bg=level_color, fg='white', padx=5, pady=2).pack(side=tk.RIGHT)
            
            # Mensaje
            tk.Label(log_frame, text=log['message'], font=("Arial", 11),
                    bg='white', fg='#030213', wraplength=600, justify=tk.LEFT).pack(anchor=tk.W, padx=10, pady=(0, 10))
        
    def refresh_data(self):
        """Refrescar todos los datos"""
        # Simular actualización de datos
        for interface in self.interface_stats:
            if interface['status'] == 'up':
                # Simular cambios pequeños en utilización
                change = random.randint(-5, 5)
                interface['utilization'] = max(0, min(100, interface['utilization'] + change))
        
        # Actualizar uso de CPU
        change = random.randint(-3, 3)
        self.system_resources['cpu']['usage'] = max(0, min(100, self.system_resources['cpu']['usage'] + change))
        
        # Refrescar vistas
        self.refresh_interfaces_table()
        
        messagebox.showinfo("Actualización", "Datos actualizados correctamente")
        
    def export_logs(self):
        """Exportar logs"""
        messagebox.showinfo("Exportar", "Logs exportados a router_logs.txt")
        
    def refresh(self):
        """Refrescar la vista completa"""
        self.refresh_interfaces_table()
        self.refresh_logs()
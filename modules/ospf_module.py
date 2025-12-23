import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, List


class OspfModuleWindow(tk.Toplevel):
    """Ventana de detalles para el módulo OSPF.

    Muestra información parseada: estado, process-id, router-id,
    redes anunciadas y vecinos OSPF si están disponibles.
    """

    def __init__(self, parent: tk.Widget, shared_data: Dict[str, Any]) -> None:
        super().__init__(parent)
        self.title("Detalles de OSPF")
        self.geometry("800x600")
        self.configure(bg="#ffffff")

        self.shared_data = shared_data or {}

        container = ttk.Frame(self, style="Card.TFrame", padding=(15, 15))
        container.pack(fill=tk.BOTH, expand=True)

        # Encabezado
        title = ttk.Label(container, text="OSPF (Open Shortest Path First)", font=("Arial", 14, "bold"), background="white")
        title.pack(anchor="w")

        # Resumen
        summary_frame = ttk.Frame(container, style="Card.TFrame", padding=(10, 10))
        summary_frame.pack(fill=tk.X, pady=(10, 10))

        ospf = (self.shared_data.get("routing_protocols", {}).get("ospf", {}) or {})
        enabled = bool(ospf.get("enabled"))
        processes = list(ospf.get("processes") or [])
        process_id = ospf.get("process_id", "")
        router_id = ospf.get("router_id", "")

        ttk.Label(summary_frame, text=f"Estado: {'Habilitado' if enabled else 'Deshabilitado'}", background="white").pack(side=tk.LEFT)
        if processes:
            pid_list = ", ".join([str(p.get("process_id", "")) or "?" for p in processes])
            ttk.Label(summary_frame, text=f"  |  Procesos: {pid_list}", background="white").pack(side=tk.LEFT)
        else:
            ttk.Label(summary_frame, text=f"  |  Proceso: {process_id or 'N/A'}", background="white").pack(side=tk.LEFT)
        ttk.Label(summary_frame, text=f"  |  Router-ID: {router_id or (', '.join([p.get('router_id','') for p in processes if p.get('router_id')]) or 'N/A')}", background="white").pack(side=tk.LEFT)

        # Redes OSPF
        networks_frame = ttk.Frame(container, style="Card.TFrame", padding=(10, 10))
        networks_frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(networks_frame, text="Redes Anunciadas (network / wildcard / area)", font=("Arial", 11, "bold"), background="white").pack(anchor="w", pady=(0, 6))

        if processes:
            nb = ttk.Notebook(networks_frame)
            nb.pack(fill=tk.BOTH, expand=True)
            for idx, proc in enumerate(processes):
                tab = ttk.Frame(nb)
                nb.add(tab, text=f"P{proc.get('process_id') or idx+1}")
                rid_lbl = ttk.Label(tab, text=f"Router-ID: {proc.get('router_id', '') or 'N/A'}", background="white")
                rid_lbl.pack(anchor="w", pady=(0,6))
                net_rows = [
                    (n.get("network", ""), n.get("wildcard", ""), n.get("area", ""))
                    for n in (proc.get("networks", []) or [])
                ]
                self._build_table_window(tab, ["Network", "Wildcard", "Area"], net_rows)
        else:
            net_rows = [
                (n.get("network", ""), n.get("wildcard", ""), n.get("area", ""))
                for n in (ospf.get("networks", []) or [])
            ]
            self._build_table_window(networks_frame, ["Network", "Wildcard", "Area"], net_rows)

        # Vecinos OSPF (si están disponibles)
        peers = []
        try:
            peers = (self.shared_data.get("parsed_data", {}).get("ospf_neighbors", []) or [])
        except Exception:
            peers = []

        peers_frame = ttk.Frame(container, style="Card.TFrame", padding=(10, 10))
        peers_frame.pack(fill=tk.X, expand=False)
        ttk.Label(peers_frame, text="Vecinos OSPF", font=("Arial", 11, "bold"), background="white").pack(anchor="w", pady=(0, 6))

        peer_rows = [
            (
                p.get("router_id", ""),
                p.get("address", ""),
                p.get("state", ""),
                p.get("dead_time", ""),
                p.get("interface", ""),
            )
            for p in peers
        ]
        self._build_table_window(peers_frame, ["Router-ID", "Dirección", "Estado", "Dead Time", "Interfaz"], peer_rows)

        # Sección de configuración OSPF: mostrar salida si está disponible; de lo contrario, comandos sugeridos.
        cfg_label = ttk.Label(container, text="Configuración OSPF", font=("Arial", 11, "bold"), background="white")
        cfg_label.pack(anchor="w", pady=(10, 6))

        raw_cfg = ""
        try:
            raw_cfg = (self.shared_data.get("parsed_data", {})
                       .get("raw", {})
                       .get("ospf_config_section", "") or "").strip()
        except Exception:
            raw_cfg = ""

        if raw_cfg:
            text_frame = ttk.Frame(container, style="Card.TFrame", padding=(10, 10))
            text_frame.pack(fill=tk.BOTH, expand=True)
            # Área de texto con scroll
            txt = tk.Text(text_frame, height=12, font=("Consolas", 10), bg="white")
            vs = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=txt.yview)
            txt.configure(yscrollcommand=vs.set)
            txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            vs.pack(side=tk.RIGHT, fill=tk.Y)
            try:
                txt.insert("1.0", raw_cfg)
            except Exception:
                txt.insert("1.0", str(raw_cfg))
            txt.configure(state=tk.DISABLED)
        else:
            cmd_frame = ttk.Frame(container, style="Card.TFrame", padding=(10, 10))
            cmd_frame.pack(fill=tk.X, expand=False)
            # Detectar fabricante desde datos parseados o pista de conexión
            vendor = ""
            try:
                vendor = (self.shared_data.get("parsed_data", {})
                          .get("device_info", {})
                          .get("vendor", "") or "").lower()
                if not vendor:
                    vendor = (self.shared_data.get("connection_data", {})
                              .get("vendor_hint", "") or "").lower()
            except Exception:
                vendor = ""

            mono = ("Consolas", 10)
            if vendor.startswith("cisco"):
                tk.Label(cmd_frame, text="CISCO# show running-config | sec ospf", font=mono, bg="white").pack(anchor="w")
            elif vendor.startswith("huawei"):
                tk.Label(cmd_frame, text="<HUAWEI> dis current-configuration | section include ospf", font=mono, bg="white").pack(anchor="w")
                tk.Label(cmd_frame, text="(En algunos modelos: dis current-configuration | section ospf)", font=("Arial", 9), bg="white").pack(anchor="w", pady=(4,0))
            else:
                tk.Label(cmd_frame, text="CISCO# show running-config | sec ospf", font=mono, bg="white").pack(anchor="w")
                tk.Label(cmd_frame, text="<HUAWEI> dis current-configuration | section include ospf", font=mono, bg="white").pack(anchor="w", pady=(6,0))
                tk.Label(cmd_frame, text="(En algunos modelos: dis current-configuration | section ospf)", font=("Arial", 9), bg="white").pack(anchor="w")

        # Botón cerrar
        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(btn_frame, text="Cerrar", command=self.destroy, style="Secondary.TButton").pack(side=tk.RIGHT)

    def _build_table_window(self, parent: tk.Widget, headers: List[str], rows: List[tuple]) -> None:
        table = tk.Frame(parent, bg="white")
        table.pack(fill=tk.X, expand=False)
        for c, title in enumerate(headers):
            lbl = tk.Label(
                table,
                text=title,
                font=("Arial", 9, "bold"),
                bg="#f7f7f7",
                bd=1,
                relief="solid",
                padx=6,
                pady=4,
                anchor="center",
            )
            lbl.grid(row=0, column=c, sticky="nsew")
        if rows:
            for r, row in enumerate(rows, start=1):
                for c, cell in enumerate(row):
                    cell_lbl = tk.Label(
                        table,
                        text=str(cell),
                        font=("Arial", 9),
                        bg="white",
                        bd=1,
                        relief="solid",
                        padx=6,
                        pady=3,
                        anchor="w",
                    )
                    cell_lbl.grid(row=r, column=c, sticky="nsew")
        else:
            empty = tk.Label(
                table,
                text="Sin datos",
                font=("Arial", 9, "italic"),
                bg="white",
                bd=1,
                relief="solid",
                padx=6,
                pady=3,
                anchor="w",
            )
            empty.grid(row=1, column=0, columnspan=len(headers), sticky="nsew")
        for c in range(len(headers)):
            table.grid_columnconfigure(c, weight=1)


class OspfModulePanel(tk.Frame):
    """Panel embebido para mostrar detalles de OSPF dentro de un contenedor.

    Replica el contenido de la ventana en un `tk.Frame` para integrarlo
    en layouts con panel derecho (Ver/Config).
    """

    def __init__(self, parent: tk.Widget, shared_data: Dict[str, Any]) -> None:
        super().__init__(parent, bg="#ffffff")
        self.shared_data = shared_data or {}

        container = ttk.Frame(self, style="Card.TFrame", padding=(16, 16))
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        title = ttk.Label(container, text="OSPF (Open Shortest Path First)", font=("Arial", 14, "bold"), background="white")
        title.pack(anchor="w")

        summary_frame = ttk.Frame(container, style="Card.TFrame", padding=(10, 10))
        summary_frame.pack(fill=tk.X, pady=(8, 12))

        ospf = (self.shared_data.get("routing_protocols", {}).get("ospf", {}) or {})
        enabled = bool(ospf.get("enabled"))
        processes = list(ospf.get("processes") or [])
        process_id = ospf.get("process_id", "")
        router_id = ospf.get("router_id", "")

        ttk.Label(summary_frame, text=f"Estado: {'Habilitado' if enabled else 'Deshabilitado'}", background="white").pack(side=tk.LEFT)
        if processes:
            pid_list = ", ".join([str(p.get("process_id", "")) or "?" for p in processes])
            ttk.Label(summary_frame, text=f"  |  Procesos: {pid_list}", background="white").pack(side=tk.LEFT)
        else:
            ttk.Label(summary_frame, text=f"  |  Proceso: {process_id or 'N/A'}", background="white").pack(side=tk.LEFT)
        ttk.Label(summary_frame, text=f"  |  Router-ID: {router_id or (', '.join([p.get('router_id','') for p in processes if p.get('router_id')]) or 'N/A')}", background="white").pack(side=tk.LEFT)

        networks_frame = ttk.Frame(container, style="Card.TFrame", padding=(10, 10))
        networks_frame.pack(fill=tk.BOTH, expand=True, pady=(6, 8))
        ttk.Label(networks_frame, text="Redes Anunciadas (network / wildcard / area)", font=("Arial", 11, "bold"), background="white").pack(anchor="w", pady=(0, 6))

        if processes:
            nb = ttk.Notebook(networks_frame)
            nb.pack(fill=tk.BOTH, expand=True)
            for idx, proc in enumerate(processes):
                tab = ttk.Frame(nb)
                nb.add(tab, text=f"P{proc.get('process_id') or idx+1}")
                rid_lbl = ttk.Label(tab, text=f"Router-ID: {proc.get('router_id', '') or 'N/A'}", background="white")
                rid_lbl.pack(anchor="w", pady=(0,6))
                net_rows = [
                    (n.get("network", ""), n.get("wildcard", ""), n.get("area", ""))
                    for n in (proc.get("networks", []) or [])
                ]
                self._build_table(
                    tab,
                    headers=["Network", "Wildcard", "Area"],
                    rows=net_rows,
                )
        else:
            net_rows = [
                (n.get("network", ""), n.get("wildcard", ""), n.get("area", ""))
                for n in (ospf.get("networks", []) or [])
            ]
            self._build_table(
                networks_frame,
                headers=["Network", "Wildcard", "Area"],
                rows=net_rows,
            )

        peers = []
        try:
            peers = (self.shared_data.get("parsed_data", {}).get("ospf_neighbors", []) or [])
        except Exception:
            peers = []

        peers_frame = ttk.Frame(container, style="Card.TFrame", padding=(10, 10))
        peers_frame.pack(fill=tk.X, expand=False, pady=(8, 10))
        ttk.Label(peers_frame, text="Vecinos OSPF", font=("Arial", 11, "bold"), background="white").pack(anchor="w", pady=(0, 6))

        peer_rows = [
            (
                p.get("router_id", ""),
                p.get("address", ""),
                p.get("state", ""),
                p.get("dead_time", ""),
                p.get("interface", ""),
            )
            for p in peers
        ]
        self._build_table(
            peers_frame,
            headers=["Router-ID", "Dirección", "Estado", "Dead Time", "Interfaz"],
            rows=peer_rows,
        )

        # Sección de configuración OSPF: mostrar salida si está disponible; de lo contrario, comandos sugeridos.
        cfg_label = ttk.Label(container, text="Configuración OSPF", font=("Arial", 11, "bold"), background="white")
        cfg_label.pack(anchor="w", pady=(10, 6))

        raw_cfg = ""
        try:
            raw_cfg = (self.shared_data.get("parsed_data", {})
                       .get("raw", {})
                       .get("ospf_config_section", "") or "").strip()
        except Exception:
            raw_cfg = ""

        if raw_cfg:
            text_frame = ttk.Frame(container, style="Card.TFrame", padding=(10, 10))
            text_frame.pack(fill=tk.BOTH, expand=True)
            txt = tk.Text(text_frame, height=10, font=("Consolas", 10), bg="white")
            vs = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=txt.yview)
            txt.configure(yscrollcommand=vs.set)
            txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            vs.pack(side=tk.RIGHT, fill=tk.Y)
            try:
                txt.insert("1.0", raw_cfg)
            except Exception:
                txt.insert("1.0", str(raw_cfg))
            txt.configure(state=tk.DISABLED)
        else:
            cmd_frame = ttk.Frame(container, style="Card.TFrame", padding=(10, 10))
            cmd_frame.pack(fill=tk.X, expand=False)
            vendor = ""
            try:
                vendor = (self.shared_data.get("parsed_data", {})
                          .get("device_info", {})
                          .get("vendor", "") or "").lower()
                if not vendor:
                    vendor = (self.shared_data.get("connection_data", {})
                              .get("vendor_hint", "") or "").lower()
            except Exception:
                vendor = ""

            mono = ("Consolas", 10)
            if vendor.startswith("cisco"):
                tk.Label(cmd_frame, text="CISCO# show running-config | sec ospf", font=mono, bg="white").pack(anchor="w")
            elif vendor.startswith("huawei"):
                tk.Label(cmd_frame, text="<HUAWEI> dis current-configuration | section include ospf", font=mono, bg="white").pack(anchor="w")
                tk.Label(cmd_frame, text="(En algunos modelos: dis current-configuration | section ospf)", font=("Arial", 9), bg="white").pack(anchor="w", pady=(4,0))
            else:
                tk.Label(cmd_frame, text="CISCO# show running-config | sec ospf", font=mono, bg="white").pack(anchor="w")
                tk.Label(cmd_frame, text="<HUAWEI> dis current-configuration | section include ospf", font=mono, bg="white").pack(anchor="w", pady=(6,0))
                tk.Label(cmd_frame, text="(En algunos modelos: dis current-configuration | section ospf)", font=("Arial", 9), bg="white").pack(anchor="w")

    def _build_table(self, parent: tk.Widget, headers: List[str], rows: List[tuple]) -> None:
        """Construye una tabla con celdas y bordes utilizando Labels en grid.

        La altura total del contenedor se ajusta automáticamente al número de filas.
        """
        table = tk.Frame(parent, bg="white")
        table.pack(fill=tk.X, expand=False)

        # Encabezados
        for c, title in enumerate(headers):
            lbl = tk.Label(
                table,
                text=title,
                font=("Arial", 9, "bold"),
                bg="#f7f7f7",
                bd=1,
                relief="solid",
                padx=6,
                pady=4,
                anchor="center",
            )
            lbl.grid(row=0, column=c, sticky="nsew")

        # Filas
        if rows:
            for r, row in enumerate(rows, start=1):
                for c, cell in enumerate(row):
                    cell_lbl = tk.Label(
                        table,
                        text=str(cell),
                        font=("Arial", 9),
                        bg="white",
                        bd=1,
                        relief="solid",
                        padx=6,
                        pady=3,
                        anchor="w",
                    )
                    cell_lbl.grid(row=r, column=c, sticky="nsew")
        else:
            # Fila vacía informativa
            empty = tk.Label(
                table,
                text="Sin datos",
                font=("Arial", 9, "italic"),
                bg="white",
                bd=1,
                relief="solid",
                padx=6,
                pady=3,
                anchor="w",
            )
            empty.grid(row=1, column=0, columnspan=len(headers), sticky="nsew")

        # Hacer que las columnas se expandan de forma uniforme
        for c in range(len(headers)):
            table.grid_columnconfigure(c, weight=1)
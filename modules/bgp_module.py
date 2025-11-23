import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Dict, Any, List


class BgpModuleWindow(tk.Toplevel):
    """Ventana de detalles para el módulo BGP.

    Muestra información parseada: estado, AS, IP del router (desde datos de conexión),
    vecinos BGP y resumen/estado si está disponible.
    """

    def __init__(self, parent: tk.Widget, shared_data: Dict[str, Any]) -> None:
        super().__init__(parent)
        self.title("Detalles de BGP")
        self.geometry("850x600")
        self.configure(bg="#ffffff")

        self.shared_data = shared_data or {}

        container = ttk.Frame(self, style="Card.TFrame", padding=(15, 15))
        container.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(container, text="BGP (Border Gateway Protocol)", font=("Arial", 14, "bold"), background="white")
        title.pack(anchor="w")

        # Resumen
        summary_frame = ttk.Frame(container, style="Card.TFrame", padding=(10, 10))
        summary_frame.pack(fill=tk.X, pady=(10, 10))

        bgp = (self.shared_data.get("routing_protocols", {}).get("bgp", {}) or {})
        enabled = bool(bgp.get("enabled"))
        asn = bgp.get("as_number", "")
        router_ip = (self.shared_data.get("connection_data", {}).get("hostname") or "N/A")

        ttk.Label(summary_frame, text=f"Estado: {'Habilitado' if enabled else 'Deshabilitado'}", background="white").pack(side=tk.LEFT)
        ttk.Label(summary_frame, text=f"  |  AS: {asn or 'N/A'}", background="white").pack(side=tk.LEFT)
        ttk.Label(summary_frame, text=f"  |  IP del Router: {router_ip}", background="white").pack(side=tk.LEFT)

        # Vecinos BGP
        neighbors_frame = ttk.Frame(container, style="Card.TFrame", padding=(10, 10))
        neighbors_frame.pack(fill=tk.X, expand=False)
        ttk.Label(neighbors_frame, text="Vecinos BGP", font=("Arial", 11, "bold"), background="white").pack(anchor="w", pady=(0, 6))

        # Cargar vecinos desde parsed_data si está disponible (resumen BGP)
        peers_summary: List[Dict[str, Any]] = []
        try:
            peers_summary = (self.shared_data.get("parsed_data", {}).get("bgp_peers", []) or [])
        except Exception:
            peers_summary = []

        neighbor_rows = []
        if peers_summary:
            for p in peers_summary:
                neighbor_rows.append((p.get("ip", ""), p.get("as", ""), p.get("state", ""), p.get("pref_rcv", ""), p.get("updown", "")))
        else:
            for n in bgp.get("neighbors", []) or []:
                neighbor_rows.append((n.get("ip", ""), n.get("remote_as", ""), "", "", ""))

        self._build_table(neighbors_frame, ["IP Vecino", "AS Remoto", "Estado", "Pref Rcv", "Up/Down"], neighbor_rows)

        # Configuración BGP cruda (si existe)
        cfg_label = ttk.Label(container, text="Configuración BGP", font=("Arial", 11, "bold"), background="white")
        cfg_label.pack(anchor="w", pady=(10, 0))

        cfg_text = scrolledtext.ScrolledText(container, height=8, font=("Consolas", 9))
        cfg_text.pack(fill=tk.BOTH, expand=True)
        try:
            cfg_text.insert("1.0", bgp.get("config", ""))
        except Exception:
            pass

        # Botón cerrar
        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(btn_frame, text="Cerrar", command=self.destroy, style="Secondary.TButton").pack(side=tk.RIGHT)

    def _build_table(self, parent: tk.Widget, headers: List[str], rows: List[tuple]) -> None:
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


class BgpModulePanel(tk.Frame):
    """Panel embebido para mostrar detalles de BGP dentro de un contenedor.

    Replica el contenido de la ventana en un `tk.Frame` para integrarlo
    en layouts con panel derecho (Ver/Config).
    """

    def __init__(self, parent: tk.Widget, shared_data: Dict[str, Any]) -> None:
        super().__init__(parent, bg="#ffffff")
        self.shared_data = shared_data or {}

        container = ttk.Frame(self, style="Card.TFrame", padding=(16, 16))
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        title = ttk.Label(container, text="BGP (Border Gateway Protocol)", font=("Arial", 14, "bold"), background="white")
        title.pack(anchor="w")

        summary_frame = ttk.Frame(container, style="Card.TFrame", padding=(10, 10))
        summary_frame.pack(fill=tk.X, pady=(8, 12))

        bgp = (self.shared_data.get("routing_protocols", {}).get("bgp", {}) or {})
        enabled = bool(bgp.get("enabled"))
        asn = bgp.get("as_number", "")
        router_ip = (self.shared_data.get("connection_data", {}).get("hostname") or "N/A")

        ttk.Label(summary_frame, text=f"Estado: {'Habilitado' if enabled else 'Deshabilitado'}", background="white").pack(side=tk.LEFT)
        ttk.Label(summary_frame, text=f"  |  AS: {asn or 'N/A'}", background="white").pack(side=tk.LEFT)
        ttk.Label(summary_frame, text=f"  |  IP del Router: {router_ip}", background="white").pack(side=tk.LEFT)

        neighbors_frame = ttk.Frame(container, style="Card.TFrame", padding=(10, 10))
        neighbors_frame.pack(fill=tk.X, expand=False, pady=(6, 10))
        ttk.Label(neighbors_frame, text="Vecinos BGP", font=("Arial", 11, "bold"), background="white").pack(anchor="w", pady=(0, 6))

        peers_summary: List[Dict[str, Any]] = []
        try:
            peers_summary = (self.shared_data.get("parsed_data", {}).get("bgp_peers", []) or [])
        except Exception:
            peers_summary = []

        neighbor_rows = []
        if peers_summary:
            for p in peers_summary:
                neighbor_rows.append((p.get("ip", ""), p.get("as", ""), p.get("state", ""), p.get("pref_rcv", ""), p.get("updown", "")))
        else:
            for n in bgp.get("neighbors", []) or []:
                neighbor_rows.append((n.get("ip", ""), n.get("remote_as", ""), "", "", ""))

        self._build_table(
            neighbors_frame,
            headers=["IP Vecino", "AS Remoto", "Estado", "Pref Rcv", "Up/Down"],
            rows=neighbor_rows,
        )

        cfg_label = ttk.Label(container, text="Configuración BGP", font=("Arial", 11, "bold"), background="white")
        cfg_label.pack(anchor="w", pady=(10, 2))

        cfg_text = scrolledtext.ScrolledText(container, height=8, font=("Consolas", 9))
        cfg_text.pack(fill=tk.BOTH, expand=True, pady=(6, 0))
        try:
            cfg_text.insert("1.0", bgp.get("config", ""))
        except Exception:
            pass

    def _build_table(self, parent: tk.Widget, headers: List[str], rows: List[tuple]) -> None:
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
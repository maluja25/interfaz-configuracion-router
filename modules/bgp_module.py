import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Dict, Any, List
from .router_analyzer.parsers import parse_cisco_bgp_summary, parse_huawei_bgp_peer
from .router_analyzer.connections import run_ssh_command, run_telnet_command, run_serial_command
from .router_analyzer.vendor_commands import DISABLE_PAGING


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

        # Datos base
        bgp = (self.shared_data.get("routing_protocols", {}).get("bgp", {}) or {})
        enabled = bool(bgp.get("enabled"))
        asn = bgp.get("as_number", "")
        router_id = bgp.get("router_id", "")
        vendor = (self.shared_data.get("parsed_data", {}).get("device_info", {}).get("vendor", "") or
                  self.shared_data.get("connection_data", {}).get("vendor_hint", "") or "").lower()
        vrfs = bgp.get("vrfs", []) or []

        # Notebook de pestañas: GLOBAL + VRFs
        notebook = ttk.Notebook(container)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(8, 0))

        # Pestaña GLOBAL
        global_tab = ttk.Frame(notebook, style="Card.TFrame")
        notebook.add(global_tab, text="GLOBAL")
        gsum = ttk.Frame(global_tab, style="Card.TFrame", padding=(0, 0))
        gsum.pack_forget()

        gcontent = ttk.Frame(global_tab, style="Card.TFrame", padding=(10, 8))
        gcontent.pack(fill=tk.BOTH, expand=True)
        # Tabla única de resumen BGP (GLOBAL)
        # Card con borde completo alrededor del bloque de resumen
        gcard = tk.Frame(gcontent, bg="white", bd=1, relief="solid", highlightthickness=1, highlightbackground="#c9c9c9")
        gcard.pack(fill=tk.X, expand=False, padx=10, pady=8)
        gbody = tk.Frame(gcard, bg="white")
        gbody.pack(fill=tk.X, padx=8, pady=8)
        ttk.Label(gbody, text="Resumen BGP", font=("Arial", 12, "bold"), background="white", anchor="center", justify="center").pack(fill=tk.X, pady=(2, 6))
        ttk.Label(gbody, text=f"Local AS: {asn or 'N/A'}", background="white", anchor="center", justify="center").pack(fill=tk.X)
        ttk.Label(gbody, text=f"Router-ID: {router_id or 'N/A'}", background="white", anchor="center", justify="center").pack(fill=tk.X, pady=(0, 6))
        # Botón para obtener información bajo demanda (GLOBAL)
        ttk.Button(
            gbody,
            text="Obtener información",
            command=lambda: self._fetch_and_render(scope="global", vendor=vendor)
        ).pack(pady=(0, 8))
        # No autopoblar: la tabla se llenará al presionar el botón
        rows: List[tuple] = []
        # Área contenedor para poder reconstruir la tabla al actualizar
        self._global_table_area = ttk.Frame(gbody, style="Card.TFrame")
        self._global_table_area.pack(fill=tk.X, expand=False)
        self._build_table(self._global_table_area, [
            "NEIGHBOR", "V", "AS", "MSGRCVD", "MSGSENT", "TBLVER", "INQ", "OUTQ", "UP/DOWN", "STATE/PFXRCD"
        ], rows)

        # Pestañas por VRF
        for v in vrfs:
            vrf_tab = ttk.Frame(notebook, style="Card.TFrame")
            notebook.add(vrf_tab, text=f"VRF {v.get('name','')}")
            vsum = ttk.Frame(vrf_tab, style="Card.TFrame", padding=(0, 0))
            vsum.pack_forget()

            vcontent = ttk.Frame(vrf_tab, style="Card.TFrame", padding=(10, 8))
            vcontent.pack(fill=tk.BOTH, expand=True)
            vcard = tk.Frame(vcontent, bg="white", bd=1, relief="solid", highlightthickness=1, highlightbackground="#c9c9c9")
            vcard.pack(fill=tk.X, expand=False, padx=10, pady=8)
            vbody = tk.Frame(vcard, bg="white")
            vbody.pack(fill=tk.X, padx=8, pady=8)
            ttk.Label(vbody, text="Resumen BGP", font=("Arial", 12, "bold"), background="white", anchor="center", justify="center").pack(fill=tk.X, pady=(2, 6))
            ttk.Label(vbody, text=f"Local AS: {asn or 'N/A'}", background="white", anchor="center", justify="center").pack(fill=tk.X)
            ttk.Label(vbody, text=f"Router-ID: {v.get('router_id','') or router_id or 'N/A'}", background="white", anchor="center", justify="center").pack(fill=tk.X, pady=(0, 6))
            # Botón para obtener información bajo demanda en VRF
            vrfname = v.get("name", "")
            ttk.Button(
                vbody,
                text="Obtener información",
                command=lambda n=vrfname: self._fetch_and_render(scope="vrf", vendor=vendor, vrf_name=n)
            ).pack(pady=(0, 8))
            # Tabla única de resumen BGP por VRF
            # No autopoblar: se llenará al presionar el botón
            vrows: List[tuple] = []
            # Área contenedor por VRF para reconstruir la tabla
            if not hasattr(self, "_vrf_table_areas"):
                self._vrf_table_areas = {}
            varea = ttk.Frame(vbody, style="Card.TFrame")
            varea.pack(fill=tk.X, expand=False)
            self._vrf_table_areas[vrfname] = varea
            self._build_table(varea, [
                "NEIGHBOR", "V", "AS", "MSGRCVD", "MSGSENT", "TBLVER", "INQ", "OUTQ", "UP/DOWN", "STATE/PFXRCD"
            ], vrows)

    def _fetch_and_render(self, scope: str, vendor: str, vrf_name: str = "") -> None:
        """Obtiene resumen BGP en vivo y actualiza la tabla correspondiente."""
        conn = self.shared_data.get("connection_data", {}) or {}
        proto = conn.get("protocol", "SSH2")

        # Deshabilitar paginación si no está marcada aún
        try:
            if not bool(conn.get("paging_disabled")):
                for p in DISABLE_PAGING.get(vendor, []):
                    if proto == "SSH2":
                        _ = run_ssh_command(conn, p)
                    elif proto == "Telnet":
                        _ = run_telnet_command(conn, p, vendor=vendor)
                    elif proto == "Serial":
                        _ = run_serial_command(conn, p)
                conn["paging_disabled"] = True
        except Exception:
            pass

        # Comando por vendor/ámbito
        cmd = ""
        if vendor.startswith("cisco"):
            cmd = "show ip bgp sum" if scope == "global" else f"show ip bgp vpnv4 vrf {vrf_name} summary"
        elif vendor.startswith("huawei"):
            cmd = "display bgp peer" if scope == "global" else f"display bgp vpnv4 vpn-instance {vrf_name} peer"

        if not cmd:
            return

        # Ejecutar comando
        try:
            if proto == "SSH2":
                output = run_ssh_command(conn, cmd)
            elif proto == "Telnet":
                output = run_telnet_command(conn, cmd, vendor=vendor)
            elif proto == "Serial":
                output = run_serial_command(conn, cmd)
            else:
                output = ""
        except Exception:
            output = ""

        # Parsear y renderizar
        try:
            if vendor.startswith("cisco"):
                parsed = parse_cisco_bgp_summary(output)
            else:
                parsed = parse_huawei_bgp_peer(output)
        except Exception:
            parsed = []

        rows = [
            (
                r.get("ip", ""), r.get("v", ""), r.get("as", ""), r.get("msg_rcvd", ""),
                r.get("msg_sent", ""), r.get("tblver", ""), r.get("inq", ""), r.get("outq", ""),
                r.get("updown", ""), r.get("pref_rcv", "") or r.get("state", "")
            ) for r in parsed
        ]

        headers = [
            "NEIGHBOR", "V", "AS", "MSGRCVD", "MSGSENT", "TBLVER", "INQ", "OUTQ", "UP/DOWN", "STATE/PFXRCD"
        ]

        # Limpiar y reconstruir la tabla en el área adecuada
        if scope == "global":
            area = getattr(self, "_global_table_area", None)
        else:
            area = getattr(self, "_vrf_table_areas", {}).get(vrf_name)
        if area:
            for w in area.winfo_children():
                try:
                    w.destroy()
                except Exception:
                    pass
            self._build_table(area, headers, rows)

        # Bloque final de configuración completa BGP (comando por vendor)
        cfg_label = ttk.Label(container, text="Configuración BGP (sección filtrada)", font=("Arial", 11, "bold"), background="white")
        cfg_label.pack(anchor="w", pady=(10, 2))
        cmd_frame = ttk.Frame(container, style="Card.TFrame", padding=(10, 10))
        cmd_frame.pack(fill=tk.X, expand=False)
        mono = ("Consolas", 10)
        if vendor.startswith("cisco"):
            tk.Label(cmd_frame, text="CISCO#show running-config | sec bgp", font=mono, bg="white").pack(anchor="w")
        elif vendor.startswith("huawei"):
            tk.Label(cmd_frame, text="<HUAWEI>display current-configuration | sec inc bgp", font=mono, bg="white").pack(anchor="w")
            tk.Label(cmd_frame, text="o display current-configuration | sec bgp (depende del modelo)", font=("Arial", 9), bg="white").pack(anchor="w", pady=(4,0))
        else:
            tk.Label(cmd_frame, text="CISCO#show running-config | sec bgp", font=mono, bg="white").pack(anchor="w")
            tk.Label(cmd_frame, text="<HUAWEI>display current-configuration | sec inc bgp", font=mono, bg="white").pack(anchor="w", pady=(6,0))
            tk.Label(cmd_frame, text="o display current-configuration | sec bgp (depende del modelo)", font=("Arial", 9), bg="white").pack(anchor="w")

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
        table.pack(fill=tk.X, expand=False, padx=10, pady=6)
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
                        anchor="center",
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
                anchor="center",
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

        panel_header_text = f"Estado: {'Habilitado' if enabled else 'Deshabilitado'}  |  AS: {asn or 'N/A'}  |  IP del Router: {router_ip}"
        ttk.Label(summary_frame, text=panel_header_text, background="white", anchor="center", justify="center").pack(fill=tk.X)
        # Pestañas: GLOBAL y por VRF para el resumen
        vendor = (self.shared_data.get("parsed_data", {}).get("device_info", {}).get("vendor", "") or
                  self.shared_data.get("connection_data", {}).get("vendor_hint", "") or "").lower()
        router_id = bgp.get("router_id", "")
        vrfs = bgp.get("vrfs", []) or []

        notebook = ttk.Notebook(container)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(6, 10))

        # GLOBAL TAB
        global_tab = ttk.Frame(notebook, style="Card.TFrame")
        notebook.add(global_tab, text="GLOBAL")
        gsum = ttk.Frame(global_tab, style="Card.TFrame")
        gsum.pack(fill=tk.X, pady=(6, 6))
        header_text = f"Local AS: {asn or 'N/A'}  |  Router-ID: {router_id or 'N/A'}  |  Estado: {'Habilitado' if enabled else 'Deshabilitado'}"
        ttk.Label(gsum, text=header_text, background="white", anchor="center", justify="center").pack(fill=tk.X)

        ttk.Label(global_tab, text="Resumen BGP", font=("Arial", 11, "bold"), background="white", anchor="center", justify="center").pack(fill=tk.X, pady=(0, 6))
        ttk.Button(
            global_tab,
            text="Obtener información",
            command=lambda: self._fetch_and_render(scope="global", vendor=vendor)
        ).pack(pady=(0, 8))
        # No autopoblar: se llenará al presionar el botón
        rows: List[tuple] = []
        # Wrapper con padding para separar la tabla de los bordes
        gwrap = ttk.Frame(global_tab, style="Card.TFrame", padding=(10, 8))
        gwrap.pack(fill=tk.X, expand=False)
        # Guardar área para refrescar tras obtener datos
        self._global_table_area = gwrap
        self._build_table(gwrap, headers=[
            "Neighbor", "V", "AS", "MsgRcvd", "MsgSent", "TblVer", "InQ", "OutQ", "Up/Down", "State/PfxRcd"
        ], rows=rows)

        # VRF TABS
        for v in vrfs:
            vrf_tab = ttk.Frame(notebook, style="Card.TFrame")
            notebook.add(vrf_tab, text=f"VRF {v.get('name','')}")
            vsum = ttk.Frame(vrf_tab, style="Card.TFrame")
            vsum.pack(fill=tk.X, pady=(6, 6))
            v_header_text = f"Local AS: {asn or 'N/A'}  |  Router-ID: {v.get('router_id','') or router_id or 'N/A'}"
            ttk.Label(vsum, text=v_header_text, background="white", anchor="center", justify="center").pack(fill=tk.X)

            ttk.Label(vrf_tab, text="Resumen BGP", font=("Arial", 11, "bold"), background="white", anchor="center", justify="center").pack(fill=tk.X, pady=(0, 6))
            vrfname = v.get("name", "")
            ttk.Button(
                vrf_tab,
                text="Obtener información",
                command=lambda n=vrfname: self._fetch_and_render(scope="vrf", vendor=vendor, vrf_name=n)
            ).pack(pady=(0, 8))
            # Tabla única por VRF
            # No autopoblar: se llenará al presionar el botón
            vwrap = ttk.Frame(vrf_tab, style="Card.TFrame", padding=(10, 8))
            vwrap.pack(fill=tk.X, expand=False)
            if not hasattr(self, "_vrf_table_areas"):
                self._vrf_table_areas = {}
            self._vrf_table_areas[vrfname] = vwrap
            vrows: List[tuple] = []
            self._build_table(vwrap, [
                "Neighbor", "V", "AS", "MsgRcvd", "MsgSent", "TblVer", "InQ", "OutQ", "Up/Down", "State/PfxRcd"
            ], vrows)

        # Bloque final: configuración completa BGP (sección filtrada)
        cfg_label = ttk.Label(container, text="Configuración BGP (sección filtrada)", font=("Arial", 11, "bold"), background="white")
        cfg_label.pack(anchor="w", pady=(10, 2))
        cmd_frame = ttk.Frame(container, style="Card.TFrame", padding=(10, 10))
        cmd_frame.pack(fill=tk.X, expand=False)
        mono = ("Consolas", 10)
        if vendor.startswith("cisco"):
            tk.Label(cmd_frame, text="CISCO#show running-config | sec bgp", font=mono, bg="white").pack(anchor="w")
        elif vendor.startswith("huawei"):
            tk.Label(cmd_frame, text="<HUAWEI>display current-configuration | sec inc bgp", font=mono, bg="white").pack(anchor="w")
            tk.Label(cmd_frame, text="o display current-configuration | sec bgp (depende del modelo)", font=("Arial", 9), bg="white").pack(anchor="w", pady=(4,0))
        else:
            tk.Label(cmd_frame, text="CISCO#show running-config | sec bgp", font=mono, bg="white").pack(anchor="w")
            tk.Label(cmd_frame, text="<HUAWEI>display current-configuration | sec inc bgp", font=mono, bg="white").pack(anchor="w", pady=(6,0))
            tk.Label(cmd_frame, text="o display current-configuration | sec bgp (depende del modelo)", font=("Arial", 9), bg="white").pack(anchor="w")

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

    def _fetch_and_render(self, scope: str, vendor: str, vrf_name: str = "") -> None:
        """Obtiene resumen BGP en vivo y actualiza la tabla correspondiente en el panel."""
        conn = self.shared_data.get("connection_data", {}) or {}
        proto = conn.get("protocol", "SSH2")

        # Deshabilitar paginación si es necesario
        try:
            if not bool(conn.get("paging_disabled")):
                for p in DISABLE_PAGING.get(vendor, []):
                    if proto == "SSH2":
                        _ = run_ssh_command(conn, p)
                    elif proto == "Telnet":
                        _ = run_telnet_command(conn, p, vendor=vendor)
                    elif proto == "Serial":
                        _ = run_serial_command(conn, p)
                conn["paging_disabled"] = True
        except Exception:
            pass

        # Comando correcto por vendor/ámbito
        cmd = ""
        if vendor.startswith("cisco"):
            cmd = "show ip bgp sum" if scope == "global" else f"show ip bgp vpnv4 vrf {vrf_name} summary"
        elif vendor.startswith("huawei"):
            cmd = "display bgp peer" if scope == "global" else f"display bgp vpnv4 vpn-instance {vrf_name} peer"
        if not cmd:
            return

        # Ejecutar
        try:
            if proto == "SSH2":
                output = run_ssh_command(conn, cmd)
            elif proto == "Telnet":
                output = run_telnet_command(conn, cmd, vendor=vendor)
            elif proto == "Serial":
                output = run_serial_command(conn, cmd)
            else:
                output = ""
        except Exception:
            output = ""

        # Parsear
        try:
            if vendor.startswith("cisco"):
                parsed = parse_cisco_bgp_summary(output)
            else:
                parsed = parse_huawei_bgp_peer(output)
        except Exception:
            parsed = []

        rows = [
            (
                r.get("ip", ""), r.get("v", ""), r.get("as", ""), r.get("msg_rcvd", ""),
                r.get("msg_sent", ""), r.get("tblver", ""), r.get("inq", ""), r.get("outq", ""),
                r.get("updown", ""), r.get("pref_rcv", "") or r.get("state", "")
            ) for r in parsed
        ]

        headers = [
            "Neighbor", "V", "AS", "MsgRcvd", "MsgSent", "TblVer", "InQ", "OutQ", "Up/Down", "State/PfxRcd"
        ]

        # Elegir el área a refrescar
        if scope == "global":
            area = getattr(self, "_global_table_area", None)
        else:
            area = getattr(self, "_vrf_table_areas", {}).get(vrf_name)
        if area:
            for w in area.winfo_children():
                try:
                    w.destroy()
                except Exception:
                    pass
            self._build_table(area, headers, rows)
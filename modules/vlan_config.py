import tkinter as tk
from tkinter import ttk

class VLANConfigFrame(tk.Frame):
    def __init__(self, parent, shared_data):
        super().__init__(parent)
        self.shared_data = shared_data
        
        self.configure(bg='#ffffff')
        
        label = ttk.Label(self, text="Configuración de VLAN", font=("Arial", 16))
        label.pack(pady=20, padx=20)

        # Aquí irá el contenido para la configuración de VLAN

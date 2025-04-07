# main.py
import customtkinter as ctk
import sqlite3
from tkinter import messagebox
import sys
import os

# Función para obtener la ruta base
def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

BASE_PATH = get_base_path()
DB_PATH = os.path.join(BASE_PATH, "DatosApp.db")

from actualizar_plan import UpdatePlanWindow
from actualizar_equivalencias import UpdateEquivalencesWindow
from consultar_estudiantes import ConsultarEstudiantesWindow
from realizar_estudio import NuevoEstudioWindow

# Función para obtener los datos del plan desde la BD
def fetch_plan_details(db_path=DB_PATH):
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT Codigo_plan, Nombre_plan FROM Planes_de_estudio")
            result = cursor.fetchone()
            if result:
                codigo_plan, nombre_plan = result
            else:
                codigo_plan, nombre_plan = "N/A", "N/A"
    except Exception as e:
        codigo_plan, nombre_plan = "N/A", "N/A"
    return codigo_plan, nombre_plan

# Ventana modal para actualizar el registro único de Planes_de_estudio
class UpdatePlanModal:
    def __init__(self, parent, db_path=DB_PATH, update_callback=None):
        self.parent = parent
        self.db_path = db_path
        self.update_callback = update_callback
        
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Modificar Plan de Estudios")
        self.window.geometry("400x250")
        self.window.transient(parent)
        self.window.grab_set()

        # Se obtienen los datos actuales del plan
        codigo_plan, nombre_plan = fetch_plan_details(db_path)

        label_nombre = ctk.CTkLabel(self.window, text="Nombre del Plan:")
        label_nombre.pack(pady=(20, 5))
        self.entry_nombre = ctk.CTkEntry(self.window)
        self.entry_nombre.insert(0, nombre_plan)
        self.entry_nombre.pack(pady=5, padx=20, fill="x")

        label_codigo = ctk.CTkLabel(self.window, text="Código del Plan:")
        label_codigo.pack(pady=(10, 5))
        self.entry_codigo = ctk.CTkEntry(self.window)
        self.entry_codigo.insert(0, codigo_plan)
        self.entry_codigo.pack(pady=5, padx=20, fill="x")

        save_button = ctk.CTkButton(self.window, text="Guardar", command=self.save_changes)
        save_button.pack(pady=20)

    def save_changes(self):
        new_nombre = self.entry_nombre.get().strip()
        new_codigo = self.entry_codigo.get().strip()
        if not new_nombre or not new_codigo:
            messagebox.showerror("Error", "Ambos campos son obligatorios.")
            return
        try:
            with sqlite3.connect(self.db_path, timeout=5) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE Planes_de_estudio SET Nombre_plan = ?, Codigo_plan = ?", (new_nombre, new_codigo))
                conn.commit()
            messagebox.showinfo("Éxito", "Plan de estudios actualizado correctamente.")
            self.window.destroy()
            if self.update_callback:
                self.update_callback(new_nombre, new_codigo)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el plan: {e}")

# Configuración inicial de la ventana principal
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Menú de Dobles Titulaciones")
root.geometry("1000x550")  # Tamaño inicial

# === Función de cierre limpio ===
def cerrar_aplicacion():
    try:
        root.destroy()  # Cierra la ventana de Tkinter
    except:
        pass
    sys.exit()  # Finaliza el proceso de Python

root.protocol("WM_DELETE_WINDOW", cerrar_aplicacion)
# ===================================

# Obtener los datos del plan para el encabezado
codigo_plan, nombre_plan = fetch_plan_details()

# Crear un frame para el encabezado y el botón de edición
header_frame = ctk.CTkFrame(root, fg_color="#65C2C6", corner_radius=8)
header_frame.pack(fill="x", pady=(10, 20))

plan_text = f"Programa: {nombre_plan} ({codigo_plan})"
plan_label = ctk.CTkLabel(header_frame, text=plan_text,
                          font=("Arial", 16), fg_color="#65C2C6", text_color="black", corner_radius=8, height=40)
plan_label.pack(side="left", padx=10)

# Función para abrir la ventana modal de actualización del plan
def open_update_plan_modal():
    def update_header(new_nombre, new_codigo):
        new_text = f"Programa: {new_nombre} ({new_codigo})"
        plan_label.configure(text=new_text)
    UpdatePlanModal(root, db_path=DB_PATH, update_callback=update_header)

# Botón de edición al lado del encabezado
edit_button = ctk.CTkButton(header_frame, text="( Modificar ✍)", font=("Arial", 16),
                            fg_color="#65C2C6", text_color="black", width=40,
                            command=open_update_plan_modal)
edit_button.pack(side="left", padx=10)

# Título principal
main_label = ctk.CTkLabel(root, text="¡Bienvenido al aplicativo de manejo de\nDobles Titulaciones!",
                          font=("Arial", 20, "bold"), text_color="black", justify="center")
main_label.pack(pady=10)

# Funciones para abrir nuevas ventanas
def abrir_actualizar_plan():
    root.withdraw()
    UpdatePlanWindow(root, plan_text)

def abrir_actualizar_equivalencias():
    root.withdraw()
    UpdateEquivalencesWindow(root, plan_text)

def consultar_estudiantes_aprobados():
    root.withdraw()
    ConsultarEstudiantesWindow(root, plan_text)

def abrir_nuevo_estudio():
    root.withdraw()  
    NuevoEstudioWindow(root, plan_text)

# Botones del menú principal
buttons_text = [
    "Actualizar Plan de Estudios en Origen",
    "Actualizar la tabla de equivalencias y convalidaciones",
    "Realizar un nuevo estudio de Doble Titulación",
    "Consultar y actualizar Historias Académicas en DT"
]

for text in buttons_text:
    if text == "Actualizar Plan de Estudios en Origen":
        command = abrir_actualizar_plan
    elif text == "Actualizar la tabla de equivalencias y convalidaciones":
        command = abrir_actualizar_equivalencias 
    elif text == "Consultar y actualizar Historias Académicas en DT":
        command = consultar_estudiantes_aprobados
    elif text == "Realizar un nuevo estudio de Doble Titulación":
        command = abrir_nuevo_estudio
    else:
        command = None

    button = ctk.CTkButton(root, text=text, font=("Arial", 16), height=40, fg_color="#65C2C6",
                           hover_color="#519899", text_color="black", corner_radius=20, command=command)
    button.pack(fill="x", padx=50, pady=10)

root.mainloop()

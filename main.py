# main.py
import customtkinter as ctk
from actualizar_plan import UpdatePlanWindow
from actualizar_equivalencias import UpdateEquivalencesWindow
from consultar_estudiantes import ConsultarEstudiantesWindow
from realizar_estudio import NuevoEstudioWindow

# Configurar el modo de apariencia
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# Ventana principal
root = ctk.CTk()
root.title("Menú de Dobles Titulaciones")
root.geometry("1000x700")  # Tamaño inicial de la ventana

# Título del programa
program_label = ctk.CTkLabel(root, text="Programa: Ciencias de la Computación (2933)",
                             font=("Arial", 16), fg_color="#65C2C6", text_color="black", corner_radius=8, height=40)
program_label.pack(fill="x", pady=(10, 20))

# Título principal
main_label = ctk.CTkLabel(root, text="¡Bienvenido al aplicativo de manejo de\nDobles Titulaciones!",
                          font=("Arial", 20, "bold"), text_color="black", justify="center")
main_label.pack(pady=10)

# Funciones para abrir nuevas ventanas
def abrir_actualizar_plan():
    root.withdraw()  # Oculta la ventana principal
    UpdatePlanWindow(root)  # Abre la ventana de actualizar plan

def abrir_actualizar_equivalencias():
    #root.withdraw()  # Oculta la ventana principal
    UpdateEquivalencesWindow(root)  # Abre la ventana de equivalencias

def consultar_estudiantes_aprobados():
    #root.withdraw()  # Oculta la ventana principal
    ConsultarEstudiantesWindow(root)  # Abre la ventana para consultar estudiantes

def abrir_nuevo_estudio():
    #root.withdraw()  # Oculta la ventana principal
    NuevoEstudioWindow(root)  # Abre la ventana para realizar el estudio de doble titulación

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
        command = None  # Otros botones pueden no tener funcionalidad aún

    # Crear solo un botón por iteración
    button = ctk.CTkButton(root, text=text, font=("Arial", 16), height=40, fg_color="#65C2C6",
                           hover_color="#519899", text_color="black", corner_radius=20, command=command)
    button.pack(fill="x", padx=50, pady=10)

# Ejecutar la ventana principal
root.mainloop()
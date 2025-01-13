import customtkinter as ctk
from tkinter import PhotoImage
from actualizar_plan import UpdatePlanWindow  # Importa la clase desde otro archivo

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

# Función para abrir la ventana de "Actualizar Plan de Estudios en Origen"
def abrir_actualizar_plan():
    UpdatePlanWindow(root)  # Abre la ventana nueva

# Botones del menú principal
buttons_text = [
    "Actualizar Plan de Estudios en Origen",
    "Actualizar la tabla de equivalencias y convalidaciones",
    "Realizar un nuevo estudio de Doble Titulación",
    "Consultar y actualizar Historias Académicas en DT"
]

for text in buttons_text:
    # Agregar funcionalidad al botón de "Actualizar Plan de Estudios en Origen"
    command = abrir_actualizar_plan if text == "Actualizar Plan de Estudios en Origen" else None
    button = ctk.CTkButton(root, text=text, font=("Arial", 16), height=40, fg_color="#65C2C6",
                           hover_color="#519899", text_color="black", corner_radius=20, command=command)
    button.pack(fill="x", padx=50, pady=10)

# Ejecutar la ventana principal
root.mainloop()

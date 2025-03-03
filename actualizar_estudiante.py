import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import shutil

class ActualizarEstudianteWindow:
    def __init__(self, parent, nombre_estudiante, identificacion):
        self.parent = parent  # Guarda una referencia a la ventana principal
        self.window = ctk.CTkToplevel(parent)
        self.window.title(f"Actualización: {nombre_estudiante} ({identificacion})")
        self.window.geometry("950x600")

        # Opcional: al cerrar la ventana con la X de la barra, vuelve al menú
        self.window.protocol("WM_DELETE_WINDOW", self.return_to_main_menu)

        # Encabezado
        header_frame = ctk.CTkFrame(self.window, fg_color="#65C2C6", corner_radius=8)
        header_frame.pack(fill="x", pady=(10, 5))

        menu_button = ctk.CTkButton(
            header_frame,
            text="Menú principal",
            font=("Arial", 14),
            fg_color="white",
            text_color="black",
            hover_color="#E0E0E0",
            corner_radius=8,
            command=self.return_to_main_menu  # Regresar al menú principal
        )
        menu_button.pack(side="left", padx=10, pady=10)

        title_label = ctk.CTkLabel(
            header_frame,
            text="Programa: Ciencias de la Computación (2933)",
            font=("Arial", 16, "bold"),
            text_color="black",
        )
        title_label.pack(side="left", padx=10)

        # Título principal
        main_label = ctk.CTkLabel(
            self.window,
            text=f"Actualización: {nombre_estudiante} ({identificacion})",
            font=("Arial", 18, "bold")
        )
        main_label.pack(pady=10)

        # Frame para botones de archivos
        files_frame = ctk.CTkFrame(self.window)
        files_frame.pack(pady=10)

        # Historia Académica 1
        label_plan1 = ctk.CTkLabel(files_frame, text="Historia académica 1: Origen")
        label_plan1.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.button_plan1 = ctk.CTkButton(
            files_frame,
            text="Elegir archivo",
            command=self.elegir_archivo_plan1
        )
        self.button_plan1.grid(row=0, column=1, padx=10, pady=5)

        # Historia Académica 2
        label_plan2 = ctk.CTkLabel(files_frame, text="Historia académica 2: 2933-CC")
        label_plan2.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.button_plan2 = ctk.CTkButton(
            files_frame,
            text="Elegir archivo",
            command=self.elegir_archivo_plan2
        )
        self.button_plan2.grid(row=1, column=1, padx=10, pady=5)

        # Botón "Subir historias académicas"
        upload_button = ctk.CTkButton(
            self.window,
            text="Subir historias académicas",
            fg_color="#65C2C6",
            text_color="black",
            font=("Arial", 14, "bold"),
            command=self.subir_historias
        )
        upload_button.pack(pady=10)

        # Label para resultados
        self.result_label = ctk.CTkLabel(self.window, text="")
        self.result_label.pack()

    def elegir_archivo_plan1(self):
        """Selecciona el PDF para Plan1 y lo copia a la carpeta 'Uploaded_Files'."""
        ruta_archivo = filedialog.askopenfilename(
            title="Seleccionar archivo PDF (Plan de Origen)",
            filetypes=[("Archivos PDF", "*.pdf")]
        )
        if ruta_archivo:
            os.makedirs("Uploaded_Files", exist_ok=True)
            destino = os.path.join("Uploaded_Files", "Plan1.pdf")
            shutil.copy(ruta_archivo, destino)
            self.pdf_plan1_path = destino
            self.button_plan1.configure(fg_color="#00FF00")  # Cambiar color a verde

    def elegir_archivo_plan2(self):
        """Selecciona el PDF para Plan2 y lo copia a la carpeta 'Uploaded_Files'."""
        ruta_archivo = filedialog.askopenfilename(
            title="Seleccionar archivo PDF (CC-2933)",
            filetypes=[("Archivos PDF", "*.pdf")]
        )
        if ruta_archivo:
            os.makedirs("Uploaded_Files", exist_ok=True)
            destino = os.path.join("Uploaded_Files", "Plan2.pdf")
            shutil.copy(ruta_archivo, destino)
            self.pdf_plan2_path = destino
            self.button_plan2.configure(fg_color="#00FF00")  # Cambiar color a verde

    def subir_historias(self):
        """Llama a la función Actualizar_Historia del módulo funciones_estudio.py."""
        if not hasattr(self, 'pdf_plan1_path') or not hasattr(self, 'pdf_plan2_path'):
            messagebox.showerror("Error", "Debes elegir ambos archivos PDF antes de subir.")
            return

        try:
            from funciones_estudio import Actualizar_Historia
            df_resultado = Actualizar_Historia(self.pdf_plan1_path, self.pdf_plan2_path)
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al procesar las historias académicas:\n{e}")
            return

        self.result_label.configure(text="Se encontraron las siguientes equivalencias/convalidaciones:")
        # Aquí puedes agregar la lógica para mostrar los resultados en un Treeview.

    def return_to_main_menu(self):
        """Cierra la ventana secundaria y vuelve a mostrar el menú principal."""
        self.window.destroy()  # Cierra la ventana secundaria
        self.parent.deiconify()  # Muestra la ventana principal nuevamente
        self.parent.lift()       # Levanta la ventana principal
        self.parent.focus_force()  # Forzar el foco a la ventana principal

# Ejemplo de ejecución directa (para pruebas)
if __name__ == "__main__":
    ctk.set_appearance_mode("Light")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.withdraw()  # Para no mostrar la ventana raíz
    app = ActualizarEstudianteWindow(
        parent=root,
        nombre_estudiante="Pepe Grillo Sanchez Garzón",
        identificacion="1000158341"
    )
    root.mainloop()
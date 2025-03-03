import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import shutil
import os
from datetime import datetime

# Se asume que en funciones_estudio.py hay una función:
#     def Actualizar_Historia(pdf_plan1: str, pdf_plan2: str) -> pd.DataFrame:
#         ...
# que recibe las rutas de los PDF y retorna un DataFrame con las columnas:
# Periodo_Academico, Codigo, Asignatura, Codigo_CC, Asignatura_CC, Agrupacion, Nota, Tipo, Creditos

class ActualizarEstudianteWindow:
    def __init__(self, parent, nombre_estudiante, identificacion, db_path="DatosApp.db"):
        """
        :param parent: Ventana padre (por lo general un CTk o Toplevel)
        :param nombre_estudiante: Nombre completo del estudiante (str)
        :param identificacion: Identificación del estudiante (str)
        :param db_path: Ruta de la BD (por si se requiere en un futuro)
        """
        self.window = ctk.CTkToplevel(parent)
        self.window.title(f"Actualización: {nombre_estudiante} ({identificacion})")
        self.window.geometry("950x600")
        self.db_path = db_path

        self.nombre_estudiante = nombre_estudiante
        self.identificacion = identificacion

        # Variables para guardar rutas de PDF
        self.pdf_plan1_path = None
        self.pdf_plan2_path = None

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
            command=self.window.destroy
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
            text=f"Actualización: {self.nombre_estudiante} ({self.identificacion})",
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

        # Tabla (Treeview) para mostrar las equivalencias
        columns = ("Periodo Académico", "Código", "Asignatura", "Código_CC", 
                   "Asignatura_CC", "Agrupación", "Nota", "Tipo", "Créditos")
        self.tree = ttk.Treeview(self.window, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Botón "Guardar actualización"
        save_button = ctk.CTkButton(
            self.window,
            text="Guardar actualización",
            fg_color="#65C2C6",
            text_color="black",
            font=("Arial", 14, "bold"),
            command=self.guardar_cambios
        )
        save_button.pack(pady=10)

    def elegir_archivo_plan1(self):
        """Selecciona el PDF para Plan1 y lo copia a la carpeta 'Uploaded_Files'. Luego cambia el color del botón a verde."""
        ruta_archivo = filedialog.askopenfilename(
            title="Seleccionar archivo PDF (Plan de Origen)",
            filetypes=[("Archivos PDF", "*.pdf")]
        )
        if ruta_archivo:
            # Creamos la carpeta si no existe
            os.makedirs("Uploaded_Files", exist_ok=True)
            destino = os.path.join("Uploaded_Files", "Plan1.pdf")
            shutil.copy(ruta_archivo, destino)
            self.pdf_plan1_path = destino
            # Cambiar el color del botón a verde
            self.button_plan1.configure(fg_color="#00FF00")

    def elegir_archivo_plan2(self):
        """Selecciona el PDF para Plan2 y lo copia a la carpeta 'Uploaded_Files'. Luego cambia el color del botón a verde."""
        ruta_archivo = filedialog.askopenfilename(
            title="Seleccionar archivo PDF (CC-2933)",
            filetypes=[("Archivos PDF", "*.pdf")]
        )
        if ruta_archivo:
            # Creamos la carpeta si no existe
            os.makedirs("Uploaded_Files", exist_ok=True)
            destino = os.path.join("Uploaded_Files", "Plan2.pdf")
            shutil.copy(ruta_archivo, destino)
            self.pdf_plan2_path = destino
            # Cambiar el color del botón a verde
            self.button_plan2.configure(fg_color="#00FF00")

    def subir_historias(self):
        """
        Llama a la función Actualizar_Historia del módulo funciones_estudio.py
        con las rutas de los dos PDFs y muestra el DataFrame en el Treeview.
        """
        if not self.pdf_plan1_path or not self.pdf_plan2_path:
            messagebox.showerror("Error", "Debes elegir ambos archivos PDF antes de subir.")
            return

        try:
            from funciones_estudio import Actualizar_Historia
            df_resultado = Actualizar_Historia(self.pdf_plan1_path, self.pdf_plan2_path)
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al procesar las historias académicas:\n{e}")
            return

        # Limpiamos el Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Cambiamos el texto del label
        self.result_label.configure(text="Se encontraron las siguientes equivalencias/convalidaciones:")

        # Insertamos los datos del DataFrame en la tabla
        for _, row in df_resultado.iterrows():
            self.tree.insert("", "end", values=(
                row.get("Periodo Académico", ""),
                row.get("Código", ""),
                row.get("Asignatura", ""),
                row.get("Código_CC", ""),
                row.get("Asignatura_CC", ""),
                row.get("Agrupación", ""),
                row.get("Nota", ""),
                row.get("Tipo", ""),
                row.get("Créditos", "")
            ))

    def guardar_cambios(self):
        """
        Por ahora, el botón "Guardar actualización" simplemente cierra esta ventana.
        (En el futuro se podría implementar más lógica, si se requiere).
        """
        self.window.destroy()


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

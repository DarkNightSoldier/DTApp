# actualizar_estudiante.py
import customtkinter as ctk 
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import shutil
import os
import sys
from datetime import datetime

# Función para obtener la ruta base (carpeta del ejecutable o del script)
def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

BASE_PATH = get_base_path()
DB_PATH = os.path.join(BASE_PATH, "DatosApp.db")
UPLOADED_DIR = os.path.join(BASE_PATH, "Uploaded_Files")
ACTUALIZACIONES_DIR = os.path.join(BASE_PATH, "Actualizaciones")

class ActualizarEstudianteWindow:
    def __init__(self, parent, plan_text, nombre_estudiante, identificacion, codigo_plan_1, codigo_plan_2, db_path="DatosApp.db"):
        """
        :param parent: Ventana padre (por lo general un CTk o Toplevel)
        :param nombre_estudiante: Nombre completo del estudiante (str)
        :param identificacion: Identificación del estudiante (str)
        :param db_path: Ruta de la BD (por si se requiere en un futuro)
        """
        # Si se usa el valor por defecto, se utiliza la ruta absoluta
        if db_path == "DatosApp.db":
            self.db_path = DB_PATH
        else:
            self.db_path = db_path

        self.window = ctk.CTkToplevel(parent)
        self.plan_text = plan_text
        self.window.title(f"Actualización: {nombre_estudiante} ({identificacion})")
        self.window.geometry("950x600")
        self.window.transient(parent)
        self.window.grab_set()
        self.window.focus_set()

        self.nombre_estudiante = nombre_estudiante
        self.identificacion = identificacion
        self.codigo_plan_1 = codigo_plan_1
        self.codigo_plan_2 = codigo_plan_2

        # Variable para guardar el DataFrame resultado
        self.df_resultado = None

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
            text=self.plan_text,
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
        label_plan1 = ctk.CTkLabel(files_frame, text=f"Historia académica 1: {self.codigo_plan_1}")
        label_plan1.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.button_plan1 = ctk.CTkButton(
            files_frame,
            text="Elegir archivo",
            command=self.elegir_archivo_plan1
        )
        self.button_plan1.grid(row=0, column=1, padx=10, pady=5)

        # Historia Académica 2
        label_plan2 = ctk.CTkLabel(files_frame, text=f"Historia académica 2: {self.codigo_plan_2}")
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
        columns = ("Periodo Académico", "Código", "Asignatura", "Código_P2", 
                   "Asignatura_P2", "Agrupación", "Nota", "Tipo", "Créditos")
        self.tree = ttk.Treeview(self.window, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Botón "Exportar a excel"
        export_button = ctk.CTkButton(
            self.window,
            text="Exportar a excel",
            fg_color="#65C2C6",
            text_color="black",
            font=("Arial", 14, "bold"),
            command=self.exportar_excel
        )
        export_button.pack(pady=10)

    def elegir_archivo_plan1(self):
        """Selecciona el PDF para Plan1 y lo copia a la carpeta 'Uploaded_Files'. Luego cambia el color del botón a verde."""
        ruta_archivo = filedialog.askopenfilename(
            title="Seleccionar archivo PDF (Plan de Origen)",
            filetypes=[("Archivos PDF", "*.pdf")]
        )
        if ruta_archivo:
            os.makedirs(UPLOADED_DIR, exist_ok=True)
            destino = os.path.join(UPLOADED_DIR, "Plan1.pdf")
            shutil.copy(ruta_archivo, destino)
            self.pdf_plan1_path = destino
            self.button_plan1.configure(fg_color="#00FF00")

    def elegir_archivo_plan2(self):
        """Selecciona el PDF para Plan2 y lo copia a la carpeta 'Uploaded_Files'. Luego cambia el color del botón a verde."""
        ruta_archivo = filedialog.askopenfilename(
            title="Seleccionar archivo PDF Plan 2",
            filetypes=[("Archivos PDF", "*.pdf")]
        )
        if ruta_archivo:
            os.makedirs(UPLOADED_DIR, exist_ok=True)
            destino = os.path.join(UPLOADED_DIR, "Plan2.pdf")
            shutil.copy(ruta_archivo, destino)
            self.pdf_plan2_path = destino
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
            # Guardar el DataFrame en un atributo para luego exportarlo
            self.df_resultado = df_resultado
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al procesar las historias académicas:\n{e}")
            return

        # Limpiamos el Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.result_label.configure(text="Se encontraron las siguientes equivalencias/convalidaciones:")

        # Insertamos los datos del DataFrame en el Treeview
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

    def exportar_excel(self):
        """
        Exporta el DataFrame df_resultado a un archivo Excel en la carpeta "Actualizaciones" 
        con el nombre "NombreEstudiante_Actualizacion.xlsx" y muestra una ventana emergente al terminar.
        """
        if self.df_resultado is None:
            messagebox.showerror("Error", "No hay datos para exportar. Primero debes subir las historias académicas.")
            return

        os.makedirs(ACTUALIZACIONES_DIR, exist_ok=True)
        filename = os.path.join(ACTUALIZACIONES_DIR, f"{self.nombre_estudiante}_Actualizacion.xlsx")
        
        try:
            self.df_resultado.rename(columns={"Código_CC": "Código", "Asignatura_CC": "Asignatura"}, inplace=True)
            self.df_resultado.to_excel(filename, index=False)
            messagebox.showinfo("Exportación completada", f"Archivo guardado: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al guardar el archivo:\n{e}")

# Ejemplo de ejecución directa (para pruebas)
if __name__ == "__main__":
    ctk.set_appearance_mode("Light")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.withdraw()  # Para no mostrar la ventana raíz
    app = ActualizarEstudianteWindow(
        parent=root,
        plan_text="Plan: Ejemplo (1234)",
        nombre_estudiante="Pepe Grillo Sanchez Garzón",
        identificacion="1000158341",
        codigo_plan_1="Plan001",
        codigo_plan_2="Plan002"
    )
    root.mainloop()

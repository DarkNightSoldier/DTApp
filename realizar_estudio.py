# realizar_estudio.py
import customtkinter as ctk
from tkinter import filedialog, StringVar, messagebox
import PyPDF2
from funciones_estudio import Realizar_Estudio
import sys
import os

# (Opcional) Función para obtener la ruta base si se requiere en el futuro
def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

BASE_PATH = get_base_path()
# En este módulo se leen PDFs a través de un diálogo, por lo que no es necesario modificar rutas relativas.

class NuevoEstudioWindow(ctk.CTkToplevel):
    def __init__(self, parent, plan_text):
        super().__init__(parent)
        self.parent = parent
        self.plan_text = plan_text
        
        self.title("Nuevo Estudio de Doble Titulación")
        self.geometry("800x600")

        # Encabezado
        header_frame = ctk.CTkFrame(self, fg_color="#65C2C6", corner_radius=8)
        header_frame.pack(fill="x", pady=(10, 5))

        # Botón para regresar al menú principal
        self.menu_button = ctk.CTkButton(
            header_frame,
            text="Menú principal",
            font=("Arial", 14),
            fg_color="white",
            text_color="black",
            hover_color="#E0E0E0",
            corner_radius=8,
            command=self.return_to_main_menu
        )
        self.menu_button.pack(side="left", padx=10, pady=10)

        title_label = ctk.CTkLabel(
            header_frame,
            text=self.plan_text,
            font=("Arial", 16, "bold"),
            text_color="black",
        )
        title_label.pack(side="left", padx=10)

        # Label de encabezado
        self.header_label = ctk.CTkLabel(
            self, 
            text="Creación: Nuevo estudio de doble titulación", 
            font=("Arial", 18, "bold"), 
            text_color="black"
        )
        self.header_label.pack(pady=15)

        # Botón para seleccionar el PDF
        self.load_pdf_button = ctk.CTkButton(
            self,
            text="Seleccionar PDF",
            command=self.open_pdf,
            fg_color="#65C2C6",
            hover_color="#519899",
            text_color="black",
            font=("Arial", 14, "bold"),
            corner_radius=8
        )
        self.load_pdf_button.pack(pady=10)

        # Cuadro de texto para mostrar el contenido extraído
        self.pdf_text_box = ctk.CTkTextbox(self, width=700, height=300)
        self.pdf_text_box.pack(pady=10)

        # Botón para realizar el estudio de doble titulación
        self.study_button = ctk.CTkButton(
            self,
            text="Realizar Estudio de Doble Titulación",
            command=self.realizar_estudio,
            fg_color="#65C2C6",
            hover_color="#519899",
            text_color="black",
            font=("Arial", 14, "bold"),
            corner_radius=8,
            state='disabled'
        )
        self.study_button.pack(pady=20)

        # Mensaje de estado
        self.status_label = ctk.CTkLabel(self, text="", font=("Arial", 16), text_color="black")
        self.status_label.pack(pady=10)

        # Variable para almacenar la ruta del PDF
        self.pdf_path = None

    def open_pdf(self):
        """Abre un cuadro de diálogo para seleccionar un archivo PDF y muestra su contenido."""
        self.pdf_path = filedialog.askopenfilename(
            title="Seleccionar PDF",
            filetypes=[("Archivos PDF", "*.pdf")]
        )
        if not self.pdf_path:
            return

        try:
            with open(self.pdf_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                content = []
                for page in reader.pages:
                    extracted_text = page.extract_text()
                    if extracted_text:
                        content.append(extracted_text)

            self.pdf_text_box.delete("1.0", "end")
            self.pdf_text_box.insert("1.0", "\n".join(content))
            self.study_button.configure(state='normal')
            self.status_label.configure(text="PDF cargado correctamente.")
        except Exception as e:
            self.pdf_text_box.delete("1.0", "end")
            self.pdf_text_box.insert("1.0", f"Error al leer el archivo PDF:\n{str(e)}")
            self.status_label.configure(text="Error al cargar el PDF.")

    def realizar_estudio(self):
        """Realiza el estudio y muestra el resultado en una ventana emergente.
           Al cerrar la ventana emergente, la ventana se restablece a su estado inicial.
        """
        if self.pdf_path:
            resultado = Realizar_Estudio(self.pdf_path)
            # Mostrar el resultado en una ventana emergente
            messagebox.showinfo("Estudio Generado", f"Estudio generado: {resultado}")
            # Restablecer la ventana principal a su estado inicial
            self.reset_window()
        else:
            messagebox.showerror("Error", "Por favor, selecciona un PDF primero.")

    def reset_window(self):
        """Restablece la ventana a su estado inicial sin archivo cargado."""
        self.pdf_path = None
        self.pdf_text_box.delete("1.0", "end")
        self.study_button.configure(state='disabled')
        self.status_label.configure(text="")

    def return_to_main_menu(self):
        """Regresa al menú principal."""
        self.destroy()
        self.parent.deiconify()


# Ejecución para pruebas
if __name__ == "__main__":
    ctk.set_appearance_mode("Light")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    root.geometry("800x600")
    NuevoEstudioWindow(root, plan_text="Plan: Ejemplo de Plan")
    root.mainloop()

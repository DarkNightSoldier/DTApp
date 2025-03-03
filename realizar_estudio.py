# realizar_estudio.py
import customtkinter as ctk
from tkinter import filedialog, StringVar
import PyPDF2
from funciones_estudio import Realizar_Estudio  # Asegúrate de que el nombre del archivo de funciones sea correcto

class NuevoEstudioWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        
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
            text_color="black",  # Color de texto gris
            hover_color="#E0E0E0",
            corner_radius=8,
            command=self.return_to_main_menu
        )
        self.menu_button.pack(side="left", padx=10, pady=10)

        title_label = ctk.CTkLabel(
            header_frame,
            text="Programa: Ciencias de la Computación (2933)",
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
        self.pdf_text_box = ctk.CTkTextbox(self, width=700, height=300)  # Ajustar altura
        self.pdf_text_box.pack(pady=10)

        # Botón para realizar el estudio de doble titulación
        self.study_button = ctk.CTkButton(
            self,
            text="Realizar Estudio de Doble Titulación",
            command=self.realizar_estudio,
            fg_color="#65C2C6",
            hover_color="#519899",
            text_color="black",  # Color de texto gris
            font=("Arial", 14, "bold"),
            corner_radius=8,
            state='disabled'  # Deshabilitar inicialmente
        )
        self.study_button.pack(pady=20)

        # Mensaje de estado
        self.status_label = ctk.CTkLabel(self, text="", font=("Arial", 12), text_color="black")
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
            return  # Si no se selecciona nada, no hacer nada

        try:
            # Se utiliza PyPDF2 para leer el contenido del PDF
            with open(self.pdf_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                content = []
                for page in reader.pages:
                    extracted_text = page.extract_text()
                    if extracted_text:
                        content.append(extracted_text)

            # Se limpia el cuadro de texto y se inserta el contenido
            self.pdf_text_box.delete("1.0", "end")
            self.pdf_text_box.insert("1.0", "\n".join(content))

            # Habilitar el botón de estudio
            self.study_button.configure(state='normal')
            self.status_label.configure(text="PDF cargado correctamente.")

        except Exception as e:
            # Manejo simple de errores
            self.pdf_text_box.delete("1.0", "end")
            self.pdf_text_box.insert(
                "1.0", 
                f"Error al leer el archivo PDF:\n{str(e)}"
            )
            self.status_label.configure(text="Error al cargar el PDF.")

    def realizar_estudio(self):
        """Llama a la función para realizar el estudio de doble titulación."""
        if self.pdf_path:
            resultado = Realizar_Estudio(self.pdf_path)
            self.status_label.configure(text=f"Estudio generado: {resultado}")  # Mostrar en la interfaz
        else:
            self.status_label.configure(text="Por favor, selecciona un PDF primero.")

    def return_to_main_menu(self):
        """Función para regresar al menú principal."""
        self.destroy()  # Cierra la ventana actual

# Ejecutar la ventana principal
if __name__ == "__main__":
    ctk.set_appearance_mode("Light")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.geometry("800x600")  # Tamaño de la ventana principal
    NuevoEstudioWindow(root)  # Crear la ventana de estudio
    root.mainloop()
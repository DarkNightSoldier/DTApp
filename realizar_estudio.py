import customtkinter as ctk
from tkinter import filedialog, Toplevel, Canvas, Frame, Scrollbar
import PyPDF2
from funciones_estudio import Realizar_Estudio 

class NuevoEstudioWindow:
    def __init__(self, parent):
        self.parent = parent  # Guarda una referencia a la ventana principal
        self.window = Toplevel(parent)        
        self.window.title("Nuevo Estudio de Doble Titulación")
        self.window.geometry("1300x900")
    
        # Encabezado
        header_frame = ctk.CTkFrame(self.window, fg_color="#65C2C6", corner_radius=8)
        header_frame.pack(fill="x", pady=(10, 5))

        # Botón para regresar al menú principal
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

        scroll_canvas = Canvas(self.window)
        scroll_canvas.pack(side="left", fill="both", expand=True)

        scrollbar = Scrollbar(self.window, command=scroll_canvas.yview)
        scrollbar.pack(side="right", fill="y")

        scroll_canvas.configure(yscrollcommand=scrollbar.set)
        scroll_frame = Frame(scroll_canvas)
        scroll_canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

        scroll_frame.bind(
            "<Configure>",
            lambda e: scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))
        )

        # Botón para seleccionar el PDF
        self.load_pdf_button = ctk.CTkButton(
            scroll_frame,
            text="Seleccionar PDF",
            command=self.open_pdf,
            fg_color="#65C2C6",
            hover_color="#519899",
            text_color="black",
            font=("Arial", 14, "bold"),
            corner_radius=8
        )
        self.load_pdf_button.pack(pady=10)  # Alinear a la izquierda

        # Cuadro de texto para mostrar el contenido extraído
        self.pdf_text_box = ctk.CTkTextbox(scroll_frame, width=800, height=300)  # Ajustar altura
        self.pdf_text_box.pack(pady=10)  # Alinear a la izquierda

        # Botón para realizar el estudio de doble titulación
        self.study_button = ctk.CTkButton(
            scroll_frame,
            text="Realizar Estudio de Doble Titulación",
            command=self.realizar_estudio,
            fg_color="#65C2C6",
            hover_color="#519899",
            text_color="black",  # Color de texto gris
            font=("Arial", 14, "bold"),
            corner_radius=8,
            state='disabled'  # Deshabilitar inicialmente
        )
        self.study_button.pack(pady=20)  # Alinear a la izquierda

        # Frame para el mensaje de estado (creado solo una vez)
        self.status_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        self.status_frame.pack(side="bottom", fill="x", pady=10, padx=10)

        # Mensaje de estado (creado solo una vez)
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="",
            font=("Arial", 12),
            text_color="black",
            anchor="w"  # Alineación horizontal a la izquierda
        )
        self.status_label.pack(side="left", padx=10, fill="x", expand=True)

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
            self.status_label.configure(text="PDF cargado correctamente.")  # Actualizar el mensaje

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
        self.window.destroy()  # Cierra la ventana actual
        self.parent.deiconify()  # Muestra la ventana principal de nuevo

# Ventana principal (menú)
if __name__ == "__main__":
    ctk.set_appearance_mode("Light")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk() 
    root.geometry("1000x700")
    NuevoEstudioWindow(root)  
    root.mainloop()
import customtkinter as ctk
from tkinter import Toplevel, PhotoImage, IntVar, StringVar, Label


class UpdatePlanWindow:
    def __init__(self, parent):
        self.window = Toplevel(parent)
        self.window.title("Actualizar Plan de Estudios en Origen")
        self.window.geometry("1000x700")

        # Encabezado principal
        header_frame = ctk.CTkFrame(self.window, fg_color="#65C2C6", corner_radius=8)
        header_frame.pack(fill="x", pady=(10, 5))

        # Botón "Menú principal"
        menu_button = ctk.CTkButton(
            header_frame,
            text="Menú principal",
            font=("Arial", 14),
            fg_color="white",
            text_color="black",
            hover_color="#E0E0E0",
            corner_radius=8,
            command=self.return_to_main_menu  # Acción al presionar
        )
        menu_button.pack(side="left", padx=10, pady=10)

        # Título del programa
        title_label = ctk.CTkLabel(
            header_frame,
            text="Programa: Ciencias de la Computación (2933)",
            font=("Arial", 16, "bold"),
            text_color="black",
        )
        title_label.pack(side="left", padx=10)

        # Tabla de resumen superior
        summary_frame = ctk.CTkFrame(self.window, fg_color="#F5F5F5", corner_radius=8)
        summary_frame.pack(fill="x", padx=10, pady=10)

        # Encabezados principales
        headers = [
            ("Fundamentación", 2),
            ("Disciplinar", 3),
            ("Libre Elección (L)", 1)
        ]
        subheaders = [
            ["Obligatorios (B)", "Optativos (O)"],
            ["Obligatorios (C)", "Optativos (T)", "Trabajo de Grado (P)"],
            [""]
        ]
        data = [
            [49, 11],
            [29, 22, 8],
            [28]
        ]

        # Encabezados principales
        col_start = 0
        for header, span in headers:
            label = Label(summary_frame, text=header, font=("Arial", 12, "bold"),
                          bg="#D3D3D3", relief="ridge", width=15 * span, height=2, anchor="center")
            label.grid(row=0, column=col_start, columnspan=span, sticky="nsew", padx=1, pady=1)
            col_start += span

        # Subencabezados
        col_start = 0
        for row in subheaders:
            for subheader in row:
                label = Label(summary_frame, text=subheader, font=("Arial", 10),
                              bg="#E8E8E8", relief="ridge", width=15, height=2, anchor="center")
                label.grid(row=1, column=col_start, sticky="nsew", padx=1, pady=1)
                col_start += 1

        # Datos
        col_start = 0
        for row_data in data:
            for value in row_data:
                label = Label(summary_frame, text=value, font=("Arial", 10),
                              bg="#FFFFFF", relief="ridge", width=15, height=2, anchor="center")
                label.grid(row=2, column=col_start, sticky="nsew", padx=1, pady=1)
                col_start += 1

        # Componente
        component_title = ctk.CTkLabel(self.window, text="Componente: Fundamentación",
                                       font=("Arial", 18, "bold"), text_color="black")
        component_title.pack(pady=10)

        # Tabla principal
        table_frame = ctk.CTkFrame(self.window, fg_color="white", corner_radius=8)
        table_frame.pack(fill="x", padx=10, pady=10)

        # Tabla de asignaturas
        headers = ["Código", "Nombre de la asignatura", "Créditos", "B", "O", "Modificar"]
        for i, header in enumerate(headers):
            header_label = ctk.CTkLabel(table_frame, text=header, font=("Arial", 12, "bold"), text_color="black")
            header_label.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")

        # Datos
        subjects = [
            ["2026573", "Introducción a las ciencias de la computación", 3],
            ["2016375", "Programación orientada a objetos", 3],
            ["2016699", "Estructuras de datos", 3]
        ]

        for row, subject in enumerate(subjects, start=1):
            code_var = StringVar(value=subject[0])
            name_var = StringVar(value=subject[1])
            credit_var = StringVar(value=subject[2])

            # Código
            code_entry = ctk.CTkEntry(table_frame, textvariable=code_var, state="readonly", width=100)
            code_entry.grid(row=row, column=0, padx=5, pady=5)

            # Nombre
            name_entry = ctk.CTkEntry(table_frame, textvariable=name_var, state="readonly", width=250)
            name_entry.grid(row=row, column=1, padx=5, pady=5)

            # Créditos
            credit_entry = ctk.CTkEntry(table_frame, textvariable=credit_var, state="readonly", width=50)
            credit_entry.grid(row=row, column=2, padx=5, pady=5)

            # Checkboxes
            b_var = IntVar(value=1 if row == 1 else 0)
            b_checkbox = ctk.CTkCheckBox(table_frame, variable=b_var, text="")
            b_checkbox.grid(row=row, column=3, padx=5, pady=5)

            o_var = IntVar(value=0)
            o_checkbox = ctk.CTkCheckBox(table_frame, variable=o_var, text="")
            o_checkbox.grid(row=row, column=4, padx=5, pady=5)

            # Botón de lápiz
            pencil_img = PhotoImage(file="pencil.png").subsample(12, 12)
            pencil_button = ctk.CTkButton(table_frame, text="", image=pencil_img, width=40, height=40,
                                          command=lambda e=[code_entry, name_entry, credit_entry]: self.enable_edit(e))
            pencil_button.image = pencil_img  # Prevenir pérdida de referencia
            pencil_button.grid(row=row, column=5, padx=5, pady=5)

        # Botón "Agregar agrupación"
        add_button = ctk.CTkButton(self.window, text="Agregar agrupación", font=("Arial", 14),
                                   fg_color="#65C2C6", hover_color="#519899", text_color="white")
        add_button.pack(pady=10)

    def return_to_main_menu(self):
        """Cerrar ventana y retornar al menú principal."""
        self.window.destroy()

    def enable_edit(self, entries):
        """Habilitar edición."""
        for entry in entries:
            entry.configure(state="normal")


# Ventana principal para prueba
if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("1200x800")
    UpdatePlanWindow(root)
    root.mainloop()

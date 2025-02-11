import customtkinter as ctk
from tkinter import Toplevel, Canvas, Frame, Scrollbar, IntVar, StringVar, Label


class UpdatePlanWindow:
    def __init__(self, parent):
        self.window = Toplevel(parent)
        self.window.title("Actualizar Plan de Estudios en Origen")
        self.window.geometry("1200x700")

        # Encabezado principal
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
            command=self.return_to_main_menu
        )
        menu_button.pack(side="left", padx=10, pady=10)

        title_label = ctk.CTkLabel(
            header_frame,
            text="Programa: Ciencias de la Computación (2933)",
            font=("Arial", 16, "bold"),
            text_color="black",
        )
        title_label.pack(side="left", padx=10)

        # Contenedor de desplazamiento
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

        # Tabla de resumen superior (con colores grises y diseño original)
        summary_frame = ctk.CTkFrame(scroll_frame, fg_color="#F5F5F5", corner_radius=8)
        summary_frame.pack(fill="x", padx=10, pady=10)

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

        col_start = 0
        for header, span in headers:
            label = Label(summary_frame, text=header, font=("Arial", 12, "bold"),
                          bg="#D3D3D3", relief="ridge", width=15 * span, height=2, anchor="center")
            label.grid(row=0, column=col_start, columnspan=span, sticky="nsew", padx=1, pady=1)
            col_start += span

        col_start = 0
        for row in subheaders:
            for subheader in row:
                label = Label(summary_frame, text=subheader, font=("Arial", 10),
                              bg="#E8E8E8", relief="ridge", width=15, height=2, anchor="center")
                label.grid(row=1, column=col_start, sticky="nsew", padx=1, pady=1)
                col_start += 1

        col_start = 0
        for row_data in data:
            for value in row_data:
                label = Label(summary_frame, text=value, font=("Arial", 10),
                              bg="#FFFFFF", relief="ridge", width=15, height=2, anchor="center")
                label.grid(row=2, column=col_start, sticky="nsew", padx=1, pady=1)
                col_start += 1

        # Componente
        component_title = ctk.CTkLabel(scroll_frame, text="Componente: Fundamentación",
                                       font=("Arial", 18, "bold"), text_color="black")
        component_title.pack(pady=10)

        grouping_frame = ctk.CTkFrame(scroll_frame, fg_color="#F5F5F5", corner_radius=8)
        grouping_frame.pack(fill="x", padx=10, pady=10)

        group_name_var = StringVar(value="Programación y Estructuras de Datos")
        credits_b_var = IntVar(value=9)
        credits_o_var = IntVar(value=0)

        ctk.CTkLabel(grouping_frame, text="Agrupación:", font=("Arial", 12), text_color="black").grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkEntry(grouping_frame, textvariable=group_name_var, width=300).grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(grouping_frame, text="Obligatorios:", font=("Arial", 12), text_color="black").grid(row=1, column=0, padx=5, pady=5)
        ctk.CTkEntry(grouping_frame, textvariable=credits_b_var, width=100).grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(grouping_frame, text="Optativos:", font=("Arial", 12), text_color="black").grid(row=2, column=0, padx=5, pady=5)
        ctk.CTkEntry(grouping_frame, textvariable=credits_o_var, width=100).grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Área de tabla
        table_container = ctk.CTkFrame(scroll_frame, fg_color="white", corner_radius=8)
        table_container.pack(fill="x", padx=10, pady=10)

        headers = ["Código", "Nombre de la asignatura", "Créditos", "B", "O", "Modificar"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(table_container, text=header, font=("Arial", 12, "bold"))
            label.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")

        self.subjects = [
            ["2026573", "Introducción a las ciencias de la computación", 3],
            ["2016375", "Programación orientada a objetos", 3],
            ["2016699", "Estructuras de datos", 3]
        ]

        for row, subject in enumerate(self.subjects, start=1):
            for col, value in enumerate(subject):
                entry = ctk.CTkEntry(table_container, width=100, textvariable=StringVar(value=value))
                entry.grid(row=row, column=col, padx=5, pady=5)

            b_var = IntVar(value=1 if row < len(self.subjects) else 0)
            ctk.CTkCheckBox(table_container, variable=b_var, text="").grid(row=row, column=3, padx=5, pady=5)

            o_var = IntVar(value=0)
            ctk.CTkCheckBox(table_container, variable=o_var, text="").grid(row=row, column=4, padx=5, pady=5)

            ctk.CTkButton(
                table_container, text="✏", width=40, height=40, font=("Arial", 14),
                command=lambda: None
            ).grid(row=row, column=5, padx=5, pady=5)

    def return_to_main_menu(self):
        self.window.destroy()


if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("1200x800")
    UpdatePlanWindow(root)
    root.mainloop()

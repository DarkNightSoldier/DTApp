import customtkinter as ctk
from tkinter import Toplevel, StringVar, IntVar, Canvas, Scrollbar, Frame, Label
from plan_estudios_actual import components  # Importar la estructura de datos

class PlanData:
    def __init__(self, data):
        self.data = data

    def get_groupings(self, component_name):
        return self.data.get(component_name, {}).get("agrupaciones", [])

    def find_grouping(self, component_name, grouping_name):
        for grouping in self.get_groupings(component_name):
            if grouping["nombre"] == grouping_name:
                return grouping
        return None

class UpdatePlanWindow:
    def __init__(self, parent):
        self.plan_data = PlanData(components)

        self.window = Toplevel(parent)
        self.window.title("Actualizar Plan de Estudios en Origen")
        self.window.geometry("1200x700")

        self.selected_component = None
        self.grouping_var = StringVar()

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
            label = Label(summary_frame, text=header, font=("Arial", 13, "bold"),
                          bg="#D3D3D3", relief="ridge", width=19 * span, height=2, anchor="center")
            label.grid(row=0, column=col_start, columnspan=span, sticky="nsew", padx=1, pady=1)
            col_start += span

        col_start = 0
        for row in subheaders:
            for subheader in row:
                label = Label(summary_frame, text=subheader, font=("Arial", 13),
                              bg="#E8E8E8", relief="ridge", width=19, height=2, anchor="center")
                label.grid(row=1, column=col_start, sticky="nsew", padx=1, pady=1)
                col_start += 1

        col_start = 0
        for row_data in data:
            for value in row_data:
                label = Label(summary_frame, text=value, font=("Arial", 13),
                              bg="#FFFFFF", relief="ridge", width=19, height=2, anchor="center")
                label.grid(row=2, column=col_start, sticky="nsew", padx=1, pady=1)
                col_start += 1

        self.fundamentacion_label = Label(
            summary_frame,
            text="Fundamentación",
            font=("Arial", 12, "bold"),
            bg="#D3D3D3",
            relief="ridge",
            width=20,
            height=2,
            anchor="center"
        )
        self.fundamentacion_label.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=1, pady=1)
        self.fundamentacion_label.bind("<Button-1>", lambda e: self.select_component("Fundamentación"))
        self.fundamentacion_label.bind("<Enter>", lambda e: self.fundamentacion_label.config(bg="#B0E0E6"))
        self.fundamentacion_label.bind("<Leave>", lambda e: self.fundamentacion_label.config(bg="#D3D3D3"))

        self.disciplinar_label = Label(
            summary_frame,
            text="Disciplinar",
            font=("Arial", 12, "bold"),
            bg="#D3D3D3",
            relief="ridge",
            width=15,
            height=2,
            anchor="center"
        )
        self.disciplinar_label.grid(row=0, column=2, columnspan=3, sticky="nsew", padx=1, pady=1)
        self.disciplinar_label.bind("<Button-1>", lambda e: self.select_component("Disciplinar"))
        self.disciplinar_label.bind("<Enter>", lambda e: self.disciplinar_label.config(bg="#B0E0E6"))
        self.disciplinar_label.bind("<Leave>", lambda e: self.disciplinar_label.config(bg="#D3D3D3"))

        self.subject_table_frame = ctk.CTkFrame(scroll_frame)
        self.subject_table_frame.pack_forget()

    def select_component(self, component_name):
        if self.selected_component == "Fundamentación":
            self.fundamentacion_label.config(bg="#D3D3D3")
        elif self.selected_component == "Disciplinar":
            self.disciplinar_label.config(bg="#D3D3D3")

        self.selected_component = component_name

        if component_name == "Fundamentación":
            self.fundamentacion_label.config(bg="#A0C4D7")
        else:
            self.disciplinar_label.config(bg="#A0C4D7")

        self.subject_table_frame.pack(fill="x", padx=10, pady=10)
        group_names = [g["nombre"] for g in self.plan_data.get_groupings(component_name)]
        if group_names:
            self.load_grouping(group_names[0], update_option_menu=True)
        else:
            for widget in self.subject_table_frame.winfo_children():
                widget.destroy()

    def load_grouping(self, grouping_name, update_option_menu=False):
        if not self.selected_component:
            return

        grouping = self.plan_data.find_grouping(self.selected_component, grouping_name)
        if not grouping:
            return

        self.create_grouping_frame(self.selected_component, grouping, update_option_menu)

    def create_grouping_frame(self, component_name, grouping, update_option_menu):
        for widget in self.subject_table_frame.winfo_children():
            widget.destroy()

        top_frame = ctk.CTkFrame(self.subject_table_frame, fg_color="#F5F5F5")
        top_frame.pack(fill="x", padx=5, pady=5)

        label = ctk.CTkLabel(top_frame, text="Agrupación:", font=("Arial", 12), text_color="black")
        label.pack(side="left", padx=5, pady=5)

        group_names = [g["nombre"] for g in self.plan_data.get_groupings(component_name)]

        grouping_menu = ctk.CTkOptionMenu(
            top_frame,
            variable=self.grouping_var,
            values=group_names,
            command=self.on_grouping_selected,
            fg_color="#B0E0E6",
            text_color="black"
        )
        self.grouping_var.set(grouping["nombre"])
        grouping_menu.pack(side="left", padx=5, pady=5)

        self.credits_b_var = StringVar(value="Obligatorios: 0")
        self.credits_o_var = StringVar(value="Optativos: 0")

        self.obligatorios_label = ctk.CTkLabel(top_frame, textvariable=self.credits_b_var, font=("Arial", 12))
        self.obligatorios_label.pack(side="right", padx=10)

        self.optativos_label = ctk.CTkLabel(top_frame, textvariable=self.credits_o_var, font=("Arial", 12))
        self.optativos_label.pack(side="right", padx=10)

        # Crear el contenedor para la tabla
        self.table_container = ctk.CTkFrame(self.subject_table_frame, fg_color="white", corner_radius=8)
        self.table_container.pack(fill="x", padx=10, pady=10)

        # Botón para añadir asignaturas
        add_button = ctk.CTkButton(
            self.subject_table_frame,
            text="Añadir Asignatura",
            command=lambda: self.add_subject("Nuevo Código", "Nueva Asignatura", "3")
        )
        add_button.pack(side="top", padx=5, pady=5)  # Se ubicará debajo de la tabla

        self.create_subject_table(grouping["subjects"], component_name)

    def on_grouping_selected(self, selected_group):
        self.load_grouping(selected_group, update_option_menu=False)

    def create_subject_table(self, subjects, component_name):
        headers_frame = ctk.CTkFrame(self.table_container, fg_color="white")
        headers_frame.pack(fill="x", pady=5)

        if component_name == "Fundamentación":
            headers = ["Código", "Nombre de la asignatura", "Créditos", "B", "O", "Eliminar"]
        else:
            headers = ["Código", "Nombre de la asignatura", "Créditos", "C", "T", "Eliminar"]

        col_widths = [70, 420, 60, 40, 40, 60]

        for header, width in zip(headers, col_widths):
            label = ctk.CTkLabel(headers_frame, text=header, font=("Arial", 12, "bold"))
            label.pack(side="left", padx=5)
            label.configure(width=width)

        self.rows_info = []

        for row_index, subject in enumerate(subjects, start=1):
            self._create_subject_row(self.table_container, row_index, subject, col_widths)

        self.update_credit_count()

    def _create_subject_row(self, parent_container, row_index, subject, col_widths):
        row_frame = ctk.CTkFrame(parent_container, fg_color="white")
        row_frame.pack(fill="x", pady=2)

        code_var = StringVar(value=str(subject[0]))
        name_var = StringVar(value=str(subject[1]))
        credit_var = StringVar(value=str(subject[2]))
        b_var = IntVar(value=0)
        o_var = IntVar(value=0)

        code_entry = ctk.CTkEntry(row_frame, textvariable=code_var, width=col_widths[0])
        code_entry.pack(side="left", padx=5)

        name_entry = ctk.CTkEntry(row_frame, textvariable=name_var, width=col_widths[1])
        name_entry.pack(side="left", padx=5)

        credit_entry = ctk.CTkEntry(row_frame, textvariable=credit_var, width=col_widths[2])
        credit_entry.pack(side="left", padx=5)

        check_frame_b = ctk.CTkFrame(row_frame, width=col_widths[3], height=30, fg_color="white", corner_radius=0)
        check_frame_b.pack(side="left", padx=(15,5))
        check_frame_b.pack_propagate(False)

        b_checkbox = ctk.CTkCheckBox(check_frame_b, variable=b_var, text="")
        b_checkbox.pack(expand=True)

        check_frame_o = ctk.CTkFrame(row_frame, width=col_widths[4], height=30, fg_color="white", corner_radius=0)
        check_frame_o.pack(side="left", padx=5)
        check_frame_o.pack_propagate(False)

        o_checkbox = ctk.CTkCheckBox(check_frame_o, variable=o_var, text="")
        o_checkbox.pack(expand=True)

        b_checkbox.configure(command=lambda b=b_var, o=o_var: (self.toggle_checkboxes(b, o), self.update_credit_count()))
        o_checkbox.configure(command=lambda o=o_var, b=b_var: (self.toggle_checkboxes(o, b), self.update_credit_count()))

        delete_btn = ctk.CTkButton(
            row_frame, text="🗑", width=col_widths[5], height=30, font=("Arial", 14),
            hover_color="#FF0000",
            command=lambda r=row_index: self.delete_subject(r)
        )
        delete_btn.pack(side="left", padx=(0,5), expand=True)

        row_data = {
            "frame": row_frame,
            "code_var": code_var,
            "name_var": name_var,
            "credit_var": credit_var,
            "b_var": b_var,
            "o_var": o_var,
            "delete_btn": delete_btn
        }
        self.rows_info.append(row_data)

    def update_credit_count(self):
        total_obligatorios = 0
        total_optativos = 0

        for row_data in self.rows_info:
            creditos = int(row_data["credit_var"].get())
            if row_data["b_var"].get() == 1:
                total_obligatorios += creditos
            if row_data["o_var"].get() == 1:
                total_optativos += creditos

        self.credits_b_var.set(f"Obligatorios: {total_obligatorios}")
        self.credits_o_var.set(f"Optativos: {total_optativos}")

    def toggle_checkboxes(self, selected_var, other_var):
        if selected_var.get() == 1:
            other_var.set(0)

    def delete_subject(self, row_index):
        real_index = row_index - 1
        if 0 <= real_index < len(self.rows_info):
            row_data = self.rows_info.pop(real_index)
            row_data["frame"].destroy()
            self.update_credit_count()

    def add_subject(self, code, name, credits):
        """
        Añade una nueva fila (asignatura) al final de la tabla,
        usando la misma lógica que create_subject_table.
        """
        row_index = len(self.rows_info) + 1
        subject = [code, name, credits]
        self._create_subject_row(self.table_container, row_index, subject, [70, 420, 60, 40, 40, 60])
        self.update_credit_count()

    def return_to_main_menu(self):
        pass

if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("1200x800")
    UpdatePlanWindow(root)
    root.mainloop()
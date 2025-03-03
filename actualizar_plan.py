import customtkinter as ctk
import sqlite3
from tkinter import Toplevel, StringVar, IntVar, Canvas, Scrollbar, Frame, Label
from plan_estudios_actual import *

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
        components = cargar_componentes()
        self.plan_data = PlanData(components)

        self.window = Toplevel(parent)
        self.window.title("Actualizar Plan de Estudios en Origen")
        self.window.geometry("1200x700")

        self.selected_component = None
        self.grouping_var = StringVar()
        self.current_grouping_name = None  # Nombre de la agrupación seleccionada

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

        # -------------------------------------------
        # Construcción del resumen (tabla de encabezado)
        # -------------------------------------------
        self.summary_frame = ctk.CTkFrame(scroll_frame, fg_color="#F5F5F5", corner_radius=8)
        self.summary_frame.pack(fill="x", padx=10, pady=10)
        self.refresh_summary()

        self.subject_table_frame = ctk.CTkFrame(scroll_frame)
        self.subject_table_frame.pack_forget()

    # Método para refrescar el resumen (incluye la suma de obligatorios y optativos)
    def refresh_summary(self):
        # Limpia el summary_frame
        for widget in self.summary_frame.winfo_children():
            widget.destroy()

        # Consulta dinámica a la BD para obtener sumas
        with sqlite3.connect("DatosApp.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Tipologia, 
                       SUM(Cant_Obligatorios) AS SumaOblig, 
                       SUM(Cant_Optativos)    AS SumaOpt 
                  FROM Agrupaciones_CC
                 GROUP BY Tipologia
            """)
            rows = cursor.fetchall()

        tipology_data = {}
        for tip, obl, opt in rows:
            sum_obl = obl if obl else 0
            sum_opt = opt if opt else 0
            tipology_data[tip] = (sum_obl, sum_opt)

        fund_obl, fund_opt = tipology_data.get("Fundamentación", (0, 0))
        disc_obl, disc_opt = tipology_data.get("Disciplinar", (0, 0))
        tg_opt   = tipology_data.get("Trabajo de grado", (0, 0))[1]
        le_opt   = tipology_data.get("Libre Elección", (0, 0))[1]

        headers = [
            ("Fundamentación", 2),
            ("Disciplinar", 2),
            ("Trabajo de Grado (P)", 1),
            ("Libre Elección (L)", 1)
        ]
        subheaders = [
            ["Obligatorios (B)", "Optativos (O)"],
            ["Obligatorios (C)", "Optativos (T)"],
            [""],
            [""]
        ]
        data = [
            [fund_obl, fund_opt],
            [disc_obl, disc_opt],
            [tg_opt],
            [le_opt]
        ]

        col_start = 0
        for header, span in headers:
            lbl = Label(self.summary_frame, text=header, font=("Arial", 13, "bold"),
                        bg="#D3D3D3", relief="ridge", width=19 * span, height=2, anchor="center")
            lbl.grid(row=0, column=col_start, columnspan=span, sticky="nsew", padx=1, pady=1)
            col_start += span

        col_start = 0
        for row_sub in subheaders:
            for subheader in row_sub:
                lbl = Label(self.summary_frame, text=subheader, font=("Arial", 13),
                            bg="#E8E8E8", relief="ridge", width=19, height=2, anchor="center")
                lbl.grid(row=1, column=col_start, sticky="nsew", padx=1, pady=1)
                col_start += 1

        col_start = 0
        for row_data in data:
            for value in row_data:
                lbl = Label(self.summary_frame, text=value, font=("Arial", 13),
                            bg="#FFFFFF", relief="ridge", width=19, height=2, anchor="center")
                lbl.grid(row=2, column=col_start, sticky="nsew", padx=1, pady=1)
                col_start += 1

        # Reincorporamos los labels clicables para cada componente
        self.fundamentacion_label = Label(
            self.summary_frame,
            text="Fundamentación",
            font=("Arial", 12, "bold"),
            bg="#D3D3D3", relief="ridge", width=20, height=2, anchor="center"
        )
        self.fundamentacion_label.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=1, pady=1)
        self.fundamentacion_label.bind("<Button-1>", lambda e: self.select_component("Fundamentación"))
        self.fundamentacion_label.bind("<Enter>", lambda e: self.fundamentacion_label.config(bg="#B0E0E6"))
        self.fundamentacion_label.bind("<Leave>", lambda e: self.fundamentacion_label.config(bg="#D3D3D3"))

        self.disciplinar_label = Label(
            self.summary_frame,
            text="Disciplinar",
            font=("Arial", 12, "bold"),
            bg="#D3D3D3", relief="ridge", width=15, height=2, anchor="center"
        )
        self.disciplinar_label.grid(row=0, column=2, columnspan=2, sticky="nsew", padx=1, pady=1)
        self.disciplinar_label.bind("<Button-1>", lambda e: self.select_component("Disciplinar"))
        self.disciplinar_label.bind("<Enter>", lambda e: self.disciplinar_label.config(bg="#B0E0E6"))
        self.disciplinar_label.bind("<Leave>", lambda e: self.disciplinar_label.config(bg="#D3D3D3"))

        self.trabajo_label = Label(
            self.summary_frame,
            text="Trabajo de Grado (P)",
            font=("Arial", 12, "bold"),
            bg="#D3D3D3", relief="ridge", width=20, height=2, anchor="center"
        )
        self.trabajo_label.grid(row=0, column=4, columnspan=1, sticky="nsew", padx=1, pady=1)
        self.trabajo_label.bind("<Button-1>", lambda e: self.select_component("Trabajo de Grado (P)"))
        self.trabajo_label.bind("<Enter>", lambda e: self.trabajo_label.config(bg="#B0E0E6"))
        self.trabajo_label.bind("<Leave>", lambda e: self.trabajo_label.config(bg="#D3D3D3"))

        self.le_label = Label(
            self.summary_frame,
            text="Libre Elección (L)",
            font=("Arial", 12, "bold"),
            bg="#D3D3D3", relief="ridge", width=20, height=2, anchor="center"
        )
        self.le_label.grid(row=0, column=5, columnspan=1, sticky="nsew", padx=1, pady=1)
        self.le_label.bind("<Button-1>", lambda e: self.select_component("Libre Elección (L)"))
        self.le_label.bind("<Enter>", lambda e: self.le_label.config(bg="#B0E0E6"))
        self.le_label.bind("<Leave>", lambda e: self.le_label.config(bg="#D3D3D3"))

    def select_component(self, component_name):
        if self.selected_component == "Fundamentación":
            self.fundamentacion_label.config(bg="#D3D3D3")
        elif self.selected_component == "Disciplinar":
            self.disciplinar_label.config(bg="#D3D3D3")
        elif self.selected_component == "Trabajo de Grado (P)":
            self.trabajo_label.config(bg="#D3D3D3")
        elif self.selected_component == "Libre Elección (L)":
            self.le_label.config(bg="#D3D3D3")

        self.selected_component = component_name

        if component_name == "Fundamentación":
            self.fundamentacion_label.config(bg="#A0C4D7")
        elif component_name == "Disciplinar":
            self.disciplinar_label.config(bg="#A0C4D7")
        elif component_name == "Trabajo de Grado (P)":
            self.trabajo_label.config(bg="#A0C4D7")
        else:
            self.le_label.config(bg="#A0C4D7")

        self.subject_table_frame.pack(fill="x", padx=10, pady=10)

        if component_name == "Trabajo de Grado (P)":
            grouping_name = "TRABAJO DE GRADO"
        elif component_name == "Libre Elección (L)":
            grouping_name = "LIBRE ELECCIÓN"
        else:
            group_names = [g["nombre"] for g in self.plan_data.get_groupings(component_name)]
            if not group_names:
                for widget in self.subject_table_frame.winfo_children():
                    widget.destroy()
                return
            grouping_name = group_names[0]

        self.load_grouping(grouping_name, update_option_menu=True)

    def load_grouping(self, grouping_name, update_option_menu=False):
        for widget in self.subject_table_frame.winfo_children():
            widget.destroy()

        self.current_grouping_name = grouping_name

        top_frame = ctk.CTkFrame(self.subject_table_frame, fg_color="#F5F5F5")
        top_frame.pack(fill="x", padx=5, pady=5)

        lbl = ctk.CTkLabel(top_frame, text="Agrupación:", font=("Arial", 12), text_color="black")
        lbl.pack(side="left", padx=5, pady=5)

        # Menú de selección de agrupación
        group_names = [g["nombre"] for g in self.plan_data.get_groupings(self.selected_component)]
        grouping_menu = ctk.CTkOptionMenu(
            top_frame,
            variable=self.grouping_var,
            values=group_names,
            command=self.on_grouping_selected,
            fg_color="#B0E0E6",
            text_color="black"
        )
        self.grouping_var.set(grouping_name)
        grouping_menu.pack(side="left", padx=5, pady=5)

        # Campo editable "Optativos:" (Cant_Optativos)
        with sqlite3.connect("DatosApp.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT Cant_Optativos FROM Agrupaciones_CC WHERE Nom_Agrupacion = ?",
                (self.current_grouping_name,)
            )
            row = cursor.fetchone()
            current_opt = row[0] if row and row[0] is not None else 0

        ctk.CTkLabel(top_frame, text="Optativos:", font=("Arial", 12)).pack(side="left", padx=10)
        self.optativos_var = StringVar(value=str(current_opt))
        optativos_entry = ctk.CTkEntry(top_frame, textvariable=self.optativos_var, width=60)
        optativos_entry.pack(side="left", padx=5, pady=5)
        optativos_entry.bind("<FocusOut>", lambda e: self.update_optativos_db())

        # Mostrar "Obligatorios:" solo para componentes distintos de Trabajo de Grado (P) y Libre Elección (L)
        if self.selected_component not in ["Trabajo de Grado (P)", "Libre Elección (L)"]:
            self.credits_b_var = StringVar(value="Obligatorios: 0")
            obligatorios_label = ctk.CTkLabel(top_frame, textvariable=self.credits_b_var, font=("Arial", 12))
            obligatorios_label.pack(side="right", padx=10)

        self.table_container = ctk.CTkFrame(self.subject_table_frame, fg_color="white", corner_radius=8)
        self.table_container.pack(fill="x", padx=10, pady=10)

        add_button = ctk.CTkButton(
            self.subject_table_frame,
            text="Añadir Asignatura",
            command=lambda: self.add_subject("Nuevo Código", "Nueva Asignatura", "3")
        )
        add_button.pack(side="top", padx=5, pady=5)

        subjects = self.get_subjects_from_db(self.current_grouping_name)
        self.create_subject_table(subjects, self.selected_component)

    def on_grouping_selected(self, selected_group):
        self.load_grouping(selected_group, update_option_menu=False)

    def get_subjects_from_db(self, nom_agrupacion):
        with sqlite3.connect("DatosApp.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT CC.Cod_Asignatura_CC, INF.Nom_Asignatura, INF.Creditos, CC.Tipo
                FROM Asignaturas_CC CC
                JOIN Asignaturas_Info INF
                    ON CC.Cod_Asignatura_CC = INF.Cod_Asignatura
                WHERE CC.Nom_Agrupacion = ?
                """,
                (nom_agrupacion,)
            )
            rows = cursor.fetchall()
        subjects = [list(r) for r in rows]
        return subjects

    def update_optativos_db(self):
        try:
            new_opt = int(self.optativos_var.get())
        except ValueError:
            new_opt = 0
        if self.current_grouping_name:
            with sqlite3.connect("DatosApp.db") as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE Agrupaciones_CC SET Cant_Optativos = ? WHERE Nom_Agrupacion = ?",
                    (new_opt, self.current_grouping_name)
                )
                conn.commit()
        self.refresh_summary()

    def update_obligatorios_db(self):
        # Solo para componentes que calculan obligatorios
        if self.selected_component not in ["Trabajo de Grado (P)", "Libre Elección (L)"]:
            total_obl = 0
            for row_data in self.rows_info:
                try:
                    creditos = int(row_data["credit_var"].get())
                except ValueError:
                    creditos = 0
                if row_data["b_var"].get() == 1:
                    total_obl += creditos
            with sqlite3.connect("DatosApp.db") as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE Agrupaciones_CC SET Cant_Obligatorios = ? WHERE Nom_Agrupacion = ?",
                    (total_obl, self.current_grouping_name)
                )
                conn.commit()
            self.refresh_summary()

    def create_subject_table(self, subjects, component_name):
        headers_frame = ctk.CTkFrame(self.table_container, fg_color="white")
        headers_frame.pack(fill="x", pady=5)

        if component_name in ["Trabajo de Grado (P)", "Libre Elección (L)"]:
            headers = ["Código", "Nombre de la asignatura", "Créditos", "Eliminar"]
            col_widths = [70, 420, 60, 60]
        elif component_name == "Fundamentación":
            headers = ["Código", "Nombre de la asignatura", "Créditos", "B", "O", "Eliminar"]
            col_widths = [70, 420, 60, 40, 40, 60]
        else:
            headers = ["Código", "Nombre de la asignatura", "Créditos", "C", "T", "Eliminar"]
            col_widths = [70, 420, 60, 40, 40, 60]

        for header, width in zip(headers, col_widths):
            lbl = ctk.CTkLabel(headers_frame, text=header, font=("Arial", 12, "bold"))
            lbl.pack(side="left", padx=5)
            lbl.configure(width=width)

        self.rows_info = []
        for row_index, subject in enumerate(subjects, start=1):
            self._create_subject_row(self.table_container, row_index, subject, col_widths, component_name)

        self.update_credit_count()

    def _create_subject_row(self, parent_container, row_index, subject, col_widths, component_name):
        row_frame = ctk.CTkFrame(parent_container, fg_color="white")
        row_frame.pack(fill="x", pady=2)

        code_var = StringVar(value=str(subject[0]))
        name_var = StringVar(value=str(subject[1]))
        credit_var = StringVar(value=str(subject[2]))

        if component_name in ["Trabajo de Grado (P)", "Libre Elección (L)"]:
            b_var = IntVar(value=0)
            o_var = IntVar(value=0)
        else:
            if subject[3] in ["B", "C"]:
                b_var = IntVar(value=1)
                o_var = IntVar(value=0)
            elif subject[3] in ["O", "T"]:
                b_var = IntVar(value=0)
                o_var = IntVar(value=1)
            else:
                b_var = IntVar(value=0)
                o_var = IntVar(value=0)

        for i, w in enumerate(col_widths):
            row_frame.grid_columnconfigure(i, minsize=w)

        code_entry = ctk.CTkEntry(row_frame, textvariable=code_var, width=col_widths[0], height=30)
        code_entry.grid(row=0, column=0, padx=5, pady=2, sticky="nsew")

        name_entry = ctk.CTkEntry(row_frame, textvariable=name_var, width=col_widths[1], height=30)
        name_entry.grid(row=0, column=1, padx=5, pady=2, sticky="nsew")

        credit_entry = ctk.CTkEntry(row_frame, textvariable=credit_var, width=col_widths[2], height=30)
        credit_entry.grid(row=0, column=2, padx=5, pady=2, sticky="nsew")

        delete_btn_col = 3
        if component_name not in ["Trabajo de Grado (P)", "Libre Elección (L)"]:
            b_checkbox = ctk.CTkCheckBox(row_frame, variable=b_var, text="", width=col_widths[3], height=30)
            b_checkbox.grid(row=0, column=3, padx=5, pady=2)
            o_checkbox = ctk.CTkCheckBox(row_frame, variable=o_var, text="", width=col_widths[4], height=30)
            o_checkbox.grid(row=0, column=4, padx=5, pady=2)
            delete_btn_col = 5

        delete_btn = ctk.CTkButton(row_frame, text="🗑", width=30, height=30, font=("Arial", 14),
                                   hover_color="#FF0000")
        delete_btn.grid(row=0, column=delete_btn_col, padx=5, pady=2)

        row_data = {
            "frame": row_frame,
            "code_var": code_var,
            "name_var": name_var,
            "credit_var": credit_var,
            "b_var": b_var,
            "o_var": o_var,
            "original_code": subject[0]
        }
        delete_btn.configure(command=lambda rd=row_data: self.delete_subject(rd))

        code_entry.bind("<FocusOut>", lambda e, rd=row_data: self.update_subject_in_db(rd))
        name_entry.bind("<FocusOut>", lambda e, rd=row_data: self.update_subject_in_db(rd))
        credit_entry.bind("<FocusOut>", lambda e, rd=row_data: self.update_subject_in_db(rd))

        if component_name not in ["Trabajo de Grado (P)", "Libre Elección (L)"]:
            b_checkbox.configure(
                command=lambda rd=row_data: (
                    self.toggle_checkboxes(b_var, o_var),
                    self.update_credit_count(),
                    self.update_subject_in_db(rd)
                )
            )
            o_checkbox.configure(
                command=lambda rd=row_data: (
                    self.toggle_checkboxes(o_var, b_var),
                    self.update_credit_count(),
                    self.update_subject_in_db(rd)
                )
            )

        self.rows_info.append(row_data)

    def toggle_checkboxes(self, selected_var, other_var):
        if selected_var.get() == 1:
            other_var.set(0)

    def update_credit_count(self):
        if self.selected_component not in ["Trabajo de Grado (P)", "Libre Elección (L)"]:
            total_obligatorios = 0
            for row_data in self.rows_info:
                try:
                    creditos = int(row_data["credit_var"].get())
                except ValueError:
                    creditos = 0
                if row_data["b_var"].get() == 1:
                    total_obligatorios += creditos
            self.credits_b_var.set(f"Obligatorios: {total_obligatorios}")

    def update_subject_in_db(self, row_data):
        old_code = row_data["original_code"]
        new_code = row_data["code_var"].get()
        new_name = row_data["name_var"].get()
        try:
            new_credits = int(row_data["credit_var"].get())
        except ValueError:
            new_credits = 0

        if self.selected_component == "Fundamentación":
            if row_data["b_var"].get() == 1:
                typology = "B"
            elif row_data["o_var"].get() == 1:
                typology = "O"
            else:
                typology = None
        elif self.selected_component == "Disciplinar":
            if row_data["b_var"].get() == 1:
                typology = "C"
            elif row_data["o_var"].get() == 1:
                typology = "T"
            else:
                typology = None
        elif self.selected_component == "Trabajo de Grado (P)":
            typology = "TRABAJO DE GRADO"
        else:
            typology = "Libre Elección"

        with sqlite3.connect("DatosApp.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE Asignaturas_CC
                SET Cod_Asignatura_CC = ?, Nom_Agrupacion = ?, Tipo = ?
                WHERE Cod_Asignatura_CC = ?
                """,
                (new_code, self.current_grouping_name, typology, old_code)
            )
            cursor.execute(
                """
                UPDATE Asignaturas_Info
                SET Cod_Asignatura = ?, Nom_Asignatura = ?, Creditos = ?
                WHERE Cod_Asignatura = ?
                """,
                (new_code, new_name, new_credits, old_code)
            )
            conn.commit()

        row_data["original_code"] = new_code
        self.update_obligatorios_db()
        self.refresh_summary()

    def update_obligatorios_db(self):
        # Para componentes que calculan obligatorios
        if self.selected_component not in ["Trabajo de Grado (P)", "Libre Elección (L)"]:
            total_obl = 0
            for row_data in self.rows_info:
                try:
                    creditos = int(row_data["credit_var"].get())
                except ValueError:
                    creditos = 0
                if row_data["b_var"].get() == 1:
                    total_obl += creditos
            with sqlite3.connect("DatosApp.db") as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE Agrupaciones_CC SET Cant_Obligatorios = ? WHERE Nom_Agrupacion = ?",
                    (total_obl, self.current_grouping_name)
                )
                conn.commit()

    def delete_subject(self, row_data):
        if row_data in self.rows_info:
            self.rows_info.remove(row_data)
        old_code = row_data["original_code"]
        with sqlite3.connect("DatosApp.db") as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Asignaturas_CC WHERE Cod_Asignatura_CC = ?", (old_code,))
            cursor.execute("DELETE FROM Asignaturas_Info WHERE Cod_Asignatura = ?", (old_code,))
            conn.commit()
        row_data["frame"].destroy()
        # Actualizamos el conteo de créditos obligatorios en la BD
        self.update_obligatorios_db()
        self.update_credit_count()
        self.refresh_summary()
        self.load_grouping(self.current_grouping_name)


    def add_subject(self, code, name, credits):
        if self.selected_component in ["Trabajo de Grado (P)", "Libre Elección (L)"]:
            tipo = "TRABAJO DE GRADO" if self.selected_component == "Trabajo de Grado (P)" else "Libre Elección"
        else:
            tipo = None
        with sqlite3.connect("DatosApp.db") as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO Asignaturas_CC (Cod_Asignatura_CC, Nom_Agrupacion, Tipo)
                VALUES (?, ?, ?)
                """,
                (code, self.current_grouping_name, tipo)
            )
            cursor.execute(
                """
                INSERT INTO Asignaturas_Info (Cod_Asignatura, Nom_Asignatura, Creditos)
                VALUES (?, ?, ?)
                """,
                (code, name, credits)
            )
            conn.commit()
        self.load_grouping(self.current_grouping_name)
        self.refresh_summary()

    def return_to_main_menu(self):
        pass

if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("1200x800")
    UpdatePlanWindow(root)
    root.mainloop()

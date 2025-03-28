import customtkinter as ctk
import sqlite3
import pandas as pd
from tkinter import ttk, messagebox, Toplevel, Canvas, Scrollbar, Frame
from datetime import datetime

class ConsultarEstudiantesWindow:
    def __init__(self, parent, db_path="DatosApp.db"):
        self.parent = parent
        self.window = Toplevel(parent)        

        self.window.title("Consulta y actualización: Estudiantes con DT aprobada")
        self.window.geometry("1100x900")
        self.db_path = db_path

        # Encabezado
        header_frame = ctk.CTkFrame(self.window, fg_color="#65C2C6", corner_radius=8)
        header_frame.pack(fill="x", padx=10, pady=(10, 5), anchor="w")

        # Botón para regresar al menú principal
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
        menu_button.pack(side="left", padx=(10, 5), pady=10, anchor="w")

        # Título del programa
        title_label = ctk.CTkLabel(
            header_frame,
            text="Programa: Ciencias de la Computación (2933)",
            font=("Arial", 16, "bold"),
            text_color="black",
        )
        title_label.pack(side="left", padx=(20, 10), pady=10, anchor="w")

        # Canvas y scrollbar
        scroll_canvas = Canvas(self.window)
        scroll_canvas.pack(side="left", fill="both", expand=True, anchor="w")

        scrollbar = Scrollbar(self.window, command=scroll_canvas.yview)
        scrollbar.pack(side="right", fill="y")

        scroll_canvas.configure(yscrollcommand=scrollbar.set)
        scroll_frame = Frame(scroll_canvas)
        scroll_canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

        scroll_frame.bind(
            "<Configure>",
            lambda e: scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))
        )

        # Tabla de estudiantes aprobados
        columns = (
            "Identificacion",
            "Nombre",
            "Codigo_plan",
            "Resol_apro",
            "Fecha_actualizacion",
            "Actualizar",
            "Eliminar"
        )

        self.tree = ttk.Treeview(scroll_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140, anchor="center")

        # Ajustamos un poco anchos específicos
        self.tree.column("Nombre", width=200)
        self.tree.column("Fecha_actualizacion", width=120)
        self.tree.column("Actualizar", width=90)
        self.tree.column("Eliminar", width=80)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10, anchor="w")

        # Vinculamos el doble clic a la edición de celdas o acciones
        self.tree.bind("<Double-1>", self.on_double_click)

        # Botón para agregar estudiante (ahora debajo de la tabla)
        add_button = ctk.CTkButton(
            scroll_frame,  # Cambiado a scroll_frame para que esté dentro del scroll
            text="Añadir un nuevo estudiante aprobado",
            fg_color="#65C2C6",
            text_color="black",
            font=("Arial", 14, "bold"),
            command=self.add_estudiante
        )
        add_button.pack(pady=(10, 20), anchor="w")  # Ajusta el padding según sea necesario

        self.editing_item = None
        self.load_data()

    def load_data(self):
        """Carga los datos desde la BD y los muestra en la tabla."""
        with sqlite3.connect(self.db_path, timeout=5) as conn:
            query = """
                SELECT
                    Identificacion,
                    Nombre,
                    Codigo_plan,
                    Resol_apro,
                    Fecha_actualizacion
                FROM Estudiantes_Aprobados
            """
            df = pd.read_sql_query(query, conn)

        # Limpiar la tabla
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Insertar datos en la tabla
        for _, row in df.iterrows():
            self.tree.insert(
                "",
                "end",
                values=(
                    row["Identificacion"],
                    row["Nombre"],
                    row["Codigo_plan"],
                    row["Resol_apro"],
                    row["Fecha_actualizacion"],
                    "Actualizar",
                    "Eliminar"
                )
            )

    def on_double_click(self, event):
        """Detecta si se hizo doble clic en la tabla y decide qué hacer."""
        item_id = self.tree.identify_row(event.y)
        column_id = self.tree.identify_column(event.x)
        col_index = int(column_id.replace("#", "")) - 1
        col_name = self.tree["columns"][col_index]

        if not item_id:
            return

        # Verificamos si se hizo clic en "Eliminar" o "Actualizar"
        if col_name == "Eliminar":
            self.delete_estudiante(item_id)
        elif col_name == "Actualizar":
            self.actualizar_estudiante(item_id)
        else:
            # Si es uno de los campos editables, iniciamos edición
            self.edit_cell(item_id, col_name)

    def edit_cell(self, item_id, col_name):
        """Crea un Entry sobre la celda para editar su valor."""
        x, y, width, height = self.tree.bbox(item_id, col_name)
        old_value = self.tree.set(item_id, col_name)

        # Creamos un Entry para editar
        self.entry = ctk.CTkEntry(self.window, width=width, height=height)
        self.entry.insert(0, old_value)
        self.entry.focus()
        self.entry.place(x=self.tree.winfo_x() + x, y=self.tree.winfo_y() + y)

        # Guardamos la info necesaria para luego actualizar
        self.editing_item = (item_id, col_name, old_value)

        # Cuando presione Enter o pierda el foco, se guarda
        self.entry.bind("<Return>", self.save_edit)
        self.entry.bind("<FocusOut>", self.save_edit)

    def save_edit(self, event):
        """Guarda el valor editado en la base de datos."""
        if not self.editing_item:
            return

        item_id, col_name, old_value = self.editing_item
        new_value = self.entry.get()
        self.entry.destroy()
        self.editing_item = None

        # Si no cambió el valor, no hacemos nada
        if new_value == old_value:
            return

        # Actualizamos en la tabla (Treeview)
        self.tree.set(item_id, col_name, new_value)

        # Ahora, actualizamos en la BD
        current_values = self.tree.item(item_id, "values")
        identificacion = current_values[0]
        nombre = current_values[1]
        codigo_plan = current_values[2]
        resol_apro = current_values[3]
        fecha_act = current_values[4]

        with sqlite3.connect(self.db_path, timeout=5) as conn:
            cursor = conn.cursor()
            if col_name == "Identificacion":
                update_query = """
                    UPDATE Estudiantes_Aprobados
                    SET Identificacion = ?,
                        Nombre = ?,
                        Codigo_plan = ?,
                        Resol_apro = ?,
                        Fecha_actualizacion = ?
                    WHERE Identificacion = ?
                """
                cursor.execute(update_query, (
                    new_value,
                    nombre,
                    codigo_plan,
                    resol_apro,
                    fecha_act,
                    old_value
                ))
            else:
                update_query = f"""
                    UPDATE Estudiantes_Aprobados
                    SET {col_name} = ?
                    WHERE Identificacion = ?
                """
                cursor.execute(update_query, (new_value, identificacion))

            conn.commit()

    def delete_estudiante(self, item_id):
        """Elimina al estudiante de la BD y de la tabla."""
        values = self.tree.item(item_id, "values")
        identificacion = values[0]

        if messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Eliminar al estudiante con identificación {identificacion}?"
        ):
            with sqlite3.connect(self.db_path, timeout=5) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM Estudiantes_Aprobados WHERE Identificacion = ?",
                    (identificacion,)
                )
                conn.commit()

            self.tree.delete(item_id)

    def actualizar_estudiante(self, item_id):
        """Actualiza la fecha de actualización a hoy y abre la ventana real de 'actualizar_estudiante.py'."""
        today = datetime.now().strftime("%d/%m/%Y")
        values = self.tree.item(item_id, "values")
        identificacion = values[0]

        with sqlite3.connect(self.db_path, timeout=5) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE Estudiantes_Aprobados
                SET Fecha_actualizacion = ?
                WHERE Identificacion = ?
                """,
                (today, identificacion)
            )
            conn.commit()

        current_list = list(values)
        current_list[4] = today
        self.tree.item(item_id, values=current_list)

        self.open_update_window(item_id)

    def open_update_window(self, item_id):
        """Importa y abre la ventana ActualizarEstudianteWindow."""
        from actualizar_estudiante import ActualizarEstudianteWindow

        values = self.tree.item(item_id, "values")
        identificacion = values[0]
        nombre = values[1]

        ActualizarEstudianteWindow(
            parent=self.window,
            nombre_estudiante=nombre,
            identificacion=identificacion,
            db_path=self.db_path
        )

    def add_estudiante(self):
        """Abre una ventana para añadir un nuevo estudiante aprobado."""
        self.add_window = ctk.CTkToplevel(self.window)
        self.add_window.title("Añadir nuevo estudiante aprobado")
        self.add_window.geometry("400x400")

        # Etiqueta e ingreso para Identificacion
        label_ident = ctk.CTkLabel(self.add_window, text="Identificación:")
        label_ident.pack(pady=(10, 0))
        self.entry_ident = ctk.CTkEntry(self.add_window)
        self.entry_ident.pack(pady=5)

        # Etiqueta e ingreso para Nombre
        label_nombre = ctk.CTkLabel(self.add_window, text="Nombre:")
        label_nombre.pack(pady=(10, 0))
        self.entry_nombre = ctk.CTkEntry(self.add_window)
        self.entry_nombre.pack(pady=5)

        # Etiqueta e ingreso para Código_plan
        label_codplan = ctk.CTkLabel(self.add_window, text="Código Plan:")
        label_codplan.pack(pady=(10, 0))
        self.entry_codplan = ctk.CTkEntry(self.add_window)
        self.entry_codplan.pack(pady=5)

        # Etiqueta e ingreso para Resol_apro
        label_resol = ctk.CTkLabel(self.add_window, text="Resolución aprobación:")
        label_resol.pack(pady=(10, 0))
        self.entry_resol = ctk.CTkEntry(self.add_window)
        self.entry_resol.pack(pady=5)

        # Botón para guardar
        guardar_button = ctk.CTkButton(
            self.add_window,
            text="Guardar",
            command=self.guardar_nuevo_estudiante
        )
        guardar_button.pack(pady=15)

    def guardar_nuevo_estudiante(self):
        """Inserta un nuevo registro en la tabla Estudiantes_Aprobados."""
        identificacion = self.entry_ident.get().strip()
        nombre = self.entry_nombre.get().strip()
        codigo_plan = self.entry_codplan.get().strip()
        resol_apro = self.entry_resol.get().strip()

        if not identificacion or not nombre or not codigo_plan:
            messagebox.showerror(
                "Error",
                "Debe completar al menos Identificación, Nombre y Código Plan."
            )
            return

        fecha_hoy = datetime.now().strftime("%d/%m/%Y")

        try:
            with sqlite3.connect(self.db_path, timeout=5) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Estudiantes_Aprobados
                    (Identificacion, Nombre, Codigo_plan, Resol_apro, Fecha_actualizacion)
                    VALUES (?, ?, ?, ?, ?)
                """, (identificacion, nombre, codigo_plan, resol_apro, fecha_hoy))
                conn.commit()
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar el estudiante:\n{e}")
            return

        self.add_window.destroy()
        self.load_data()
    
    def return_to_main_menu(self):
        """Función para regresar al menú principal."""
        self.window.destroy()
        self.parent.deiconify()

if __name__ == "__main__":
    ctk.set_appearance_mode("Light")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    root.geometry("1000x700")
    app = ConsultarEstudiantesWindow(root, db_path="DatosApp.db")
    root.mainloop()
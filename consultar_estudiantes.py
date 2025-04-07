import customtkinter as ctk
import sqlite3
import pandas as pd
from tkinter import messagebox, Toplevel
from datetime import datetime
import re

class ConsultarEstudiantesWindow:
    def __init__(self, parent, plan_text, db_path="DatosApp.db"):
        self.parent = parent
        self.plan_text = plan_text
        self.window = Toplevel(parent)
        self.window.title("Consulta y actualización: Estudiantes")
        self.window.geometry("1100x800")
        self.db_path = db_path

        # Encabezado
        header_frame = ctk.CTkFrame(self.window, fg_color="#65C2C6", corner_radius=8)
        header_frame.pack(fill="x", padx=10, pady=(10, 5), anchor="w")

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

        title_label = ctk.CTkLabel(
            header_frame,
            text=self.plan_text,
            font=("Arial", 16, "bold"),
            text_color="black",
        )
        title_label.pack(side="left", padx=(20, 10), pady=10, anchor="w")

        # Contenedor scrolleable (usando CTkScrollableFrame)
        self.scrollable_frame = ctk.CTkScrollableFrame(self.window, fg_color="white")
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Encabezado de la tabla (sin Resol_apro)
        self.headers = ["Identificacion", "Nombre", "Codigo_plan", "Fecha_actualizacion", "Actualizar", "Eliminar"]
        self.col_widths = [140, 200, 140, 140, 90, 80]
        header_tbl = ctk.CTkFrame(self.scrollable_frame, fg_color="white")
        header_tbl.pack(fill="x", pady=5)
        for header, width in zip(self.headers, self.col_widths):
            lbl = ctk.CTkLabel(header_tbl, text=header, font=("Arial", 12, "bold"))
            lbl.pack(side="left", padx=5)
            lbl.configure(width=width)

        # Lista para almacenar información de cada fila (para edición, etc.)
        self.rows_info = []

        # Cargar datos desde la BD
        self.load_data()

        # Botón para agregar estudiante, centrado
        add_button = ctk.CTkButton(
            self.window,
            text="Añadir un nuevo estudiante aprobado",
            fg_color="#65C2C6",
            text_color="black",
            font=("Arial", 14, "bold"),
            command=self.add_estudiante
        )
        add_button.pack(pady=(10, 20), anchor="center")

    def load_data(self):
        """Carga los datos de la BD y crea las filas en la tabla personalizada."""
        try:
            with sqlite3.connect(self.db_path, timeout=5) as conn:
                query = """
                    SELECT Identificacion, Nombre, Codigo_plan, Fecha_actualizacion
                    FROM Estudiantes_Aprobados
                """
                df = pd.read_sql_query(query, conn)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los datos:\n{str(e)}")
            return

        # Limpiar filas previas
        for row_info in self.rows_info:
            row_info["frame"].destroy()
        self.rows_info.clear()

        if not df.empty:
            for record in df.values:
                self._create_student_row(record)

    def _create_student_row(self, record):
        """
        Crea una fila en la tabla con los datos del estudiante.
        record: (Identificacion, Nombre, Codigo_plan, Fecha_actualizacion)
        """
        row_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="white")
        row_frame.pack(fill="x", pady=2)

        # Convertir cada valor a cadena
        data = [str(item) for item in record]
        # Crear StringVar para cada dato
        data_vars = [ctk.StringVar(value=value) for value in data]
        entries = []
        # Se crean 4 celdas (los datos)
        for i, (var, width) in enumerate(zip(data_vars, self.col_widths[:4])):
            entry = ctk.CTkEntry(row_frame, textvariable=var, width=width, height=30, state="disabled")
            entry.pack(side="left", padx=5)
            entries.append(entry)
        # Crear el diccionario para la fila
        row_info = {
            "frame": row_frame,
            "data": data,                      # Valores actuales (índices 0 a 3)
            "data_vars": data_vars,            # Variables asociadas
            "entries": entries,                # Referencias a los CTkEntry
            "original_identificacion": data[0],
            "is_new": False
        }
        # Vincular doble clic para habilitar la edición en cada celda
        for i, entry in enumerate(entries):
            entry.bind("<Double-Button-1>", lambda e, ent=entry, ri=row_info, col=i: self.enable_edit(ent, ri, col))
            entry.bind("<Return>", lambda e, ent=entry, ri=row_info, col=i: self.save_edit(ent, ri, col))
            entry.bind("<FocusOut>", lambda e, ent=entry, ri=row_info, col=i: self.save_edit(ent, ri, col))
        # Botón "Actualizar" con ícono "🗘"
        btn_actualizar = ctk.CTkButton(
            row_frame,
            text="🗘",
            width=self.col_widths[4],
            height=30,
            font=("Arial", 12),
            command=lambda ri=row_info: self.actualizar_estudiante(ri)
        )
        btn_actualizar.pack(side="left", padx=5)
        # Botón "Eliminar" con ícono "🗑"
        btn_eliminar = ctk.CTkButton(
            row_frame,
            text="🗑",
            width=self.col_widths[5],
            height=30,
            font=("Arial", 12),
            command=lambda ri=row_info: self.delete_estudiante(ri)
        )
        btn_eliminar.pack(side="left", padx=5)

        self.rows_info.append(row_info)

    def enable_edit(self, widget, row_info, col):
        """Habilita el Entry para editar y vincula el guardado al presionar Enter o perder el foco."""
        widget.configure(state="normal")
        widget.focus()
        widget.bind("<Return>", lambda e, ent=widget, ri=row_info, col=col: self.save_edit(ent, ri, col))
        widget.bind("<FocusOut>", lambda e, ent=widget, ri=row_info, col=col: self.save_edit(ent, ri, col))

    def save_edit(self, widget, row_info, col):
        """Guarda el nuevo valor editado, actualiza la BD y vuelve a deshabilitar la celda."""
        new_value = widget.get()
        old_value = row_info["data"][col]
        if new_value == old_value:
            widget.configure(state="disabled")
            return
        row_info["data"][col] = new_value
        row_info["data_vars"][col].set(new_value)
        widget.configure(state="disabled")
        self.update_database(row_info, col, old_value, new_value)

    def update_database(self, row_info, col, old_value, new_value):
        """
        Actualiza en la BD el cambio realizado en la celda.
        Si la fila es nueva y se ingresa la Identificación, se inserta (INSERT);
        en filas existentes se actualiza (UPDATE).
        """
        columns = ["Identificacion", "Nombre", "Codigo_plan", "Fecha_actualizacion"]
        col_name = columns[col]
        if row_info.get("is_new", False):
            # Para un registro nuevo, se inserta cuando el campo Identificación no esté vacío
            if row_info["data"][0] == "":
                return
            try:
                with sqlite3.connect(self.db_path, timeout=5) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO Estudiantes_Aprobados (Identificacion, Nombre, Codigo_plan, Fecha_actualizacion)
                        VALUES (?, ?, ?, ?)
                    """, (row_info["data"][0], row_info["data"][1], row_info["data"][2], row_info["data"][3]))
                    conn.commit()
                row_info["is_new"] = False
                row_info["original_identificacion"] = row_info["data"][0]
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo insertar el estudiante:\n{str(e)}")
        else:
            identificacion = row_info["original_identificacion"]
            try:
                with sqlite3.connect(self.db_path, timeout=5) as conn:
                    cursor = conn.cursor()
                    if col_name == "Identificacion":
                        data = row_info["data"]
                        update_query = """
                            UPDATE Estudiantes_Aprobados
                            SET Identificacion = ?, Nombre = ?, Codigo_plan = ?, Fecha_actualizacion = ?
                            WHERE Identificacion = ?
                        """
                        cursor.execute(update_query, (data[0], data[1], data[2], data[3], old_value))
                        row_info["original_identificacion"] = new_value
                    else:
                        update_query = f"""
                            UPDATE Estudiantes_Aprobados
                            SET {col_name} = ?
                            WHERE Identificacion = ?
                        """
                        cursor.execute(update_query, (new_value, identificacion))
                    conn.commit()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar el estudiante:\n{str(e)}")

    def actualizar_estudiante(self, row_info):
        """
        Actualiza la fecha de actualización a hoy y abre la ventana
        de actualización (que permite actualizar información adicional).
        """
        today = datetime.now().strftime("%d/%m/%Y")
        identificacion = row_info["original_identificacion"]
        try:
            with sqlite3.connect(self.db_path, timeout=5) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE Estudiantes_Aprobados SET Fecha_actualizacion = ? WHERE Identificacion = ?",
                    (today, identificacion)
                )
                conn.commit()
            row_info["data"][3] = today
            row_info["data_vars"][3].set(today)
            self.open_update_window(identificacion, row_info["data"][1], row_info["data"][2])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el estudiante:\n{str(e)}")

    def open_update_window(self, identificacion, nombre, codigo_plan_1):
        """Abre la ventana de actualización (que permite actualizar información adicional)."""
        try:
            from actualizar_estudiante import ActualizarEstudianteWindow
            ActualizarEstudianteWindow(
                parent=self.window,
                nombre_estudiante=nombre,
                plan_text=self.plan_text,
                codigo_plan_1=codigo_plan_1,
                codigo_plan_2=re.search(r'\(([\w\d]+)\)', self.plan_text).group(1),
                identificacion=identificacion,
                db_path=self.db_path
            )
        except ImportError:
            messagebox.showerror("Error", "No se pudo importar la ventana de actualización.")

    def delete_estudiante(self, row_info):
        """Elimina el estudiante de la BD y remueve la fila de la interfaz."""
        identificacion = row_info["original_identificacion"]
        if messagebox.askyesno("Confirmar eliminación", f"¿Eliminar al estudiante con identificación {identificacion}?"):
            try:
                with sqlite3.connect(self.db_path, timeout=5) as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM Estudiantes_Aprobados WHERE Identificacion = ?", (identificacion,))
                    conn.commit()
                row_info["frame"].destroy()
                self.rows_info.remove(row_info)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el estudiante:\n{str(e)}")

    def add_estudiante(self):
        """
        Agrega una nueva fila en la interfaz para un nuevo estudiante.
        Los campos se muestran en estado editable y al editar se actualiza la BD.
        """
        row_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="white")
        row_frame.pack(fill="x", pady=2)
        # Se crean 4 celdas vacías: Identificación, Nombre, Código Plan y Fecha Actualización
        data = ["", "", "", ""]
        data_vars = [ctk.StringVar(value="") for _ in range(4)]
        entries = []
        for i, (var, width) in enumerate(zip(data_vars, self.col_widths[:4])):
            entry = ctk.CTkEntry(row_frame, textvariable=var, width=width, height=30, state="normal")
            entry.pack(side="left", padx=5)
            entries.append(entry)
        # Crear el diccionario de la nueva fila antes de asignar los botones y vinculaciones
        new_row_info = {
            "frame": row_frame,
            "data": data,
            "data_vars": data_vars,
            "entries": entries,
            "original_identificacion": "",
            "is_new": True
        }
        # Botón "Actualizar" con ícono "🗘"
        btn_actualizar = ctk.CTkButton(
            row_frame,
            text="🗘",
            width=self.col_widths[4],
            height=30,
            font=("Arial", 12),
            command=lambda ri=new_row_info: self.actualizar_estudiante(ri)
        )
        btn_actualizar.pack(side="left", padx=5)
        # Botón "Eliminar" con ícono "🗑"
        btn_eliminar = ctk.CTkButton(
            row_frame,
            text="🗑",
            width=self.col_widths[5],
            height=30,
            font=("Arial", 12),
            command=lambda ri=new_row_info: self.delete_estudiante(ri)
        )
        btn_eliminar.pack(side="left", padx=5)
        # Vincular eventos para edición
        for i, entry in enumerate(entries):
            entry.bind("<Double-Button-1>", lambda e, ent=entry, ri=new_row_info, col=i: self.enable_edit(ent, ri, col))
            entry.bind("<Return>", lambda e, ent=entry, ri=new_row_info, col=i: self.save_edit(ent, ri, col))
            entry.bind("<FocusOut>", lambda e, ent=entry, ri=new_row_info, col=i: self.save_edit(ent, ri, col))
        self.rows_info.append(new_row_info)

    def return_to_main_menu(self):
        """Cierra la ventana actual y vuelve al menú principal."""
        self.window.destroy()
        self.parent.deiconify()


if __name__ == "__main__":
    ctk.set_appearance_mode("Light")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    root.geometry("1000x700")
    app = ConsultarEstudiantesWindow(root, db_path="DatosApp.db")
    root.mainloop()

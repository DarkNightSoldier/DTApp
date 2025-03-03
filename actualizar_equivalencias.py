import customtkinter as ctk
import sqlite3
import pandas as pd
from tkinter import ttk, messagebox

class UpdateEquivalencesWindow:
    def __init__(self, parent, db_path="DatosApp.db"):
        self.parent = parent  # Guarda una referencia a la ventana principal
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Actualizar Equivalencias y Convalidaciones")
        self.window.geometry("950x500")
        self.db_path = db_path

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

        # Título principal
        main_label = ctk.CTkLabel(
            self.window,
            text="Equivalencias y convalidaciones",
            font=("Arial", 18, "bold")
        )
        main_label.pack(pady=10)

        # Tabla de equivalencias
        columns = ("Código", "Asignatura", "Código2", "Asignatura2", "Créditos", "Eliminar")
        self.tree = ttk.Treeview(self.window, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        
        self.tree.column("Asignatura", width=200)
        self.tree.column("Asignatura2", width=200)
        self.tree.column("Créditos", width=70)
        self.tree.column("Eliminar", width=70)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<Double-1>", self.on_double_click)

        # Botón para agregar equivalencias
        add_button = ctk.CTkButton(
            self.window,
            text="Agregar equivalencia/convalidación",
            fg_color="#65C2C6",
            text_color="black",
            font=("Arial", 14, "bold"),
            command=self.add_equivalence
        )
        add_button.pack(pady=10)

        self.load_data()
        self.editing_item = None

    def load_data(self):
        with sqlite3.connect(self.db_path, timeout=5) as conn:
            query = """
                SELECT
                    e.Cod_Asignatura AS Código,
                    a1.Nom_Asignatura AS Asignatura,
                    e.Cod_Asignatura_CC AS Código2,
                    a2.Nom_Asignatura AS Asignatura2,
                    a2.Creditos AS Créditos
                FROM Equivalencias AS e
                JOIN Asignaturas_Info AS a1 ON e.Cod_Asignatura = a1.Cod_Asignatura
                JOIN Asignaturas_Info AS a2 ON e.Cod_Asignatura_CC = a2.Cod_Asignatura;
            """
            df = pd.read_sql_query(query, conn)

        # Limpiamos la tabla y volvemos a insertar los datos
        for row in self.tree.get_children():
            self.tree.delete(row)

        for _, row in df.iterrows():
            self.tree.insert("", "end", values=(
                row["Código"],
                row["Asignatura"],
                row["Código2"],
                row["Asignatura2"],
                row["Créditos"],
                "🗑️"
            ))

    def on_double_click(self, event):
        item_id = self.tree.identify_row(event.y)
        column_id = self.tree.identify_column(event.x)
        col_index = int(column_id.replace("#", "")) - 1
        col_name = self.tree["columns"][col_index]

        if not item_id:
            return

        if col_name == "Eliminar":
            self.delete_row(item_id)
        else:
            self.edit_cell(item_id, col_name)

    def edit_cell(self, item_id, col_name):
        x, y, width, height = self.tree.bbox(item_id, col_name)
        old_value = self.tree.set(item_id, col_name)

        self.entry = ctk.CTkEntry(self.window, width=width, height=height)
        self.entry.insert(0, old_value)
        self.entry.focus()
        self.entry.place(x=self.tree.winfo_x() + x, y=self.tree.winfo_y() + y)
        self.editing_item = (item_id, col_name, old_value)

        self.entry.bind("<Return>", self.save_edit)
        self.entry.bind("<FocusOut>", self.save_edit)

    def save_edit(self, event):
        if not self.editing_item:
            return

        item_id, col_name, old_value = self.editing_item
        new_value = self.entry.get()
        self.entry.destroy()
        self.editing_item = None

        if new_value == old_value:
            return

        self.tree.set(item_id, col_name, new_value)

        # Solo actualizamos la base de datos si se cambió Código o Código2
        if col_name in ("Código", "Código2"):
            self.update_equivalencias_in_db(item_id, col_name, old_value, new_value)

    def update_equivalencias_in_db(self, item_id, col_name, old_value, new_value):
        current_values = self.tree.item(item_id, "values")
        codigo = current_values[0]
        codigo2 = current_values[2]

        with sqlite3.connect(self.db_path, timeout=5) as conn:
            cursor = conn.cursor()
            update_query = """
                UPDATE Equivalencias
                SET Cod_Asignatura = ?, Cod_Asignatura_CC = ?
                WHERE Cod_Asignatura = ? AND Cod_Asignatura_CC = ?
            """
            cursor.execute(
                update_query,
                (
                    new_value if col_name == "Código" else codigo,
                    new_value if col_name == "Código2" else codigo2,
                    codigo,
                    codigo2
                )
            )
            conn.commit()

        self.load_data()

    def delete_row(self, item_id):
        values = self.tree.item(item_id, "values")
        codigo, codigo2 = values[0], values[2]

        if messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Eliminar equivalencia?\n(Código={codigo}, Código2={codigo2})"
        ):
            with sqlite3.connect(self.db_path, timeout=5) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM Equivalencias WHERE Cod_Asignatura = ? AND Cod_Asignatura_CC = ?",
                    (codigo, codigo2)
                )
                conn.commit()
            self.tree.delete(item_id)

    def add_equivalence(self):
        # Ventana modal para ingresar datos de la equivalencia
        self.add_window = ctk.CTkToplevel(self.window)
        self.add_window.title("Agregar equivalencia/convalidación")
        self.add_window.geometry("400x320")

        # Etiqueta e ingreso para Código (primer asignatura)
        label_codigo = ctk.CTkLabel(self.add_window, text="Código:")
        label_codigo.pack(pady=(10, 0))
        self.entry_codigo = ctk.CTkEntry(self.add_window)
        self.entry_codigo.pack(pady=5)

        # Etiqueta e ingreso para Nombre Asignatura (primer asignatura)
        label_nombre = ctk.CTkLabel(self.add_window, text="Nombre Asignatura:")
        label_nombre.pack(pady=(10, 0))
        self.entry_nombre = ctk.CTkEntry(self.add_window)
        self.entry_nombre.pack(pady=5)

        # Etiqueta e ingreso para Código2
        label_codigo2 = ctk.CTkLabel(self.add_window, text="Código2:")
        label_codigo2.pack(pady=(10, 0))
        self.entry_codigo2 = ctk.CTkEntry(self.add_window)
        self.entry_codigo2.pack(pady=5)

        # Botón para buscar los datos de Asignatura2 y Créditos a partir del Código2
        buscar_button = ctk.CTkButton(self.add_window, text="Buscar datos", command=self.buscar_datos_codigo2)
        buscar_button.pack(pady=5)

        # Etiquetas y entradas de solo lectura para Asignatura2 y Créditos (marcadas en gris)
        label_asignatura2 = ctk.CTkLabel(self.add_window, text="Asignatura2:")
        label_asignatura2.pack(pady=(10, 0))
        self.entry_asignatura2 = ctk.CTkEntry(
            self.add_window,
            state="disabled",
            placeholder_text="Se autocompleta",
            fg_color="#D3D3D3"
        )
        self.entry_asignatura2.pack(pady=5)

        label_creditos = ctk.CTkLabel(self.add_window, text="Créditos:")
        label_creditos.pack(pady=(10, 0))
        self.entry_creditos = ctk.CTkEntry(
            self.add_window,
            state="disabled",
            placeholder_text="Se autocompleta",
            fg_color="#D3D3D3"
        )
        self.entry_creditos.pack(pady=5)

        # Botón para guardar la equivalencia
        guardar_button = ctk.CTkButton(self.add_window, text="Guardar", command=self.guardar_equivalencia)
        guardar_button.pack(pady=15)

    def buscar_datos_codigo2(self):
        codigo2 = self.entry_codigo2.get().strip()
        if not codigo2:
            messagebox.showerror("Error", "Ingrese un Código2 válido.")
            return

        with sqlite3.connect(self.db_path, timeout=5) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT Nom_Asignatura, Creditos FROM Asignaturas_Info WHERE Cod_Asignatura = ?",
                (codigo2,)
            )
            resultado = cursor.fetchone()

        if resultado:
            asignatura2, creditos = resultado
            # Actualizamos las entradas de solo lectura
            self.entry_asignatura2.configure(state="normal")
            self.entry_asignatura2.delete(0, "end")
            self.entry_asignatura2.insert(0, asignatura2)
            self.entry_asignatura2.configure(state="disabled")

            self.entry_creditos.configure(state="normal")
            self.entry_creditos.delete(0, "end")
            self.entry_creditos.insert(0, creditos)
            self.entry_creditos.configure(state="disabled")
        else:
            messagebox.showerror("Error", f"No se encontró asignatura para el Código2: {codigo2}")

    def guardar_equivalencia(self):
        codigo = self.entry_codigo.get().strip()
        nombre = self.entry_nombre.get().strip()
        codigo2 = self.entry_codigo2.get().strip()
        asignatura2 = self.entry_asignatura2.get().strip()
        creditos = self.entry_creditos.get().strip()

        if not codigo or not nombre or not codigo2 or not asignatura2 or not creditos:
            messagebox.showerror("Error", "Debe completar todos los campos y buscar los datos de Código2.")
            return

        try:
            with sqlite3.connect(self.db_path, timeout=5) as conn:
                cursor = conn.cursor()

                # 1) Verificar si la equivalencia ya existe
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM Equivalencias
                    WHERE Cod_Asignatura = ? 
                      AND Cod_Asignatura_CC = ?
                """, (codigo, codigo2))
                existe_equivalencia = cursor.fetchone()[0]

                if existe_equivalencia > 0:
                    messagebox.showerror(
                        "Error",
                        "Esta equivalencia/convalidación ya existe en la base de datos."
                    )
                    return

                # 2) Verificar si la asignatura (código) ya existe en Asignaturas_Info
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM Asignaturas_Info 
                    WHERE Cod_Asignatura = ?
                """, (codigo,))
                existe_asignatura = cursor.fetchone()[0]

                if existe_asignatura == 0:
                    # No existe: Insertar en Asignaturas_Info
                    cursor.execute("""
                        INSERT INTO Asignaturas_Info 
                            (Cod_Asignatura, Nom_Asignatura, Creditos) 
                        VALUES (?, ?, 0)
                    """, (codigo, nombre))
                else:
                    # Sí existe: Actualizar nombre y poner créditos en 0
                    cursor.execute("""
                        UPDATE Asignaturas_Info 
                        SET Nom_Asignatura = ?, Creditos = 0 
                        WHERE Cod_Asignatura = ?
                    """, (nombre, codigo))

                # 3) Insertar la equivalencia
                cursor.execute("""
                    INSERT INTO Equivalencias (Cod_Asignatura, Cod_Asignatura_CC) 
                    VALUES (?, ?)
                """, (codigo, codigo2))

                conn.commit()

        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar la equivalencia:\n{e}")
            return

        # Cerramos la ventana de agregar y refrescamos la tabla
        self.add_window.destroy()
        self.load_data()

    def load_data(self):
        # Implementa la lógica para cargar los datos en la tabla
        pass

    def return_to_main_menu(self):
        """Función para regresar al menú principal."""
        self.window.destroy()  # Cierra la ventana actual
        self.parent.deiconify()  # Muestra la ventana principal de nuevo

if __name__ == "__main__":
    ctk.set_appearance_mode("Light")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    app = UpdateEquivalencesWindow(root, db_path="DatosApp.db")
    root.mainloop()
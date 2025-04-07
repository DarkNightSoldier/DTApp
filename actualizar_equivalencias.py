import customtkinter as ctk
import sqlite3
import pandas as pd
from tkinter import messagebox, StringVar

class UpdateEquivalencesWindow:
    def __init__(self, parent, plan_text, db_path="DatosApp.db"):
        self.parent = parent
        self.plan_text = plan_text
        self.parent.withdraw()  # Minimiza el menú principal
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Actualizar Equivalencias y Convalidaciones")
        self.window.geometry("1200x550")
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
            command=self.return_to_main_menu
        )
        menu_button.pack(side="left", padx=10, pady=10)

        title_label = ctk.CTkLabel(
            header_frame,
            text=self.plan_text,
            font=("Arial", 16, "bold"),
            text_color="black",
        )
        title_label.pack(side="left", padx=10)

        # Contenedor scrolleable para la tabla de equivalencias
        # CTkScrollableFrame añade automáticamente una barra de scroll vertical.
        self.scrollable_frame = ctk.CTkScrollableFrame(self.window, fg_color="white")
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Botón para agregar nueva equivalencia (abrirá la ventana modal estilo Código 1)
        add_button = ctk.CTkButton(
            self.window,
            text="Agregar equivalencia/convalidación",
            fg_color="#65C2C6",
            text_color="black",
            font=("Arial", 14, "bold"),
            command=self.add_equivalence_window
        )
        add_button.pack(pady=10)

        self.rows_info = []  # Almacenará la información de cada fila creada
        self.load_data()

    def return_to_main_menu(self):
        """Cierra la ventana actual y vuelve a mostrar el menú principal."""
        self.window.destroy()
        self.parent.deiconify()

    def load_data(self):
        """Carga las equivalencias desde la BD y las muestra en la tabla (en modo lectura)."""
        # Limpiar el contenedor scrolleable
        for child in self.scrollable_frame.winfo_children():
            child.destroy()
        self.rows_info.clear()

        try:
            with sqlite3.connect(self.db_path, timeout=5) as conn:
                query = """
                    WITH RankedEquivalencias AS (
                        SELECT 
                            Cod_Asignatura AS Código,
                            (SELECT Nom_Asignatura 
                               FROM Asignaturas_Info 
                              WHERE Cod_Asignatura = e.Cod_Asignatura) AS Asignatura,
                            Cod_Asignatura_CC AS Código2,
                            (SELECT Nom_Asignatura 
                               FROM Asignaturas_Info 
                              WHERE Cod_Asignatura = e.Cod_Asignatura_CC) AS Asignatura2,
                            (SELECT Creditos 
                               FROM Asignaturas_Info 
                              WHERE Cod_Asignatura = e.Cod_Asignatura_CC) AS Créditos,
                            ROW_NUMBER() OVER (
                                PARTITION BY Cod_Asignatura, Cod_Asignatura_CC 
                                ORDER BY Cod_Asignatura, Cod_Asignatura_CC
                            ) AS rn
                        FROM Equivalencias e
                    )
                    SELECT Código, Asignatura, Código2, Asignatura2, Créditos
                    FROM RankedEquivalencias
                    WHERE rn = 1
                    ORDER BY Código;
                """
                df = pd.read_sql_query(query, conn)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los datos:\n{str(e)}")
            return

        # Crear la cabecera de la tabla
        headers_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="white")
        headers_frame.pack(fill="x", pady=5)

        headers = ["Código", "Asignatura", "Código2", "Asignatura2", "Créditos", "Eliminar"]
        col_widths = [70, 400, 70, 400, 70, 60]

        for header, width in zip(headers, col_widths):
            lbl = ctk.CTkLabel(headers_frame, text=header, font=("Arial", 12, "bold"))
            lbl.pack(side="left", padx=5)
            lbl.configure(width=width)

        # Crear las filas en modo "solo lectura"
        if not df.empty:
            for row_index, row_data in enumerate(df.values, start=1):
                self._create_equivalence_row(row_data, col_widths)

    def _create_equivalence_row(self, equivalence_data, col_widths):
        """
        Crea una fila (frame) dentro del self.scrollable_frame con entradas deshabilitadas
        y un botón de eliminación.
        """
        row_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="white")
        row_frame.pack(fill="x", pady=2)

        # Desempaquetar datos
        codigo, asignatura, codigo2, asignatura2, creditos = equivalence_data

        # StringVars para mostrar datos (sin editar)
        code_var   = StringVar(value=str(codigo))
        name_var   = StringVar(value=str(asignatura))
        code2_var  = StringVar(value=str(codigo2))
        name2_var  = StringVar(value=str(asignatura2))
        credit_var = StringVar(value=str(creditos))

        # Entradas en estado 'disabled'
        code_entry = ctk.CTkEntry(row_frame, textvariable=code_var, width=col_widths[0], height=30, state="disabled")
        code_entry.grid(row=0, column=0, padx=5, pady=2)

        name_entry = ctk.CTkEntry(row_frame, textvariable=name_var, width=col_widths[1], height=30, state="disabled")
        name_entry.grid(row=0, column=1, padx=5, pady=2)

        code2_entry = ctk.CTkEntry(row_frame, textvariable=code2_var, width=col_widths[2], height=30, state="disabled")
        code2_entry.grid(row=0, column=2, padx=5, pady=2)

        name2_entry = ctk.CTkEntry(row_frame, textvariable=name2_var, width=col_widths[3], height=30, state="disabled")
        name2_entry.grid(row=0, column=3, padx=5, pady=2)

        credit_entry = ctk.CTkEntry(row_frame, textvariable=credit_var, width=col_widths[4], height=30, state="disabled")
        credit_entry.grid(row=0, column=4, padx=5, pady=2)

        # Botón para eliminar la fila
        delete_btn = ctk.CTkButton(row_frame, text="🗑", width=30, height=30,
                                   font=("Arial", 14), hover_color="#FF0000",
                                   command=lambda: self.delete_equivalence(codigo, codigo2, row_frame))
        delete_btn.grid(row=0, column=5, padx=(10, 5), pady=2)

    def delete_equivalence(self, code, code2, frame_to_destroy):
        """
        Elimina la equivalencia de la BD y la fila correspondiente en la interfaz.
        """
        if messagebox.askyesno("Confirmar eliminación",
                               f"¿Eliminar equivalencia?\n(Código={code}, Código2={code2})"):
            try:
                with sqlite3.connect(self.db_path, timeout=5) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "DELETE FROM Equivalencias WHERE Cod_Asignatura = ? AND Cod_Asignatura_CC = ?",
                        (code, code2)
                    )
                    conn.commit()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar la equivalencia:\n{str(e)}")
                return

            # Eliminar la fila de la interfaz
            frame_to_destroy.destroy()
            # Opcional: recargar toda la tabla
            # self.load_data()

    # Ventana para añadir equivalencias     
    def add_equivalence_window(self):
        self.add_window = ctk.CTkToplevel(self.window)
        self.add_window.title("Agregar equivalencia/convalidación")
        self.add_window.geometry("400x500")
        
        # Hace que la ventana modal sea hija de la ventana principal y se mantenga al frente.
        self.add_window.transient(self.window)
        self.add_window.grab_set()
        self.add_window.focus_set()

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

        # Etiquetas y entradas de solo lectura para Asignatura2 y Créditos
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
        """
        Busca en la BD el nombre y créditos de la asignatura con 'Código2' que
        el usuario introduzca. Luego autocompleta los campos en la ventana.
        """
        codigo2 = self.entry_codigo2.get().strip()
        if not codigo2:
            messagebox.showerror("Error", "Ingrese un Código2 válido.")
            return

        try:
            with sqlite3.connect(self.db_path, timeout=5) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT Nom_Asignatura, Creditos FROM Asignaturas_Info WHERE Cod_Asignatura = ?",
                    (codigo2,)
                )
                resultado = cursor.fetchone()

            if resultado:
                asignatura2, creditos = resultado

                # Habilitar temporalmente para insertar datos
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
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al buscar datos:\n{str(e)}")

    def guardar_equivalencia(self):
        """
        Inserta en la BD la nueva equivalencia, verificando que no exista
        previamente y actualizando la tabla de la interfaz.
        """
        codigo = self.entry_codigo.get().strip()
        nombre = self.entry_nombre.get().strip()
        codigo2 = self.entry_codigo2.get().strip()
        asignatura2 = self.entry_asignatura2.get().strip()
        creditos = self.entry_creditos.get().strip()

        if not (codigo and nombre and codigo2 and asignatura2 and creditos):
            messagebox.showerror(
                "Error",
                "Debe completar todos los campos y buscar los datos de Código2."
            )
            return

        try:
            with sqlite3.connect(self.db_path, timeout=5) as conn:
                cursor = conn.cursor()

                # 1) Verificar si la equivalencia ya existe
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM Equivalencias
                    WHERE Cod_Asignatura = ? AND Cod_Asignatura_CC = ?
                """, (codigo, codigo2))
                existe_equivalencia = cursor.fetchone()[0]

                if existe_equivalencia > 0:
                    messagebox.showerror(
                        "Error",
                        "Esta equivalencia/convalidación ya existe en la base de datos."
                    )
                    return

                # 2) Verificar/insertar/actualizar la asignatura (código)
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM Asignaturas_Info
                    WHERE Cod_Asignatura = ?
                """, (codigo,))
                existe_asignatura = cursor.fetchone()[0]

                if existe_asignatura == 0:
                    # No existe: Insertar en Asignaturas_Info
                    cursor.execute("""
                        INSERT INTO Asignaturas_Info (Cod_Asignatura, Nom_Asignatura, Creditos)
                        VALUES (?, ?, 0)
                    """, (codigo, nombre))
                else:
                    # Sí existe: Actualizar nombre y créditos en 0 (o lo que desees)
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

        # Cerrar la ventana de agregar y refrescar la tabla principal
        self.add_window.destroy()
        self.load_data()

# Ejecución de la ventana principal (demo)
if __name__ == "__main__":
    ctk.set_appearance_mode("Light")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    app = UpdateEquivalencesWindow(root, db_path="DatosApp.db")
    root.mainloop()

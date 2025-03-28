import customtkinter as ctk
import sqlite3
import pandas as pd
from tkinter import messagebox, StringVar

class UpdateEquivalencesWindow:
    is_open = False  # Para rastrear si la ventana está abierta

    def __init__(self, parent, db_path="DatosApp.db"):
        self.parent = parent
        self.parent.withdraw()  # Minimiza el menú principal
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Actualizar Equivalencias y Convalidaciones")
        self.window.geometry("1150x550")
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
            text="Programa: Ciencias de la Computación (2933)",
            font=("Arial", 16, "bold"),
            text_color="black",
        )
        title_label.pack(side="left", padx=10)

        # Contenedor para la tabla de equivalencias
        self.table_container = ctk.CTkFrame(self.window, fg_color="white", corner_radius=8)
        self.table_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Botón para agregar nueva equivalencia
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

    def return_to_main_menu(self):
        """Cierra la ventana actual y vuelve a mostrar el menú principal."""
        self.window.destroy()
        self.parent.deiconify()

    def load_data(self):
        try:
            with sqlite3.connect(self.db_path, timeout=5) as conn:
                query = """
                    WITH RankedEquivalencias AS (
                        SELECT 
                            Cod_Asignatura AS Código,
                            (SELECT Nom_Asignatura FROM Asignaturas_Info WHERE Cod_Asignatura = e.Cod_Asignatura) AS Asignatura,
                            Cod_Asignatura_CC AS Código2,
                            (SELECT Nom_Asignatura FROM Asignaturas_Info WHERE Cod_Asignatura = e.Cod_Asignatura_CC) AS Asignatura2,
                            (SELECT Creditos FROM Asignaturas_Info WHERE Cod_Asignatura = e.Cod_Asignatura_CC) AS Créditos,
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

        # Limpiar el contenedor y la lista de filas actuales
        for child in self.table_container.winfo_children():
            child.destroy()
        
        self.rows_info = []
        
        # Solo crear tabla si hay datos
        if not df.empty:
            self.create_equivalence_table(df.values)

    def create_equivalence_table(self, equivalences):
        # Crear cabecera de la tabla
        headers_frame = ctk.CTkFrame(self.table_container, fg_color="white")
        headers_frame.pack(fill="x", pady=5)

        headers = ["Código", "Asignatura", "Código2", "Asignatura2", "Créditos", "Eliminar"]
        col_widths = [70, 400, 70, 400, 70, 60]

        for header, width in zip(headers, col_widths):
            lbl = ctk.CTkLabel(headers_frame, text=header, font=("Arial", 12, "bold"))
            lbl.pack(side="left", padx=5)
            lbl.configure(width=width)

        # Crear cada una de las filas con sus respectivos widgets
        for row_index, equivalence in enumerate(equivalences, start=1):
            self._create_equivalence_row(self.table_container, row_index, equivalence, col_widths)

    def _create_equivalence_row(self, parent_container, row_index, equivalence, col_widths):
        row_frame = ctk.CTkFrame(parent_container, fg_color="white")
        row_frame.pack(fill="x", pady=2)

        # Inicializar variables con datos provenientes de la BD
        code_var   = StringVar(value=str(equivalence[0]))
        name_var   = StringVar(value=str(equivalence[1]))
        code2_var  = StringVar(value=str(equivalence[2]))
        name2_var  = StringVar(value=str(equivalence[3]))
        credit_var = StringVar(value=str(equivalence[4]))

        # Configurar el grid para utilizar el ancho deseado en cada columna.
        for i, w in enumerate(col_widths):
            row_frame.grid_columnconfigure(i, minsize=w)

        # Crear cada entry y colocarlo en la columna correspondiente
        code_entry = ctk.CTkEntry(row_frame, textvariable=code_var, width=col_widths[0], height=30)
        code_entry.grid(row=0, column=0, padx=5, pady=2, sticky="nsew")

        name_entry = ctk.CTkEntry(row_frame, textvariable=name_var, width=col_widths[1], height=30)
        name_entry.grid(row=0, column=1, padx=5, pady=2, sticky="nsew")

        code2_entry = ctk.CTkEntry(row_frame, textvariable=code2_var, width=col_widths[2], height=30)
        code2_entry.grid(row=0, column=2, padx=5, pady=2, sticky="nsew")

        name2_entry = ctk.CTkEntry(row_frame, textvariable=name2_var, width=col_widths[3], height=30)
        name2_entry.grid(row=0, column=3, padx=5, pady=2, sticky="nsew")

        credit_entry = ctk.CTkEntry(row_frame, textvariable=credit_var, width=col_widths[4], height=30)
        credit_entry.grid(row=0, column=4, padx=5, pady=2, sticky="nsew")

        # Botón para eliminar la fila
        delete_btn = ctk.CTkButton(row_frame, text="🗑", width=30, height=30,
                                   font=("Arial", 14), hover_color="#FF0000")
        delete_btn.grid(row=0, column=5, padx=(10, 5), pady=2)

        # Diccionario que almacena la info relevante de la fila
        row_data = {
            "frame": row_frame,
            "code_var": code_var,
            "name_var": name_var,
            "code2_var": code2_var,
            "name2_var": name2_var,
            "credit_var": credit_var,
            "is_new": False,  # Esta fila proviene de la BD
            "original_code": code_var.get(),
            "original_code2": code2_var.get()
        }

        delete_btn.configure(command=lambda rd=row_data: self.delete_equivalence(rd))

        # Vincular el evento FocusOut a cada campo para actualizar automáticamente la BD
        code_entry.bind("<FocusOut>",   lambda e, rd=row_data: self.update_equivalence_in_db(rd))
        name_entry.bind("<FocusOut>",   lambda e, rd=row_data: self.update_equivalence_in_db(rd))
        code2_entry.bind("<FocusOut>",  lambda e, rd=row_data: self.update_equivalence_in_db(rd))
        name2_entry.bind("<FocusOut>",  lambda e, rd=row_data: self.update_equivalence_in_db(rd))
        credit_entry.bind("<FocusOut>", lambda e, rd=row_data: self.update_equivalence_in_db(rd))

        self.rows_info.append(row_data)

    def add_equivalence(self):
        # Crear una nueva fila con campos vacíos, indicando que es nueva.
        new_row_data = {
            "frame": None,
            "code_var": StringVar(value=""),
            "name_var": StringVar(value=""),
            "code2_var": StringVar(value=""),
            "name2_var": StringVar(value=""),
            "credit_var": StringVar(value=""),
            "is_new": True
        }

        row_frame = ctk.CTkFrame(self.table_container, fg_color="white")
        row_frame.pack(fill="x", pady=2)

        # Crear entries para la nueva fila
        code_entry = ctk.CTkEntry(row_frame, textvariable=new_row_data["code_var"], width=70, height=30)
        code_entry.grid(row=0, column=0, padx=5, pady=2, sticky="nsew")

        name_entry = ctk.CTkEntry(row_frame, textvariable=new_row_data["name_var"], width=400, height=30)
        name_entry.grid(row=0, column=1, padx=5, pady=2, sticky="nsew")

        code2_entry = ctk.CTkEntry(row_frame, textvariable=new_row_data["code2_var"], width=70, height=30)
        code2_entry.grid(row=0, column=2, padx=5, pady=2, sticky="nsew")

        name2_entry = ctk.CTkEntry(row_frame, textvariable=new_row_data["name2_var"], width=400, height=30)
        name2_entry.grid(row=0, column=3, padx=5, pady=2, sticky="nsew")

        credit_entry = ctk.CTkEntry(row_frame, textvariable=new_row_data["credit_var"], width=70, height=30)
        credit_entry.grid(row=0, column=4, padx=5, pady=2, sticky="nsew")

        # Botón de eliminación
        delete_btn = ctk.CTkButton(row_frame, text="🗑", width=30, height=30,
                                   font=("Arial", 14), hover_color="#FF0000",
                                   command=lambda rd=new_row_data: self.delete_equivalence(rd))
        delete_btn.grid(row=0, column=5, padx=(10, 5), pady=2)

        new_row_data["frame"] = row_frame

        # Vincular eventos para la nueva fila
        code_entry.bind("<FocusOut>",   lambda e, rd=new_row_data: self.update_equivalence_in_db(rd))
        name_entry.bind("<FocusOut>",   lambda e, rd=new_row_data: self.update_equivalence_in_db(rd))
        code2_entry.bind("<FocusOut>",  lambda e, rd=new_row_data: self.update_equivalence_in_db(rd))
        name2_entry.bind("<FocusOut>",  lambda e, rd=new_row_data: self.update_equivalence_in_db(rd))
        credit_entry.bind("<FocusOut>", lambda e, rd=new_row_data: self.update_equivalence_in_db(rd))

        self.rows_info.append(new_row_data)

    def update_equivalence_in_db(self, row_data):
        # Recoger los valores actuales
        code   = row_data["code_var"].get().strip()
        name   = row_data["name_var"].get().strip()
        code2  = row_data["code2_var"].get().strip()
        name2  = row_data["name2_var"].get().strip()
        credit = row_data["credit_var"].get().strip()

        # Solo se procede si TODOS los campos tienen valor
        if not code or not name or not code2 or not name2 or not credit:
            return

        try:
            with sqlite3.connect(self.db_path, timeout=5) as conn:
                cursor = conn.cursor()
                
                # Verificar si la equivalencia ya existe
                cursor.execute(
                    "SELECT COUNT(*) FROM Equivalencias WHERE Cod_Asignatura = ? AND Cod_Asignatura_CC = ?",
                    (code, code2)
                )
                existe_equivalencia = cursor.fetchone()[0]

                if row_data.get("is_new", False):
                    if existe_equivalencia > 0:
                        messagebox.showwarning("Duplicado", "Esta equivalencia ya existe en la base de datos.")
                        return

                    # Eliminar cualquier equivalencia preexistente con los mismos códigos
                    cursor.execute(
                        "DELETE FROM Equivalencias WHERE Cod_Asignatura = ? AND Cod_Asignatura_CC = ?",
                        (code, code2)
                    )

                    # Inserción en la base de datos para filas nuevas
                    cursor.execute(
                        "INSERT INTO Equivalencias (Cod_Asignatura, Cod_Asignatura_CC) VALUES (?, ?)",
                        (code, code2)
                    )
                    
                    # Insertar o actualizar información de asignaturas
                    cursor.execute(
                        """INSERT OR REPLACE INTO Asignaturas_Info 
                        (Cod_Asignatura, Nom_Asignatura, Creditos) 
                        VALUES (?, ?, ?)""",
                        (code, name, credit)
                    )
                    cursor.execute(
                        """INSERT OR REPLACE INTO Asignaturas_Info 
                        (Cod_Asignatura, Nom_Asignatura, Creditos) 
                        VALUES (?, ?, ?)""",
                        (code2, name2, credit)
                    )
                    
                    row_data["is_new"] = False
                    row_data["original_code"]  = code
                    row_data["original_code2"] = code2
                    messagebox.showinfo("Guardado", "La nueva equivalencia ha sido guardada correctamente.")
                
                else:
                    # Actualizar filas existentes
                    orig_code  = row_data.get("original_code", code)
                    orig_code2 = row_data.get("original_code2", code2)
                    
                    cursor.execute(
                        "UPDATE Equivalencias SET Cod_Asignatura = ?, Cod_Asignatura_CC = ? "
                        "WHERE Cod_Asignatura = ? AND Cod_Asignatura_CC = ?",
                        (code, code2, orig_code, orig_code2)
                    )
                    
                    cursor.execute(
                        "UPDATE Asignaturas_Info SET Nom_Asignatura = ?, Creditos = ? "
                        "WHERE Cod_Asignatura = ?",
                        (name, credit, orig_code)
                    )
                    
                    cursor.execute(
                        "UPDATE Asignaturas_Info SET Nom_Asignatura = ?, Creditos = ? "
                        "WHERE Cod_Asignatura = ?",
                        (name2, credit, orig_code2)
                    )
                    
                    row_data["original_code"]  = code
                    row_data["original_code2"] = code2
                
                conn.commit()
        
        except Exception as e:
            messagebox.showerror("Error de base de datos",
                                 f"No se pudo actualizar la equivalencia:\n{str(e)}")
        
        # Recargar los datos después de guardar
        finally:
            self.load_data()

    def delete_equivalence(self, row_data):
        code  = row_data["code_var"].get().strip()
        code2 = row_data["code2_var"].get().strip()
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
            
            # Eliminar la fila de la interfaz:
            if row_data in self.rows_info:
                self.rows_info.remove(row_data)
            row_data["frame"].destroy()
            self.load_data()

if __name__ == "__main__":
    ctk.set_appearance_mode("Light")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    app = UpdateEquivalencesWindow(root, db_path="DatosApp.db")
    root.mainloop()
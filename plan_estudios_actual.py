import pandas as pd
import sqlite3

def cargar_componentes():
  # Conexión a la base de datos SQLite
  Apuntador = sqlite3.connect('DatosApp.db')
  cursor = Apuntador.cursor()

  query_1 = """
  SELECT
      a_cc.Cod_Asignatura_CC as Código,
      a_info.Nom_Asignatura as Asignatura,
      a_info.Creditos as Créditos,
      a_cc.Nom_Agrupacion as Agrupación,
      a_cc.Tipo as Tipo
      FROM Asignaturas_CC AS a_cc
      JOIN Asignaturas_Info AS a_info ON a_cc.Cod_Asignatura_CC = a_info.Cod_Asignatura
  """
  componentes = pd.read_sql_query(query_1, Apuntador)
  # Estructura base del JSON que queremos construir
  components = {
      "Fundamentación": {
          "agrupaciones": {}
      },
      "Disciplinar": {
          "agrupaciones": {}
      },
      "Trabajo de grado":{
            "agrupaciones": {}
      }
  }

  # Recorremos cada fila del DataFrame y la ubicamos en la estructura adecuada
  for _, row in componentes.iterrows():
      codigo = row['Código']
      asignatura = row['Asignatura']
      creditos = row['Créditos']
      tipo = row['Tipo']

      # Determinamos el componente
      if tipo in ['B', 'O']:
          componente = 'Fundamentación'
      elif tipo in ['C', 'T']:
          componente = 'Disciplinar'
      elif tipo == 'P':
          componente = 'Trabajo de grado'

      # Determinamos la agrupación (subgrupo) a partir de alguna lógica
      agrupacion = row["Agrupación"]

      # Aseguramos que exista el diccionario de la agrupación dentro del componente
      if agrupacion not in components[componente]['agrupaciones']:
          components[componente]['agrupaciones'][agrupacion] = []

      # Añadimos la asignatura en el formato [Código, Asignatura, Créditos]
      components[componente]['agrupaciones'][agrupacion].append([codigo, asignatura, creditos, tipo])

  # Finalmente, convertimos cada agrupación en la forma {"nombre": ..., "subjects": [...]} 
  for comp, comp_data in components.items():
      nuevas_agrupaciones = []
      for nombre_agrup, lista_subjects in comp_data['agrupaciones'].items():
          nuevas_agrupaciones.append({
              'nombre': nombre_agrup,
              'subjects': lista_subjects
          })
      comp_data['agrupaciones'] = nuevas_agrupaciones

  return components
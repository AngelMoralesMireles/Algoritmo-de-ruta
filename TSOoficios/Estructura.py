import pandas as pd
import random

# 1. Cargar archivo Excel
df = pd.read_excel("Tabla de datos.xlsx")

# 2. Filtrar entregas del día 2
df_dia2 = df[df["Día"] == 2].copy()

# 3. Convertir prioridad en valor numérico
valores_prioridad = {"Alta": 3, "Media": 2,}
df_dia2["Valor"] = df_dia2["Prioridad"].map(valores_prioridad)

# 4. Definir columna de duración de entrega y capacidad (tiempo total disponible)
TIEMPO_COL = "Tiempo estimado entrega (min)"
capacidad_maxima = 450  # minutos disponibles

# 5. Función GRASP + 2-intercambio
def grasp_2intercambio(df, capacidad, iteraciones=100):
    mejor_solucion = []
    mejor_valor = 0
    mejor_tiempo = 0

    for _ in range(iteraciones):
        # a) Generar solución aleatoria sin repetir entregas
        candidatos = df.sample(frac=1).reset_index(drop=True)
        tiempo, valor, seleccion, usados = 0, 0, [], set()

        for idx, row in candidatos.iterrows():
            if idx in usados:
                continue
            if tiempo + row[TIEMPO_COL] <= capacidad:
                seleccion.append((idx, row))
                usados.add(idx)
                tiempo += row[TIEMPO_COL]
                valor += row["Valor"]

        # b) Mejorar solución con 2-intercambio
        indices_en_sol = [i for i, _ in seleccion]
        dentro = [r for _, r in seleccion]
        fuera = df[~df.index.isin(indices_en_sol)]

        for i in range(len(dentro)):
            for idx, nuevo in fuera.iterrows():
                tiempo_nuevo = tiempo - dentro[i][TIEMPO_COL] + nuevo[TIEMPO_COL]
                valor_nuevo = valor - dentro[i]["Valor"] + nuevo["Valor"]
                if tiempo_nuevo <= capacidad and valor_nuevo > valor:
                    tiempo = tiempo_nuevo
                    valor = valor_nuevo
                    dentro[i] = nuevo
                    break

        # c) Guardar si es la mejor solución
        if valor > mejor_valor:
            mejor_solucion = dentro
            mejor_valor = valor
            mejor_tiempo = tiempo

    return pd.DataFrame(mejor_solucion), mejor_tiempo, mejor_valor

# 6. Ejecutar el algoritmo
solucion, tiempo_total, valor_total = grasp_2intercambio(df_dia2, capacidad_maxima)

# 7. Mostrar resultados
print(solucion[[...]])  # selecciona columnas como Hora, Dirección, etc.
print(f"Tiempo total: {tiempo_total}")
print(f"Prioridad total: {valor_total}")

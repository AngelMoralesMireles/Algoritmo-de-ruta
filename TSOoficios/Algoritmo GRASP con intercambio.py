import pandas as pd
import random

# Cargar el archivo Excel
archivo = "BD Registros.xlsx"
df = pd.read_excel(archivo,sheet_name="Datos con el algoritmo")

# Filtrar datos del Día 2
df_dia2 = df[df["Día"] == 2].copy()

# Limpiar y convertir tiempos
df_dia2["TiempoEstimado"] = (
    df_dia2["Tiempo estimado entrega (min)"]
    .astype(str)
    .str.strip()
    .replace("NE", pd.NA)
)
df_dia2["TiempoEstimado"] = pd.to_numeric(df_dia2["TiempoEstimado"], errors="coerce")
df_dia2 = df_dia2.dropna(subset=["TiempoEstimado"])
  # Elimina entregas con tiempo 0

# Asignar valor numérico por prioridad
df_dia2["Valor"] = df_dia2["Prioridad"].apply(lambda p: 3 if p == "Alta" else (2 if p == "Media" else 1))

# Capacidad total de tiempo disponible (en minutos)
capacidad_maxima = 480

# Función GRASP + 2-intercambio
def grasp_2intercambio(df, capacidad, iteraciones=500):
    mejor_solucion = []
    mejor_valor = 0
    mejor_tiempo = 0

    for _ in range(iteraciones):
        df_random = df.sample(frac=1).reset_index(drop=True)
        tiempo = 0
        valor = 0
        solucion = []

        for idx, row in df_random.iterrows():
            if tiempo + row["TiempoEstimado"] <= capacidad:
                solucion.append(idx)
                tiempo += row["TiempoEstimado"]
                valor += row["Valor"]

        # 2-intercambio
        improved = True
        while improved:
            improved = False
            for i in range(len(solucion)):
                for j in range(i+1, len(solucion)):
                    nueva_sol = solucion[:]
                    nueva_sol[i], nueva_sol[j] = nueva_sol[j], nueva_sol[i]
                    nuevo_tiempo = df.iloc[nueva_sol]["TiempoEstimado"].sum()
                    nuevo_valor = df.iloc[nueva_sol]["Valor"].sum()
                    if nuevo_tiempo <= capacidad and nuevo_valor > valor:
                        solucion = nueva_sol
                        tiempo = nuevo_tiempo
                        valor = nuevo_valor
                        improved = True

        if valor > mejor_valor:
            mejor_solucion = solucion
            mejor_valor = valor
            mejor_tiempo = tiempo

    return df.iloc[mejor_solucion], mejor_tiempo, mejor_valor

# Ejecutar
solucion_final, tiempo_usado, prioridad_total = grasp_2intercambio(df_dia2, capacidad_maxima)

# Mostrar resultados
print(" Ruta óptima encontrada:")
print(solucion_final[["Hora de llegada", "Dirección", "Zona", "Prioridad", "TiempoEstimado"]])

print(f"\n⏱ Tiempo total utilizado: {tiempo_usado:.2f} minutos")
print(f"⭐ Prioridad total acumulada: {prioridad_total}")

#  Mostrar conteo por prioridad
prioridades = solucion_final["Prioridad"].value_counts()
baja = prioridades.get("Baja", 0)
media = prioridades.get("Media", 0)
alta = prioridades.get("Alta", 0)
total = len(solucion_final)

print(f"\n Entregas por prioridad:")
print(f" Baja: {baja}")
print(f" Media: {media}")
print(f" Alta: {alta}")
print(f" Total entregas: {total}")

import pandas as pd
from datetime import datetime
import random

# Cargar archivo Excel
archivo = "Registros Algoritmo.xlsx"
df = pd.read_excel(archivo, sheet_name="Hoja1")

# Estandarizar valores en la columna "Prioridad"
df["Prioridad"] = df["Prioridad"].astype(str).str.strip().str.capitalize()

# Diagnóstico inicial
print("\n✅ Columnas encontradas en el archivo:")
print(df.columns.tolist())

print("\n📌 Total de registros en el archivo:", len(df))
print("📋 Valores únicos en 'Día':", df["Día"].unique())
print("📋 Valores únicos en 'Prioridad':", df["Prioridad"].unique())

# Punto de inicio para el día 5
dia_objetivo = 5
punto_inicio = df[(df["Día"] == dia_objetivo) & (df["Prioridad"] == "Inicio")]
print(f"\n🚩 Coincidencias con INICIO y Día {dia_objetivo}:", len(punto_inicio))
direccion_inicio = punto_inicio["Dirección"].iloc[0] if not punto_inicio.empty else "DESCONOCIDO"

# Filtrar entregas válidas para día 5
df_dia = df[(df["Día"] == dia_objetivo) & (df["Prioridad"].isin(["Alta", "Media", "Baja"]))].copy()
print(f"\n📦 Entregas con prioridad Alta, Media o Baja en Día {dia_objetivo}:", len(df_dia))
print("🎯 Prioridades encontradas:", df_dia["Prioridad"].unique())

# Revisar valores únicos antes de limpieza
print("\n🧪 Valores únicos en 'Tiempo estimado entrega (min)':")
print(df_dia["Tiempo estimado entrega (min)"].unique())

# Convertir tiempo estimado a numérico
df_dia["TiempoEstimado"] = pd.to_numeric(
    df_dia["Tiempo estimado entrega (min)"].astype(str).str.strip().replace("NE", pd.NA),
    errors="coerce"
)

# Verificar conversión
print("\n🔍 Registros con TiempoEstimado válido:", df_dia["TiempoEstimado"].notna().sum())

# Limpiar y filtrar
df_dia = df_dia.dropna(subset=["TiempoEstimado"])
df_dia = df_dia[df_dia["TiempoEstimado"] > 0]
print("✅ Registros luego de limpiar TiempoEstimado:", len(df_dia))

# Mostrar una fila como ejemplo
if not df_dia.empty:
    print("\n📄 Ejemplo de fila lista para procesamiento:")
    print(df_dia.iloc[0])
else:
    print("\n⚠️ No hay datos válidos para procesar después de la limpieza.")

# Función para convertir hora a minutos
def hora_a_minutos(hora_str):
    try:
        fmt = "%H:%M:%S" if len(hora_str.split(":")) == 3 else "%H:%M"
        t = datetime.strptime(hora_str.strip(), fmt)
        return t.hour * 60 + t.minute
    except:
        return 0

# Calcular campos adicionales
df_dia["HoraCierreMin"] = df_dia["HoraCierre"].astype(str).apply(hora_a_minutos)
df_dia["Valor"] = df_dia["Prioridad"].map({"Alta": 3, "Media": 2, "Baja": 1})
df_dia["Puntaje"] = df_dia["Valor"] * 10000 - df_dia["HoraCierreMin"]

print("\n🧠 Zonas detectadas:", df_dia["Zona"].unique())
print("📊 Entradas finales listas para algoritmo:", len(df_dia))

# Parámetros
capacidad_maxima = 540  # 9 horas
hora_inicio = 480       # 08:00

# Tiempo estimado de regreso por zona
tiempo_regreso_por_zona = {
    "Centro": 15,
    "Norte": 25,
    "Sur": 30,
    "Poniente": 35,
    "Oriente": 40
}

# Algoritmo GRASP
def grasp_ruta(df, capacidad, inicio=480, iteraciones=500):
    def calcular_tiempo_total(solucion):
        tiempo_actual = inicio
        for idx in solucion:
            duracion = df.loc[idx, "TiempoEstimado"]
            cierre = df.loc[idx, "HoraCierreMin"]
            salida = tiempo_actual + duracion
            if salida > cierre:
                return None
            tiempo_actual = salida
        zona_final = df.loc[solucion[-1], "Zona"] if solucion else None
        tiempo_regreso = tiempo_regreso_por_zona.get(zona_final, 30)
        return tiempo_actual - inicio + tiempo_regreso

    def valor_total(solucion):
        return sum(df.loc[solucion, "Valor"])

    def intercambio_2opt(sol, i, k):
        return sol[:i] + sol[i:k+1][::-1] + sol[k+1:]

    mejor_solucion = []
    mejor_valor = 0
    mejor_horas_llegada = []
    mejor_tiempo_regreso = 0

    for _ in range(iteraciones):
        df_ordenado = df.sort_values(by="Puntaje", ascending=False).copy()
        candidatos = df_ordenado.index.tolist()
        random.shuffle(candidatos)

        solucion = []
        tiempo_actual = inicio
        for idx in candidatos:
            duracion = df.loc[idx, "TiempoEstimado"]
            cierre = df.loc[idx, "HoraCierreMin"]
            salida = tiempo_actual + duracion
            if salida > cierre:
                continue
            zona_temp = df.loc[idx, "Zona"]
            tiempo_regreso = tiempo_regreso_por_zona.get(zona_temp, 30)
            tiempo_total = salida - inicio + tiempo_regreso
            if tiempo_total <= capacidad:
                solucion.append(idx)
                tiempo_actual = salida

        # Búsqueda local
        mejor_local = solucion
        mejora = True
        while mejora and len(mejor_local) > 2:
            mejora = False
            for i in range(len(mejor_local) - 1):
                for k in range(i+1, len(mejor_local)):
                    nueva = intercambio_2opt(mejor_local, i, k)
                    tiempo_total = calcular_tiempo_total(nueva)
                    if tiempo_total is not None and valor_total(nueva) > valor_total(mejor_local):
                        mejor_local = nueva
                        mejora = True
                        break
                if mejora:
                    break

        if valor_total(mejor_local) > mejor_valor:
            mejor_solucion = mejor_local
            mejor_valor = valor_total(mejor_local)
            tiempo_actual = inicio
            mejor_horas_llegada = []
            for idx in mejor_solucion:
                mejor_horas_llegada.append(tiempo_actual)
                tiempo_actual += df.loc[idx, "TiempoEstimado"]
            zona_final = df.loc[mejor_solucion[-1], "Zona"]
            mejor_tiempo_regreso = tiempo_regreso_por_zona.get(zona_final, 30)

    df_resultado = df.loc[mejor_solucion].copy().reset_index(drop=True)
    df_resultado["Hora de llegada"] = [f"{h//60:02d}:{h%60:02d}" for h in mejor_horas_llegada]
    return df_resultado, mejor_horas_llegada, mejor_valor, mejor_tiempo_regreso

# Ejecutar GRASP para día 5
solucion_final, llegadas, prioridad_total, tiempo_regreso = grasp_ruta(df_dia, capacidad_maxima, hora_inicio)

# Mostrar resultados
print(f"\n🚩 Punto de inicio de la ruta: {direccion_inicio}")
print("\n📦 Ruta óptima encontrada:")
print(solucion_final[["Hora de llegada", "Dirección", "Zona", "Prioridad", "TiempoEstimado", "HoraCierre"]])

tiempo_entregas = sum(solucion_final["TiempoEstimado"])
tiempo_total = tiempo_entregas + tiempo_regreso
print(f"\n⏱ Tiempo total utilizado en entregas: {tiempo_entregas:.2f} minutos")
print(f"⏱ Tiempo estimado de regreso a la base: {tiempo_regreso} minutos")
print(f"⏱ Tiempo total jornada estimado (entregas + regreso): {tiempo_total:.2f} minutos")
print(f"⏰ Hora estimada de inicio: 08:00")

if llegadas:
    hora_regreso = llegadas[-1] + solucion_final.iloc[-1]["TiempoEstimado"] + tiempo_regreso
    h_regreso_str = f"{hora_regreso//60:02.0f}:{hora_regreso%60:02.0f}"
    print(f"🛑 Hora estimada de llegada a base (regreso): {h_regreso_str}")
else:
    print("⚠️ No hay entregas programadas.")

# Estadísticas de prioridad
prioridades = solucion_final["Prioridad"].value_counts()
print(f"\n📊 Entregas por prioridad:")
print(f"🔴 Baja: {prioridades.get('Baja', 0)}")
print(f"🟡 Media: {prioridades.get('Media', 0)}")
print(f"🟢 Alta: {prioridades.get('Alta', 0)}")
print(f"📦 Total entregas: {len(solucion_final)}")

total_alta = df_dia[df_dia["Prioridad"] == "Alta"].shape[0]
porcentaje_alta = (prioridades.get("Alta", 0) / total_alta) * 100 if total_alta > 0 else 0
print(f"\n📈 % de entregas de alta prioridad realizadas: {porcentaje_alta:.2f}% de {total_alta}")

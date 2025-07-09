import pandas as pd
from datetime import datetime
import random

# Cargar archivo Excel
archivo = "BD Registros.xlsx"
df = pd.read_excel(archivo, sheet_name="Datos con el algoritmo")

# Punto de inicio
punto_inicio = df[(df["Día"] == 2) & (df["Prioridad"] == "INICIO")]
direccion_inicio = punto_inicio["Dirección"].iloc[0] if not punto_inicio.empty else "DESCONOCIDO"

# Filtrar entregas válidas
df_dia2 = df[(df["Día"] == 2) & (df["Prioridad"].isin(["Alta", "Media", "Baja"]))].copy()

# Limpiar y convertir tiempos
df_dia2["TiempoEstimado"] = pd.to_numeric(
    df_dia2["Tiempo estimado entrega (min)"].astype(str).str.strip().replace("NE", pd.NA),
    errors="coerce"
)
df_dia2 = df_dia2.dropna(subset=["TiempoEstimado"])
df_dia2 = df_dia2[df_dia2["TiempoEstimado"] > 0]

# Función para convertir a minutos
def hora_a_minutos(hora_str):
    try:
        fmt = "%H:%M:%S" if len(hora_str.split(":")) == 3 else "%H:%M"
        t = datetime.strptime(hora_str.strip(), fmt)
        return t.hour * 60 + t.minute
    except:
        return 0

# Agregar tiempos en minutos
df_dia2["HoraAperturaMin"] = df_dia2["HoraApertura"].astype(str).apply(hora_a_minutos)
df_dia2["HoraCierreMin"] = df_dia2["HoraCierre"].astype(str).apply(hora_a_minutos)
df_dia2["Valor"] = df_dia2["Prioridad"].map({"Alta": 3, "Media": 2, "Baja": 1})

# Parámetros de jornada
capacidad_maxima = 540  # 9 horas en minutos
hora_inicio = 480       # 08:00 en minutos

# Tiempo estimado de regreso por zona
tiempo_regreso_por_zona = {
    "Centro": 15,
    "Norte": 25,
    "Sur": 30,
    "Poniente": 35,
    "Oriente": 40
}

def grasp_ruta_local_search(df, capacidad, inicio=480, iteraciones=500):
    def calcular_tiempo_total(solucion, df):
        tiempo_actual = inicio
        for idx in solucion:
            apertura = df.loc[idx, "HoraAperturaMin"]
            duracion = df.loc[idx, "TiempoEstimado"]
            llegada = max(tiempo_actual, apertura)
            salida = llegada + duracion
            cierre = df.loc[idx, "HoraCierreMin"]
            if salida > cierre:
                return None  # Ruta no válida
            tiempo_actual = salida
        tiempo_recorrido = tiempo_actual - inicio
        zona_final = df.loc[solucion[-1], "Zona"] if solucion else None
        tiempo_regreso = tiempo_regreso_por_zona.get(zona_final, 30) if zona_final else 30
        return tiempo_recorrido + tiempo_regreso

    def valor_total(solucion, df):
        return sum(df.loc[solucion, "Valor"])

    def intercambio_2opt(solucion, i, k):
        return solucion[:i] + solucion[i:k+1][::-1] + solucion[k+1:]

    # 1. Primer bloque: entregas disponibles a las 8:00
    grupo_A = df[df["HoraAperturaMin"] <= inicio].copy()
    grupo_A = grupo_A.sort_values(by=["Valor", "HoraCierreMin", "TiempoEstimado"], ascending=[False, True, True])
    solucion_A = []
    tiempo_actual = inicio
    tiempo_usado = 0

    for idx, row in grupo_A.iterrows():
        apertura = row["HoraAperturaMin"]
        duracion = row["TiempoEstimado"]
        cierre = row["HoraCierreMin"]
        llegada = max(tiempo_actual, apertura)
        salida = llegada + duracion
        if salida <= cierre and (salida - inicio) <= 60:  # Solo 60 minutos para primer bloque
            solucion_A.append(idx)
            tiempo_actual = salida
            tiempo_usado = tiempo_actual - inicio
        else:
            break

    # 2. Segundo bloque: entregas restantes después de las 9:00
    tiempo_inicio_B = inicio + 60  # 09:00
    capacidad_restante = capacidad - tiempo_usado

    grupo_B = df.drop(solucion_A)
    grupo_B = grupo_B.sort_values(by=["Valor", "HoraCierreMin", "TiempoEstimado"], ascending=[False, True, True])
    mejor_valor_B = 0
    mejor_solucion_B = []

    for _ in range(iteraciones):
        solucion_parcial = []
        tiempo_actual = tiempo_inicio_B
        valor_parcial = 0
        candidatos = grupo_B.index.tolist()
        random.shuffle(candidatos)  # Diversidad en búsqueda

        for idx in candidatos:
            apertura = df.loc[idx, "HoraAperturaMin"]
            duracion = df.loc[idx, "TiempoEstimado"]
            cierre = df.loc[idx, "HoraCierreMin"]
            llegada = max(tiempo_actual, apertura)
            salida = llegada + duracion
            if salida > cierre or (salida - tiempo_inicio_B) > capacidad_restante:
                continue
            solucion_parcial.append(idx)
            valor_parcial += df.loc[idx, "Valor"]
            tiempo_actual = salida

        # Búsqueda local 2-opt para mejorar la solución parcial
        mejor_local = solucion_parcial.copy()
        mejor_valor_local = valor_parcial
        mejora = True
        while mejora and len(mejor_local) > 2:
            mejora = False
            for i in range(len(mejor_local) - 1):
                for k in range(i + 1, len(mejor_local)):
                    nueva_sol = intercambio_2opt(mejor_local, i, k)
                    tiempo_total = calcular_tiempo_total(nueva_sol, df)
                    if tiempo_total is not None and tiempo_total <= capacidad_restante:
                        valor_nuevo = valor_total(nueva_sol, df)
                        if valor_nuevo > mejor_valor_local:
                            mejor_local = nueva_sol
                            mejor_valor_local = valor_nuevo
                            mejora = True
                            break
                if mejora:
                    break

        if mejor_valor_local > mejor_valor_B:
            mejor_valor_B = mejor_valor_local
            mejor_solucion_B = mejor_local

    # Combinar ambas soluciones
    solucion_final = solucion_A + mejor_solucion_B

    # Calcular horas de llegada para solución completa
    horas_llegada = []
    tiempo_actual = inicio
    for idx in solucion_final:
        apertura = df.loc[idx, "HoraAperturaMin"]
        duracion = df.loc[idx, "TiempoEstimado"]
        llegada = max(tiempo_actual, apertura)
        horas_llegada.append(llegada)
        tiempo_actual = llegada + duracion

    df_resultado = df.loc[solucion_final].copy().reset_index(drop=True)
    df_resultado["Hora de llegada"] = [f"{h//60:02d}:{h%60:02d}" for h in horas_llegada]

    # Tiempo de regreso
    zona_final = df.loc[solucion_final[-1], "Zona"] if solucion_final else None
    tiempo_regreso = tiempo_regreso_por_zona.get(zona_final, 30) if zona_final else 30

    return df_resultado, horas_llegada, sum(df.loc[solucion_final, "Valor"]), tiempo_regreso


# Ejecutar función
solucion_final, llegadas, prioridad_total, tiempo_regreso = grasp_ruta_local_search(df_dia2, capacidad_maxima, hora_inicio)

# Mostrar resultados
print(f"\n🚩 Punto de inicio de la ruta: {direccion_inicio}")
print("\n📦 Ruta óptima encontrada:")
print(solucion_final[["Hora de llegada", "Dirección", "Zona", "Prioridad", "TiempoEstimado", "HoraApertura", "HoraCierre"]])

# Calcular tiempos
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
    print("No hay entregas programadas.")

# Estadísticas de prioridad
prioridades = solucion_final["Prioridad"].value_counts()
print(f"\n📊 Entregas por prioridad:")
print(f"🔴 Baja: {prioridades.get('Baja', 0)}")
print(f"🟡 Media: {prioridades.get('Media', 0)}")
print(f"🟢 Alta: {prioridades.get('Alta', 0)}")
print(f"📦 Total entregas: {len(solucion_final)}")

total_alta = df_dia2[df_dia2["Prioridad"] == "Alta"].shape[0]
porcentaje_alta = (prioridades.get("Alta", 0) / total_alta) * 100 if total_alta > 0 else 0
print(f"\n📈 % de entregas de alta prioridad realizadas: {porcentaje_alta:.2f}% de {total_alta}")

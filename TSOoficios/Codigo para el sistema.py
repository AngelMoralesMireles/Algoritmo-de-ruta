import pandas as pd
from datetime import datetime, timedelta
import random

# --- Función para convertir tiempo estimado a minutos ---
def tiempo_a_minutos(valor):
    try:
        if isinstance(valor, pd.Timedelta):
            return valor.total_seconds() / 60
        elif isinstance(valor, str):
            t = datetime.strptime(valor.strip(), "%H:%M:%S")
            return t.hour * 60 + t.minute
        elif pd.notna(valor):
            return float(valor)
    except:
        return pd.NA

# --- Función para convertir hora a minutos ---
def hora_a_minutos(hora_str):
    try:
        fmt = "%H:%M:%S" if len(hora_str.split(":")) == 3 else "%H:%M"
        t = datetime.strptime(hora_str.strip(), fmt)
        return t.hour * 60 + t.minute
    except:
        return 0

# --- Función para obtener siguiente día laboral ---
def siguiente_dia_laboral(fecha):
    siguiente = fecha + timedelta(days=1)
    while siguiente.weekday() >= 5:  # 5 = sábado, 6 = domingo
        siguiente += timedelta(days=1)
    return siguiente

# --- Cargar y preparar datos ---
archivo = "export_folios.xlsx"
df = pd.read_excel(archivo)

# Normalizar columnas
df["prioridad"] = df["prioridad"].astype(str).str.strip().str.capitalize()
df["entregado"] = df["entregado"].astype(str).str.strip().str.lower()
df["fecha_folio"] = pd.to_datetime(df["fecha_folio"], errors="coerce").dt.date

# Obtener fecha objetivo
fecha_objetivo = df["fecha_folio"].dropna().min()
print(f"📆 Fecha objetivo de trabajo: {fecha_objetivo}")

# Filtrar datos válidos
df_dia = df[(df["fecha_folio"] == fecha_objetivo) & (df["prioridad"].isin(["Alta", "Media", "Baja"]))].copy()
df_dia["Entregado"] = df_dia["entregado"].isin(["true", "1", "si", "yes"])
df_pendientes = df_dia[~df_dia["Entregado"]].copy()

if df_pendientes.empty:
    print("✅ Todos los oficios ya fueron entregados para esta fecha.")
    exit()

df_pendientes["TiempoEstimado"] = df_pendientes["tiempo_estimado_entrega"].apply(tiempo_a_minutos)
df_pendientes = df_pendientes.dropna(subset=["TiempoEstimado"])
df_pendientes = df_pendientes[df_pendientes["TiempoEstimado"] > 0]
df_pendientes["HoraCierreMin"] = df_pendientes["hora_cierre"].astype(str).apply(hora_a_minutos)
df_pendientes["Valor"] = df_pendientes["prioridad"].map({"Alta": 3, "Media": 2, "Baja": 1})
df_pendientes["Puntaje"] = df_pendientes["Valor"] * 100000 - df_pendientes["HoraCierreMin"]

# Parámetros
capacidad_maxima = 480
hora_inicio = 8 * 60
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
        zona_final = df.loc[solucion[-1], "zona"] if solucion else None
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
            zona_temp = df.loc[idx, "zona"]
            tiempo_regreso = tiempo_regreso_por_zona.get(zona_temp, 30)
            tiempo_total = salida - inicio + tiempo_regreso
            if tiempo_total <= capacidad:
                solucion.append(idx)
                tiempo_actual = salida

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
            zona_final = df.loc[mejor_solucion[-1], "zona"]
            mejor_tiempo_regreso = tiempo_regreso_por_zona.get(zona_final, 30)

    df_resultado = df.loc[mejor_solucion].copy().reset_index(drop=True)
    df_resultado["Hora de llegada"] = [f"{h//60:02d}:{h%60:02d}" for h in mejor_horas_llegada]
    return df_resultado, mejor_horas_llegada, mejor_valor, mejor_tiempo_regreso

# Ejecutar GRASP
solucion_final, llegadas, prioridad_total, tiempo_regreso = grasp_ruta(df_pendientes, capacidad_maxima, hora_inicio)

print(f"\n📦 Ruta óptima encontrada con {len(solucion_final)} entregas:")
print(solucion_final[["Hora de llegada", "direccion", "zona", "prioridad", "tiempo_estimado_entrega", "hora_cierre"]])

tiempo_entregas = sum(solucion_final["TiempoEstimado"])
tiempo_total = tiempo_entregas + tiempo_regreso

prioridades = solucion_final["prioridad"].value_counts()
total_alta = df_pendientes[df_pendientes["prioridad"] == "Alta"].shape[0]
porcentaje_alta = (prioridades.get("Alta", 0) / total_alta) * 100 if total_alta > 0 else 0

# --- Guardar oficios NO entregados ---
oficios_entregados_idx = solucion_final.index
oficios_no_entregados_idx = df_pendientes.index.difference(oficios_entregados_idx)
if len(oficios_no_entregados_idx) > 0:
    fecha_nueva = siguiente_dia_laboral(fecha_objetivo)
    df.loc[oficios_no_entregados_idx, "fecha_folio"] = fecha_nueva
    df.loc[oficios_no_entregados_idx, "entregado"] = "false"
    nombre_archivo = f"oficios_pendientes_{fecha_nueva}.xlsx"
    df.loc[oficios_no_entregados_idx].to_excel(nombre_archivo, index=False)
    print(f"\n📁 Oficios NO entregados guardados para el {fecha_nueva} en: {nombre_archivo}")
else:
    print("\n✅ Todos los oficios fueron entregados hoy.")

# --- Crear resumen ---
resumen_datos = {
    "Fecha objetivo": [fecha_objetivo],
    "Entregas realizadas": [len(solucion_final)],
    "Tiempo en entregas (min)": [round(tiempo_entregas, 2)],
    "Tiempo de regreso (min)": [tiempo_regreso],
    "Jornada total estimada (min)": [round(tiempo_total, 2)],
    "Entregas Alta": [prioridades.get('Alta', 0)],
    "Entregas Media": [prioridades.get('Media', 0)],
    "Entregas Baja": [prioridades.get('Baja', 0)],
    "% Alta entregada": [round(porcentaje_alta, 2)]
}
df_resumen = pd.DataFrame(resumen_datos)

# --- Guardar todo en un solo Excel con dos hojas ---
nombre_archivo_completo = f"resultado_entregas_{fecha_objetivo}.xlsx"
with pd.ExcelWriter(nombre_archivo_completo, engine='xlsxwriter') as writer:
    solucion_final.to_excel(writer, sheet_name="Ruta óptima", index=False)
    df_resumen.to_excel(writer, sheet_name="Resumen", index=False)

print(f"\n💾 Ruta óptima y resumen guardados en '{nombre_archivo_completo}'")

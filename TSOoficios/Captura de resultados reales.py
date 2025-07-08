import pandas as pd

# Cargar el archivo Excel (cambiar 'sheet_name' si es necesario)
archivo = "BD Registros.xlsx"
df = pd.read_excel(archivo, sheet_name= "Datos reales")  # o sheet_name="Hoja1" si tiene nombre

# Filtrar solo Día 2
df_dia2 = df[df["Día"] == 2].copy()

# Limpiar columna de tiempo estimado
df_dia2["TiempoEstimado"] = (
    df_dia2["Tiempo estimado entrega (min)"]
    .astype(str)
    .str.strip()
    .replace("NE", pd.NA)
)
df_dia2["TiempoEstimado"] = pd.to_numeric(df_dia2["TiempoEstimado"], errors="coerce")

# Eliminar filas sin tiempo estimado
df_dia2 = df_dia2.dropna(subset=["TiempoEstimado"])

# Asignar valor por prioridad
df_dia2["Valor"] = df_dia2["Prioridad"].apply(lambda p: 3 if p == "Alta" else (2 if p == "Media" else 1))

# Limite de tiempo (8 horas = 480 minutos)
limite_minutos = 480
tiempo_acumulado = 0
entregas_realizadas = []

# Recorrer entregas en el mismo orden y detener cuando se excede el límite
for _, row in df_dia2.iterrows():
    if tiempo_acumulado + row["TiempoEstimado"] <= limite_minutos:
        entregas_realizadas.append(row)
        tiempo_acumulado += row["TiempoEstimado"]
    else:
        break

# Crear DataFrame con entregas hechas
df_entregadas = pd.DataFrame(entregas_realizadas)

# Calcular prioridad acumulada
prioridad_total = df_entregadas["Valor"].sum()

# Contar entregas por prioridad
conteo_prioridades = df_entregadas["Prioridad"].value_counts()

# Mostrar resultados
print("📦 Entregas realizadas (en orden original, hasta 480 minutos):")
print(df_entregadas[["Hora de llegada", "Dirección", "Zona", "Prioridad", "TiempoEstimado"]])

print(f"\n⏱ Tiempo total utilizado: {tiempo_acumulado:.2f} minutos")
print(f"⭐ Prioridad total acumulada: {prioridad_total}")

print("\n📊 Cantidad de entregas por prioridad:")
print(f"Alta : {conteo_prioridades.get('Alta', 0)}")
print(f"Media: {conteo_prioridades.get('Media', 0)}")
print(f"Baja : {conteo_prioridades.get('Baja', 0)}")
print(f"Total: {len(df_entregadas)}")

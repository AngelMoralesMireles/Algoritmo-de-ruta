import pandas as pd
from datetime import datetime

# Cargar archivo Excel
archivo = "Registros Algoritmo.xlsx"
df = pd.read_excel(archivo, sheet_name="Hoja1")

# Estandarizar valores en la columna "Prioridad"
df["Prioridad"] = df["Prioridad"].astype(str).str.strip().str.capitalize()

# Seleccionar día 5
dia_objetivo = 5

# Filtrar entregas con prioridad Alta, Media o Baja y Día 5
df_dia = df[(df["Día"] == dia_objetivo) & (df["Prioridad"].isin(["Alta", "Media", "Baja"]))].copy()

# Crear columna "Entregado" (True si no es "NE", False si es "NE")
df_dia["Entregado"] = ~df_dia["Se entregó"].astype(str).str.upper().eq("NE")

# Filtrar sólo las entregas que efectivamente se entregaron para la ruta
df_entregadas = df_dia[df_dia["Entregado"]].copy()

# Convertir "Tiempo estimado entrega (min)" a numérico y limpiar
df_entregadas["TiempoEstimado"] = pd.to_numeric(df_entregadas["Tiempo estimado entrega (min)"], errors="coerce")
df_entregadas = df_entregadas.dropna(subset=["TiempoEstimado"])
df_entregadas = df_entregadas[df_entregadas["TiempoEstimado"] > 0]

# Función para convertir hora a minutos
def hora_a_minutos(hora_str):
    try:
        fmt = "%H:%M:%S" if len(hora_str.split(":")) == 3 else "%H:%M"
        t = datetime.strptime(hora_str.strip(), fmt)
        return t.hour * 60 + t.minute
    except:
        return 0

df_entregadas["HoraCierreMin"] = df_entregadas["HoraCierre"].astype(str).apply(hora_a_minutos)

# Mostrar la ruta original (orden Excel) para entregas válidas
print(f"\n Ruta original del usuario para el día {dia_objetivo} (solo entregas efectivas):\n")
print(df_entregadas[["Hora de llegada", "Dirección", "Zona", "Prioridad", "Tiempo estimado entrega (min)", "HoraCierre", "Se entregó", "Entregado"]])

# Calcular tiempos usando sólo entregas efectivas
tiempo_entregas = df_entregadas["TiempoEstimado"].sum()
tiempo_regreso = 15
tiempo_total = tiempo_entregas + tiempo_regreso

print(f"\n Tiempo total utilizado en entregas: {tiempo_entregas:.2f} minutos")
print(f" Tiempo estimado de regreso a la base: {tiempo_regreso} minutos")
print(f" Tiempo total jornada estimado (entregas + regreso): {tiempo_total:.2f} minutos")
print(f" Hora estimada de inicio: 08:00")

# Calcular hora de llegada a la base desde la última entrega efectuada
def hora_str_a_minutos(hora):
    try:
        hora = str(hora).strip().lower().replace(".", "")
        if "am" in hora or "pm" in hora:
            return datetime.strptime(hora, "%I:%M %p").hour * 60 + datetime.strptime(hora, "%I:%M %p").minute
        elif len(hora.split(":")) == 3:
            return datetime.strptime(hora, "%H:%M:%S").hour * 60 + datetime.strptime(hora, "%H:%M:%S").minute
        elif len(hora.split(":")) == 2:
            return datetime.strptime(hora, "%H:%M").hour * 60 + datetime.strptime(hora, "%H:%M").minute
    except:
        return None

hora_ultima_entrega_str = df_entregadas["Hora de llegada"].iloc[-1]
minutos_ultima_entrega = hora_str_a_minutos(hora_ultima_entrega_str)

if minutos_ultima_entrega is not None:
    minutos_llegada_base = minutos_ultima_entrega + tiempo_regreso
    hora_llegada_base = f"{int(minutos_llegada_base // 60):02}:{int(minutos_llegada_base % 60):02}"
    print(f" Hora estimada de llegada a base (desde última entrega): {hora_llegada_base}")
else:
    print(" No se pudo calcular la hora de regreso a base desde la última entrega (formato inválido).")

# Estadísticas con base en todo el día 5 (sin filtrar por entregas)
prioridades_totales = df_dia["Prioridad"].value_counts()
total_entregas_dia = len(df_dia)
total_entregas_alta_prioridad = df_dia[df_dia["Prioridad"] == "Alta"].shape[0]

# Estadísticas con base en entregas realizadas
prioridades_entregadas = df_entregadas["Prioridad"].value_counts()
total_entregadas = len(df_entregadas)

print(f"\n Entregas por prioridad (original):")
print(f" Baja: {prioridades_entregadas.get('Baja', 0)}")
print(f" Media: {prioridades_entregadas.get('Media', 0)}")
print(f" Alta: {prioridades_entregadas.get('Alta', 0)}")
print(f" Total entregas realizadas: {total_entregadas}")

# % de entregas alta prioridad realizadas (entregadas sobre total)
porcentaje_alta = (prioridades_entregadas.get("Alta", 0) / total_entregas_alta_prioridad) * 100 if total_entregas_alta_prioridad > 0 else 0
print(f"\n % de entregas de alta prioridad realizadas (original): {porcentaje_alta:.2f}% de {total_entregas_alta_prioridad}")

# Estado entregas (basado en todo el día 5)
entregadas_real = df_dia["Entregado"].sum()
no_entregadas_real = total_entregas_dia - entregadas_real
print(f"\n Estado de entregas:")
print(f" Entregadas: {entregadas_real} ({entregadas_real / total_entregas_dia * 100:.2f}%)")
print(f" No entregadas: {no_entregadas_real} ({no_entregadas_real / total_entregas_dia * 100:.2f}%)")

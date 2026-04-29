# Optimizador de rutas con GRASP

Proyecto en Python para generar una ruta recomendada de entregas a partir de datos cargados desde Excel.

El objetivo del sistema es ayudar a seleccionar y ordenar entregas considerando prioridad, tiempo disponible, zona, horarios de cierre y tiempo estimado de entrega. Para esto se utiliza una heurística basada en **GRASP** con mejora local mediante intercambio.

## Introducción

En una jornada de entregas no siempre es posible visitar todos los destinos disponibles. Algunas entregas pueden tener mayor prioridad, horarios límite o tiempos de traslado diferentes.

Este proyecto busca apoyar ese proceso generando una ruta recomendada que aproveche mejor el tiempo disponible y dé prioridad a las entregas más importantes.

El sistema procesa registros desde un archivo Excel, limpia los datos principales, aplica el algoritmo de optimización y muestra una ruta final con información útil para la toma de decisiones.

## Tecnologías utilizadas

- Python
- Pandas
- OpenPyXL
- XlsxWriter
- Excel como fuente de datos
- Algoritmo GRASP
- Búsqueda local por intercambio

## Características

- Lectura de registros desde archivos Excel.
- Limpieza y preparación de datos.
- Filtrado de entregas por día o fecha.
- Clasificación de entregas por prioridad: alta, media y baja.
- Conversión de horarios y tiempos a minutos.
- Cálculo de puntaje según prioridad y hora de cierre.
- Generación de rutas considerando restricciones de tiempo.
- Estimación de hora de llegada a cada destino.
- Cálculo de tiempo total de entregas.
- Cálculo de tiempo estimado de regreso a base.
- Conteo de entregas por prioridad.
- Generación de archivo Excel con resultados.

## Lo que el usuario puede hacer

Con este sistema, el usuario puede:

- Cargar una base de entregas desde Excel.
- Obtener una ruta recomendada para una jornada.
- Priorizar entregas importantes.
- Consultar el tiempo total estimado de la ruta.
- Identificar cuántas entregas de prioridad alta, media y baja se incluyen.
- Generar un archivo de salida con la ruta optimizada y un resumen.

## Proceso general

El sistema sigue este flujo:

1. Carga el archivo Excel con los registros de entregas.
2. Limpia y normaliza los datos principales.
3. Filtra las entregas correspondientes al día o fecha objetivo.
4. Convierte tiempos y horarios a valores numéricos.
5. Asigna un valor numérico a cada entrega según su prioridad.
6. Genera soluciones candidatas mediante GRASP.
7. Mejora las soluciones usando intercambio local.
8. Selecciona la mejor ruta encontrada.
9. Calcula horas de llegada, tiempo total y estadísticas.
10. Exporta los resultados a un archivo Excel.

## Cómo lo construí

El proyecto fue desarrollado en Python utilizando Pandas para la lectura, limpieza y manipulación de datos desde Excel.

Primero se trabajó con una versión inicial del algoritmo, donde se filtraban entregas por día, se convertían los tiempos estimados y se asignaba un valor numérico a cada prioridad.

Después se implementó GRASP para generar varias soluciones posibles de forma iterativa. Cada solución se construye seleccionando entregas que respetan la capacidad máxima de tiempo y los horarios de cierre.

Posteriormente se agregó una etapa de mejora local mediante intercambio, con el objetivo de encontrar una combinación de entregas con mayor valor total sin superar las restricciones de tiempo.

Finalmente, se agregó la exportación de resultados a Excel, incluyendo la ruta recomendada y un resumen de la jornada.

## Algoritmo utilizado

El proyecto utiliza una heurística GRASP, que trabaja en dos etapas principales:

### Construcción de solución

Se genera una ruta candidata seleccionando entregas que cumplen con las restricciones de tiempo, prioridad y horario de cierre.

### Mejora local

Después de construir una solución inicial, se aplica intercambio local para intentar mejorar la ruta.  
La solución solo se actualiza si mejora el valor total y sigue cumpliendo con las restricciones establecidas.

## Entrada esperada

El sistema espera un archivo Excel con registros de entregas.  
Los archivos reales de datos no se incluyen en el repositorio por motivos de privacidad y limpieza del proyecto.

Ejemplo de columnas esperadas:

```text
nombre
direccion
zona
prioridad
fecha_folio
hora_apertura

Salida generada

El programa puede mostrar en consola información como:

Ruta óptima encontrada
Hora de llegada
Dirección
Zona
Prioridad
Tiempo estimado de entrega
Hora de cierre
Tiempo total utilizado
Tiempo estimado de regreso
Entregas por prioridad

Cómo ejecutar el proyecto
1. Clonar el repositorio
git clone https://github.com/tu-usuario/nombre-del-repositorio.git
cd nombre-del-repositorio
2. Crear entorno virtual
python -m venv venv

Activar entorno virtual en Windows:

venv\Scripts\activate

Activar entorno virtual en Linux o Mac:

source venv/bin/activate
3. Instalar dependencias
pip install pandas openpyxl xlsxwriter

O, si el repositorio incluye requirements.txt:

pip install -r requirements.txt
4. Agregar archivo Excel

Coloca tu archivo Excel en la carpeta principal del proyecto o en una carpeta data/.

Ejemplo:

data/export_folios.xlsx

Después, verifica que el nombre del archivo coincida con el que se carga en el código.

Ejemplo dentro del código:

archivo = "export_folios.xlsx"

O si está dentro de una carpeta:

archivo = "data/export_folios.xlsx"
5. Ejecutar el programa
python main.py

Si el archivo conserva otro nombre, por ejemplo:

python "Codigo para el sistema.py"
Estructura sugerida del proyecto
optimizador-rutas-grasp/
│
├── src/
│   └── main.py
│
├── data/
│   └── .gitkeep
│
├── output/
│   └── .gitkeep
│
├── README.md
├── requirements.txt
└── .gitignore
Nota sobre los archivos de datos

Los archivos Excel y documentos utilizados durante el desarrollo no se incluyen en este repositorio.

Esto se hizo para evitar publicar datos reales o archivos innecesarios.
Para probar el proyecto, se puede utilizar un archivo Excel propio con la estructura indicada en la sección de entrada esperada.

Lo que aprendí

Con este proyecto reforcé conocimientos sobre:

Manipulación de datos con Pandas.
Lectura y escritura de archivos Excel.
Limpieza de datos antes de ejecutar un algoritmo.
Conversión de horarios y tiempos.
Aplicación de heurísticas para problemas de optimización.
Uso de GRASP para generar soluciones aproximadas.
Mejora local mediante intercambio.
Exportación de resultados para análisis posterior.

También aprendí que en problemas de optimización, la calidad de los datos de entrada es muy importante, ya que valores incompletos, formatos distintos o registros no válidos pueden afectar el resultado final.

Posibles mejoras

Algunas mejoras futuras para el proyecto son:

Crear una interfaz gráfica o web para cargar archivos Excel.
Permitir seleccionar la fecha o día objetivo desde la interfaz.
Agregar un archivo Excel de ejemplo con datos ficticios.
Integrar cálculo de distancias reales mediante mapas.
Mostrar la ruta en un mapa interactivo.
Permitir configurar la jornada máxima de trabajo.
Guardar historial de rutas generadas.
Comparar la ruta original contra la ruta optimizada.
Agregar pruebas unitarias.
Separar el código en módulos para mejorar su mantenimiento.
Estado del proyecto

Proyecto funcional en etapa de prototipo académico.

Actualmente permite procesar registros desde Excel, aplicar una heurística de optimización y generar una ruta recomendada con resumen de resultados.

hora_cierre
tiempo_estimado_entrega
entregado

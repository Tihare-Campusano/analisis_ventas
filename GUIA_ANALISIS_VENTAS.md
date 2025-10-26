# Guía Completa del Análisis de Ventas

## 📋 Tabla de Contenidos

1. [Resumen General](#resumen-general)
2. [Estructura del Proyecto](#estructura-del-proyecto)
3. [Descripción de los Datos](#descripción-de-los-datos)
4. [Análisis del Código](#análisis-del-código)
5. [Funcionalidades Implementadas](#funcionalidades-implementadas)
6. [Flujo de Ejecución](#flujo-de-ejecución)
7. [Requisitos y Dependencias](#requisitos-y-dependencias)
8. [Cómo Usar el Análisis](#cómo-usar-el-análisis)
9. [Resultados del Análisis](#resultados-del-análisis)
10. [Mejoras Futuras](#mejoras-futuras)

---

## 📊 Resumen General

Este análisis de ventas es una aplicación Python que procesa datos de transacciones comerciales almacenadas en un archivo CSV. El sistema realiza:

- **Limpieza y validación de datos** para garantizar calidad
- **Análisis de ventas mensuales** para identificar tendencias temporales
- **Identificación de productos líderes** (más vendidos y con mayor ingreso)
- **Visualización de datos** mediante gráficos interactivos

---

## 📁 Estructura del Proyecto

```
analisis_ventas/
├── analisis.py          # Script principal del análisis
├── ventas.csv           # Datos de ventas en formato CSV
└── GUIA_ANALISIS_VENTAS.md  # Esta guía
```

---

## 📄 Descripción de los Datos

### Archivo: ventas.csv

El archivo de datos contiene información sobre las ventas realizadas con las siguientes columnas:

| Columna   | Tipo      | Descripción                                    |
|-----------|-----------|------------------------------------------------|
| fecha     | Date      | Fecha de la venta (formato: YYYY-MM-DD)       |
| producto  | String    | Nombre del producto vendido                    |
| cantidad  | Integer   | Cantidad de unidades vendidas                 |
| precio  | Float     | Precio unitario del producto                  |

### Ejemplo de Datos

```csv
fecha,producto,cantidad,precio
2025-01-06,A,2,10.0
2025-01-07,B,1,20.0
2025-01-08,C,2,5.0
```

### Características del Dataset Actual

- **Período**: Enero a Marzo 2025
- **Productos**: A, B, C, D
- **Total de registros**: 61 transacciones
- **Rango de fechas**: 2025-01-06 al 2025-03-28

---

## 🔍 Análisis del Código

### Función: `cargar_datos(ruta_archivo)`

**Ubicación**: Líneas 6-21 de `analisis.py`

**Propósito**: Cargar y validar el archivo CSV de ventas.

**Proceso**:
1. Verifica que el archivo existe en el sistema
2. Lee el contenido usando pandas
3. Valida que contiene las columnas requeridas: `fecha`, `producto`, `cantidad`, `precio`
4. Retorna un DataFrame con los datos cargados

**Manejo de errores**:
- Si el archivo no existe, muestra mensaje y termina el programa
- Si hay error en la lectura, muestra el error y termina
- Si faltan columnas, muestra las columnas requeridas y termina

```6:21:analisis.py
def cargar_datos(ruta_archivo):
    if not os.path.isfile(ruta_archivo):
        print(f"Error: El archivo '{ruta_archivo}' no existe.")
        sys.exit(1)
    try:
        df = pd.read_csv(ruta_archivo)
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
        sys.exit(1)

    columnas_esperadas = {'fecha', 'producto', 'cantidad', 'precio'}
    if not columnas_esperadas.issubset(df.columns):
        print(f"Error: El archivo debe contener las columnas: {columnas_esperadas}")
        sys.exit(1)

    return df
```

---

### Función: `limpiar_y_transformar(df)`

**Ubicación**: Líneas 23-38 de `analisis.py`

**Propósito**: Limpiar datos y crear campos calculados.

**Proceso de limpieza**:
1. **Eliminar valores nulos** en columnas críticas
2. **Convertir fechas** a formato datetime
3. **Convertir cantidades y precios** a numéricos
4. **Filtrar valores inválidos** (negativos o cero)
5. **Crear columnas derivadas**:
   - `año`: Año de la venta
   - `mes`: Mes de la venta
   - `total_venta`: Cálculo de `cantidad × precio`

```23:38:analisis.py
def limpiar_y_transformar(df):
    # Eliminar filas con valores faltantes en columnas críticas
    df = df.dropna(subset=['fecha', 'producto', 'cantidad', 'precio'])
    # Corregir posibles tipos de datos incorrectos
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    df = df.dropna(subset=['fecha'])
    df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce')
    df['precio'] = pd.to_numeric(df['precio'], errors='coerce')
    df = df.dropna(subset=['cantidad', 'precio'])
    # Eliminar filas con cantidades o precios negativos o cero
    df = df[(df['cantidad'] > 0) & (df['precio'] > 0)]

    df['año'] = df['fecha'].dt.year
    df['mes'] = df['fecha'].dt.month
    df['total_venta'] = df['cantidad'] * df['precio']
    return df
```

**Campos calculados**:
- `total_venta = cantidad × precio`: Total de cada transacción

---

### Función: `calcular_ventas_por_mes(df)`

**Ubicación**: Líneas 40-42 de `analisis.py`

**Propósito**: Agrupar ventas por mes y año.

**Método**: Usa `groupby` para sumar todas las ventas de cada mes:

```40:42:analisis.py
def calcular_ventas_por_mes(df):
    total_ventas_por_mes = df.groupby(['año', 'mes'])['total_venta'].sum()
    return total_ventas_por_mes
```

**Resultado**: Serie con total de ventas por mes (índice: (año, mes))

---

### Función: `extraer_resumen_productos(df)`

**Ubicación**: Líneas 44-60 de `analisis.py`

**Propósito**: Identificar productos más relevantes.

**Análisis realizado**:
1. Producto más vendido (por cantidad)
2. Producto con mayor ingreso (por total de ventas)

**Proceso**:
1. Agrupa por producto y suma cantidades
2. Agrupa por producto y suma ingresos totales
3. Identifica el máximo de cada métrica

```44:60:analisis.py
def extraer_resumen_productos(df):
    resumen = {}
    cantidades_por_producto = df.groupby('producto')['cantidad'].sum()
    if cantidades_por_producto.empty:
        resumen['producto_mas_vendido'] = None
        resumen['cantidad_producto_mas_vendido'] = 0
    else:
        resumen['producto_mas_vendido'] = cantidades_por_producto.idxmax()
        resumen['cantidad_producto_mas_vendido'] = cantidades_por_producto.max()
    ingresos_por_producto = df.groupby('producto')['total_venta'].sum()
    if ingresos_por_producto.empty:
        resumen['producto_mayor_ingreso'] = None
        resumen['ingreso_producto_mayor'] = 0.0
    else:
        resumen['producto_mayor_ingreso'] = ingresos_por_producto.idxmax()
        resumen['ingreso_producto_mayor'] = ingresos_por_producto.max()
    return resumen
```

---

### Función: `graficar_ventas_por_mes(total_ventas_por_mes)`

**Ubicación**: Líneas 62-74 de `analisis.py`

**Propósito**: Visualizar las ventas mensuales en un gráfico de barras.

**Características**:
- Gráfico de barras vertical
- Eje X: Meses (formato YYYY-MM)
- Eje Y: Total de ventas
- Rotación de 45° en etiquetas

```62:74:analisis.py
def graficar_ventas_por_mes(total_ventas_por_mes):
    if total_ventas_por_mes.empty:
        print("No hay datos suficientes para graficar ventas por mes.")
        return
    fig, ax = plt.subplots(figsize=(8, 5))
    etiquetas = [f"{año}-{mes:02d}" for (año, mes) in total_ventas_por_mes.index]
    ax.bar(etiquetas, total_ventas_por_mes.values, color='skyblue')
    ax.set_xlabel('Mes')
    ax.set_ylabel('Total de Ventas')
    ax.set_title('Ventas Totales por Mes')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
```

---

### Función: `graficar_top_productos(df, top_n=5)`

**Ubicación**: Líneas 76-92 de `analisis.py`

**Propósito**: Visualizar los top N productos por ingresos totales.

**Características**:
- Gráfico de barras horizontal
- Muestra los top N productos (por defecto 5)
- Valores etiquetados en cada barra
- Ordena por ingreso total descendente

```76:92:analisis.py
def graficar_top_productos(df, top_n=5):
    ingresos_productos = df.groupby('producto')['total_venta'].sum()
    if ingresos_productos.empty:
        print("No hay datos suficientes para graficar top productos por ingreso.")
        return
    top_productos = ingresos_productos.sort_values(ascending=False).head(top_n)
    fig, ax = plt.subplots(figsize=(7, 4))
    barras = ax.bar(top_productos.index, top_productos.values, color='orange')
    ax.set_xlabel('Producto')
    ax.set_ylabel('Ingreso Total')
    ax.set_title(f'Top {top_n} Productos por Ingreso')
    # Añadir etiquetas a las barras
    for bar in barras:
        ax.annotate(f"{bar.get_height():.2f}", xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                    xytext=(0,3), textcoords="offset points", ha='center', va='bottom', fontsize=8)
    plt.tight_layout()
    plt.show()
```

---

### Función: `main()`

**Ubicación**: Líneas 94-116 de `analisis.py`

**Propósito**: Orquestar todo el flujo del análisis.

**Flujo de ejecución**:

```94:116:analisis.py
def main():
    ruta_archivo = 'ventas.csv'
    df = cargar_datos(ruta_archivo)
    df = limpiar_y_transformar(df)
    if df.empty:
        print("No hay datos válidos después de limpiar el dataset.")
        sys.exit(1)

    total_ventas_por_mes = calcular_ventas_por_mes(df)
    resumen = extraer_resumen_productos(df)

    if resumen['producto_mas_vendido'] is not None:
        print(f"Producto más vendido: {resumen['producto_mas_vendido']} (Cantidad: {resumen['cantidad_producto_mas_vendido']})")
    else:
        print("No se encontró un producto más vendido.")

    if resumen['producto_mayor_ingreso'] is not None:
        print(f"Producto con mayor ingreso: {resumen['producto_mayor_ingreso']} (Ingreso: {resumen['ingreso_producto_mayor']:.2f})")
    else:
        print("No se encontró un producto con mayor ingreso.")

    graficar_ventas_por_mes(total_ventas_por_mes)
    graficar_top_productos(df, top_n=5)
```

1. Carga `ventas.csv`
2. Limpia y transforma los datos
3. Calcula ventas por mes
4. Extrae resumen de productos
5. Imprime resultados en consola
6. Genera dos gráficos

---

## ⚙️ Funcionalidades Implementadas

### 1. Carga de Datos Robusta
- Validación de existencia del archivo
- Verificación de estructura de columnas
- Manejo de errores de lectura

### 2. Limpieza de Datos
- Eliminación de valores faltantes
- Conversión de tipos de datos
- Filtrado de valores inválidos (negativos, ceros)

### 3. Análisis Temporal
- Agrupación de ventas por mes
- Visualización de tendencias temporales

### 4. Análisis de Productos
- Identificación del producto más vendido
- Identificación del producto con mayor ingreso
- Ranking de productos por ingresos

### 5. Visualización
- Gráfico de barras para ventas mensuales
- Gráfico de barras para top productos
- Etiquetas con valores en las barras

---

## 🔄 Flujo de Ejecución

```
INICIO
  ↓
[1] Cargar archivo ventas.csv
  ↓
[2] Validar estructura de datos
  ↓
[3] Limpiar datos (eliminar nulos, convertir tipos)
  ↓
[4] Crear campos derivados (año, mes, total_venta)
  ↓
[5] Calcular ventas por mes
  ↓
[6] Extraer resumen de productos
  ↓
[7] Mostrar resultados en consola
  ↓
[8] Generar gráfico de ventas por mes
  ↓
[9] Generar gráfico de top productos
  ↓
FIN
```

---

## 📦 Requisitos y Dependencias

### Librerías Utilizadas

| Librería       | Versión | Propósito                             |
|----------------|---------|---------------------------------------|
| pandas         | -      | Manipulación y análisis de datos     |
| matplotlib     | -      | Generación de gráficos                |
| os             | -      | Manejo de rutas y archivos (built-in)|
| sys            | -      | Manejo de errores y salida (built-in)|

### Instalación de Dependencias

```bash
pip install pandas matplotlib
```

### Requisitos del Sistema
- Python 3.6 o superior
- Sistema operativo: Windows, Linux o macOS

---

## 🚀 Cómo Usar el Análisis

### Ejecución Básica

1. **Verificar que existe el archivo `ventas.csv`** en el mismo directorio
2. **Asegurarse de tener las dependencias instaladas**:
   ```bash
   pip install pandas matplotlib
   ```
3. **Ejecutar el script**:
   ```bash
   python analisis.py
   ```

### Formato de Datos Requerido

El archivo CSV debe tener exactamente estas columnas:
- `fecha`: Fecha en formato YYYY-MM-DD
- `producto`: Nombre del producto
- `cantidad`: Cantidad vendida (número entero o decimal)
- `precio`: Precio unitario (número decimal)

### Personalización

Para analizar un archivo diferente, modifica la línea 95 de `analisis.py`:

```python
ruta_archivo = 'tu_archivo.csv'
```

Para cambiar el número de productos top, modifica la línea 116:

```python
graficar_top_productos(df, top_n=10)  # Cambiar 5 a 10
```

---

## 📈 Resultados del Análisis

### Salida en Consola

El script imprime dos líneas con los resultados principales:

1. **Producto más vendido**: Muestra el producto con mayor cantidad de unidades vendidas
2. **Producto con mayor ingreso**: Muestra el producto que genera más ingresos totales

**Ejemplo de salida**:
```
Producto más vendido: B (Cantidad: 45)
Producto con mayor ingreso: D (Ingreso: 900.00)
```

### Gráficos Generados

1. **Gráfico de Ventas por Mes**:
   - Muestra la evolución de ventas mes a mes
   - Permite identificar tendencias y estacionalidad

2. **Gráfico de Top Productos**:
   - Muestra los 5 productos con mayor ingreso
   - Incluye valores numéricos en cada barra

---

## 🔮 Mejoras Futuras

### Análisis Adicional
- [ ] Análisis de tendencias con predicción de ventas
- [ ] Comparación año sobre año
- [ ] Análisis de estacionalidad
- [ ] Identificación de outliers y valores atípicos
- [ ] Análisis de correlación entre productos

### Visualizaciones
- [ ] Gráfico de línea temporal para tendencias
- [ ] Gráfico de torta para distribución de ventas
- [ ] Heatmap de ventas por día de la semana
- [ ] Dashboard interactivo con múltiples gráficos

### Funcionalidades
- [ ] Exportación de resultados a PDF
- [ ] Exportación de gráficos a imágenes (PNG, JPG)
- [ ] Soporte para múltiples formatos de entrada (Excel, JSON)
- [ ] Configuración mediante archivo de parámetros
- [ ] Análisis comparativo entre períodos

### Robustez
- [ ] Manejo avanzado de errores con logging
- [ ] Validación de datos con mayor detalle
- [ ] Tests unitarios para cada función
- [ ] Documentación con docstrings

### Arquitectura
- [ ] Separar en módulos (carga, limpieza, análisis, visualización)
- [ ] Crear clases para mejor organización
- [ ] Configuración externa (archivo config)

---

## 📝 Notas Adicionales

### Limitaciones Actuales

1. El análisis asume datos históricos únicamente
2. No incluye análisis predictivo
3. Las visualizaciones se abren en ventanas separadas
4. No hay exportación automática de resultados

### Mejores Prácticas Implementadas

✅ **Separación de responsabilidades**: Cada función tiene un propósito específico
✅ **Validación de datos**: Múltiples verificaciones antes de procesar
✅ **Manejo de errores**: Control de excepciones en operaciones críticas
✅ **Código legible**: Nombres descriptivos y comentarios claros
✅ **Verificaciones de datos vacíos**: Evita errores en visualizaciones

---

## 📞 Conclusión

Este análisis de ventas proporciona una base sólida para entender el rendimiento comercial mediante:

- Procesamiento robusto de datos
- Análisis temporal y de productos
- Visualizaciones claras
- Resultados concisos y accionables

El código está diseñado para ser fácil de entender, modificar y extender según las necesidades específicas de cada negocio.

---

**Última actualización**: Enero 2025
**Autor**: Sistema de Análisis de Ventas
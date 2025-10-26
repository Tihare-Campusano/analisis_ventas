import matplotlib.pyplot as plt
import pandas as pd
import os
import sys

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

def calcular_ventas_por_mes(df):
    total_ventas_por_mes = df.groupby(['año', 'mes'])['total_venta'].sum()
    return total_ventas_por_mes

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

if __name__ == "__main__":
    main()

from volvo_scraper.db import setup_database, iniciar_ejecucion, registrar_producto
from volvo_scraper.scraper import obtener_enlaces_a_escanear, scrapear_enlaces
from volvo_scraper.utils import descargar_imagenes_y_actualizar_productos, generar_archivos

def main():
    conn, cursor = setup_database()
    execution_id = iniciar_ejecucion(cursor)

    url = "https://volvorepuestos.com.pe"
    query = "fh,fm,fmx,vm,fe,fl"
    search = ''

    enlaces = obtener_enlaces_a_escanear(url, query, search)

    productos = scrapear_enlaces(enlaces)
    
    descargar_imagenes_y_actualizar_productos(productos)

    print(f"Total de productos: {len(productos)}")

    for producto in productos:
        registrar_producto(cursor, execution_id, producto['codigo'], producto['descripcion'], producto['precio_normal'], producto['precio_descuento'], producto['imagen'], producto['porcentaje_descuento'])

    generar_archivos(productos, execution_id, conn)

    conn.close()

if __name__ == '__main__':
    main()

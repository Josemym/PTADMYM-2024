import os
import requests
import sqlite3

def descargar_imagenes_y_actualizar_productos(productos):
    for producto in productos:
        imagen_url = producto['imagen']
        codigo = producto['codigo']
        imagen_nombre = f"{codigo.replace(' ', '_')}{os.path.splitext(imagen_url)[1]}"
        try:
            descargar_imagen(imagen_url, imagen_nombre)
            producto['imagen'] = imagen_nombre
        except Exception as e:
            print(f"Advertencia: {e}")
            producto['imagen'] = None

def descargar_imagen(imagen_url, nombre_archivo):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'}
    response = requests.get(imagen_url, headers=headers)
    if response.status_code == 200:
        with open(os.path.join('assets', nombre_archivo), 'wb') as f:
            f.write(response.content)
    else:
        raise Exception(f"Error al descargar la imagen: {response.status_code}")
import os
import requests
import sqlite3
import csv
import json

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

def generar_archivos(productos, execution_id, conn):
    csv_filename = f'respuestos_{execution_id}.csv'
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['codigo', 'descripcion', 'precio_normal', 'precio_descuento', 'imagen', 'porcentaje_descuento']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for producto in productos:
            writer.writerow(producto)

    json_filename = f'repuesto_{execution_id}.json'
    with open(json_filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(productos, jsonfile, indent=4)

    sql_filename = 'query.sql'
    with open(sql_filename, 'w', encoding='utf-8') as sqlfile:
        for line in conn.iterdump():
            sqlfile.write(f'{line}\n')   
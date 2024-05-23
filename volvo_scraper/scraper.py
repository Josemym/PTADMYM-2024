import requests
import sqlite3
from bs4 import BeautifulSoup
import re

def obtener_enlaces_a_escanear(url, query=None, search=None):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    menu = soup.find('nav', class_='navigation sw-megamenu')
    enlaces = set()

    if menu:
        if query:
            queries = [q.lower().strip() for q in re.split(',|-', query)]
            if search == 'all':
                for link in menu.find_all('a'):
                    href = link.get('href')
                    text = link.get_text(strip=True).lower()
                    if any(q in text for q in queries):
                        enlaces.add(href)
            else:
                for link in menu.find_all('a'):
                    href = link.get('href')
                    text = link.get_text(strip=True).lower()
                    parent_li = link.find_parent('li', class_='ui-menu-item')
                    if parent_li and 'level2' in parent_li.get('class', []):
                        continue
                    if any(q in text for q in queries):
                        enlaces.add(href)
        else:
            for link in menu.find_all('a', class_='level-top custom-attribute'):
                href = link.get('href')
                enlaces.add(href)

    return list(enlaces)

def obtener_productos_en_pagina(url, pagina):
    response = requests.get(f"{url}?p={pagina}")
    soup = BeautifulSoup(response.content, 'html.parser')
    contenedor_productos = soup.find('div', class_='products wrapper grid columns4 products-grid')
    if not contenedor_productos:
        return []

    productos_html = contenedor_productos.find_all('li', class_='item product product-item')
    productos = []

    for producto_html in productos_html:
        codigo = producto_html.find('div', class_='marca').find_all('span')[-1].text.strip()
        descripcion = producto_html.find('a', class_='product-item-link').text.strip()
        imagen_url = producto_html.find('img', class_='product-image-photo default_image')['src']
        
        precios = producto_html.find('div', class_='price-box price-final_price')
        precio_normal = precio_descuento = porcentaje_descuento = None
        
        old_price_span = precios.find('span', class_='old-price')
        special_price_span = precios.find('span', class_='special-price')
        final_price_span = precios.find('span', class_='price-wrapper')

        if old_price_span and special_price_span:
            precio_normal = float(old_price_span.find('span', class_='price-wrapper')['data-price-amount'])
            precio_descuento = float(special_price_span.find('span', class_='price-wrapper')['data-price-amount'])
            porcentaje_descuento = obtener_porcentaje_descuento(precio_normal, precio_descuento)
        elif final_price_span:
            precio_normal = float(final_price_span['data-price-amount'])
        
        productos.append({
            'codigo': codigo,
            'descripcion': descripcion,
            'precio_normal': precio_normal,
            'precio_descuento': precio_descuento,
            'imagen': imagen_url,
            'porcentaje_descuento': porcentaje_descuento
        })

    return productos

def obtener_porcentaje_descuento(precio_normal, precio_descuento):
    if precio_normal > 0:
        return round((1 - (precio_descuento / precio_normal)) * 100, 2)
    return 0

def scrapear_enlaces(enlaces):
    productos = []
    productos_unicos = {}

    for enlace in enlaces:
        pagina = 1
        while True:
            productos_pagina = obtener_productos_en_pagina(enlace, pagina)
            if not productos_pagina:
                break
            for producto in productos_pagina:
                codigo = producto['codigo']
                if codigo not in productos_unicos:
                    productos_unicos[codigo] = producto
            pagina += 1

    productos = list(productos_unicos.values())
    return productos
 

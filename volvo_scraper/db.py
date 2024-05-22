import sqlite3
from datetime import datetime


def setup_database():
    conn = sqlite3.connect('productos.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS productos (
                    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo TEXT UNIQUE NOT NULL,
                    descripcion TEXT NOT NULL,
                    precio_normal REAL NOT NULL,
                    precio_descuento REAL,
                    imagen TEXT,
                    porcentaje_descuento REAL
                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS ejecuciones (
                    execution_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    execution_time TEXT NOT NULL
                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS historial_cambios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER,
                    execution_id INTEGER,
                    change_date TEXT NOT NULL,
                    change_type TEXT NOT NULL,
                    old_value TEXT,
                    new_value TEXT,
                    FOREIGN KEY (product_id) REFERENCES productos (product_id),
                    FOREIGN KEY (execution_id) REFERENCES ejecuciones (execution_id)
                )''')

    return conn, c

def iniciar_ejecucion(cursor):
    execution_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('INSERT INTO ejecuciones (execution_time) VALUES (?)', (execution_time,))
    cursor.connection.commit()
    return cursor.lastrowid

def registrar_producto(cursor, execution_id, codigo, descripcion, precio_normal, precio_descuento, imagen, porcentaje_descuento):
    cursor.execute('SELECT product_id, descripcion, precio_normal, precio_descuento, porcentaje_descuento FROM productos WHERE codigo = ?', (codigo,))
    row = cursor.fetchone()

    change_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if row:
        product_id, old_descripcion, old_precio_normal, old_precio_descuento, old_porcentaje_descuento = row

        if old_descripcion != descripcion:
            cursor.execute('INSERT INTO historial_cambios (product_id, execution_id, change_date, change_type, old_value, new_value) VALUES (?, ?, ?, ?, ?, ?)',
                      (product_id, execution_id, change_date, 'descripcion', old_descripcion, descripcion))
            cursor.execute('UPDATE productos SET descripcion = ? WHERE product_id = ?', (descripcion, product_id))

        if old_precio_normal != precio_normal:
            cursor.execute('INSERT INTO historial_cambios (product_id, execution_id, change_date, change_type, old_value, new_value) VALUES (?, ?, ?, ?, ?, ?)',
                      (product_id, execution_id, change_date, 'precio_normal', old_precio_normal, precio_normal))
            cursor.execute('UPDATE productos SET precio_normal = ? WHERE product_id = ?', (precio_normal, product_id))

        if old_precio_descuento != precio_descuento:
            cursor.execute('INSERT INTO historial_cambios (product_id, execution_id, change_date, change_type, old_value, new_value) VALUES (?, ?, ?, ?, ?, ?)',
                      (product_id, execution_id, change_date, 'precio_descuento', old_precio_descuento, precio_descuento))
            cursor.execute('UPDATE productos SET precio_descuento = ? WHERE product_id = ?', (precio_descuento, product_id))

        if old_porcentaje_descuento != porcentaje_descuento:
            cursor.execute('INSERT INTO historial_cambios (product_id, execution_id, change_date, change_type, old_value, new_value) VALUES (?, ?, ?, ?, ?, ?)',
                      (product_id, execution_id, change_date, 'porcentaje_descuento', old_porcentaje_descuento, porcentaje_descuento))
            cursor.execute('UPDATE productos SET porcentaje_descuento = ? WHERE product_id = ?', (porcentaje_descuento, product_id))
        
    else:
        cursor.execute('INSERT INTO productos (codigo, descripcion, precio_normal, precio_descuento, imagen, porcentaje_descuento) VALUES (?, ?, ?, ?, ?, ?)', 
                  (codigo, descripcion, precio_normal, precio_descuento, imagen, porcentaje_descuento))

    cursor.connection.commit()
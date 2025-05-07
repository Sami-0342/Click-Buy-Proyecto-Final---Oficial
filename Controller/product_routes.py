from flask import Blueprint, request, render_template, jsonify, redirect
from werkzeug.utils import secure_filename
import os
from Model.database import get_connection
from config import Config
from Controller.main_routes import nose
from flask import Blueprint, render_template

product_bp = Blueprint('product', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@product_bp.route('/agregar_producto', methods=['GET', 'POST'])
def agregar_producto():
    if request.method == 'POST':
        nombre_producto = request.form['nombre_producto']
        descripcion = request.form['descripcion']
        cantidad_disponible = request.form['cantidad_disponible']
        precio = request.form['precio']
        imagen = request.files['imagen']

        imagen_path = None
        if imagen and allowed_file(imagen.filename):
            filename = secure_filename(imagen.filename)
            imagen_path = f'product_images/{filename}'
            imagen.save(os.path.join(Config.UPLOAD_FOLDER, filename))

        conexion = get_connection()
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO producto (nombre_producto, cantidad_disponible, descripcion, precio, Imagen) VALUES (?, ?, ?, ?, ?)",
                    (nombre_producto, cantidad_disponible, descripcion, precio, imagen_path))
        conexion.commit()
        cursor.close()

        return redirect('/Catalogo')

    return render_template('agregar_producto.html')

@product_bp.route('/eliminar_producto', methods=['POST'])
def eliminar_producto():
    try:
        conexion = get_connection()
        data = request.get_json()
        producto_id = data.get('id')

        if not producto_id:
            return jsonify({"success": False, "message": "ID de producto no proporcionado"}), 400

        cursor = conexion.cursor()
        cursor.execute("DELETE FROM producto WHERE id=?", (producto_id,))
        conexion.commit()
        cursor.close()

        return jsonify({"success": True, "message": "Producto eliminado exitosamente"})

    except Exception as e:
        return jsonify({"success": False, "message": f"Error al eliminar el producto: {str(e)}"}), 500

@product_bp.route('/Catalogo', methods=['GET'])
def catalogo():
    try:
        user = nose()
        conexion = get_connection()
        cursor = conexion.cursor()
        cursor.execute("SELECT id, nombre_producto, descripcion, cantidad_disponible, precio, Imagen FROM producto")
        productos = cursor.fetchall()  
        cursor.close()

        productos_formateados = []
        for producto in productos:
            productos_formateados.append({
                'id': producto[0],  
                'nombre_producto': producto[1],
                'descripcion': producto[2],
                'cantidad_disponible': producto[3],
                'precio': producto[4],
                'Imagen': producto[5]
            })

        return render_template('Catalogo.html', productos=productos_formateados)
    except Exception as e:
        return jsonify({"success": False, "message": f"Error al obtener los productos: {str(e)}"}), 500


@product_bp.route('/CatalogoC', methods=['GET'])
def catalogoC():
    try:
        user = nose()
        conexion = get_connection()
        cursor = conexion.cursor()
        cursor.execute("SELECT id, nombre_producto, descripcion, cantidad_disponible, precio, Imagen FROM producto")
        productos = cursor.fetchall()  
        cursor.close()

        productos_formateados = []
        for producto in productos:
            productos_formateados.append({
                'id': producto[0],  
                'nombre_producto': producto[1],
                'descripcion': producto[2],
                'cantidad_disponible': producto[3],
                'precio': producto[4],
                'Imagen': producto[5]
            })

        return render_template('CatalogoC.html', productos=productos_formateados)
    except Exception as e:
        return jsonify({"success": False, "message": f"Error al obtener los productos: {str(e)}"}), 500

@product_bp.route('/modificar_producto/<int:producto_id>', methods=['POST'])
def modificar_producto(producto_id):
    conexion = get_connection()
    cursor = conexion.cursor()

    nombre_producto = request.form['nombre_producto']
    descripcion = request.form['descripcion']
    cantidad_disponible = request.form['cantidad_disponible']
    precio = request.form['precio']
    imagen = request.files.get('imagen')
    
    imagen_path = None
    if imagen and allowed_file(imagen.filename):
        filename = secure_filename(imagen.filename)
        imagen_path = f'product_images/{filename}'
        imagen.save(os.path.join(Config.UPLOAD_FOLDER, filename))
    
    if imagen_path:
        cursor.execute(
            "UPDATE producto SET nombre_producto = ?, descripcion = ?, cantidad_disponible = ?, precio = ?, Imagen = ? WHERE id = ?",
            (nombre_producto, descripcion, cantidad_disponible, precio, imagen_path, producto_id)
        )
    else:
        cursor.execute(
            "UPDATE producto SET nombre_producto = ?, descripcion = ?, cantidad_disponible = ?, precio = ? WHERE id = ?",
            (nombre_producto, descripcion, cantidad_disponible, precio, producto_id)
        )
    
    conexion.commit()
    cursor.close()
    
    return jsonify({"success": True, "message": "Producto actualizado correctamente"})


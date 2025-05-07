from flask import Blueprint, render_template, session, redirect, request, jsonify
from Model.database import obtener_datos, actualizar_registro, eliminar_registro, insertar_registro
from Model.database import get_connection

main_routes = Blueprint('main_routes', __name__)

@main_routes.route('/')
def index():
    return render_template("index.html")

@main_routes.route('/<page>')
def render_page(page):
    try:
        return render_template(f'{page}.html') 
    except:
        return "Página no encontrada", 404  

@main_routes.route('/DbaTables/<page>')
def render_pageFile(page):
    try:
        return render_template(f'DbaTables/{page}.html')
    except:
        return "Página no encontrada", 404  

@main_routes.route('/nose')
def nose():
    if 'usuario' in session:
        usuario = session['usuario']
        role = session.get('role', 'cliente')
        return render_template('nose.html', usuario=usuario, role=role)
    else:
        return redirect('/login')

# Obtener datos de una tabla
@main_routes.route('/api/datos_tabla', methods=['GET'])
def obtener_tabla():
    tabla = request.args.get("tabla")

    if tabla not in ["empleado", "cliente", "cuenta", "producto", "venta","pedido","pedido_producto"]:
        return jsonify({"success": False, "message": "Tabla no válida"}), 400

    datos = obtener_datos(tabla)
    return jsonify({"success": True, "datos": datos})

# Modificar un registro en una tabla
@main_routes.route('/api/modificar', methods=['PUT'])
def modificar_dato():
    tabla = request.args.get("tabla")
    id = request.args.get("id")
    data = request.json

    if not tabla or not id or not data:
        return jsonify({"success": False, "message": "Datos insuficientes"}), 400

    columna = list(data.keys())[0]
    valor = list(data.values())[0]

    resultado = actualizar_registro(tabla, id, columna, valor)
    return jsonify(resultado)

# Eliminar un registro
@main_routes.route('/api/eliminar', methods=['DELETE'])
def eliminar_dato():
    tabla = request.args.get("tabla")
    id = request.args.get("id")

    if not tabla or not id:
        return jsonify({"success": False, "message": "Datos insuficientes"}), 400

    resultado = eliminar_registro(tabla, id)
    return jsonify(resultado)

@main_routes.route('/api/insertar', methods=['POST'])
def insertar_dato():
    tabla = request.args.get("tabla")
    datos = request.json

    if not tabla or not datos:
        return jsonify({"success": False, "message": "Datos insuficientes"}), 400

    resultado = insertar_registro(tabla, datos)
    if resultado["success"]:
        return jsonify({"success": True, "mensaje": "Registro agregado correctamente"})
    else:
        return jsonify({"success": False, "mensaje": "Error al agregar el registro"})
    
    

@main_routes.route('/get_pedidos', methods=['GET'])
def get_pedidos():
    usuario = session.get('usuario')
    if not usuario:
        return jsonify([]), 401

    nombre_usuario = usuario['nombre_usuario']
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM cliente WHERE nombre_cliente = ?",
        (nombre_usuario,)
    )
    row = cursor.fetchone()
    if not row:
        conn.close()
        return jsonify([]), 404
    cliente_id = row[0]

    cursor.execute("""
        SELECT id, fecha_estimada, estado_pedido, total
        FROM pedido
        WHERE id_cliente = ?
        ORDER BY fecha_compra DESC
    """, (cliente_id,))
    rows = cursor.fetchall()
    conn.close()

    pedidos = []
    for r in rows:
        fecha = r[1]
        # si es datetime, convertir a string YYYY-MM-DD
        fecha_str = fecha.date().isoformat() if hasattr(fecha, 'date') else str(fecha)
        pedidos.append({
            'numero_pedido':  r[0],
            'fecha_estimada': fecha_str,
            'estado_envio':   r[2],
            'total':          float(r[3])
        })

    return jsonify(pedidos)


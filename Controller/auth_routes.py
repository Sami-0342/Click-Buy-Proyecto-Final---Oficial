# auth_routes.py

import os
from flask import (
    Blueprint, request, session, render_template,
    jsonify, send_file, current_app
)
from Model.database import get_connection
from datetime import datetime, timedelta
from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/insertar', methods=["POST", "GET"])
def registro():
    try:
        if request.method == 'POST':
            nombre_usuario = request.form.get("nombrerg")
            contrasena     = request.form.get("contrasenarg")
            email          = request.form.get("emailrg")

            if not nombre_usuario or not contrasena or not email:
                return jsonify({"success": False, "message": "Todos los campos son obligatorios."}), 400

            conn   = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM cuenta WHERE nombre_usuario = ?",
                (nombre_usuario,)
            )
            if cursor.fetchone()[0] > 0:
                cursor.close()
                return jsonify({"success": False, "message": "El nombre de usuario ya está en uso."}), 400

            cursor.execute(
                "INSERT INTO cuenta (tipo_usuario, nombre_usuario, contrasena) VALUES (?, ?, ?)",
                ('cliente', nombre_usuario, contrasena)
            )
            conn.commit()
            cursor.close()
            return jsonify({
                "success": True,
                "message": "Registro exitoso.",
                "redirect_url": "/indexCliente"
            }), 200

        return render_template("indexCliente.html")

    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500


@auth_bp.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        conn           = get_connection()
        nombre_usuario = request.form.get("nombrelg")
        contrasena     = request.form.get("contrasenalg")
        if not nombre_usuario or not contrasena:
            return jsonify({"success": False, "message": "Por favor, completa todos los campos."}), 400

        cursor = conn.cursor()
        cursor.execute(
            "SELECT tipo_usuario FROM cuenta WHERE nombre_usuario = ? AND contrasena = ?",
            (nombre_usuario, contrasena)
        )
        row = cursor.fetchone()
        cursor.close()

        if not row:
            return jsonify({"success": False, "message": "Usuario o contraseña incorrectos."}), 401

        tipo_usuario = row[0]
        session['usuario'] = {
            'nombre_usuario': nombre_usuario,
            'tipo_usuario': tipo_usuario
        }

        dest = {
            'empleado': '/indexEmpleado',
            'cliente':  '/indexCliente',
            'Admin':    '/indexAdmin'
        }.get(tipo_usuario, '/')
        return jsonify({
            "success": True,
            "message": "Inicio de sesión exitoso.",
            "redirect_url": dest
        })

    return render_template("login.html")


@auth_bp.route('/checkout', methods=['POST'])
def checkout():
    usuario = session.get('usuario')
    if not usuario:
        return jsonify({"success": False, "message": "No autenticado"}), 401

    nombre_usuario  = usuario['nombre_usuario']
    data            = request.get_json()
    empresa_envio   = data.get('empresa_envio')
    direccion_envio = data.get('direccion_envio')
    metodo_pago     = data.get('metodo_pago')
    cart_items      = data.get('cart')

    if not cart_items or not direccion_envio or not metodo_pago:
        return jsonify({"success": False, "message": "Faltan datos."}), 400

    dias_base = {
        'FedEx': 5, 'UPS': 10, 'DHL': 3,
        'Nacional Express': 15, 'Otra': 20
    }
    dias_estimados = max(dias_base.get(empresa_envio, 10), 30)

    conn   = get_connection()
    cursor = conn.cursor()
    try:
        # 1. Cliente
        cursor.execute(
            "SELECT id FROM cliente WHERE nombre_cliente = ?",
            (nombre_usuario,)
        )
        row = cursor.fetchone()
        if not row:
            return jsonify({"success": False, "message": "Cliente no encontrado."}), 404
        cliente_id = row[0]

        # 2. Total
        total = sum(item['qty'] * item['price'] for item in cart_items)

        # 3. Insertar pedido
        fecha_compra   = datetime.now()
        fecha_estimada = fecha_compra + timedelta(days=dias_estimados)
        cursor.execute("""
            INSERT INTO pedido
            (id_cliente, fecha_compra, total, estado_pedido,
             empresa_envio, direccion_envio, fecha_estimada)
            OUTPUT INSERTED.id
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            cliente_id, fecha_compra, total, 'Pendiente',
            empresa_envio, direccion_envio, fecha_estimada
        ))
        id_pedido = cursor.fetchone()[0]

        # 4. Detalles
        for item in cart_items:
            cursor.execute("""
                INSERT INTO pedido_producto
                (id_pedido, producto_id, cantidad, precio_unitario)
                VALUES (?, ?, ?, ?)
            """, (id_pedido, item['id'], item['qty'], item['price']))

        # 5. Venta (si aplica)
        for item in cart_items:
            cursor.execute("""
                INSERT INTO venta
                (empleado_id, cliente_id, producto_id,
                 metodo_pago_id, fecha_venta, total_venta)
                VALUES (?, ?, ?, ?, GETDATE(), ?)
            """, (None, cliente_id, item['id'], metodo_pago, item['qty'] * item['price']))

        conn.commit()

    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        conn.close()

    return jsonify({
        "success": True,
        "message": "Compra realizada.",
        "id": id_pedido,
        "redirect_url": "/carrito"
    })


@auth_bp.route('/checkout/pdf/<int:pedido_id>')
def descargar_factura(pedido_id):
    # 1. Cargar datos
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT fecha_compra, total, empresa_envio, direccion_envio, fecha_estimada
        FROM pedido WHERE id = ?
    """, (pedido_id,))
    pedido = cursor.fetchone()
    if not pedido:
        cursor.close()
        return jsonify({"message": "Pedido no encontrado"}), 404
    fecha_compra, total, empresa_envio, direccion_envio, fecha_estimada = pedido

    cursor.execute("""
        SELECT pp.cantidad, pp.precio_unitario, p.nombre_producto
        FROM pedido_producto pp
        JOIN producto p ON pp.producto_id = p.id
        WHERE pp.id_pedido = ?
    """, (pedido_id,))
    items = cursor.fetchall()
    cursor.close()
    conn.close()

    # 2. Generar PDF
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    ancho, alto = letter

    # 2.1 Encabezado coral + logo
    header_h = 80
    p.setFillColor(colors.HexColor('#FF7F50'))
    p.rect(0, alto-header_h, ancho, header_h, fill=1, stroke=0)

    logo_path = os.path.join(current_app.static_folder, 'img', 'asdas.png')
    if os.path.exists(logo_path):
        p.drawImage(logo_path, 40, alto-60, width=60, height=40, mask='auto')

    p.setFont("Helvetica-Bold", 20)
    p.setFillColor(colors.white)
    p.drawString(120, alto-50, "FACTURA DE PEDIDO")

    # 2.2 Datos del pedido
    p.setFont("Helvetica", 10)
    p.setFillColor(colors.black)
    y = alto - header_h - 20
    p.drawString(40, y, f"Número: {pedido_id}")
    p.drawString(300, y, f"Fecha: {fecha_compra.strftime('%Y-%m-%d')}")
    y -= 15
    p.drawString(40, y, f"Cliente: {session['usuario']['nombre_usuario']}")
    p.drawString(300, y, f"Entrega estimada: {fecha_estimada.strftime('%Y-%m-%d')}")
    y -= 30

    # 2.3 Tabla con Platypus
    data = [["Cant.", "Producto", "P.Unitario", "Subtotal"]]
    for qty, precio, nombre in items:
        data.append([qty, nombre, f"${precio:.2f}", f"${qty*precio:.2f}"])
    data.append(["", "", "TOTAL", f"${total:.2f}"])

    table = Table(data, colWidths=[40, 260, 80, 80])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor('#FF7F50')),
        ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
        ("ALIGN",      (2,1), (-1,-1), "RIGHT"),
        ("GRID",       (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,1), (-1,-2), colors.whitesmoke),
        ("BACKGROUND", (0,-1), (-1,-1), colors.lightgrey),
        ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTNAME",   (0,-1), (-1,-1), "Helvetica-Bold"),
    ]))
    w, h = table.wrapOn(p, ancho-80, alto)
    table.drawOn(p, 40, y-h)

    # 2.4 Pie de página
    p.setFont("Helvetica-Oblique", 8)
    p.setFillColor(colors.grey)
    p.drawString(40, 30, "Gracias por su compra. Para dudas: info@Click&Buy.com")

    p.showPage()
    p.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"factura_{pedido_id}.pdf",
        mimetype="application/pdf"
    )


@auth_bp.route('/api/detalle_pedido/<int:pedido_id>')
def detalle_pedido(pedido_id):
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            p.id          AS id_pedido,
            p.id_cliente,
            p.fecha_compra,
            p.total,
            p.empresa_envio,
            p.direccion_envio,
            pp.producto_id,
            pr.nombre_producto,
            pp.cantidad,
            pp.precio_unitario,
            pr.Imagen
        FROM pedido AS p
        JOIN pedido_producto AS pp ON p.id = pp.id_pedido
        JOIN producto      AS pr ON pr.id = pp.producto_id
        WHERE p.id = ?
    """, (pedido_id,))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    if not rows:
        return jsonify({"error": "Pedido no encontrado"}), 404

    # Cabecera (datos de la 1ª fila)
    first = rows[0]
    pedido = {
        "id_pedido":      first.id_pedido,
        "id_cliente":     first.id_cliente,
        "fecha_compra":   first.fecha_compra.isoformat(),
        "empresa_envio":  first.empresa_envio,
        "direccion_envio":first.direccion_envio,
        "total":          float(first.total)
    }

    # Líneas
    lineas = []
    for r in rows:
        lineas.append({
            "producto_id":     r.producto_id,
            "nombre":          r.nombre_producto,
            "cantidad":        r.cantidad,
            "precio_unitario": float(r.precio_unitario),
            "url_imagen":      r.Imagen  # asegúrate de que sea la ruta relativa correcta
        })

    return jsonify(pedido=pedido, lineas=lineas)

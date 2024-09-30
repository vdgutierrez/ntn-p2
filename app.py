from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)

# Lista temporal de productos (esto debería provenir de la base de datos)
productos = [
    {'id': 1, 'nombre': 'TV 4K', 'categoria': 'electronicos', 'precio_inicial': 300.00, 'foto_url': '/static/img/tv.jpg'},
    {'id': 2, 'nombre': 'Coche', 'categoria': 'vehiculos', 'precio_inicial': 15000.00, 'foto_url': '/static/img/coche.jpg'},
    {'id': 3, 'nombre': 'Sofá', 'categoria': 'muebles', 'precio_inicial': 200.00, 'foto_url': '/static/img/sofa.jpg'}
]

subastas = [
    {'id': 1, 'nombre_producto': 'TV 4K', 'precio_actual': 350.00, 'imagen': '/static/img/tv.jpg'},
    {'id': 2, 'nombre_producto': 'Coche', 'precio_actual': 15500.00, 'imagen': '/static/img/coche.jpg'},
    {'id': 3, 'nombre_producto': 'Sofá', 'precio_actual': 220.00, 'imagen': '/static/img/sofa.jpg'}
]

# Rutas del cliente
@app.route('/cliente/explorar-subastas')
def explorar_subastas():
    # Lista temporal de subastas, que idealmente provendría de la base de datos
    subastas = [
        {'id': 1, 'nombre_producto': 'TV 4K', 'categoria': 'electronicos', 'precio_inicial': 300.00, 'precio_actual': 350.00, 'imagen': '/static/img/tv.jpg'},
        {'id': 2, 'nombre_producto': 'Coche', 'categoria': 'vehiculos', 'precio_inicial': 15000.00, 'precio_actual': 15500.00, 'imagen': '/static/img/coche.jpg'},
        {'id': 3, 'nombre_producto': 'Sofá', 'categoria': 'muebles', 'precio_inicial': 200.00, 'precio_actual': 220.00, 'imagen': '/static/img/sofa.jpg'}
    ]
    return render_template('cliente/explorar_subastas.html', subastas=subastas)

@app.route('/cliente/detalle-subasta/<int:subasta_id>', methods=['GET', 'POST'])
def detalle_subasta(subasta_id):
    # Buscar la subasta en base al id proporcionado
    subasta = next((s for s in subastas if s['id'] == subasta_id), None)

    if subasta is None:
        return "Subasta no encontrada", 404

    # Historial de pujas (esto debería venir de una base de datos en un caso real)
    historial_pujas = [
        {'pujador': 'Carlos', 'monto': 320.00},
        {'pujador': 'Ana', 'monto': 340.00},
        {'pujador': 'Luis', 'monto': 350.00}
    ]

    # Si el cliente hace una nueva puja (POST request)
    if request.method == 'POST':
        nueva_puja = float(request.form['monto'])
        if nueva_puja > subasta['precio_actual']:
            subasta['precio_actual'] = nueva_puja
            # Aquí se debería guardar la puja en el historial en una base de datos real
            historial_pujas.append({'pujador': 'Juanjo Valda', 'monto': nueva_puja})
        else:
            return "La puja debe ser mayor al precio actual", 400

    return render_template('cliente/detalle_subasta.html', subasta=subasta, historial_pujas=historial_pujas)


@app.route('/cliente/historial-subastas')
def historial_subastas_cliente():
    # Historial de subastas en las que el cliente ha participado
    historial = [
        {'id': 1, 'nombre_producto': 'TV 4K', 'precio_final': 350.00, 'estado': 'Ganada'},
        {'id': 2, 'nombre_producto': 'Coche', 'precio_final': 15500.00, 'estado': 'Perdida'}
    ]
    return render_template('cliente/historial_subasta_cliente.html', historial=historial)

@app.route('/cliente/perfil')
def perfil_cliente():
    # Perfil del cliente
    cliente = {'nombre': 'Juan Pérez', 'correo': 'juan@example.com', 'saldo': 500.00}
    return render_template('cliente/perfil_cliente.html', cliente=cliente)

# Ruta para gestionar productos (con filtro)
@app.route('/subastador/gestion-productos', methods=['GET'])
def gestion_productos():
    # Obtén el valor de 'categoriaFiltro' desde la URL; si no existe, usa 'todos' por defecto
    categoria_filtro = request.args.get('categoriaFiltro', 'todos')

    # Si la categoría es 'todos', no se aplica ningún filtro
    if categoria_filtro == 'todos':
        productos_filtrados = productos
    else:
        # Filtrar los productos por la categoría seleccionada
        productos_filtrados = [producto for producto in productos if producto['categoria'] == categoria_filtro]

    # Renderiza la página con los productos filtrados
    return render_template('subastador/gestion_productos.html', productos=productos_filtrados)


# Ruta para editar un producto
@app.route('/subastador/editar-producto/<int:id>', methods=['GET', 'POST'])
def editar_producto(id):
    producto = next((p for p in productos if p['id'] == id), None)
    if request.method == 'POST':
        # Aquí actualizarías los datos del producto con los valores del formulario
        producto['nombre'] = request.form['nombre']
        producto['precio_inicial'] = request.form['precio_inicial']
        producto['categoria'] = request.form['categoria']
        return redirect(url_for('gestion_productos'))
    
    return render_template('subastador/editar_producto.html', producto=producto)

# Ruta para eliminar un producto
@app.route('/subastador/eliminar-producto/<int:id>')
def eliminar_producto(id):
    global productos
    productos = [producto for producto in productos if producto['id'] != id]
    return redirect(url_for('gestion_productos'))

# Ruta para la página principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para el dashboard del cliente
@app.route('/cliente/dashboard')
def cliente_dashboard():
    return render_template('cliente/index_cliente.html')

# Ruta para el dashboard del subastador
@app.route('/subastador/dashboard')
def subastador_dashboard():
    return render_template('subastador/index_sub.html')

# Ruta para gestión de subastas
@app.route('/subastador/gestion-subastas')
def gestion_subastas():
    return render_template('subastador/gestionsub.html')

# Ruta para ver una subasta activa
@app.route('/subastador/subasta-activa')
def subasta_activa():
    return render_template('subastador/subasta_activa.html')

# Ruta para el historial de subastas
@app.route('/subastador/historial-subastas')
def historial_subastas():
    return render_template('subastador/historial.html')

# Ruta para estadísticas y reportes
@app.route('/subastador/estadisticas-reportes')
def estadisticas_reportes():
    return render_template('subastador/estadisticas_reportes.html')

# Ruta para notificaciones
@app.route('/subastador/notificaciones')
def notificaciones():
    return render_template('subastador/notificaciones.html')

# Ruta para la página de inicio de sesión
@app.route('/login')
def login():
    return render_template('login.html')

# Ruta para la página de registro
@app.route('/register')
def register():
    return render_template('register.html')

# Iniciar el servidor Flask
if __name__ == '__main__':
    app.run(debug=True)

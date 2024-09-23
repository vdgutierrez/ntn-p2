from flask import Flask,request, render_template, redirect, url_for

app = Flask(__name__)
# Lista temporal de productos (esto debería provenir de la base de datos)
productos = [
    {'id': 1, 'nombre': 'TV 4K', 'categoria': 'electronicos', 'precio_inicial': 300.00, 'foto_url': '/static/img/tv.jpg'},
    {'id': 2, 'nombre': 'Coche', 'categoria': 'vehiculos', 'precio_inicial': 15000.00, 'foto_url': '/static/img/coche.jpg'},
    {'id': 3, 'nombre': 'Sofá', 'categoria': 'muebles', 'precio_inicial': 200.00, 'foto_url': '/static/img/sofa.jpg'}
]

@app.route('/subastador/gestion-productos', methods=['GET', 'POST'])
def gestion_productos():
    categoria_filtro = request.args.get('categoriaFiltro', 'todos')
    productos_filtrados = productos

    if categoria_filtro != 'todos':
        productos_filtrados = [producto for producto in productos if producto['categoria'] == categoria_filtro]

    return render_template('subastador/gestion_productos.html', productos=productos_filtrados)

@app.route('/subastador/filtrar-productos', methods=['GET'])
def filtrar_productos():
    categoria_filtro = request.args.get('categoriaFiltro', 'todos')
    productos_filtrados = productos

    if categoria_filtro != 'todos':
        productos_filtrados = [producto for producto in productos if producto['categoria'] == categoria_filtro]

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

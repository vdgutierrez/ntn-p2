from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from db import *

app = Flask(__name__)
app.secret_key = 'Arqui123'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Modelo de usuario
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    conexion = db_connection()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM persona  WHERE id_persona = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    conexion.close()
    if user_data:
        return User(user_data['id_persona'], user_data['nombre'])
    return None


# Lista temporal de productos (esto debería provenir de la base de datos)
productos = [
    {'id': 1, 'nombre': 'TV 4K', 'categoria': 'electronicos',
        'precio_inicial': 300.00, 'foto_url': '/static/img/tv.jpg'},
    {'id': 2, 'nombre': 'Coche', 'categoria': 'vehiculos',
        'precio_inicial': 15000.00, 'foto_url': '/static/img/coche.jpg'},
    {'id': 3, 'nombre': 'Sofá', 'categoria': 'muebles',
        'precio_inicial': 200.00, 'foto_url': '/static/img/sofa.jpg'}
]

subastas = [
    {'id': 1, 'nombre_producto': 'TV 4K',
        'precio_actual': 350.00, 'imagen': '/static/img/tv.jpg'},
    {'id': 2, 'nombre_producto': 'Coche', 'precio_actual': 15500.00,
        'imagen': '/static/img/coche.jpg'},
    {'id': 3, 'nombre_producto': 'Sofá', 'precio_actual': 220.00,
        'imagen': '/static/img/sofa.jpg'}
]

# Ruta para explorar subastas


@app.route('/cliente/explorar_subastas')
def explorar_subastas():
    conexion = db_connection()
    cursor = conexion.cursor(dictionary=True)

    # Consulta para obtener subastas
    cursor.execute('''SELECT s.id_subasta, s.hora_inicio, s.hora_final, m.tipo_moneda, p.nombre, p.apellido 
                      FROM subasta s, tipo_moneda m, organizador o, persona p
                      WHERE s.organizador_id = o.id_organizador
                      AND s.tipo_moneda_id = m.id_tipo_moneda
                      AND o.persona_id = p.id_persona''')

    subastas = cursor.fetchall()
    print(subastas)

    conexion.close()
    return render_template('cliente/explorar_subastas.html', subastas=subastas)

# Ruta para ver el detalle de una subasta



@app.route('/cliente/detalle-subasta/<int:subasta_id>', methods=['GET', 'POST'])
def detalle_subasta(subasta_id):
    conexion = db_connection()
    cursor = conexion.cursor(dictionary=True)

    # Obtener detalles de la subasta
    cursor.execute('''SELECT s.id_subasta, s.hora_inicio, s.hora_final, m.tipo_moneda, p.nombre, p.apellido 
                      FROM subasta s
                      JOIN tipo_moneda m ON s.tipo_moneda_id = m.id_tipo_moneda
                      JOIN organizador o ON s.organizador_id = o.id_organizador
                      JOIN persona p ON o.persona_id = p.id_persona 
                      WHERE s.id_subasta = %s''', (subasta_id,))
    subasta = cursor.fetchone()
    cursor.fetchall()  # Asegúrate de que todos los resultados se hayan leído

    if not subasta:
        cursor.close()
        conexion.close()
        return "Subasta no encontrada", 404
    
    # Obtener la última puja
    cursor.execute(
        '''SELECT p.id_puja, p.subasta_producto_id, p.cliente_id, p.precio_puja, p.hora 
           FROM puja p
           JOIN subasta_producto sp ON p.subasta_producto_id = sp.id_subasta_producto
           JOIN subasta s ON sp.subasta_id = s.id_subasta
           WHERE s.id_subasta = %s 
           ORDER BY p.precio_puja DESC LIMIT 1''', (subasta_id,))
    ultima_puja = cursor.fetchone()
    cursor.fetchall()  # Asegúrate de que todos los resultados se hayan leído

    # Obtener el precio inicial
    cursor.execute(
        '''SELECT sp.precio_inicial 
           FROM subasta_producto sp
           JOIN subasta s ON sp.subasta_id = s.id_subasta
           WHERE s.id_subasta = %s 
           LIMIT 1''', (subasta_id,))
    precio_inicial = cursor.fetchone()
    cursor.fetchall()  # Asegúrate de que todos los resultados se hayan leído

    # Obtener el historial de pujas de la subasta
    cursor.execute(
        '''SELECT p.id_puja, p.subasta_producto_id, p.cliente_id, p.precio_puja, p.hora 
           FROM puja p
           JOIN subasta_producto sp ON p.subasta_producto_id = sp.id_subasta_producto
           JOIN subasta s ON sp.subasta_id = s.id_subasta
           WHERE s.id_subasta = %s 
           ORDER BY p.precio_puja DESC''', (subasta_id,))
    historial_pujas = cursor.fetchall()
    cursor.fetchall()  # Asegúrate de que todos los resultados se hayan leído

    # Obtener categoría y nombre del producto
    cursor.execute(
        '''SELECT c.nombre_categoria, p.nombre, p.descripcion
           FROM subasta_producto sp
           JOIN subasta s ON sp.subasta_id = s.id_subasta
           JOIN producto p ON sp.producto_id = p.id_producto
           JOIN categoria c ON p.categoria_id = c.id_categoria
           WHERE s.id_subasta = %s 
           LIMIT 1''', (subasta_id,))
    categoria = cursor.fetchone()
    cursor.fetchall()  # Asegúrate de que todos los resultados se hayan leído

    if request.method == 'POST':
        nueva_puja = float(request.form['monto'])
        # Verificar si la nueva puja es mayor que el precio actual de la subasta
        if nueva_puja > (ultima_puja['precio_puja'] if ultima_puja else precio_inicial['precio_inicial']):
            # Obtener el `id_subasta_producto` correspondiente para esta subasta
            cursor.execute(
                '''SELECT sp.id_subasta_producto 
                   FROM subasta_producto sp 
                   WHERE sp.subasta_id = %s''', (subasta_id,))
            subasta_producto = cursor.fetchone()
            cursor.fetchall()  # Asegúrate de que todos los resultados se hayan leído

            if not subasta_producto:
                cursor.close()
                conexion.close()
                return "Producto de la subasta no encontrado", 404

            subasta_producto_id = subasta_producto['id_subasta_producto']

            # Obtener el ID del cliente autenticado directamente desde current_user
            cliente_id = current_user.id  # Usa el atributo correcto del modelo de usuario

            # Insertar la nueva puja en la tabla `puja`
            cursor.execute(
                "INSERT INTO puja (subasta_producto_id, cliente_id, precio_puja, hora) VALUES (%s, %s, %s, NOW())",
                (subasta_producto_id, cliente_id, nueva_puja))
            conexion.commit()

            # Actualizar los datos después de la puja
            cursor.execute(
                '''SELECT p.id_puja, p.subasta_producto_id, p.cliente_id, p.precio_puja, p.hora 
                   FROM puja p
                   JOIN subasta_producto sp ON p.subasta_producto_id = sp.id_subasta_producto
                   JOIN subasta s ON sp.subasta_id = s.id_subasta
                   WHERE s.id_subasta = %s 
                   ORDER BY p.precio_puja DESC LIMIT 1''', (subasta_id,))
            ultima_puja = cursor.fetchone()
            cursor.fetchall()  # Asegúrate de que todos los resultados se hayan leído

            cursor.execute(
                '''SELECT p.id_puja, p.subasta_producto_id, p.cliente_id, p.precio_puja, p.hora 
                   FROM puja p
                   JOIN subasta_producto sp ON p.subasta_producto_id = sp.id_subasta_producto
                   JOIN subasta s ON sp.subasta_id = s.id_subasta
                   WHERE s.id_subasta = %s 
                   ORDER BY p.precio_puja DESC''', (subasta_id,))
            historial_pujas = cursor.fetchall()
            cursor.fetchall()  # Asegúrate de que todos los resultados se hayan leído

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                cursor.close()
                conexion.close()
                return render_template('cliente/detalle_subasta.html', subasta=subasta, historial_pujas=historial_pujas, precio_inicial=precio_inicial, categoria=categoria, puja=ultima_puja)

        else:
            cursor.close()
            conexion.close()
            return "La puja debe ser mayor al precio actual", 400

    cursor.close()
    conexion.close()
    return render_template('cliente/detalle_subasta.html', subasta=subasta, historial_pujas=historial_pujas, precio_inicial=precio_inicial, categoria=categoria, puja=ultima_puja)


#TODO Ruta para el historial de subastas del cliente
@app.route('/cliente/historial-subastas')
def historial_subastas_cliente():
    # conexion = db_connection()
    # cursor = conexion.cursor(dictionary=True)

    # # Consulta para obtener el historial de subastas del cliente
    # # Suponiendo cliente con ID 1
    # cursor.execute("SELECT * FROM subastas WHERE comprador_id = 1")
    # historial = cursor.fetchall()

    # conexion.close()
    #return render_template('cliente/historial_subasta_cliente.html', historial=historial)
    return render_template('cliente/historial_subasta_cliente.html')

#TODO Perfil cliente
@app.route('/cliente/perfil')
def perfil_cliente():
    # conexion = db_connection()
    # cursor = conexion.cursor(dictionary=True)

    # # Consulta para obtener datos del cliente
    # # Suponiendo cliente con ID 1
    # cursor.execute("SELECT * FROM clientes WHERE id = 1")
    # cliente = cursor.fetchone()

    # conexion.close()
    #return render_template('cliente/perfil_cliente.html', cliente=cliente)
    return render_template('cliente/perfil_cliente.html')

# Ruta para gestionar productos del subastador


@app.route('/subastador/gestion-productos', methods=['GET'])
def gestion_productos():
    conexion = db_connection()
    cursor = conexion.cursor(dictionary=True)

    categoria_filtro = request.args.get('categoriaFiltro', 'todos')

    if categoria_filtro == 'todos':
        cursor.execute("SELECT * FROM productos")
    else:
        cursor.execute(
            "SELECT * FROM productos WHERE categoria = %s", (categoria_filtro,))

    productos = cursor.fetchall()
    conexion.close()
    return render_template('subastador/gestion_productos.html', productos=productos)

# Ruta para editar un producto


@app.route('/subastador/editar-producto/<int:id>', methods=['GET', 'POST'])
def editar_producto(id):
    conexion = db_connection()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT * FROM productos WHERE id = %s", (id,))
    producto = cursor.fetchone()

    if request.method == 'POST':
        nombre = request.form['nombre']
        precio_inicial = request.form['precio_inicial']
        categoria = request.form['categoria']

        cursor.execute("UPDATE productos SET nombre = %s, precio_inicial = %s, categoria = %s WHERE id = %s",
                       (nombre, precio_inicial, categoria, id))
        conexion.commit()
        conexion.close()
        return redirect(url_for('gestion_productos'))

    conexion.close()
    return render_template('subastador/editar_producto.html', producto=producto)

# Ruta para eliminar un producto


@app.route('/subastador/eliminar-producto/<int:id>')
def eliminar_producto(id):
    conexion = db_connection()
    cursor = conexion.cursor()

    cursor.execute("DELETE FROM productos WHERE id = %s", (id,))
    conexion.commit()
    conexion.close()
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

# Ruta para gestionar subastas


@app.route('/subastador/gestion-subastas')
def gestion_subastas():
    conexion = db_connection()
    cursor = conexion.cursor(dictionary=True)

    # Obtener todas las subastas del subastador
    # Suponiendo subastador con ID 1
    cursor.execute("SELECT * FROM subastas WHERE subastador_id = 1")
    subastas = cursor.fetchall()
    conexion.close()
    return render_template('subastador/gestionsub.html', subastas=subastas)

# Ruta para ver subastas activas


@app.route('/subastador/subasta-activa')
def subasta_activa():
    conexion = db_connection()
    cursor = conexion.cursor(dictionary=True)

    # Obtener subastas activas
    cursor.execute("SELECT * FROM subastas WHERE estado = 'activa'")
    subastas = cursor.fetchall()
    conexion.close()
    return render_template('subastador/subasta_activa.html', subastas=subastas)

# Ruta para el historial de subastas


@app.route('/subastador/historial-subastas')
def historial_subastas():
    conexion = db_connection()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT * FROM subastas WHERE estado = 'finalizada'")
    historial = cursor.fetchall()
    conexion.close()
    return render_template('subastador/historial.html', historial=historial)


# Ruta para estadísticas y reportes
@app.route('/subastador/estadisticas-reportes')
def estadisticas_reportes():
    # Aquí irían consultas que proporcionen estadísticas e informes, como número de subastas, ganancia total, etc.
    return render_template('subastador/estadisticas_reportes.html')

# Ruta para notificaciones


@app.route('/subastador/notificaciones')
def notificaciones():
    conexion = db_connection()
    cursor = conexion.cursor(dictionary=True)

    # Suponiendo subastador con ID 1
    cursor.execute("SELECT * FROM notificaciones WHERE subastador_id = 1")
    notificaciones = cursor.fetchall()
    conexion.close()
    return render_template('subastador/notificaciones.html', notificaciones=notificaciones)


# Ruta de inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conexion = db_connection()
        cursor = conexion.cursor(dictionary=True)

        # Verificar si el usuario es un organizador
        cursor.execute('''
            SELECT o.id_organizador AS id, o.usuario AS username, o.contrasena AS password, 'organizador' AS role
            FROM organizador o
            INNER JOIN persona p ON o.persona_id = p.id_persona
            WHERE p.correo = %s AND o.contrasena = %s
        ''', (email, password))
        user_data = cursor.fetchone()

        # Si no es organizador, verificar si es cliente
        if not user_data:
            cursor.execute('''
                SELECT c.id_cliente AS id, p.nombre AS username, c.contrasena AS password, 'cliente' AS role
                FROM cliente c
                INNER JOIN persona p ON c.persona_id = p.id_persona
                WHERE p.correo = %s AND c.contrasena = %s
            ''', (email, password))
            user_data = cursor.fetchone()

        conexion.close()

        if user_data:
            user = User(user_data['id'], user_data['username'])
            login_user(user)
            if user_data['role'] == 'organizador':
                return redirect(url_for('crear_subasta'))
            elif user_data['role'] == 'cliente':
                return redirect(url_for('cliente_dashboard'))
        else:
            flash('Usuario o contraseña incorrectos. Por favor, inténtalo de nuevo.', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')

# Ruta de cierre de sesión
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# Ruta para la página de registro


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('nombre')
        lastname = request.form.get('apellido')
        email = request.form.get('correo')
        password = request.form.get('password')
        tipo = request.form.get('rol')
        phone = request.form.get('telefono')

        print(f"Nombre: {name}")
        print(f"Apellido: {lastname}")
        print(f"Correo: {email}")
        print(f"Contraseña: {password}")
        print(f"Tipo: {tipo}")
        print(f"Telefono: {phone}")

        # Verifica que todos los campos se han llenado
        if not all([name, lastname, email, password, tipo, phone]):
            return "Todos los campos son obligatorios", 400

        # Inserta datos en la base de datos
        insert_perfil(name, lastname, email, password, tipo, phone)

        return redirect(url_for('explorar_subastas'))

    return render_template('register.html')

def insert_perfil(name, lastname, email, password, tipo, phone):
    conexion = db_connection()
    if conexion is None:
        print("Error: No se pudo establecer la conexión con la base de datos.")
        return
    try:
        cursor = conexion.cursor()

        # Inserción en la tabla persona
        cursor.execute(
            "INSERT INTO persona (nombre, apellido, correo, telefono) VALUES (%s, %s, %s, %s)",
            (name, lastname, email, phone)
        )
        conexion.commit()

        id_persona = cursor.lastrowid  # Obtiene el ID de la persona insertada
        print(f"Persona insertada con ID: {id_persona}")

        # Inserción en la tabla cliente u organizador según el tipo de usuario
        if tipo == 'Cliente':
            cursor.execute(
                "INSERT INTO cliente (contrasena, persona_id) VALUES (%s, %s)",
                (password, id_persona)
            )
            print("Cliente insertado correctamente.")
        elif tipo == 'Subastador':
            cursor.execute(
                "INSERT INTO organizador (usuario, contrasena, persona_id) VALUES (%s, %s, %s)",
                (f'{name} {lastname}', password, id_persona)
            )
            print("Subastador insertado correctamente.")
        else:
            print("Tipo de usuario no válido.")
            return "Tipo de usuario no válido", 400

        conexion.commit()

    except Error as e:
        print(f"Error al insertar en persona/cliente/organizador: {e}")
    finally:
        cursor.close()
        conexion.close()


def insert_cliente(name, lastname, id_perfil):
    conexion = db_connection()
    if conexion is None:
        return
    try:
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO Cliente (NOMBRES, APELLIDOS,ID_PERFIL) VALUES (%s, %s, %s)",
            (name, lastname, id_perfil)
        )
        conexion.commit()
    except Error as e:
        print(f"Error al insertar en Cliente: {e}")
    finally:
        cursor.close()
        conexion.close()


def insert_subastador(name, lastname, id_perfil):
    conexion = db_connection()
    if conexion is None:
        return
    try:
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO subastador (NOMBRES, APELLIDOS, ID_PERFIL) VALUES (%s, %s, %s)",
            (name, lastname, id_perfil)
        )

        conexion.commit()
    except Error as e:
        print(f"Error al insertar en Subastador: {e}")
    finally:
        cursor.close()
        conexion.close()
@app.route('/subastador/agregar-producto', methods=['GET', 'POST'])
def agregar_producto():
    if request.method == 'POST':
        nombre = request.form.get('nombre')

        if not nombre:
            message = "Faltan datos obligatorios"
            message_type = "error"
            return render_template('subastador/agregar_producto.html', message=message, message_type=message_type)
        
        message = "Producto agregado correctamente"
        message_type = "success"
        return render_template('subastador/agregar_producto.html', message=message, message_type=message_type)

    return render_template('subastador/agregar_producto.html')


# Ruta protegida para crear subasta
@app.route('/subastador/crear-subasta', methods=['GET', 'POST'])
def crear_subasta():
    conexion = db_connection()
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id_categoria, nombre_categoria FROM categoria")
        categorias = cursor.fetchall()
        
        cursor.execute("SELECT id_tipo_moneda, tipo_moneda FROM tipo_moneda")
        tipos_moneda = cursor.fetchall()
        
        cursor.close()
        conexion.close()
    else:
        categorias = []
        tipos_moneda = []

    if request.method == 'POST':
        hora_inicio = request.form['horaInicio']
        hora_final = request.form['horaFinal']
        tipo_moneda_id = request.form['tipoMoneda']

        nombre_productos = request.form.getlist('nombreProducto[]')
        descripcion_productos = request.form.getlist('descripcionProducto[]')
        categoria_productos = request.form.getlist('categoriaProducto[]')
        precio_iniciales = request.form.getlist('precioInicial[]')

        conexion = db_connection()
        if conexion:
            cursor = conexion.cursor()
            try:
                # Insertar la subasta
                cursor.execute(
                    "INSERT INTO subasta (hora_inicio, hora_final, organizador_id, tipo_moneda_id) VALUES (%s, %s, %s, %s)",
                    (hora_inicio, hora_final, current_user.id, tipo_moneda_id)
                )
                subasta_id = cursor.lastrowid

                # Insertar los productos y asociarlos a la subasta
                for nombre_producto, descripcion_producto, categoria_producto, precio_inicial in zip(nombre_productos, descripcion_productos, categoria_productos, precio_iniciales):
                    cursor.execute(
                        "INSERT INTO producto (nombre, descripcion, categoria_id) VALUES (%s, %s, %s)",
                        (nombre_producto, descripcion_producto, categoria_producto)
                    )
                    producto_id = cursor.lastrowid

                    cursor.execute(
                        "INSERT INTO subasta_producto (subasta_id, producto_id, precio_inicial) VALUES (%s, %s, %s)",
                        (subasta_id, producto_id, precio_inicial)
                    )

                conexion.commit()
                flash('Subasta creada exitosamente', 'success')
            except mysql.connector.Error as err:
                print(f"Error: {err}")
                flash('Error al crear la subasta', 'danger')
            finally:
                cursor.close()
                conexion.close()
        else:
            flash('Error al conectar a la base de datos', 'danger')

        return redirect(url_for('crear_subasta'))

    return render_template('subastador/crear_subasta.html', categorias=categorias, tipos_moneda=tipos_moneda)

# Otras rutas...

if __name__ == '__main__':
    app.run(debug=True)
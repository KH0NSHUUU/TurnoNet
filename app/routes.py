from flask import render_template, request, redirect, session, url_for, flash, jsonify
from app import app, mysql
from datetime import datetime, timedelta
import locale

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        dni = request.form['dni']
        contraseña = request.form['contraseña']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE dni = %s AND contraseña = %s", (dni, contraseña))
        user = cur.fetchone()
        
        if user:
            session['dni'] = user[0]
            session['nombre'] = user[1]
            session['apellido'] = user[2]
            session['contacto'] = user[3]
            session['correo'] = user[4]
            session['contraseña'] = user[5]
            session['rol'] = user[6]  # Rol del usuario

            next_page=request.args.get('next')

            if next_page:
                return redirect(next_page)

            if user[6] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user[6] == 'empleado':
                return redirect(url_for('empleado'))
            elif user[6] == 'cliente':
                return redirect(url_for('cliente'))
        else:
            flash('Credenciales incorrectas', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')
    
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        dni = request.form['dni']
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        contacto = request.form['contacto']
        correo = request.form['correo']
        contraseña = request.form['contraseña']
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO usuarios (dni,nombre,apellido,contacto,correo,contraseña,rol) values (%s, %s, %s, %s, %s, %s, %s)',(dni, nombre, apellido, contacto, correo, contraseña, 'cliente'))
        cur.execute('INSERT INTO clientes (dni,nombre,apellido,contacto,correo,contraseña,rol) values (%s, %s, %s, %s, %s, %s, %s)',(dni, nombre, apellido, contacto, correo, contraseña, 'cliente'))
        mysql.connection.commit()
        cur.close()

        flash('Registro exitoso.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# Todas las rutas del admin
@app.route('/admin') #acceder a la pag del admin
def admin_dashboard():
    if 'rol' in session and session['rol'] == 'admin':
        return render_template('admin.html')
    else:
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('login'))

@app.route('/admin/servicios', methods=['GET','POST']) #muestra los servicios y agrega nuevos servicios desde el administrador
def gestionar_servicios():#si es get lista los servicios
    if request.method=='GET':
        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM servicios')
        servicios=cur.fetchall()
        cur.close()
    
        return jsonify([{'id':servicio[0], 'nombre':servicio[1], 'descripcion':servicio[2], 'precio':servicio[3]} for servicio in servicios])

    if request.method=='POST':#si es post agrega uno nuevo
        nombre=request.form['nombre']
        descripcion=request.form['descripcion']
        precio=request.form['precio']
        cur=mysql.connection.cursor()
        cur.execute('SELECT MAX(id) FROM servicios')
        id=cur.fetchone()
        if not id[0]:
            idd=1
        else:
            idd=id[0]+1
        cur.execute('INSERT INTO servicios (id,nombre,descripcion,precio) values (%s,%s,%s,%s)',(idd,nombre,descripcion,precio))
        mysql.connection.commit()
        cur.close()

        return jsonify({'status':'success'})

@app.route('/admin/servicios/<int:servicio_id>', methods=['PUT'])
def modificar_servicio(servicio_id):#modifica los datos del empleado si es put
    datos=request.get_json() 
    cur=mysql.connection.cursor()

    if 'nombre' in datos:
        cur.execute('UPDATE servicios SET nombre =%s WHERE id=%s',(datos['nombre'],servicio_id))
    if 'descripcion' in datos:
        cur.execute('UPDATE servicios SET descripcion=%s WHERE id=%s',(datos['descripcion'],servicio_id))
    if 'precio' in datos:
        cur.execute('UPDATE servicios SET precio=%s WHERE id=%s',(datos['precio'],servicio_id))

    mysql.connection.commit()
    cur.close()

    return jsonify({'status': 'success'})

@app.route('/admin/servicios/<int:servicio_id>', methods=['DELETE'])
def eliminar_servicio(servicio_id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM turnos WHERE id_servicio = %s', (servicio_id,))
    cur.execute('DELETE FROM servicios WHERE id = %s', (servicio_id,))
    mysql.connection.commit()
    cur.close()

    return jsonify({'status': 'success'})

@app.route('/admin/empleados/<int:dni>', methods=['PUT'])
def modificar_emplezados(dni):
    datos=request.get_json()
    cur=mysql.connection.cursor()

    if 'dni' in datos:
        cur.execute('UPDATE empleados SET dni=%s where dni=%s',(datos['dni'],dni))
    if 'nombre' in datos:
        cur.execute('UPDATE empleados SET nombre=%s where dni=%s',(datos['nombre'],dni))   
    if 'apellido' in datos:
        cur.execute('UPDATE empleados SET apellido=%s where dni=%s',(datos['apellido'],dni))
    if 'contacto' in datos:
        cur.execute('UPDATE empleados SET contacto=%s where dni=%s',(datos['contacto'],dni))
    if 'correo' in datos:
        cur.execute('UPDATE empleados SET correo=%s where dni=%s',(datos['correo'],dni))
    if 'contraseña' in datos:
        cur.execute('UPDATE empleados SET contraseña=%s where dni=%s',(datos['contraseña'],dni))

    mysql.connection.commit()
    cur.close()

    return jsonify({'status': 'success'})

@app.route('/admin/empleados/<int:dni>', methods=['DELETE'])
def eliminar_empleados(dni):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM empleados WHERE dni = %s', (dni,))
    cur.execute('DELETE FROM usuarios WHERE dni = %s', (dni,))
    mysql.connection.commit()
    cur.close()

    return jsonify({'status': 'success'})

@app.route('/admin/empleados', methods=['GET','POST'])
def gestionar_empleados():
    if request.method=='GET':
        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM empleados')
        empleados=cur.fetchall()
        cur.close()

        return jsonify([{'dni':empleado[0],'nombre':empleado[1],'apellido':empleado[2],'contacto':empleado[3],'correo':empleado[4],'contraseña':empleado[5]} for empleado in empleados])
    
    if request.method=='POST':
        dni=request.form['dni']
        nombre=request.form['nombre']
        apellido=request.form['apellido']
        contacto=request.form['contacto']
        correo=request.form['correo']
        contraseña=request.form['contraseña']
        cur=mysql.connection.cursor()
        cur.execute('INSERT INTO usuarios (dni,nombre,apellido,contacto,correo,contraseña,rol) values (%s,%s,%s,%s,%s,%s,%s)',(dni,nombre,apellido,contacto,correo,contraseña,'empleado'))
        cur.execute('INSERT INTO empleados (dni,nombre,apellido,contacto,correo,contraseña,rol) values (%s,%s,%s,%s,%s,%s,%s)',(dni,nombre,apellido,contacto,correo,contraseña,'empleado'))
        mysql.connection.commit()
        cur.close()

        return jsonify({'status':'success'})


# Empleados
@app.route('/empleado')
def empleado():
    if 'rol' in session and session['rol'] == 'empleado':
        return render_template('empleado.html')
    else:
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('login'))
    
@app.route('/empleado/perfil', methods=['PUT'])
def modificar_perfil_empleado():
    datos=request.get_json()
    print(datos)
    cur=mysql.connection.cursor()
    if 'dni' in datos:
        cur.execute('UPDATE empleados SET dni=%s where dni=%s',(datos['dni'],datos['dni']))
        cur.execute('UPDATE usuarios SET dni=%s where dni=%s',(datos['dni'],datos['dni']))
    if 'nombre' in datos:
        cur.execute('UPDATE empleados SET nombre=%s where dni=%s',(datos['nombre'],datos['dni']))   
        cur.execute('UPDATE usuarios SET nombre=%s where dni=%s',(datos['nombre'],datos['dni']))   
    if 'apellido' in datos:
        cur.execute('UPDATE empleados SET apellido=%s where dni=%s',(datos['apellido'],datos['dni']))
        cur.execute('UPDATE usuarios SET apellido=%s where dni=%s',(datos['apellido'],datos['dni']))
    if 'contacto' in datos:
        cur.execute('UPDATE empleados SET contacto=%s where dni=%s',(datos['contacto'],datos['dni']))
        cur.execute('UPDATE usuarios SET contacto=%s where dni=%s',(datos['contacto'],datos['dni']))
    if 'correo' in datos:
        cur.execute('UPDATE empleados SET correo=%s where dni=%s',(datos['correo'],datos['dni']))
        cur.execute('UPDATE usuarios SET correo=%s where dni=%s',(datos['correo'],datos['dni']))
    if 'contraseña' in datos:
        cur.execute('UPDATE empleados SET contraseña=%s where dni=%s',(datos['contraseña'],datos['dni']))
        cur.execute('UPDATE usuarios SET contraseña=%s where dni=%s',(datos['contraseña'],datos['dni']))

    mysql.connection.commit()
    cur.close()
    session['nombre']=datos['nombre']
    return jsonify({'status': 'success'})


@app.route('/servicios', methods=['GET', 'POST'])
def listar_servicios():
    # Verifica si el usuario está logueado
    if 'dni' not in session:
        return redirect(url_for('login', next=request.url))

    if 'rol' in session and session['rol'] == 'cliente':
        cur = mysql.connection.cursor()

        if request.method == 'GET':
            cur.execute('SELECT * FROM servicios')
            servicios = cur.fetchall()
            cur.execute('SELECT * FROM empleados')
            empleados = cur.fetchall()

            # Generar todas las horas posibles de 30 minutos entre las 9 AM y las 6 PM
            horas_disponibles = []
            inicio = datetime.strptime("09:00", "%H:%M")
            fin = datetime.strptime("18:00", "%H:%M")

            while inicio < fin:
                hora_str = inicio.strftime("%H:%M")
                # Verificar si la hora ya está ocupada
                cur.execute('SELECT * FROM turnos WHERE fecha LIKE %s', (f"%{hora_str}%",))
                turno_existente = cur.fetchone()
                if not turno_existente:
                    horas_disponibles.append(hora_str)
                inicio += timedelta(minutes=30)  # Incremento de 30 minutos

            cur.close()
            return render_template('servicios.html', servicios=servicios, empleados=empleados, horas_disponibles=horas_disponibles)

        elif request.method == 'POST':
            # Verifica que los datos estén presentes
            servicio_id = request.form.get('servicio_id')
            empleado_id = request.form.get('empleado_id')
            fecha = request.form.get('fecha')
            hora = request.form.get('hora')

            if not servicio_id or not empleado_id or not fecha or not hora:
                return jsonify({'error': 'Todos los campos son requeridos.'})

            fechaHora = f'{fecha} {hora}'
            dni_cliente = session['dni']  # Obtener el DNI desde la sesión

            # Verificar si la hora está dentro del horario permitido
            hora_turno = datetime.strptime(hora, '%H:%M').hour
            if hora_turno < 9 or hora_turno >= 18:
                cur.close()
                return jsonify({'error': 'La hora seleccionada está fuera del horario de trabajo. Por favor, elija una hora entre las 9 AM y las 6 PM.'})

            # Verificar si el turno ya está ocupado
            cur.execute('SELECT * FROM turnos WHERE fecha = %s', (fechaHora,))
            turno_existente = cur.fetchone()
            if turno_existente:
                cur.close()
                return jsonify({'error': 'La hora seleccionada está ocupada. Intente con otra.'})

            # Si todo es válido, insertar el turno en la base de datos
            estado = 'reservado'
            cur.execute('INSERT INTO turnos(fecha, estado, id_empleado, id_cliente, id_servicio) values (%s, %s, %s, %s, %s)', (fechaHora, estado, empleado_id, dni_cliente, servicio_id))
            mysql.connection.commit()
            cur.close()
            return jsonify({'success': True})

    return jsonify({'error': 'Acceso denegado.'})

        
@app.route('/cliente')
def cliente():
    if 'rol' in session and session['rol'] == 'cliente':
        return render_template('cliente.html', cliente=cliente)
    else:
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('login'))
    
@app.route('/cliente/perfil', methods=['GET', 'POST'])
def perfil_cliente():
    print(session)
    if 'rol' in session and session['rol'] == 'cliente':
        dni_cliente = session['dni']
        cur = mysql.connection.cursor()

        # Consulta para obtener los turnos del cliente logueado
        cur.execute('SELECT t.fecha, t.estado, s.nombre AS servicio, e.nombre AS empleado_nombre, e.apellido AS empleado_apellido, s.precio '
            'FROM turnos AS t '
            'INNER JOIN servicios AS s ON t.id_servicio = s.id '
            'INNER JOIN empleados AS e ON t.id_empleado = e.dni '
            'WHERE t.id_cliente = %s '
            'ORDER BY t.fecha ASC', (dni_cliente,))

        turnos = cur.fetchall()
        cur.close()

        return render_template('perfil.html', turnos=turnos)
    else:
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('login'))



@app.route('/cliente/perfil/actualizar', methods=['POST'])
def actualizar_perfil():
    if 'rol' in session and session['rol'] == 'cliente':
        # Obtener datos del formulario
        print(request.form)
        dni=request.form['dni']
        nuevo_nombre = request.form['nombre']
        nuevo_email = request.form['email']

        
        cur=mysql.connection.cursor()

        cur.execute('UPDATE clientes SET nombre=%s where dni=%s',(nuevo_nombre,dni))
        cur.execute('UPDATE usuarios SET nombre=%s where dni=%s',(nuevo_nombre,dni))

        mysql.connection.commit()
        cur.close()

        # Actualizar la sesión (opcional)
        session['nombre'] = nuevo_nombre

        return redirect(url_for('perfil'))  # Redirigir de nuevo al perfil
    else:
        return redirect(url_for('login'))

@app.route('/empleado/turnos', methods=['GET'])
def obtener_turnos_empleado(): 
    if 'rol' in session and session['rol'] == 'empleado': 
        id_empleado = session['dni']
        cur = mysql.connection.cursor()
        print(f"ID empleado: {id_empleado}")

        cur.execute('SELECT t.id, t.fecha, s.nombre, c.nombre, c.apellido '
            'FROM turnos AS t '
            'INNER JOIN servicios AS s ON t.id_servicio = s.id '
            'INNER JOIN clientes AS c ON t.id_cliente = c.dni '
            'WHERE t.id_empleado = %s and estado != "finalizado" '
            'ORDER BY t.fecha ASC', (id_empleado,))
        
        turnos = cur.fetchall()
        cur.close()

        # Establecer el idioma español
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

        # Formatear la fecha
        turnos_formateados = []
        for turno in turnos:
            # La fecha ya es un objeto datetime, por lo que solo lo formateamos directamente
            fecha_obj = turno[1]
            # Formatear la fecha en español
            fecha_formateada = fecha_obj.strftime("%A, %d de %B de %Y %H:%M:%S")
            turnos_formateados.append({
                'id': turno[0],
                'fecha': fecha_formateada,  # Fecha ya formateada
                'NomServicio': turno[2],
                'NombreCliente': turno[3],
                'apellido': turno[4]
            })
        
        # Responder con los turnos formateados
        return jsonify(turnos_formateados)
    else: 
        flash('Acceso denegado.')
        return redirect(url_for('login'))
    
@app.route('/empleado/turno/<int:turno_id>/finalizar', methods=['PUT'])
def finalizar_turno(turno_id):
    cur = mysql.connection.cursor()

    # Verificar si el turno existe
    cur.execute('SELECT estado FROM turnos WHERE id = %s', (turno_id,))
    turno = cur.fetchone()

    if turno:
        if turno[0] == 'finalizado':
            return jsonify({"error": "Este turno ya ha sido finalizado"}), 400

        # Actualizar el estado del turno a 'Finalizado'
        cur.execute('UPDATE turnos SET estado = "finalizado" WHERE id = %s', (turno_id,))
        mysql.connection.commit()  # Guardar los cambios en la base de datos

        return jsonify({"message": "Turno finalizado correctamente"}), 200
    else:
        return jsonify({"error": "Turno no encontrado"}), 404

    cur.close()


    
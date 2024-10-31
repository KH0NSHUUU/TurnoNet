from flask import render_template, request, redirect, session, url_for, flash, jsonify
from app import app, mysql

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
            session['rol'] = user[6]  # Rol del usuario

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
    if 'nombre' in datos:
        cur.execute('UPDATE empleados SET nombre=%s where dni=%s',(datos['nombre'],datos['dni']))   
    if 'apellido' in datos:
        cur.execute('UPDATE empleados SET apellido=%s where dni=%s',(datos['apellido'],datos['dni']))
    if 'contacto' in datos:
        cur.execute('UPDATE empleados SET contacto=%s where dni=%s',(datos['contacto'],datos['dni']))
    if 'correo' in datos:
        cur.execute('UPDATE empleados SET correo=%s where dni=%s',(datos['correo'],datos['dni']))
    if 'contraseña' in datos:
        cur.execute('UPDATE empleados SET contraseña=%s where dni=%s',(datos['contraseña'],datos['dni']))

    mysql.connection.commit()
    cur.close()

    return jsonify({'status': 'success'})

# Clientes
@app.route('/cliente')
def cliente():
    if 'rol' in session and session['rol'] == 'cliente':
        return render_template('cliente.html')
    else:
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('login'))

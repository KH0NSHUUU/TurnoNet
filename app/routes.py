from flask import render_template, request, redirect, session, url_for, flash
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
                return redirect(url_for('admin'))
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
        cur.execute(
            'INSERT INTO usuarios (dni,nombre,apellido,contacto,correo,contraseña,rol) values (%s, %s, %s, %s, %s, %s, %s)',
            (dni, nombre, apellido, contacto, correo, contraseña, 'cliente')
        )
        cur.execute(
            'INSERT INTO clientes (dni,nombre,apellido,contacto,correo,contraseña,rol) values (%s, %s, %s, %s, %s, %s, %s)',
            (dni, nombre, apellido, contacto, correo, contraseña, 'cliente')
        )
        mysql.connection.commit()
        cur.close()

        flash('Registro exitoso.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/empleado')
def empleado():
    return render_template('empleado.html')

@app.route('/cliente')
def cliente():
    return render_template('cliente.html')

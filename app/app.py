from flask import Flask
from flask_mysqldb import MySQL
from flask_session import Session

app=Flask(__name__)

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='123456' #pone tu contraseña de la BD
app.config['MYSQL_DB']='TurnoNet'
app.secret_key='asdasdasdasd'
app.config['SESSION_TYPE'] = 'filesystem'  # O el tipo de sesión que desees usar
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
Session(app)

mysql=MySQL(app)

from routes import * 

if __name__ == '__main__':
    app.run(debug=True)

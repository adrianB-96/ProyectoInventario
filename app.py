from flask import Flask
from flask import render_template, redirect, request, Response, session, url_for, flash, jsonify
from flask_mysqldb import MySQL, MySQLdb
from config import config
from configdb2 import *
from flask_login import LoginManager,login_user,logout_user,login_required

# Models:
from models.ModelUser import ModelUser

# Entitites:
from models.entities.User import User

app = Flask(__name__, template_folder='template')
app.secret_key = ''

db = MySQL(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(id):
        return ModelUser.get_by_id(db,id)

#@app.errorhandler(404)
#def not_found(error):
#        return redirect(url_for(home))

@app.route('/')
def home():
        return render_template('web.html')

@app.route('/busqueda/<puesto_id>')
def ver_resultados_puesto(puesto_id):
    conexion_MySQLdb = connectionBD()
    mycursor = conexion_MySQLdb.cursor(dictionary=True)
    mycursor.execute("select * from registros where nombre_puesto = %s", (puesto_id,))
    data = mycursor.fetchall()
        #print (data)
    total = mycursor.rowcount
    mycursor.close()
    conexion_MySQLdb.close()
        #print (total)
    return render_template('/resultadobusqueda.html', dataconsulta=data, datatotal=total)

@app.route('/iniciosesion')
def about():
        return render_template('edit.html')

@app.route('/apuntarllamadas')
def apuntarllamadas():
        return render_template('apuntarllamadas.html')

@app.route('/editllamadas', methods=['GET', 'POST'])
def editllamadas():
        if request.method == 'POST':
                pais = request.form['pais']
                numero = request.form['numero']
                agente = request.form['agente']
                agente_receptor = request.form['agente_receptor']
                hora_atendido = request.form['hora_atendido']
                especialidad = request.form['especialidad']
                comentarios = request.form['comentarios']
                conexion_MySQLdb = connectionBD()
                cursor1 = conexion_MySQLdb.cursor(dictionary=True)
                editar = ("INSERT INTO LLAMADAS_ESPECIALISTAS (pais, numero, agente, agente_receptor, hora_atendido, especialidad_destino, comentarios) VALUES (%s, %s, %s, %s, %s, %s, %s);")
                cursor1.execute(editar,(pais,numero,agente,agente_receptor,hora_atendido,especialidad,comentarios,))
                conexion_MySQLdb.commit()
                cursor1.close()
                conexion_MySQLdb.close()
                flash("DATOS CREADOS CORRECTAMENTE")
                return render_template('apuntarllamadas.html')
        else:
                return render_template('apuntarllamadas.html')

@app.route('/llamadasespecialistas')
def llamadasespecialistas():
        conexion_MySQLdb = connectionBD()
        mycursor = conexion_MySQLdb.cursor(dictionary=True)
        consultaSqlPais = ("SELECT DISTINCT pais FROM llamadas_especialistas;")
        mycursor.execute(consultaSqlPais)
        data = mycursor.fetchall()
        #print (data)
        #total = mycursor.rowcount
        mycursor.close()
        conexion_MySQLdb.close()
        #print (total)
        return render_template('llamadasespecialistas.html', resultadoConsultaPais = data)

@app.route('/llamadasespecialistas', methods=['GET', 'POST'])
def buscarLlamadasEspecialistas():
        if request.method == 'POST':
                pais = request.form['paises']

                #print(pais)
                if pais != "*":
                        conexion_MySQLdb = connectionBD()
                        mycursor = conexion_MySQLdb.cursor(dictionary=True)
                        consultasql = ("select * from llamadas_especialistas where pais = %s and fechayhora_contactado is NULL and (fechayhora_nocontactado is NULL or fechayhora_nocontactado2 is NULL);")
                        parametros = (pais,)
                        mycursor.execute(consultasql, parametros)
                        data = mycursor.fetchall()
                        #print (data)
                        total = mycursor.rowcount
                        mycursor.close()
                        conexion_MySQLdb.close()
                        #print (total)
                        return render_template('resultadollamadasespecialistas.html', dataconsulta = data, datatotal = total)
                
                if pais == "*":
                        conexion_MySQLdb = connectionBD()
                        mycursor = conexion_MySQLdb.cursor(dictionary=True)
                        consultasql = ("select * from llamadas_especialistas where fechayhora_contactado is NULL and (fechayhora_nocontactado is NULL or fechayhora_nocontactado2 is NULL);")
                        mycursor.execute(consultasql)
                        data = mycursor.fetchall()
                        #print (data)
                        total = mycursor.rowcount
                        mycursor.close()
                        conexion_MySQLdb.close()
                        #print (total)
                        return render_template('resultadollamadasespecialistas.html', dataconsulta = data, datatotal = total)
        else:
                return render_template('llamadasespecialistas.html')

@app.route('/actualizar_llamada_especialista/<int:id_llamada>', methods=['POST'])
def actualizar_llamada_especialista(id_llamada):
        try:
                # 1. Recoger los datos enviados desde los inputs de la fila
                datos_json = request.get_json()

                if datos_json is None:
                        return jsonify({'status': 'error', 'message': 'No se recibieron datos JSON'}), 400

                cliente = datos_json.get('cliente')
                agente = datos_json.get('agente')
                fechayhoracontactado = datos_json.get('fechayhoracontactado')
                fechayhoraNO = datos_json.get('fechayhoraNO')
                fechayhoraNO2 = datos_json.get('fechayhoraNO2')
                nota = datos_json.get('nota')

                if not cliente: cliente = None
                if not agente: agente = None
                if not fechayhoracontactado: fechayhoracontactado = None
                if not fechayhoraNO: fechayhoraNO = None
                if not fechayhoraNO2: fechayhoraNO2 = None
                if not nota: nota = None

                # 2. Conectar a la base de datos y lanzar el UPDATE
                conexion_MySQLdb = connectionBD()
                mycursor = conexion_MySQLdb.cursor(dictionary=True)
                
                sql = """
                        UPDATE llamadas_especialistas 
                        SET cliente = %(cliente)s, agente = %(agente)s, fechayhora_contactado = %(fechayhoracontactado)s, fechayhora_nocontactado = %(fechayhora_nocontactado)s, fechayhora_nocontactado2 = %(fechayhora_nocontactado2)s, nota = %(nota)s 
                        WHERE id_llamada = %(id_llamada)s
                """
                datos_dict = {
                        'cliente': cliente, 
                        'agente': agente, 
                        'fechayhoracontactado': fechayhoracontactado,
                        'fechayhora_nocontactado': fechayhoraNO,
                        'fechayhora_nocontactado2': fechayhoraNO2,
                        'nota': nota, 
                        'id_llamada': id_llamada
                }

                mycursor.execute(sql, datos_dict)
                conexion_MySQLdb.commit()
                mycursor.close()
                conexion_MySQLdb.close()

                #return redirect(request.referrer or url_for('llamadas.html'))
                return jsonify({'status': 'success', 'message': 'Registro actualizado correctamente'}), 1
        except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)}), 1

@app.route('/llamadas')
def llamadas():
        conexion_MySQLdb = connectionBD()
        mycursor = conexion_MySQLdb.cursor(dictionary=True)
        consultaSqlPais = ("SELECT DISTINCT pais FROM llamadas;")
        mycursor.execute(consultaSqlPais)
        data = mycursor.fetchall()
        #print (data)
        #total = mycursor.rowcount
        mycursor.close()
        conexion_MySQLdb.close()
        #print (total)
        return render_template('llamadas.html', resultadoConsultaPais = data)



@app.route('/llamadas', methods=['GET', 'POST'])
def buscarLlamadas():
        if request.method == 'POST':
                pais = request.form['paises']

                #print(pais)
                if pais != "*":
                        conexion_MySQLdb = connectionBD()
                        mycursor = conexion_MySQLdb.cursor(dictionary=True)
                        consultasql = ("select * from llamadas where pais = %s and hora_contacto is NULL and (fechayhora_nocontactado is NULL or fechayhora_nocontactado2 is NULL);")
                        parametros = (pais,)
                        mycursor.execute(consultasql, parametros)
                        data = mycursor.fetchall()
                        #print (data)
                        total = mycursor.rowcount
                        mycursor.close()
                        conexion_MySQLdb.close()
                        #print (total)
                        return render_template('resultadollamadas.html', dataconsulta = data, datatotal = total)
                
                if pais == "*":
                        conexion_MySQLdb = connectionBD()
                        mycursor = conexion_MySQLdb.cursor(dictionary=True)
                        consultasql = ("select * from llamadas where hora_contacto is NULL and (fechayhora_nocontactado is NULL or fechayhora_nocontactado2 is NULL);")
                        mycursor.execute(consultasql)
                        data = mycursor.fetchall()
                        #print (data)
                        total = mycursor.rowcount
                        mycursor.close()
                        conexion_MySQLdb.close()
                        #print (total)
                        return render_template('resultadollamadas.html', dataconsulta = data, datatotal = total)
        else:
                return render_template('llamadas.html')

@app.route('/actualizar_llamada/<int:id_llamada>', methods=['POST'])
def actualizar_llamada(id_llamada):
        try:
                # 1. Recoger los datos enviados desde los inputs de la fila
                datos_json = request.get_json()

                if datos_json is None:
                        return jsonify({'status': 'error', 'message': 'No se recibieron datos JSON'}), 400

                cliente = datos_json.get('cliente')
                agente = datos_json.get('agente')
                fecha_contacto = datos_json.get('fecha_contacto')
                hora_contacto = datos_json.get('hora_contacto')
                fechayhoraNO = datos_json.get('fechayhoraNO')
                fechayhoraNO2 = datos_json.get('fechayhoraNO2')
                nota = datos_json.get('nota')

                if not cliente: cliente = None
                if not agente: agente = None
                if not fecha_contacto: fecha_contacto = None
                if not hora_contacto: hora_contacto = None
                if not fechayhoraNO: fechayhoraNO = None
                if not fechayhoraNO2: fechayhoraNO2 = None
                if not nota: nota = None

                # 2. Conectar a la base de datos y lanzar el UPDATE
                conexion_MySQLdb = connectionBD()
                mycursor = conexion_MySQLdb.cursor(dictionary=True)
                
                sql = """
                        UPDATE llamadas 
                        SET cliente = %(cliente)s,  agente = %(agente)s, fecha_contacto = %(fecha_contacto)s, hora_contacto = %(hora_contacto)s, fechayhora_nocontactado = %(fechayhora_nocontactado)s, fechayhora_nocontactado2 = %(fechayhora_nocontactado2)s, nota = %(nota)s 
                        WHERE id_llamada = %(id_llamada)s
                """
                datos_dict = {
                        'cliente': cliente, 
                        'agente': agente, 
                        'fecha_contacto': fecha_contacto, 
                        'hora_contacto': hora_contacto, 
                        'fechayhora_nocontactado': fechayhoraNO,
                        'fechayhora_nocontactado2': fechayhoraNO2,
                        'nota': nota, 
                        'id_llamada': id_llamada
                }

                mycursor.execute(sql, datos_dict)
                conexion_MySQLdb.commit()
                mycursor.close()
                conexion_MySQLdb.close()

                #return redirect(request.referrer or url_for('llamadas.html'))
                return jsonify({'status': 'success', 'message': 'Registro actualizado correctamente'}), 1
        except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)}), 1

@app.route('/busqueda')
def busqueda():
        conexion_MySQLdb = connectionBD()
        mycursor = conexion_MySQLdb.cursor(dictionary=True)
        consultadatosespecialidad = ("SELECT DISTINCT nombre_especialidad FROM registros;")
        consultadatosproducto = ("SELECT DISTINCT modelo_producto FROM registros;")
        consultadatospuesto = ("SELECT DISTINCT nombre_puesto FROM registros;")
        mycursor.execute(consultadatosespecialidad)
        datosespecialidad = mycursor.fetchall()
        mycursor.execute(consultadatosproducto)
        datosproducto = mycursor.fetchall()
        mycursor.execute(consultadatospuesto)
        datospuesto = mycursor.fetchall()
        ##print (datosespecialidad)
        ##print (datosproducto)
        ##print (datospuesto)
        mycursor.close()
        conexion_MySQLdb.close()
        return render_template("busqueda.html", resultadoconsultaespecialidad = datosespecialidad, resultadoconsultaproducto = datosproducto, resultadoconsultapuesto = datospuesto)


@app.route('/editcorrect')
@login_required
def editcorrect():
        conexion_MySQLdb = connectionBD()
        mycursor = conexion_MySQLdb.cursor(dictionary=True)
        listaespecialidades = ("SELECT nombre FROM especialidad;")
        listapuestos = ("SELECT nombre FROM puestos;")
        mycursor.execute(listaespecialidades)
        resultadoespecialidad = mycursor.fetchall()
        mycursor.execute(listapuestos)
        resultadopuestos = mycursor.fetchall()
        #print (resultadoespecialidad)
        #print (resultadopuestos)
        mycursor.close()
        conexion_MySQLdb.close()
        return render_template('editcorrect.html', specialist = resultadoespecialidad, puesto = resultadopuestos)


@app.route('/editbusqueda', methods=['GET', 'POST'])
def editbusqueda():
        if request.method == 'POST':
                id = request.form['id']
                ip = request.form['ip']
                puerto = request.form['puerto']
                usuario = request.form['usuario']
                contraseña = request.form['contraseña']
                #print(id)
                #print(ip)
                #print(puerto)
                #print(usuario)
                #print(contraseña)
                conexion_MySQLdb = connectionBD()
                micursor1 = conexion_MySQLdb.cursor(dictionary=True)
                idcheck = ("select id_registro from registros where id_registro=%s;")
                micursor1.execute(idcheck,(id,))
                check = micursor1.fetchall()
                check2 = micursor1.rowcount
                micursor1.close()
                conexion_MySQLdb.close()
                print(check2)
                if check2 > 0:
                        conexion_MySQLdb = connectionBD()
                        cursor1 = conexion_MySQLdb.cursor(dictionary=True)
                        editar = ("update registros set ip_producto=%s, puerto=%s, usuario_producto=%s, pwd_terminal=%s where id_registro=%s;")
                        cursor1.execute(editar,(ip,puerto,usuario,contraseña,id,))
                        conexion_MySQLdb.commit()
                        cursor1.close()
                        conexion_MySQLdb.close()
                        flash("DATOS EDITADOS CORRECTAMENTE")
                        return render_template('editbusqueda.html')
                else:
                        flash("DATOS INTRODUCIDOS NO EXISTEN O NO SON VALIDOS")
                        return render_template('editbusqueda.html')
        else:
                return render_template('editbusqueda.html')

@app.route('/edit', methods=['GET', 'POST'])
def login():
        if request.method == 'POST':
                #print(request.form['user'])
                #print(request.form['password'])
                user=User(0,request.form['user'],request.form['password'])
                logged_user=ModelUser.login(db,user)
                if logged_user != None:
                        if logged_user.pwd:
                                login_user(logged_user)
                                ##flash("HAS INICIADO SESION CORRECTAMENTE")
                                return render_template('modificar.html')
                                
                        else:
                                flash("CONTRASEÑA INCORRECTA")
                                return render_template('edit.html')
                else:
                        flash("USUARIO NO EXISTE")
                        return render_template('edit.html')
        else:
                return render_template('edit.html')

@app.route('/logout')
def logout():
        logout_user()
        flash("HAS CERRADO SESION CORRECTAMENTE")
        return render_template('edit.html')

@app.route('/insert', methods=['GET', 'POST'])
def insertar():
        if request.method == 'POST':
                especialidad = request.form['especialidad']
                puesto = request.form['puesto']
                producto = request.form['producto']
                ipproducto = request.form['ipproducto']
                puerto = request.form['puerto']
                userproducto = request.form['userproducto']
                pwdproducto = request.form['pwdproducto']

                #print(especialidad)
                #print(puesto)
                #print(producto)
                #print(ipproducto)
                #print(ipproducto)
                #print(userproducto)
                #print(pwdproducto)
                
                conexion_MySQLdb = connectionBD()
                cursor = conexion_MySQLdb.cursor(dictionary=True)

                sqlinsert = ("INSERT INTO registros(nombre_especialidad, modelo_producto, ip_producto, puerto, usuario_producto, pwd_terminal, nombre_puesto) VALUES (%s, %s, %s, %s, %s, %s, %s);")
                cursor.execute(sqlinsert,(especialidad,producto,ipproducto,puerto,userproducto,pwdproducto,puesto,))
                conexion_MySQLdb.commit()
                cursor.close()
                conexion_MySQLdb.close()
                flash("DATOS ALMACENADOS CORRECTAMENTE")
                return render_template('editcorrect.html')
        else:
                return render_template('edit.html')


@app.route('/busqueda', methods=['GET', 'POST'])
def buscar():
        if request.method == 'POST':
                especialidades = request.form['especialidad']
                puestos = request.form['puestos']
                productos = request.form['productos']

                #print(especialidades)
                #print(productos)
                #print(puestos)
                if especialidades != "*" and puestos != "*" and productos != "*": 
                        conexion_MySQLdb = connectionBD()
                        mycursor = conexion_MySQLdb.cursor(dictionary=True)
                        consultasql = ("select * from registros where nombre_especialidad=%s and modelo_producto=%s and nombre_puesto=%s;")
                        mycursor.execute(consultasql,(especialidades,productos,puestos,))
                        data = mycursor.fetchall()
                        #print (data)
                        total = mycursor.rowcount
                        mycursor.close()
                        conexion_MySQLdb.close()
                        #print (total)
                        return render_template('resultadobusqueda.html', dataconsulta = data, datatotal = total)
                
                if especialidades == "*" and puestos != "*" and productos != "*":
                        conexion_MySQLdb = connectionBD()
                        mycursor = conexion_MySQLdb.cursor(dictionary=True)
                        consultasql = ("select * from registros where modelo_producto=%s and nombre_puesto=%s;")
                        mycursor.execute(consultasql,(productos,puestos,))
                        data = mycursor.fetchall()
                        #print (data)
                        total = mycursor.rowcount
                        mycursor.close()
                        conexion_MySQLdb.close()
                        #print (total)
                        return render_template('resultadobusqueda.html', dataconsulta = data, datatotal = total)
                
                if productos == "*" and especialidades != "*" and puestos != "*":
                        conexion_MySQLdb = connectionBD()
                        mycursor = conexion_MySQLdb.cursor(dictionary=True)
                        consultasql = ("select * from registros where nombre_especialidad=%s and nombre_puesto=%s;")
                        mycursor.execute(consultasql,(especialidades,puestos,))
                        data = mycursor.fetchall()
                        #print (data)
                        total = mycursor.rowcount
                        mycursor.close()
                        conexion_MySQLdb.close()
                        #print (total)
                        return render_template('resultadobusqueda.html', dataconsulta = data, datatotal = total)
                
                if puestos == "*" and especialidades != "*" and productos != "*":
                        conexion_MySQLdb = connectionBD()
                        mycursor = conexion_MySQLdb.cursor(dictionary=True)
                        consultasql = ("select * from registros where nombre_especialidad=%s and modelo_producto=%s;")
                        mycursor.execute(consultasql,(especialidades,productos,))
                        data = mycursor.fetchall()
                        #print (data)
                        total = mycursor.rowcount
                        mycursor.close()
                        conexion_MySQLdb.close()
                        #print (total)
                        return render_template('resultadobusqueda.html', dataconsulta = data, datatotal = total)

                if especialidades != "*" and puestos == "*" and productos == "*":
                        conexion_MySQLdb = connectionBD()
                        mycursor = conexion_MySQLdb.cursor(dictionary=True)
                        consultasql = ("select * from registros where nombre_especialidad=%s;")
                        mycursor.execute(consultasql,(especialidades,))
                        data = mycursor.fetchall()
                        #print (data)
                        total = mycursor.rowcount
                        mycursor.close()
                        conexion_MySQLdb.close()
                        #print (total)
                        return render_template('resultadobusqueda.html', dataconsulta = data, datatotal = total)

                if puestos != "*" and especialidades == "*" and productos == "*":
                        conexion_MySQLdb = connectionBD()
                        mycursor = conexion_MySQLdb.cursor(dictionary=True)
                        consultasql = ("select * from registros where nombre_puesto=%s;")
                        mycursor.execute(consultasql,(puestos,))
                        data = mycursor.fetchall()
                        #print (data)
                        total = mycursor.rowcount
                        mycursor.close()
                        conexion_MySQLdb.close()
                        #print (total)
                        return render_template('resultadobusqueda.html', dataconsulta = data, datatotal = total)

                if productos != "*" and puestos == "*" and especialidades == "*":
                        conexion_MySQLdb = connectionBD()
                        mycursor = conexion_MySQLdb.cursor(dictionary=True)
                        consultasql = ("select * from registros where modelo_producto=%s;")
                        mycursor.execute(consultasql,(productos,))
                        data = mycursor.fetchall()
                        #print (data)
                        total = mycursor.rowcount
                        mycursor.close()
                        conexion_MySQLdb.close()
                        #print (total)
                        return render_template('resultadobusqueda.html', dataconsulta = data, datatotal = total)     

                else:
                        conexion_MySQLdb = connectionBD()
                        mycursor = conexion_MySQLdb.cursor(dictionary=True)
                        consultasql = ("select * from registros")
                        mycursor.execute(consultasql)
                        data = mycursor.fetchall()
                        #print (data)
                        total = mycursor.rowcount
                        mycursor.close()
                        conexion_MySQLdb.close()
                        #print (total)
                        return render_template('resultadobusqueda.html', dataconsulta = data, datatotal = total)
        else:
                return render_template('busqueda.html')

@app.route('/editeliminar', methods=['GET', 'POST'])
@login_required
def editeliminar():
        if request.method == 'POST':
                id = request.form['id']
                #print(id)
                conexion_MySQLdb = connectionBD()
                micursor1 = conexion_MySQLdb.cursor(dictionary=True)
                idcheck = ("select id_registro from registros where id_registro=%s;")
                micursor1.execute(idcheck,(id,))
                check = micursor1.fetchall()
                check2 = micursor1.rowcount
                micursor1.close()
                conexion_MySQLdb.close()
                print(check2)
                if check2 > 0:
                        conexion_MySQLdb = connectionBD()
                        micursor2 = conexion_MySQLdb.cursor(dictionary=True)
                        sqleliminar = ("delete from registros where id_registro=%s;")
                        micursor2.execute(sqleliminar,(id,))
                        conexion_MySQLdb.commit()
                        micursor2.close()
                        conexion_MySQLdb.close()
                        flash("Registro eliminado correctamente")
                        return render_template('editeliminar.html')
                else:
                        flash("El valor introducido no es valido o no existe")
                        return render_template('editeliminar.html')
        else:
                return render_template('editeliminar.html')
        
@app.route('/llamadasespecialistasALL', methods=['GET', 'POST'])
@login_required
def llamadasespecialistasALL():
        return render_template('llamadasespecialistasALL.html')

@app.route('/llamadasALL')
@login_required
def llamadasALL():
        conexion_MySQLdb = connectionBD()
        mycursor = conexion_MySQLdb.cursor(dictionary=True)
        consultaSqlPais = ("SELECT DISTINCT pais FROM llamadas;")
        consultaSqlAgente = ("SELECT DISTINCT agente FROM llamadas;")
        mycursor.execute(consultaSqlPais)
        dataPais = mycursor.fetchall()
        mycursor.execute(consultaSqlAgente)
        dataAgente = mycursor.fetchall()
        #print (data)
        #total = mycursor.rowcount
        mycursor.close()
        conexion_MySQLdb.close()
        #print (total)
        return render_template('llamadasALL.html', resultadoConsultaPais = dataPais, resultadoConsultaAgente = dataAgente)

@app.route('/llamadasALL', methods=['GET', 'POST'])
def buscarLlamadasALL():
        if request.method == 'POST':
                pais = request.form['paises']
                cliente = request.form['cliente']
                fecha = request.form['fecha_abandono']
                hora = request.form['hora_abandono']
                agente = request.form['agente']

                query_base = "SELECT * FROM llamadas"
                condiciones = []
                valores = []

                if pais and pais != "*":
                        condiciones.append("pais = %s")
                        valores.append(pais)

                if cliente:
                        condiciones.append("cliente LIKE %s")
                        valores.append(f"%{cliente}%")

                if fecha:
                        condiciones.append("fecha_abandono = %s")
                        valores.append(fecha)

                if hora:
                        condiciones.append("hora_abandono = %s")
                        valores.append(hora)

                if agente != "None" and agente != "*":
                        condiciones.append("agente = %s")
                        valores.append(agente)
                if agente == "None":
                        condiciones.append("agente IS NULL")

                if condiciones:
                        query_final = f"{query_base} WHERE {' AND '.join(condiciones)};"
                else:
                        query_final = f"{query_base};"

                conexion_MySQLdb = connectionBD()
                mycursor = conexion_MySQLdb.cursor(dictionary=True)
                
                mycursor.execute(query_final, tuple(valores))
                data = mycursor.fetchall()
                total = mycursor.rowcount
                
                mycursor.close()
                conexion_MySQLdb.close()
                
                return render_template('resultadollamadas.html', dataconsulta=data, datatotal=total)
        else:
                return render_template('llamadasALL.html')

if __name__ == '__main__':
        app.config.from_object(config['development'])
        app.run(debug=True, host='0.0.0.0', port=5001, threaded=True)

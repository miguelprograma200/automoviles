from flask import Flask,jsonify, render_template,request,redirect,url_for,flash #importaciones
import pymysql
import pymysql.cursors
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

CORS(app, origins=["http://localhost:62384/","http://192.168.10.212"])

app.secret_key =  '12'

def connect_to_db():
    return pymysql.connect (
        host= 'localhost',
        user= 'root',
        passwd='',
        database='automoviles',
        cursorclass=pymysql.cursors.DictCursor,
        ssl_disabled=True
    )

#ruta de pagina de incio 
@app.route("/")
def inicio():
    conn = connect_to_db()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM clientes")
    clientes_data = cur.fetchall()
    
    cur.execute("""
        SELECT coches.*, clientes.nombre as nombre_cliente 
        FROM coches 
        LEFT JOIN clientes ON coches.nif_cliente = clientes.nif
    """)
    coches_data = cur.fetchall()
    
    cur.execute("SELECT * FROM revisiones")
    revisiones_data = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('index.html', clientes=clientes_data, coches=coches_data, revisiones=revisiones_data)


#ruta de autos deportivos
@app.route('/deportivos')
def deportivos():
    return render_template('deportivos.html')


#ruta de autos camionetas
@app.route('/camionetas')
def camionetas():
    return render_template('camionetas.html')


#ruta de autos familiares
@app.route('/familiares')
def familiares():
    return render_template('familiares.html')


#ruta de agregar clientes
@app.route('/clientes/add', methods=['GET', 'POST'])
def add_cliente():
    if request.method == 'POST':
        nif = request.form['nif']
        nombre = request.form['nombre']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        try:
            conn = connect_to_db()
            cur = conn.cursor()
            cur.execute("INSERT INTO clientes (nif, nombre, direccion, telefono) VALUES (%s, %s, %s, %s)",
                        (nif, nombre, direccion, telefono))
            conn.commit()
            flash('Cliente agregado correctamente')
        except Exception as e:
            flash(f"Error al agregar cliente: {e}")
        finally:
            cur.close()
            conn.close()
        return redirect(url_for('inicio'))
    return render_template('add_cliente.html')


#  RUTAS PARA COCHES 
@app.route('/coches/add', methods=['GET', 'POST'])
def add_coche():
    conn = connect_to_db()
    cur = conn.cursor()
    
    if request.method == 'POST':
        matricula = request.form['matricula']
        marca = request.form['marca']
        modelo = request.form['modelo']
        color = request.form['color']
        precio = request.form['precio']
        nif_cliente = request.form['nif_cliente']
        try:
            cur.execute("INSERT INTO coches (matricula, marca, modelo, color, precio, nif_cliente) VALUES (%s,%s,%s,%s,%s,%s)",
                        (matricula, marca, modelo, color, precio, nif_cliente))
            conn.commit()
            flash('Coche agregado correctamente')
        except Exception as e:
            flash(f"Error al agregar coche: {e}")
        finally:
            cur.close()
            conn.close()
        return redirect(url_for('inicio'))
    
    cur.execute("SELECT nif, nombre FROM clientes")
    clientes = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('add_coche.html', clientes=clientes)


# RUTAS PARA REVISIONES 
@app.route('/revisiones/add', methods=['GET', 'POST'])
def add_revision():
    conn = connect_to_db()
    cur = conn.cursor()

    if request.method == 'POST':
        matricula_coche = request.form['matricula_coche']
        filtro = request.form.get('filtro') 
        aceite = request.form.get('aceite')
        frenos = request.form.get('frenos')

        filtro_val = 1 if filtro == 'on' else 0
        aceite_val = 1 if aceite == 'on' else 0
        frenos_val = 1 if frenos == 'on' else 0

        try:
            cur.execute("INSERT INTO revisiones (matricula_coche, filtro, aceite, frenos) VALUES (%s, %s, %s, %s)",
                        (matricula_coche, filtro_val, aceite_val, frenos_val))
            conn.commit()
            flash('Revisión agregada correctamente')
        except Exception as e:
            flash(f"Error al agregar revisión: {e}")
        finally:
            cur.close()
            conn.close()
        return redirect(url_for('inicio'))
    cur.execute("SELECT matricula, marca, modelo FROM coches")
    coches = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('add_revision.html', coches=coches)



#RUTA PARA EDITAR UN CLIENTE
@app.route('/cliente/edit/<string:nif>', methods=['GET', 'POST'])
def edit_cliente(nif):
    conn = connect_to_db()
    cur = conn.cursor()
    if request.method == 'POST':
        nombre = request.form['nombre']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        cur.execute("""
            UPDATE clientes
            SET nombre = %s,
                direccion = %s,
                telefono = %s
            WHERE nif = %s
        """, (nombre, direccion, telefono, nif))
        conn.commit()
        cur.close()
        conn.close()
        flash('Cliente actualizado correctamente')
        return redirect(url_for('inicio'))

    cur.execute("SELECT * FROM clientes WHERE nif = %s", (nif,))
    cliente = cur.fetchone() 
    cur.close()
    conn.close()
    return render_template('edit_cliente.html', cliente=cliente)


# RUTA PARA ELIMINAR UN CLIENTE
@app.route('/cliente/delete/<string:nif>', methods=['POST'])
def delete_cliente(nif):
    conn = connect_to_db()
    cur = conn.cursor()
    try:
        # Intentar eliminar el cliente
        cur.execute("DELETE FROM clientes WHERE nif = %s", (nif,))
        conn.commit()
        flash('Cliente eliminado correctamente')
    except Exception as e:
        flash(f'Error al eliminar el cliente: No se puede eliminar porque tiene coches asociados.')
    finally:
        cur.close()
        conn.close()
    return redirect(url_for('inicio'))


#ruta para editar un coche
@app.route('/coche/edit/<string:matricula>', methods=['GET', 'POST'])
def edit_coche(matricula):
    conn = connect_to_db()
    cur = conn.cursor()
    if request.method == 'POST':
        marca = request.form['marca']
        modelo = request.form['modelo']
        color= request.form['color']
        precio= request.form['precio']
        nif_cliente = request.form['nif_cliente']
        
        cur.execute("""
            UPDATE coches
            SET marca = %s,
                modelo = %s,
                color = %s,
                precio = %s,
                nif_cliente = %s
            WHERE matricula = %s
        """, (marca, modelo, color,precio,nif_cliente,matricula))
        conn.commit()
        cur.close()
        conn.close()
        flash('Coche actualizado correctamente')
        return redirect(url_for('inicio'))

    cur.execute("SELECT * FROM coches WHERE matricula = %s", (matricula,))
    coche = cur.fetchone() 

    cur.execute("SELECT nif, nombre FROM clientes")
    clientes = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('edit_coche.html', coche=coche, clientes=clientes)

# --- RUTA PARA ELIMINAR UN COCHE ---
@app.route('/coche/delete/<string:matricula>', methods=['POST'])
def delete_coche(matricula):
    conn = connect_to_db()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM coches WHERE matricula = %s", (matricula,))
        conn.commit()
        flash('Coche eliminado correctamente')
        
    except Exception as e:
        
        conn.rollback() 
        flash('Error: No se puede eliminar el coche porque tiene revisiones asociadas.')
        
    finally:
    
        cur.close()
        conn.close()
    return redirect(url_for('inicio'))


#ruta para editar una revison
@app.route('/revision/edit/<int:codigo>', methods=['GET', 'POST'])
def edit_revision(codigo):
    conn = connect_to_db()
    cur = conn.cursor()
    if request.method == 'POST':
        matricula_coche = request.form['matricula_coche']
        filtro = 1 if 'filtro' in request.form else 0
        aceite = 1 if 'aceite' in request.form else 0
        frenos = 1 if 'frenos' in request.form else 0

        cur.execute("""
            UPDATE revisiones
            SET matricula_coche = %s,
                filtro = %s,
                aceite = %s,
                frenos = %s
            WHERE codigo = %s
        """, (matricula_coche, filtro, aceite, frenos, codigo))
        
        conn.commit()
        cur.close()
        conn.close()
        flash('Revisión actualizada correctamente')
        return redirect(url_for('inicio'))

    cur.execute("SELECT * FROM revisiones WHERE codigo = %s", (codigo,))
    revision = cur.fetchone() 

    cur.execute("SELECT matricula, marca, modelo FROM coches")
    coches = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('edit_revision.html', revision=revision, coches=coches)

# ruta para eliminar a una revicion
@app.route('/revision/delete/<int:codigo>', methods=['POST'])
def delete_revision(codigo):
    conn = connect_to_db()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM revisiones WHERE codigo = %s", (codigo,))
        conn.commit()
        flash('Revision eliminada correctamente')
        
    except Exception as e:
        
        conn.rollback() 
        flash('Oucrrio un error al eliminar la revision: {e}')
        
    finally:
        cur.close()
        conn.close()
    return redirect(url_for('inicio'))


# Endpoint para consultar la lista de todos los clientes
@app.route('/datos/clientes', methods=['GET'])
def consultar_todos_los_clientes():
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("SELECT nif, nombre FROM clientes")
        lista_clientes = cur.fetchall()
       
        return jsonify(lista_clientes)
    except Exception as e:
       
        return jsonify({'mensaje': 'Error al obtener los clientes', 'error': str(e)}), 500
    finally:
        if 'cur' in locals() and cur is not None:
            cur.close()
        if 'conn' in locals() and conn is not None:
            conn.close()

# coches mostrar datos

@app.route('/datos/coches', methods=['GET'])
def consultar_todos_los_coches():
    try:
        conn = connect_to_db()
        cur = conn.cursor() 
        cur.execute("""
            SELECT c.*, cl.nombre as propietario
            FROM coches c
            JOIN clientes cl ON c.nif_cliente = cl.nif
        """)
        lista_coches = cur.fetchall()
        return jsonify(lista_coches)
    except Exception as e:
        return jsonify({'mensaje': 'Error al obtener los coches', 'error': str(e)}), 500
    finally:
        if 'cur' in locals() and cur is not None:
            cur.close()
        if 'conn' in locals() and conn is not None:
            conn.close()

@app.route('/datos/revisiones', methods=['GET'])
def consultar_todas_las_revisiones():
    try:
       
        conn = connect_to_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT r.*, c.marca, c.modelo
            FROM revisiones r
            JOIN coches c ON r.matricula_coche = c.matricula
        """)
        lista_de_revisiones = cur.fetchall()

       
        return jsonify(lista_de_revisiones)

    except Exception as e:
       
        return jsonify({'mensaje':  'Error al obtener las revisiones', 'error': str(e)}), 500
    finally:
       
        if 'cur' in locals() and cur is not None:
            cur.close()
        if 'conn' in locals() and conn is not None:
            conn.close()

#ruta API PARA AGREGAR  clientes consumo de api con flutter
@app.route('/api/clientes', methods=['GET'] )
def api_add_clientes_desde_url():
    try:
       nif = request.args.get('nif')
       nombre = request.args.get('nombre')
       direccion = request.args.get('direccion')
       telefono  = request.args.get('telefono')

       if not all([nif,nombre,direccion,telefono]):
           return jsonify({'error': 'faltan campos obligatorios en base de datos'}), 400
       
       conn = connect_to_db()
       cur = conn.cursor()
       cur.execute("""
             INSERT INTO clientes (nif,nombre,direccion,telefono)
                   VALUES (%s,%s,%s,%s)   
                   """, (nif,nombre,direccion,telefono))
       conn.commit()
       new_id = cur.lastrowid
       cur.close()
       conn.close()
       return jsonify({'messge': 'cliente agregado desde URL', 'id':new_id}), 201
        
    except Exception as e:
      return jsonify({'error':str(e)}), 500
    

#api de agregar coche  con python para registrar en flutter
@app.route('/api/coches', methods=['GET'])
def api_add_coches_desde_url():
    try:
        matricula = request.args.get('matricula')    
        marca = request.args.get('marca')
        modelo = request.args.get('modelo')
        color = request.args.get('color')
        precio = request.args.get('precio')
        nif_cliente = request.args.get('nif_cliente')

        if not all([matricula,marca,modelo,color,precio,nif_cliente]):
             
             return jsonify({'error': 'faltan campos obligatorios'}), 400
        
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO coches (matricula,marca,modelo,color,precio,nif_cliente)
             VALUES (%s, %s, %s, %s, %s, %s)
      """, (matricula,marca,modelo,color,precio,nif_cliente))
        
        conn.commit()
        new_id = cur.lastrowid
        cur.close()
        conn.close()
        return jsonify({'messge': 'Coche agregado desde URL', 'id': new_id }), 201
     
    except Exception as e:
        return jsonify({'error': str(e)}),500
    

@app.route('/api/revisiones', methods=['GET'] )    
def api_add_revisiones_desde_url():
    try:
        # Ya NO se recibe el código desde la URL
        filtro = request.args.get('filtro')
        aceite = request.args.get('aceite')
        frenos = request.args.get('frenos')
        matricula_coche = request.args.get('matricula_coche')

        # La validación ya NO incluye el código
        if not all([filtro, aceite, frenos, matricula_coche]):
            return jsonify({'error':'faltan campos obligatorios' }), 400
        
        conn = connect_to_db()
        cur = conn.cursor()
        # La consulta SQL ya NO inserta el código
        cur.execute("""
             INSERT INTO revisiones (filtro, aceite, frenos, matricula_coche)
                    VALUES (%s, %s, %s, %s)
        """, (filtro, aceite, frenos, matricula_coche))
        conn.commit()
        new_id = cur.lastrowid
        cur.close()
        conn.close()
        return jsonify({'message':'Revision agregada desde la url', 'id': new_id }), 201
    
    except  Exception as e:
        return jsonify({'error':str(e)}), 500

if __name__ ==   '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
from flask import Flask, request, redirect, url_for, render_template

app = Flask(__name__)

# "Base de datos" simulada en la memoria RAM usando un diccionario
usuarios_db = {}


@app.route('/', methods=['GET', 'POST'])
def registro():
    error = None
    if request.method == 'POST':
        # Capturamos los datos del formulario
        nombre_usuario = request.form.get('usuario').strip()
        correo = request.form.get('email').strip()
        clave = request.form.get('password')
        edad = request.form.get('edad')

        # Validación básica
        if not nombre_usuario or not correo or not clave:
            error = "Por favor, completa todos los campos obligatorios."
        elif nombre_usuario in usuarios_db:
            # Verificamos si la clave (el nombre de usuario) ya existe en el diccionario
            error = "Ese nombre de usuario ya está registrado."
        else:
            # Guardamos los datos en nuestro diccionario
            # La clave principal será el nombre de usuario
            usuarios_db[nombre_usuario] = {
                'username': nombre_usuario,
                'email': correo,
                'password': clave,
                'edad': edad if edad else None
            }

            # Redirigimos al perfil
            return redirect(url_for('mostrar_usuario', username=nombre_usuario))

    return render_template('ej03_index.html', error=error)


@app.route('/usuario/<username>')
def mostrar_usuario(username):
    # Buscamos al usuario en nuestro diccionario
    usuario = usuarios_db.get(username)

    # Si alguien intenta entrar a un perfil que no existe, mostramos error
    if not usuario:
        return "<h1>Error 404: Usuario no encontrado</h1>", 404

    # Le pasamos el diccionario del usuario a la plantilla HTML
    return render_template('ej03_saludo.html', usuario=usuario)


if __name__ == '__main__':
    app.run(debug=True)

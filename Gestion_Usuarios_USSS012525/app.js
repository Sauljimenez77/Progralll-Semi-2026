
const $ = id => document.getElementById(id);

let usuarios = [];
let modoFormulario = 'nuevo';

async function peticion(ruta, opciones) {
    const respuesta = await fetch(ruta, opciones);
    const datos = await respuesta.json();

    if (!respuesta.ok) {
        throw new Error(datos.msg || 'Error del servidor');
    }

    return datos;
}

const enviar = datos => peticion('/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(datos)
});

function aviso(mensaje, error = false) {
    $('aviso').textContent = mensaje;
    $('aviso').className = error ? 'error' : 'bien';
}

function prepararNuevoUsuario() {
    const formulario = $('form-usuario');

    formulario.reset();
    formulario.elements.idUsuario.value = '';

    modoFormulario = 'nuevo';

    $('titulo-form').textContent = 'Nuevo usuario';
    $('ayuda-clave').textContent = '(obligatoria)';
    $('editor').hidden = false;
}

async function estado() {
    try {
        const datos = await peticion('/estado');

        $('acceso').hidden = !!datos.usuario;
        $('panel').hidden = !datos.usuario;
        $('salir').hidden = !datos.usuario;

        $('titulo-acceso').textContent = datos.inicial
            ? 'Crear primer usuario'
            : 'Iniciar sesión';

        $('nota-acceso').textContent = datos.inicial
            ? 'No hay usuarios registrados. Crea el primero para comenzar.'
            : 'Ingresa con tu usuario y contraseña.';

        $('form-login').querySelector('button').textContent =
            datos.inicial ? 'Crear primer usuario' : 'Ingresar';

        if (datos.usuario) {
            await listar();
        }

    } catch (error) {
        aviso(error.message, true);
    }
}

$('form-login').addEventListener('submit', async evento => {
    evento.preventDefault();

    const formulario = new FormData(evento.target);

    try {
        const info = await peticion('/estado');

        if (info.inicial) {
            prepararNuevoUsuario();

            $('acceso').hidden = true;
            $('panel').hidden = false;

            $('titulo-form').textContent = 'Registrar primer usuario';

            $('form-usuario').elements.usuario.value =
                formulario.get('usuario');

            $('form-usuario').elements.clave.value =
                formulario.get('clave');

            aviso(
                'Completa el nombre, dirección y teléfono para crear el primer usuario.'
            );

        } else {
            await enviar({
                modulo: 'login',
                usuario: formulario.get('usuario'),
                clave: formulario.get('clave')
            });

            aviso('Sesión iniciada correctamente');
            await estado();
        }

    } catch (error) {
        aviso(error.message, true);
    }
});

$('salir').addEventListener('click', async () => {
    try {
        await enviar({
            modulo: 'salir'
        });

        $('editor').hidden = true;
        modoFormulario = 'nuevo';

        await estado();

    } catch (error) {
        aviso(error.message, true);
    }
});

$('nuevo').addEventListener('click', () => {
    prepararNuevoUsuario();
});

$('cancelar').addEventListener('click', () => {
    $('editor').hidden = true;
    modoFormulario = 'nuevo';
    estado();
});

$('btn-buscar').addEventListener('click', listar);

$('buscar').addEventListener('keydown', evento => {
    if (evento.key === 'Enter') {
        listar();
    }
});

async function listar() {
    try {
        usuarios = await peticion(
            '/usuarios?buscar=' +
            encodeURIComponent($('buscar').value)
        );

        const tabla = $('tabla');
        tabla.replaceChildren();

        if (!usuarios.length) {
            tabla.textContent = 'No se encontraron usuarios.';
            return;
        }

        const tablaHTML = document.createElement('table');
        const encabezado = document.createElement('tr');

        [
            'ID',
            'Usuario',
            'Nombre',
            'Dirección',
            'Teléfono',
            'Acciones'
        ].forEach(texto => {
            const columna = document.createElement('th');
            columna.textContent = texto;
            encabezado.append(columna);
        });

        tablaHTML.append(encabezado);

        usuarios.forEach(usuario => {
            const fila = document.createElement('tr');

            [
                'idUsuario',
                'usuario',
                'nombre',
                'direccion',
                'telefono'
            ].forEach(campo => {
                const columna = document.createElement('td');
                columna.textContent = usuario[campo];
                fila.append(columna);
            });

            const acciones = document.createElement('td');

            const botonEditar = document.createElement('button');
            botonEditar.textContent = 'Editar';
            botonEditar.className = 'pequeno';

            botonEditar.addEventListener('click', () => {
                editarUsuario(usuario.idUsuario);
            });

            const botonEliminar = document.createElement('button');
            botonEliminar.textContent = 'Eliminar';
            botonEliminar.className = 'pequeno peligro';

            botonEliminar.addEventListener('click', () => {
                eliminarUsuario(usuario.idUsuario);
            });

            acciones.append(botonEditar, botonEliminar);
            fila.append(acciones);
            tablaHTML.append(fila);
        });

        tabla.append(tablaHTML);

    } catch (error) {
        aviso(error.message, true);
    }
}

function editarUsuario(id) {
    const usuario = usuarios.find(
        elemento => String(elemento.idUsuario) === String(id)
    );

    if (!usuario) {
        return;
    }

    const formulario = $('form-usuario');

    formulario.reset();

    [
        'idUsuario',
        'usuario',
        'nombre',
        'direccion',
        'telefono'
    ].forEach(campo => {
        formulario.elements[campo].value = usuario[campo];
    });

    modoFormulario = 'modificar';

    $('titulo-form').textContent = 'Editar usuario';
    $('ayuda-clave').textContent =
        '(dejar vacía para conservar)';

    $('editor').hidden = false;
}

async function eliminarUsuario(id) {
    if (!confirm('¿Eliminar este usuario?')) {
        return;
    }

    try {
        const resultado = await enviar({
            modulo: 'usuario',
            accion: 'eliminar',
            idUsuario: id
        });

        aviso(resultado.msg);
        await listar();

    } catch (error) {
        aviso(error.message, true);
    }
}

$('form-usuario').addEventListener('submit', async evento => {
    evento.preventDefault();

    const formulario = new FormData(evento.target);
    const datos = Object.fromEntries(formulario.entries());

    datos.modulo = 'usuario';
    datos.accion = modoFormulario;

    if (modoFormulario === 'nuevo') {
        delete datos.idUsuario;
    }

    if (modoFormulario === 'modificar' && !datos.idUsuario) {
        aviso('No se encontró el usuario que deseas modificar.', true);
        return;
    }

    try {
        const resultado = await enviar(datos);

        aviso(resultado.msg);

        $('editor').hidden = true;
        modoFormulario = 'nuevo';

        $('form-usuario').reset();
        $('form-usuario').elements.idUsuario.value = '';

        const info = await peticion('/estado');

        if (info.inicial === false && !info.usuario) {
            $('acceso').hidden = false;
            $('panel').hidden = true;

            aviso('Primer usuario creado. Ahora inicia sesión.');
            await estado();

        } else {
            await listar();
        }

    } catch (error) {
        aviso(error.message, true);
    }
});

estado();


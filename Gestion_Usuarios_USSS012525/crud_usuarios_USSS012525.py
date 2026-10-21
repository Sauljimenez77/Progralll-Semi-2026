import base64
import hashlib
import hmac
import os
from conexion import Conexion

db = Conexion()
TABLA = 'usuarios_USSS012525'

def cifrar_clave(clave):
    sal = os.urandom(8)
    resumen = hashlib.pbkdf2_hmac('sha256', clave.encode('utf-8'), sal, 150000, dklen=16)
    return 'p$' + base64.urlsafe_b64encode(sal + resumen).decode('ascii').rstrip('=')

def comprobar_clave(clave, guardada):
    if not guardada.startswith('p$'):
        return False
    try:
        contenido = guardada[2:]
        bruto = base64.urlsafe_b64decode(contenido + '=' * (-len(contenido) % 4))
        sal, esperado = bruto[:8], bruto[8:]
        obtenido = hashlib.pbkdf2_hmac('sha256', clave.encode('utf-8'), sal, 150000, dklen=16)
        return hmac.compare_digest(obtenido, esperado)
    except (ValueError, TypeError):
        return False

class crud_usuarios_USSS012525:
    def consultar(self, buscar=''):
        patron = '%' + buscar + '%'
        return db.consultar(f'''SELECT idUsuario, TRIM(usuario) AS usuario, TRIM(nombre) AS nombre,
            TRIM(direccion) AS direccion, TRIM(telefono) AS telefono FROM {TABLA}
            WHERE usuario LIKE %s OR nombre LIKE %s ORDER BY idUsuario DESC''', (patron, patron))

    def verificar_login(self, usuario, clave):
        filas = db.consultar(f'SELECT idUsuario, TRIM(usuario) AS usuario, TRIM(nombre) AS nombre, TRIM(clave) AS clave FROM {TABLA} WHERE usuario=%s', (usuario,))
        if filas and comprobar_clave(clave, filas[0]['clave']):
            return {'idUsuario': filas[0]['idUsuario'], 'usuario': filas[0]['usuario'], 'nombre': filas[0]['nombre']}
        return None

    def hay_usuarios(self):
        return bool(db.consultar(f'SELECT idUsuario FROM {TABLA} LIMIT 1'))

    def administrar(self, datos):
        accion = datos.get('accion')
        if accion not in ('nuevo', 'modificar', 'eliminar'):
            raise ValueError('Acción no permitida')
        if accion == 'eliminar':
            cantidad = db.ejecutar(f'DELETE FROM {TABLA} WHERE idUsuario=%s', (int(datos['idUsuario']),))
            return 'Usuario eliminado' if cantidad else 'No se encontró el usuario'
        usuario = str(datos.get('usuario', '')).strip()
        clave = str(datos.get('clave', ''))
        nombre = str(datos.get('nombre', '')).strip()
        direccion = str(datos.get('direccion', '')).strip()
        telefono = str(datos.get('telefono', '')).strip()
        if not usuario or not nombre or not direccion or not telefono:
            raise ValueError('Completa todos los campos obligatorios')
        if len(usuario)>35 or len(nombre)>85 or len(direccion)>100 or len(telefono)>9:
            raise ValueError('Uno de los campos excede el tamaño permitido')
        if not telefono.isdigit() or len(telefono) not in (8, 9):
            raise ValueError('El teléfono debe contener 8 o 9 dígitos')
        if accion == 'nuevo':
            if not clave or len(clave)<6:
                raise ValueError('La contraseña debe tener al menos 6 caracteres')
            db.ejecutar(f'INSERT INTO {TABLA}(usuario,clave,nombre,direccion,telefono) VALUES (%s,%s,%s,%s,%s)',
                (usuario,cifrar_clave(clave),nombre,direccion,telefono))
            return 'Usuario registrado correctamente'
        identificador = int(datos['idUsuario'])
        if clave:
            if len(clave)<6:
                raise ValueError('La nueva contraseña debe tener al menos 6 caracteres')
            db.ejecutar(f'UPDATE {TABLA} SET usuario=%s, clave=%s, nombre=%s, direccion=%s, telefono=%s WHERE idUsuario=%s',
                (usuario,cifrar_clave(clave),nombre,direccion,telefono,identificador))
        else:
            db.ejecutar(f'UPDATE {TABLA} SET usuario=%s, nombre=%s, direccion=%s, telefono=%s WHERE idUsuario=%s',
                (usuario,nombre,direccion,telefono,identificador))
        return 'Usuario modificado correctamente'

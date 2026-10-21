from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from http.cookies import SimpleCookie
import json
import secrets
import time
from pathlib import Path
import mysql.connector
from conexion import preparar_base
from crud_usuarios_USSS012525 import crud_usuarios_USSS012525

PORT = 3000
RAIZ = Path(__file__).resolve().parent
crudUsuarios = crud_usuarios_USSS012525()
sesiones = {}

class miServidor(SimpleHTTPRequestHandler):
    def responder(self, estado, datos, cookie=None):
        contenido = json.dumps(datos, ensure_ascii=False).encode('utf-8')
        self.send_response(estado)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        if cookie:
            self.send_header('Set-Cookie', cookie)
        self.send_header('Content-Length', str(len(contenido)))
        self.end_headers()
        self.wfile.write(contenido)

    def usuario_actual(self):
        cookies = SimpleCookie()
        try:
            cookies.load(self.headers.get('Cookie', ''))
        except Exception:
            return None
        token = cookies.get('sesion')
        if not token:
            return None
        sesion = sesiones.get(token.value)
        if not sesion or sesion['vence'] < time.time():
            sesiones.pop(token.value, None)
            return None
        return sesion['usuario']

    def do_POST(self):
        try:
            origen = self.headers.get('Origin')
            if origen and origen not in (f'http://localhost:{PORT}', f'http://127.0.0.1:{PORT}'):
                return self.responder(403, {'msg': 'Origen no permitido'})
            longitud = int(self.headers.get('Content-Length', '0'))
            if longitud < 1 or longitud > 30000:
                return self.responder(400, {'msg': 'Datos no válidos'})
            datos = json.loads(self.rfile.read(longitud).decode('utf-8'))
            modulo = datos.get('modulo')
            if modulo == 'login':
                usuario = crudUsuarios.verificar_login(str(datos.get('usuario','')).strip(), str(datos.get('clave','')))
                if not usuario:
                    return self.responder(401, {'msg': 'Usuario o contraseña incorrectos'})
                token = secrets.token_urlsafe(32)
                sesiones[token] = {'usuario': usuario, 'vence': time.time()+28800}
                return self.responder(200, {'msg': 'Bienvenido', 'usuario': usuario}, f'sesion={token}; HttpOnly; SameSite=Strict; Path=/')
            if modulo == 'salir':
                cookies = SimpleCookie()
                cookies.load(self.headers.get('Cookie',''))
                if cookies.get('sesion'):
                    sesiones.pop(cookies['sesion'].value, None)
                return self.responder(200, {'msg': 'Sesión cerrada'}, 'sesion=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0')
            if modulo == 'usuario':
                if not self.usuario_actual() and not (datos.get('accion') == 'nuevo' and not crudUsuarios.hay_usuarios()):
                    return self.responder(401, {'msg': 'Inicia sesión primero'})
                resultado = crudUsuarios.administrar(datos)
                return self.responder(200, {'msg': resultado})
            return self.responder(400, {'msg': 'Módulo desconocido'})
        except (ValueError, KeyError, TypeError) as e:
            self.responder(400, {'msg': str(e)})
        except mysql.connector.IntegrityError:
            self.responder(409, {'msg': 'El nombre de usuario ya existe'})
        except Exception as e:
            print('Error del servidor:', e)
            self.responder(500, {'msg': 'Error de base de datos o del servidor; revisa la terminal'})

    def do_GET(self):
        url = urlparse(self.path)
        qs = parse_qs(url.query)
        try:
            if url.path == '/estado':
                return self.responder(200, {'inicial': not crudUsuarios.hay_usuarios(), 'usuario': self.usuario_actual()})
            if url.path == '/usuarios':
                if not self.usuario_actual():
                    return self.responder(401, {'msg': 'Inicia sesión primero'})
                return self.responder(200, crudUsuarios.consultar(qs.get('buscar',[''])[0]))
            if url.path == '/':
                self.path = '/index.html'
            elif url.path == '/vistas':
                nombre = qs.get('form',[''])[0]
                if nombre not in ('usuarios','busqueda_usuarios','login'):
                    return self.send_error(404)
                self.path = f'/modulos/{nombre}.html'
            elif url.path not in ('/index.html','/app.js','/estilos.css'):
                return self.send_error(404)
            return super().do_GET()
        except Exception as e:
            print('Error:', e)
            return self.responder(500, {'msg': 'No se pudo conectar con MySQL'})

if __name__ == '__main__':
    import os
    os.chdir(RAIZ)
    try:
        preparar_base()
    except Exception as e:
        print('ERROR DE MYSQL:', e)
        raise SystemExit(1)
    print(f'Servidor funcionando: http://localhost:{PORT}')
    HTTPServer(('localhost', PORT), miServidor).serve_forever()

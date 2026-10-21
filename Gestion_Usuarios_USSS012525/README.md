# Parcial II - Gestión de Usuarios USSS012525

Proyecto hecho con **Python nativo**, sin Django ni Flask, siguiendo la separación de archivos de la rama ComputoII del profesor: `server.py`, `conexion.py`, módulo CRUD, `index.html`, `app.js`.

## Instrucciones en Windows

1. Descomprime el ZIP y abre la carpeta en VS Code.
2. Inicia **MySQL** desde XAMPP.
3. En la terminal, dentro de la carpeta que contiene `server.py`, ejecuta:

   py -3.14 -m pip install -r requirements.txt
   py -3.14 server.py

4. Abre **http://localhost:3000**. El servidor crea la base y tabla automáticamente. Alternativamente puedes importar `db.sql` en phpMyAdmin.
5. Si no existen usuarios, registra el primero desde la pantalla inicial. Luego inicia sesión con esas credenciales.
6. Para detener el servidor: Ctrl+C.

## Si MySQL no conecta

Abre `conexion.py` y verifica `CONFIG` (usuario `root`, contraseña vacía en XAMPP por defecto). El código prueba los puertos 3307 y 3306. Si MySQL usa otro puerto, cámbialos en `conectar()` y `preparar_base()`.

## Relación con el parcial

1. `db.sql` / `preparar_base()` crean `db_academica.usuarios_USSS012525` con columnas CHAR solicitadas.
2. `index.html` y `app.js` capturan los datos y los envían con `fetch()` a `server.py`.
3. `crud_usuarios_USSS012525.py` contiene la clase `crud_usuarios_USSS012525` y sus métodos `consultar`, `administrar` y `verificar_login`.
4. Buscar, editar y eliminar desde la tabla de usuarios.
5. Login aparece al abrir el servidor. La primera vez se permite registrar el primer usuario.

Contraseñas: se guarda un resumen PBKDF2 con sal de 34 caracteres para ajustarse a `CHAR(35)`, no el texto de la contraseña. Consultas SQL con parámetros para evitar inyección SQL.

Nota: se usa `mysql-connector-python` para conectar MySQL, igual que el ejemplo del profesor; el servidor web usa solo la biblioteca estándar de Python.

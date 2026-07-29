# Gestión de Cuentas Corrientes

Esta aplicación es un sistema desarrollado con **Streamlit** y **MySQL** para la administración de clientes y sus movimientos de cuenta corriente.

## Requisitos Previos

- Python 3.x instalado.
- Servidor MySQL instalado y corriendo (se recomienda configurar en puerto `3307`).

## Configuración paso a paso

### 1. Clonar o descargar el repositorio
Asegúrate de estar en la carpeta raíz del proyecto:
`C:\Users\Win_11\Documents\Facultad\Soporte\TareaSQL-Server`

### 2. Base de Datos
1. Abre tu gestor de base de datos (MySQL Workbench o similar).
2. Crea una base de datos vacía llamada `GestionClientesDB`:
   ```sql
   CREATE DATABASE GestionClientesDB;
   ```
3. Asegúrate de conocer el puerto, usuario y contraseña de tu servidor MySQL.

### 3. Entorno Virtual y Dependencias
Desde la terminal en la carpeta raíz del proyecto:

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
.\venv\Scripts\Activate.ps1

# Instalar dependencias
cd streamlit_app
pip install -r requirements.txt
```

### 4. Configuración del archivo .env
Dentro de la carpeta `streamlit_app/`, encontrarás un archivo llamado `.env`. Si no existe, créalo con el siguiente contenido y ajusta los valores a tu entorno:

```text
DB_HOST=localhost
DB_PORT=3307
DB_USER=tu_usuario_de_mysql
DB_PASSWORD=tu_contraseña_de_mysql
DB_NAME=GestionClientesDB
```

### 5. Ejecución
Para iniciar la aplicación:

```bash
# Asegúrate de estar dentro de la carpeta streamlit_app
streamlit run main.py
```

Al iniciar por primera vez, la aplicación ejecutará automáticamente `init_db.py` para crear las tablas necesarias (`Clientes`, `CuentaCorriente`, `Movimientos`) si aún no existen.

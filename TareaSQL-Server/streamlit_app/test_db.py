from db_connection import get_db_connection

conn = get_db_connection()
if conn:
    print("Conexión exitosa!")
    conn.close()
else:
    print("Fallo la conexión.")

from db_connection import get_db_connection

def check_and_create_tables():
    """Verifica si las tablas existen y las crea si no es así."""
    conn = get_db_connection()
    if not conn:
        print("No se pudo conectar a la BD para inicializar tablas.")
        return
    
    cursor = conn.cursor()
    
    # Lista de tablas a crear
    tables = [
        """CREATE TABLE IF NOT EXISTS Clientes (
            NumeroCliente INT PRIMARY KEY,
            Nombre VARCHAR(100) NOT NULL,
            CUIT VARCHAR(20) NOT NULL
        );""",
        """CREATE TABLE IF NOT EXISTS CuentaCorriente (
            NumeroCuenta INT AUTO_INCREMENT PRIMARY KEY,
            NumeroCliente INT NOT NULL,
            Fecha DATE NOT NULL,
            NroComprobante VARCHAR(20) NOT NULL,
            Detalle VARCHAR(100),
            FOREIGN KEY (NumeroCliente) REFERENCES Clientes(NumeroCliente)
        );""",
        """CREATE TABLE IF NOT EXISTS Movimientos (
            ID_Movimiento INT AUTO_INCREMENT PRIMARY KEY,
            NumeroCuenta INT NOT NULL,
            Fecha DATE NOT NULL,
            NroComprobante VARCHAR(20) NOT NULL,
            Detalle VARCHAR(100),
            Debe DECIMAL(18, 2) DEFAULT 0,
            Haber DECIMAL(18, 2) DEFAULT 0,
            FOREIGN KEY (NumeroCuenta) REFERENCES CuentaCorriente(NumeroCuenta)
        );"""
    ]
    
    for table_sql in tables:
        cursor.execute(table_sql)
        
    conn.commit()
    cursor.close()
    conn.close()
    print("Tablas verificadas/creadas correctamente.")

# Project Agents & Components

This project is a Streamlit application designed for managing customer current accounts, interacting with a MySQL database.

## Components

### 1. Database Connector (`streamlit_app/db_connection.py`)

- **Role**: Manages the secure connection to the MySQL database.
- **Functionality**: Reads configuration from `.env`, establishes the connection, and handles errors.

### 2. Export Utility (`streamlit_app/export_utils.py`)

- **Role**: Handles the generation of reports in different formats.
- **Functionality**:
  - Generates Excel files (`.xlsx`) using `xlsxwriter`.
  - Generates PDF reports (`.pdf`) using `fpdf`.
  - Handles buffering for direct browser downloads in Streamlit.

### 3. Main Application (`streamlit_app/main.py`)
- **Role**: The main interface for the user.
- **Functionality**:
    - Connects to the database using `db_connection.py`.
    - Automatically initializes the database schema using `init_db.py`.
    - Displays a customer selection interface.
    - Queries the database for customer movements (joins `Clientes`, `CuentaCorriente`, `Movimientos`).
    - Calculates the current account balance.
    - Triggers export functionality via `export_utils.py`.
    - Generates monthly billing reports using interactive `plotly` charts.

### 4. Database Initializer (`streamlit_app/init_db.py`)
- **Role**: Automatically sets up the database schema upon application startup.
- **Functionality**:
    - Ensures tables (`Clientes`, `CuentaCorriente`, `Movimientos`) exist and creates them if not.

## Setup Instructions


Ensure you have a `.env` file in `streamlit_app/` with the following configuration:

```text
DB_HOST=localhost
DB_PORT=3307
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=gestionclientesdb
```

Run the application with:

```bash
cd streamlit_app
streamlit run main.py
```

import streamlit as st
import pandas as pd
import os
import plotly.express as px
from db_connection import get_db_connection
from export_utils import export_to_excel, export_to_pdf
from init_db import check_and_create_tables

# Inicializar tablas al arrancar la app
check_and_create_tables()

st.title("Gestión de Cuenta Corriente")

conn = get_db_connection()

if conn:
    # 1. Obtener lista de clientes
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT NumeroCliente, Nombre FROM Clientes")
    clientes = cursor.fetchall()
    cursor.close()

    if not clientes:
        st.warning("No hay clientes en la base de datos.")
    else:
        cliente_dict = {c['Nombre']: c['NumeroCliente'] for c in clientes}
        nombre_seleccionado = st.selectbox("Seleccione un cliente:", list(cliente_dict.keys()))
        cliente_id = cliente_dict[nombre_seleccionado]

        # 2. Consultar movimientos
        query = """
            SELECT m.Fecha, m.NroComprobante, m.Detalle, m.Debe, m.Haber
            FROM Movimientos m
            JOIN CuentaCorriente cc ON m.NumeroCuenta = cc.NumeroCuenta
            WHERE cc.NumeroCliente = %s
            ORDER BY m.Fecha DESC
        """
        # Ejecutar consulta usando pandas
        df = pd.read_sql(query, conn, params=[cliente_id])

        st.write(f"Movimientos de: {nombre_seleccionado}")
        st.dataframe(df)

        # 3. Calcular saldo
        if not df.empty:
            saldo = df['Debe'].sum() - df['Haber'].sum()
            st.metric("Saldo Actual", f"${saldo:,.2f}")
            
            # Export buttons
            st.subheader("Exportar datos")
            col1, col2 = st.columns(2)
            
            excel_buffer, excel_name = export_to_excel(df, nombre_seleccionado)
            col1.download_button(
                "Descargar Excel", 
                data=excel_buffer, 
                file_name=os.path.basename(excel_name), 
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            pdf_buffer, pdf_name = export_to_pdf(df, nombre_seleccionado)
            col2.download_button(
                "Descargar PDF", 
                data=pdf_buffer, 
                file_name=os.path.basename(pdf_name), 
                mime="application/pdf"
            )

            # Tarea 4: Botón para reporte mensual de facturación
            st.subheader("Reportes")
            if st.button("Ver Reporte Mensual de Facturación"):
                query_reporte = """
                    SELECT 
                        DATE_FORMAT(Fecha, '%Y-%m') AS Periodo, 
                        SUM(Debe) AS TotalFacturado
                    FROM Movimientos
                    WHERE Debe > 0
                    GROUP BY Periodo
                    ORDER BY Periodo;
                """
                
                # Ejecutar consulta usando pandas
                df_reporte = pd.read_sql(query_reporte, conn)
                
                if not df_reporte.empty:
                    st.subheader("Monto Facturado por Periodo")
                    
                    # Crear gráfico interactivo con Plotly
                    fig = px.bar(
                        df_reporte, 
                        x='Periodo', 
                        y='TotalFacturado',
                        labels={'Periodo': 'Mes (Año-Mes)', 'TotalFacturado': 'Monto Facturado ($)'},
                        title="Facturación Mensual",
                        text_auto='.2s' 
                    )
                    fig.update_traces(hoverinfo='x+y')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No hay datos de facturación para mostrar.")
        else:
            st.write("No hay movimientos para este cliente.")

    conn.close()
else:
    st.error("No se pudo conectar a la base de datos.")

import streamlit as st 
import pandas as pd
import numpy as np
from datetime import datetime,timedelta
from datetime import date
import secrets
import math
from dateutil.relativedelta import relativedelta
from scipy import stats
import psycopg2
import psycopg2.extras as extras

from backtesting.utils_backtesting import modelo, backtesting

import os
# cargamos dotenv
from dotenv import load_dotenv
load_dotenv()

# el streamlit 
with open('styles/style_info.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


# titulo 
st.markdown("<h1 style='text-align: center;'> BACKTESTING 🕗🔙</h1>", unsafe_allow_html=True)

# Add white space
st.write("\n\n")
st.write("\n\n")


# abrimos los resultados de backtesintg guardados y pintamos
backtest_guardado= pd.read_csv("backtesting/backt_result_5_years.csv")

first_c, second_c, third_c =st.columns(3)

first_c.metric("N de Muestras", round(backtest_guardado["n_muestras"][0]))
second_c.metric("% de acierto al SP500", round(backtest_guardado["%_acierto_sp500"][0],2))

third_c.metric("% de acierto a un fondo",round(backtest_guardado["%_acierto_fondo"][0],2))

# second row 
first_c.metric("% aciertos cartera aleatoria", round(backtest_guardado["%_cartera_aleatoria"][0],2))
second_c.metric("% alpha positivo", round(backtest_guardado["%_alpha"][0],2))
third_c.metric("media de alpha",round(backtest_guardado["media_alpha"][0],2))

# creamos un info para añadir los datos con los que hemos calculado este backtesting

# info bottom para explicar el proceso
info_button = st.checkbox("ℹ️")
# Display information when the button is clicked
if info_button:
    st.markdown("""
                - Los datos con los que hemos calculado este backtesting son:
                    - 5 años desde la fecha de hoy
                    - una comision de  
                    - xxxxx
                    - yyyyy
                    """)
st.markdown("---")





# para centrar el botton de mas
st.markdown("""
  <style>
  div.stButton {text-align:center}
  </style>""", unsafe_allow_html=True)


if st.checkbox(':heavy_plus_sign:'):

    st.markdown("#### Escoge tus preferencias")

    st.write("\n\n")
    st.write("\n\n")


    st.markdown("##### 1. Fechas")

    col1, col2 = st.columns(2)
    
    fecha_comienzo = col1.date_input("Fecha Comienzo", value=None)
    fecha_final = col2.date_input("Fecha Final", value=None)

    dias_back =  col1.number_input('Dias para el backtesting',value = 10)

    comision = col2.number_input('comision',value = 0.001)

    porc_minimo = col1.number_input('Porcentaje minimo',value = 5)



    if st.button("Correr"):

        # probamos que la conexion funciona!
        conn = psycopg2.connect(
                host=os.getenv("HOST_TFM") ,
                user =os.getenv("USER_TFM") ,
                password=os.getenv("PASSWORD_TFM"),
                port=os.getenv("PORT_TFM"),
                database=os.getenv("DATABASE_TFM")
        )

        cursor = conn.cursor()

        # Tabla 1 

        sql = """SELECT * FROM precios_sp500
                     WHERE date >= %s
                     AND date <= %s"""
        cursor.execute(sql, (fecha_comienzo,fecha_final))

        precios = pd.DataFrame(cursor.fetchall())
        colnames = [desc[0] for desc in cursor.description]

        precios.columns = colnames

        # tabla 2 

        sql = """SELECT * FROM fondo_referencia  
                    WHERE fecha >= %s 
                    AND fecha <= %s"""


        cursor.execute(sql, (fecha_comienzo,fecha_final))

        precios_fondo = pd.DataFrame(cursor.fetchall())
        colnames = [desc[0] for desc in cursor.description]

        precios_fondo.columns = colnames

        # cerrar conexiones
        cursor.close()
        conn.close()


        # empeiza el backtesting 
        precios_acciones = precios[['fs_perm_regional_id','close_adjusted','date']]

        precios_acciones = precios_acciones.pivot_table(values='close_adjusted', index=precios_acciones.date, columns='fs_perm_regional_id', aggfunc='first')
        precios_acciones = precios_acciones.fillna(method='ffill')
        precios_acciones = precios_acciones.fillna(method='bfill')

        precios_fondo.index = precios_fondo.fecha
        precios_fondo = precios_fondo['lu0076314649']

        precios_indice = precios_acciones['SP50-USA']
        precios_acciones = precios_acciones.drop(['SP50-USA'],axis=1)


        fechas = precios_indice.index
        tabla_resumen = pd.DataFrame(columns=['rentabilidad_periodo', 'rentabilidad_benchmark_p', 'rentabilidad_fondo','rentabilidad_aleatoria', 'alpha', 'acierto_benchmark', 'acierto_fondo','acierto_aleatorio','acierto_alpha'],index=fechas)

        for fecha in fechas:
            #fecha = fecha.strftime('%Y-%m-%d')
            try:
                a, b, c, d, e, f, g, h, k = backtesting(fecha, comision, dias_back, porc_minimo, precios_acciones, precios_indice, precios_fondo)
                tabla_resumen.loc[fecha]['rentabilidad_periodo'] = a
                tabla_resumen.loc[fecha]['rentabilidad_benchmark_p'] = b
                tabla_resumen.loc[fecha]['rentabilidad_fondo'] = c
                tabla_resumen.loc[fecha]['rentabilidad_aleatoria'] = d
                tabla_resumen.loc[fecha]['alpha'] = h
                tabla_resumen.loc[fecha]['acierto_benchmark'] = e
                tabla_resumen.loc[fecha]['acierto_fondo'] = f
                tabla_resumen.loc[fecha]['acierto_aleatorio'] = g
                tabla_resumen.loc[fecha]['acierto_alpha'] = k
                
            except:
                pass

        # tabla_resumen.to_excel('tabla_resumen.xlsx')

        resumen = pd.DataFrame(columns=['número muestras', 'p. acietos sobre SP500', 'p. acietos sobre fondo', 'p. acietos sobre cartera aleatoria','p. alpha positivo','media alphas'],index=['modelo'])
        resumen['número muestras']['modelo'] = len(fechas)
        resumen['p. acietos sobre SP500']['modelo'] = tabla_resumen['acierto_benchmark'].sum()/len(fechas)
        resumen['p. acietos sobre fondo']['modelo'] = tabla_resumen['acierto_fondo'].sum()/len(fechas)
        resumen['p. acietos sobre cartera aleatoria']['modelo'] = tabla_resumen['acierto_aleatorio'].sum()/len(fechas)
        resumen['p. alpha positivo']['modelo'] = tabla_resumen['acierto_alpha'].sum()/len(fechas)
        resumen['media alphas']['modelo'] = tabla_resumen['alpha'].mean()



        resumen.columns = ["n_muestras","%_acierto_sp500","%_acierto_fondo","%_cartera_aleatoria","%_alpha","media_alpha"]
     

            
        first_c_dos, second_c_dos, third_c_dos =st.columns(3)

        first_c_dos.metric("N de Muestras int ", round(resumen["n_muestras"][0],2))
        second_c_dos.metric("ROE int", round(resumen["%_acierto_sp500"][0],2))
        third_c_dos.metric("PE Ratio int",round(resumen["%_acierto_fondo"][0],2))

        # second row 
        first_c_dos.metric("% aciertos cartera aleatoria int", round(resumen["%_cartera_aleatoria"][0],2))
        second_c_dos.metric("% alpha positivo int", round(resumen["%_alpha"][0],2))
        third_c_dos.metric("media de alpha int",round(resumen["media_alpha"][0],2))

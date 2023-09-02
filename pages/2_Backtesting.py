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
import json
import requests


import os
# cargamos dotenv
from dotenv import load_dotenv
load_dotenv()

#borarr 
import pandas as pd

#-------------

# Cargamos el Css de la pagina 
with open('styles/style_info.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


# titulo 
st.markdown("<h1 style='text-align: center;'> BACKTESTING 🕗🔙</h1>", unsafe_allow_html=True)

# Add white space
st.write("\n\n")
st.write("\n\n")


# abrimos los resultados de backtesintg guardados y pintamos
backtest_guardado= pd.read_csv("fundamanetals/back_result_5_years.csv")

first_c, second_c, third_c =st.columns(3)

first_c.metric("N de Muestras", round(backtest_guardado["n_muestras"][0]))
second_c.metric("% de aciertos al SP500", round(backtest_guardado["%_acierto_sp500"][0],2))
third_c.metric("% de acierto a un fondo",round(backtest_guardado["%_acierto_fondo"][0],2))

# second row 
first_c.metric("% aciertos cartera aleatoria", round(backtest_guardado["%_acierto_cartera_aleatoria"][0],2))
second_c.metric("% alpha positivo", round(backtest_guardado["%_alpha"][0],2))
third_c.metric("media de alpha",round(backtest_guardado["media_alpha"][0],2))

# creamos un info para añadir los datos con los que hemos calculado este backtesting

# info bottom para explicar el proceso
info_button = st.checkbox("ℹ️")
# Mostrar la info cuando el boton es pulsado
if info_button:
    st.markdown("""
                - Los datos con los que hemos calculado este backtesting son:
                    - Precios desde el 01/01/2016 hasta 31/09/2023
                    - una comision del 0,001  
                    - Cada activo podra tener como minimo un 5% en cartera
                    
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


    # recogemos los inputs del cliente para el backtesting

    col1, col2 = st.columns(2)
    
    fecha_comienzo = col1.date_input("Fecha Comienzo", value=None)
    fecha_final = col2.date_input("Fecha Final", value=None)

    #dias_back =  col1.number_input('Dias para el backtesting',value = 10)
    dias_back = 10
    comision = col2.number_input('comision en porcentaje',value = 0.1)

    porc_minimo = col1.number_input('Porcentaje minimo',value = 5)
    


    if st.button("Correr"):

        # Llamamos al endpoints de Backtesting para calcularlo con los inputs
        # del cliente. 

        url = os.getenv("BACKTESTINGS_RESULTS")

        comision = comision /100
        payload = json.dumps({
                                "dias": dias_back,
                                "comision": comision,
                                "porcentaje": porc_minimo,
                                "fecha_comienzo": str(fecha_comienzo),
                                "fecha_final": str(fecha_final)
                                })
        
      
        
        headers = {
                    'Content-Type': 'application/json'
                    }

        response = requests.request("POST", url, headers=headers, data=payload)
        response_backtest = eval(json.loads(response.text))

        # creamos cuadros para completarlos con los resultados de las APIS
            
        first_c_dos, second_c_dos, third_c_dos =st.columns(3)

        first_c_dos.metric("N de Muestras int ", round(response_backtest[0],2))
        second_c_dos.metric("ROE int", round(response_backtest[1],2))
        third_c_dos.metric("PE Ratio int",round(response_backtest[2],2))

        # second row 
        first_c_dos.metric("% aciertos cartera aleatoria int", round(response_backtest[3],2))
        second_c_dos.metric("% alpha positivo int", round(response_backtest[4],2))
        third_c_dos.metric("media de alpha int",round(response_backtest[5],2))

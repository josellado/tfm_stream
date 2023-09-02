import streamlit as st 
import json 
import pandas as pd 
import requests
import os
# cargamos dotenv
from dotenv import load_dotenv
load_dotenv()


st.markdown("<h1 style='text-align: center;'> RANKING 🏆</h1>", unsafe_allow_html=True)

# 1 primera llamada al endpoint consulta rankeo para consultar todas las fechas
# disponibiles del rankeo 


url = os.getenv("RANKEO_ENDPOINT")

payload = ""
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

listado_comphias=json.loads(response.text)

#ordenamos
order_lista =  sorted(listado_comphias, reverse=True)

fechas_rankeo = st.selectbox("Fecha para Visualizar Rankeo", order_lista)


if fechas_rankeo != '':

    # 2 llamaamda al endpoint consulta_rankeo, esta vez un metodo
    # post para que nos devuelva el orden del rankeo en base a la fecha
    # escogida 
    
    url = os.getenv("RANKEO_ENDPOINT")
    
    payload = json.dumps({
    "fecha_backtesing": f"{fechas_rankeo}"
    })
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    ranking = response.text
    rankeo_df =  pd.read_json(eval(ranking), orient='records')

    # lo añadimos a streamlit 
    emoji = "🔝"
    emoji2 = "💣"


    
    st.markdown("<h2 style='text-align:center;'>OUR 🔝 20 CHOICES! 💣 💰</h2>", unsafe_allow_html=True)

    st.write("\n\n")
    st.write("\n\n")

    # enseñamos los primeros 20 
    df_rankeo_top20 =rankeo_df[:20]
    df_rankeo_top20["name_completo"] = df_rankeo_top20["company_name"] + "-" + df_rankeo_top20["ticker_region"]

    # Split the Streamlit page into two columns
    left_column, right_column = st.columns(2)

    # Display the first three items in the left column
    #left_column.header("First Three Items")
    for i, item in enumerate(df_rankeo_top20['name_completo'][:10], start=1):
        left_column.write(f"{i}. {item}")
    # Display the last two items in the right column
    for i, item in enumerate(df_rankeo_top20['name_completo'][10:], start=11):
        right_column.write(f"{i}. {item}")



    st.markdown("---")

    if st.checkbox(':heavy_plus_sign: listado'):
        
        resto_rankeo= rankeo_df[["company_name","ticker_region"]][20:]
        st.markdown(resto_rankeo.style.hide(axis="index").to_html(), unsafe_allow_html=True)

      



#df.set_index(df.columns, inplace=True)

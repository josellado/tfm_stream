import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import fundamentalanalysis as fa
from datetime import datetime
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import requests
import json
# cargamos dotenv
from dotenv import load_dotenv
load_dotenv()

# cargamos las funciones 
from fundamanetals.finan_model_prep import load_data_fin_model_prep,get_price_data_fig

from fundamanetals.tablas_fa import get_balance_sheet,\
                                                get_inconme_statement, \
                                                get_cash_flow_statement 



# las Api keys del proyecto 
# import api key for stock data
FA_API_KEY = os.getenv("financial_model_key")


st.set_page_config(page_title="Analisis Fundamental", layout="wide")


with open('styles/style_info.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


# creamos df donde metemos datos
TIME_DIFFS = {
    "1 week": pd.DateOffset(weeks=1),
    "1 month": pd.DateOffset(months=1),
    "3 months": pd.DateOffset(months=3),
    "1 year": pd.DateOffset(years=1),
    "3 years": pd.DateOffset(years=3),
    "5 years": pd.DateOffset(years=5)
}

# 1 llamada 
# devuelve el listado de tickers para obtener la info de FMP
url = os.getenv("LISTA_INFO")

payload = {}
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

listado_comphias=json.loads(response.text)
listado_comphias.insert(0, " ")

#listado_comphias = [" ","AAPL","MSFT","AMZN","NVDA","GOOGL","META","TSLA"]
ticker = st.selectbox("Listado de las compañias", listado_comphias)


# Hasta que no se introduce un ticker no hace nada

if ticker != " ":


    
    #            FINANCIAL MODEL PREP!
   
    
    # aqui cargamos todo finacial model prep. 
    # contamos con muchos datos.

    stock_data = load_data_fin_model_prep(ticker)

    info = stock_data["info"]
    try:
        currency = info["currency"]
    except:
        currency= 'USD'

    try:
        website = info["website"]
        info_companhia = info["description"]
        companyName=info['companyName']
        symbol=info['symbol']

    except:
        website = "DATA NO AVAILABLE"
        info_companhia = "DATA NO AVAILABLE"
        companyName = "DATA NO AVAILABLE"
        symbol= "DATA NO AVAILABLE"

    # ratios 

    key_metrics_annually = stock_data["key_metrics_annually"]

    # Nos quedamos con el cierre. 
    close = stock_data["stock_closings"]
    close.index =  pd.to_datetime(close.index)
    latest_price = close.iloc[-1]

    # Title
    st.title(f"{companyName} ({symbol})")


    # should all be displayed on the same row
    change_columns = st.columns(len(TIME_DIFFS))
    today = pd.to_datetime("today").floor("D")

    for i, (name, difference) in enumerate(TIME_DIFFS.items()):

        # go back to the date <difference> ago
        date = (today - difference)

        # Si no tenemos datos seleccionamos el primero
        if date < close.index[0]:
            date = close.index[0]

        #en el caso de que caiga en fin de semana
        closest_date_index = np.abs(close.index - date)

        closest_date_index = closest_date_index.argmin()

        previous_price = close[closest_date_index]

        # calculamos el cambio porcentual
        change = 100*(latest_price - previous_price) / previous_price
        # show red if negativo, green if positivo
        color = "red" if change < 0 else "green"

        # color can be displayed as :red[this will be red] in markdown
        change_columns[i].markdown(f"{name}: :{color}[{round(change, 2)}%]")

    # info de la empresa
    st.write(info_companhia)

    #Company website
    st.write("**Website:** " + website)
    st.markdown("---")


    # fundamentals view 
    first_c, second_c, third_c, fourth_c=st.columns(4)

    if len(key_metrics_annually) != 0:

        first_c.metric("Current Ratio", round(key_metrics_annually.loc["currentRatio"][0], 2) if key_metrics_annually.loc["currentRatio"][0] is not None else None)
        second_c.metric("ROE", round(key_metrics_annually.loc["roe"][0], 2) if key_metrics_annually.loc["roe"][0] is not None else None)
        third_c.metric("PE Ratio", round(key_metrics_annually.loc["peRatio"][0], 2) if key_metrics_annually.loc["peRatio"][0] is not None else None)
        fourth_c.metric("Payout Ratio", round(key_metrics_annually.loc["payoutRatio"][0], 2) if key_metrics_annually.loc["payoutRatio"][0] is not None else None)


        first_c.metric("Revenue per Share", round(key_metrics_annually.loc["revenuePerShare"][0], 2) if key_metrics_annually.loc["revenuePerShare"][0] is not None else None)
        second_c.metric("Cash per Share", round(key_metrics_annually.loc["cashPerShare"][0], 2) if key_metrics_annually.loc["cashPerShare"][0] is not None else None)
        third_c.metric("Debt to Equity", round(key_metrics_annually.loc["debtToEquity"][0], 2) if key_metrics_annually.loc["debtToEquity"][0] is not None else None)
        fourth_c.metric("Debt to Assets", round(key_metrics_annually.loc["debtToAssets"][0], 2) if key_metrics_annually.loc["debtToAssets"][0] is not None else None)

    else: 

        first_c.metric("Current Ratio", "Data Not Available")
        second_c.metric("ROE", "Data Not Available")
        third_c.metric("PE Ratio", "Data Not Available")
        fourth_c.metric("Payout Ratio", "Data Not Available")


        first_c.metric("Revenue per Share", "Data Not Available")
        second_c.metric("Cash per Share", "Data Not Available")
        third_c.metric("Debt to Equity", "Data Not Available")
        fourth_c.metric("Debt to Assets", "Data Not Available")

    st.markdown("---")
    

    #-----------------------------------------------------------------------
        
    # establecemos el tamaño de cada columna

    overview_columns = st.columns([1, 3])

    # first column, basic information

    overview_columns[0].markdown("<br/>"*4, unsafe_allow_html=True)

    # text will be displayed and key is the key in info
    try:
        for text, key in [
            ("Current price", "price"),
            ("Country", "country"),
            ("Exchange", "exchange"),
            ("Sector", "sector"),
            ("Industry", "industry"),
            ("Full time employees", "fullTimeEmployees")
        ]:
            overview_columns[0].markdown("")
            overview_columns[0].markdown(f"- {text}: **{info[key]}**")
    except:
        pass

    # second column el grafico

    graph_placeholder = overview_columns[1].empty()

    graph_placeholder.plotly_chart(go.Figure(), use_container_width=True)

    # options that will dictate the graph:

    # botones para elegir el plazo del grafico
    time_window_key = overview_columns[1].radio("Time window", TIME_DIFFS.keys(), index=len(TIME_DIFFS)-1, horizontal=True)
    # select the value from the key, i.e. the pd.DateOffset
    time_window = TIME_DIFFS[time_window_key]

    # slider para el moving average de 2 a 500, por defecto 30
    moving_average = overview_columns[1].slider("Moving average", min_value=2, max_value=500, value=30)


    # show the graph
    fig = get_price_data_fig(stock_data["stock_closings"], moving_average, time_window, time_window_key, currency)
    # add to placeholder to be displayed before options
    graph_placeholder.plotly_chart(fig, use_container_width=True)


    st.markdown("---")

    # Parte 3 los financial Statements

    tab1, tab2, tab3,tab4,tab5 = st.tabs([" ",
                                        "Balance Sheet",
                                        "Inconme Statment",
                                        "Cash Flow Statment",
                                        "DCF Graph"])



    with tab1:
        print("tab1 - nada")

    with tab2:
        #ticker = "MSFT"

        st.header(f"Balance Sheet - {ticker}")

        st.dataframe(get_balance_sheet(ticker,FA_API_KEY),width=1200,height=1600)


    with tab3:
        
        #ticker = "MSFT"
        st.header(f"Inconme Statement - {ticker}")

        st.dataframe(get_inconme_statement(ticker,FA_API_KEY),width=1200,height=1000)



    with tab4:
        
        #ticker = "MSFT"
        st.header(f"Cash Flow - {ticker}")

        st.dataframe(get_cash_flow_statement(ticker,FA_API_KEY),width=1200,height=1000)



    with tab5:

        try:
            dcf =fa.discounted_cash_flow(
                            ticker,
                            FA_API_KEY,
                            period="annualy",
                    )

            # create figures for normal and moving average
            fig1 = px.line(y=list(dcf.iloc[2].values)[::-1],
                            x=list(dcf.columns.values)[::-1])
            
            
            fig1.update_traces(line_color="blue", name="DCF", showlegend=True)

            # combine and add layout
            fig = go.Figure(data = fig1.data)
            fig.update_layout(
                title=f"DCF Graph- {ticker}",
                xaxis_title="Fecha",
                yaxis_title="Discounted Cash Flows",
                title_x = 0.5,
                # align labels top-left, side-by-side
                legend=dict(y=1.1, x=0, orientation="h"),
                showlegend=True
            )

            st.plotly_chart(fig)
        except:
            st.write("No DATA AVAILABLE")
        
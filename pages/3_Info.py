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


# create 3 columns and add a text_input
# in the second/center column
#ticker = st.columns(3)[1].text_input("Ticker")


listado_comphias = [" ","AAPL","MSFT","AMZN","NVDA","GOOGL","META","TSLA"]
ticker = st.selectbox("Listado de las compañias", listado_comphias)


# Hasta que no se introduce un ticker no hace nada

if ticker != " ":


    
    #            FINANCIAL MODEL PREP!
   
    
    # aqui cargamos todo finacial model prep. 
    # contamos con muchos datos. Investigarlos

    stock_data = load_data_fin_model_prep(ticker)

    info = stock_data["info"]
    currency = info["currency"]
    website = info["website"]
    info_companhia = info["description"]

    # ratios 

    key_metrics_annually = stock_data["key_metrics_annually"]

    # Nos quedamos con el cierre. 
    close = stock_data["stock_closings"]
    close.index =  pd.to_datetime(close.index)
    latest_price = close.iloc[-1]

    # Title
    st.title(f"{info['companyName']} ({info['symbol']})")



    #            YAHOO FINANCE
 
    
    #stock_yf = yf.Ticker("AAPL")
    #yahoo_info = get_company_info(stock_yf)
    



    # should all be displayed on the same row
    change_columns = st.columns(len(TIME_DIFFS))
    today = pd.to_datetime("today").floor("D")

    for i, (name, difference) in enumerate(TIME_DIFFS.items()):
        print(name)
        print(difference)
        # go back to the date <difference> ago
        date = (today - difference)
        # if there is no data back then, then use the earliest
        if date < close.index[0]:
            date = close.index[0]

        # if no match, get the date closest to it back in time, e.g. weekend to friday
        closest_date_index = np.abs(close.index - date)

        closest_date_index = closest_date_index.argmin()

        previous_price = close[closest_date_index]

        # calculate change in percent
        change = 100*(latest_price - previous_price) / previous_price
        # show red if negative, green if positive
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

    first_c.metric("Current Ratio", round(key_metrics_annually.loc["currentRatio"][0],2))
    second_c.metric("ROE", round(key_metrics_annually.loc["roe"][0],2))
    third_c.metric("PE Ratio", round(key_metrics_annually.loc["peRatio"][0],2))
    fourth_c.metric("Payout Ratio", round(key_metrics_annually.loc["payoutRatio"][0],2))


    first_c.metric("Revenue per Share", round(key_metrics_annually.loc["revenuePerShare"][0],2))
    second_c.metric("Cash per Share", round(key_metrics_annually.loc["cashPerShare"][0],2))
    third_c.metric("Debt to Equity", round(key_metrics_annually.loc["debtToEquity"][0],2))
    fourth_c.metric("Debt to Assets", round(key_metrics_annually.loc["debtToAssets"][0],2))

    st.markdown("---")
    
    #-----------------------------------------------------------------------
        
    # here I set different widths to each column,
    # meaning the first is 1 width and the second 3,
    # i.e. 1/(1+3) = 25% and 3 / (1+4) = 75%
    overview_columns = st.columns([1, 3])

    # first column, basic information

    # The <br/> tag in html simple adds a linebreak.
    # I add 4 of those to lower the text to become more
    # vertically aligned
    overview_columns[0].markdown("<br/>"*4, unsafe_allow_html=True)
    # text will be displayed and key is the key in info
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

    # second column, graph and graph settings

    # empty() functions as a placeholder,
    # that is, after I later add items to this placeholder,
    # the items will appear here before elements that are
    # added later. 
    graph_placeholder = overview_columns[1].empty()
    # The reason a placeholder is used is because I would like
    # to show the graph options beneath the graph, but they
    # need to be set first so that their returned values can
    # be used when constructing the graph

    # here I add an empty graph to avoid the elements from
    # jmping around when updating the graph
    graph_placeholder.plotly_chart(go.Figure(), use_container_width=True)

    # options that will dictate the graph:

    # radio buttons for what time window to display the stock price
    time_window_key = overview_columns[1].radio("Time window", TIME_DIFFS.keys(), index=len(TIME_DIFFS)-1, horizontal=True)
    # select the value from the key, i.e. the pd.DateOffset
    time_window = TIME_DIFFS[time_window_key]

    # slider to select the moving average to display in the graph
    moving_average = overview_columns[1].slider("Moving average", min_value=2, max_value=500, value=30)

    # Use above to construct the graph:

    # show the graph
    fig = get_price_data_fig(stock_data["stock_closings"], moving_average, time_window, time_window_key, currency)
    # add to placeholder to be displayed before options
    graph_placeholder.plotly_chart(fig, use_container_width=True)


    st.markdown("---")

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

        #ticker = "MSFT"
        #st.header(f"DCF Graph- {ticker}")
        #plot_DCF(ticker,FA_API_KEY)

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
    
import os
import fundamentalanalysis as fa
from datetime import datetime
import pandas as pd
import streamlit as st
# cargamos dotenv
from dotenv import load_dotenv
load_dotenv()

import plotly.express as px
import plotly.graph_objects as go
# las Api keys del proyecto 
# import api key for stock data
FA_API_KEY = os.getenv("financial_model_key")



"""
        "website": website,
        "info": info,
        "book_value": book_value,
        "price_book":Price_Book,
        "debt_equity":Debt_Equity,
        "current_ratio":Current_Ratio,
        "return_equity":returnOnEquity,
        "return_assets":returnOnAssets,
        "ebitda_margins":ebitdaMargins,
        "total_cash_share":totalCashPerShare

    }


"""





def load_data_fin_model_prep(ticker):
    # load data
    profile = fa.profile(ticker, FA_API_KEY)
    key_metrics_annually = fa.key_metrics(ticker, FA_API_KEY, period="annual")
    stock_data = fa.stock_data(ticker, period="5y", interval="1d")
    #financial_ratios_annually = fa.financial_ratios(ticker, FA_API_KEY, period="annual")
    #income_statement_annually = fa.income_statement(ticker, FA_API_KEY, period="annual")
    try:
        dividends = fa.stock_dividend(ticker, FA_API_KEY)
        dividends.index = pd.to_datetime(dividends.index)
        dividends = dividends["adjDividend"].resample("1Y").sum().sort_index()
    except:
        dividends = pd.Series(0, name="Dividends")

    # return information of interest
    return {
        "stock_closings": stock_data["close"].sort_index(),
        #"historical_PE": key_metrics_annually.loc["peRatio"].sort_index(),
        #"payout_ratio": financial_ratios_annually.loc["payoutRatio"].sort_index(),
        #"dividend_yield": 100*financial_ratios_annually.loc["dividendYield"].sort_index(),
        #"cash_per_share": key_metrics_annually.loc["cashPerShare"].sort_index(),
        #"debt_to_equity": key_metrics_annually.loc["debtToEquity"].sort_index(),
        #"free_cash_flow_per_share": key_metrics_annually.loc["freeCashFlowPerShare"].sort_index(),
        "dividends": dividends,
       # "earnings_per_share": income_statement_annually.loc["eps"].sort_index(),
        "info": profile.iloc[:, 0],
        "key_metrics_annually":key_metrics_annually

        #"website":profile["website"]
    }













def get_price_data_fig(srs, moving_average, time_window, time_window_key, currency):
    # create moving average
    ma = srs.rolling(window=moving_average).mean().dropna()
    # only in time window
    start = (pd.to_datetime("today").floor("D") - time_window)
    srs = srs.loc[start:]
    ma = ma.loc[start:]
    # create figures for normal and moving average
    fig1 = px.line(y=srs, x=srs.index)
    fig1.update_traces(line_color="blue", name="Price", showlegend=True)
    fig2 = px.line(y=ma, x=ma.index)
    fig2.update_traces(line_color="orange", name=f"Moving average price ({moving_average})", showlegend=True)
    # combine and add layout
    fig = go.Figure(data = fig1.data + fig2.data)
    fig.update_layout(
        title=f"Price data last {time_window_key}",
        xaxis_title="Date",
        yaxis_title=currency,
        title_x = 0.5,
        # align labels top-left, side-by-side
        legend=dict(y=1.1, x=0, orientation="h"),
        showlegend=True
    )
    return fig

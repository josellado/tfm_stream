import pandas as pd
import fundamentalanalysis as fa
import os

# cargamos dotenv
from dotenv import load_dotenv
load_dotenv()


from datetime import (
    date as d,
    datetime,
    timedelta,
)


###FUNCIONES 

def lambda_long_number_format(num, round_decimal=3):
    """limpieza de los numeros."""

    if num == float("inf"):
        return "inf"

    if isinstance(num, float):
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0

        string_fmt = f".{round_decimal}f"

        num_str = int(num) if num.is_integer() else f"{num:{string_fmt}}"

        return f"{num_str} {' KMBTP'[magnitude]}".strip()
    if isinstance(num, int):
        num = str(num)
    if (
        isinstance(num, str)
        and num.lstrip("-").isdigit()
        and not num.lstrip("-").startswith("0")
        and not is_valid_date(num)
    ):
        num = int(num)
        num /= 1.0
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0

        string_fmt = f".{round_decimal}f"
        num_str = int(num) if num.is_integer() else f"{num:{string_fmt}}"

        return f"{num_str} {' KMBTP'[magnitude]}".strip()
    return num


def is_valid_date(s: str) -> bool:
    """Comprobar que la fehca tiene su formato correspondiente"""
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return True
    except ValueError:
        return False
    

def limpiar_df_fmp(data, num):
    
    # para comprobar que tenemos suficientes columnas
    num = min(num, data.shape[1])
    data = data.iloc[:, 0:num]



    data = data.mask(data.astype(object).eq(num * ["None"])).dropna()
    data = data.mask(data.astype(object).eq(num * ["0"])).dropna()
    
    # diccionario para los datos que son fecha.
    date_rows = {
            "calendarYear": "%Y-%m-%d",
            "fillingDate": "%Y-%m-%d",
            "acceptedDate": "%Y-%m-%d",
        }

    # convertimos en fechas, los datos del diccionario
    for row, dt_type in date_rows.items():
        if row in data.index:
            data.loc[row] = pd.to_datetime(data.loc[row]).dt.strftime(dt_type)


    # funcion para dar el formato a los numeros 
    data = data.applymap(lambda x: lambda_long_number_format(x))

    data.loc["calendarYear"] = pd.to_datetime(data.loc["calendarYear"]).dt.strftime("%Y")



    # el index, separamos por palabras y ponemos mayusculas
    data.index = [
            "".join(" " + char if char.isupper() else char.strip() for char in idx).strip()
            for idx in data.index.tolist()
        ]

    data.index = [s_val.capitalize() for s_val in data.index]

    return data




"""

El script  se divide en 2 partes: 

    1. funciones que descargan el balance sheet the financial model prep 

    2. funciones que limpian la el blaance sheet
"""




# get balance sheet!  


def get_balance_sheet(ticker, FA_API_KEY):

    try: 

        df_fa = fa.balance_sheet_statement(
                    ticker, FA_API_KEY
                )
    except: 
        print("no tenemoos los datos")
        return pd.DataFrame()


    df_fa = df_fa.iloc[:, 0:5]

    df_fa_c = limpiar_df_fmp(df_fa, num=5)

    df_fa_c.index = df_fa_c.index

    df_fa_c=df_fa_c.drop(index=["Final link", "Link"])

    return df_fa_c



# Get inconme statement!

def get_inconme_statement(ticker, FA_API_KEY):
    
    try: 

        df_fa = fa.income_statement(
                    ticker, FA_API_KEY
                )
    except: 
        print("no tenemoos los datos")
        return pd.DataFrame()


    df_fa = df_fa.iloc[:, 0:5]

    df_fa_c = limpiar_df_fmp(df_fa, num=5)

    df_fa_c.index = df_fa_c.index

    df_fa_c=df_fa_c.drop(index=["Final link", "Link"])

    df_fa_c = df_fa_c.rename(
        index={
            "Ebitdaratio": "Ebitda ratio",
            "Epsdiluted":"Eps diluted"
        }
    )

    return df_fa_c




# Get inconme statement!

def get_cash_flow_statement(ticker, FA_API_KEY):
    
    try: 

        df_fa = fa.cash_flow_statement(
                    ticker, FA_API_KEY
                )
    except: 
        print("no tenemoos los datos")
        return pd.DataFrame()


    df_fa = df_fa.iloc[:, 0:5]

    df_fa_c = limpiar_df_fmp(df_fa, num=5)

    df_fa_c.index = df_fa_c.index

    df_fa_c=df_fa_c.drop(index=["Final link", "Link"])

    df_fa_c = df_fa_c.rename(
        index={
            "Ebitdaratio": "Ebitda ratio",
            "Epsdiluted":"Eps diluted"
        }
    )

    return df_fa_c




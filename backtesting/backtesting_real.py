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
#
import os
# cargamos dotenv
from dotenv import load_dotenv
load_dotenv()
# hace 5 anhos 
five_years_ago = datetime.now() - timedelta(days=5*365)
#
# Conexion con credenciales a la BBDD
conn = psycopg2.connect(
                host=os.getenv("HOST_TFM") ,
                user =os.getenv("USER_TFM") ,
                password=os.getenv("PASSWORD_TFM"),
                port=os.getenv("PORT_TFM"),
                database=os.getenv("DATABASE_TFM")
        )

cursor = conn.cursor()

# 1
sql = """SELECT * FROM precios_sp500 WHERE date >= %s"""
#cursor.execute(sql)


cursor.execute(sql, (five_years_ago,))

precios = pd.DataFrame(cursor.fetchall())
colnames = [desc[0] for desc in cursor.description]

precios.columns = colnames

# 2 
sql = """SELECT * FROM fondo_referencia  WHERE fecha >= %s """


cursor.execute(sql, (five_years_ago,))

precios_fondo = pd.DataFrame(cursor.fetchall())
colnames = [desc[0] for desc in cursor.description]

precios_fondo.columns = colnames

# cerrar
cursor.close()
conn.close()


#cursor.execute(sql)
#
#embeddings_sp500 = pd.DataFrame(cursor.fetchall())
#colnames = [desc[0] for desc in cursor.description]

precios_acciones = precios[['fs_perm_regional_id','close_adjusted','date']]

precios_acciones = precios_acciones.pivot_table(values='close_adjusted', index=precios_acciones.date, columns='fs_perm_regional_id', aggfunc='first')
precios_acciones = precios_acciones.fillna(method='ffill')
precios_acciones = precios_acciones.fillna(method='bfill')

precios_fondo.index = precios_fondo.fecha
precios_fondo = precios_fondo['lu0076314649']

precios_indice = precios_acciones['SP50-USA']
precios_acciones = precios_acciones.drop(['SP50-USA'],axis=1)


# fecha = '2018-08-30'
dias = 10
comision = 0.001
minimo = 5 # Porcentaje %

# consultar resultados de nuestro modelo a una fecha dada
def modelo(fecha):
    activos = list(precios_acciones.columns)
    mod = secrets.SystemRandom().sample(activos,500)
    return mod


def backtesting(fecha, comision, dias, minimo, precios_acciones, precios_indice, precios_fondo):

    risk_free_rate = 0
    acierto_benchmark = 0
    acierto_fondo = 0
    acierto_aleatorio = 0
    acierto_alpha = 0
    precios_acciones = precios_acciones[fecha:].head(dias+1)
    precios_indice = precios_indice[fecha:].head(dias+1)
    fecha_final_p = precios_indice.tail(1).index.item()

    importe = 100 # porcentaje total de la cartera
    inversion_total_i = importe
    ranking = modelo(fecha)
    importes_ind = []
    while importe > minimo:
        inv = importe * 0.25
        if inv > minimo:
            importe = importe - inv
            importes_ind.append(inv)
        else:
            num = int(importe/minimo)
            importes = importe/num
            importe = 0
            for j in range(num):
                importes_ind.append(importes)
    
    importes_ind_comision = [importes_ind[x] * (1-comision) for x in range(len(importes_ind))]
    muestra = ranking[1:len(importes_ind)+1]

    cartera = pd.DataFrame()
    cartera.index = muestra
    cartera['PESOS'] = importes_ind_comision
    cartera['PRECIO'] = precios_acciones[muestra].loc[fecha]
    cartera[f'PRECIO + {dias}'] = precios_acciones[muestra].loc[fecha_final_p]
    cartera['RENT_ACTIVO'] = (cartera[f'PRECIO + {dias}']-cartera[f'PRECIO']) / cartera[f'PRECIO']
    cartera['PESOS_FINAL'] = cartera['PESOS'] * (1 + cartera['RENT_ACTIVO'])


    inversion_total_f = cartera['PESOS_FINAL'].sum() * (1-comision)
    rentabilidad_periodo = ((inversion_total_f - inversion_total_i) / inversion_total_i) * 100
    rentabilidad_benchmark_p = ((precios_indice.loc[fecha_final_p]-precios_indice.loc[fecha])/precios_indice.loc[fecha]) * 100
    rentabilidad_fondo = ((precios_fondo.loc[fecha_final_p]-precios_fondo.loc[fecha])/precios_fondo.loc[fecha]) * 100

    # Creamos la cartera aleatoria, con 10 activos elegidos aleatoriamente y con un peso de 10% en cada uno
    # ponemos una semilla que cambia por dia
   # f = datetime.strptime(fecha, "%Y-%m-%d")
    f =fecha
    
    a = int(f.strftime('%Y%m%d'))

    fondos = []
    np.random.seed(a)
    for i in range(0, 10):
        fondos.append(np.random.choice(ranking))

    cartera_aleatoria = pd.DataFrame()
    cartera_aleatoria.index = fondos
    cartera_aleatoria['PESOS'] = 10
    cartera_aleatoria['PRECIO'] = precios_acciones[fondos].loc[fecha]
    cartera_aleatoria[f'PRECIO + {dias}'] = precios_acciones[fondos].loc[fecha_final_p]
    cartera_aleatoria['RENT_ACTIVO'] = (cartera_aleatoria[f'PRECIO + {dias}']-cartera_aleatoria[f'PRECIO']) / cartera_aleatoria[f'PRECIO']
    cartera_aleatoria['PESOS_FINAL'] = cartera_aleatoria['PESOS'] * (1 + cartera_aleatoria['RENT_ACTIVO'])


    inversion_total_f_aleatoria = cartera_aleatoria['PESOS_FINAL'].sum() * (1-comision)
    rentabilidad_periodo_aleatoria = ((inversion_total_f_aleatoria - inversion_total_i) / inversion_total_i) * 100


    if rentabilidad_periodo > rentabilidad_benchmark_p:
        acierto_benchmark = 1
    else:
        acierto_benchmark = 0
    
    if rentabilidad_periodo > rentabilidad_fondo:
        acierto_fondo = 1
    else:
        acierto_fondo = 0
    
    if rentabilidad_periodo > rentabilidad_periodo_aleatoria:
        acierto_aleatorio = 1
    else:
        acierto_aleatorio = 0

    # calcula alpha cartera_mod 
    pesos_final_mod = []
    dia_anterior = fecha
    for j in precios_acciones.index:
        cartera_alpha = pd.DataFrame()
        cartera_alpha.index = muestra
        cartera_alpha['PESOS'] = importes_ind_comision
        cartera_alpha[f'PRECIO + {dia_anterior}'] = precios_acciones[muestra].loc[dia_anterior]
        cartera_alpha[f'PRECIO + {j}'] = precios_acciones[muestra].loc[j]
        cartera_alpha['RENT_ACTIVO'] = (cartera_alpha[f'PRECIO + {j}']-cartera_alpha[f'PRECIO + {dia_anterior}']) / cartera_alpha[f'PRECIO + {dia_anterior}']
        cartera_alpha['PESOS_FINAL'] = cartera_alpha['PESOS'] * (1 + cartera_alpha['RENT_ACTIVO'])
        pesos_final_mod.append(cartera_alpha['PESOS_FINAL'].sum())
        dia_anterior = j
        importes_ind_comision = cartera_alpha['PESOS_FINAL']
    
    # Calculamos retornos diarios
    modelo_return = pd.DataFrame(pesos_final_mod).pct_change() * 100
    indice_return = pd.DataFrame(precios_indice.loc[fecha:j]).pct_change() * 100
    # Calculamos exceso de rentabilidad (portfolio - market)
    average_modelo_return = (modelo_return - pd.DataFrame(indice_return.values)).mean()
    # Perform linear regression, el (slope) es la beta de la cartera
    beta_modelo = stats.linregress(np.array(pd.DataFrame(indice_return.values).dropna()[0]), np.array(modelo_return.dropna()[0]))

    alpha = average_modelo_return.item() - (beta_modelo[0] * (indice_return.mean().item() - risk_free_rate))

    if alpha > 0:
        acierto_alpha = 1
    else:
        acierto_alpha = 0
    return rentabilidad_periodo, rentabilidad_benchmark_p, rentabilidad_fondo, rentabilidad_periodo_aleatoria, acierto_benchmark, acierto_fondo, acierto_aleatorio, alpha, acierto_alpha


fechas = precios_indice.index
tabla_resumen = pd.DataFrame(columns=['rentabilidad_periodo', 'rentabilidad_benchmark_p', 'rentabilidad_fondo','rentabilidad_aleatoria', 'alpha', 'acierto_benchmark', 'acierto_fondo','acierto_aleatorio','acierto_alpha'],index=fechas)

for fecha in fechas:
    #fecha = fecha.strftime('%Y-%m-%d')
    try:
        a, b, c, d, e, f, g, h, k = backtesting(fecha, comision, dias, minimo, precios_acciones, precios_indice, precios_fondo)
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
resumen.to_csv("backt_result_5_years.csv",index=False)


import streamlit as st
#import psycopg2
import pandas as pd
#from sklearn.metrics.pairwise import cosine_similarity
import requests
import json

# para graf correlacion 
import seaborn as sns
import matplotlib.pyplot as plt
# grapg
import networkx as nx

import os
# cargamos dotenv
from dotenv import load_dotenv
load_dotenv()



def main():
    st.title("Embeddings y Clusters Sp500")

    # Create a tickbox (checkbox)
    show_table = st.checkbox("Cluster Map del SP500")

    if show_table:

        # para que fuera mas rapido precargamos la imagen
        st.image("fundamanetals/cluster_map_sp500.png")
  
    st.markdown("#### Similutad entre empresas")
    
    # info bottom para explicar el proceso
    info_button = st.checkbox("ℹ️")
    # Display information when the button is clicked
    if info_button:
        st.markdown("""
                    - La idea de este gráfico es mostrar las compañías más similares a la escogida, para \
                    para ello los pasos realizados son:

                        - WebScrapping de Wikipedia para obtener listado del S&P 500 y su descripción.
                        - Crear embeddings usando un modelo de Sentence Transformer.
                        - Seleccionar las compañías más similares a la escogida y representarla gráficamente.
                        """)
        



    # 1 LLamar API listado embeddgins para obtener una lista de 
    # posibles compañias del sp500

    url = os.getenv("LISTA_EMBEDDINGS")

    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)

    lsita_compahias = json.loads(response.text)
    # creamos un None en la lista 
    listado_columnas = lsita_compahias
    listado_columnas.insert(0, " ")
    # dropdown list
    selected_value = st.selectbox("Listado de las compañias", listado_columnas)

    if selected_value != ' ':
    

        comphia_mostrar = selected_value
 
        # Llamada a la API 2. 
        # De la emp selecionada escogemos las 100 mas similares en base a la similitud coseno

        url = os.getenv("SIMILITUD_EMBEDDINGS")

        payload = json.dumps({
                     "comphia_mostrar": f"{comphia_mostrar}"
                        })
        
        headers = {
                    'Content-Type': 'application/json'
                    }

        response = requests.request("POST", url, headers=headers, data=payload)

        response_df =json.loads(response.text)


        distance_matrix = pd.read_json(response_df, orient='records')
        distance_matrix.set_index(distance_matrix.columns, inplace=True)


        companies = distance_matrix.columns.to_list()

        # grafico using NetworkX
        graph = nx.from_numpy_array(distance_matrix.values)

        # calculamos the minimum spanning tree
        mst = nx.minimum_spanning_tree(graph)

        plt.figure(figsize=(20, 20))

        
        pos = nx.spring_layout(mst, seed=42)
        custom_labels = {i: companies[i] for i in range(len(companies))}

        # el color 
        node_colors = ["red" if node == companies.index(comphia_mostrar) else "skyblue" for node in mst.nodes()]
        nodes = nx.draw_networkx_nodes(mst, pos, node_color=node_colors, node_size=1000, alpha=0.8)

        # Draw edges
        nx.draw_networkx_edges(mst, pos, alpha=0.5)

        # Draw node labels
        nx.draw_networkx_labels(mst, pos, labels=custom_labels, font_size=10)

        # Draw edge labels
        #edge_labels = {(companies[u], companies[v]): f"{d['weight']:.2f}" for u, v, d in mst.edges(data=True)}

        #nx.draw_networkx_edge_labels(mst,pos, edge_labels=edge_labels, font_size=5)

        # Set the node color for IBM explicitly
        nodes.set_edgecolor('black')


        fig = plt.gcf()
        st.pyplot(fig)




if __name__ == "__main__":
    main()



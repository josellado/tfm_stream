import streamlit as st
import psycopg2
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# para graf correlacion 
import seaborn as sns
import matplotlib.pyplot as plt
# grapg
import networkx as nx

import os
# cargamos dotenv
#from dotenv import load_dotenv
#load_dotenv()

# 1 Consultamos la bbdd para extraer los embeddings 


conn = psycopg2.connect(
                host=os.getenv("HOST_TFM") ,
                user =os.getenv("USER_TFM") ,
                password=os.getenv("PASSWORD_TFM"),
                port=os.getenv("PORT_TFM"),
                database=os.getenv("DATABASE_TFM")
        )


cursor=conn.cursor()



sql = f'''
                select * from public.embeddings_sentencetransformer
               
                    '''
                
cursor.execute(sql)

embeddings_sp500 = pd.DataFrame(cursor.fetchall())
colnames = [desc[0] for desc in cursor.description]

embeddings_sp500.columns = colnames
#
## cerramos conexion 
cursor.close()
conn.close()

# abrimos csv para ma rapido 
#embeddings_sp500 = pd.read_csv("news_similarity/embedding_sp500.csv")
## borrar unmmaed 0
#embeddings_sp500.drop('Unnamed: 0',axis=1,inplace=True)


# Similitud de Coseno 

cosine_sim_matrix = cosine_similarity(embeddings_sp500.T)


df_cos_sim = pd.DataFrame(
    cosine_sim_matrix,
    index=embeddings_sp500.columns,
    columns=embeddings_sp500.columns)


#sacamos la corre de coseno de las compañias 
corr_matrix = df_cos_sim.corr()






def main():
    st.title("Embeddings y Clusters Sp500")

    # Create a tickbox (checkbox)
    show_table = st.checkbox("Cluster Map del SP500")

    if show_table:
        sns.set_theme()
        clustermap= sns.clustermap(df_cos_sim, figsize=(14, 10))
        st.pyplot(clustermap.fig)



    st.markdown("#### Similutad entre empresas")
    
    # info bottom para explicar el proceso
    info_button = st.checkbox("ℹ️")
    # Display information when the button is clicked
    if info_button:
        st.markdown("""
                    - La idea de este gráfico es mostrar las compañias mas similiares a la escogida, para \
                    ello los pasos realizados son:

                        - Webscrapping de wikepedia para obtener listado del Sp500 y su describcion
                        - crear embeddings usando el modelo Sentence Transformer 
                        - seleccionar las compañias mas similares a la escogida y representarla graficamente 
                        """)

    # creamos un None en la lista 
    listado_columnas = list(df_cos_sim.columns)
    listado_columnas.insert(0, " ")
    # Create a selectbox (dropdown list)
    selected_value = st.selectbox("Listado de las compañias", listado_columnas)

    # Display the selected values
    #st.write("Selected value:", selected_value)

    if selected_value != ' ':
    

        comphia_mostrar = selected_value
 
        lista_mas_parecidas =df_cos_sim[comphia_mostrar].sort_values(ascending=False).iloc[:100].index.to_list()

        distance_matrix = 1 - df_cos_sim

        distance_matrix = distance_matrix.loc[lista_mas_parecidas, lista_mas_parecidas]


        companies = distance_matrix.columns.to_list()

        # Create a graph using NetworkX
        graph = nx.from_numpy_array(distance_matrix.values)

        # Compute the minimum spanning tree
        mst = nx.minimum_spanning_tree(graph)

        plt.figure(figsize=(20, 20))

        # Visualize the minimum spanning tree
        pos = nx.spring_layout(mst, seed=42)
        custom_labels = {i: companies[i] for i in range(len(companies))}

        # Draw nodes
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
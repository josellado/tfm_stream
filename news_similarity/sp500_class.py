import concurrent.futures
import requests
from bs4 import BeautifulSoup
import wikipediaapi
import numpy as np
import pandas as pd
import networkx as nx
import nltk
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

def get_wikipedia_text(page_title, language='en'):
    wiki = wikipediaapi.Wikipedia(language)
    page = wiki.page(page_title)
    
    if page.exists():
        return page.text
    else:
        return None


def get_sp500_company_links(wikipedia_url):
    response = requests.get(wikipedia_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    table = soup.find('table', {'class': 'wikitable sortable'})
    rows = table.findAll('tr')
    
    links = []
    for row in rows[1:]:
        link = row.find('td').find_next('td').find('a')['href']
        links.append(link)
    
    return links


wikipedia_url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
sp500_company_links = get_sp500_company_links(wikipedia_url)

page_titles = [link.split('/wiki/')[1] for link in sp500_company_links
                if 'wiki' in link]

page_titles = [title if '%26' not in title else title.replace('%26', '&')
                for title in page_titles]
page_titles = [title if '%27' not in title else title.replace('%27', "'")
                for title in page_titles]
page_titles = [
    title if '%C3%A9' not in title else title.replace('%C3%A9', "é")
    for title in page_titles]
page_titles = [
    title if '%E2%80%93' not in title else title.replace('%E2%80%93', "–")
    for title in page_titles]

page_content = {}
for page_title in tqdm(page_titles):
    text = get_wikipedia_text(page_title)
    if text:
        page_content[page_title] = text
    else:
        print(f"Page '{page_title}' does not exist.")


nltk.download('punkt')
model_name='all-mpnet-base-v2'
model = SentenceTransformer(model_name)

def get_article_embedding(text, model ,model_name='all-mpnet-base-v2'):
    #model = SentenceTransformer(model_name) # meter fuera
    # Tokenize the text into sentences
    sentences = nltk.sent_tokenize(text)
    # Get embeddings for each sentence
    sentence_embeddings = model.encode(sentences)
    # Compute the average embedding for the whole article
    article_embedding = np.mean(sentence_embeddings, axis=0)
    return article_embedding


def get_embedding_for_page(title,content):
    title, content = title,content
    embedding = get_article_embedding(content, model)
    return title, embedding

embeddings = {}

# Definir función para obtener el embedding en paralelo
def get_embedding_parallel(args):
    title, content = args
    return title, get_embedding_for_page(title, content)

num_threads = 4  
with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
    # Mapear las llamadas de get_embedding_for_page en paralelo
    futures = executor.map(get_embedding_parallel, page_content.items())
    # Recorrer los resultados y almacenar los embeddings
    for title, embedding in tqdm(futures, total=len(page_content)):
        embeddings[title] = embedding

embeddings = {}
for title, content in tqdm(page_content.items(), total=len(page_content)):
    embedding = get_embedding_for_page(title, content)
    embeddings[title] = embedding



df_final = pd.DataFrame(embeddings).T
df_final = df_final.drop(columns = [0])

new_df = pd.DataFrame()
for index, row in df_final.iterrows():
    empresa = index
    embedding = row.loc[1]
    new_df[empresa] = embedding

df_final = new_df

# ---- Leer aqui el csv con el embedding y llamarlo df_final

# AQUI

df_final = pd.read_csv("news_similarity/embedding_sp500.csv")

# borrar unmmaed 0
df_final.drop('Unnamed: 0',axis=1,inplace=True)

cosine_sim_matrix = cosine_similarity(df_final.T)


df_cos_sim = pd.DataFrame(
    cosine_sim_matrix,
    index=df_final.columns,
    columns=df_final.columns)

df_cos_sim.loc['Nvidia'].sort_values(ascending=False)

corr_matrix = df_cos_sim.corr()


sns.clustermap(df_cos_sim)
plt.show()


distance_matrix = 1 - df_cos_sim

columnas_quedamos = distance_matrix["Apple_Inc."].sort_values(ascending=False).index[:10]


xxx = distance_matrix[distance_matrix.columns[distance_matrix.columns.isin(columnas_quedamos)]]
distance_matrix =xxx[xxx.index.isin(columnas_quedamos)]

graph = nx.from_numpy_array(distance_matrix.values)

# Compute the minimum spanning tree
mst = nx.minimum_spanning_tree(graph)

plt.figure(figsize=(20, 20))


# Visualize the minimum spanning tree
pos = nx.spring_layout(mst, seed=42)
custom_labels = {i: df_cos_sim.columns[i]
                for i in range(distance_matrix.shape[0])}

nx.draw(mst, pos, labels=custom_labels, with_labels=True,
        node_color="skyblue", font_size=10, node_size=100)
nx.draw_networkx_edge_labels(
    mst, pos, edge_labels={(u, v): f"{d['weight']:.2f}"
    for u, v, d in mst.edges(data=True)}, font_size=5)
plt.title("Minimum Spanning Tree for the S&P 500 fron News.",
        fontsize=24)
plt.show()




# --------------------


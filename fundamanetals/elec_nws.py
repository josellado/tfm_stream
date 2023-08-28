import pandas as pd 
import requests 


# ellect us

symbol = 'AAPL'


response = requests.get(f"https://api.eclect.us/symbol/{symbol.lower()}?page=1")

response_dict = response.json()

# comprobamos que ha devuelto algo 

if len(response_dict) == 0:
    print("No hemos encontrado noticis en la api de SEC")
    

response_dict[0]["rf_highlights"]
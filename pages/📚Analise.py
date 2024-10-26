import streamlit as st
import os, re
import time
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup
from datetime import datetime

load_dotenv()
#openai_api_key = os.environ['OPENAI_API_KEY']
openai_api_key = os.getenv("OPENAI_API_KEY")


# https://emojipedia.org/books

# Definindo cabeçalhos para a requisição
headers = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def acessar_sinergias(url,headers):
    try:
        # Requisição para obter os dados JSON
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Verificar se a requisição foi bem-sucedida
    
        # Tentar decodificar o JSON
        data = response.json()
        #print(data)
    
        # Carregar os dados JSON em um DataFrame
        #df = pd.DataFrame(data['despacho'])
        #df['despacho'] = df['despacho'].fillna('Unknown')
    
        #print(df)
    
        # Verificar e converter a coluna 'count' para inteiro
        #df['tempo'] = pd.to_numeric(df['tempo'], errors='coerce')
        return data
    
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Error occurred during request: {req_err}")
    except ValueError as json_err:
        print(f"JSON decode error: {json_err}")
    except Exception as err:
        print(f"An unexpected error occurred: {err}")    
    return -1

llm = ChatOpenAI(api_key=openai_api_key)
out_parser = StrOutputParser()
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "Você é um assistente virtual."),
        ("user", "{user_input}"),
    ])

def main():
    st.title("Análise de documentos de patente")
    st.header("Elaboração de resumos")

    st.write("Entre com o número do pedido de patente em recurso: p.ex. 102012005032. ùltima atualização: 26/10/2024")
    numero = st.text_input("Digite aqui:")
    if numero:
        st.markdown(f"Numero: {numero}")
        
        # url = http://www.cientistaspatentes.com.br/apiphp/patents/query/?q={"mysql_query":"* FROM anterioridades where numero='102012005032'"}
        url = f"http://www.cientistaspatentes.com.br/apiphp/patents/query/?q={{%22mysql_query%22:%22*%20FROM%20anterioridades%20where%20numero=%27{numero}%27%22}}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Verificar se a requisição foi bem-sucedida
        data = response.json()
        df = pd.DataFrame(data['patents'])
        codigos = df['codigo'] 
        docs = df['doc']
        for i in range(len(codigos)):
            kindcode = codigos.iloc[i]
            doc = docs.iloc[i]
            st.markdown(f"{kindcode} = {doc}")

            # https://patents.google.com/patent/US5866903A/en?oq=US5866903

            url = f"https://patents.google.com/patent/{doc}A/en?oq={doc}"
            st.markdown(url)
            tentar_novamente = False
            try:
                html = urlopen(url)
                tentar_novamente = False
            except Exception as e:
                tentar_novamente = True            
            
            if tentar_novamente:  
                url = f"https://patents.google.com/patent/{doc}A1/en?oq={doc}"
                st.markdown(url)
                tentar_novamente = False
                try:
                    html = urlopen(url)
                    tentar_novamente = False
                except Exception as e:
                    tentar_novamente = True            
            
            if tentar_novamente:  
                url = f"https://patents.google.com/patent/{doc}A2/en?oq={doc}"
                st.markdown(url)
                tentar_novamente = False
                try:
                    html = urlopen(url)
                    tentar_novamente = False
                except Exception as e:
                    tentar_novamente = True            
            
            if tentar_novamente:  
                url = f"https://patents.google.com/patent/{doc}B1/en?oq={doc}"
                st.markdown(url)
                tentar_novamente = False
                try:
                    html = urlopen(url)
                    tentar_novamente = False
                except Exception as e:
                    tentar_novamente = True            
            
            bs = BeautifulSoup(html.read(),'html.parser')

            #print(bs.title)
            #nameList = bs.findAll("div", {"class":"abstract"})
            #resumo_D1 = ''
            #for name in nameList:
            #  resumo_D1 = name.getText()

            texto = ''
            nameList = bs.findAll("section", {"itemprop":"description"})
            for name in nameList:
                texto = name.getText()

            chain = prompt | llm | out_parser
            query = f"Resuma o documento em português: {texto}"
            resposta = chain.invoke({"user_input":f"{query}"})
            st.markdown(f"Resumo {kindcode} {doc}: {resposta}")

main()
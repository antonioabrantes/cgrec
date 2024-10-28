import streamlit as st
import os, re, json
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

def summarize_the_pdf(
    file_dir: str,
    max_final_token: int,
    token_threshold: int,
    gpt_model: str,
    temperature: float,
    summarizer_llm_system_role: str,
    final_summarizer_llm_system_role: str,
    character_overlap: int
):
    """
    Summarizes the content of a PDF file using OpenAI's ChatGPT engine.

    Args:
        file_dir (str): The path to the PDF file.
        max_final_token (int): The maximum number of tokens in the final summary.
        token_threshold (int): The threshold for token count reduction.
        gpt_model (str): The ChatGPT engine model name.
        temperature (float): The temperature parameter for ChatGPT response generation.
        summarizer_llm_system_role (str): The system role for the summarizer.

    Returns:
        str: The final summarized content.
    """
    docs = []
    docs.extend(PyPDFLoader(file_dir).load())
    print(f"Document length: {len(docs)}")
    max_summarizer_output_token = int(
        max_final_token/len(docs)) - token_threshold
    full_summary = ""
    counter = 1
    print("Generating the summary..")
    # if the document has more than one pages
    if len(docs) > 1:
        for i in range(len(docs)):
            # NOTE: This part can be optimized by considering a better technique for creating the prompt. (e.g: lanchain "chunksize" and "chunkoverlap" arguments.)

            if i == 0:  # For the first page
                prompt = docs[i].page_content + \
                    docs[i+1].page_content[:character_overlap]
            # For pages except the fist and the last one.
            elif i < len(docs)-1:
                prompt = docs[i-1].page_content[-character_overlap:] + \
                    docs[i].page_content + \
                    docs[i+1].page_content[:character_overlap]
            else:  # For the last page
                prompt = docs[i-1].page_content[-character_overlap:] + \
                    docs[i].page_content
            summarizer_llm_system_role = summarizer_llm_system_role.format(
                max_summarizer_output_token)
            full_summary += Summarizer.get_llm_response(
                gpt_model,
                temperature,
                summarizer_llm_system_role,
                prompt=prompt
            )
    else:  # if the document has only one page
        full_summary = docs[0].page_content

        print(f"Page {counter} was summarized. ", end="")
        counter += 1
    print("\nFull summary token length:", count_num_tokens(
        full_summary, model=gpt_model))
    final_summary = Summarizer.get_llm_response(
        gpt_model,
        temperature,
        final_summarizer_llm_system_role,
        prompt=full_summary
    )
    return final_summary


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
        st.markdown(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        st.markdown(f"Error occurred during request: {req_err}")
    except ValueError as json_err:
        st.markdown(f"JSON decode error: {json_err}")
    except Exception as err:
        st.markdown(f"An unexpected error occurred: {err}")    
    return -1

def conectar_siscap(url,headers,return_json=False):
    try:
        response = requests.get(url,headers=headers,verify=False,timeout=10)
        if response.status_code == 200:
            if return_json:
                data = response.json()
                json_data = json.dumps(data, indent=4)
                return(json_data)
            else:
                return response.text
        else:
            st.markdown(f"Erro: {response.status_code}")
            return(f"Erro: {response.status_code}")

    except requests.exceptions.HTTPError as http_err:
        st.markdown(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        st.markdown(f"Error occurred during request: {req_err}")
    except ValueError as json_err:
        st.markdown(f"JSON decode error: {json_err}")
    except Exception as err:
        st.markdown(f"An unexpected error occurred: {err}")    
    return -1

        
llm = ChatOpenAI(api_key=openai_api_key, model='gpt-4o-mini', temperature=0)
out_parser = StrOutputParser()
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "Você é um assistente virtual."),
        ("user", "{user_input}"),
    ])
chain = prompt | llm | out_parser

def main():
    st.title("Análise de documentos de patente")
    st.header("Elaboração de resumos")

    st.write("Entre com o número do pedido de patente em recurso: p.ex. 102012005032. ùltima atualização: 26/10/2024")
    numero = st.text_input("Digite aqui:")
    if numero:
        st.markdown(f"Numero: {numero}")
        
        query = '"' + "mysql_query" + '"' ":" + '"' + f" * FROM pedido where (decisao='indeferimento' or decisao='ciencia de parecer') and numero='{numero}' order by rpi desc" + '"'
        url = f"https://cientistaspatentes.com.br/apiphp/patents/query/?q={query}"
        json_data = conectar_siscap(url,headers,return_json=True)
        data = json.loads(json_data)
        codigo = data["patents"][0]["codigo"]
        divisao = data["patents"][0]["divisao"]
        #st.markdown(f"Indeferimento: {codigo} {divisao}")
        url = f"https://siscap.inpi.gov.br/adm/pareceres/{divisao}/{numero}{codigo}.txt"
        st.markdown(url)
        texto_relatorio = conectar_siscap(url,headers,return_json=False)
        
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
            # primeiro registro de anterioridades: 102012001686 WO2007057692 mas como teste use US20110314263

            url = f"https://patents.google.com/patent/{doc}A/en?oq={doc}"
            tentar_novamente = False
            try:
                html = urlopen(url)
                tentar_novamente = False
            except Exception as e:
                tentar_novamente = True            
            
            if tentar_novamente:  
                url = f"https://patents.google.com/patent/{doc}A1/en?oq={doc}"
                tentar_novamente = False
                try:
                    html = urlopen(url)
                    tentar_novamente = False
                except Exception as e:
                    tentar_novamente = True            
            
            if tentar_novamente:  
                url = f"https://patents.google.com/patent/{doc}A2/en?oq={doc}"
                tentar_novamente = False
                try:
                    html = urlopen(url)
                    tentar_novamente = False
                except Exception as e:
                    tentar_novamente = True            
            
            if tentar_novamente:  
                url = f"https://patents.google.com/patent/{doc}B1/en?oq={doc}"
                tentar_novamente = False
                try:
                    html = urlopen(url)
                    tentar_novamente = False
                except Exception as e:
                    tentar_novamente = True            
            
            st.markdown(url)
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
            
            query = f"Resuma o documento em português: {texto}"
            resposta = chain.invoke({"user_input":f"{query}"})
            st.markdown(f"Resumo {kindcode} {doc}: {resposta}")
            
            # sistema evista https://parecer.inpi.gov.br/patentes.php

main()
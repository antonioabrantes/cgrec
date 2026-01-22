# https://share.streamlit.io/
# https://faleconosco.streamlit.app/

import streamlit as st
#import pytesseract
#import fitz  # PyMuPDF
import re
#from pdf2image import convert_from_bytes
#from langchain.document_loaders import PyPDFLoader
import PyPDF2
#from PIL import Image
import io, os
import requests
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate 
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv() 
groq_api_key = os.getenv("GROQ_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(openai_api_key=openai_api_key,
                 temperature=0.0,
                 max_tokens=4000,
                 model="gpt-4o-mini"
                 )

# Define your system instruction
system_instruction = """ 
Você é um assistente virtual que busca decisões recursais cadastradas. Faça um resumo das decisões encontradas em poucos parágrafos. 
"""

# Define your template with the system instruction
template = (
    f"{system_instruction} "
    "Pergunta recebida {question}"
    "Contexto: {context}. "
)

prompt = PromptTemplate(input_variables=['context', 'question'], template=template)
chain = prompt | llm

#llm = ChatGroq(model="openai/gpt-oss-20b",temperature=0.2, max_tokens=1024)
#llm = ChatGroq(model="llama3-8b-8192",api_key=groq_api_key,temperature=0.2,max_tokens=1024)


def conectar_siscap(url,return_json=False):
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url,headers=headers,verify=False)
    if response.status_code == 200:
        if return_json:
            data = response.json()
            json_data = json.dumps(data, indent=4)
            return(json_data)
        else:
            return response.text
    else:
        return(f"Erro: {response.status_code}")

st.set_page_config(page_title="OCR de Petição INPI", layout="wide")

st.title("📄 OCR e Extração da Argumentação do Requerente")

url = 'https://cientistaspatentes.com.br/plos/peticao.txt'

st.write(f"Lendo {url}")

texto_txt = conectar_siscap(url)


def extrair_argumentacao_ipas(texto: str) -> str:
    """
    Extrai apenas a argumentação do requerente em petições do INPI,
    removendo dados pessoais e partes administrativas iniciais.
    """

    if not texto or not texto.strip():
        return ""

    # Normaliza espaços
    texto = re.sub(r'\n{2,}', '\n\n', texto)

    # Padrões que indicam início da argumentação
    padrao_inicio = re.compile(
        r"(ILMO\s+SENHOR\s+PRESIDENTE\s+DO\s+INPI|"
        r"DOS\s+FATOS|"
        r"DO\s+DIREITO|"
        r"DAS\s+RAZÕES)",
        re.IGNORECASE
    )

    match = padrao_inicio.search(texto)

    if match:
        texto_filtrado = texto[match.start():]
        return texto_filtrado.strip()

    # Se nenhum marcador for encontrado, retorna texto inteiro (fallback)
    return texto.strip()


#def ocr_pdf(pdf_bytes):
#    images = convert_from_bytes(pdf_bytes, dpi=300)
#    full_text = ""

#    for i, img in enumerate(images):
#        text = pytesseract.image_to_string(img, lang="por")
#        full_text += f"\n\n--- Página {i+1} ---\n{text}"

#    return full_text

def ler_pdf_pypdf2(pdf_bytes):
    """
    Lê PDF textual usando PyPDF2 e retorna o texto completo
    """
    leitor = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
    texto = ""

    for i, pagina in enumerate(leitor.pages):
        texto_pagina = pagina.extract_text()
        if texto_pagina:
            texto += f"\n\n--- Página {i+1} ---\n{texto_pagina}"

    return texto
    
def extrair_argumentacao_siscap(texto):
    """
    Extrai apenas a parte argumentativa típica de recursos do INPI
    """
    texto = texto.replace("\n", " ")

    padrao_inicio = re.compile(
        r"(Recurso contra o indeferimento|DOS ARGUMENTOS)",
        re.IGNORECASE
    )

    padrao_fim = re.compile(
        r"(CONSIDERAÇÕES FINAIS|CONCLUSÃO)",
        re.IGNORECASE
    )

    inicio = padrao_inicio.search(texto)
    fim = padrao_fim.search(texto)

    if inicio:
        start_idx = inicio.start()
        end_idx = fim.start() if fim else len(texto)
        return texto[start_idx:end_idx].strip()
    else:
        return "⚠️ Não foi possível identificar automaticamente a seção de argumentação."



st.info("🔍 Processando OCR do TXT, aguarde...")

argumentacao = extrair_argumentacao_ipas(texto_txt)

st.subheader("🧠 Argumentação do Requerente (extraída automaticamente)")
st.text_area(
    label="Conteúdo filtrado",
    value=argumentacao,
    height=500
)

with st.expander("📜 Ver8 texto completo do OCR"):
    st.text_area(
        label="Texto integral",
        value=texto_txt,
        height=400
    )

MAX_CHARS = 12000  # seguro para Groq
texto_filtrado = argumentacao[:MAX_CHARS]
if not texto_filtrado.strip():
    st.error("Texto vazio após filtragem.")
    st.stop()

system_block = "Você é um assistente adninistrativo, sua tarefa é fazer o resumo de uma petição administrativa"
question = f"Resuma o seguinte texto de argumentação do requerente um pedido de marca: {argumentacao}"
response = chain.invoke({
    "context": "",
    "question": question,
    "chat_history": ""
})
#qa_prompt = ChatPromptTemplate.from_messages(
#    [
#        # Define o papel de sistema com as instruções base
#        SystemMessage(content = system_block),
#       
#        # Define a estrutura da mensagem humana com pergunta e contexto
#        ("human", "Tarefa: {question}\n\nResponda de forma sucinta, técnica e didática.")
#    ]
#)

#messages=[{"role":"user", "content":question}]
#chain = qa_prompt | llm | StrOutputParser()
#resumo = chain.invoke({
#    "question": texto_filtrado
#})

st.subheader("🧠 Resumo gerado pela LLM")
st.write(response.content)

uploaded_file = st.file_uploader("Faça upload do PDF da petição", type=["pdf"])

if uploaded_file:
    st.info("🔍 Processando OCR do PDF, aguarde...")

    pdf_bytes = uploaded_file.read()
    
    #texto_ocr = ocr_pdf(pdf_bytes)
    #argumentacao = extrair_argumentacao(texto_ocr)

    texto_pdf = ler_pdf_pypdf2(pdf_bytes)
    argumentacao = extrair_argumentacao(texto_pdf)

    st.subheader("🧠 Argumentação do Requerente (extraída automaticamente)")
    st.text_area(
        label="Conteúdo filtrado",
        value=argumentacao,
        height=500
    )

    with st.expander("📜 Ver texto completo do OCR"):
        st.text_area(
            label="Texto integral",
            value=texto_pdf,
            height=400
        )
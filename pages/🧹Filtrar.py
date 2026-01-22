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

st.write('Lendo https://cientistaspatentes.com.br/plos/peticao.txt')

resposta = conectar_siscap(url)

st.write(resposta)

uploaded_file = st.file_uploader("Faça upload do PDF da petição", type=["pdf"])

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
    
def extrair_argumentacao(texto):
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
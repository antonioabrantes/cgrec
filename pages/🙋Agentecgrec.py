# Agente de IA para CGREC em Python com LangChain
# App com o uso de RAG
# ambiente dsa_python3_12
# cd DataScienceAcademy/Chap14
# streamlit run agentecgrec.py --server.port=8051
# Get-Process | Where-Object {$_.ProcessName -like "*streamlit*"}
# Stop-Process -Id 10456
# netstat -ano | findstr :8053
# taskkill /PID 10456 /F

# Importa o módulo 'os' para manipular variáveis de ambiente
import os

# Importa o módulo 'tempfile' para criação de diretórios e arquivos temporários
import tempfile

# Importa o Streamlit para criar a interface web interativa
import streamlit as st

# Importa o conector ChatGroq para uso de modelos via API Groq
from langchain_groq import ChatGroq

# Importa utilitários para criação de prompts estruturados
from langchain_core.prompts import ChatPromptTemplate

# Importa o tipo de mensagem de sistema (usada para instruções de comportamento do modelo)
from langchain_core.messages import SystemMessage

# Importa o carregador de documentos PDF da comunidade LangChain
from langchain_community.document_loaders import PyPDFLoader

# Importa o divisor de texto que segmenta o conteúdo em partes menores
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Importa o gerador de embeddings baseados em modelos HuggingFace
from langchain_huggingface import HuggingFaceEmbeddings

# Importa o repositório vetorial Chroma para armazenamento e busca de embeddings
from langchain_community.vectorstores import Chroma

# Importa utilitários para construção de pipelines paralelos de execução
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

# Importa o parser de saída para converter a resposta em texto simples
from langchain_core.output_parsers import StrOutputParser

# importa bibliotecas para colocar a chava da LLM em ambiente
import os
from dotenv import load_dotenv

# permite fazer o download de arquivos da internet, o sreamlit nao permite fazer link, tem que baixar o arquivo
import requests

#pip install mysql-connector-python permite concectar com a base Mysql
##import mysql.connector
from urllib.request import Request, urlopen
import json
from datetime import datetime

conexao = None
##try:
##    conexao = mysql.connector.connect(host='localhost',user='root',password='',database='producao')
##    cursor = conexao.cursor()
##except:
##    conexao = None
    
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
        
# Desativa o paralelismo de tokenização para evitar conflitos com o HuggingFace
os.environ["TOKENIZERS_PARALLELISM"] = "false"

@st.cache_data
def baixar_portaria(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, verify=False, timeout=15)
    return r.content if r.status_code == 200 else None

pdf_bytes_portaria16 = baixar_portaria(
    "https://cientistaspatentes.com.br/sinergias/pesquisa2/portaria16.pdf"
)

pdf_bytes_portaria10 = baixar_portaria(
    "https://cientistaspatentes.com.br/sinergias/pesquisa2/portaria10.pdf"
)

#url = "https://cientistaspatentes.com.br/sinergias/pesquisa2/portaria16.pdf"
#response = requests.get(url, verify=False)
#if response.status_code == 200:
#    pdf_bytes_portaria16 = response.content
#else:
#    pdf_bytes_portaria16 = None

# Define as configurações da página principal do app Streamlit
st.set_page_config(page_title = "CGREC/DIREP", page_icon = ":100:", layout = "wide")

# Cria a barra lateral do aplicativo com opções e instruções
with st.sidebar:
    st.header("Configurações")
    numero = st.text_input("Coloque aqui o número do pedido e pressione Enter")
    st.divider()
    st.subheader("Instruções")
    st.write("1) Informe número do pedido no campo acima.\n2) Digite sua pergunta ou dúvida.\n3) Clique em Enviar.")
    st.info("Aviso: a IA pode cometer erros. Verifique fatos críticos.")
    st.link_button("Clique Aqui Se Precisar de Suporte", "")
    st.divider()
    st.subheader("Documentos carregados")
    #st.sidebar.link_button(
    #    "📄 Portaria INPI/DIRPA nº 16/2024",
    #    "https://cientistaspatentes.com.br/sinergias/pesquisa2/portaria16.pdf"
    #)
    if pdf_bytes_portaria16:
        st.download_button(
            label=f"📄Portaria INPI/DIRPA n° 16/2024",
            data=pdf_bytes_portaria16,
            file_name='portaria16.pdf',
            mime="application/pdf"
        )
    else:
        st.error("Não foi possível carregar Portaria INPI/DIRPA n° 16/2024.")

    if pdf_bytes_portaria10:
        st.download_button(
            label=f"📄Portaria INPI/PR n° 10/2024",
            data=pdf_bytes_portaria10,
            file_name='portaria10.pdf',
            mime="application/pdf"
        )
    else:
        st.error("Não foi possível carregar Portaria INPI/PR n° 10/2024.")
    

# Exibe títulos e informações sobre o projeto
st.title("CGREC/DIREP")
st.title("Módulo de Análise de Preclusão - Versão 1")
st.caption("Modelo: openai/gpt-oss-20b via Groq + LangChain")

# Verifica se o número do pedido foi informada, interrompendo a execução caso contrário
if not numero:
    st.warning("Informe o número do pedido na barra lateral para continuar.")
    st.stop()

# Define a variável de ambiente com a chave informada
load_dotenv(dotenv_path='.env', override=True)
api_key = os.getenv("GROQ_API_KEY")
os.environ["GROQ_API_KEY"] = api_key

# Inicializa o modelo de linguagem via ChatGroq com temperatura e limite de tokens
llm = ChatGroq(model = "openai/gpt-oss-20b", temperature = 0.2, max_tokens = 1024)

# Cria um campo para o upload de um arquivo PDF jurídico
pdf_file = st.file_uploader("Envie um PDF da área jurídica (contrato, parecer, decisão, lei consolidada…)", type = ["pdf"])

# Cria um diretório temporário para armazenar os vetores do ChromaDB
if "chroma_dir" not in st.session_state:
    st.session_state.chroma_dir = tempfile.mkdtemp(prefix = "chroma_rag_")

# Define função para construir o índice vetorial a partir do PDF enviado
def dsa_cria_banco_vetorial(pdf_bytes) -> Chroma:

    # Cria um arquivo temporário e salva o conteúdo do PDF nele
    with tempfile.NamedTemporaryFile(delete = False, suffix = ".pdf") as tmp:
        tmp.write(pdf_bytes)
        tmp_path = tmp.name

    # Carrega o conteúdo do PDF usando o PyPDFLoader
    docs = PyPDFLoader(tmp_path).load()
    
    # Cria o divisor de texto em blocos menores com sobreposição entre partes
    splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 150)

    # Aplica o divisor de texto e cria os chunks
    chunks = splitter.split_documents(docs)

    # Gera embeddings com um modelo da HuggingFace especializado em recuperação semântica
    embeddings = HuggingFaceEmbeddings(model_name = "sentence-transformers/msmarco-bert-base-dot-v5")
    
    # Cria um banco de vetores persistente com o Chroma
    vectordb = Chroma.from_documents(documents = chunks, embedding = embeddings, persist_directory = st.session_state.chroma_dir)

    # Retorna o banco vetorial criado
    return vectordb

# Realiza a indexação do PDF quando enviado e ainda não processado
if pdf_file and "vectordb_ready" not in st.session_state:
    with st.spinner("Indexando o PDF no ChromaDB…"):
        st.session_state.vectordb = dsa_cria_banco_vetorial(pdf_file.read())
        st.session_state.vectordb_ready = True
        st.success("Indexação concluída.")

# Inicializa o recuperador de contexto (retriever) como None
retriever = None

# Caso o vetor esteja pronto, cria o retriever com busca dos 3 blocos mais relevantes
if st.session_state.get("vectordb_ready"):
    retriever = st.session_state.vectordb.as_retriever(search_kwargs = {"k": 3})

# Nesse trecho acima, a estratégia matemática é busca vetorial por similaridade, mais especificamente, 
# uma busca por vizinhos mais próximos (k-NN, “k-nearest neighbors”) baseada em distância de similaridade coseno.

# Quando você chama vectordb.as_retriever(search_kwargs={"k": 3}), o Chroma é instruído a, para cada nova consulta (query), 
# converter a pergunta em vetor de embeddings e depois calcular a proximidade angular entre esse vetor e os vetores armazenados dos chunks do PDF. 
# Essa proximidade é medida pelo cosseno do ângulo entre os vetores: quanto menor o ângulo (maior o cosseno, mais próximo de 1), 
# maior a similaridade semântica.

# Assim, o retriever retorna os 3 vetores mais próximos (os 3 blocos de texto mais semanticamente relacionados à pergunta). Ou seja, 
# a base matemática é: similaridade_coseno(A, B) = (A · B) / (||A|| × ||B||)

# Define as instruções principais do assistente jurídico
system_block = """Você é um assistente jurídico que responde usando estritamente o conteúdo do PDF fornecido quando possível.
Se a resposta não estiver no PDF, diga que não encontrou no documento e ofereça passos de verificação.
Formate a resposta com: Resumo, Fundamentação (com citações de trechos entre aspas) e Próximos passos.
Se houver conflito entre o PDF e conhecimento externo, priorize o PDF e sinalize a divergência."""

# Cria o template de prompt que será usado para formatar perguntas e contexto do PDF
qa_prompt = ChatPromptTemplate.from_messages(
    [
        # Define o papel de sistema com as instruções base
        SystemMessage(content = system_block),
        
        # Define a estrutura da mensagem humana com pergunta e contexto
        ("human", "Pergunta: {question}\n\nContexto do PDF:\n{context}\n\nResponda de forma sucinta, técnica e didática.")
    ]
)

# Função auxiliar para formatar os documentos recuperados
def dsa_formata_docs(docs):
    
    # Lista para armazenar trechos formatados
    out = []
    
    # Percorre os documentos e extrai conteúdo e metadados (como número da página)
    for d in docs:
        meta = d.metadata or {}
        where = f"p.{meta.get('page', '?')}"
        out.append(f'[{where}] "{d.page_content.strip()[:800]}{"…" if len(d.page_content) > 800 else ""}"')
    
    # Junta todos os trechos formatados em um único texto
    return "\n\n".join(out)

# Marca o estado de prontidão do chat se ainda não estiver configurado
if "chat_ready" not in st.session_state:
    st.session_state.chat_ready = True

# url = https://cientistaspatentes.com.br/apiphp/patents/query/?q={"mysql_query":" * FROM arquivados where numero='102012005032' order by data desc"}
query = '"' + "mysql_query" + '"' ":" + '"' + f" * FROM pedido where decisao='indeferimento' and numero='{numero}'" + '"'
url = f"https://cientistaspatentes.com.br/apiphp/patents/query/?q={query}" # 102012005032
json_data = conectar_siscap(url,return_json=True) # por exemplo 
#json_data='{"patents": [{"numero":"PI0905487","prioridade":"BR","instancia":"2 exame","decisao":"indeferimento","prioritario":"0","cc1":"4","anulado":"0","codigo":"1340921","rpi":"2020-12-29","divisao":"dicel","etapa":"2"}]}'
data = json.loads(json_data)
codigo = data["patents"][0]["codigo"]
divisao = data["patents"][0]["divisao"]
data_indeferimento = data["patents"][0]["rpi"]
dt = datetime.strptime(data_indeferimento, "%Y-%m-%d")
# formata no padrão brasileiro
data_formatada = dt.strftime("%d/%m/%Y")
frase = f"O indeferimento do pedido {numero} foi encontrado em {data_formatada}"
st.write(frase) 
st.link_button(
   "📄 Parecer",
   f"https://siscap.inpi.gov.br/adm/pareceres/{divisao}/00_{numero}{codigo}.pdf"
)

headers = {
    "User-Agent": "Mozilla/5.0"
}
url = f"https://siscap.inpi.gov.br/adm/pareceres/{divisao}/{numero}{codigo}.txt"
#PASTA_DOCS = "docs"
#os.makedirs(PASTA_DOCS, exist_ok=True)
#nome_arquivo = f"00_{numero}{codigo}.pdf"
#caminho_arquivo = os.path.join(PASTA_DOCS, nome_arquivo)
response = None 
try:
    response = requests.get(url, headers=headers, verify=False, timeout=30)
    if response.status_code == 200:
        texto = response.text  # 🔹 texto direto em memória sem ter feito download do arquivo
        st.write(texto) 
#        with open(caminho_arquivo, "wb") as f:
#            f.write(response.content)
#            st.success(f"Arquivo salvo localmente em: {caminho_arquivo}")
#            st.link_button("📄 Abrir parecer", caminho_arquivo)
    else:
        st.error("Não foi possível baixar o arquivo (status diferente de 200).")
except Exception as e:
    st.error(f"Erro ao baixar o arquivo: {e}")


# url = https://cientistaspatentes.com.br/apiphp/patents/query/?q={"mysql_query":" * FROM despachos_pag where numero='102012005032' and tipo_peticao=214"}
query = '"' + "mysql_query" + '"' ":" + '"' + f" * FROM despachos_pag where tipo_peticao=214 and numero='{numero}'" + '"'
url = f"https://cientistaspatentes.com.br/apiphp/patents/query/?q={query}"
json_data = conectar_siscap(url,return_json=True)
# json_data = {"patents": [{"numero":"102012005032","peticao":"WBRJ 870210040884","numnossonumero":"29409161934400520","data_peticao":"2021-05-05","tipo_peticao":"214","flag_pedexame":"1","flag_imagem":"1","cd_imagem":"8154379","update_imagem":"2021-05-07 01:05:10","conciliado":"1"}]}
data = json.loads(json_data)
peticao = data["patents"][0]["peticao"]
data_peticao = data["patents"][0]["data_peticao"]
dt = datetime.strptime(data_peticao, "%Y-%m-%d")
# formata no padrão brasileiro
data_formatada = dt.strftime("%d/%m/%Y")
frase = f"A petição de recurso {peticao} é de {data_formatada}"
st.write(frase)

#headers = {
#    "User-Agent": "Mozilla/5.0",
#    "Accept": "application/json"
#}
#req = Request(url, headers=headers)
#try:
#    with urlopen(req, timeout=10) as response:
#        json_data = json.load(response)
#    btn = st.button(json_data)
#except Exception as e:
#    print("⚠️ Erro ao acessar a API:", e)
#    json_data = None

# Campo de texto para o usuário escrever sua pergunta jurídica
pergunta = st.text_area("Escreva sua pergunta jurídica", height = 120, placeholder = "Ex.: Quais cláusulas tratam de rescisão e multas?")

# Cria duas colunas e insere o botão na primeira
col1, col2 = st.columns([1,1])
with col1:
    # Botão de envio da pergunta
    btn = st.button("Perguntar")

# Executa o pipeline quando o botão for clicado
if btn:

    # Verifica se há retriever disponível (PDF processado)
    if not retriever:
        st.error("Envie um PDF primeiro para habilitar o RAG.")
        st.stop()

    # Define o pipeline RAG: busca contexto no PDF, gera prompt e invoca o LLM
    rag_pipeline = RunnableParallel(
        context = retriever | dsa_formata_docs,
        question = RunnablePassthrough()
    ) | qa_prompt | llm | StrOutputParser()

    # Exibe o spinner enquanto gera a resposta
    with st.spinner("Gerando resposta…"):
        answer = rag_pipeline.invoke(pergunta)

    # Exibe o resultado final na tela
    st.markdown("### Resposta")
    st.write(answer)


# Explicação do rag_pipeline:

# Em nosso fluxo, a conversão da pergunta em vetor acontece dentro do ramo context = retriever | dsa_formata_docs, exatamente no momento 
# em que o retriever é executado quando você chama rag_pipeline.invoke(pergunta). O retriever criado a partir do Chroma chama internamente 
# o vectordb.similarity_search(pergunta, k=3), que por sua vez executa embeddings.embed_query(pergunta) usando o modelo 
# que você definiu (sentence-transformers/msmarco-bert-base-dot-v5). Esse vetor da query é então comparado aos vetores dos chunks já indexados 
# (gerados antes em Chroma.from_documents(...)). Em paralelo, o RunnablePassthrough() só carrega a string da pergunta adiante, sem vetorização. 
# Ou seja, a query do usuário é vetorizada toda vez que o retriever roda, antes da busca de similaridade no Chroma, 
# enquanto os vetores dos documentos já estavam persistidos desde a etapa de indexação.

# O RunnableParallel dispara em paralelo o ramo que busca e formata o contexto a partir do retriever e o ramo que apenas preserva a pergunta. 
# Isso é útil porque o ChatPromptTemplate espera receber um objeto com campos nomeados, por exemplo {context, question}, e você ganha eficiência 
# por não fazer esses passos em série quando não há dependência entre eles.








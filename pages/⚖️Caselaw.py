import streamlit as st
import os
# from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_community.embeddings import OpenAIEmbeddings

from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import ChatOpenAI

# from langchain.vectorstores import FAISS
from langchain_community.vectorstores import FAISS

from dotenv import load_dotenv
# from langchain.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings

# from langchain.document_loaders import PyPDFLoader ,TextLoader
from langchain_community.document_loaders import PyPDFLoader, TextLoader

from langchain.prompts.prompt import PromptTemplate
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.text_splitter import RecursiveCharacterTextSplitter
import tiktoken
import PyPDF2
from typing import List, Tuple
import re, ast, html
from bs4 import BeautifulSoup

load_dotenv()
# openai_api_key = os.environ['OPENAI_API_KEY']
openai_api_key = os.getenv("OPENAI_API_KEY")

st.title("Compêndio de decisões da CGREC")
st.markdown(
    """
    <img src="https://cientistaspatentes.com.br/imagens/IARA.png" width="140"/>
    """,
    unsafe_allow_html=True
)
st.markdown(
    "<small>Olá meu nome é Iara (Inteligência Artificial sobre Recursos Administrativos) uma assistente virtual para auxiliar em dúvidas sobre o exame. As fontes usadas incluem o a Resolução n°124/13 e a Lei 9279/96 (LPI). Última atualização: 17/10/2024 </small>",
    unsafe_allow_html=True)

# https://docs.streamlit.io/develop/concepts/architecture/session-state#initialization
# emoji https://emojipedia.org/balance-scale


if 'step' not in st.session_state:
    st.session_state['step'] = 0
    chat_history = []

if 'prompt' not in st.session_state:
    st.session_state['prompt'] = ''

if 'response' not in st.session_state:
    st.session_state['response'] = ''

if 'similar_response' not in st.session_state:
    st.session_state['similar_response'] = ''

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.step = 0

# Display chat messages from history on app rerun
# for message in st.session_state.messages:
#    with st.chat_message(message["role"]):
#        st.markdown(message["content"])


arquivos = {
    1: "caselaws.txt",
    2: "lei9279.txt",
    3: "resolucao124.txt"
}


def busca_indice(arquivos, arquivo_procurado):
    for chave, valor in arquivos.items():
        if valor == arquivo_procurado:
            indice = chave
            return indice
    return None


def ler_doc(arquivo):
    all_text = None
    if arquivo.endswith(".txt"):
        all_text = ler_txt(arquivo)
    if arquivo.endswith(".pdf"):
        all_text = ler_pdf(arquivo)
    return all_text


def ler_pdf(pdf_path):
    # Verificar se o arquivo existe no caminho especificado
    if os.path.exists(pdf_path):
        print(f"Arquivo {pdf_path} carregado com sucesso!")
    else:
        print(f"O arquivo {pdf_path} não foi encontrado. Verifique o caminho e tente novamente.")
        return None

    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)

        all_text = ""

        for page_num in range(num_pages):
            page = reader.pages[page_num]
            text = page.extract_text()
            if text:
                all_text += text

    return all_text


# Abrir o arquivo TXT
def ler_txt(txt_path):
    # Verificar se o arquivo existe no caminho especificado
    st.markdown("Lendo txt...")
    if os.path.exists(txt_path):
        st.markdown(f"Arquivo {txt_path} carregado com sucesso!")
    else:
        st.markdown(f"O arquivo {txt_path} não foi encontrado. Verifique o caminho e tente novamente.")
        return None

    with open(txt_path, 'r', encoding='utf-8') as file:
        all_text = file.read()

    return all_text


tokenizer = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    return len(tokenizer.encode(text))


def load_doc():
    # name1 = "caselaws.txt"
    name = arquivos.get(1)
    arquivo = f"dados/{name}"  # Especifique o caminho do PDF
    #text1 = ler_doc(arquivo)

    # name2 = "lei9279.txt"
    name = arquivos.get(2)
    arquivo = f"dados/{name}"  # Especifique o caminho do PDF
    text2 = ler_doc(arquivo)

    # name3 = "resolucao124.txt"
    name = arquivos.get(3)
    arquivo = f"dados/{name}"  # Especifique o caminho do PDF
    text3 = ler_doc(arquivo)

    text_splitter = RecursiveCharacterTextSplitter(  # divide o PDF em blocos/chunks de 512 tokens
        chunk_size=512,
        chunk_overlap=24,
        length_function=count_tokens,
        separators=["#"]  # "\n\n",
    )

    chunks1 = []
    chunks2 = []
    chunks3 = []
    chunks4 = []
    chunks5 = []
    chunks6 = []
    chunks7 = []
    chunks8 = []
    chunks9 = []

    # chunks = text_splitter.create_documents([text])
    metadata = {"source": arquivos.get(1), "row": 0}
    #chunks1 = text_splitter.create_documents([text1], metadatas=[metadata])

    # chunks = text_splitter.create_documents([text])
    metadata = {"source": arquivos.get(2), "row": 0}
    chunks2 = text_splitter.create_documents([text2], metadatas=[metadata])

    # chunks = text_splitter.create_documents([text])
    metadata = {"source": arquivos.get(3), "row": 0}
    chunks3 = text_splitter.create_documents([text3], metadatas=[metadata])

    combined_chunks = chunks1 + chunks2 + chunks3 + chunks4 + chunks5 + chunks6 + chunks7 + chunks8 + chunks9

    embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
    vectorstore = FAISS.from_documents(combined_chunks, embeddings)

    # Persist the vectors locally on disk
    vectorstore.save_local("faiss_index_datamodel_law")

    # Load from local storage
    persisted_vectorstore = FAISS.load_local("faiss_index_datamodel_law", embeddings,
                                             allow_dangerous_deserialization=True)
    return persisted_vectorstore


def load_model():
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
    return chain


def ask_pdf(query):
    st.markdown("Iniciando...")
    db = load_doc()
    st.markdown("Dados carregados no Vector store...")
    # similar_response = db.similarity_search(query,k=3)
    similar_response = db.similarity_search_with_score(query, k=3)
    st.markdown("Teste de similaridade concluído...")
    # Exibindo os resultados com suas pontuações
    docs = []
    pontuacoes = []
    for doc, score in similar_response:
        docs.append(doc)
        pontuacoes.append(score)
        # print(f"Documento: {doc}")
        # print(f"Pontuação: {score}")

    similar_response = clean_references(docs, pontuacoes)

    # similar_response = chat_gen.clean_references(similar_response)
    context = similar_response
    # context = [doc.page_content + doc.metadata['source'] for doc in similar_response]
    # print(context)

    # result = {"answer": "vazio"}
    chain = load_model()

    # Execute the chain and get the result
    result = chain.invoke({
        "context": context,
        "question": query,
        "chat_history": ""
    })
    # chat_history.append((query, result.content))
    # print(result)

    return result.content, similar_response


def clean_references(documents: List, pontuacoes: List) -> str:
    """
    Clean and format references from retrieved documents.

    Parameters:
        documents (List): List of retrieved documents.

    Returns:
        str: A string containing cleaned and formatted references.
    """
    server_url = "https://cientistaspatentes.com.br/central/data"
    documents = [str(x) + "\n\n" for x in documents]  # insere duas quebra de linha ao final de cada documento da lista
    markdown_documents = ""
    counter = 1
    for doc in documents:
        regex = r"page_content='(.*?)'\s+metadata=({.*})"
        match = re.search(regex, doc, re.DOTALL)
        if match:
            content = match.group(1)
            metadata = match.group(2)
            metadata_dict = ast.literal_eval(metadata)  # converte a string metadata em um dict real
            # Decode newlines and other escape sequences
            ##content = bytes(content, "utf-8").decode("unicode_escape")

            # Replace escaped newlines with actual newlines
            content = re.sub(r'\\n', '\n', content)
            # Remove special tokens
            ##content = re.sub(r'\s*<EOS>\s*<pad>\s*', ' ', content)
            # Remove any remaining multiple spaces
            ##content = re.sub(r'\s+', ' ', content).strip()
            content = re.sub(r'\s{2,}', ' ', content).strip()

            # Decode HTML entities
            ##content = html.unescape(content)

            # Replace incorrect unicode characters with correct ones
            ##content = content.encode('latin1').decode('utf-8', 'ignore')

            # Remove or replace special characters and mathematical symbols
            # This step may need to be customized based on the specific symbols in your documents
            ##content = re.sub(r'â', '-', content)
            ##content = re.sub(r'â', '∈', content)
            ##content = re.sub(r'Ã', '×', content)
            ##content = re.sub(r'ï¬', 'fi', content)
            ##content = re.sub(r'â', '∈', content)
            ##content = re.sub(r'Â·', '·', content)
            ##content = re.sub(r'ï¬', 'fl', content)

            nome = os.path.basename(metadata_dict['source'])
            nome = nome.replace("#", "")
            nome = nome.replace(".txt", ".pdf")
            pdf_url = f"{server_url}/{nome}"
            pontuacao = pontuacoes[counter - 1]

            soup = BeautifulSoup(content, 'html.parser')
            plain_text = soup.get_text()
            plain_text = plain_text.replace("\r\n", "").replace("\n", "")
            plain_text = plain_text.replace("*", "")
            indice = re.findall(r'\[(.*?)\]', plain_text)  # str(metadata_dict['row'])

            # Append cleaned content to the markdown string with two newlines between documents

            markdown_documents += f"**Conteúdo {counter}:**\n" + "*" + plain_text + "*" + "\n\n" + \
                                  f"**Referência:** {os.path.basename(metadata_dict['source'])}" + " | " + \
                                  f"**Id:** {indice}" + " | " + \
                                  f"**Pontuação:** {pontuacao:.3f}" + \
                                  f" [View PDF]({pdf_url})" + "\n\n"
            counter += 1
        else:
            print(f"No match found for doc: {doc}")

    return markdown_documents


# Interface gráfica:

if st.session_state.step == 0:
    if prompt := st.text_area(
            "Entre com sua busca abaixo, por exemplo, qual o prazo de sigilo dos pedidos de patente ?"):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.prompt = prompt

        response, similar_response = ask_pdf(prompt, )
        st.session_state.similar_response = similar_response
        st.session_state.response = response

        with st.chat_message("assistant"):
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

        if st.button("Referências"):
            # st.write(similar_response)
            st.session_state.step = 1
            st.rerun()

if st.session_state.step == 1:
    st.markdown(f"**Pergunta:** {st.session_state.prompt}")
    st.markdown(f"**Resposta:** {st.session_state.response}")
    st.markdown(f"**Referências:**")
    st.markdown(f"{st.session_state.similar_response}")
    st.session_state['step'] = 0
    chat_history = []

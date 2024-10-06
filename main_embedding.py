import os
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain.vectorstores import FAISS
from dotenv import load_dotenv
#from langchain.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.document_loaders import PyPDFLoader ,TextLoader
from langchain.prompts.prompt import PromptTemplate
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.text_splitter import RecursiveCharacterTextSplitter
import tiktoken
import PyPDF2
from typing import List, Tuple
import re, ast, html

load_dotenv()
#openai_api_key = os.environ['OPENAI_API_KEY']
openai_api_key = os.getenv("OPENAI_API_KEY")

arquivos = {
    1: "chatbot_cgrec#.txt",
    2: "parecer_03#.txt",
    3: "parecer_16#.txt",
    4: "parecer_19#.txt",
    5: "portaria_10#.txt",
    6: "parecer4.pdf",
    7: "parecer04#.txt"
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
    if os.path.exists(txt_path):
        print(f"Arquivo {txt_path} carregado com sucesso!")
    else:
        print(f"O arquivo {txt_path} não foi encontrado. Verifique o caminho e tente novamente.")
        return None
    
    with open(txt_path, 'r', encoding='utf-8') as file:
        all_text = file.read()

    return all_text

tokenizer = tiktoken.get_encoding("cl100k_base")
def count_tokens(text: str) -> int:
    return len(tokenizer.encode(text))
        

class chat_gen():
    def __init__(self):
        self.chat_history=[]

    def load_doc(self):
        #name1 = "chatbot_cgrec#.txt"
        name = arquivos.get(1)
        arquivo = f"dados/{name}"  # Especifique o caminho do PDF
        text1 = ler_doc(arquivo)
        
        #name2 = "parecer_03#.txt"
        name = arquivos.get(2)
        arquivo = f"dados/{name}"  # Especifique o caminho do PDF
        text2 = ler_doc(arquivo)
        
        #name3 = "parecer_16#.txt"
        name = arquivos.get(3)
        arquivo = f"dados/{name}"  # Especifique o caminho do PDF
        text3 = ler_doc(arquivo)
        
        #name4 = "parecer_19#.txt"
        name = arquivos.get(4)
        arquivo = f"dados/{name}"  # Especifique o caminho do PDF
        text4 = ler_doc(arquivo)
        
        #name5 = "portaria_10#.txt"
        name = arquivos.get(5)
        arquivo = f"dados/{name}"  # Especifique o caminho do PDF
        text5 = ler_doc(arquivo)
    
        #name6 = "parecer4.pdf"
        name = arquivos.get(6)
        arquivo = f"dados/{name}"  # Especifique o caminho do PDF
        #text6 = ler_pdf(arquivo)

        #name7 = "parecer04#.txt"
        name = arquivos.get(7)
        arquivo = f"dados/{name}"  # Especifique o caminho do PDF
        text7 = ler_doc(arquivo)

        text_splitter = RecursiveCharacterTextSplitter( # divide o PDF em blocos/chunks de 512 tokens
            chunk_size = 512,
            chunk_overlap  = 24,
            length_function = count_tokens,
            separators=["#"] #  "\n\n",
        )
        
        chunks1 = []
        chunks2 = []
        chunks3 = []
        chunks4 = []
        chunks5 = []
        chunks6 = []
        chunks7 = []
        
        # chunks = text_splitter.create_documents([text])
        metadata = {"source": arquivos.get(1),"row": 0}
        chunks1 = text_splitter.create_documents([text1], metadatas=[metadata])
        
        metadata = {"source": arquivos.get(2),"row": 0}
        chunks2 = text_splitter.create_documents([text2], metadatas=[metadata])
        
        metadata = {"source": arquivos.get(3),"row": 0}
        chunks3 = text_splitter.create_documents([text3], metadatas=[metadata])
        
        metadata = {"source": arquivos.get(4),"row": 0}
        chunks4 = text_splitter.create_documents([text4], metadatas=[metadata])
        
        metadata = {"source": arquivos.get(5),"row": 0}
        chunks5 = text_splitter.create_documents([text5], metadatas=[metadata])
        
        metadata = {"source": arquivos.get(6),"row": 0}
        #chunks6 = text_splitter.create_documents([text6], metadatas=[metadata])

        metadata = {"source": arquivos.get(7),"row": 0}
        chunks7 = text_splitter.create_documents([text7], metadatas=[metadata])

        combined_chunks = chunks1 + chunks2 + chunks3 + chunks4 + chunks5 + chunks6 + chunks7
        
        embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
        vectorstore = FAISS.from_documents(combined_chunks, embeddings)
        
        # Persist the vectors locally on disk
        vectorstore.save_local("faiss_index_datamodel")
    
        # Load from local storage
        persisted_vectorstore = FAISS.load_local("faiss_index_datamodel", embeddings, allow_dangerous_deserialization=True)
        return persisted_vectorstore

    def load_model(self):
        llm = ChatOpenAI(openai_api_key=openai_api_key,
                            temperature=0.0,
                            max_tokens=4000,
                            model="gpt-4o-mini"
                            )
     
        # Define your system instruction
        system_instruction = """ 
        Você é um assistente virtual de um escritório de patentes do governo.
        Sua função será responder perguntas que recebemos de requerentes que depositaram pedidos de patentes e tiveram seus pedidos indeferidos.
        Segundo a Lei de Patente a Lei 9279/96 (LPI) estes requerentes dispõe de 60 dias úteis para dar entrada numa petição de recurso (código 214) solitando
        a revisão da decisão de indeferimento numa segunda instância, a Coordenação de Recursos e Nulidades CGREC.
        Vou te passar algum contexto de nosso time de Fale Conosco para que você ter uma ideia das respostas que fornecemos.
        
        Siga todas as regras abaixo:
        1. Você deve buscar se comportar de maneira cordial e solícita.
        2. Suas respostas devem ser bem similares ou até identicas às enviadas em termos de comprimento, tom de voz, argumentos lógicos do Fale Conosco.
        3. Alguns das respostas podem conter links e informações irrelevantes. Preste atenção apenas no conteúdo útil da mensagem.
        
        Encerre com o cabeçalho:
        Atenciosamente,
        INPI / CGREC / Equipe Fale Conosco
        """

        # Define your template with the system instruction
        template = (
            f"{system_instruction} "
            "Combine o histórico {chat_history} "
            "Aqui está a dúvida recebida {question}"
            "Aqui está o contexto de respostas anteriores recebidas de requerentes feitas pelo nosso time do Fale Conosco {context}. "
            "Escreva a melhor resposta para solucionar a dúvida apresentada pelo requerente."
        )

        prompt = PromptTemplate(input_variables=['context','question','chat_history'],template=template)
        chain = prompt | llm
        return chain

    def ask_pdf(self,query):
        #print("iniciando...")
        db = self.load_doc()
        similar_response = db.similarity_search(query,k=3)
        similar_response = chat_gen.clean_references(similar_response)
        self.context = similar_response
        # self.context = [doc.page_content + doc.metadata['source'] for doc in similar_response]
        #print(self.context)

        #result = {"answer": "vazio"}
        chain = self.load_model()

        # Execute the chain and get the result
        result = chain.invoke({
            "context": self.context,
            "question": query,
            "chat_history": self.chat_history
        })
        self.chat_history.append((query, result.content))
        #print(result)
        
        return result.content, similar_response
        

    def clean_references(documents: List) -> str:
        """
        Clean and format references from retrieved documents.

        Parameters:
            documents (List): List of retrieved documents.

        Returns:
            str: A string containing cleaned and formatted references.
        """
        server_url = "https://faleconosco.streamlit.app/dados/"
        documents = [str(x)+"\n\n" for x in documents] # insere duas quebra de linha ao final de cada documento da lista
        markdown_documents = ""
        counter = 1
        for doc in documents:
            regex = r"page_content='(.*?)'\s+metadata=({.*})"
            match = re.search(regex, doc, re.DOTALL)
            if match:
                content = match.group(1)
                metadata = match.group(2)
                metadata_dict = ast.literal_eval(metadata) # converte a string metadata em um dict real
                # Decode newlines and other escape sequences
                content = bytes(content, "utf-8").decode("unicode_escape")
    
                # Replace escaped newlines with actual newlines
                content = re.sub(r'\\n', '\n', content)
                # Remove special tokens
                content = re.sub(r'\s*<EOS>\s*<pad>\s*', ' ', content)
                # Remove any remaining multiple spaces
                content = re.sub(r'\s+', ' ', content).strip()
    
                # Decode HTML entities
                ##content = html.unescape(content)
    
                # Replace incorrect unicode characters with correct ones
                content = content.encode('latin1').decode('utf-8', 'ignore')
    
                # Remove or replace special characters and mathematical symbols
                # This step may need to be customized based on the specific symbols in your documents
                content = re.sub(r'â', '-', content)
                content = re.sub(r'â', '∈', content)
                content = re.sub(r'Ã', '×', content)
                content = re.sub(r'ï¬', 'fi', content)
                content = re.sub(r'â', '∈', content)
                content = re.sub(r'Â·', '·', content)
                content = re.sub(r'ï¬', 'fl', content)
    
                pdf_url = f"{server_url}/{os.path.basename(metadata_dict['source'])}"
    
                # Append cleaned content to the markdown string with two newlines between documents
                # f"[View PDF]({pdf_url})" "\n\n"
                markdown_documents += f"Retrieved content {counter}:\n" + content + "\n\n" + \
                    f"Source: {os.path.basename(metadata_dict['source'])}" + " | " +\
                    f"Page number: {str(metadata_dict['row'])}" + " | " +\
                    "\n\n"
                counter += 1
            else:
                print(f"No match found for doc: {doc}")
                    

        return markdown_documents

if __name__ == "__main__":
    chat = chat_gen()
    #print(chat.ask_pdf("o que é causa madura ?"))
    #print(chat.ask_pdf("quando ela é aplicada?"))
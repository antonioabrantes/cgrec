import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.prompts.prompt import PromptTemplate
from dotenv import load_dotenv
#from main_embedding import chat_gen

load_dotenv()
#openai_api_key = os.environ['OPENAI_API_KEY']
openai_api_key = os.getenv("OPENAI_API_KEY")

#@st.cache_resource
#def initialize():
#    chat= chat_gen()
#    return chat

#st.session_state.chat=initialize()

st.title("Projeção de exame")
st.markdown(
"""
<img src="https://cientistaspatentes.com.br/imagens/IARA.png" width="140"/>
""", 
unsafe_allow_html=True
)
st.markdown("<small>Olá meu nome é Iara (Inteligência Artificial sobre Recursos Administrativos) uma assistente virtual auxiliar na projeção de primeiro exame de recursos administrativos e para dados do estoque de pedidos e produção de 2020 a 2024. Por exemplo, experimente perguntar: Apresente o gráfico dos pedidos de recurso em estoque na dicel de 2002 a 2024.", unsafe_allow_html=True)

# https://docs.streamlit.io/develop/concepts/architecture/session-state#initialization

#if 'step' not in st.session_state:
#    st.session_state['step'] = 0

chat_history=[]
llm = ChatOpenAI(openai_api_key=openai_api_key,
                    temperature=0.0,
                    max_tokens=4000,
                    model="gpt-4o-mini"
                    )

# Define your system instruction
system_instruction = """ 
Você é um assistente virtual de um escritório de patentes do governo.
Sua função será responder as perguntas com base nos dados fornecidos.
Você deve buscar se comportar de maneira cordial e solícita.

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
#for message in st.session_state.messages:
#    with st.chat_message(message["role"]):
#        st.markdown(message["content"])

if st.session_state.step == 0:
    if prompt := st.text_area("Entre com sua pergunta abaixo."):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.prompt = prompt

        response, similar_response = st.session_state.chat.ask_pdf(prompt,) 
        st.session_state.similar_response = similar_response
        st.session_state.response = response

        with st.chat_message("assistant"):
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        

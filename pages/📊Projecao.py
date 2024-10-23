import os
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.prompts.prompt import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
#from main_embedding import chat_gen

load_dotenv()
#openai_api_key = os.environ['OPENAI_API_KEY']
openai_api_key = os.getenv("OPENAI_API_KEY")

#@st.cache_resource
#def initialize():
#    chat= chat_gen()
#    return chat

#st.session_state.chat=initialize()

def save_and_execute_python_code(code_string, filename='script.py'):
    # Salvar o código no arquivo especificado
    with open(filename, 'w', encoding="utf-8") as file:
        file.write(code_string)

    print("### RODANDO ###")

    # Executar o arquivo
    os.system(f'python {filename}')

    print("### RODOU ###")
    
st.title("Projeção de exame")
st.markdown(
"""
<img src="https://cientistaspatentes.com.br/imagens/IARA.png" width="140"/>
""", 
unsafe_allow_html=True
)
st.markdown("<small>Olá meu nome é Iara (Inteligência Artificial sobre Recursos Administrativos) uma assistente virtual auxiliar na projeção de primeiro exame de recursos administrativos e para dados do estoque de pedidos e produção de 2020 a 2024. Por exemplo, experimente perguntar: Apresente os dados dos pedidos de recurso em estoque na dicel de 2020 a 2024. Últime atualização: 23/10/2024", unsafe_allow_html=True)

# https://docs.streamlit.io/develop/concepts/architecture/session-state#initialization

#if 'step' not in st.session_state:
#    st.session_state['step'] = 0

# para gerar estes dados: https://cientistaspatentes.com.br/central/control.php?action=173&op=5

context = '{"patents":[{"divisao":"dirpa","estoque":{"2020":4169,"2021":5186,"2022":6067,"2023":6312,"2024":7022},"producao":{"2020":1127,"2021":1126,"2022":1201,"2023":1687,"2024":511}},{"divisao":"ditex","estoque":{"2020":170,"2021":240,"2022":320,"2023":328,"2024":379},"producao":{"2020":59,"2021":36,"2022":21,"2023":87,"2024":5}},{"divisao":"difari","estoque":{"2020":299,"2021":418,"2022":482,"2023":489,"2024":521},"producao":{"2020":52,"2021":46,"2022":94,"2023":136,"2024":35}},{"divisao":"difarii","estoque":{"2020":270,"2021":365,"2022":455,"2023":492,"2024":520},"producao":{"2020":53,"2021":49,"2022":70,"2023":110,"2024":47}},{"divisao":"dipol","estoque":{"2020":207,"2021":263,"2022":301,"2023":331,"2024":366},"producao":{"2020":57,"2021":50,"2022":36,"2023":51,"2024":7}},{"divisao":"dinor","estoque":{"2020":182,"2021":241,"2022":298,"2023":279,"2024":277},"producao":{"2020":32,"2021":70,"2022":56,"2023":103,"2024":53}},{"divisao":"dialp","estoque":{"2020":395,"2021":515,"2022":596,"2023":643,"2024":669},"producao":{"2020":67,"2021":106,"2022":94,"2023":118,"2024":51}},{"divisao":"dibio","estoque":{"2020":196,"2021":218,"2022":253,"2023":264,"2024":302},"producao":{"2020":26,"2021":58,"2022":16,"2023":31,"2024":1}},{"divisao":"dimol","estoque":{"2020":228,"2021":371,"2022":490,"2023":553,"2024":619},"producao":{"2020":80,"2021":57,"2022":72,"2023":129,"2024":33}},{"divisao":"dipem","estoque":{"2020":0,"2021":0,"2022":0,"2023":0,"2024":0},"producao":{"2020":9,"2021":4,"2022":0,"2023":0,"2024":0}},{"divisao":"dipaq","estoque":{"2020":281,"2021":370,"2022":421,"2023":486,"2024":562},"producao":{"2020":38,"2021":46,"2022":69,"2023":66,"2024":49}},{"divisao":"dipae","estoque":{"2020":180,"2021":251,"2022":402,"2023":489,"2024":557},"producao":{"2020":123,"2021":45,"2022":27,"2023":35,"2024":0}},{"divisao":"ditel","estoque":{"2020":149,"2021":168,"2022":199,"2023":166,"2024":162},"producao":{"2020":111,"2021":75,"2022":67,"2023":74,"2024":38}},{"divisao":"dicel","estoque":{"2020":261,"2021":314,"2022":327,"2023":388,"2024":422},"producao":{"2020":85,"2021":72,"2022":88,"2023":114,"2024":60}},{"divisao":"difel","estoque":{"2020":189,"2021":246,"2022":272,"2023":182,"2024":184},"producao":{"2020":45,"2021":39,"2022":49,"2023":142,"2024":26}},{"divisao":"dipeq","estoque":{"2020":223,"2021":254,"2022":326,"2023":306,"2024":349},"producao":{"2020":54,"2021":65,"2022":62,"2023":126,"2024":48}},{"divisao":"diciv","estoque":{"2020":53,"2021":42,"2022":22,"2023":21,"2024":34},"producao":{"2020":29,"2021":28,"2022":45,"2023":13,"2024":2}},{"divisao":"dimat","estoque":{"2020":261,"2021":237,"2022":110,"2023":81,"2024":130},"producao":{"2020":58,"2021":80,"2022":178,"2023":109,"2024":11}},{"divisao":"dimec","estoque":{"2020":72,"2021":88,"2022":102,"2023":92,"2024":108},"producao":{"2020":23,"2021":5,"2022":25,"2023":50,"2024":19}},{"divisao":"ditem","estoque":{"2020":41,"2021":37,"2022":49,"2023":73,"2024":117},"producao":{"2020":38,"2021":40,"2022":31,"2023":40,"2024":0}},{"divisao":"dinec","estoque":{"2020":206,"2021":182,"2022":196,"2023":169,"2024":179},"producao":{"2020":49,"2021":74,"2022":44,"2023":71,"2024":23}},{"divisao":"dimut","estoque":{"2020":306,"2021":366,"2022":444,"2023":478,"2024":562},"producao":{"2020":38,"2021":81,"2022":57,"2023":82,"2024":3}}]}'

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

template2 = (
    "Aqui está a dúvida recebida {question}"
    "Aqui está o contexto de respostas anteriores recebidas de requerentes feitas pelo nosso time do Fale Conosco {context}. "
    "Escreva a resposta sucinta."
)

classification_template = PromptTemplate.from_template(
    """Você deve classificar uma pergunta
    
    Dada a pergunta do usuário abaixo, classifique-a como sendo sobre `Projecao`, `Status` ou `Estoque`.

    <Se a pergunta for sobre a projeção de exame de um recurso classifique-as como 'Projecao'>
    <Se a pergunta for sobre o andamento / porcessamento / status de um pedido de recurso classifique-a como 'Status'>
    <Se a pergunta for sobre o estoque de pedidos de recurso em uma divisão classifique-a como 'Estoque'>
    
    <question>
    {question}
    </question>
    
    Classificação:"""
)

classification_chain = classification_template | ChatOpenAI() | StrOutputParser()

projecao_template = """{system_instruction} Você é um especialista que é capaz de fazer uma projeção de quando o pedido de recurso será examinado, levando em conta o contexto {context}.\
\
Pergunta:\
{query}"""

estoque_template = """{system_instruction} Você é um assistente que mostra os gráficos de estoque de pedidos de recurso pendentes em uma dada divisão \
\
Pergunta:\
{query}"""

patent_template = """{system_instruction} Você é um assistente que responde perguntas sobre pedidos de patente, levando em conta o contexto {context} \
\
Pergunta:\
{query}"""

def prompt_router(input):
    question = input["query"]
    context = input["context"]
    chat_history = input["chat_history"]
    
    classification = classification_chain.invoke({"question": question})
   
    if classification == "Projecao":
        st.markdown("Questão relativa a projeção de exame de um pedido de recurso")
        numero = extrair_numero_pedido(question)
        if numero:
            contexto = f"O pedido {numero} será examinado em 2024" 
        else:
            contexto = "Informações adicionais sobre o pedido não foram encontradas."
        return PromptTemplate.from_template(projecao_template).format(query=question, context=context)
    elif classification == "Estoque":
        st.markdown("Questão relativa ao estoque de recursos de uma divisão")
        return PromptTemplate.from_template(estoque_template).format(query=question)
    elif classification == "Status":
        st.markdown("Questão relativa ao andamento de um pedido de recurso")
        numero = extrair_numero_pedido(input["query"])
        if numero:
            contexto = f"O pedido {numero} teve carta patente concedida em 2024" 
        else:
            contexto = "Informações adicionais sobre o pedido não foram encontradas."
        return PromptTemplate.from_template(patent_template).format(query=question, context=context)
    else:
        st.markdown("Não classificado:", classification)
        return None
        
chain3 = (
    {"query": RunnablePassthrough()}
    | RunnableLambda(prompt_router)
    | ChatOpenAI()
)

prompt2 = PromptTemplate(input_variables=['context','question'],template=template2)
chain2 = prompt2 | llm

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

        response = chain3.invoke({
            "context": context,
            "question": prompt,
            "chat_history": chat_history
        })
        chat_history.append((prompt, response.content))
        st.session_state.response = response

        with st.chat_message("assistant"):
            st.markdown(response.content)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
        prompt_modificado = f"Escreva um código Python que gere um gráfico mostrando " + prompt + ". Mostre apenas os comandos do código."
        response = chain2.invoke({
            "context": context,
            "question": prompt_modificado
        })
        #st.markdown(response.content)
        comando = response.content
        comando = comando.replace("```","")
        comando = comando.replace("python","")
        st.markdown("Imprimindo gráfico...")
        try:
            exec(comando)
            st.pyplot(plt.gcf())
        except Exception as e:
            st.markdown(f"Ocorreu um erro ao executar o código : {e}")
        

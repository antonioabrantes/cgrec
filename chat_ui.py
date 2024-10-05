import streamlit as st
from main_embedding import chat_gen

@st.cache_resource
def initialize():
    chat= chat_gen()
    return chat

st.session_state.chat=initialize()

st.title("Fale Conosco da CGREC")
st.markdown(
"""
<img src="https://cientistaspatentes.com.br/imagens/IARA.png" width="140"/>
""", 
unsafe_allow_html=True
)
st.markdown("<small>Olá meu nome é Iara (Inteligência Artificial sobre Recursos Administrativos) uma assistente virtual para auxiliar em dúvidas sobre procedimentos em pedidos de recurso administrativo de pedidos de patentes indeferidos em primeira instãncia no INPI. As respostas são baseadas nas Portarias 10/2024, 04/2024 e Pareceres 03/2024, 16/2023, 19/2024, bem como um conjunto de 60 perguntas & respostas levantados durante as oficinas da CGREC e do grupo de ZAP da CGREC</small>", unsafe_allow_html=True)


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.text_area("Entre com sua pergunta."):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    response, similar_response = st.session_state.chat.ask_pdf(prompt,) 
    #f"Echo: {prompt}"
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    if st.button("Referências"):
        st.write(similar_response)
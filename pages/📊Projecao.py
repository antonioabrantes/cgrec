import os, re
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.prompts.prompt import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
#from main_embedding import chat_gen
import requests
from datetime import datetime

load_dotenv()
#openai_api_key = os.environ['OPENAI_API_KEY']
openai_api_key = os.getenv("OPENAI_API_KEY")

#@st.cache_resource
#def initialize():
#    chat= chat_gen()
#    return chat

#st.session_state.chat=initialize()

fig, ax = plt.subplots()
df = pd.DataFrame()
        
month_names = {
    1: "janeiro",
    2: "fevereiro",
    3: "março",
    4: "abril",
    5: "maio",
    6: "junho",
    7: "julho",
    8: "agosto",
    9: "setembro",
    10: "outubro",
    11: "novembro",
    12: "dezembro"
}

def convert_date(date_str):
    # Parse the date string
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    
    # Extract the day, month, and year
    day = date_obj.day
    month = month_names[date_obj.month]
    year = date_obj.year
    
    # Format the date in the desired format
    formatted_date = f"{day} de {month} de {year}"
    return formatted_date
    
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
st.markdown("<small>Olá meu nome é Iara (Inteligência Artificial sobre Recursos Administrativos) uma assistente virtual auxiliar na projeção de primeiro exame de recursos administrativos e para dados do estoque de pedidos e produção de 2020 a 2024. Por exemplo, experimente perguntar: i) Apresente os dados dos pedidos de recurso em estoque na dicel de 2020 a 2024, ii) Qual andamento do pedido 112021005834 ?, iii) O pedido 102015001282 tem carta patente ?, iv) qual a projeção de exame de 112021005834? Última atualização: 25/10/2024", unsafe_allow_html=True)

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
    "Aqui está a dúvida recebida {query}"
    "Aqui está o contexto de respostas anteriores recebidas de requerentes feitas pelo nosso time do Fale Conosco {context}. "
    "Escreva a melhor resposta para solucionar a dúvida apresentada pelo requerente."
)

prompt = PromptTemplate(input_variables=['context','query','chat_history'],template=template)
chain = prompt | llm

template2 = (
    "Aqui está a dúvida recebida {query}"
    "Aqui está o contexto de respostas anteriores recebidas de requerentes feitas pelo nosso time do Fale Conosco {context}. "
    "Escreva a resposta sucinta."
)

classification_template = PromptTemplate.from_template(
    """Você deve classificar uma pergunta
    
    Dada a pergunta do usuário abaixo, classifique-a como sendo sobre `Projecao`, `Status` ou `Estoque`.

    <Se a pergunta for sobre a projeção de exame de um recurso classifique-as como 'Projecao'>
    <Se a pergunta for sobre o andamento / processamento / status de um pedido de recurso classifique-a como 'Status'>
    <Se a pergunta for sobre o estoque de pedidos de recurso em uma divisão classifique-a como 'Estoque'>
    
    <query>
    {query}
    </query>
    
    Aqui alguns exemplos de perguntas classificadas como 'Projecao':
    > Qual a estimativa de exame de recurso para o pedido 112021005834?
    > Quando o pedido 112021005834 deve ser examinado no recurso?
        
    Aqui alguns exemplos de perguntas classificadas como 'Status':
    > Qual andamento do pedido 112021005834?
    > Qual o status do pedido 112021005834?
    > Quais os despachos de 112021005834?
    > O pedido 112021005834 tem carta patente?
    
    Aqui alguns exemplos de perguntas classificadas como 'Estoque':
    > Apresente os dados dos pedidos de recurso em estoque na dicel de 2020 a 2024
    > Mostre um gráfico de recursos em estoque na dirpa entre 2022 e 2024
    
    Classificação:"""
)

classification_chain = classification_template | ChatOpenAI() | StrOutputParser()

projecao_template = """Você é um especialista que é capaz de fazer uma projeção de quando o pedido de recurso será examinado, levando em conta o contexto {context}.\
\
Pergunta:\
{query}"""

estoque_template = """Você é um assistente que mostra os gráficos de estoque de pedidos de recurso pendentes em uma dada divisão \
\ Este é o contexto com dados do estoque e de recursos pendentes: {context}
Pergunta:\
{query}"""

patent_template = """Você é um assistente que responde perguntas sobre o andamento de pedidos de patente em recurso, levando em conta o contexto {context} \
\
Pergunta:\
{query}"""

#Patentes de Invenção: 
#10 – para pedidos depositados por nacionais e via CUP (antigo PI); 
#11 – para pedidos depositados via PCT (antigo PI PCT); 
#12 – para pedidos divididos (antigo PI); 
#13 – para certificado de adição (antigo C1, C2, etc). 
#Patentes de Modelo de Utilidade: 
#20 – para pedidos depositados por nacionais e via CUP (antigo MU); 
#21 – para pedidos depositados via PCT (antigo MU PCT); 
#22 – para pedidos divididos (antigo MU).

def extrair_numero_pedido(texto):
    padrao = r"(PI|MU|C1|C2|C3|C4|C5|C6|C7|C8|C9)\s*\d{7}(?:-\d)?|(?:BR\s*)?(?:\d{2}\s*)?(?:\d{4}\s*)?\d{6}(?:-\d)?"
    match = re.search(padrao, texto)
    if match:
        numero_pedido = match.group()
        numero_pedido = numero_pedido.replace(" ", "").upper().strip()
        return numero_pedido
    else:
        return None
        
def extrair_digito_verificador(numero_pedido):
    # Remover espaços e prefixo "BR" se presente
    numero_pedido = numero_pedido.strip().replace(" ", "").upper()
    
    # Encontrar a posição do hífen e extrair o dígito verificador
    if '-' in numero_pedido:
        partes = numero_pedido.split('-')
        if len(partes) == 2 and len(partes[1]) == 1 and partes[1].isdigit():
            digito_verificador = partes[1]
        else:
            return -1 # ("O formato do número do pedido está incorreto.")
    else:
        return -2 # ("O número do pedido não contém um hífen com o dígito verificador.")
    
    return int(digito_verificador)
    
    
def calcular_digito_verificador(numero_pedido):
    # Remover espaços e juntar os números do pedido em uma única string
    numero_pedido = ''.join(numero_pedido.split())

    numero_pedido = numero_pedido.replace(" ", "").upper().strip()

    prefixos = ("BR", "PI", "MU", "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9")
    if numero_pedido.startswith(prefixos):
        numero_pedido = numero_pedido[2:]
        
    digito_verificador = -1

    numero_pedido = numero_pedido.split('-')[0] # ignore o que ve depois do hofen, se houver
    
    # Verificar se o número tem o formato correto (12 dígitos)
    if len(numero_pedido) == 12 and numero_pedido.isdigit():

        prefixos = ("10", "11", "12", "13", "20", "21", "22")
        if not numero_pedido.startswith(prefixos):
            return -2

        # https://www.uece.br/agin/noticias/inpi-veja-como-calcular-o-digito-verificador-na-nova-numeracao-da-dirpa-e-da-dicig/
        # Inverter o número do pedido
        numero_invertido = numero_pedido[::-1]
        
        # Inicializar variáveis
        soma = 0
        multiplicador = 2
        
        # Calcular soma dos produtos dos dígitos pelo multiplicador
        for digito in numero_invertido:
            soma += int(digito) * multiplicador
            multiplicador += 1
            if multiplicador > 9:
                multiplicador = 2
        
        # Calcular o resto da divisão da soma por 11
        resto = soma % 11
        
        # Calcular o dígito verificador
        digito_verificador = 11 - resto
        if digito_verificador == 10 or digito_verificador == 11:
            digito_verificador = 0

    if len(numero_pedido) == 7 and numero_pedido.isdigit():
        
        # Inverter o número do pedido
        numero_invertido = numero_pedido[::-1]
        
        # Inicializar variáveis
        soma = 0
        multiplicador = 2
        
        # Calcular soma dos produtos dos dígitos pelo multiplicador
        for digito in numero_invertido:
            soma += int(digito) * multiplicador
            multiplicador += 1
            if multiplicador > 9:
                multiplicador = 2
        
        # Calcular o resto da divisão da soma por 11
        resto = soma % 11
        
        # Calcular o dígito verificador
        digito_verificador = 11 - resto
        if digito_verificador == 10 or digito_verificador == 11:
            digito_verificador = 0

        #digito_verificador = -3

    return digito_verificador

classification = None


divisoes_indices = {
    "dirpa": 0,
    "ditex": 1,
    "difari": 2,
    "difarii": 3,    
    "dipol": 4,    
    "dinor": 5,    
    "dialp": 6,    
    "dibio": 7,    
    "dimol": 8,    
    "dipem": 9,    
    "dipaq": 10,    
    "dipae": 11,    
    "ditel": 12,    
    "dicel": 13,    
    "difel": 14,    
    "dipeq": 15,    
    "diciv": 16,    
    "dimat": 17,    
    "dimec": 18,    
    "ditem": 19,    
    "dinec": 20,
    "dimut": 21,    
}

divisoes_nome = {
    "dirpa": 'DIRPA',
    "ditex": 'CGPAT I/DITEX',
    "difari": 'CGPAT I/DIFAR I',
    "difarii": 'CGPAT I/DIFAR II',
    "dipol": 'CGPAT I/DIPOL',
    "dinor": 'CGPAT I/DINOR',
    "dialp": 'CGPAT II/DIALP',
    "dibio": 'CGPAT II/DIBIO',
    "dimol": 'CGPAT II/DIMOL',
    "dipem": 'CGPAT II/DIPEM',
    "dipaq": 'CGPAT II/DIPAQ',
    "dipae": 'CGPAT II/DIPAE',
    "ditel": 'CGPAT III/DITEL',
    "dicel": 'CGPAT III/DICEL',
    "difel": 'CGPAT III/DIFEL',
    "dipeq": 'CGPAT III/DIPEQ',
    "diciv": 'CGPAT III/DICIV',
    "dimat": 'CGPAT IV/DIMAT',
    "dimec": 'CGPAT IV/DIMEC',
    "ditem": 'CGPAT IV/DITEM',
    "dinec": 'CGPAT IV/DINEC',
    "dimut": 'CGPAT IV/DIMUT',
}


# Função para recuperar o índice com base no nome da divisão
def obter_indice(divisao):
    return divisoes_indices.get(divisao, "Divisão não encontrada")
    
def prompt_router(input):
    global classification
    query = input["query"]
    context = input["context"]
    chat_history = input["chat_history"]
    
    classification = classification_chain.invoke({"query": query})
    
    if classification == "Projecao":
        numero = extrair_numero_pedido(query)
        st.markdown(f"Questão relativa a projeção de exame de um pedido de recurso {numero}")
        # url = http://www.cientistaspatentes.com.br/apiphp/patents/query/?q={"mysql_query":"* FROM arquivados where despacho='12.2' and anulado=0 and numero='PI0923431'"}
        url = f"http://www.cientistaspatentes.com.br/apiphp/patents/query/?q={{%22mysql_query%22:%22*%20FROM%20arquivados%20where%20despacho=%2712.2%27%20and%20anulado=0%20and%20numero=%27{numero}%27%22}}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Verificar se a requisição foi bem-sucedida
        data1 = response.json()
        df2 = pd.DataFrame(data1['patents'])
        ano = df2['data'].astype(str).str[:4].astype(int).iloc[0] 
        #st.markdown(f"ano={ano}")
        
        # url = http://www.cientistaspatentes.com.br/apiphp/patents/query/?q={"mysql_query":"* FROM pedido where decisao in ('9.2','indeferimento') and anulado=0 and numero='PI0923431'"}
        url = f"http://www.cientistaspatentes.com.br/apiphp/patents/query/?q={{%22mysql_query%22:%22*%20FROM%20pedido%20where%20(decisao=%279.2%27%20or%20decisao=%27indeferimento%27)%20and%20anulado=0%20and%20numero=%27{numero}%27%22}}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Verificar se a requisição foi bem-sucedida
        data3 = response.json()
        df3 = pd.DataFrame(data3['patents'])
        divisao = df3['divisao'].iloc[0] 
        st.markdown(f"divisao={divisao}")
        
        url = f"https://cientistaspatentes.com.br/central/data/cgrec_json_{ano}.txt"
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Verificar se a requisição foi bem-sucedida
        data = response.json()
        df1 = pd.DataFrame(data['patents'])
        #df['producao'] = pd.to_numeric(df['producao'], errors='coerce')
        #df['estoque'] = pd.to_numeric(df['estoque'], errors='coerce')
        #df['ano'] = pd.to_numeric(df['ano'], errors='coerce')
        str_estoque = f"O estoque da DIRPA de pedidos de recurso com 12.2 em {ano} é de "
        str_estoque = str_estoque + str(df1['estoque'][0]) + ' pedidos, enquanto a produção efetiva realizada (independente do ano do 12.2) foi de '
        str_estoque = str_estoque + str(df1['producao'][0]) + ' primeiros exames de recurso.'
        i = obter_indice(divisao)
        idivisao = divisoes_nome.get(divisao)
        str_estoque = str_estoque + f". O estoque da {idivisao} de pedidos de recurso com 12.2 em {ano} é de "
        str_estoque = str_estoque + str(df1['estoque'][i]) + ' pedidos, enquanto a produção efetiva realizada (independente do ano do 12.2) foi de '
        str_estoque = str_estoque + str(df1['producao'][i]) + ' primeiros exames de recurso.'
        st.markdown(str_estoque)

        estoque_2020 = df1.loc[df1['divisao'] == divisao, 'estoque'].values[0].get('2020')
        estoque_2021 = df1.loc[df1['divisao'] == divisao, 'estoque'].values[0].get('2021')
        estoque_2022 = df1.loc[df1['divisao'] == divisao, 'estoque'].values[0].get('2022')
        estoque_2023 = df1.loc[df1['divisao'] == divisao, 'estoque'].values[0].get('2023')
        estoque_2024 = df1.loc[df1['divisao'] == divisao, 'estoque'].values[0].get('2024')

        producao_2020 = df1.loc[df1['divisao'] == divisao, 'producao'].values[0].get('2020')
        producao_2021 = df1.loc[df1['divisao'] == divisao, 'producao'].values[0].get('2021')
        producao_2022 = df1.loc[df1['divisao'] == divisao, 'producao'].values[0].get('2022')
        producao_2023 = df1.loc[df1['divisao'] == divisao, 'producao'].values[0].get('2023')
        producao_2024 = df1.loc[df1['divisao'] == divisao, 'producao'].values[0].get('2024')
        producao_2024_anualizada =  int(round(producao_2024*12/9,0))
        
        output = f"O pedido {numero} é um recurso que teve o 12.2 em {ano}. O pedido foi indeferido pela {divisao}, que por sua vez em 2024 tem um estoque de {estoque_2024} de recursos de pedidos com 12.2 em {ano} ou anteriores. Em 2024 a produção de primeiros exames de recurso de pedidos indeferidos nesta divisão é de {producao_2024} pareceres nos primeiros 9 meses do ano. O valor anualizado da produção estimada em 2024 é de {producao_2024_anualizada} primeiros exames. " 
        if (producao_2024_anualizada>estoque_2024):
            output = output + f" Desta forma, com esse estoque de recursos com 12.2 em {ano} da {divisao}, mantida a produção atual, o pedido {numero} terá seu primeiro exame em menos de um ano."
        st.markdown(output)

        projecao_2020 = 2020 + round(estoque_2020/producao_2020, 2)
        projecao_2021 = 2021 + round(estoque_2021/producao_2021, 2)
        projecao_2022 = 2022 + round(estoque_2022/producao_2022, 2)
        projecao_2023 = 2023 + round(estoque_2023/producao_2023, 2)
        projecao_2024 = 2024 + round(estoque_2024/producao_2024_anualizada, 2)
        #st.write(f"projeção 2020={projecao_2020}")
        #st.write(f"projeção 2021={projecao_2021}")
        #st.write(f"projeção 2022={projecao_2022}")
        #st.write(f"projeção 2023={projecao_2023}")
        #st.write(f"projeção 2024={projecao_2024}")

        df['ano'] = [2020, 2021, 2022, 2023]
        #df['prj'] = [2033.9, 2030.5, 2031.5, 2030.5, 2029.8]
        df['prj'] = [projecao_2020, projecao_2021, projecao_2022, projecao_2023]



        return PromptTemplate.from_template(projecao_template).format(query=query, context=context)
    elif classification == "Estoque":
        st.markdown("Questão relativa ao estoque de recursos de uma divisão.")
        return PromptTemplate.from_template(estoque_template).format(query=query, context=context)
    elif classification == "Status":
        str_context = ''
        context = ''
        numero = extrair_numero_pedido(query)
        digito = calcular_digito_verificador(numero)
        numerocd = f"{numero}-{digito}"
        st.markdown(f"Questão relativa ao andamento de um pedido de recurso {numerocd}")

        # http://www.cientistaspatentes.com.br/apiphp/patents/query/?q={"mysql_query":"* FROM arquivados WHERE numero='102015001282' and anulado=0 order by data desc"}
        query = '"' + "mysql_query" + '"' ":" + '"' + f" * FROM arquivados where numero='{numero}' and anulado=0 order by data desc" + '"'
        url = f"http://www.cientistaspatentes.com.br/apiphp/patents/query/?q={query}"
        data = acessar_sinergias(url,headers)

        descricao = ''
        resumo = ''
        despacho = ''
        formatted_date = ''
        
        #if 'patents' in data and isinstance(data['patents'], list) and len(data['patents']) > 0 and 'descricao' in data['patents'][0]:
        #    descricao = data['patents'][0]['descricao']
        #else:
        #    descricao = None  # Ou alguma mensagem de erro ou tratamento apropriado
    
        #try:
        #    if 'patents' in data and isinstance(data['patents'], list) and len(data['patents']) > 0 and 'descricao' in data['patents'][0]:
        #        descricao = data['patents'][0]['descricao']
        #    else:
        #        descricao = 'pedido inexistente'
        #except Exception as e:
        #    descricao = 'pedido inexistente'

        #st.markdown(descricao)

        try:
            if 'patents' in data and isinstance(data['patents'], list) and len(data['patents']) > 0 and 'despacho' in data['patents'][0]:
                despachos = [patent['despacho'] for patent in data['patents']]
            else:
                despachos = ''
                context = 'Diga que o pedido é inexistente'
                
        except Exception as e:
            despachos = ''
            context = 'Diga que o pedido é inexistente'

        if despachos != '':
        #if 'patents' in data and len(data['patents']) > 0 and 'despacho' in data['patents'][0]:
            despachos = [patent['despacho'] for patent in data['patents']]
            str_context = 'Despachos publicados para este pedido após uma consulta SQL a base de dados: '
            for despacho in despachos:
                query = '"' + "mysql_query" + '"' ":" + '"' + f" * FROM despachos WHERE despacho='{despacho}'" + '"'
                url = f"http://www.cientistaspatentes.com.br/apiphp/patents/query/?q={query}"
                data1 = acessar_sinergias(url,headers)
                descricao = data1['patents'][0]['descricao'].strip()
                resumo = data1['patents'][0]['resumo'].strip()
                str_context = str_context + '[' + despacho + ', ' + resumo + ', ' + descricao + '], '
            
            str_context = str_context + f"Se o despacho perguntado aparece nesta lista diga simplesmente que o despacho foi encontrado especificando o código do despacho encontrado"
            # http://www.cientistaspatentes.com.br/apiphp/patents/query/?q={%22mysql_query%22:%22*%20FROM%20revistas4%20WHERE%20numero=%27112021005834-6%27%20and%20data=%272024-10-22%27%20and%20despacho=%27PR%20-%20Recursos%27%22} 
            # http://www.cientistaspatentes.com.br/apiphp/patents/query/?q={"mysql_query":"* FROM revistas4 WHERE numero='112021005834-6' and data='2024-10-22' and despacho='PR - Recursos'"}
            
            despacho = data['patents'][0]['despacho'].strip()
            data_original = data['patents'][0]['data']
            formatted_date = convert_date(data['patents'][0]['data'])
            if despacho=='PR - Recursos':
                query = '"' + "mysql_query" + '"' ":" + '"' + f" * FROM revistas4 WHERE numero='{numerocd}' and data='{data_original}' and despacho='PR - Recursos'" + '"'
                url = f"http://www.cientistaspatentes.com.br/apiphp/patents/query/?q={query}"
                data = acessar_sinergias(url,headers)
                descricao = data['patents'][0]['descricao'].strip()
                resumo = ''
            else:
                query = '"' + "mysql_query" + '"' ":" + '"' + f" * FROM despachos WHERE despacho='{despacho}'" + '"'
                url = f"http://www.cientistaspatentes.com.br/apiphp/patents/query/?q={query}"
                data = acessar_sinergias(url,headers)
                descricao = data['patents'][0]['descricao'].strip()
                resumo = data['patents'][0]['resumo'].strip()

            context = "Última publicação: " + despacho + f" (publicado em {formatted_date}) " + resumo + '. ' + descricao
            st.markdown(context)
            context = context + str_context + " Seja sucinto na resposta, diga apenas se o despacho perguntado foi encontrado ou não."
            
        return PromptTemplate.from_template(patent_template).format(query=query, context=context)
    else:
        st.markdown("Não classificado:", classification)
        return None
        
chain3 = (
    RunnablePassthrough()
    | RunnableLambda(prompt_router)
    | ChatOpenAI()
)

prompt2 = PromptTemplate(input_variables=['context','query'],template=template2)
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
            "query": prompt,
            "chat_history": chat_history
        })
        chat_history.append((prompt, response.content))
        st.session_state.response = response
        
        if classification == "Status":
            with st.chat_message("assistant"):
                st.markdown(response.content)
                st.session_state.messages.append({"role": "assistant", "content": response})

        if classification == "Estoque":
            with st.chat_message("assistant"):
                st.markdown(response.content)
                st.session_state.messages.append({"role": "assistant", "content": response})

            prompt_modificado = f"Escreva um código Python que gere um gráfico mostrando " + prompt + ". Mostre apenas os comandos do código."
            response = chain2.invoke({
                "context": context,
                "query": prompt_modificado
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
        

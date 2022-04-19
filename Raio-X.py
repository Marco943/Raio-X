# Importar Streamlit e Pandas
import streamlit as st, pandas as pd
# Importar função de baixar arquivo do sharepoint
from funcoes import baixar_excel_sharepoint, subir_arquivo_sharepoint
from datetime import datetime

# Configura o Título da página
st.set_page_config(page_title='Raio-X Piloto')
parametros = st.experimental_get_query_params()
projeto = parametros['cliente'][0]

# Puxa Login e Senha do arquivo secreto
login = st.secrets['login_microsoft']['login']
senha = st.secrets['login_microsoft']['senha']
url_sharepoint = 'https://sucessoemvendassv.sharepoint.com'
time = time = '/sites/GestodeResultados'
caminho_arquivo = '/Shared Documents/10- Desenvolvimento/Streamlit/Raio-X/Perguntas Raio-x.xlsx'
caminho_respostas = '/Shared Documents/10- Desenvolvimento/Streamlit/Raio-X/Respostas/'

# Função que puxa o arquivo do sharepoint e mantém em cache
@st.cache
def perguntas(projeto):
    arquivo_baixado = baixar_excel_sharepoint(url_sharepoint, time, caminho_arquivo, login, senha)
    arquivo_baixado = arquivo_baixado[arquivo_baixado['Projeto'] == projeto]
    return arquivo_baixado
# Guarda o arquivo do sharepoint na variável perguntas
perguntas = perguntas(projeto)

# Definição dos elementos da página
cabecalho = st.container()
corpo = st.container()

# Preencher cabeçalho
with cabecalho:
    st.header('Raio-X {}'.format(projeto))
    st.subheader('App piloto')

# Preencher Formulário

with corpo:
    dados = st.columns(2)
    with dados[0]:
        loja = st.text_input(label = 'Loja', key='loja')
    with dados[1]:
        gerente = st.text_input(label = 'Gerente', key='gerente')
    vendedor = st.text_input(label = 'Nome', key = 'vendedor')
    # Inicializa um dicionário para guardar as respostas
    respostas = dict()

    # Faz um loop em cada etapa que existe no raio-x, normalmente 6
    for etapa in perguntas['ID_Etapa'].unique():
        # Faz uma tabela filtrada só para a etapa atual
        perguntas_f = perguntas[perguntas['ID_Etapa'] == etapa]
        # Pega o nome da etapa atual
        nome_etapa = perguntas_f['Etapa'].max()

        # Para a etapa atual, cria um expander com o nome da etapa
        with st.expander(label=nome_etapa):

            # Se for a última etapa, faz um botão de rádio para perguntar se o cliente fechou a compra
            if etapa == perguntas['ID_Etapa'].unique()[-1]:
                fechoucompra = st.radio(
                    label = 'O cliente fechou a compra?',
                    options = [True, False], index = 0, # O índice diz qual a seleção padrão
                    format_func = lambda x: {False: 'Não', True: 'Sim'}.get(x)
                )

            # Para a etapa atual, faz um loop em cada pergunta que existe nesta etapa
            for pergunta in perguntas_f['ID_Pergunta'].unique():

                # Faz uma tabela filtrada só com a pergunta atual, ou seja, tabela de uma linha
                perguntas_ff = perguntas_f[perguntas_f['ID_Pergunta'] == pergunta]

                # Pega a descrição da pergunta atual
                nome_pergunta = perguntas_ff['Pergunta'].max()

                # Verifica se a pergunta é dependente ou não de o cliente ter fechado a compra, e também verifica se a opção de o cliente ter fechado a compra está como Sim ou Não. Vai mostrar só as perguntas correspondentes
                if (perguntas_ff['Compra_Fechada'].max() == 0) or (perguntas_ff['Compra_Fechada'].max() == -1 and fechoucompra == False) or (perguntas_ff['Compra_Fechada'].max() == 1 and fechoucompra == True):

                    # Guarda nas respostas um True ou False, com o valor do ID da pergunta. Ex: {1: True, 2: False}
                    respostas[int(pergunta)] = st.checkbox(
                        label = nome_pergunta,
                        key = {'pergunta_{}'.format(pergunta)}
                    )
                # Se a pergunta não deve ser mostrada, continua o loop sem fazer nada
                else:
                    continue

enviar = st.button('Enviar')

if enviar:
    respostas = pd.DataFrame.from_dict(respostas, orient='index').reset_index().rename(columns = {'index': 'ID_Pergunta', 0: 'Resposta'})
    respostas['Fechou'] = fechoucompra
    datahora = datetime.now().strftime('%d_%m_%Y_%H_%M_%S')
    nome_arquivo = 'Raio-X_{projeto}_{loja}_{vendedor}_{datahora}.csv'.format(projeto = projeto, loja = loja, vendedor = vendedor, datahora=datahora)
    #st.write('Enviado {}'.format(nome_arquivo))

    subir_arquivo_sharepoint(respostas, url_sharepoint, time, caminho_respostas+nome_arquivo, login, senha)
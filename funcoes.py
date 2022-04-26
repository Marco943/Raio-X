import pandas as pd, io
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File

def baixar_excel_sharepoint(url_sharepoint, time, caminho_arquivo, login, senha):
    url = url_sharepoint
    time = time
    login = login
    senha = senha
    caminho_arquivo = caminho_arquivo #'/Shared Documents/10- Desenvolvimento/Streamlit/Raio-X/Perguntas Raio-X.xlsx'

    # Conectar ao site com as credenciais
    ctx = ClientContext(url+time).with_credentials(UserCredential(login, senha))

    # Checar se está conectado ao site
    # web = ctx.web
    # ctx.load(web)
    # ctx.execute_query()
    # print("Site title: {0}".format(web.properties['Title']))

    response = File.open_binary(ctx, time+caminho_arquivo)

    bytes_file_obj = io.BytesIO()
    bytes_file_obj.write(response.content)
    bytes_file_obj.seek(0)
    return pd.read_excel(bytes_file_obj)

def subir_arquivo_sharepoint(dados, url_sharepoint, time, caminho_arquivo, login, senha):
    url = url_sharepoint
    time = time
    login = login
    senha = senha
    caminho_arquivo = caminho_arquivo[1:] if caminho_arquivo[0] == '/' else caminho_arquivo #'/Shared Documents/10- Desenvolvimento/Streamlit/Raio-X/Perguntas Raio-X.xlsx'

    ctx = ClientContext(url+time).with_credentials(UserCredential(login, senha))

    buffer = io.BytesIO()
    dados.to_csv(buffer, index=False, encoding = 'utf-8')
    buffer.seek(0)
    file_content = buffer.read()

    ctx.web.get_folder_by_server_relative_url(time).upload_file(caminho_arquivo, file_content).execute_query()

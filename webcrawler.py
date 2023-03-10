import requests
import sqlite3
from bs4 import BeautifulSoup
from datetime import datetime

def get_current_time():
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    return current_time

# Define a URL base do site que será rastreado
plataform = "PC"
base_url = "https://www.nuuvem.com/br-pt/catalog/platforms/pc/page/"

# Conecta-se ao banco de dados SQLite
conn = sqlite3.connect('documentos_html.db')
c = conn.cursor()

# Cria a tabela para armazenar os documentos HTML, se ela não existir
c.execute('''CREATE TABLE IF NOT EXISTS documentos_html 
             (id INTEGER PRIMARY KEY, url TEXT, html TEXT, plataform TEXT, timestamp DATETIME)''')
# Função que busca e salva o HTML da página
def salvar_html(url):
    # Faz uma requisição GET para a URL
    response = requests.get(url)

    # Cria um objeto BeautifulSoup com o conteúdo da página
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extrai o HTML da página
    html = str(soup)

    # Salva o HTML no banco de dados
    # if not url.startswith('https://www.nuuvem.com/br-pt/catalog/platforms/pc/page/'):
    c.execute("INSERT INTO documentos_html (url, html, plataform, timestamp) VALUES (?, ?, ?, ?)", (url, html, plataform, get_current_time()))
    conn.commit()

    # Retorna o HTML
    return html

# Função que rastreia as páginas do site
def rastrear_paginas(url):
    # Salva o HTML da página atual
    html = salvar_html(url)

    # Cria um objeto BeautifulSoup com o conteúdo da página
    soup = BeautifulSoup(html, 'html.parser')

    # Encontra todos os links na página
    links = soup.find_all('a')
    # Rastreia os links encontrados
    for link in links:
        # Extrai o URL do link
        link_url = link.get('href')

        if link_url is None:
            continue
        # Ignora links externos ou não HTTP
        if not link_url.startswith('https://www.nuuvem.com/br-pt/item/'):
            continue

        # Salva o HTML da página linkada
        salvar_html(link_url)

# Inicia o rastreamento na página inicial
pageIndex = 1
while pageIndex <= 10:       
    rastrear_paginas(base_url+str(pageIndex))
    pageIndex = pageIndex+1

# Fecha a conexão com o banco de dados
conn.close()

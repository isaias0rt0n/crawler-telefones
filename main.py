import re
import threading

import requests
from bs4 import BeautifulSoup

DOMINIO = "https://django-anuncios.solyd.com.br"
URL_AUTOMOVEIS = "https://django-anuncios.solyd.com.br/automoveis/"

LINKS = []
TELEFONES = []


def request(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:  # obeve sucesso
            return response.text  # retorno da requisição em modo texto
        else:
            print("Erro ao tentar fazer requisição")
    except Exception as error:
        print("Erro ao fazer requisição: {}".format(error))


def parsing(response_html):
    try:
        soup = BeautifulSoup(response_html, 'html.parser')
        return soup
    except Exception as error:
        print("Erro ao fazer parsing HTML: {}".format(error))


def encontrar_links(soup):
    try:
        cards_pai = soup.find("div", class_="ui three doubling link cards")
        cards = cards_pai.find_all("a")
    except:
        print("Erro ao encontrar links")
        return None

    links = []
    for card in cards:
        try:
            link = card['href']
            links.append(link)
        except:
            pass

    return links


def encontrar_telefones(soup):
    try:
        descricao = soup.find_all("div", class_="sixteen wide column")[2].p.get_text().strip()
    except:
        print("Erro ao encontrar descrição")
        return None

    regex = re.findall(r"\(?0?([1-9]{2})[ \-\.\)]{0,2}(9[ \-\.]?\d{4})[ \-\.]?(\d{4})", descricao)  # expressão regular para encontrar telefones
    if regex:
        return regex


def descobrir_telefones():
    while True:
        try:
            link_anuncio = LINKS.pop(0)
        except:
            return None

        resposta_anuncio = request(DOMINIO + link_anuncio)

        if resposta_anuncio:
            soup_anuncio = parsing(resposta_anuncio)
            telefones = encontrar_telefones(soup_anuncio)
            if telefones:
                for telefone in telefones:
                    print("Telefone encontrado:", telefone)
                    TELEFONES.append(telefone)
                    salvar_telefones(telefone)


def salvar_telefones(telefone):
    string_telefone = "{}{}{}\n".format(telefone[0], telefone[1], telefone[2])
    try:
        with open("telefones.csv", "a") as arquivo:
            arquivo.write(string_telefone)
    except Exception as error:
        print("Erro ao tentar salvar telefone: {}".format(error))


if __name__ == "__main__":
    resposta_busca = request(URL_AUTOMOVEIS)
    if resposta_busca:
        soup_busca = parsing(resposta_busca)
        if soup_busca:
            LINKS = encontrar_links(soup_busca)

            THREADS = []

            # Cria as threads
            for i in range(5):
                t = threading.Thread(target=descobrir_telefones)
                THREADS.append(t)

            # Inicia as threads
            for t in THREADS:
                t.start()

            # espera as threads acabarem
            for t in THREADS:
                t.join()


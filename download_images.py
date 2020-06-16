#!/usr/bin/env python3

# lib para regex
import re

# lib para lidar com a execução do script pelo sistema operacional
import sys

# path: lib para trabalhar com arquivos e diretórios
from os import path

# funções de tempo
import time

# lib para trabalhar com requisições web
import requests

# utilitarios do python para lidar com funcões e processamento paralelo
from functools import partial
from concurrent.futures import ThreadPoolExecutor

# lib para manipular o navegador
import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# regex para pegar as URLs das imagens
pattern = re.compile(r'<img [^>]*src="([^"]+)')
# identificador para o bloco onde estão as imagens no Google Images
css_locator = 'div[data-cid="GRID_STATE0"]'


# função para baixar e salvar uma imagem
def download_image(url, filename):
    if 'http' not in url:
        # garante que só urls válidas serão usadas
        return

    # requests.get "acessa" a url e baixa o código dela.
    # Caso for arquivo, baixa o arquivo
    image = requests.get(url)

    with open(filename, 'wb') as file:      # abre o arquivo em modo de escrita
        file.write(image.content)           # salva a imagem que foi baixada no arquivo aberto
        print('filename created: {}'.format(filename))


def main(dst_path, url):
    # inicia o driver (abre o browser)
    print('Opening Chrome using selenium')
    driver = selenium.webdriver.Chrome()

    # navega para uma URL
    print('Navigating to {}'.format(url))
    driver.get(url)

    # fica esperando algo acontecer no maximo 10seg, no caso fica esperando carregar o bloco de imagens
    print('waiting for page')
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, css_locator))
    )

    #### Workaround para carregar as imagens dinamicamente no google images.
    #### Ele só carrega uma parte, então é preciso ir para o final da página para ele
    #### carregar mais imagens
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        print('loading more images...')
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            break
        last_height = new_height

    # pega somente o bloco onde estão as imagens e depois pega o código fonte que foi
    # gerado dinamicamente pelo javascript
    print('getting the source code')
    body = driver.find_element_by_css_selector(css_locator)
    source_code = body.get_attribute('innerHTML')

    # Já temos o HTML com as imagens, não é mais necessário o selenium.
    # Então vamos fechar
    print('closing Chrome')
    driver.close()

    # baseado no regex, extrai somente as URLs das imagens e joga em uma lista
    images = pattern.findall(source_code)
    print('{} images found'.format(len(images)))

    # bloco que inicia um proceso paralelo usando o máximo de threads para o computador
    with ThreadPoolExecutor() as executor:
        # navega entre as imagens
        for index, image_url in enumerate(images, 1):
            # gera o nome do arquivo baseado no tempo em segundos atual desde 01/01/1970 00h00m00s
            filename = '{}/img_{}.jpg'.format(dst_path, time.time())

            # gera o caminho absoluto do arquivo baseado no path.
            # isso permite que o script possa ser rodado a partir de qualquer lugar,
            # bastando estar no PATH
            filename = path.normpath(path.join(path.abspath('.'), filename))

            # executa a funcao download_image em uma thread disponível passando
            # a url da imagem e onde o arquivo deve ser salvo
            executor.submit(partial(download_image, image_url, filename)).result()


# executa esse bloco se for executado como script
if __name__ == '__main__':
    dst_path = sys.argv[1]
    google_images_url = sys.argv[2]

    main(dst_path, google_images_url)
 
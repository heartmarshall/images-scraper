import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import urllib.request
import os


def sort_pics(pics_dir):  # сортирует картинки по размеру
    return


# Параметры работы программы:
download_dir = "C:\\playground\\pics_parser\\pics\\"  # куда будут скачиваться картинки
existed_pics = [re.match(r'(.*\.png|.*\.jpg)', i).group() for i in os.listdir(download_dir)]
# existed_pics - картинки, которые уже есть на компьютере, чтобы не скачивать их повторно.
url = 'https://boards.4channel.org/w/thread/2198850/vector-thread-requests-sharing'  # откуда скачиваем

base_url = re.match(r'^(http:\/\/|https:\/\/)?[^\/: \n]*', url).group()  # корневой адрес сайта
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
links = []
founded_pics = []
for link in soup.find_all('a'):
    links.append(urljoin(base_url, link.get('href')))
for link in soup.find_all('img'):
    links.append(urljoin(base_url, link.get('src')))

download_links = {}
for link in links:  # задаём словарь вида {ссылка : имя файла} из тех ссылок, которые ведут на картинки
    if re.match(r'(.*\.png|.*\.jpg)', link):
        download_links[link] = re.search(r'[^/]*\.(png|jpg)', link).group()

pic_counter = 0  # счетчик скаченных картинок
for link, pic_name in download_links.items():  # скачиваем картинки
    if pic_name not in existed_pics:
        with open(download_dir + pic_name, "wb") as file:
            response = requests.get(link)
            file.write(response.content)
            pic_counter += 1

print('Всего новых файлов скачено:', pic_counter)

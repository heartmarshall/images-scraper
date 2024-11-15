# TODO: limitation on the size of the downloaded image
# TODO: run a benchmark: download + then sort OR download and sort at the same time

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import urllib.request
import os
from tqdm import tqdm
from pathlib import Path
from collections import deque



class ImagesScrapper:
    def __init__(self, url: str, output_dir: Path, buffer_size: int,):
        self.url = url
        self.output_dir = output_dir
        self.buffer_size = buffer_size
        self.buffer = deque()

    def reset_url(self, new_url):
        self.url = new_url
        self.buffer.clear()

    def parse(self):
        pass

    def download_images(self):
        pass

    def _dump_buffer(self):
        pass

def sort_files(sorting_dir, files_list):
    """
    Раскладывает файлы по трём папкам: large, medium, small

    :param sorting_dir: директория в которой лежат файлы, которые нужно рассортировать
    :param files_list: список файлов, которые будут рассортрованы
    """
    for dir_name in ["large", "medium", "small"]:
        try:
            os.mkdir(os.path.join(sorting_dir, dir_name))
        except FileExistsError:
            pass
    for file_name in files_list:
        file_size = os.stat(os.path.join(sorting_dir, file_name)).st_size
        print(file_size)
        if file_size >= 1048576:
            category = "large"
        elif 512000 <= file_size < 1048576:
            category = "medium"
        else:
            category = "small"
        os.replace(os.path.join(sorting_dir, file_name), os.path.join(sorting_dir, category, file_name))
    return


# Параметры работы программы:
# Директория, куда будут загружаться файлы. Если такой нет, то она будет создана.
download_dir = "downloaded_pics"
parent_dir = os.getcwd()
download_path = os.path.join(parent_dir, download_dir)
try:
    os.mkdir(download_path)
except FileExistsError:
    pass
print("Картинки будут загружены в папку: {}".format(download_path))

existed_pics = [re.match(r'(.*\.png|.*\.jpg)', file_name).group() for file_name in os.listdir(download_path)]
# existed_pics - картинки, которые уже есть в заданной директории, узнаём их чтобы не скачивать повторно.

# откуда скачиваем
url = 'https://boards.4channel.org/w/thread/2198850/vector-thread-requests-sharing'

# корневой адрес сайта
base_url = re.match(r'^(http:\/\/|https:\/\/)?[^\/: \n]*', url).group()
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
links = []
founded_pics = []
for link in soup.find_all('a'):
    links.append(urljoin(base_url, link.get('href')))
for link in soup.find_all('img'):
    links.append(urljoin(base_url, link.get('src')))

download_links = {}
# задаём словарь вида {ссылка : имя файла} из тех ссылок, которые ведут на картинки
for link in links:
    if re.match(r'(.*\.png|.*\.jpg)', link):
        download_links[link] = re.search(r'[^/]*\.(png|jpg)', link).group()

pic_counter = 0  # счетчик скаченных картинок
for link, pic_name in tqdm(download_links.items()):  # скачиваем картинки
    if pic_name not in existed_pics:
        with open(os.path.join(download_path, pic_name), "wb") as file:
            response = requests.get(link)
            file.write(response.content)
            pic_counter += 1

print("Всего новых файлов скачено:", pic_counter)
print("Начинаю сортировку файлов...")
sort_files(download_path, download_links.values())
print("Сортировка закончена! Программа завершена")

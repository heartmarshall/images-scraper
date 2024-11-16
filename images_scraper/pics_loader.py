import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from pathlib import Path
from collections import deque
from typing import List
import cssutils


class ImagesDownloader:
    def __init__(self, urls: List[str], output_dir: Path, buffer_size: int, min_img_size: int, max_img_size: int):
        self.urls = urls
        self.output_dir = output_dir
        self.buffer_size = buffer_size
        self.buffer = deque() 
        self.current_buffer_size = 0
        self.min_img_size = min_img_size
        self.max_img_size = max_img_size
    
    def _save_image(self, image_data: bytes, image_name: str):
        output_path = self.output_dir / image_name
        with open(output_path, 'wb') as f:
            f.write(image_data)

    def _get_file_name_from_url(self, url: str) -> str:
        return Path(url).name
    
    def _is_valid_image(self, image_data: bytes) -> bool:
        size = len(image_data)
        return self.min_img_size <= size <= self.max_img_size

    def _save_buffer(self):
        print(f"Saving {len(self.buffer)} images from the buffer...")
        while self.buffer:
            file_name, image_data = self.buffer.popleft()
            self._save_image(image_data, file_name)
        self.current_buffer_size = 0

    def download_all(self):
        for url in self.urls:
            try:
                response = requests.get(url, stream=True)
                response.raise_for_status()
                image_data = response.content

                if self._is_valid_image(image_data):
                    file_name = self._get_file_name_from_url(url)
                    self.buffer.append((file_name, image_data))
                    self.current_buffer_size += len(image_data)
                    print(f"Added to buffer: {file_name} (size: {len(image_data)} bytes)")

                    if self.current_buffer_size >= self.buffer_size:
                        self._save_buffer()
                else:
                    print(f"Image from {url} does not meet size requirements")
            except Exception as e:
                print(f"Error downloading {url}: {e}")

        if self.buffer:
            self._save_buffer()


class ImagesScrapper:
    def __init__(self, url: str, imgs_exts={'jpg', 'png', 'bmp'}):
        self.url = url
        self.imgs_exts = imgs_exts

    def reset_url(self, new_url: str):
        self.url = new_url

    def _get_css_images(self, css_url: str) -> List[str]:
        try:
            response = requests.get(css_url)
            response.raise_for_status()
            css_content = response.text

            parser = cssutils.CSSParser()
            css_sheet = parser.parseString(css_content)

            img_urls = set()

            for rule in css_sheet.cssRules:
                if isinstance(rule, cssutils.css.CSSStyleRule):
                    style = rule.style
                    for property in style:
                        if property.name == 'background-image':
                            url_match = property.value.strip().strip('url(")').strip('url(\')')
                            if any(url_match.lower().endswith(ext) for ext in self.imgs_exts):
                                img_urls.add(url_match)

            return list(img_urls)
        except Exception as e:
            print(f"Error processing CSS {css_url}: {e}")
            return []

    def parse(self) -> List[str]:
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            img_urls = set()

            for tag in soup.find_all(True):
                for attr in ['src', 'href', 'data-src', 'data-href']:
                    if attr in tag.attrs:
                        link = tag.attrs[attr]
                        if any(link.lower().endswith(ext) for ext in self.imgs_exts):
                            img_urls.add(link)

            css_links = [
                link['href'] for link in soup.find_all('link', rel='stylesheet') if 'href' in link.attrs
            ]
            for css_url in css_links:
                if not css_url.startswith('http'):
                    css_url = requests.compat.urljoin(self.url, css_url)
                img_urls.update(self._get_css_images(css_url))

            return list(img_urls)
        except Exception as e:
            print(f"Error parsing {self.url}: {e}")
            return []

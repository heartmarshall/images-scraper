from images_scraper.images_scraper import ImagesDownloader, ImagesScrapper
from pathlib import Path

scraper = ImagesScrapper('https://example.com')
image_urls = scraper.parse()

downloader = ImagesDownloader(
    urls=image_urls,
    output_dir=Path('./images'),
    buffer_size=10_000_000,
    min_img_size=1000,
    max_img_size=5_000_000 
)
downloader.download_all()
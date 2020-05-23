import os
import re
import urllib.parse
import urllib.request
from zipfile import ZipFile

from bs4 import BeautifulSoup
import progressbar


def download_files(librivox_url, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    with urllib.request.urlopen(librivox_url) as f:
        librivox_soup = BeautifulSoup(f.read(), 'lxml')

    gutenberg_link = librivox_soup.find('a', {'href': re.compile(r'http://www.gutenberg.org/.*')})
    if gutenberg_link is None:
        print('Link to the gutenberg.org is not found. Text will not be downloaded.')
    else:
        print('Downloading text...')
        gutenberg_url = gutenberg_link['href']

        with urllib.request.urlopen(gutenberg_url) as f:
            gutenberg_soup = BeautifulSoup(f.read(), 'lxml')

        text_relative_url = gutenberg_soup.find('a', {'type': re.compile(r'text/plain.*')})['href']
        text_absolute_url = urllib.parse.urljoin('http://www.gutenberg.org/', text_relative_url)
        text_path = os.path.join(output_dir, 'text.txt')

        urllib.request.urlretrieve(text_absolute_url, text_path, reporthook=ProgressBar())

        print(f'Text has been downloaded and saved as {text_path}')

    print('Downloading audio...')

    book_url = librivox_soup.find('a', class_='book-download-btn')['href']
    local_filename, _ = urllib.request.urlretrieve(book_url, reporthook=ProgressBar())

    audio_dir = os.path.join(output_dir, 'audio')

    with ZipFile(local_filename) as z:
        z.extractall(path=audio_dir)

    print(f'Audio has been downloaded and saved to {audio_dir}')


class ProgressBar():
    def __init__(self):
        self.pbar = None

    def __call__(self, block_num, block_size, total_size):
        if self.pbar is None:
            self.pbar = progressbar.ProgressBar(maxval=total_size)
            self.pbar.start()

        downloaded = block_num * block_size

        if downloaded < total_size:
            self.pbar.update(downloaded)
        else:
            self.pbar.finish()
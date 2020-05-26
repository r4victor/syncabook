import json
import os.path
import re
import urllib.parse
import urllib.request
from zipfile import ZipFile

from bs4 import BeautifulSoup
import progressbar


# synclibrivox repo parameters
GITHUB_CONTENTS_URL = f'https://api.github.com/repos/r4victor/synclibrivox/contents/'
MAPPING_FILE = 'map.json'
BOOKS_DIR = 'books'


def download_files(librivox_url, output_dir, skip_text, skip_audio):
    """
    Downloads files needed to create an ebook.

    The downloading process looks as follows:
    Download files from the synclibrivox repository.
    If a book is not found there, download plaintext transcript from gutenberg.org.
    Download audio files from librivox.org.
    """
    os.makedirs(output_dir, exist_ok=True)

    with urllib.request.urlopen(librivox_url) as f:
        librivox_soup = BeautifulSoup(f.read(), 'lxml')

    if not skip_text:
        print('Searching for files in the synclibrivox repository...')
        found = _download_synclibrivox_files(librivox_url, output_dir)
        if found:
            print(
                f'This book has been found in the synclibrivox repository.'
                f' Corresponding files have been downloaded to {output_dir}.'
            )
        else:
            print(
                f'The synclibrivox repository doesn\'t contain this book.\n'
                'Downloading text from gutenberg.org...'
            )
            gutenberg_link = librivox_soup.find(
                'a', {'href': re.compile(r'http://www.gutenberg.org/.*')}
            )
            if gutenberg_link is None:
                print('Link to the gutenberg.org is not found. Text won\'t be downloaded.')
            else:
                gutenberg_url = gutenberg_link['href']
                _download_gutenberg_text(gutenberg_url, output_dir)

    if not skip_audio:
        print('Downloading audio files...')
        audiobook_url = librivox_soup.find('a', class_='book-download-btn')['href']
        _download_audio_files(audiobook_url, output_dir)


def _download_synclibrivox_files(librivox_url, output_dir):
    """
    Downloads files from synclibrivox repository for a book with corresponding `librivox_url`.
    If a book is not found in the repository, returns False.
    Otherwise, returns True.
    """
    book_dir = _get_book_dir(librivox_url)
    if book_dir is None:
        return False
    
    book_path = os.path.join(BOOKS_DIR, book_dir)
    _download_github_directory(book_path, relative_to=book_path, output_dir=output_dir)
    return True


def _download_github_directory(path, relative_to='', output_dir=''):
    url = urllib.parse.urljoin(GITHUB_CONTENTS_URL, path)
    with urllib.request.urlopen(url) as f:
        contents = json.loads(f.read())

    os.makedirs(os.path.join(output_dir, os.path.relpath(path, relative_to)), exist_ok=True)

    for content in contents:
        if content['type'] == 'file':
            urllib.request.urlretrieve(
                content['download_url'],
                os.path.join(output_dir, os.path.relpath(content['path'], relative_to))
            )
        elif content['type'] == 'dir':
            _download_github_directory(content['path'], relative_to=relative_to, output_dir=output_dir)


def _get_book_dir(librivox_url):
    return json.loads(_get_github_file_contents(MAPPING_FILE)).get(librivox_url)


def _get_github_file_contents(file_path):
    file_url = urllib.parse.urljoin(GITHUB_CONTENTS_URL, file_path)
    with urllib.request.urlopen(file_url) as f:
        download_url = json.loads(f.read())['download_url']

    with urllib.request.urlopen(download_url) as f:
        return f.read()


def _download_gutenberg_text(gutenberg_url, output_dir):
    with urllib.request.urlopen(gutenberg_url) as f:
        gutenberg_soup = BeautifulSoup(f.read(), 'lxml')

    text_relative_url = gutenberg_soup.find('a', {'type': re.compile(r'text/plain.*')})['href']
    text_absolute_url = urllib.parse.urljoin('http://www.gutenberg.org/', text_relative_url)
    text_path = os.path.join(output_dir, 'text.txt')

    urllib.request.urlretrieve(text_absolute_url, text_path, reporthook=ProgressBar())
    print(f'Text has been downloaded and saved as {text_path}')


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


def _download_audio_files(audiobook_url, output_dir):
    local_filename, _ = urllib.request.urlretrieve(audiobook_url, reporthook=ProgressBar())

    audio_dir = os.path.join(output_dir, 'audio')

    with ZipFile(local_filename) as z:
        z.extractall(path=audio_dir)
    print(f'Audio files have been downloaded to {audio_dir}')

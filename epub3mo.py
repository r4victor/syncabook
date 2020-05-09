import argparse
from datetime import date, datetime, timedelta
import json
import os.path
import math
import re
import shutil
import subprocess
import urllib.request
import urllib.parse
import uuid
from zipfile import ZipFile

from bs4 import BeautifulSoup
import jinja2


def get_book(librivox_url, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    with urllib.request.urlopen(librivox_url) as f:
        librivox_soup = BeautifulSoup(f.read(), 'lxml')

    # download text
    gutenberg_url = librivox_soup.find('a', {'href': re.compile(r'http://www.gutenberg.org/.*')})['href']

    with urllib.request.urlopen(gutenberg_url) as f:
        gutenberg_soup = BeautifulSoup(f.read(), 'lxml')

    text_relative_url = gutenberg_soup.find('a', {'type': re.compile(r'text/plain.*')})['href']
    text_absolute_url = urllib.parse.urljoin('http://www.gutenberg.org/', text_relative_url)
    text_path = os.path.join(output_dir, 'text.txt')

    urllib.request.urlretrieve(text_absolute_url, text_path)

    # download audiobook
    book_url = librivox_soup.find('a', class_='book-download-btn')['href']
    local_filename, _ = urllib.request.urlretrieve(book_url)

    audio_dir = os.path.join(output_dir, 'audio')

    with ZipFile(local_filename) as z:
        z.extractall(path=audio_dir)


def split_text(text_file, output_dir, mode, pattern, n):
    with open(text_file, 'r') as f:
            text = f.read()

    if mode in ['opening', 'delimeter'] and pattern is None:
        print(f'\nERROR: --pattern is required in {mode} mode.\n')
        return

    if mode == 'opening':
        n_files = split_text_by_opening(pattern, text, output_dir)
    elif mode == 'delimeter':
        n_files = split_text_by_delimeter(pattern, text, output_dir)
    elif mode == 'equal':
        if n is None:
            print(f'\nERROR: --n is required in {mode} mode.\n')
        
        n_files = split_text_into_n_parts(n, text, output_dir)

    if n_files > 0:
        print(f'\nSplitting into {n_files} files is performed.\n')


def split_text_by_opening(split_pattern, text, output_dir):
    openings = re.findall(split_pattern, text)

    if len(openings) == 0:
        print(
            f'\nERROR: No text matching pattern "{split_pattern}". '
            'Splitting is not permformed.\n'
        )
        return

    texts = re.split(split_pattern, text)
    texts = [d + t for d, t in zip(openings, texts[1:])]

    save_texts(texts, output_dir)

    return len(texts)


def split_text_by_delimeter(split_pattern, text, output_dir):
    texts = re.split(split_pattern, text)

    if len(texts) == 0:
        print(
            f'\nERROR: No text matching pattern "{split_pattern}". '
            'Splitting is not permformed.\n'
        )
        return

    save_texts(texts, output_dir)

    return len(texts)


def split_text_into_n_parts(n, text, output_dir):
    l = len(text) // n

    texts = []

    j = 0
    for i in range(len(text)):
        if i >= l + j and text[i] == text[i+1] == '\n':
            texts.append(text[j:i+2])
            j = i + 2

    texts.append(text[j:])

    save_texts(texts, output_dir)

    return len(texts)


def save_texts(texts, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    for i, text in enumerate(texts, start=1):
        n = get_number_of_digits_to_name(len(texts))
        file_path = os.path.join(output_dir, f'{i:0>{n}}.txt')
        with open(file_path, 'w') as f:
            f.write(text)


def textfiles_to_xhtmls(input_dir, output_dir, fragment_type):
    os.makedirs(output_dir, exist_ok=True)

    input_filenames = sorted(x for x in os.listdir(input_dir) if x.endswith('.txt'))

    texts = []
    for filename in input_filenames:
        file_path = os.path.join(input_dir, filename)
        with open(file_path, 'r') as f:
            texts.append(f.read())
    
    # fragment texts
    contents = []
    for text in texts:
        paragraphs_contents = [p.strip().replace('\n', ' ') for p in text.split('\n\n') if p.strip()]
        paragraphs = []
        for p in paragraphs_contents:
            if fragment_type == 'sentence':
                fragments = get_sentences(p)
            else:
                # use paragraphs as fragments
                fragments = [p]
            paragraphs.append(fragments)
        contents.append(paragraphs)

    # calculate total number of fragments
    fragments_num = sum(sum(sum(len(fs) for f in fs) for fs in ps) for ps in contents)
    n = get_number_of_digits_to_name(fragments_num)

    # render xhtmls
    xhtmls = []
    fragment_id = 1
    for ps in contents:
        paragraphs = []
        for fs in ps:
            fragments = []
            for f in fs:
                fragments.append({'id': f'f{fragment_id:0>{n}}', 'text': f})
                fragment_id += 1
            paragraphs.append(fragments)
        
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader('templates/'),
            autoescape=True
        )
        template = env.get_template('text.xhtml')
        xhtml = template.render(paragraphs=paragraphs)
        xhtmls.append(xhtml)

    for filename, xhtml in zip(input_filenames, xhtmls):
        file_path = os.path.join(output_dir, f'{drop_ext(filename)}.xhtml')
        with open(file_path, 'x') as f:
            f.write(xhtml)


def get_sentences(text):
    """
    Fragment by "{sentence_ending_char}{space}"
    """
    sentence_endings = {'.', '!', '?'}
    fragments = []
    sentence_start_idx = 0
    sentence_ended = False
    for i, c in enumerate(text):
        if i == len(text) - 1:
            fragments.append(text[sentence_start_idx:i+1])
        if c in sentence_endings:
            sentence_ended = True
            continue
        if sentence_ended and c == ' ':
            fragments.append(text[sentence_start_idx:i+1])
            sentence_start_idx = i+1
        sentence_ended = False
    return fragments


def create_ebook(audio_dir, text_dir, metadatafile, output_dir):
    tmp_dir = os.path.join(output_dir, 'tmp')

    # initialize epub files
    container_dir = os.path.join(tmp_dir, 'container')
    epub_dir = os.path.join(container_dir, 'epub')
    epub_audio_dir = os.path.join(epub_dir, 'audio')
    epub_text_dir = os.path.join(epub_dir, 'text')
    epub_smil_dir = os.path.join(epub_dir, 'smil')
    epub_styles_dir = os.path.join(epub_dir, 'styles')

    os.makedirs(container_dir)
    os.makedirs(epub_dir)
    os.makedirs(os.path.join(container_dir, 'META-INF'))
    os.makedirs(epub_audio_dir)
    os.makedirs(epub_text_dir)
    os.makedirs(epub_styles_dir)

    shutil.copy('templates/mimetype', os.path.join(container_dir, 'mimetype'))
    shutil.copy('templates/container.xml', os.path.join(container_dir, 'META-INF', 'container.xml'))
    shutil.copy('templates/style.css', os.path.join(epub_styles_dir, 'style.css'))

    audiofiles_num = len(list(os.listdir(audio_dir)))
    textfiles_num = len(list(os.listdir(text_dir)))
    assert audiofiles_num == textfiles_num
    n = get_number_of_digits_to_name(textfiles_num)

    # copy resources to epub
    for i, audiofile in enumerate(sorted(os.listdir(audio_dir)), start=1):
        shutil.copy(os.path.join(audio_dir, audiofile), os.path.join(epub_audio_dir, f'{i:0>{n}}.mp3'))

    for i, textfile in enumerate(sorted(os.listdir(text_dir)), start=1):
        shutil.copy(os.path.join(text_dir, textfile), os.path.join(epub_text_dir, f'{i:0>{n}}.xhtml'))

    # create SMIL using aeneas
    job_dir = os.path.join(tmp_dir, 'job')
    job_resources_dir = os.path.join(job_dir, 'resources')

    os.makedirs(job_resources_dir, exist_ok=True)
    shutil.copy('templates/config.txt', job_dir)
    
    for audiofile in os.listdir(epub_audio_dir):
        shutil.copy(os.path.join(epub_audio_dir, audiofile), job_resources_dir)

    for textfile in os.listdir(epub_text_dir):
        shutil.copy(os.path.join(epub_text_dir, textfile), job_resources_dir)

    subprocess.run(['python', '-m', 'aeneas.tools.execute_job', '-v', job_dir, epub_dir])

    # shutil.rmtree(tmp_dir)

    # create package document
    audios = [
        {
            'name': filename,
            'id': f'audio{drop_ext(filename)}',
        }
        for filename in sorted(os.listdir(epub_audio_dir))
    ]

    texts = [
        {
            'name': filename,
            'id': f'text{drop_ext(filename)}',
            'smil_id': f'smil{drop_ext(filename)}',
        }
        for filename in sorted(os.listdir(epub_text_dir))
    ]

    smils = [
        {
            'name': filename,
            'id': f'smil{drop_ext(filename)}',
        }
        for filename in sorted(os.listdir(epub_smil_dir))
    ]

    # calculate durations of Media Overlays
    media_durations = [
        get_duration(os.path.join(epub_smil_dir, filename))
        for filename in sorted(os.listdir(epub_smil_dir))
    ]
    total_duration = format_duration(sum(media_durations, timedelta()))

    medias = [
        {
            'duration': format_duration(duration),
            'smil_id': f'smil{drop_ext(filename)}',
        }
        for filename, duration in zip(sorted(os.listdir(epub_smil_dir)), media_durations)
    ]

    with open(metadatafile, 'r') as f:
        metadata = json.load(f)

    env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates/'))
    opf_template = env.get_template('content.opf')
    opf_content = opf_template.render({
        'uuid': metadata.get('uuid', uuid.uuid4()),
        'title': metadata['title'],
        'author': metadata['author'],
        'description': metadata.get('description', 'No description'),
        'narrator': metadata['narrator'],
        'contributor': metadata.get('contributor', 'Unknown'),
        'date': metadata.get('date', date.today().isoformat()),
        'modified': datetime.now().isoformat(' ', 'seconds'),
        'texts': texts,
        'audios': audios,
        'smils': smils,
        'medias': medias,
        'total_duration': total_duration,
    })
    with open(os.path.join(epub_dir, 'content.opf'), 'x') as f:
        f.write(opf_content)

    shutil.copy('templates/nav.xhtml', os.path.join(epub_text_dir, 'nav.xhtml'))

    # create epub archive
    with ZipFile(os.path.join(output_dir, 'ebook.epub'), 'x') as z:
        # mimetype must be first file in archive
        z.writestr('mimetype', 'application/epub+zip')
        z.write(os.path.join(container_dir, 'META-INF', 'container.xml'), 'META-INF/container.xml')
        for dirpath, _, filenames in os.walk(epub_dir):
            for filename in filenames:
                arcname = os.path.join(os.path.relpath(dirpath, container_dir), filename)
                z.write(os.path.join(dirpath, filename), arcname)


def get_number_of_digits_to_name(num):
    return math.floor(math.log10(num)) + 1


def drop_ext(filename):
    return filename.split('.')[0]


def get_duration(smil_file_path):
    with open(smil_file_path, 'r') as f:
        soup = BeautifulSoup(f.read(), 'xml')

    clips = soup.find_all('audio')
    return sum(
        [parse_clockvalue(clip['clipEnd']) - parse_clockvalue(clip['clipBegin']) for clip in clips],
        timedelta(0)
    )


def format_duration(tdelta):
    hours = int(tdelta.total_seconds()) // 3600
    minutes = int(tdelta.total_seconds() % 3600) // 60
    seconds = int(tdelta.total_seconds()) % 60
    ms = int(tdelta.microseconds) // 1000
    return f'{hours:d}:{minutes:0>2d}:{seconds:0>2d}.{ms:0>3d}'


def parse_clockvalue(clockvalue):
    pattern = r'(?P<h>\d+):(?P<m>\d\d):(?P<s>\d\d).(?P<ms>\d\d\d)'
    m = re.match(pattern, clockvalue)
    return timedelta(
        hours=int(m.group('h')), minutes=int(m.group('m')),
        seconds=int(m.group('s')), milliseconds=int(m.group('ms'))
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command', required=True)

    parser_split = subparsers.add_parser('get')
    parser_split.add_argument('librivox_url')
    parser_split.add_argument('output_dir')

    parser_split = subparsers.add_parser(
        'split_text',
        description='Split single text file into multiple files.'
    )
    parser_split.add_argument('textfile')
    parser_split.add_argument('output_dir')
    parser_split.add_argument(
        '--mode', dest='mode', choices=['delimeter', 'opening', 'equal'], default='opening',
        help=(
            'opening mode splits text file by opening PATTERN, i.e. '
            'each file begins with a PATTERN.\n'
            'delimeter mode splits text file using PATTERN.\n'
            'equal mode splits text file into N equal parts.'
        ),
    )
    parser_split.add_argument('--n', dest='n', type=int)
    parser_split.add_argument('--pattern', dest='pattern')

    parser_to_xhtml = subparsers.add_parser('to_xhtml')
    parser_to_xhtml.add_argument('input_dir')
    parser_to_xhtml.add_argument('output_dir')
    parser_to_xhtml.add_argument(
        '--fragment-type', choices=['sentence', 'paragraph'],
        dest='fragment_type', default='sentence'
    )

    parser_create = subparsers.add_parser('create')
    parser_create.add_argument('book_dir')

    args = parser.parse_args()

    if args.command == 'get':
        get_book(args.librivox_url, args.output_dir)
    elif args.command == 'split_text':
        split_text(args.textfile, args.output_dir, args.mode, args.pattern, args.n)
    elif args.command == 'to_xhtml':
        textfiles_to_xhtmls(args.input_dir, args.output_dir, args.fragment_type)
    elif args.command == 'create':
        audio_dir = os.path.join(args.book_dir, 'audio')
        text_dir = os.path.join(args.book_dir, 'text')
        metadatafile = os.path.join(args.book_dir, 'metadata.json')
        output_dir = os.path.join(args.book_dir, 'out')
        create_ebook(audio_dir, text_dir, metadatafile, output_dir)

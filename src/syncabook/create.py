from datetime import date, datetime, timedelta
import json
import os.path
import re
import shutil
import uuid
from zipfile import ZipFile

from bs4 import BeautifulSoup
import jinja2

from . import TEMPLATES_DIR
from .sync import sync
from .utils import drop_extension, format_duration


def create_ebook(book_dir, alignment_radius=None, alignment_skip_penalty=None, language='eng'):
    audio_dir = os.path.join(book_dir, 'audio')
    sync_text_dir = os.path.join(book_dir, 'sync_text')
    no_sync_text_dir = os.path.join(book_dir, 'no_sync_text')
    smil_dir = os.path.join(book_dir, 'smil')
    images_dir = os.path.join(book_dir, 'images')
    metadatafile = os.path.join(book_dir, 'metadata.json')
    output_dir = os.path.join(book_dir, 'out')

    tmp_dir = os.path.join(output_dir, 'tmp')

    os.makedirs(no_sync_text_dir, exist_ok=True)

    # create SMIL files using afaligner
    if not os.path.isdir(smil_dir) or len(list(os.listdir(smil_dir))) == 0:
        print('❗ SMIL files are not found. Synchronizing...')
        sync(
            book_dir,
            alignment_radius=alignment_radius,
            alignment_skip_penalty=alignment_skip_penalty,
            language=language,
        )
    else:
        print(f'✔ Using existing SMIL files from {smil_dir}.')

    try:
        with open(metadatafile, 'r') as f:
            metadata = json.load(f)
    except FileNotFoundError:
        print('❗ File metadata.json is not found. Please provide metadata')
        metadata = {}
        metadata['title'] = input('Title: ')
        metadata['author'] = input('Author: ')
        metadata['description'] = input('Description: ')
        metadata['narrator'] = input('Narrator: ')
        metadata['contributor'] = input('Contributor: ')
        metadata['transcriber'] = input('Transcriber: ')
        with open(metadatafile, 'w') as f:
            json.dump(metadata, f, indent=2)
        print('✔ File metadata.json is created.')

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATES_DIR), autoescape=True)

    # create ToC file if doesn't exist
    nav_path = os.path.join(no_sync_text_dir, 'nav.xhtml')
    if not os.path.exists(nav_path):
        print(f'❗ File {nav_path} is not found. Creating...')
        content_files = []
        for i, filename in enumerate(sorted(os.listdir(sync_text_dir)), start=1):
            with open(os.path.join(sync_text_dir, filename)) as f:
                soup = BeautifulSoup(f.read(), 'xml')
            heading = soup.find('h2')
            content_files.append({
                'name': filename,
                'toc_name': heading.string if heading is not None else i
            })
        nav_template = env.get_template('nav.xhtml')
        nav_content = nav_template.render(content_files=content_files)
        with open(nav_path, 'x') as f:
            f.write(nav_content)

        print(f'✔ File {nav_path} has been created. You may want to make some changes.')
        input('Press any key to proceed:')

    # create colophon file if doesn't exist
    colophon_path = os.path.join(no_sync_text_dir, 'colophon.xhtml')
    if not os.path.exists(colophon_path):
        print(f'File {colophon_path} is not found. Creating...')
        colophon_template = env.get_template('colophon.xhtml')
        colophon_content = colophon_template.render(
            title=metadata['title'],
            author=metadata['author'],
            contributor=metadata.get('contributor', 'me'),
            transcriber=metadata.get('transcriber', 'someone')
        )
        with open(colophon_path, 'x') as f:
            f.write(colophon_content)

        print(f'✔ File {colophon_path} has been created. You may want to make some changes.')
        input('Press any key to proceed:')

    # initialize epub files
    container_dir = os.path.join(tmp_dir, 'container')
    epub_dir = os.path.join(container_dir, 'epub')
    epub_audio_dir = os.path.join(epub_dir, 'audio')
    epub_text_dir = os.path.join(epub_dir, 'text')
    epub_smil_dir = os.path.join(epub_dir, 'smil')
    epub_styles_dir = os.path.join(epub_dir, 'styles')
    epub_images_dir = os.path.join(epub_dir, 'images')

    os.makedirs(container_dir)
    os.makedirs(epub_dir)
    os.makedirs(os.path.join(container_dir, 'META-INF'))
    os.makedirs(epub_audio_dir)
    os.makedirs(epub_text_dir)
    os.makedirs(epub_smil_dir)
    os.makedirs(epub_styles_dir)
    os.makedirs(epub_images_dir)

    shutil.copy(
        os.path.join(TEMPLATES_DIR, 'mimetype'),
        os.path.join(container_dir, 'mimetype')
    )
    shutil.copy(
        os.path.join(TEMPLATES_DIR, 'container.xml'),
        os.path.join(container_dir, 'META-INF', 'container.xml')
    )
    shutil.copy(
        os.path.join(TEMPLATES_DIR, 'style.css'),
        os.path.join(epub_styles_dir, 'style.css')
    )

    # copy resources to epub
    for from_, to in (
        (audio_dir, epub_audio_dir), (sync_text_dir, epub_text_dir),
        (no_sync_text_dir, epub_text_dir), (smil_dir, epub_smil_dir),
        (images_dir, epub_images_dir)
    ):
        if os.path.exists(from_):
            for filename in os.listdir(from_):
                shutil.copy(os.path.join(from_, filename), os.path.join(to, filename))

    # create package document
    audios = [
        {
            'name': filename,
            'id': f'audio{drop_extension(filename)}',
        }
        for filename in sorted(os.listdir(epub_audio_dir))
    ]

    sync_texts = [
        {
            'name': filename,
            'id': f'text{drop_extension(filename)}',
            'smil_id': f'smil{drop_extension(filename)}',
        }
        for filename in os.listdir(sync_text_dir)
    ]

    no_sync_texts = [
        {
            'name': filename,
            'id': f'text{drop_extension(filename)}',
        }
        for filename in os.listdir(no_sync_text_dir) if filename != 'nav.xhtml'
    ]

    texts = sorted(sync_texts + no_sync_texts, key=lambda x: x['name'])

    smils = [
        {
            'name': filename,
            'id': f'smil{drop_extension(filename)}',
        }
        for filename in sorted(os.listdir(epub_smil_dir))
    ]

    # calculate durations of Media Overlays
    media_durations = [
        _get_media_duration(os.path.join(epub_smil_dir, filename))
        for filename in sorted(os.listdir(epub_smil_dir))
    ]
    total_duration = format_duration(sum(media_durations, timedelta()))

    medias = [
        {
            'duration': format_duration(duration),
            'smil_id': f'smil{drop_extension(filename)}',
        }
        for filename, duration in zip(sorted(os.listdir(epub_smil_dir)), media_durations)
    ]

    cover_path = os.path.join(images_dir, 'cover.jpg')
    include_cover = os.path.exists(cover_path)

    opf_template = env.get_template('content.opf')
    opf_content = opf_template.render({
        'uuid': metadata.get('uuid', uuid.uuid4()),
        'title': metadata['title'],
        'author': metadata['author'],
        'description': metadata['description'],
        'narrator': metadata['narrator'],
        'contributor': metadata.get('contributor', 'me'),
        'date': metadata.get('date', date.today().isoformat()),
        'modified': datetime.now().isoformat(' ', 'seconds'),
        'include_cover': include_cover,
        'texts': texts,
        'audios': audios,
        'smils': smils,
        'medias': medias,
        'total_duration': total_duration,
    })
    with open(os.path.join(epub_dir, 'content.opf'), 'x') as f:
        f.write(opf_content)

    # create epub archive
    ebook_path = os.path.join(output_dir, f'{_get_book_name(metadata["title"])}.epub')

    with ZipFile(ebook_path, 'w') as z:
        # mimetype must be first file in archive
        z.writestr('mimetype', 'application/epub+zip')
        z.write(os.path.join(container_dir, 'META-INF', 'container.xml'), 'META-INF/container.xml')
        for dirpath, _, filenames in os.walk(epub_dir):
            for filename in filenames:
                arcname = os.path.join(os.path.relpath(dirpath, container_dir), filename)
                z.write(os.path.join(dirpath, filename), arcname)

    shutil.rmtree(tmp_dir)

    print(f'✔ The ebook has been successfully created and saved as {ebook_path}')


def _get_media_duration(smil_file_path):
    with open(smil_file_path, 'r') as f:
        soup = BeautifulSoup(f.read(), 'xml')

    clips = soup.find_all('audio')
    return sum(
        [_parse_clockvalue(clip['clipEnd']) - _parse_clockvalue(clip['clipBegin']) for clip in clips],
        timedelta(0)
    )


def _parse_clockvalue(clockvalue):
    pattern = r'(?P<h>\d+):(?P<m>\d\d):(?P<s>\d\d).(?P<ms>\d\d\d)'
    m = re.match(pattern, clockvalue)
    return timedelta(
        hours=int(m.group('h')), minutes=int(m.group('m')),
        seconds=int(m.group('s')), milliseconds=int(m.group('ms'))
    )


def _get_book_name(title):
    return title.replace(' ', '_').lower()
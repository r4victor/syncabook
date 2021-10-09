import os.path
import shutil
import shutil

import pytest
from epubcheck import EpubCheck

from syncabook import download_files
from syncabook import create

from . import BASE_DIR


@pytest.mark.integration
def test_create_ebook():
    book_dir = os.path.join(BASE_DIR, 'resources/civil_disobedience/')
    if not os.path.exists(os.path.join(book_dir, 'audio')):
        download_files.download_files(
            'https://librivox.org/civil-disobedience-by-henry-david-thoreau/',
            book_dir, skip_text=True
        )
    smil_dir = os.path.join(book_dir, 'smil')

    try:
        create.create_ebook(book_dir)
    finally:
        # Remove smil dir so that the next time the test performs a sync again
        if os.path.exists(smil_dir):
            shutil.rmtree(smil_dir)
    
    res = EpubCheck(os.path.join(book_dir, 'out/on_the_duty_of_civil_disobedience.epub'))
    assert res.valid is True
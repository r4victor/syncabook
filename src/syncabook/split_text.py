import os
import re

from .utils import get_number_of_digits_to_name


def split_text(text_file, output_dir, mode, pattern, n):
    """
    Splits contents of `text_file` into several texts and saves them to `output_dir`.
    """
    with open(text_file, 'r') as f:
            text = f.read()

    if mode in ['opening', 'delimeter'] and pattern is None:
        print(f'\n❌ --pattern is required in {mode} mode.\n')
        return

    if mode == 'opening':
        texts = _split_text_by_opening(pattern, text)
    elif mode == 'delimeter':
        texts = _split_text_by_delimeter(pattern, text)
    elif mode == 'equal':
        if n is None:
            print(f'\n❌ --n is required in {mode} mode.\n')
            return

        texts = _split_text_into_n_parts(n, text, output_dir)
    else:
        print(f'\n❌ Unknown mode {mode}.\n')

    if len(texts) > 0:
        _save_texts(texts, output_dir)
        print(f'✔ Splitting into {len(texts)} files is performed.')


def _split_text_by_opening(pattern, text):
    """
    Splits text into parts identified by opening that matches `pattern`.
    For example, --pattern='\n\nCHAPTER \\d+\n\n' may be used
    to split text into chapters.
    """
    openings = re.findall(pattern, text)

    if len(openings) == 0:
        print(f'\n❗ No text matching pattern "{pattern}". Splitting is not performed.\n')
        return []

    texts = re.split(pattern, text)
    texts = [d + t for d, t in zip(openings, texts[1:])]
    return texts


def _split_text_by_delimeter(pattern, text):
    """
    Splits text into parts separated by delimeter that matches `pattern`.
    Delimeter is not included in the returned texts.
    For example, --pattern='\n\n---------\n\n' may be used if 
    chapter are separated by 8 dashes.
    """
    texts = re.split(pattern, text)

    if len(texts) == 0:
        print(f'\n❗ No text matching pattern "{pattern}". Splitting is not performed.\n')

    return texts


def _split_text_into_n_parts(n, text, output_dir):
    """
    Splits text into `n` approximately equal parts.
    The splitting is permformed only at paragraphs' boundaries.
    """
    l = len(text) // n

    texts = []

    cur_part_start = 0
    for i in range(len(text)):
        if i >= cur_part_start + l and text[i] == text[i+1] == '\n':
            texts.append(text[cur_part_start:i+2])
            cur_part_start = i + 2

    texts.append(text[cur_part_start:])

    return texts


def _save_texts(texts, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    for i, text in enumerate(texts, start=1):
        n = get_number_of_digits_to_name(len(texts))
        file_path = os.path.join(output_dir, f'{i:0>{n}}.txt')
        with open(file_path, 'w') as f:
            f.write(text)
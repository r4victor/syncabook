import os
import re

from .utils import get_number_of_digits_to_name


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
        return 0

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
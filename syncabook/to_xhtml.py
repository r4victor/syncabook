import os.path

import jinja2

from . import TEMPLATES_DIR
from .utils import drop_extension, get_number_of_digits_to_name


def textfiles_to_xhtml_files(input_dir, output_dir, fragment_type, include_heading=False):
    """
    Converts plain text files in `input_dir` to a list of XHTML files
    and saves them to `output_dir`.
    Each XHTML file consists of fragments – <span> elements with id='f[0-9]+' grouped by <p></p>.
    """
    os.makedirs(output_dir, exist_ok=True)

    input_filenames = sorted(x for x in os.listdir(input_dir) if x.endswith('.txt'))

    texts_contents = []
    for filename in input_filenames:
        with open(os.path.join(input_dir, filename), 'r') as f:
            texts_contents.append(f.read())

    xhtmls = _text_contents_to_xhtmls(texts_contents, fragment_type, include_heading)

    for filename, xhtml in zip(input_filenames, xhtmls):
        file_path = os.path.join(output_dir, f'{drop_extension(filename)}.xhtml')
        with open(file_path, 'w') as f:
            f.write(xhtml)

    print(f'{len(texts_contents)} plain text files have been converted to XHTML.')


def _text_contents_to_xhtmls(texts_contents, fragment_type, include_heading):
    texts = [_get_paragraphs(texts_content, fragment_type) for texts_content in texts_contents]

    # calculate total number of fragments to give fragments proper ids
    fragments_num = sum(sum(len(p) for p in t) for t in texts)
    n = get_number_of_digits_to_name(fragments_num)

    # render xhtmls
    xhtmls = []
    fragment_id = 1
    for t in texts:
        paragraphs = []
        for p in t:
            fragments = []
            for f in p:
                fragments.append({'id': f'f{fragment_id:0>{n}}', 'text': f})
                fragment_id += 1
            paragraphs.append(fragments)

        heading = None
        if include_heading:
            heading = {
                'id': paragraphs[0][0]['id'],
                'text': ''. join(f['text'] for f in paragraphs[0])
            }
            paragraphs = paragraphs[1:]
        
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(TEMPLATES_DIR),
            autoescape=True
        )
        template = env.get_template('text.xhtml')
        xhtml = template.render(heading=heading, paragraphs=paragraphs)
        xhtmls.append(xhtml)

    return xhtmls


def _get_paragraphs(texts_content, fragment_type):
    """
    Returns a list of paragraphs in a text where
    each paragraph is a list of fragments.
    """
    paragraphs = []
    for paragraphs_content in _get_paragraphs_contents(texts_content):
        fragments = _get_fragments(paragraphs_content, fragment_type)
        paragraphs.append(fragments)
    return paragraphs


def _get_paragraphs_contents(texts_content):
    return [p.strip().replace('\n', ' ') for p in texts_content.split('\n\n') if p.strip()]


def _get_fragments(paragraphs_content, fragment_type):
    if fragment_type == 'sentence':
        return _get_sentences(paragraphs_content)
    elif fragment_type == 'paragraph':
        return [paragraphs_content]
    else:
        raise ValueError(f'Unknown fragment_type: {fragment_type}')


def _get_sentences(text):
    """
    Fragment by "{sentence_ending}{space}"
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
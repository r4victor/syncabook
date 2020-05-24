from syncabook import to_xhtml


def test_get_paragraphs():
    texts_content = (
        'This is the first paragraph.\nThe next is the second. It\'s coming soon.\n\n'
        'Here it comes.'
    )
    paragraphs = to_xhtml._get_paragraphs(texts_content, fragment_type='sentence')
    assert paragraphs == [
        ['This is the first paragraph. ', 'The next is the second. ', 'It\'s coming soon.'],
        ['Here it comes.']
    ]


def test_get_sentences():
    paragraphs_content = 'One. Two. Fourty two... Five, six'
    sentences = to_xhtml._get_sentences(paragraphs_content)
    assert sentences == ['One. ', 'Two. ', 'Fourty two... ', 'Five, six']
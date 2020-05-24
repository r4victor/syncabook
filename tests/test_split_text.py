from syncabook import split_text


def test_split_by_opening():
    text = (
        'Title by author\n'
        '\nCHAPTER 1\n'
        '\nThis is CHAPTER 1.\n'
        '\nCHAPTER 343434\n'
        '\nThis is CHAPTER 343434'
    )
    pattern = '\n\nCHAPTER \\d+\n\n'
    texts = split_text._split_text_by_opening(pattern, text)
    assert texts == [
        '\n\nCHAPTER 1\n\nThis is CHAPTER 1.',
        '\n\nCHAPTER 343434\n\nThis is CHAPTER 343434'
    ]


def test_split_text_by_delimeter():
    text = (
        'Title by author\n'
        '\nChapter one weird name\n'
        '\nThis is CHAPTER 1.\n'
        '\n########\n'
        '\nEven more weird name of chapter II\n'
        '\nThis is CHAPTER 2'
    )
    pattern = '\n\n#{8}\n\n'
    texts = split_text._split_text_by_delimeter(pattern, text)
    assert texts == [
        'Title by author\n\nChapter one weird name\n\nThis is CHAPTER 1.',
        'Even more weird name of chapter II\n\nThis is CHAPTER 2'
    ]

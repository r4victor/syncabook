import argparse

from .create import create_ebook
from .download_files import download_files
from .split_text import split_text
from .sync import sync
from .to_xhtml import textfiles_to_xhtml_files


def main():
    parser = argparse.ArgumentParser(
        description=(
            'A set of tools for creating ebooks with synchronized text and audio (EPUB3 with Media Overlays).\n\n'
            'To see what each command does enter $ syncabook `command_name` -h.'
        )
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    parser_download = subparsers.add_parser(
        'download_files',
        description='Download text and audio files from the LibriVox page.'
    )
    parser_download.add_argument('librivox_url')
    parser_download.add_argument('output_dir')
    parser_download.add_argument(
        '--skip-text', 
        action='store_true',
        dest='skip_text',
        default=False,
        help='Do not download any files from synclibrivox repository or gutenberg.org.'
    )
    parser_download.add_argument(
        '--skip-audio', 
        action='store_true',
        dest='skip_audio',
        default=False,
        help='Do not download audio files.'
    )

    parser_split = subparsers.add_parser(
        'split_text',
        description='Split single text file into multiple files.'
    )
    parser_split.add_argument('textfile')
    parser_split.add_argument('output_dir')
    parser_split.add_argument(
        '-m', '--mode', dest='mode', choices=['delimeter', 'opening', 'equal'], default='opening',
        help=(
            'opening mode splits text file by opening PATTERN, i.e. '
            'each file begins with a PATTERN.\n'
            'delimeter mode splits text file using PATTERN.\n'
            'equal mode splits text file into N equal parts.'
        )
    )
    parser_split.add_argument('-n', dest='n', type=int)
    parser_split.add_argument('-p', '--pattern', dest='pattern')

    parser_to_xhtml = subparsers.add_parser(
        'to_xhtml',
        description='Convert plain text files to XHTML files consisting of fragments.'
    )
    parser_to_xhtml.add_argument('input_dir')
    parser_to_xhtml.add_argument('output_dir')
    parser_to_xhtml.add_argument(
        '-f', '--fragment-type', choices=['sentence', 'paragraph'],
        dest='fragment_type', default='sentence',
        help=(
            'Determines how text is splitted into the fragments. Defaults to sentence.'
        )
    )

    parser_sync = subparsers.add_parser(
        'sync',
        description=(
            'Synchronize text and audio producing a list of SMIL files.'
            ' See afaligner library for synchronization details.'
        )
    )
    parser_sync.add_argument('book_dir')

    parser_create = subparsers.add_parser(
        'create',
        description=(
            'Create EPUB3 ebook with synchronized text and audio.'
        )
    )
    parser_create.add_argument(
        'book_dir',
        help=(
            'book_dir must contain sync_text/ directory with a list of synchronized XHTML files,'
            ' no_sync_text/ directory containing nav.xhtml and colophon.xhtml'
            ' and any other non-synchronized XHTML files,'
            ' audio/ directory with a list of audio files,'
            ' smil/ directory with a list of SMIL files'
            ' and a file named metadata.json'
            ' describing a book to be produced.'
            ' If smil/ directory doesn\'t exist or is empty, synchronization will be performed.'
            ' If not provided, metadata.json, nav.xhtml and colophon.xhtml will be created in the process.'
        )
    )

    # arguments common to both parsers
    for p in (parser_sync, parser_create):
        p.add_argument(
            '-r', '--alignment-radius',
            dest='alignment_radius', type=int,
            help=(
                'Parameter of the alignment algorithm that determines the trade-off'
                ' between optimality and computational resources.'
                ' If not specified, afaligner\'s default value is used.'
            )
        )
        p.add_argument(
            '-p', '--alignment-skip-penalty',
            dest='alignment_skip_penalty', type=float,
            help=(
                'Parameter of the alignment algorithm that determines the cost'
                ' of unsynchronized text or audio.'
                ' If not specified, afaligner\'s default value is used.'
            )
        )

    args = parser.parse_args()

    if args.command == 'download_files':
        download_files(args.librivox_url, args.output_dir, args.skip_text, args.skip_audio)
    elif args.command == 'split_text':
        split_text(args.textfile, args.output_dir, args.mode, args.pattern, args.n)
    elif args.command == 'to_xhtml':
        textfiles_to_xhtml_files(args.input_dir, args.output_dir, args.fragment_type)
    elif args.command == 'sync':
        sync(
            args.book_dir,
            alignment_radius=args.alignment_radius,
            alignment_skip_penalty=args.alignment_skip_penalty
        )
    elif args.command == 'create':
        create_ebook(
            args.book_dir,
            alignment_radius=args.alignment_radius,
            alignment_skip_penalty=args.alignment_skip_penalty
        )


if __name__ == '__main__':
    main()
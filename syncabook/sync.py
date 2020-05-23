import os.path

from afaligner import align


def sync(book_dir, alignment_radius, alignment_skip_penalty):
    sync_text_dir = os.path.join(book_dir, 'sync_text')
    audio_dir = os.path.join(book_dir, 'audio')
    output_dir = os.path.join(book_dir, 'smil')
    print('Calling afaligner for syncing...')
    sync_map = align(
        sync_text_dir, audio_dir, output_dir,
        output_format='smil',
        sync_map_text_path_prefix='../text/',
        sync_map_audio_path_prefix='../audio/',
        radius=alignment_radius,
        skip_penalty=alignment_skip_penalty
    )
    if sync_map is not None:
        print('\nText and audio have been successfully synced.\n')
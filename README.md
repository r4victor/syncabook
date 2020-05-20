# Overview

<b>syncabook</b> is a set of tools for creating ebooks with synchronized text and audio (a.k.a read along, read aloud, like Amazon's Whispersync). It allows anyone to create such an ebook using open EPUB3 with Media Overlays format.

The synchronization is done automatically using [afaligner](https://github.com/r4victor/afaligner) library. It is a forced aligner that works by synthesizing text and then aligning synthesized and recorded audio using a variation of [DTW](https://en.wikipedia.org/wiki/Dynamic_time_warping) (Dynamic Time Warping) algorithm. For alignment details, please refer to afaligner repository.


## Ebook production

The ebook is assembled from source files in ebook's root directory which includes:

* `audio/` directory containing a list of audiobook's audio files.
* `sync_text/` directory containing a list of XHTML files synchronized with audio files.
* `no_sync_text/` directory containing a list of XHTML files NOT synchronized with audio files (table of contents, colophon and any other files).
* `smil/` directory containing SMIL files (synchronization info).
* `metadata.json` file which contains information about the book such as title, author, narrator, etc.

In order to prepare such a structure <b>syncabook</b> provides a set of tools. 

From the start we have an empty directory named `ebooks/my_ebook/`. Then we need to get an audiobook and save it in `ebooks/my_ebook/audio/`. We also need to get a text. We save it, for example, as `ebooks/my_ebook/text.txt`. Now we need to convert plain text to a list of XHTML files. `split_text` command can help us to split one plain text file into a list of plain text files and `to_xhtml` command converts a list of plain text files to a list of XHTML files. What's left is to synchronize text and audio. We may use `sync` command to do a synchronization and produce a list of SMIL files, or we may just use `create` command that will do a synchronization as well as create `nav.xhtml` file containing a table of contents and `colophon.xhtml` to credit contributors asking us for all the necessary information in the process and saving it as `ebooks/my_ebook/metadata.json`.

If you want to create an ebook for a LibriVox recording, `download_files` command lets you automatically download all audio files from librivox.org and transcribed text from gutenberg.org. Moreover, if someone has produced an ebook for that recording and contributed prepared XHTML and SMIL files to a 
[sync_librivox](https://github.com/r4victor/sync_librivox) repository, all you need to do is to run `create` command.

## Example usage

TODO

## Notes

* While it is not required to have a one-to-one correspondance
    between text and audio files (i.e. the splitting can be done differently), as the practice shows, it's not always possible to achive a satisfying quality of synchronization and if it is possible, one may need to know the appropriate alignment parameters. Therefore, it is recommended to split text in such a way as to match audio.

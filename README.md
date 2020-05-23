# syncabook

## Overview

<b>syncabook</b> is a set of tools for creating ebooks with synchronized text and audio (a.k.a read along, read aloud, like Amazon's Whispersync). It allows anyone to create such an ebook using open EPUB3 with Media Overlays format.

The synchronization is done automatically using [afaligner](https://github.com/r4victor/afaligner) library. It is a forced aligner that works by synthesizing text and then aligning synthesized and recorded audio using a variation of [DTW](https://en.wikipedia.org/wiki/Dynamic_time_warping) (Dynamic Time Warping) algorithm. For alignment details, please refer to afaligner repository.

## Requirements

* Python (>= 3.6)
* [afaligner](https://github.com/r4victor/afaligner)
* Python packages: `beautifulsoup4`, `Jinja2`, `lxml`, `progressbar2`

## Installation

1. Install [afaligner](https://github.com/r4victor/afaligner)
2. Get <b>syncabook</b>:
```
$ git clone https://github.com/r4victor/syncabook/ && cd syncabook
```
3. Create source distribution and install:
```
$ python setup.py sdist && pip install dist/syncabook*.tar.gz
```

Now, <b>syncabook</b> is installed and can be run simply from command line:

```
$ syncabook -h
```

## Ebook production

The ebook is assembled from source files in ebook's root directory which includes:

* `audio/` directory containing a list of audiobook's audio files.
* `sync_text/` directory containing a list of XHTML files synchronized with audio files.
* `no_sync_text/` directory containing a list of XHTML files NOT synchronized with audio files (table of contents, colophon and any other files).
* `smil/` directory containing SMIL files (synchronization info).
* `metadata.json` file which contains information about the book such as title, author, narrator, etc.

In order to prepare such a structure <b>syncabook</b> provides a set of tools. Here is a brief outline of a typical usage, see concrete example below.

From the start we have an empty directory named `ebooks/my_ebook/`. Then we need to get an audiobook and save it in `ebooks/my_ebook/audio/`. We also need to get a text. We save it, for example, as `ebooks/my_ebook/text.txt`. Now we need to convert plain text to a list of XHTML files. `split_text` command can help us to split one plain text file into a list of plain text files and `to_xhtml` command converts a list of plain text files to a list of XHTML files. What's left is to synchronize text and audio. We may use `sync` command to do a synchronization and produce a list of SMIL files, or we may just use `create` command that will do a synchronization as well as create `nav.xhtml` file containing a table of contents and `colophon.xhtml` to credit contributors asking us for all the necessary information in the process and saving it as `ebooks/my_ebook/metadata.json`.

If you want to create an ebook for a LibriVox recording, `download_files` command lets you automatically download all audio files from librivox.org and transcribed text from gutenberg.org. Moreover, if someone has produced an ebook for that recording and contributed prepared XHTML and SMIL files to a 
[sync_librivox](https://github.com/r4victor/sync_librivox) repository, all you need to do is to run `create` command.

## Usage example

We will create an ebook for On the Duty of Civil Disobedience by Henry David Thoreau based on [LibriVox recording](https://librivox.org/civil-disobedience-by-henry-david-thoreau/) by Bob Neufeld.

1. Download text and audio:

```
$ syncabook download_files https://librivox.org/civil-disobedience-by-henry-david-thoreau/ civil_disobedience
```

2. Audio is recored in two parts, thus we create two files in  `civil_disobedience/plainext/` in which we respecpectively copy content of the first and the second part. This is a little bit of manual labor. If a book is long and recording is made in units like chapters, then `split_text` command can help us to automate this proccess.

3. Convert plain text files into XHTML files:

```
$ syncabook to_xhtml civil_disobedience/plaintext/ civil_disobedience/sync_text/
```

4. Sync text and audio to produce SMIL files:

```
$ syncabook sync civil_disobedience/
```

5. Create EPUB3 ebook:

```
$ syncabook create civil_disobedience/
```

We're asked for book's title, author and other information. `nav.xhtml` containing a table of contents and `colophon.xhtml` to credit contributors are generated and placed in `civil_disobedience/no_sync_text/`. We make some changes in `nav.xhtml` and proceed. Congrats! Our ebook is created and saved in `civil_disobedience/out/`.

## How to read and listen

The ebooks produced are in EPUB3 format and can be opened in any EPUB3 reader. Unfortunately, read aloud feature is not well supported. Here is a list of apps, which I know of, that support it:

* [Readium](https://chrome.google.com/webstore/detail/readium/fepbnnnkkadjhjahcafoaglimekefifl) (Chrome App) – great read & listen experience. Unfortunately, Google is going to deprecate Chrome Apps.

* [Adobe Digital Editions](https://www.adobe.com/la/solutions/ebook/digital-editions/download.html) (Windows, MacOS, iOS, Android) – fully supports EPUB3 standard. Not the best reading experience, though: text and audio seem out of sync.

* [Menestrello](https://github.com/readbeyond/menestrello) (iOS, Android) – the best app to read & listen that was developed for this specific purpose. Unfortunately, no longer maintained and not even available on AppStore or Google Play. Still, .apk can be installed on Android.

Please let me know if you know of other apps that support EPUB3 with Media Overlay.

## Notes

* While it is not required to have a one-to-one correspondance
    between text and audio files (i.e. the splitting can be done differently), as the practice shows, it's not always possible to achive a satisfying quality of synchronization and if it is possible, one may need to know the appropriate alignment parameters. Therefore, it is recommended to split text in such a way as to match audio.

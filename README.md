# syncabook

## Overview

<b>syncabook</b> is a set of tools for creating ebooks with synchronized text and audio (a.k.a read along, read aloud, like Amazon's Whispersync). It allows anyone to create such an ebook using the open EPUB3 with Media Overlays format. [Here is a video](https://www.youtube.com/watch?v=vEHIzX2yAy4) that demonstrates what reading the ebook produced with <b>syncabook</b> looks like.

The synchronization is done automatically using the [afaligner](https://github.com/r4victor/afaligner) library. It is a forced aligner that works by synthesizing text and then aligning synthesized and recorded audio using a variation of the [DTW](https://en.wikipedia.org/wiki/Dynamic_time_warping) (Dynamic Time Warping) algorithm. For alignment details, please refer to the afaligner repository.

## Requirements

* Python (>= 3.6)
* [afaligner](https://github.com/r4victor/afaligner) (optional – required only for synchronization step)
* Python packages: `beautifulsoup4`, `Jinja2`, `lxml`, `progressbar2`

## Installation

1. Get <b>syncabook</b>:
```
$ git clone https://github.com/r4victor/syncabook/ && cd syncabook
```
2. Create the source distribution and install it:
```
$ python setup.py sdist && pip install dist/syncabook*.tar.gz
```

Now, <b>syncabook</b> is installed and can be run simply from the command line:

```
$ syncabook -h
```

3. If you're going to produce your own books, your must install [afaligner](https://github.com/r4victor/afaligner) to do the synchronization. If you only need to assemble ebooks from prepared files like those in the [synclibrivox](https://github.com/r4victor/synclibrivox) repository, this step can be omitted.

### Installation via Docker

Installing <b>afaligner</b> with all its dependencies may seem tedious. If it does for you, then consider using <b>syncabook</b> as a Docker container.

1. Get <b>syncabook</b>:
```
$ git clone https://github.com/r4victor/syncabook/ && cd syncabook
```

2. Create a Docker image:
```
$ docker build -t syncabook .
```

Now, <b>syncabook</b> can be run as a Docker container. The only difference with the native installation is that you have to mount a volume with the `-v` option:

```
$ docker run -v "$PWD":/books/mybook syncabook sync /books/mybook
```


## Ebook production

The ebook is assembled from the source files in the ebook's root directory that includes:

* The `audio/` directory containing a list of audiobook's audio files.
* The `sync_text/` directory containing a list of XHTML files synchronized with audio files.
* The `no_sync_text/` directory containing a list of XHTML files NOT synchronized with audio files (table of contents, colophon and any other files).
* The `smil/` directory containing SMIL files (synchronization info).
* The `metadata.json` file which contains information about the book such as title, author, narrator, etc.

In order to prepare such a structure <b>syncabook</b> provides a set of tools. Here's a brief outline of a typical usage; see a concrete example below.

From the start, we have an empty directory named `ebooks/my_ebook/`. We get an audiobook and save it in `ebooks/my_ebook/audio/`. Then we get a text and save it, for example, as `ebooks/my_ebook/text.txt`. Now we need to convert plain text to a list of XHTML files. The `split_text` command can help us to split one plain text file into a list of plain text files, and the `to_xhtml` command can help us to convert a list of plain text files to a list of XHTML files. What's left is to synchronize the text and the audio. We may use the `sync` command that performs the synchronization and produces a list of SMIL files, or we may just use the `create` command that performs the synchronization as well as creates the ebook. The `create` command automatically creates the `nav.xhtml` file containing a table of contents and the `colophon.xhtml` file to credit contributors. It ask us for all the necessary information in the process and saves it as `ebooks/my_ebook/metadata.json`.

If you want to create an ebook for a LibriVox recording, the `download_files` command lets you automatically download the audio files from librivox.org and the transcribed text from gutenberg.org. Moreover, if someone has produced an ebook for that recording and contributed the prepared XHTML and SMIL files to the 
[synclibrivox](https://github.com/r4victor/synclibrivox) repository, the `download_files` command gets them as well and all you are left to do is to run the `create` command.

## Usage example

We will create an ebook for On the Duty of Civil Disobedience by Henry David Thoreau based on the [LibriVox recording](https://librivox.org/civil-disobedience-by-henry-david-thoreau/) by Bob Neufeld.

1. Download the text and the audio:

```
$ syncabook download_files https://librivox.org/civil-disobedience-by-henry-david-thoreau/ civil_disobedience
```

2. The audio is recorded in two parts, thus we create two files in  `civil_disobedience/plainext/` in which we respectively copy the contents of the first and second parts. This is a little bit of manual labor. If a book is long and recording is made in units like chapters, then the `split_text` command can help us to automate this process.

3. Convert the plain text files into the XHTML files:

```
$ syncabook to_xhtml civil_disobedience/plaintext/ civil_disobedience/sync_text/
```

4. Sync the text and the audio to produce the SMIL files:

```
$ syncabook sync civil_disobedience/
```

5. Create the EPUB3 ebook:

```
$ syncabook create civil_disobedience/
```

We're asked for a book's title, a book's author and other information. The `nav.xhtml` file containing a table of contents and the `colophon.xhtml` file to credit contributors are generated and placed in `civil_disobedience/no_sync_text/`. We make some changes in `nav.xhtml` and proceed. Congrats! Our ebook is created and saved in `civil_disobedience/out/`.

See the [synclibrivox](https://github.com/r4victor/synclibrivox) repository for this and other ebooks.

## How to read and listen

The ebooks produced are in the EPUB3 format and can be opened in any EPUB3 reader. Unfortunately, the Read Aloud feature is not well supported. Here's a list of apps, which I know of, that support it:

* [Readium](https://chrome.google.com/webstore/detail/readium/fepbnnnkkadjhjahcafoaglimekefifl) (Chrome App) – great read & listen experience. Unfortunately, Google is going to deprecate Chrome Apps.

* [Adobe Digital Editions](https://www.adobe.com/la/solutions/ebook/digital-editions/download.html) (Windows, MacOS, iOS, Android) – fully supports EPUB3 standard. Not the best reading experience, though: text and audio seem out of sync.

* [Menestrello](https://github.com/readbeyond/menestrello) (iOS, Android) – the best app to read & listen that was developed for this specific purpose. Unfortunately, no longer maintained and not even available on AppStore or Google Play. Still, .apk can be installed on Android.

Please let me know if you know of other apps that support EPUB3 with Media Overlays.

## Notes

* While it is not required to have a one-to-one correspondence
    between text and audio files (i.e. the splitting can be done differently), as the practice shows, it's not always possible to achieve a satisfying quality of synchronization and if it is possible, one may need to know the appropriate alignment parameters. Therefore, it is recommended to split text in such a way as to match audio.

# syncabook

## Overview

<b>syncabook</b> is a set of tools for creating ebooks with synchronized text and audio (a.k.a. read along, read aloud; like Amazon's Whispersync). You start with a list of text files (plaintext or XTML) and a list of audio files (.wav or .mp3) and get an ebook in the open [EPUB3 with Media Overlays](https://www.w3.org/publishing/epub3/epub-mediaoverlays.html) format. [Here is a video](https://www.youtube.com/watch?v=vEHIzX2yAy4) that demonstrates what reading an ebook produced with <b>syncabook</b> looks like.

The synchronization is done automatically using the [afaligner](https://github.com/r4victor/afaligner) library. It is a forced aligner that works by synthesizing text and then aligning synthesized and recorded audio using a variation of the [DTW](https://en.wikipedia.org/wiki/Dynamic_time_warping) (Dynamic Time Warping) algorithm. For alignment details, please refer to the [afaligner repository](https://github.com/r4victor/afaligner).

## Requirements

* Python (>= 3.6)
* [afaligner](https://github.com/r4victor/afaligner) (optional – required only for synchronization step)
* Python packages: `beautifulsoup4`, `Jinja2`, `lxml`, `progressbar2`

## Installation

1. Get the source code:
   ```
   git clone https://github.com/r4victor/syncabook/ && cd syncabook
   ```

2. Install <b>syncabook</b>:
   ```
   pip install .
   ```

Now you can run <b>syncabook</b> from the command line:

```
syncabook -h
```

3. [optional] If you need to do the synchronization, you must also install the [afaligner](https://github.com/r4victor/afaligner) library. It's not necessary if you already have SMIL files that contain synchronization information for the book. For example, you can download such files for LibriVox recordings from the [synclibrivox](https://github.com/r4victor/synclibrivox) repository.

### Installation via Docker

Installing <b>afaligner</b> with all its dependencies may seem tedious. In that case,  consider using <b>syncabook</b> as a Docker container.

1. Get the source code::
   ```
   git clone https://github.com/r4victor/syncabook/ && cd syncabook
   ```

2. Create a Docker image:
   ```
   docker build -t syncabook .
   ```

Now you can run <b>syncabook</b> as a Docker container. The only difference with the native installation is that you have to mount the book's directory as a volume with the `-v` option. So if you're currently in the book's directory, then the command will look like this:

```
docker run -v "$(PWD)":/books/mybook syncabook sync /books/mybook
```

## Running tests

1. Install `pytest` and [`epubcheck`](https://pypi.org/project/epubcheck/):
   ```
   pip install pytest epubcheck
   ```

2. Run tests:
   ```
   python -m pytest -s tests/
   ```


## Ebook production

The ebook is assembled from source files in the book's root directory that includes:

* The `audio/` directory containing a list of audiobook's audio files.
* The `sync_text/` directory containing a list of XHTML files synchronized with audio files.
* The `no_sync_text/` directory containing a list of XHTML files NOT synchronized with audio files (table of contents, colophon and any other files).
* The `smil/` directory containing SMIL files (synchronization info).
* The `metadata.json` file which contains information about the book such as title, author, narrator, etc.

In order to prepare such a structure <b>syncabook</b> provides a set of tools. Here's a brief outline of a typical usage; see a concrete example below.

Initially we have an empty directory named `ebooks/my_ebook/`. Then we somehow get the audio files and save them to `ebooks/my_ebook/audio/`. Next we get the text and save it, for example, as `ebooks/my_ebook/text.txt`. Now we need to convert this plain text to a list of XHTML files. We use the `split_text` and `to_xhtml` commands.  The `split_text` command splits one plain text file into a list of plain text files, and the `to_xhtml` command converts a list of plain text files to a list of XHTML files. What's left is to synchronize the text and the audio. We may use the `sync` command that performs the synchronization and produces a list of SMIL files, or we may just use the `create` command that performs the synchronization and then creates an ebook. The `create` command automatically creates a `nav.xhtml` file containing a table of contents and a `colophon.xhtml` file to credit contributors. It ask us for all the necessary information in the process and saves it as `ebooks/my_ebook/metadata.json`.

If you want to create an ebook for a LibriVox recording, the `download_files` command lets you automatically download the audio files from librivox.org and the transcribed text from gutenberg.org. Moreover, if someone has produced an ebook for that recording and contributed the prepared XHTML and SMIL files to the 
[synclibrivox](https://github.com/r4victor/synclibrivox) repository, the `download_files` command gets them as well and all you are left to do is to run the `create` command.

## Usage example

We will create an ebook for On the Duty of Civil Disobedience by Henry David Thoreau based on the [LibriVox recording](https://librivox.org/civil-disobedience-by-henry-david-thoreau/) by Bob Neufeld.

1. Download the text and the audio:

   ```
   syncabook download_files https://librivox.org/civil-disobedience-by-henry-david-thoreau/ civil_disobedience
   ```

2. The audio is recorded in two parts, thus we create two files in  `civil_disobedience/plaintext/` in which we respectively copy the contents of the first and second parts. This is a little bit of manual labor. If a book is long and recording is made in units like chapters, the `split_text` command can help you automate this process.

3. Convert the plain text files into the XHTML files:
   ```
   syncabook to_xhtml civil_disobedience/plaintext/ civil_disobedience/sync_text/
   ```

4. Sync the text and the audio to produce the SMIL files:
   ```
   syncabook sync civil_disobedience/
   ```

5. Create the EPUB3 ebook:
   ```
   syncabook create civil_disobedience/
   ```
   It asks us for the book's title, book's author and other information. Then it generates the `nav.xhtml` file containing a table of contents and the `colophon.xhtml` file to credit contributors and places them in `civil_disobedience/no_sync_text/`. We make some changes in `nav.xhtml` and proceed. Congrats! Our ebook is created and saved in `civil_disobedience/out/`.

See the [synclibrivox](https://github.com/r4victor/synclibrivox) repository for this and other ebooks.

## More features

1. To add a cover to the produced ebook, put a JPEG image named `cover.jpg` in the `images/` directory before running `syncabook create`.

## How to read and listen

The ebooks produced are in the EPUB3 format and can be opened in any EPUB3 reader. Unfortunately, the Read Aloud feature is not well supported. Here's a list of apps, which I know of, that support it:

* [Readium](https://chrome.google.com/webstore/detail/readium/fepbnnnkkadjhjahcafoaglimekefifl) (Chrome App) – great read & listen experience. Unfortunately, Google is going to deprecate Chrome Apps.

* [Thorium Reader](https://www.edrlab.org/software/thorium-reader/) (Windows, MacOS and Linux) – Readium's successor, a desktop app in active development.

* [Adobe Digital Editions](https://www.adobe.com/la/solutions/ebook/digital-editions/download.html) (Windows, MacOS, iOS, Android) – fully supports EPUB3 standard. Not the best reading experience, though: text and audio seem out of sync.

* [Menestrello](https://github.com/readbeyond/menestrello) (iOS, Android) – the best app to read & listen that was developed for this specific purpose. Unfortunately, no longer maintained and not even available on AppStore or Google Play. Still, .apk can be installed on Android.

Please let me know if you know of other apps that support EPUB3 with Media Overlays.

## Notes

* While it is not required to have a one-to-one correspondence
    between text and audio files (i.e. the splitting can be done differently), as the practice shows, it's not always possible to achieve a satisfying quality of synchronization and if it is possible, one may need to know the appropriate alignment parameters. Therefore, it is recommended to split text in such a way as to match audio.
* **syncabook** identifies text fragments in XHTML files by looking for tags with attributes of the form `id="f[0-9]+"` ([see an example](https://github.com/r4victor/afaligner/blob/master/tests/resources/shakespeare/text_complete/p001.xhtml)). If you use the `to_xhtml` command to produce XHTML files from plaintext, they will contain the proper tags automatically. If you use your own XHTML files, you'll need to modify them to contain the tags with `id` attributes.

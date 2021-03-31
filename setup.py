from setuptools import setup


setup(
    name='syncabook',
    version='0.0.1',
    description='A tool for creating ebooks with synchronized text and audio (EPUB3 with Media Overlays)',
    url='https://github.com/r4victor/syncabook',
    author='Victor Skvortsov',
    author_email='vds003@gmail.com',
    license='MIT',
    packages=['syncabook'],
    package_data={'syncabook': ['templates/*']},
    entry_points={'console_scripts': ['syncabook=syncabook.__main__:main']},
    install_requires=[
        'beautifulsoup4==4.8.2',
        'Jinja2==2.11.1',
        'lxml==4.6.3',
        'progressbar2==3.51.3',
    ]
)
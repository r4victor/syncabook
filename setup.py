from setuptools import setup


setup(
    name='syncabook',
    version='0.2.0',
    description='A tool for creating ebooks with synchronized text and audio (EPUB3 with Media Overlays)',
    url='https://github.com/r4victor/syncabook',
    author='Victor Skvortsov',
    author_email='vds003@gmail.com',
    license='MIT',
    packages=['syncabook'],
    package_data={'syncabook': ['templates/*']},
    package_dir={'': 'src'},
    entry_points={'console_scripts': ['syncabook=syncabook.__main__:main']},
    install_requires=[
        'beautifulsoup4>=4.11.1',
        'Jinja2>=3.1.2',
        'lxml>=4.9.1',
        'progressbar2>=4.1.1',
    ]
)

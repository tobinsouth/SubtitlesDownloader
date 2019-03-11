# This is the SETUP file
from distutils.core import setup

setup(
    name='SubtitleDownloader',
    version='0.2dev',
    packages=['SubDownloader',],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    description='Uses IMDB and OpenSubtitles to download and process subtitles.',
    long_description=open('README.md').read(),
    install_requires=[
        "imdbpy >= 6.6",
        "python-opensubtitles",
        "re",
        "nltk",
    ],
)

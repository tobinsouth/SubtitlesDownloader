# This is the SETUP file
from distutils.core import setup

setup(
    name='SubtitleDownloader',
    version='0.1dev',
    packages=['src',],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    description='Uses IMDB and OpenSubtitles to download and process subtitles.',
    long_description=open('README.txt').read(),
    install_requires=[
        "Django >= 1.1.1",
        "caldav == 0.1.4",
    ],
)
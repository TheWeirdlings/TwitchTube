import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "twitchtube",
    version = "1.0.0",
    author = "Keith Holliday",
    author_email = "keithrholliday@gmail.com",
    description = ("A bot that syncronizes chat between streams and does other normal bot stuff. Plus some more cool stuff."),
    license = "BSD",
    keywords = "twitchbot youtubebot server",
    url = "http://twitchtube.com",
    packages=['twitchtube', 'youtubelivestreaming'],
    long_description=read('README.md'),
    install_requires=['pymongo', 'google-api-python-client'],
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Twitch Bot :: Server',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2.7',
    ],
)

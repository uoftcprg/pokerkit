#!/usr/bin/env python3

from setuptools import setup

with open('README.rst', 'r') as file:
    long_description = file.read()

setup(
    name='pokerkit',
    version='0.0.0.dev0',
    description='A Python package for various poker tools',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/uoftcprg/pokerkit',
    author='University of Toronto Computer Poker Research Group',
    author_email='uoftcprg@outlook.com',
    license='MIT',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Topic :: Education',
        'Topic :: Games/Entertainment',
        'Topic :: Games/Entertainment :: Board Games',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    keywords=[
        'poker',
        'nlhe',
        'ai',
        'game',
        'game theory',
        'libratus',
        'modicum',
    ],
    project_urls={
        'Documentation': 'https://pokerkit.uoftcprg.com',
        'Source': 'https://github.com/uoftcprg/pokerkit',
        'Tracker': 'https://github.com/uoftcprg/pokerkit/issues',
    },
    packages=['pokerkit'],
    python_requires='>=3.10',
)

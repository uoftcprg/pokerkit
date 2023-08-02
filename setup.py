#!/usr/bin/env python3

from setuptools import find_packages, setup

with open('README.rst', 'r') as file:
    long_description = file.read()

setup(
    name='pokerkit',
    version='0.0.0',
    description='A Python package for various poker tools',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/uoftcprg/pokerkit',
    author='University of Toronto Computer Poker Research Group',
    author_email='uoftcprg@outlook.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Topic :: Education',
        'Topic :: Games/Entertainment',
        'Topic :: Games/Entertainment :: Board Games',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
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
        'Documentation': 'https://pokerkit.readthedocs.io/en/latest/',
        'Source': 'https://github.com/uoftcprg/pokerkit',
        'Tracker': 'https://github.com/uoftcprg/pokerkit/issues',
    },
    package_data={'pokerkit': ['py.typed']},
    packages=find_packages(),
    python_requires='>=3.11',
)

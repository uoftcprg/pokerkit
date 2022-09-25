from setuptools import find_packages, setup

from krieg import __version__

with open('README.rst', 'r') as long_description_file:
    long_description = long_description_file.read()

setup(
    name='krieg',
    version=__version__,
    author='Juho Kim',
    author_email='juho-kim@outlook.com',
    description='A Python package for a general game framework.',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/AussieSeaweed/krieg',
    packages=find_packages(),
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.7',
    install_requires='auxiliary~=1.0',
)

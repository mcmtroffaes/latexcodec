# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import codecs


def readfile(filename):
    with codecs.open(filename, encoding="utf-8") as stream:
        return stream.read().split("\n")

doclines = readfile("README.rst")
version = readfile("VERSION")[0].strip()

setup(
    name='latexcodec',
    version=version,
    url='https://github.com/mcmtroffaes/latexcodec',
    download_url='http://pypi.python.org/pypi/sphinxcontrib-bibtex',
    license='MIT',
    author="Matthias C. M. Troffaes",
    author_email='matthias.troffaes@gmail.com',
    description=doclines[0],
    long_description="\n".join(doclines[2:]),
    zip_safe=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Text Processing :: Markup :: LaTeX',
        'Topic :: Text Processing :: Filters',
    ],
    platforms='any',
    packages=find_packages(),
    use_2to3=True,
)

# -*- coding: utf-8 -*-

import io
from setuptools import setup, find_packages


def readfile(filename):
    with io.open(filename, encoding="utf-8") as stream:
        return stream.read().split("\n")


readme = readfile("README.rst")[5:]  # skip title and badges
requires = readfile("requirements.txt")
version = readfile("VERSION")[0].strip()

setup(
    name='latexcodec',
    version=version,
    url='https://github.com/mcmtroffaes/latexcodec',
    download_url='http://pypi.python.org/pypi/latexcodec',
    license='MIT',
    author='Matthias C. M. Troffaes',
    author_email='matthias.troffaes@gmail.com',
    description=readme[0],
    long_description="\n".join(readme[2:]),
    zip_safe=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Text Processing :: Markup :: LaTeX',
        'Topic :: Text Processing :: Filters',
    ],
    platforms='any',
    packages=find_packages(),
    install_requires=requires,
)

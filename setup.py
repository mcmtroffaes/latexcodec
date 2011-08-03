"""Setup script for latexcodec."""

classifiers = """\
Development Status :: 3 - Alpha
License :: OSI Approved :: MIT License
Intended Audience :: Developers
Topic :: Text Processing :: Markup :: LaTeX
Topic :: Text Processing :: Filters
Programming Language :: Python
Programming Language :: Python :: 2
Operating System :: OS Independent"""

from setuptools import setup
from latexcodec import __version__

doclines = open('README.rst').read().split('\n')

setup(
    name = "latexcodec",
    version = __version__,
    packages = ['latexcodec'],
    author = "Matthias Troffaes",
    author_email = "matthias.troffaes@gmail.com",
    license = "MIT",
    keywords = "latex, codec, lexer",
    platforms = "any",
    description = doclines[0],
    long_description = "\n".join(doclines[2:]),
    url = "https://github.com/mcmtroffaes/latexcodec",
    classifiers = classifiers.split('\n'),
)

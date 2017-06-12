# -*- coding: utf-8 -*-
"""
    LaTeX Codec
    ~~~~~~~~~~~

    The :mod:`latexcodec.codec` module
    contains all classes and functions for LaTeX code
    translation. For practical use,
    you should only ever need to import the :mod:`latexcodec` module,
    which will automatically register the codec
    so it can be used by :meth:`str.encode`, :meth:`str.decode`,
    and any of the functions defined in the :mod:`codecs` module
    such as :func:`codecs.open` and so on.
    The other functions and classes
    are exposed in case someone would want to extend them.

    .. autofunction:: register

    .. autofunction:: find_latex

    .. autoclass:: LatexIncrementalEncoder
        :show-inheritance:
        :members:

    .. autoclass:: LatexIncrementalDecoder
        :show-inheritance:
        :members:

    .. autoclass:: LatexCodec
        :show-inheritance:
        :members:

    .. autoclass:: LatexUnicodeTable
        :members:
"""

# Copyright (c) 2003, 2008 David Eppstein
# Copyright (c) 2011-2014 Matthias C. M. Troffaes
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

from __future__ import print_function

import codecs
from six import string_types
from six.moves import range

from latexcodec import lexer


def register():
    """Register the :func:`find_latex` codec search function.

    .. seealso:: :func:`codecs.register`
    """
    codecs.register(find_latex)

# returns the codec search function
# this is used if latex_codec.py were to be placed in stdlib


def getregentry():
    """Encodings module API."""
    return find_latex('latex')


class LatexUnicodeTable:

    """Tabulates a translation between LaTeX and unicode."""

    def __init__(self, lexer):
        self.lexer = lexer
        self.unicode_map = {}
        self.max_length = 0
        self.latex_map = {}
        self.register_all()

    def register_all(self):
        """Register all symbols and their LaTeX equivalents
        (called by constructor).
        """
        # TODO complete this list
        # register special symbols
        self.register(u'\n\n', b' \\par', encode=False)
        self.register(u'\n\n', b'\\par', encode=False)
        self.register(u' ', b'\\ ', encode=False)
        self.register(u'%', b'\\%')
        self.register(u'\N{EN DASH}', b'--')
        self.register(u'\N{EN DASH}', b'\\textendash')
        self.register(u'\N{EM DASH}', b'---')
        self.register(u'\N{EM DASH}', b'\\textemdash')
        self.register(u'\N{LEFT SINGLE QUOTATION MARK}', b'`', decode=False)
        self.register(u'\N{RIGHT SINGLE QUOTATION MARK}', b"'", decode=False)
        self.register(u'\N{LEFT DOUBLE QUOTATION MARK}', b'``')
        self.register(u'\N{RIGHT DOUBLE QUOTATION MARK}', b"''")
        self.register(u'\N{DOUBLE LOW-9 QUOTATION MARK}', b'\\glqq')
        self.register(u'\N{DAGGER}', b'\\dag')
        self.register(u'\N{DOUBLE DAGGER}', b'\\ddag')

        self.register(u'\\', b'\\textbackslash', encode=False)
        self.register(u'\\', b'\\backslash', mode='math', encode=False)

        self.register(u'\N{TILDE OPERATOR}', b'\\sim', mode='math')
        self.register(u'\N{MODIFIER LETTER LOW TILDE}',
                      b'\\texttildelow', package='textcomp')
        self.register(u'\N{SMALL TILDE}', b'\\~{}')
        self.register(u'~', b'\\textasciitilde')

        self.register(u'\N{BULLET}', b'\\bullet', mode='math')
        self.register(u'\N{BULLET}', b'\\textbullet', package='textcomp')

        self.register(u'\N{NUMBER SIGN}', b'\\#')
        self.register(u'\N{LOW LINE}', b'\\_')
        self.register(u'\N{AMPERSAND}', b'\\&')
        self.register(u'\N{NO-BREAK SPACE}', b'~')
        self.register(u'\N{INVERTED EXCLAMATION MARK}', b'!`')
        self.register(u'\N{CENT SIGN}', b'\\not{c}')

        self.register(u'\N{POUND SIGN}', b'\\pounds')
        self.register(u'\N{POUND SIGN}', b'\\textsterling', package='textcomp')

        self.register(u'\N{SECTION SIGN}', b'\\S')
        self.register(u'\N{DIAERESIS}', b'\\"{}')
        self.register(u'\N{NOT SIGN}', b'\\neg')
        self.register(u'\N{SOFT HYPHEN}', b'\\-')
        self.register(u'\N{MACRON}', b'\\={}')

        self.register(u'\N{DEGREE SIGN}', b'^\\circ', mode='math')
        self.register(u'\N{DEGREE SIGN}', b'\\textdegree', package='textcomp')

        self.register(u'\N{PLUS-MINUS SIGN}', b'\\pm', mode='math')
        self.register(u'\N{PLUS-MINUS SIGN}', b'\\textpm', package='textcomp')

        self.register(u'\N{SUPERSCRIPT TWO}', b'^2', mode='math')
        self.register(
            u'\N{SUPERSCRIPT TWO}',
            b'\\texttwosuperior',
            package='textcomp')

        self.register(u'\N{SUPERSCRIPT THREE}', b'^3', mode='math')
        self.register(
            u'\N{SUPERSCRIPT THREE}',
            b'\\textthreesuperior',
            package='textcomp')

        self.register(u'\N{ACUTE ACCENT}', b"\\'{}")

        self.register(u'\N{MICRO SIGN}', b'\\mu', mode='math')
        self.register(u'\N{MICRO SIGN}', b'\\micro', package='gensymb')

        self.register(u'\N{PILCROW SIGN}', b'\\P')

        self.register(u'\N{MIDDLE DOT}', b'\\cdot', mode='math')
        self.register(
            u'\N{MIDDLE DOT}',
            b'\\textperiodcentered',
            package='textcomp')

        self.register(u'\N{CEDILLA}', b'\\c{}')

        self.register(u'\N{SUPERSCRIPT ONE}', b'^1', mode='math')
        self.register(
            u'\N{SUPERSCRIPT ONE}',
            b'\\textonesuperior',
            package='textcomp')

        self.register(u'\N{INVERTED QUESTION MARK}', b'?`')
        self.register(u'\N{LATIN CAPITAL LETTER A WITH GRAVE}', b'\\`A')
        self.register(u'\N{LATIN CAPITAL LETTER A WITH CIRCUMFLEX}', b'\\^A')
        self.register(u'\N{LATIN CAPITAL LETTER A WITH TILDE}', b'\\~A')
        self.register(u'\N{LATIN CAPITAL LETTER A WITH DIAERESIS}', b'\\"A')
        self.register(u'\N{LATIN CAPITAL LETTER A WITH RING ABOVE}', b'\\AA')
        self.register(u'\N{LATIN CAPITAL LETTER AE}', b'\\AE')
        self.register(u'\N{LATIN CAPITAL LETTER C WITH CEDILLA}', b'\\c C')
        self.register(u'\N{LATIN CAPITAL LETTER E WITH GRAVE}', b'\\`E')
        self.register(u'\N{LATIN CAPITAL LETTER E WITH ACUTE}', b"\\'E")
        self.register(u'\N{LATIN CAPITAL LETTER E WITH CIRCUMFLEX}', b'\\^E')
        self.register(u'\N{LATIN CAPITAL LETTER E WITH DIAERESIS}', b'\\"E')
        self.register(u'\N{LATIN CAPITAL LETTER I WITH GRAVE}', b'\\`I')
        self.register(u'\N{LATIN CAPITAL LETTER I WITH CIRCUMFLEX}', b'\\^I')
        self.register(u'\N{LATIN CAPITAL LETTER I WITH DIAERESIS}', b'\\"I')
        self.register(u'\N{LATIN CAPITAL LETTER N WITH TILDE}', b'\\~N')
        self.register(u'\N{LATIN CAPITAL LETTER O WITH GRAVE}', b'\\`O')
        self.register(u'\N{LATIN CAPITAL LETTER O WITH ACUTE}', b"\\'O")
        self.register(u'\N{LATIN CAPITAL LETTER O WITH CIRCUMFLEX}', b'\\^O')
        self.register(u'\N{LATIN CAPITAL LETTER O WITH TILDE}', b'\\~O')
        self.register(u'\N{LATIN CAPITAL LETTER O WITH DIAERESIS}', b'\\"O')
        self.register(u'\N{MULTIPLICATION SIGN}', b'\\times', mode='math')
        self.register(u'\N{LATIN CAPITAL LETTER O WITH STROKE}', b'\\O')
        self.register(u'\N{LATIN CAPITAL LETTER U WITH GRAVE}', b'\\`U')
        self.register(u'\N{LATIN CAPITAL LETTER U WITH ACUTE}', b"\\'U")
        self.register(u'\N{LATIN CAPITAL LETTER U WITH CIRCUMFLEX}', b'\\^U')
        self.register(u'\N{LATIN CAPITAL LETTER U WITH DIAERESIS}', b'\\"U')
        self.register(u'\N{LATIN CAPITAL LETTER Y WITH ACUTE}', b"\\'Y")
        self.register(u'\N{LATIN SMALL LETTER SHARP S}', b'\\ss')
        self.register(u'\N{LATIN SMALL LETTER A WITH GRAVE}', b'\\`a')
        self.register(u'\N{LATIN SMALL LETTER A WITH ACUTE}', b"\\'a")
        self.register(u'\N{LATIN SMALL LETTER A WITH CIRCUMFLEX}', b'\\^a')
        self.register(u'\N{LATIN SMALL LETTER A WITH TILDE}', b'\\~a')
        self.register(u'\N{LATIN SMALL LETTER A WITH DIAERESIS}', b'\\"a')
        self.register(u'\N{LATIN SMALL LETTER A WITH RING ABOVE}', b'\\aa')
        self.register(u'\N{LATIN SMALL LETTER AE}', b'\\ae')
        self.register(u'\N{LATIN SMALL LETTER C WITH CEDILLA}', b'\\c c')
        self.register(u'\N{LATIN SMALL LETTER E WITH GRAVE}', b'\\`e')
        self.register(u'\N{LATIN SMALL LETTER E WITH ACUTE}', b"\\'e")
        self.register(u'\N{LATIN SMALL LETTER E WITH CIRCUMFLEX}', b'\\^e')
        self.register(u'\N{LATIN SMALL LETTER E WITH DIAERESIS}', b'\\"e')
        self.register(u'\N{LATIN SMALL LETTER I WITH GRAVE}', b'\\`\\i')
        self.register(u'\N{LATIN SMALL LETTER I WITH GRAVE}', b'\\`i')
        self.register(u'\N{LATIN SMALL LETTER I WITH ACUTE}', b"\\'\\i")
        self.register(u'\N{LATIN SMALL LETTER I WITH ACUTE}', b"\\'i")
        self.register(u'\N{LATIN SMALL LETTER I WITH CIRCUMFLEX}', b'\\^\\i')
        self.register(u'\N{LATIN SMALL LETTER I WITH CIRCUMFLEX}', b'\\^i')
        self.register(u'\N{LATIN SMALL LETTER I WITH DIAERESIS}', b'\\"\\i')
        self.register(u'\N{LATIN SMALL LETTER I WITH DIAERESIS}', b'\\"i')
        self.register(u'\N{LATIN SMALL LETTER N WITH TILDE}', b'\\~n')
        self.register(u'\N{LATIN SMALL LETTER O WITH GRAVE}', b'\\`o')
        self.register(u'\N{LATIN SMALL LETTER O WITH ACUTE}', b"\\'o")
        self.register(u'\N{LATIN SMALL LETTER O WITH CIRCUMFLEX}', b'\\^o')
        self.register(u'\N{LATIN SMALL LETTER O WITH TILDE}', b'\\~o')
        self.register(u'\N{LATIN SMALL LETTER O WITH DIAERESIS}', b'\\"o')
        self.register(u'\N{DIVISION SIGN}', b'\\div', mode='math')
        self.register(u'\N{LATIN SMALL LETTER O WITH STROKE}', b'\\o')
        self.register(u'\N{LATIN SMALL LETTER U WITH GRAVE}', b'\\`u')
        self.register(u'\N{LATIN SMALL LETTER U WITH ACUTE}', b"\\'u")
        self.register(u'\N{LATIN SMALL LETTER U WITH CIRCUMFLEX}', b'\\^u')
        self.register(u'\N{LATIN SMALL LETTER U WITH DIAERESIS}', b'\\"u')
        self.register(u'\N{LATIN SMALL LETTER Y WITH ACUTE}', b"\\'y")
        self.register(u'\N{LATIN SMALL LETTER Y WITH DIAERESIS}', b'\\"y')
        self.register(u'\N{LATIN CAPITAL LETTER A WITH MACRON}', b'\\=A')
        self.register(u'\N{LATIN SMALL LETTER A WITH MACRON}', b'\\=a')
        self.register(u'\N{LATIN CAPITAL LETTER A WITH BREVE}', b'\\u A')
        self.register(u'\N{LATIN SMALL LETTER A WITH BREVE}', b'\\u a')
        self.register(u'\N{LATIN CAPITAL LETTER A WITH OGONEK}', b'\\k A')
        self.register(u'\N{LATIN SMALL LETTER A WITH OGONEK}', b'\\k a')
        self.register(u'\N{LATIN CAPITAL LETTER C WITH ACUTE}', b"\\'C")
        self.register(u'\N{LATIN SMALL LETTER C WITH ACUTE}', b"\\'c")
        self.register(u'\N{LATIN CAPITAL LETTER C WITH CIRCUMFLEX}', b'\\^C')
        self.register(u'\N{LATIN SMALL LETTER C WITH CIRCUMFLEX}', b'\\^c')
        self.register(u'\N{LATIN CAPITAL LETTER C WITH DOT ABOVE}', b'\\.C')
        self.register(u'\N{LATIN SMALL LETTER C WITH DOT ABOVE}', b'\\.c')
        self.register(u'\N{LATIN CAPITAL LETTER C WITH CARON}', b'\\v C')
        self.register(u'\N{LATIN SMALL LETTER C WITH CARON}', b'\\v c')
        self.register(u'\N{LATIN CAPITAL LETTER D WITH CARON}', b'\\v D')
        self.register(u'\N{LATIN SMALL LETTER D WITH CARON}', b'\\v d')
        self.register(u'\N{LATIN CAPITAL LETTER E WITH MACRON}', b'\\=E')
        self.register(u'\N{LATIN SMALL LETTER E WITH MACRON}', b'\\=e')
        self.register(u'\N{LATIN CAPITAL LETTER E WITH BREVE}', b'\\u E')
        self.register(u'\N{LATIN SMALL LETTER E WITH BREVE}', b'\\u e')
        self.register(u'\N{LATIN CAPITAL LETTER E WITH DOT ABOVE}', b'\\.E')
        self.register(u'\N{LATIN SMALL LETTER E WITH DOT ABOVE}', b'\\.e')
        self.register(u'\N{LATIN CAPITAL LETTER E WITH OGONEK}', b'\\k E')
        self.register(u'\N{LATIN SMALL LETTER E WITH OGONEK}', b'\\k e')
        self.register(u'\N{LATIN CAPITAL LETTER E WITH CARON}', b'\\v E')
        self.register(u'\N{LATIN SMALL LETTER E WITH CARON}', b'\\v e')
        self.register(u'\N{LATIN CAPITAL LETTER G WITH CIRCUMFLEX}', b'\\^G')
        self.register(u'\N{LATIN SMALL LETTER G WITH CIRCUMFLEX}', b'\\^g')
        self.register(u'\N{LATIN CAPITAL LETTER G WITH BREVE}', b'\\u G')
        self.register(u'\N{LATIN SMALL LETTER G WITH BREVE}', b'\\u g')
        self.register(u'\N{LATIN CAPITAL LETTER G WITH DOT ABOVE}', b'\\.G')
        self.register(u'\N{LATIN SMALL LETTER G WITH DOT ABOVE}', b'\\.g')
        self.register(u'\N{LATIN CAPITAL LETTER G WITH CEDILLA}', b'\\c G')
        self.register(u'\N{LATIN SMALL LETTER G WITH CEDILLA}', b'\\c g')
        self.register(u'\N{LATIN CAPITAL LETTER H WITH CIRCUMFLEX}', b'\\^H')
        self.register(u'\N{LATIN SMALL LETTER H WITH CIRCUMFLEX}', b'\\^h')
        self.register(u'\N{LATIN CAPITAL LETTER I WITH TILDE}', b'\\~I')
        self.register(u'\N{LATIN SMALL LETTER I WITH TILDE}', b'\\~\\i')
        self.register(u'\N{LATIN SMALL LETTER I WITH TILDE}', b'\\~i')
        self.register(u'\N{LATIN CAPITAL LETTER I WITH MACRON}', b'\\=I')
        self.register(u'\N{LATIN SMALL LETTER I WITH MACRON}', b'\\=\\i')
        self.register(u'\N{LATIN SMALL LETTER I WITH MACRON}', b'\\=i')
        self.register(u'\N{LATIN CAPITAL LETTER I WITH BREVE}', b'\\u I')
        self.register(u'\N{LATIN SMALL LETTER I WITH BREVE}', b'\\u\\i')
        self.register(u'\N{LATIN SMALL LETTER I WITH BREVE}', b'\\u i')
        self.register(u'\N{LATIN CAPITAL LETTER I WITH OGONEK}', b'\\k I')
        self.register(u'\N{LATIN SMALL LETTER I WITH OGONEK}', b'\\k i')
        self.register(u'\N{LATIN CAPITAL LETTER I WITH DOT ABOVE}', b'\\.I')
        self.register(u'\N{LATIN SMALL LETTER DOTLESS I}', b'\\i')
        self.register(u'\N{LATIN CAPITAL LIGATURE IJ}', b'IJ', decode=False)
        self.register(u'\N{LATIN SMALL LIGATURE IJ}', b'ij', decode=False)
        self.register(u'\N{LATIN CAPITAL LETTER J WITH CIRCUMFLEX}', b'\\^J')
        self.register(u'\N{LATIN SMALL LETTER J WITH CIRCUMFLEX}', b'\\^\\j')
        self.register(u'\N{LATIN SMALL LETTER J WITH CIRCUMFLEX}', b'\\^j')
        self.register(u'\N{LATIN CAPITAL LETTER K WITH CEDILLA}', b'\\c K')
        self.register(u'\N{LATIN SMALL LETTER K WITH CEDILLA}', b'\\c k')
        self.register(u'\N{LATIN CAPITAL LETTER L WITH ACUTE}', b"\\'L")
        self.register(u'\N{LATIN SMALL LETTER L WITH ACUTE}', b"\\'l")
        self.register(u'\N{LATIN CAPITAL LETTER L WITH CEDILLA}', b'\\c L')
        self.register(u'\N{LATIN SMALL LETTER L WITH CEDILLA}', b'\\c l')
        self.register(u'\N{LATIN CAPITAL LETTER L WITH CARON}', b'\\v L')
        self.register(u'\N{LATIN SMALL LETTER L WITH CARON}', b'\\v l')
        self.register(u'\N{LATIN CAPITAL LETTER L WITH STROKE}', b'\\L')
        self.register(u'\N{LATIN SMALL LETTER L WITH STROKE}', b'\\l')
        self.register(u'\N{LATIN CAPITAL LETTER N WITH ACUTE}', b"\\'N")
        self.register(u'\N{LATIN SMALL LETTER N WITH ACUTE}', b"\\'n")
        self.register(u'\N{LATIN CAPITAL LETTER N WITH CEDILLA}', b'\\c N')
        self.register(u'\N{LATIN SMALL LETTER N WITH CEDILLA}', b'\\c n')
        self.register(u'\N{LATIN CAPITAL LETTER N WITH CARON}', b'\\v N')
        self.register(u'\N{LATIN SMALL LETTER N WITH CARON}', b'\\v n')
        self.register(u'\N{LATIN CAPITAL LETTER O WITH MACRON}', b'\\=O')
        self.register(u'\N{LATIN SMALL LETTER O WITH MACRON}', b'\\=o')
        self.register(u'\N{LATIN CAPITAL LETTER O WITH BREVE}', b'\\u O')
        self.register(u'\N{LATIN SMALL LETTER O WITH BREVE}', b'\\u o')
        self.register(
            u'\N{LATIN CAPITAL LETTER O WITH DOUBLE ACUTE}',
            b'\\H O')
        self.register(u'\N{LATIN SMALL LETTER O WITH DOUBLE ACUTE}', b'\\H o')
        self.register(u'\N{LATIN CAPITAL LIGATURE OE}', b'\\OE')
        self.register(u'\N{LATIN SMALL LIGATURE OE}', b'\\oe')
        self.register(u'\N{LATIN CAPITAL LETTER R WITH ACUTE}', b"\\'R")
        self.register(u'\N{LATIN SMALL LETTER R WITH ACUTE}', b"\\'r")
        self.register(u'\N{LATIN CAPITAL LETTER R WITH CEDILLA}', b'\\c R')
        self.register(u'\N{LATIN SMALL LETTER R WITH CEDILLA}', b'\\c r')
        self.register(u'\N{LATIN CAPITAL LETTER R WITH CARON}', b'\\v R')
        self.register(u'\N{LATIN SMALL LETTER R WITH CARON}', b'\\v r')
        self.register(u'\N{LATIN CAPITAL LETTER S WITH ACUTE}', b"\\'S")
        self.register(u'\N{LATIN SMALL LETTER S WITH ACUTE}', b"\\'s")
        self.register(u'\N{LATIN CAPITAL LETTER S WITH CIRCUMFLEX}', b'\\^S')
        self.register(u'\N{LATIN SMALL LETTER S WITH CIRCUMFLEX}', b'\\^s')
        self.register(u'\N{LATIN CAPITAL LETTER S WITH CEDILLA}', b'\\c S')
        self.register(u'\N{LATIN SMALL LETTER S WITH CEDILLA}', b'\\c s')
        self.register(u'\N{LATIN CAPITAL LETTER S WITH CARON}', b'\\v S')
        self.register(u'\N{LATIN SMALL LETTER S WITH CARON}', b'\\v s')
        self.register(u'\N{LATIN CAPITAL LETTER T WITH CEDILLA}', b'\\c T')
        self.register(u'\N{LATIN SMALL LETTER T WITH CEDILLA}', b'\\c t')
        self.register(u'\N{LATIN CAPITAL LETTER T WITH CARON}', b'\\v T')
        self.register(u'\N{LATIN SMALL LETTER T WITH CARON}', b'\\v t')
        self.register(u'\N{LATIN CAPITAL LETTER U WITH TILDE}', b'\\~U')
        self.register(u'\N{LATIN SMALL LETTER U WITH TILDE}', b'\\~u')
        self.register(u'\N{LATIN CAPITAL LETTER U WITH MACRON}', b'\\=U')
        self.register(u'\N{LATIN SMALL LETTER U WITH MACRON}', b'\\=u')
        self.register(u'\N{LATIN CAPITAL LETTER U WITH BREVE}', b'\\u U')
        self.register(u'\N{LATIN SMALL LETTER U WITH BREVE}', b'\\u u')
        self.register(u'\N{LATIN CAPITAL LETTER U WITH RING ABOVE}', b'\\r U')
        self.register(u'\N{LATIN SMALL LETTER U WITH RING ABOVE}', b'\\r u')
        self.register(
            u'\N{LATIN CAPITAL LETTER U WITH DOUBLE ACUTE}',
            b'\\H U')
        self.register(u'\N{LATIN SMALL LETTER U WITH DOUBLE ACUTE}', b'\\H u')
        self.register(u'\N{LATIN CAPITAL LETTER U WITH OGONEK}', b'\\k U')
        self.register(u'\N{LATIN SMALL LETTER U WITH OGONEK}', b'\\k u')
        self.register(u'\N{LATIN CAPITAL LETTER W WITH CIRCUMFLEX}', b'\\^W')
        self.register(u'\N{LATIN SMALL LETTER W WITH CIRCUMFLEX}', b'\\^w')
        self.register(u'\N{LATIN CAPITAL LETTER Y WITH CIRCUMFLEX}', b'\\^Y')
        self.register(u'\N{LATIN SMALL LETTER Y WITH CIRCUMFLEX}', b'\\^y')
        self.register(u'\N{LATIN CAPITAL LETTER Y WITH DIAERESIS}', b'\\"Y')
        self.register(u'\N{LATIN CAPITAL LETTER Z WITH ACUTE}', b"\\'Z")
        self.register(u'\N{LATIN SMALL LETTER Z WITH ACUTE}', b"\\'z")
        self.register(u'\N{LATIN CAPITAL LETTER Z WITH DOT ABOVE}', b'\\.Z')
        self.register(u'\N{LATIN SMALL LETTER Z WITH DOT ABOVE}', b'\\.z')
        self.register(u'\N{LATIN CAPITAL LETTER Z WITH CARON}', b'\\v Z')
        self.register(u'\N{LATIN SMALL LETTER Z WITH CARON}', b'\\v z')
        self.register(u'\N{LATIN CAPITAL LETTER DZ WITH CARON}', b'D\\v Z')
        self.register(
            u'\N{LATIN CAPITAL LETTER D WITH SMALL LETTER Z WITH CARON}',
            b'D\\v z')
        self.register(u'\N{LATIN SMALL LETTER DZ WITH CARON}', b'd\\v z')
        self.register(u'\N{LATIN CAPITAL LETTER LJ}', b'LJ', decode=False)
        self.register(
            u'\N{LATIN CAPITAL LETTER L WITH SMALL LETTER J}',
            b'Lj',
            decode=False)
        self.register(u'\N{LATIN SMALL LETTER LJ}', b'lj', decode=False)
        self.register(u'\N{LATIN CAPITAL LETTER NJ}', b'NJ', decode=False)
        self.register(
            u'\N{LATIN CAPITAL LETTER N WITH SMALL LETTER J}',
            b'Nj',
            decode=False)
        self.register(u'\N{LATIN SMALL LETTER NJ}', b'nj', decode=False)
        self.register(u'\N{LATIN CAPITAL LETTER A WITH CARON}', b'\\v A')
        self.register(u'\N{LATIN SMALL LETTER A WITH CARON}', b'\\v a')
        self.register(u'\N{LATIN CAPITAL LETTER I WITH CARON}', b'\\v I')
        self.register(u'\N{LATIN SMALL LETTER I WITH CARON}', b'\\v\\i')
        self.register(u'\N{LATIN CAPITAL LETTER O WITH CARON}', b'\\v O')
        self.register(u'\N{LATIN SMALL LETTER O WITH CARON}', b'\\v o')
        self.register(u'\N{LATIN CAPITAL LETTER U WITH CARON}', b'\\v U')
        self.register(u'\N{LATIN SMALL LETTER U WITH CARON}', b'\\v u')
        self.register(u'\N{LATIN CAPITAL LETTER G WITH CARON}', b'\\v G')
        self.register(u'\N{LATIN SMALL LETTER G WITH CARON}', b'\\v g')
        self.register(u'\N{LATIN CAPITAL LETTER K WITH CARON}', b'\\v K')
        self.register(u'\N{LATIN SMALL LETTER K WITH CARON}', b'\\v k')
        self.register(u'\N{LATIN CAPITAL LETTER O WITH OGONEK}', b'\\k O')
        self.register(u'\N{LATIN SMALL LETTER O WITH OGONEK}', b'\\k o')
        self.register(u'\N{LATIN SMALL LETTER J WITH CARON}', b'\\v\\j')
        self.register(u'\N{LATIN CAPITAL LETTER DZ}', b'DZ', decode=False)
        self.register(
            u'\N{LATIN CAPITAL LETTER D WITH SMALL LETTER Z}',
            b'Dz',
            decode=False)
        self.register(u'\N{LATIN SMALL LETTER DZ}', b'dz', decode=False)
        self.register(u'\N{LATIN CAPITAL LETTER G WITH ACUTE}', b"\\'G")
        self.register(u'\N{LATIN SMALL LETTER G WITH ACUTE}', b"\\'g")
        self.register(u'\N{LATIN CAPITAL LETTER AE WITH ACUTE}', b"\\'\\AE")
        self.register(u'\N{LATIN SMALL LETTER AE WITH ACUTE}', b"\\'\\ae")
        self.register(
            u'\N{LATIN CAPITAL LETTER O WITH STROKE AND ACUTE}',
            b"\\'\\O")
        self.register(
            u'\N{LATIN SMALL LETTER O WITH STROKE AND ACUTE}',
            b"\\'\\o")
        self.register(u'\N{PARTIAL DIFFERENTIAL}', b'\\partial', mode='math')
        self.register(u'\N{N-ARY PRODUCT}', b'\\prod', mode='math')
        self.register(u'\N{N-ARY SUMMATION}', b'\\sum', mode='math')
        self.register(u'\N{SQUARE ROOT}', b'\\surd', mode='math')
        self.register(u'\N{INFINITY}', b'\\infty', mode='math')
        self.register(u'\N{INTEGRAL}', b'\\int', mode='math')
        self.register(u'\N{INTERSECTION}', b'\\cap', mode='math')
        self.register(u'\N{UNION}', b'\\cup', mode='math')
        self.register(u'\N{RIGHTWARDS ARROW}', b'\\rightarrow', mode='math')
        self.register(
            u'\N{RIGHTWARDS DOUBLE ARROW}',
            b'\\Rightarrow',
            mode='math')
        self.register(u'\N{LEFTWARDS ARROW}', b'\\leftarrow', mode='math')
        self.register(
            u'\N{LEFTWARDS DOUBLE ARROW}',
            b'\\Leftarrow',
            mode='math')
        self.register(u'\N{LOGICAL OR}', b'\\vee', mode='math')
        self.register(u'\N{LOGICAL AND}', b'\\wedge', mode='math')
        self.register(u'\N{ALMOST EQUAL TO}', b'\\approx', mode='math')
        self.register(u'\N{NOT EQUAL TO}', b'\\neq', mode='math')
        self.register(u'\N{LESS-THAN OR EQUAL TO}', b'\\leq', mode='math')
        self.register(u'\N{GREATER-THAN OR EQUAL TO}', b'\\geq', mode='math')
        self.register(u'\N{MODIFIER LETTER CIRCUMFLEX ACCENT}', b'\\^{}')
        self.register(u'\N{CARON}', b'\\v{}')
        self.register(u'\N{BREVE}', b'\\u{}')
        self.register(u'\N{DOT ABOVE}', b'\\.{}')
        self.register(u'\N{RING ABOVE}', b'\\r{}')
        self.register(u'\N{OGONEK}', b'\\k{}')
        self.register(u'\N{DOUBLE ACUTE ACCENT}', b'\\H{}')
        self.register(u'\N{LATIN SMALL LIGATURE FI}', b'fi', decode=False)
        self.register(u'\N{LATIN SMALL LIGATURE FL}', b'fl', decode=False)
        self.register(u'\N{LATIN SMALL LIGATURE FF}', b'ff', decode=False)

        self.register(u'\N{GREEK SMALL LETTER ALPHA}', b'\\alpha', mode='math')
        self.register(u'\N{GREEK SMALL LETTER BETA}', b'\\beta', mode='math')
        self.register(u'\N{GREEK SMALL LETTER GAMMA}', b'\\gamma', mode='math')
        self.register(u'\N{GREEK SMALL LETTER DELTA}', b'\\delta', mode='math')
        self.register(
            u'\N{GREEK SMALL LETTER EPSILON}',
            b'\\epsilon',
            mode='math')
        self.register(u'\N{GREEK SMALL LETTER ZETA}', b'\\zeta', mode='math')
        self.register(u'\N{GREEK SMALL LETTER ETA}', b'\\eta', mode='math')
        self.register(u'\N{GREEK SMALL LETTER THETA}', b'\\theta', mode='math')
        self.register(u'\N{GREEK SMALL LETTER IOTA}', b'\\iota', mode='math')
        self.register(u'\N{GREEK SMALL LETTER KAPPA}', b'\\kappa', mode='math')
        self.register(
            u'\N{GREEK SMALL LETTER LAMDA}',
            b'\\lambda',
            mode='math')  # LAMDA not LAMBDA
        self.register(u'\N{GREEK SMALL LETTER MU}', b'\\mu', mode='math')
        self.register(u'\N{GREEK SMALL LETTER NU}', b'\\nu', mode='math')
        self.register(u'\N{GREEK SMALL LETTER XI}', b'\\xi', mode='math')
        self.register(
            u'\N{GREEK SMALL LETTER OMICRON}',
            b'\\omicron',
            mode='math')
        self.register(u'\N{GREEK SMALL LETTER PI}', b'\\pi', mode='math')
        self.register(u'\N{GREEK SMALL LETTER RHO}', b'\\rho', mode='math')
        self.register(u'\N{GREEK SMALL LETTER SIGMA}', b'\\sigma', mode='math')
        self.register(u'\N{GREEK SMALL LETTER TAU}', b'\\tau', mode='math')
        self.register(
            u'\N{GREEK SMALL LETTER UPSILON}',
            b'\\upsilon',
            mode='math')
        self.register(u'\N{GREEK SMALL LETTER PHI}', b'\\phi', mode='math')
        self.register(u'\N{GREEK SMALL LETTER CHI}', b'\\chi', mode='math')
        self.register(u'\N{GREEK SMALL LETTER PSI}', b'\\psi', mode='math')
        self.register(u'\N{GREEK SMALL LETTER OMEGA}', b'\\omega', mode='math')
        self.register(
            u'\N{GREEK CAPITAL LETTER ALPHA}',
            b'\\Alpha',
            mode='math')
        self.register(u'\N{GREEK CAPITAL LETTER BETA}', b'\\Beta', mode='math')
        self.register(
            u'\N{GREEK CAPITAL LETTER GAMMA}',
            b'\\Gamma',
            mode='math')
        self.register(
            u'\N{GREEK CAPITAL LETTER DELTA}',
            b'\\Delta',
            mode='math')
        self.register(
            u'\N{GREEK CAPITAL LETTER EPSILON}',
            b'\\Epsilon',
            mode='math')
        self.register(u'\N{GREEK CAPITAL LETTER ZETA}', b'\\Zeta', mode='math')
        self.register(u'\N{GREEK CAPITAL LETTER ETA}', b'\\Eta', mode='math')
        self.register(
            u'\N{GREEK CAPITAL LETTER THETA}',
            b'\\Theta',
            mode='math')
        self.register(u'\N{GREEK CAPITAL LETTER IOTA}', b'\\Iota', mode='math')
        self.register(
            u'\N{GREEK CAPITAL LETTER KAPPA}',
            b'\\Kappa',
            mode='math')
        self.register(
            u'\N{GREEK CAPITAL LETTER LAMDA}',
            b'\\Lambda',
            mode='math')  # LAMDA not LAMBDA
        self.register(u'\N{GREEK CAPITAL LETTER MU}', b'\\Mu', mode='math')
        self.register(u'\N{GREEK CAPITAL LETTER NU}', b'\\Nu', mode='math')
        self.register(u'\N{GREEK CAPITAL LETTER XI}', b'\\Xi', mode='math')
        self.register(
            u'\N{GREEK CAPITAL LETTER OMICRON}',
            b'\\Omicron',
            mode='math')
        self.register(u'\N{GREEK CAPITAL LETTER PI}', b'\\Pi', mode='math')
        self.register(u'\N{GREEK CAPITAL LETTER RHO}', b'\\Rho', mode='math')
        self.register(
            u'\N{GREEK CAPITAL LETTER SIGMA}',
            b'\\Sigma',
            mode='math')
        self.register(u'\N{GREEK CAPITAL LETTER TAU}', b'\\Tau', mode='math')
        self.register(
            u'\N{GREEK CAPITAL LETTER UPSILON}',
            b'\\Upsilon',
            mode='math')
        self.register(u'\N{GREEK CAPITAL LETTER PHI}', b'\\Phi', mode='math')
        self.register(u'\N{GREEK CAPITAL LETTER CHI}', b'\\Chi', mode='math')
        self.register(u'\N{GREEK CAPITAL LETTER PSI}', b'\\Psi', mode='math')
        self.register(
            u'\N{GREEK CAPITAL LETTER OMEGA}',
            b'\\Omega',
            mode='math')
        self.register(u'\N{COPYRIGHT SIGN}', b'\\copyright')
        self.register(u'\N{COPYRIGHT SIGN}', b'\\textcopyright')
        self.register(u'\N{LATIN CAPITAL LETTER A WITH ACUTE}', b"\\'A")
        self.register(u'\N{LATIN CAPITAL LETTER I WITH ACUTE}', b"\\'I")
        self.register(u'\N{HORIZONTAL ELLIPSIS}', b'\\ldots')
        self.register(u'\N{TRADE MARK SIGN}', b'^{TM}', mode='math')
        self.register(
            u'\N{TRADE MARK SIGN}',
            b'\\texttrademark',
            package='textcomp')
        # \=O and \=o will be translated into Ō and ō before we can
        # match the full latex string... so decoding disabled for now
        self.register(u'Ǭ', br'\textogonekcentered{\=O}', decode=False)
        self.register(u'ǭ', br'\textogonekcentered{\=o}', decode=False)
        self.register(u'ℕ', br'\mathbb{N}', mode='math')
        self.register(u'ℕ', br'\mathbb N', mode='math', decode=False)
        self.register(u'ℤ', br'\mathbb{Z}', mode='math')
        self.register(u'ℤ', br'\mathbb Z', mode='math', decode=False)
        self.register(u'ℚ', br'\mathbb{Q}', mode='math')
        self.register(u'ℚ', br'\mathbb Q', mode='math', decode=False)
        self.register(u'ℝ', br'\mathbb{R}', mode='math')
        self.register(u'ℝ', br'\mathbb R', mode='math', decode=False)
        self.register(u'ℂ', br'\mathbb{C}', mode='math')
        self.register(u'ℂ', br'\mathbb C', mode='math', decode=False)

    def register(self, unicode_text, latex_text, mode='text', package=None,
                 decode=True, encode=True):
        """Register a correspondence between *unicode_text* and *latex_text*.

        :param str unicode_text: A unicode character.
        :param bytes latex_text: Its corresponding LaTeX translation.
        :param str mode: LaTeX mode in which the translation applies
            (``'text'`` or ``'math'``).
        :param str package: LaTeX package requirements (currently ignored).
        :param bool decode: Whether this translation applies to decoding
            (default: ``True``).
        :param bool encode: Whether this translation applies to encoding
            (default: ``True``).
        """
        if mode == 'math':
            # also register text version
            self.register(unicode_text, b'$' + latex_text + b'$', mode='text',
                          package=package, decode=decode, encode=encode)
            self.register(unicode_text,
                          br'\(' + latex_text + br'\)', mode='text',
                          package=package, decode=decode, encode=encode)
            # XXX for the time being, we do not perform in-math substitutions
            return
        if not self.lexer.binary_mode:
            latex_text = latex_text.decode("ascii")
        if package is not None:
            # TODO implement packages
            pass
        # tokenize, and register unicode translation
        self.lexer.reset()
        self.lexer.state = 'M'
        tokens = tuple(self.lexer.get_tokens(latex_text, final=True))
        if decode:
            if tokens not in self.unicode_map:
                self.max_length = max(self.max_length, len(tokens))
                self.unicode_map[tokens] = unicode_text
            # also register token variant with brackets, if appropriate
            # for instance, "\'{e}" for "\'e", "\c{c}" for "\c c", etc.
            # note: we do not remove brackets (they sometimes matter,
            # e.g. bibtex uses them to prevent lower case transformation)
            if (len(tokens) == 2 and
                tokens[0].name.startswith('control') and
                    tokens[1].name == 'chars'):
                alt_tokens = (tokens[0], self.lexer.curlylefttoken, tokens[1],
                              self.lexer.curlyrighttoken)
                if alt_tokens not in self.unicode_map:
                    self.max_length = max(self.max_length, len(alt_tokens))
                    self.unicode_map[alt_tokens] = u"{" + unicode_text + u"}"
        if encode and unicode_text not in self.latex_map:
            assert len(unicode_text) == 1
            self.latex_map[unicode_text] = (latex_text, tokens)


_LATEX_UNICODE_TABLE = LatexUnicodeTable(lexer.LatexIncrementalDecoder())
_ULATEX_UNICODE_TABLE = LatexUnicodeTable(
    lexer.UnicodeLatexIncrementalDecoder())

# incremental encoder does not need a buffer
# but decoder does


class LatexIncrementalEncoder(lexer.LatexIncrementalEncoder):

    """Translating incremental encoder for latex. Maintains a state to
    determine whether control spaces etc. need to be inserted.
    """

    table = _LATEX_UNICODE_TABLE
    """Translation table."""

    def __init__(self, errors='strict'):
        super(LatexIncrementalEncoder, self).__init__(errors=errors)
        self.reset()

    def reset(self):
        super(LatexIncrementalEncoder, self).reset()
        self.state = 'M'

    def get_space_bytes(self, bytes_):
        """Inserts space bytes in space eating mode."""
        if self.state == 'S':
            # in space eating mode
            # control space needed?
            if bytes_.startswith(self.spacechar):
                # replace by control space
                return self.controlspacechar, bytes_[1:]
            else:
                # insert space (it is eaten, but needed for separation)
                return self.spacechar, bytes_
        else:
            return self.emptychar, bytes_

    def _get_latex_bytes_tokens_from_char(self, c):
        # if ascii, try latex equivalents
        # (this covers \, #, &, and other special LaTeX characters)
        if ord(c) < 128:
            try:
                return self.table.latex_map[c]
            except KeyError:
                pass
        # next, try input encoding
        try:
            bytes_ = c.encode(self.inputenc, 'strict')
        except UnicodeEncodeError:
            pass
        else:
            if self.binary_mode:
                return bytes_, (lexer.Token(name='chars', text=bytes_),)
            else:
                return c, (lexer.Token(name='chars', text=c),)
        # next, try latex equivalents of common unicode characters
        try:
            return self.table.latex_map[c]
        except KeyError:
            # translation failed
            if self.errors == 'strict':
                raise UnicodeEncodeError(
                    "latex",  # codec
                    c,  # problematic input
                    0, 1,  # location of problematic character
                    "don't know how to translate {0} into latex"
                    .format(repr(c)))
            elif self.errors == 'ignore':
                return self.emptychar, (self.emptytoken,)
            elif self.errors == 'replace':
                # use the \\char command
                # this assumes
                # \usepackage[T1]{fontenc}
                # \usepackage[utf8]{inputenc}
                if self.binary_mode:
                    bytes_ = b'{\\char' + str(ord(c)).encode("ascii") + b'}'
                else:
                    bytes_ = u'{\\char' + str(ord(c)) + u'}'
                return bytes_, (lexer.Token(name='chars', text=bytes_),)
            elif self.errors == 'keep' and not self.binary_mode:
                return c,  (lexer.Token(name='chars', text=c),)
            else:
                raise ValueError(
                    "latex codec does not support {0} errors"
                    .format(self.errors))

    def get_latex_bytes(self, unicode_, final=False):
        if not isinstance(unicode_, string_types):
            raise TypeError(
                "expected unicode for encode input, but got {0} instead"
                .format(unicode_.__class__.__name__))
        # convert character by character
        for pos, c in enumerate(unicode_):
            bytes_, tokens = self._get_latex_bytes_tokens_from_char(c)
            space, bytes_ = self.get_space_bytes(bytes_)
            # update state
            if tokens[-1].name == 'control_word':
                # we're eating spaces
                self.state = 'S'
            else:
                self.state = 'M'
            if space:
                yield space
            yield bytes_


class LatexIncrementalDecoder(lexer.LatexIncrementalDecoder):

    """Translating incremental decoder for LaTeX."""

    table = _LATEX_UNICODE_TABLE
    """Translation table."""

    def __init__(self, errors='strict'):
        lexer.LatexIncrementalDecoder.__init__(self, errors=errors)

    def reset(self):
        lexer.LatexIncrementalDecoder.reset(self)
        self.token_buffer = []

    # python codecs API does not support multibuffer incremental decoders

    def getstate(self):
        raise NotImplementedError

    def setstate(self, state):
        raise NotImplementedError

    def get_unicode_tokens(self, bytes_, final=False):
        for token in self.get_tokens(bytes_, final=final):
            # at this point, token_buffer does not match anything
            self.token_buffer.append(token)
            # new token appended at the end, see if we have a match now
            # note: match is only possible at the *end* of the buffer
            # because all other positions have already been checked in
            # earlier iterations
            for i in range(len(self.token_buffer), 0, -1):
                last_tokens = tuple(self.token_buffer[-i:])  # last i tokens
                try:
                    unicode_text = self.table.unicode_map[last_tokens]
                except KeyError:
                    # no match: continue
                    continue
                else:
                    # match!! flush buffer, and translate last bit
                    # exclude last i tokens
                    for token in self.token_buffer[:-i]:
                        yield self.decode_token(token)
                    yield unicode_text
                    self.token_buffer = []
                    break
            # flush tokens that can no longer match
            while len(self.token_buffer) >= self.table.max_length:
                yield self.decode_token(self.token_buffer.pop(0))
        # also flush the buffer at the end
        if final:
            for token in self.token_buffer:
                yield self.decode_token(token)
            self.token_buffer = []


class LatexCodec(codecs.Codec):
    IncrementalEncoder = None
    IncrementalDecoder = None

    def encode(self, unicode_, errors='strict'):
        """Convert unicode string to LaTeX bytes."""
        encoder = self.IncrementalEncoder(errors=errors)
        return (
            encoder.encode(unicode_, final=True),
            len(unicode_),
        )

    def decode(self, bytes_, errors='strict'):
        """Convert LaTeX bytes to unicode string."""
        decoder = self.IncrementalDecoder(errors=errors)
        return (
            decoder.decode(bytes_, final=True),
            len(bytes_),
        )


class UnicodeLatexIncrementalDecoder(LatexIncrementalDecoder):
    table = _ULATEX_UNICODE_TABLE
    binary_mode = False


class UnicodeLatexIncrementalEncoder(LatexIncrementalEncoder):
    table = _ULATEX_UNICODE_TABLE
    binary_mode = False


def find_latex(encoding):
    """Return a :class:`codecs.CodecInfo` instance for the requested
    LaTeX *encoding*, which must be equal to ``latex``,
    or to ``latex+<encoding>``
    where ``<encoding>`` describes another encoding.
    """
    encoding, _, inputenc_ = encoding.partition(u"+")
    if not inputenc_:
        inputenc_ = "ascii"
    if encoding == "latex":
        IncEnc = LatexIncrementalEncoder
        DecEnc = LatexIncrementalDecoder
    elif encoding == "ulatex":
        IncEnc = UnicodeLatexIncrementalEncoder
        DecEnc = UnicodeLatexIncrementalDecoder
    else:
        return None

    class IncrementalEncoder_(IncEnc):
        inputenc = inputenc_

    class IncrementalDecoder_(DecEnc):
        inputenc = inputenc_

    class Codec(LatexCodec):
        IncrementalEncoder = IncrementalEncoder_
        IncrementalDecoder = IncrementalDecoder_

    class StreamWriter(Codec, codecs.StreamWriter):
        pass

    class StreamReader(Codec, codecs.StreamReader):
        pass

    return codecs.CodecInfo(
        encode=Codec().encode,
        decode=Codec().decode,
        incrementalencoder=Codec.IncrementalEncoder,
        incrementaldecoder=Codec.IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
    )

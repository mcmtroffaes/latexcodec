# -*- coding: utf-8 -*-
"""Tests for the latex codec."""

from __future__ import print_function

import codecs
import pytest
from six import text_type, binary_type, BytesIO, PY2
from unittest import TestCase

import latexcodec


def test_getregentry():
    assert latexcodec.codec.getregentry() is not None


def test_find_latex():
    assert latexcodec.codec.find_latex('hello') is None


def test_latex_incremental_decoder_getstate():
    encoder = codecs.getincrementaldecoder('latex')()
    with pytest.raises(NotImplementedError):
        encoder.getstate()


def test_latex_incremental_decoder_setstate():
    encoder = codecs.getincrementaldecoder('latex')()
    state = (u'', 0)
    with pytest.raises(NotImplementedError):
        encoder.setstate(state)


def split_input(input_):
    """Helper function for testing the incremental encoder and decoder."""
    if not isinstance(input_, (text_type, binary_type)):
        raise TypeError("expected unicode or bytes input")
    if input_:
        for i in range(len(input_)):
            if i + 1 < len(input_):
                yield input_[i:i + 1], False
            else:
                yield input_[i:i + 1], True
    else:
        yield input_, True


class TestDecoder(TestCase):

    """Stateless decoder tests."""
    maxDiff = None

    def decode(self, text_utf8, text_latex, inputenc=None):
        """Main test function."""
        encoding = 'latex+' + inputenc if inputenc else 'latex'
        decoded, n = codecs.getdecoder(encoding)(text_latex)
        self.assertEqual((decoded, n), (text_utf8, len(text_latex)))

    def test_invalid_type(self):
        with pytest.raises(TypeError):
            codecs.getdecoder("latex")(object())

    def test_invalid_code(self):
        with pytest.raises(ValueError):
            # b'\xe9' is invalid utf-8 code
            self.decode(u'', b'\xe9  ', 'utf-8')

    def test_null(self):
        self.decode(u'', b'')

    def test_maelstrom(self):
        self.decode(u"mælström", br'm\ae lstr\"om')

    def test_maelstrom_latin1(self):
        self.decode(u"mælström", b'm\\ae lstr\xf6m', 'latin1')

    def test_laren(self):
        self.decode(
            u"© låren av björn",
            br'\copyright\ l\aa ren av bj\"orn')

    def test_laren_brackets(self):
        self.decode(
            u"© l{å}ren av bj{ö}rn",
            br'\copyright\ l{\aa}ren av bj{\"o}rn')

    def test_laren_latin1(self):
        self.decode(
            u"© låren av björn",
            b'\\copyright\\ l\xe5ren av bj\xf6rn',
            'latin1')

    def test_droitcivil(self):
        self.decode(
            u"Même s'il a fait l'objet d'adaptations suite à l'évolution, "
            u"la transformation sociale, économique et politique du pays, "
            u"le code civil fran{ç}ais est aujourd'hui encore le texte "
            u"fondateur "
            u"du droit civil français mais aussi du droit civil belge "
            u"ainsi que "
            u"de plusieurs autres droits civils.",
            b"M\\^eme s'il a fait l'objet d'adaptations suite "
            b"\\`a l'\\'evolution, \nla transformation sociale, "
            b"\\'economique et politique du pays, \nle code civil "
            b"fran\\c{c}ais est aujourd'hui encore le texte fondateur \n"
            b"du droit civil fran\\c cais mais aussi du droit civil "
            b"belge ainsi que \nde plusieurs autres droits civils.",
        )

    def test_oeuf(self):
        self.decode(
            u"D'un point de vue diététique, l'œuf apaise la faim.",
            br"D'un point de vue di\'et\'etique, l'\oe uf apaise la faim.",
        )

    def test_oeuf_latin1(self):
        self.decode(
            u"D'un point de vue diététique, l'œuf apaise la faim.",
            b"D'un point de vue di\xe9t\xe9tique, l'\\oe uf apaise la faim.",
            'latin1'
        )

    def test_alpha(self):
        self.decode(u"α", b"$\\alpha$")

    def test_maelstrom_multibyte_encoding(self):
        self.decode(u"\\c öké", b'\\c \xc3\xb6k\xc3\xa9', 'utf8')

    def test_serafin(self):
        self.decode(u"Seraf{\xed}n", b"Seraf{\\'i}n")

    def test_astrom(self):
        self.decode(u"{\xc5}str{\xf6}m", b'{\\AA}str{\\"o}m')

    def test_space_1(self):
        self.decode(u"ææ", br'\ae \ae')

    def test_space_2(self):
        self.decode(u"æ æ", br'\ae\ \ae')

    def test_space_3(self):
        self.decode(u"æ æ", br'\ae \quad \ae')

    def test_number_sign_1(self):
        self.decode(u"# hello", br'\#\ hello')

    def test_number_sign_2(self):
        # LaTeX does not absorb the space following '\#':
        # check decoding is correct
        self.decode(u"# hello", br'\# hello')

    def test_number_sign_3(self):
        # a single '#' is not valid LaTeX:
        # for the moment we ignore this error and return # unchanged
        self.decode(u"# hello", br'# hello')

    def test_underscore(self):
        self.decode(u"_", br'\_')

    def test_dz(self):
        self.decode(u"DZ", br'DZ')

    def test_newline(self):
        self.decode(u"hello world", b"hello\nworld")

    def test_par1(self):
        self.decode(u"hello\n\nworld", b"hello\n\nworld")

    def test_par2(self):
        self.decode(u"hello\n\nworld", b"hello\\par world")

    def test_par3(self):
        self.decode(u"hello\n\nworld", b"hello \\par world")

    def test_ogonek1(self):
        self.decode(u"ĄąĘęĮįǪǫŲų",
                    br'\k A\k a\k E\k e\k I\k i\k O\k o\k U\k u')

    def test_ogonek2(self):
        # note: should decode into u"Ǭǭ" but can't support this yet...
        self.decode(u"\\textogonekcentered {Ō}\\textogonekcentered {ō}",
                    br'\textogonekcentered{\=O}\textogonekcentered{\=o}')

    def test_math_spacing_dollar(self):
        self.decode(u'This is a ψ test.', br'This is a $\psi$ test.')

    def test_math_spacing_brace(self):
        self.decode(u'This is a ψ test.', br'This is a \(\psi\) test.')

    def test_double_math(self):
        # currently no attempt to translate maths inside $$
        self.decode(u'This is a $$\\psi $$ test.',
                    br'This is a $$\psi$$ test.')

    def test_tilde(self):
        self.decode(u'This is a ˜, ˷, ∼ and ~test.',
                    (br'This is a \~{}, \texttildelow, '
                     br'$\sim$ and \textasciitilde test.'))

    def test_backslash(self):
        self.decode(u'This is a \\ \\test.',
                    br'This is a $\backslash$ \textbackslash test.')

    def test_percent(self):
        self.decode(u'This is a % test.',
                    br'This is a \% test.')

    def test_math_minus(self):
        self.decode(u'This is a − test.',
                    br'This is a $-$ test.')

    def test_swedish_again(self):
        self.decode(
            u"l{å}ren l{Å}ren",
            br'l{\r a}ren l{\r A}ren')

    def test_double_quotes(self):
        self.decode(u"“a+b”", br"``a+b''")

    def test_double_quotes_unicode(self):
        self.decode(u"“á”", u"``á''".encode("utf8"), "utf8")

    def test_double_quotes_gb2312(self):
        self.decode(u"“你好”", u"``你好''".encode('gb2312'), 'gb2312')

    def test_theta(self):
        self.decode(u"θ", br"$\theta$")
        self.decode(u"θ", br"\texttheta")

    def test_decode_comment(self):
        self.decode(u"\\\\", br"\\%")
        self.decode(u"% abc \\\\\\\\% ghi",
                    b"\\% abc\n\\\\% def\n\\\\\\% ghi")

    def test_decode_lower_quotes(self):
        self.decode(u"„", br",,")
        self.decode(u"„", br"\glqq")


class TestStreamDecoder(TestDecoder):

    """Stream decoder tests."""

    def decode(self, text_utf8, text_latex, inputenc=None):
        encoding = 'latex+' + inputenc if inputenc else 'latex'
        stream = BytesIO(text_latex)
        reader = codecs.getreader(encoding)(stream)
        self.assertEqual(text_utf8, reader.read())

    # in this test, BytesIO(object()) is eventually called
    # this is valid on Python 2, so we skip this test there
    def test_invalid_type(self):
        if PY2:
            pytest.skip("test not relevant for Python 2")
        else:
            TestDecoder.test_invalid_type(self)


class TestIncrementalDecoder(TestDecoder):

    """Incremental decoder tests."""

    def decode(self, text_utf8, text_latex, inputenc=None):
        encoding = 'latex+' + inputenc if inputenc else 'latex'
        decoder = codecs.getincrementaldecoder(encoding)()
        decoded_parts = (
            decoder.decode(text_latex_part, final)
            for text_latex_part, final in split_input(text_latex))
        self.assertEqual(text_utf8, u''.join(decoded_parts))


class TestEncoder(TestCase):

    """Stateless encoder tests."""

    def encode(self, text_utf8, text_latex, inputenc=None, errors='strict'):
        """Main test function."""
        encoding = 'latex+' + inputenc if inputenc else 'latex'
        encoded, n = codecs.getencoder(encoding)(text_utf8, errors=errors)
        self.assertEqual((encoded, n), (text_latex, len(text_utf8)))

    def test_invalid_type(self):
        with pytest.raises(TypeError):
            codecs.getencoder("latex")(object())

    # note concerning test_invalid_code_* methods:
    # u'\u2328' (0x2328 = 9000) is unicode for keyboard symbol
    # we currently provide no translation for this into LaTeX code

    def test_invalid_code_strict(self):
        with pytest.raises(ValueError):
            self.encode(u'\u2328', b'', 'ascii', 'strict')

    def test_invalid_code_ignore(self):
        self.encode(u'\u2328', b'', 'ascii', 'ignore')

    def test_invalid_code_replace(self):
        self.encode(u'\u2328', b'{\\char9000}', 'ascii', 'replace')

    def test_invalid_code_baderror(self):
        with pytest.raises(ValueError):
            self.encode(u'\u2328', b'', 'ascii', '**baderror**')

    def test_null(self):
        self.encode(u'', b'')

    def test_maelstrom(self):
        self.encode(u"mælström", br'm\ae lstr\"om')

    def test_maelstrom_latin1(self):
        self.encode(u"mælström", b'm\xe6lstr\xf6m', 'latin1')

    def test_laren(self):
        self.encode(
            u"© låren av björn",
            br'\copyright\ l\aa ren av bj\"orn')

    def test_laren_latin1(self):
        self.encode(
            u"© låren av björn",
            b'\xa9 l\xe5ren av bj\xf6rn',
            'latin1')

    def test_droitcivil(self):
        self.encode(
            u"Même s'il a fait l'objet d'adaptations suite à l'évolution, \n"
            u"la transformation sociale, économique et politique du pays, \n"
            u"le code civil fran{ç}ais est aujourd'hui encore le texte "
            u"fondateur \n"
            u"du droit civil français mais aussi du droit civil belge "
            u"ainsi que \n"
            u"de plusieurs autres droits civils.",
            b"M\\^eme s'il a fait l'objet d'adaptations suite "
            b"\\`a l'\\'evolution, \nla transformation sociale, "
            b"\\'economique et politique du pays, \nle code civil "
            b"fran{\\c c}ais est aujourd'hui encore le texte fondateur \n"
            b"du droit civil fran\\c cais mais aussi du droit civil "
            b"belge ainsi que \nde plusieurs autres droits civils.",
        )

    def test_oeuf(self):
        self.encode(
            u"D'un point de vue diététique, l'œuf apaise la faim.",
            br"D'un point de vue di\'et\'etique, l'\oe uf apaise la faim.",
        )

    def test_oeuf_latin1(self):
        self.encode(
            u"D'un point de vue diététique, l'œuf apaise la faim.",
            b"D'un point de vue di\xe9t\xe9tique, l'\\oe uf apaise la faim.",
            'latin1'
        )

    def test_alpha(self):
        self.encode(u"α", b"$\\alpha$")

    def test_serafin(self):
        self.encode(u"Seraf{\xed}n", b"Seraf{\\'\\i }n")

    def test_space_1(self):
        self.encode(u"ææ", br'\ae \ae')

    def test_space_2(self):
        self.encode(u"æ æ", br'\ae\ \ae')

    def test_space_3(self):
        self.encode(u"æ æ", br'\ae \quad \ae')

    def test_number_sign(self):
        # note: no need for control space after \#
        self.encode(u"# hello", br'\# hello')

    def test_underscore(self):
        self.encode(u"_", br'\_')

    def test_dz1(self):
        self.encode(u"DZ", br'DZ')

    def test_dz2(self):
        self.encode(u"Ǳ", br'DZ')

    def test_newline(self):
        self.encode(u"hello\nworld", b"hello\nworld")

    def test_par1(self):
        self.encode(u"hello\n\nworld", b"hello\n\nworld")

    def test_par2(self):
        self.encode(u"hello\\par world", b"hello\\par world")

    def test_ogonek1(self):
        self.encode(u"ĄąĘęĮįǪǫŲų",
                    br'\k A\k a\k E\k e\k I\k i\k O\k o\k U\k u')

    def test_ogonek2(self):
        self.encode(u"Ǭǭ",
                    br'\textogonekcentered{\=O}\textogonekcentered{\=o}')

    def test_math_spacing(self):
        self.encode(u'This is a ψ test.', br'This is a $\psi$ test.')

    def test_double_math(self):
        # currently no attempt to translate maths inside $$
        self.encode(u'This is a $$\\psi$$ test.', br'This is a $$\psi$$ test.')

    def test_tilde(self):
        self.encode(u'This is a ˜, ˷, ∼ and ~test.',
                    (br'This is a \~{}, \texttildelow , '
                     br'$\sim$ and \textasciitilde test.'))

    def test_percent(self):
        self.encode(u'This is a % test.',
                    br'This is a \% test.')

    def test_hyphen(self):
        self.encode(u'This is a \N{HYPHEN} test.',
                    br'This is a - test.')

    def test_math_minus(self):
        self.encode(u'This is a − test.',
                    br'This is a $-$ test.')

    def test_double_quotes(self):
        self.encode(u"“a+b”", br"``a+b''")

    def test_double_quotes_unicode(self):
        self.encode(u"“á”", br"``\'a''")

    def test_thin_space(self):
        self.encode(u"a\u2009b", b"a b")

    def test_theta(self):
        self.encode(u"θ", br"$\theta$")

    def test_encode_lower_quotes(self):
        self.encode(u"„", br",,")


class TestStreamEncoder(TestEncoder):

    """Stream encoder tests."""

    def encode(self, text_utf8, text_latex, inputenc=None, errors='strict'):
        encoding = 'latex+' + inputenc if inputenc else 'latex'
        stream = BytesIO()
        writer = codecs.getwriter(encoding)(stream, errors=errors)
        writer.write(text_utf8)
        self.assertEqual(text_latex, stream.getvalue())


class TestIncrementalEncoder(TestEncoder):

    """Incremental encoder tests."""

    def encode(self, text_utf8, text_latex, inputenc=None, errors='strict'):
        encoding = 'latex+' + inputenc if inputenc else 'latex'
        encoder = codecs.getincrementalencoder(encoding)(errors=errors)
        encoded_parts = (
            encoder.encode(text_utf8_part, final)
            for text_utf8_part, final in split_input(text_utf8))
        self.assertEqual(text_latex, b''.join(encoded_parts))


class TestUnicodeDecoder(TestDecoder):

    def decode(self, text_utf8, text_latex, inputenc=None):
        """Main test function."""
        text_latex = text_latex.decode(inputenc if inputenc else "ascii")
        decoded, n = codecs.getdecoder('ulatex')(text_latex)
        self.assertEqual((decoded, n), (text_utf8, len(text_latex)))


class TestUnicodeEncoder(TestEncoder):

    def encode(self, text_utf8, text_latex, inputenc=None, errors='strict'):
        """Main test function."""
        encoding = 'ulatex+' + inputenc if inputenc else 'ulatex'
        text_latex = text_latex.decode(inputenc if inputenc else 'ascii')
        encoded, n = codecs.getencoder(encoding)(text_utf8, errors=errors)
        self.assertEqual((encoded, n), (text_latex, len(text_utf8)))

    def uencode(self, text_utf8, text_ulatex, inputenc=None, errors='strict'):
        """Main test function."""
        encoding = 'ulatex+' + inputenc if inputenc else 'ulatex'
        encoded, n = codecs.getencoder(encoding)(text_utf8, errors=errors)
        self.assertEqual((encoded, n), (text_ulatex, len(text_utf8)))

    def test_ulatex_ascii(self):
        self.uencode(u'# ψ', u'\\# $\\psi$', 'ascii')

    def test_ulatex_utf8(self):
        self.uencode(u'# ψ', u'\\# ψ', 'utf8')

    # the following tests rely on the fact that \u2328 is not in our
    # translation table

    def test_ulatex_ascii_invalid(self):
        with pytest.raises(ValueError):
            self.uencode(u'# \u2328', u'', 'ascii')

    def test_ulatex_utf8_invalid(self):
        self.uencode(u'# ψ \u2328', u'\\# ψ \u2328', 'utf8')

    def test_invalid_code_keep(self):
        self.uencode(u'# ψ \u2328', u'\\# $\\psi$ \u2328', 'ascii', 'keep')

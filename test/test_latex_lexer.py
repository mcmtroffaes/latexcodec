# -*- coding: utf-8 -*-

"""Tests for the tex lexer."""

import pytest
from unittest import TestCase
import six

from latexcodec.lexer import (
    LatexLexer,
    LatexIncrementalLexer,
    LatexIncrementalDecoder, UnicodeLatexIncrementalDecoder,
    LatexIncrementalEncoder, UnicodeLatexIncrementalEncoder,
    Token)


class MockLexer(LatexLexer):
    tokens = (
        ('chars', u'mock'),
        ('unknown', u'.'),
        )


class MockIncrementalDecoder(LatexIncrementalDecoder):
    tokens = (
        ('chars', u'mock'),
        ('unknown', u'.'),
        )


def test_token_create_with_args():
    t = Token('hello', u'world')
    assert t.name == 'hello'
    assert t.text == u'world'


def test_token_assign_name():
    with pytest.raises(AttributeError):
        t = Token('hello', u'world')
        t.name = 'test'


def test_token_assign_text():
    with pytest.raises(AttributeError):
        t = Token('hello', u'world')
        t.text = 'test'


def test_token_assign_other():
    with pytest.raises(AttributeError):
        t = Token('hello', u'world')
        t.blabla = 'test'


class BaseLatexLexerTest(TestCase):

    errors = 'strict'
    Lexer = None

    def setUp(self):
        self.lexer = self.Lexer(errors=self.errors)

    def lex_it(self, latex_code, latex_tokens, final=False):
        tokens = self.lexer.get_raw_tokens(latex_code, final=final)
        self.assertEqual(
            list(token.text for token in tokens),
            latex_tokens)

    def tearDown(self):
        del self.lexer


class LatexLexerTest(BaseLatexLexerTest):

    Lexer = LatexLexer

    def test_null(self):
        self.lex_it('', [], final=True)

    def test_hello(self):
        self.lex_it(
            u'hello!  [#1] This \\is\\   \\^ a \ntest.\n'
            u'    \nHey.\n\n\\# x \\#x',
            six.u(r'h|e|l|l|o|!| | |[|#1|]| |T|h|i|s| |\is|\ | | |\^| |a| '
                  '|\n|t|e|s|t|.|\n| | | | |\n|H|e|y|.|\n|\n'
                  r'|\#| |x| |\#|x').split(u'|'),
            final=True
        )

    def test_comment(self):
        self.lex_it(
            u'test% some comment\ntest',
            u't|e|s|t|% some comment|\n|t|e|s|t'.split(u'|'),
            final=True
        )

    def test_comment_newline(self):
        self.lex_it(
            u'test% some comment\n\ntest',
            u't|e|s|t|% some comment|\n|\n|t|e|s|t'.split(u'|'),
            final=True
        )

    def test_control(self):
        self.lex_it(
            u'\\hello\\world',
            u'\\hello|\\world'.split(u'|'),
            final=True
        )

    def test_control_whitespace(self):
        self.lex_it(
            u'\\hello   \\world   ',
            u'\\hello| | | |\\world| | | '.split(u'|'),
            final=True
        )

    def test_controlx(self):
        self.lex_it(
            u'\\#\\&',
            u'\\#|\\&'.split(u'|'),
            final=True
        )

    def test_controlx_whitespace(self):
        self.lex_it(
            u'\\#    \\&   ',
            u'\\#| | | | |\\&| | | '.split(u'|'),
            final=True
        )

    def test_buffer(self):
        self.lex_it(
            u'hi\\t',
            u'h|i'.split(u'|'),
        )
        self.lex_it(
            'here',
            [u'\\there'],
            final=True,
        )

    def test_state(self):
        self.lex_it(
            u'hi\\t',
            u'h|i'.split(u'|'),
        )
        state = self.lexer.getstate()
        self.lexer.reset()
        self.lex_it(
            u'here',
            u'h|e|r|e'.split(u'|'),
            final=True,
        )
        self.lexer.setstate(state)
        self.lex_it(
            u'here',
            [u'\\there'],
            final=True,
        )

    def test_decode(self):
        with pytest.raises(NotImplementedError):
            self.lexer.decode(b'')

    def test_final_backslash(self):
        self.lex_it(
            u'notsogood\\',
            u'n|o|t|s|o|g|o|o|d|\\'.split(u'|'),
            final=True
        )

    def test_final_comment(self):
        self.lex_it(
            u'hello%',
            u'h|e|l|l|o|%'.split(u'|'),
            final=True
        )

    def test_hash(self):
        self.lex_it(u'#', [u'#'], final=True)

    def test_tab(self):
        self.lex_it(u'\\c\tc', u'\\c|\t|c'.split(u'|'), final=True)

    def test_percent(self):
        self.lex_it(u'This is a \\% test.',
                    u'T|h|i|s| |i|s| |a| |\\%| |t|e|s|t|.'.split(u'|'),
                    final=True)
        self.lex_it(u'\\% %test',
                    u'\\%| |%test'.split(u'|'), final=True)
        self.lex_it(u'\\% %test\nhi',
                    u'\\%| |%test|\n|h|i'.split(u'|'), final=True)

    def test_double_quotes(self):
        self.lex_it(u"``a+b''", u"``|a|+|b|''".split(u'|'), final=True)


class BaseLatexIncrementalDecoderTest(TestCase):

    """Tex lexer fixture."""

    errors = 'strict'
    IncrementalDecoder = None

    def setUp(self):
        self.lexer = self.IncrementalDecoder(self.errors)

    def fix(self, s):
        return s if self.lexer.binary_mode else s.decode("ascii")

    def lex_it(self, latex_code, latex_tokens, final=False):
        tokens = self.lexer.get_tokens(latex_code, final=final)
        self.assertEqual(
            list(token.text for token in tokens),
            latex_tokens)

    def tearDown(self):
        del self.lexer


class LatexIncrementalDecoderTest(BaseLatexIncrementalDecoderTest):

    IncrementalDecoder = LatexIncrementalDecoder

    def test_null(self):
        self.lex_it(u'', [], final=True)

    def test_hello(self):
        self.lex_it(
            u'hello!  [#1] This \\is\\   \\^ a \ntest.\n'
            u'    \nHey.\n\n\\# x \\#x',
            six.u(r'h|e|l|l|o|!| |[|#1|]| |T|h|i|s| |\is|\ |\^|a| '
                  r'|t|e|s|t|.| |\par|H|e|y|.| '
                  r'|\par|\#| |x| |\#|x').split(u'|'),
            final=True
        )

    def test_comment(self):
        self.lex_it(
            u'test% some comment\ntest',
            u't|e|s|t|t|e|s|t'.split(u'|'),
            final=True
        )

    def test_comment_newline(self):
        self.lex_it(
            u'test% some comment\n\ntest',
            u't|e|s|t|\\par|t|e|s|t'.split(u'|'),
            final=True
        )

    def test_control(self):
        self.lex_it(
            u'\\hello\\world',
            u'\\hello|\\world'.split(u'|'),
            final=True
        )

    def test_control_whitespace(self):
        self.lex_it(
            u'\\hello   \\world   ',
            u'\\hello|\\world'.split(u'|'),
            final=True
        )

    def test_controlx(self):
        self.lex_it(
            u'\\#\\&',
            u'\\#|\\&'.split(u'|'),
            final=True
        )

    def test_controlx_whitespace(self):
        self.lex_it(
            u'\\#    \\&   ',
            u'\\#| |\\&| '.split(u'|'),
            final=True
        )

    def test_buffer(self):
        self.lex_it(
            u'hi\\t',
            u'h|i'.split(u'|'),
        )
        self.lex_it(
            u'here',
            [u'\\there'],
            final=True,
        )

    def test_buffer_decode(self):
        self.assertEqual(
            self.lexer.decode(self.fix(b'hello!  [#1] This \\i')),
            u'hello! [#1] This ',
        )
        self.assertEqual(
            self.lexer.decode(self.fix(b's\\   \\^ a \ntest.\n')),
            u'\\is \\ \\^a test.',
        )
        self.assertEqual(
            self.lexer.decode(
                self.fix(b'    \nHey.\n\n\\# x \\#x'), final=True),
            u' \\par Hey. \\par \\# x \\#x',
        )

    def test_state_middle(self):
        self.lex_it(
            u'hi\\t',
            u'h|i'.split(u'|'),
        )
        state = self.lexer.getstate()
        self.assertEqual(self.lexer.state, 'M')
        self.assertEqual(self.lexer.raw_buffer.name, 'control_word')
        self.assertEqual(self.lexer.raw_buffer.text, u'\\t')
        self.lexer.reset()
        self.assertEqual(self.lexer.state, 'N')
        self.assertEqual(self.lexer.raw_buffer.name, 'unknown')
        self.assertEqual(self.lexer.raw_buffer.text, u'')
        self.lex_it(
            u'here',
            u'h|e|r|e'.split(u'|'),
            final=True,
        )
        self.lexer.setstate(state)
        self.assertEqual(self.lexer.state, 'M')
        self.assertEqual(self.lexer.raw_buffer.name, 'control_word')
        self.assertEqual(self.lexer.raw_buffer.text, u'\\t')
        self.lex_it(
            u'here',
            [u'\\there'],
            final=True,
        )

    def test_state_inline_math(self):
        self.lex_it(
            u'hi$t',
            u'h|i|$'.split(u'|'),
        )
        assert self.lexer.inline_math
        self.lex_it(
            u'here$',
            u't|h|e|r|e|$'.split(u'|'),
            final=True,
        )
        assert not self.lexer.inline_math

    # counterintuitive?
    def test_final_backslash(self):
        with pytest.raises(UnicodeDecodeError):
            self.lex_it(
                u'notsogood\\',
                [u'notsogood'],
                final=True
            )

    def test_final_comment(self):
        self.lex_it(
            u'hello%',
            u'h|e|l|l|o'.split(u'|'),
            final=True
        )

    def test_hash(self):
        self.lex_it(u'#', [u'#'], final=True)

    def test_tab(self):
        self.lex_it(u'\\c\tc', u'\\c|c'.split(u'|'), final=True)


class UnicodeLatexIncrementalDecoderTest(LatexIncrementalDecoderTest):
    IncrementalDecoder = UnicodeLatexIncrementalDecoder


class LatexIncrementalDecoderReplaceTest(BaseLatexIncrementalDecoderTest):

    errors = 'replace'
    IncrementalDecoder = MockIncrementalDecoder

    def test_errors_replace(self):
        self.lex_it(
            u'helmocklo',
            u'\ufffd|\ufffd|\ufffd|mock|\ufffd|\ufffd'.split(u'|'),
            final=True
        )


class LatexIncrementalDecoderIgnoreTest(BaseLatexIncrementalDecoderTest):

    errors = 'ignore'
    IncrementalDecoder = MockIncrementalDecoder

    def test_errors_ignore(self):
        self.lex_it(
            u'helmocklo',
            u'mock'.split(u'|'),
            final=True
        )


class LatexIncrementalDecoderInvalidErrorTest(BaseLatexIncrementalDecoderTest):

    errors = '**baderror**'
    IncrementalDecoder = MockIncrementalDecoder

    def test_errors_invalid(self):
        with pytest.raises(NotImplementedError):
            self.lex_it(
                u'helmocklo',
                u'?|?|?|mock|?|?'.split(u'|'),
                final=True
            )


def test_invalid_token():
    lexer = LatexIncrementalDecoder()
    # piggyback an implementation which results in invalid tokens
    lexer.get_raw_tokens = lambda bytes_, final: [Token('**invalid**', bytes_)]
    with pytest.raises(AssertionError):
        lexer.decode(b'hello')


def test_invalid_state_1():
    lexer = LatexIncrementalDecoder()
    # piggyback invalid state
    lexer.state = '**invalid**'
    with pytest.raises(AssertionError):
        lexer.decode(b'\n\n\n')


def test_invalid_state_2():
    lexer = LatexIncrementalDecoder()
    # piggyback invalid state
    lexer.state = '**invalid**'
    with pytest.raises(AssertionError):
        lexer.decode(b'   ')


class LatexIncrementalLexerTest(TestCase):

    errors = 'strict'

    def setUp(self):
        self.lexer = LatexIncrementalLexer(errors=self.errors)

    def lex_it(self, latex_code, latex_tokens, final=False):
        tokens = self.lexer.get_tokens(latex_code, final=final)
        self.assertEqual(
            list(token.text for token in tokens),
            latex_tokens)

    def tearDown(self):
        del self.lexer

    def test_newline(self):
        self.lex_it(
            u"hello\nworld", u"h|e|l|l|o| |w|o|r|l|d".split(u'|'),
            final=True)

    def test_par(self):
        self.lex_it(
            u"hello\n\nworld", u"h|e|l|l|o| |\\par|w|o|r|l|d".split(u'|'),
            final=True)


class LatexIncrementalEncoderTest(TestCase):

    """Encoder test fixture."""

    errors = 'strict'
    IncrementalEncoder = LatexIncrementalEncoder

    def setUp(self):
        self.encoder = self.IncrementalEncoder(self.errors)

    def encode(self, latex_code, latex_bytes, final=False):
        result = self.encoder.encode(latex_code, final=final)
        self.assertEqual(result, latex_bytes)

    def tearDown(self):
        del self.encoder

    def test_invalid_type(self):
        with pytest.raises(TypeError):
            self.encoder.encode(object(), final=True)

    def test_invalid_code(self):
        with pytest.raises(ValueError):
            # default encoding is ascii, \u00ff is not ascii translatable
            self.encoder.encode(u"\u00ff", final=True)

    def test_hello(self):
        self.encode(
            u'hello', b'hello' if self.encoder.binary_mode else u'hello',
            final=True)

    def test_unicode_tokens(self):
        self.assertEqual(
            list(self.encoder.get_unicode_tokens(
                u"ĄąĄ̊ą̊ĘęĮįǪǫǬǭŲųY̨y̨", final=True)),
            u"Ą|ą|Ą̊|ą̊|Ę|ę|Į|į|Ǫ|ǫ|Ǭ|ǭ|Ų|ų|Y̨|y̨".split(u"|"))

    def test_state(self):
        self.assertEqual(
            list(self.encoder.get_unicode_tokens(
                u"Ą", final=False)), [])
        state = self.encoder.getstate()
        self.encoder.reset()
        self.assertEqual(
            list(self.encoder.get_unicode_tokens(
                u"ABC", final=True)), [u"A", u"B", u"C"])
        self.encoder.setstate(state)
        self.assertEqual(
            list(self.encoder.get_unicode_tokens(
                u"̊", final=True)), [u"Ą̊"])


class UnicodeLatexIncrementalEncoderTest(LatexIncrementalEncoderTest):
    IncrementalEncoder = UnicodeLatexIncrementalEncoder

    def test_invalid_code(self):
        pass

# -*- coding: utf-8 -*-

"""Tests for the tex lexer."""
from typing import Type, TypeVar, Generic, List, Iterator

import pytest
from unittest import TestCase

from latexcodec.lexer import (
    LatexLexer,
    LatexIncrementalLexer,
    LatexIncrementalDecoder,
    LatexIncrementalEncoder,
    Token)


class MockLexer(LatexLexer):
    tokens = [
        ('chars', 'mock'),
        ('unknown', '.'),
        ]


class MockIncrementalDecoder(LatexIncrementalDecoder):
    tokens = [
        ('chars', 'mock'),
        ('unknown', '.'),
        ]


def test_token_create_with_args():
    t = Token('hello', 'world')
    assert t.name == 'hello'
    assert t.text == 'world'


def test_token_assign_name():
    with pytest.raises(AttributeError):
        t = Token('hello', 'world')
        t.name = 'test'  # type: ignore


def test_token_assign_text():
    with pytest.raises(AttributeError):
        t = Token('hello', 'world')
        t.text = 'test'  # type: ignore


def test_token_assign_other():
    with pytest.raises(AttributeError):
        t = Token('hello', 'world')
        t.blabla = 'test'  # type: ignore


class BaseLatexLexerTest(TestCase):

    errors = 'strict'
    Lexer: Type[LatexLexer]

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
            'hello!  [#1] This \\is\\   \\^ a \ntest.\n'
            '    \nHey.\n\n\\# x \\#x',
            r'h|e|l|l|o|!| | |[|#1|]| |T|h|i|s| |\is|\ | | |\^| |a| '
            '|\n|t|e|s|t|.|\n| | | | |\n|H|e|y|.|\n|\n'
            r'|\#| |x| |\#|x'.split('|'),
            final=True
        )

    def test_comment(self):
        self.lex_it(
            'test% some comment\ntest',
            't|e|s|t|% some comment|\n|t|e|s|t'.split('|'),
            final=True
        )

    def test_comment_newline(self):
        self.lex_it(
            'test% some comment\n\ntest',
            't|e|s|t|% some comment|\n|\n|t|e|s|t'.split('|'),
            final=True
        )

    def test_control(self):
        self.lex_it(
            '\\hello\\world',
            '\\hello|\\world'.split('|'),
            final=True
        )

    def test_control_whitespace(self):
        self.lex_it(
            '\\hello   \\world   ',
            '\\hello| | | |\\world| | | '.split('|'),
            final=True
        )

    def test_controlx(self):
        self.lex_it(
            '\\#\\&',
            '\\#|\\&'.split('|'),
            final=True
        )

    def test_controlx_whitespace(self):
        self.lex_it(
            '\\#    \\&   ',
            '\\#| | | | |\\&| | | '.split('|'),
            final=True
        )

    def test_buffer(self):
        self.lex_it(
            'hi\\t',
            'h|i'.split('|'),
        )
        self.lex_it(
            'here',
            ['\\there'],
            final=True,
        )

    def test_state(self):
        self.lex_it(
            'hi\\t',
            'h|i'.split('|'),
        )
        state = self.lexer.getstate()
        self.lexer.reset()
        self.lex_it(
            'here',
            'h|e|r|e'.split('|'),
            final=True,
        )
        self.lexer.setstate(state)
        self.lex_it(
            'here',
            ['\\there'],
            final=True,
        )

    def test_decode(self):
        with pytest.raises(NotImplementedError):
            self.lexer.decode(b'')

    def test_final_backslash(self):
        self.lex_it(
            'notsogood\\',
            'n|o|t|s|o|g|o|o|d|\\'.split('|'),
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


T = TypeVar('T')


class BaseLatexIncrementalDecoderTest(TestCase, Generic[T]):

    """Tex lexer fixture."""

    errors = 'strict'
    IncrementalDecoder: Type[LatexIncrementalDecoder]

    def setUp(self):
        self.lexer = self.IncrementalDecoder(self.errors)

    def decode(self, input_: T, final: bool = False) -> str:
        raise NotImplementedError

    def lex_it(self, chars: str, latex_tokens: List[str],
               final: bool = False):
        tokens = self.lexer.get_tokens(chars, final=final)
        self.assertEqual(
            list(token.text for token in tokens),
            latex_tokens)

    def tearDown(self):
        del self.lexer


class LatexIncrementalDecoderTest(BaseLatexIncrementalDecoderTest):

    IncrementalDecoder = LatexIncrementalDecoder

    def decode(self, input_: bytes, final: bool = False) -> str:
        return self.lexer.decode(input_, final)

    def test_null(self):
        self.lex_it(u'', [], final=True)

    def test_hello(self):
        self.lex_it(
            u'hello!  [#1] This \\is\\   \\^ a \ntest.\n'
            u'    \nHey.\n\n\\# x \\#x',
            r'h|e|l|l|o|!| |[|#1|]| |T|h|i|s| |\is|\ |\^|a| '
            r'|t|e|s|t|.| |\par|H|e|y|.| '
            r'|\par|\#| |x| |\#|x'.split(u'|'),
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
            self.decode(b'hello!  [#1] This \\i'),
            u'hello! [#1] This ',
        )
        self.assertEqual(
            self.decode(b's\\   \\^ a \ntest.\n'),
            u'\\is \\ \\^a test.',
        )
        self.assertEqual(
            self.decode(b'    \nHey.\n\n\\# x \\#x', final=True),
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

    def decode(self, input_: bytes, final: bool = False) -> str:
        return self.lexer.udecode(input_.decode("ascii"), final)


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


class InvalidTokenLatexIncrementalDecoder(LatexIncrementalDecoder):
    """Decoder which results in invalid tokens."""
    def get_raw_tokens(self, chars: str, final: bool = False
                       ) -> Iterator[Token]:
        return iter([Token('**invalid**', chars)])


def test_invalid_token():
    lexer = InvalidTokenLatexIncrementalDecoder()
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


class MyLatexIncrementalLexer(LatexIncrementalLexer):
    """A mock decoder to test the lexer."""
    def decode(self, input_: bytes, final: bool = False) -> str:
        return ''  # pragma: no cover


class LatexIncrementalLexerTest(TestCase):

    errors = 'strict'

    def setUp(self):
        self.lexer = MyLatexIncrementalLexer(errors=self.errors)

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

    def encode(self, chars: str, latex_bytes: bytes, final=False):
        result = self.encoder.encode(chars, final=final)
        self.assertEqual(result, latex_bytes)

    def tearDown(self):
        del self.encoder

    def test_invalid_type(self):
        with pytest.raises(TypeError):
            self.encoder.encode(object(), final=True)  # type: ignore

    def test_invalid_code(self):
        with pytest.raises(ValueError):
            # default encoding is ascii, \u00ff is not ascii translatable
            self.encoder.encode(u"\u00ff", final=True)

    def test_hello(self):
        self.encode(u'hello', b'hello', final=True)

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

    def encode(self, chars: str, latex_bytes: bytes, final: bool = False):
        result = self.encoder.uencode(chars, final=final)
        self.assertEqual(result, latex_bytes.decode('ascii'))

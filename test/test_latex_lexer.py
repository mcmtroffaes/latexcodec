# -*- coding: utf-8 -*-

"""Tests for the tex lexer."""

import nose.tools
from unittest import TestCase

from latexcodec.lexer import (
    LatexLexer, UnicodeLatexLexer,
    LatexIncrementalLexer,
    LatexIncrementalDecoder, UnicodeLatexIncrementalDecoder,
    LatexIncrementalEncoder, UnicodeLatexIncrementalEncoder,
    Token)


class MockLexer(LatexLexer):
    tokens = (
        (u'chars', br'mock'),
        (u'unknown', br'.'),
        )


class MockIncrementalDecoder(LatexIncrementalDecoder):
    tokens = (
        (u'chars', br'mock'),
        (u'unknown', br'.'),
        )


def test_token_create_with_args():
    t = Token('hello', b'world')
    nose.tools.assert_equal(t.name, 'hello')
    nose.tools.assert_equal(t.text, b'world')


@nose.tools.raises(AttributeError)
def test_token_assign_name():
    t = Token('hello', b'world')
    t.name = 'test'


@nose.tools.raises(AttributeError)
def test_token_assign_text():
    t = Token('hello', b'world')
    t.text = 'test'


@nose.tools.raises(AttributeError)
def test_token_assign_other():
    t = Token('hello', b'world')
    t.blabla = 'test'


class BaseLatexLexerTest(TestCase):

    errors = 'strict'
    Lexer = None

    def setUp(self):
        self.lexer = self.Lexer(errors=self.errors)

    def lex_it(self, latex_code, latex_tokens, final=False):
        if not self.lexer.binary_mode:
            latex_code = latex_code.decode("ascii")
            latex_tokens = [token.decode("ascii") for token in latex_tokens]
        tokens = self.lexer.get_raw_tokens(latex_code, final=final)
        self.assertEqual(
            list(token.text for token in tokens),
            latex_tokens)

    def tearDown(self):
        del self.lexer


class LatexLexerTest(BaseLatexLexerTest):

    Lexer = LatexLexer

    def test_null(self):
        self.lex_it(b'', [], final=True)

    def test_hello(self):
        self.lex_it(
            b'hello!  [#1] This \\is\\   \\^ a \ntest.\n'
            b'    \nHey.\n\n\# x \#x',
            br'h|e|l|l|o|!| | |[|#1|]| |T|h|i|s| |\is|\ | | |\^| |a| '
            b'|\n|t|e|s|t|.|\n| | | | |\n|H|e|y|.|\n|\n'
            br'|\#| |x| |\#|x'.split(b'|'),
            final=True
        )

    def test_comment(self):
        self.lex_it(
            b'test% some comment\ntest',
            b't|e|s|t|% some comment|\n|t|e|s|t'.split(b'|'),
            final=True
        )

    def test_comment_newline(self):
        self.lex_it(
            b'test% some comment\n\ntest',
            b't|e|s|t|% some comment|\n|\n|t|e|s|t'.split(b'|'),
            final=True
        )

    def test_control(self):
        self.lex_it(
            b'\\hello\\world',
            b'\\hello|\\world'.split(b'|'),
            final=True
        )

    def test_control_whitespace(self):
        self.lex_it(
            b'\\hello   \\world   ',
            b'\\hello| | | |\\world| | | '.split(b'|'),
            final=True
        )

    def test_controlx(self):
        self.lex_it(
            b'\\#\\&',
            b'\\#|\\&'.split(b'|'),
            final=True
        )

    def test_controlx_whitespace(self):
        self.lex_it(
            b'\\#    \\&   ',
            b'\\#| | | | |\\&| | | '.split(b'|'),
            final=True
        )

    def test_buffer(self):
        self.lex_it(
            b'hi\\t',
            b'h|i'.split(b'|'),
        )
        self.lex_it(
            b'here',
            [b'\\there'],
            final=True,
        )

    def test_state(self):
        self.lex_it(
            b'hi\\t',
            b'h|i'.split(b'|'),
        )
        state = self.lexer.getstate()
        self.lexer.reset()
        self.lex_it(
            b'here',
            b'h|e|r|e'.split(b'|'),
            final=True,
        )
        self.lexer.setstate(state)
        self.lex_it(
            b'here',
            [b'\\there'],
            final=True,
        )

    @nose.tools.raises(NotImplementedError)
    def test_decode(self):
            self.lexer.decode(b'')

    def test_final_backslash(self):
        self.lex_it(
            b'notsogood\\',
            b'n|o|t|s|o|g|o|o|d|\\'.split(b'|'),
            final=True
        )

    def test_final_comment(self):
        self.lex_it(
            b'hello%',
            b'h|e|l|l|o|%'.split(b'|'),
            final=True
        )

    def test_hash(self):
        self.lex_it(b'#', [b'#'], final=True)

    def test_tab(self):
        self.lex_it(b'\c\tc', b'\c|\t|c'.split(b'|'), final=True)

    def test_percent(self):
        self.lex_it(b'This is a \\% test.',
                    b'T|h|i|s| |i|s| |a| |\\%| |t|e|s|t|.'.split(b'|'),
                    final=True)
        self.lex_it(b'\\% %test',
                    b'\\%| |%test'.split(b'|'), final=True)
        self.lex_it(b'\\% %test\nhi',
                    b'\\%| |%test|\n|h|i'.split(b'|'), final=True)


class UnicodeLatexLexerTest(LatexLexerTest):
    Lexer = UnicodeLatexLexer


class BaseLatexIncrementalDecoderTest(TestCase):

    """Tex lexer fixture."""

    errors = 'strict'
    IncrementalDecoder = None

    def setUp(self):
        self.lexer = self.IncrementalDecoder(self.errors)

    def fix(self, s):
        return s if self.lexer.binary_mode else s.decode("ascii")

    def lex_it(self, latex_code, latex_tokens, final=False):
        latex_code = self.fix(latex_code)
        latex_tokens = [self.fix(token) for token in latex_tokens]
        tokens = self.lexer.get_tokens(latex_code, final=final)
        self.assertEqual(
            list(token.text for token in tokens),
            latex_tokens)

    def tearDown(self):
        del self.lexer


class LatexIncrementalDecoderTest(BaseLatexIncrementalDecoderTest):

    IncrementalDecoder = LatexIncrementalDecoder

    def test_null(self):
        self.lex_it(b'', [], final=True)

    def test_hello(self):
        self.lex_it(
            b'hello!  [#1] This \\is\\   \\^ a \ntest.\n'
            b'    \nHey.\n\n\# x \#x',
            br'h|e|l|l|o|!| |[|#1|]| |T|h|i|s| |\is|\ |\^|a| '
            br'|t|e|s|t|.| |\par|H|e|y|.| '
            br'|\par|\#| |x| |\#|x'.split(b'|'),
            final=True
        )

    def test_comment(self):
        self.lex_it(
            b'test% some comment\ntest',
            b't|e|s|t|t|e|s|t'.split(b'|'),
            final=True
        )

    def test_comment_newline(self):
        self.lex_it(
            b'test% some comment\n\ntest',
            b't|e|s|t|\\par|t|e|s|t'.split(b'|'),
            final=True
        )

    def test_control(self):
        self.lex_it(
            b'\\hello\\world',
            b'\\hello|\\world'.split(b'|'),
            final=True
        )

    def test_control_whitespace(self):
        self.lex_it(
            b'\\hello   \\world   ',
            b'\\hello|\\world'.split(b'|'),
            final=True
        )

    def test_controlx(self):
        self.lex_it(
            b'\\#\\&',
            b'\\#|\\&'.split(b'|'),
            final=True
        )

    def test_controlx_whitespace(self):
        self.lex_it(
            b'\\#    \\&   ',
            b'\\#| |\\&| '.split(b'|'),
            final=True
        )

    def test_buffer(self):
        self.lex_it(
            b'hi\\t',
            b'h|i'.split(b'|'),
        )
        self.lex_it(
            b'here',
            [b'\\there'],
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
            self.lexer.decode(self.fix(b'    \nHey.\n\n\# x \#x'), final=True),
            u' \\par Hey. \\par \\# x \\#x',
        )

    def test_state_middle(self):
        self.lex_it(
            b'hi\\t',
            b'h|i'.split(b'|'),
        )
        state = self.lexer.getstate()
        self.assertEqual(self.lexer.state, 'M')
        self.assertEqual(self.lexer.raw_buffer.name, 'control_word')
        self.assertEqual(self.lexer.raw_buffer.text, self.fix(b'\\t'))
        self.lexer.reset()
        self.assertEqual(self.lexer.state, 'N')
        self.assertEqual(self.lexer.raw_buffer.name, 'unknown')
        self.assertEqual(self.lexer.raw_buffer.text, self.fix(b''))
        self.lex_it(
            b'here',
            b'h|e|r|e'.split(b'|'),
            final=True,
        )
        self.lexer.setstate(state)
        self.assertEqual(self.lexer.state, 'M')
        self.assertEqual(self.lexer.raw_buffer.name, 'control_word')
        self.assertEqual(self.lexer.raw_buffer.text, self.fix(b'\\t'))
        self.lex_it(
            b'here',
            [b'\\there'],
            final=True,
        )

    def test_state_inline_math(self):
        self.lex_it(
            b'hi$t',
            b'h|i|$'.split(b'|'),
        )
        assert self.lexer.inline_math
        self.lex_it(
            b'here$',
            b't|h|e|r|e|$'.split(b'|'),
            final=True,
        )
        assert not self.lexer.inline_math

    # counterintuitive?
    @nose.tools.raises(UnicodeDecodeError)
    def test_final_backslash(self):
        self.lex_it(
            b'notsogood\\',
            [b'notsogood'],
            final=True
        )

    def test_final_comment(self):
        self.lex_it(
            b'hello%',
            b'h|e|l|l|o'.split(b'|'),
            final=True
        )

    def test_hash(self):
        self.lex_it(b'#', [b'#'], final=True)

    def test_tab(self):
        self.lex_it(b'\c\tc', b'\c|c'.split(b'|'), final=True)


class UnicodeLatexIncrementalDecoderTest(LatexIncrementalDecoderTest):
    IncrementalDecoder = UnicodeLatexIncrementalDecoder


class LatexIncrementalDecoderReplaceTest(BaseLatexIncrementalDecoderTest):

    errors = 'replace'
    IncrementalDecoder = MockIncrementalDecoder

    def test_errors_replace(self):
        self.lex_it(
            b'helmocklo',
            b'?|?|?|mock|?|?'.split(b'|'),
            final=True
        )


class LatexIncrementalDecoderIgnoreTest(BaseLatexIncrementalDecoderTest):

    errors = 'ignore'
    IncrementalDecoder = MockIncrementalDecoder

    def test_errors_ignore(self):
        self.lex_it(
            b'helmocklo',
            b'mock'.split(b'|'),
            final=True
        )


class LatexIncrementalDecoderInvalidErrorTest(BaseLatexIncrementalDecoderTest):

    errors = '**baderror**'
    IncrementalDecoder = MockIncrementalDecoder

    @nose.tools.raises(NotImplementedError)
    def test_errors_invalid(self):
        self.lex_it(
            b'helmocklo',
            b'?|?|?|mock|?|?'.split(b'|'),
            final=True
        )


def invalid_token_test():
    lexer = LatexIncrementalDecoder()
    # piggyback an implementation which results in invalid tokens
    lexer.get_raw_tokens = lambda bytes_, final: [Token('**invalid**', bytes_)]
    nose.tools.assert_raises(AssertionError, lambda: lexer.decode(b'hello'))


def invalid_state_test_1():
    lexer = LatexIncrementalDecoder()
    # piggyback invalid state
    lexer.state = '**invalid**'
    nose.tools.assert_raises(AssertionError, lambda: lexer.decode(b'\n\n\n'))


def invalid_state_test_2():
    lexer = LatexIncrementalDecoder()
    # piggyback invalid state
    lexer.state = '**invalid**'
    nose.tools.assert_raises(AssertionError, lambda: lexer.decode(b'   '))


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
            b"hello\nworld", b"h|e|l|l|o| |w|o|r|l|d".split(b'|'),
            final=True)

    def test_par(self):
        self.lex_it(
            b"hello\n\nworld", b"h|e|l|l|o| |\\par|w|o|r|l|d".split(b'|'),
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

    @nose.tools.raises(TypeError)
    def test_invalid_type(self):
        self.encoder.encode(object(), final=True)

    @nose.tools.raises(ValueError)
    def test_invalid_code(self):
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

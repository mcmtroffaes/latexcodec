# -*- coding: utf-8 -*-

"""Tests for the new tex lexer."""

from latexcodec._new_lexer import (
    latex_groups, make_pattern, make_lexer, make_incremental_lexer,
    is_lexer_binary, get_lexer_empty_text)
import nose.tools
from unittest import TestCase


def test_lexer_binary():
    groups = ((b'one', b'hello'), (b'two', b'world'), (b'three', b' '))
    lexer = make_lexer(make_pattern(groups))
    nose.tools.assert_equal(
        list(token.text for token in lexer(b'hello world')),
        [b'hello', b' ', b'world'])
    nose.tools.assert_true(is_lexer_binary(lexer))
    nose.tools.assert_equal(get_lexer_empty_text(lexer), b'')


def test_lexer_unicode():
    groups = ((u'one', u'нɛℓℓσ'), (u'two', u'ωσяℓ∂'), (u'three', u' '))
    lexer = make_lexer(make_pattern(groups))
    nose.tools.assert_equal(
        list(token.text for token in lexer(u'нɛℓℓσ ωσяℓ∂')),
        [u'нɛℓℓσ', u' ', u'ωσяℓ∂'])
    nose.tools.assert_false(is_lexer_binary(lexer))
    nose.tools.assert_equal(get_lexer_empty_text(lexer), u'')


def test_incremental_lexer_binary():
    groups = ((b'one', b'hello'), (b'two', b'world'), (b'three', b' '),
              (b'unknown', b'.+'))
    ilexer = make_incremental_lexer(make_lexer(make_pattern(groups)))
    ilexer.send(None)

    def send(text):
        return list(token.text for token in ilexer.send(text))

    nose.tools.assert_equal(send(b'he'), [])
    nose.tools.assert_equal(send(b'llo w'), [b'hello', b' '])
    nose.tools.assert_equal(send(b'orld'), [])
    nose.tools.assert_equal(send(None), [b'world'])
    nose.tools.assert_equal(send(b'hello world'), [b'hello', b' '])
    nose.tools.assert_equal(send(None), [b'world'])


def test_incremental_lexer_unicode():
    groups = ((u'one', u'հελλɸ'), (u'two', u'ѡɸʀλδ'), (u'three', u' '),
              (u'unknown', u'.+'))
    ilexer = make_incremental_lexer(make_lexer(make_pattern(groups)))
    ilexer.send(None)

    def send(text):
        return [token.text for token in ilexer.send(text)]

    nose.tools.assert_equal(send(u'հε'), [])
    nose.tools.assert_equal(send(u'λλɸ ѡ'), [u'հελλɸ', u' '])
    nose.tools.assert_equal(send(u'ɸʀλδ'), [])
    nose.tools.assert_equal(send(None), [u'ѡɸʀλδ'])
    nose.tools.assert_equal(send(u'հελλɸ ѡɸʀλδ'), [u'հελλɸ', u' '])
    nose.tools.assert_equal(send(None), [u'ѡɸʀλδ'])


class BaseLatexLexerTest(TestCase):

    def setUp(self):
        self.lexer = make_lexer(make_pattern(latex_groups(self.is_binary)))

    def lex_it(self, latex_code, latex_tokens):
        if not self.is_binary:
            latex_code = latex_code.decode("ascii")
            latex_tokens = [token.decode("ascii") for token in latex_tokens]
        tokens = self.lexer(latex_code)
        self.assertEqual(
            list(token.text for token in tokens),
            latex_tokens)

    def tearDown(self):
        del self.lexer


class LatexLexerBinaryTest(BaseLatexLexerTest):

    is_binary = True

    def test_null(self):
        self.lex_it(b'', [])

    def test_hello(self):
        self.lex_it(
            b'hello!  [#1] This \\is\\   \\^ a \ntest.\n'
            b'    \nHey.\n\n\# x \#x',
            br'h|e|l|l|o|!| | |[|#1|]| |T|h|i|s| |\is|\ | | |\^| |a| '
            b'|\n|t|e|s|t|.|\n| | | | |\n|H|e|y|.|\n|\n'
            br'|\#| |x| |\#|x'.split(b'|')
        )

    def test_comment(self):
        self.lex_it(
            b'test% some comment\ntest',
            b't|e|s|t|% some comment\n|t|e|s|t'.split(b'|')
        )

    def test_comment_newline(self):
        self.lex_it(
            b'test% some comment\n\ntest',
            b't|e|s|t|% some comment\n|\n|t|e|s|t'.split(b'|')
        )

    def test_control(self):
        self.lex_it(
            b'\\hello\\world',
            b'\\hello|\\world'.split(b'|')
        )

    def test_control_whitespace(self):
        self.lex_it(
            b'\\hello   \\world   ',
            b'\\hello| | | |\\world| | | '.split(b'|')
        )

    def test_controlx(self):
        self.lex_it(
            b'\\#\\&',
            b'\\#|\\&'.split(b'|')
        )

    def test_controlx_whitespace(self):
        self.lex_it(
            b'\\#    \\&   ',
            b'\\#| | | | |\\&| | | '.split(b'|')
        )

    def test_final_backslash(self):
        self.lex_it(
            b'notsogood\\',
            b'n|o|t|s|o|g|o|o|d|\\'.split(b'|')
        )

    def test_final_comment(self):
        self.lex_it(
            b'hello%',
            b'h|e|l|l|o|%'.split(b'|')
        )

    def test_hash(self):
        self.lex_it(b'#', [b'#'])


class LatexLexerUnicodeTest(LatexLexerBinaryTest):
    is_binary = False

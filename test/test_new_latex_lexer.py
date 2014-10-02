# -*- coding: utf-8 -*-

"""Tests for the new latex lexer."""

from latexcodec._new_lexer import (
    make_pattern, make_lexer, make_incremental_lexer)
from latexcodec._new_latex_lexer import latex_groups
import nose.tools
from unittest import TestCase


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

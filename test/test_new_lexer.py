# -*- coding: utf-8 -*-

"""Tests for the new lexer."""

from latexcodec._new_lexer import (
    Token, make_pattern, make_lexer, make_incremental_lexer)
import nose.tools


def test_lexer_binary():
    groups = ((b'one', b'hello'), (b'two', b'world'), (b'three', b' '))
    lexer = make_lexer(make_pattern(groups))
    nose.tools.assert_equal(
        list(token for token in lexer(b'hello world')),
        [Token(1, b'hello'), Token(3, b' '), Token(2, b'world')])


def test_lexer_unicode():
    groups = ((u'one', u'нɛℓℓσ'), (u'two', u'ωσяℓ∂'), (u'three', u' '))
    lexer = make_lexer(make_pattern(groups))
    nose.tools.assert_equal(
        list(token.text for token in lexer(u'нɛℓℓσ ωσяℓ∂')),
        [u'нɛℓℓσ', u' ', u'ωσяℓ∂'])


def test_incremental_lexer_binary():
    groups = ((b'one', b'hello'), (b'two', b'world'), (b'three', b' '),
              (b'unknown', b'.+'))
    lexer = make_lexer(make_pattern(groups))
    func = lambda tokens: list(token.text for token in tokens)
    ilexer = make_incremental_lexer(lexer, func)

    def test(state, text, expected_tokens):
        tokens, state = ilexer(state, text)
        nose.tools.assert_equal(tokens, expected_tokens)
        return state

    state = test(None, b'he', [])
    state = test(state, b'llo w', [b'hello', b' '])
    state = test(state, 'orld', [])
    state = test(state, None, [b'world'])
    state = test(None, b'hello world', [b'hello', b' '])
    state = test(state, None, [b'world'])
    state = test(None, b'', [])
    state = test(state, None, [])


def test_incremental_lexer_unicode():
    groups = ((u'one', u'հελλɸ'), (u'two', u'ѡɸʀλδ'), (u'three', u' '),
              (u'unknown', u'.+'))
    lexer = make_lexer(make_pattern(groups))
    func = lambda tokens: list(token.text for token in tokens)
    ilexer = make_incremental_lexer(lexer, func)

    def test(state, text, expected_tokens):
        tokens, state = ilexer(state, text)
        nose.tools.assert_equal(tokens, expected_tokens)
        return state

    state = test(None, u'հε', [])
    state = test(state, u'λλɸ ѡ', [u'հελλɸ', u' '])
    state = test(state, u'ɸʀλδ', [])
    state = test(state, None, [u'ѡɸʀλδ'])
    state = test(None, u'հελλɸ ѡɸʀλδ', [u'հελλɸ', u' '])
    state = test(state, None, [u'ѡɸʀλδ'])
    state = test(None, u'', [])
    state = test(state, None, [])


def test_incremental_lexer_bad_func():
    groups = ((u'char', u'.'),)
    lexer = make_lexer(make_pattern(groups))
    func = lambda tokens: tokens
    ilexer = make_incremental_lexer(lexer, func)
    nose.tools.assert_raises(ValueError, lambda: ilexer(None, u'hello'))

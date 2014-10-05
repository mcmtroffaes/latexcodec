# -*- coding: utf-8 -*-

"""Tests for the new lexer."""

from latexcodec._new_lexer import (
    make_pattern, make_lexer, make_incremental_lexer, get_state, set_state)
import nose.tools
from unittest import TestCase


def test_lexer_binary():
    groups = ((b'one', b'hello'), (b'two', b'world'), (b'three', b' '))
    lexer = make_lexer(make_pattern(groups))
    nose.tools.assert_equal(
        list(token.text for token in lexer(b'hello world')),
        [b'hello', b' ', b'world'])


def test_lexer_unicode():
    groups = ((u'one', u'нɛℓℓσ'), (u'two', u'ωσяℓ∂'), (u'three', u' '))
    lexer = make_lexer(make_pattern(groups))
    nose.tools.assert_equal(
        list(token.text for token in lexer(u'нɛℓℓσ ωσяℓ∂')),
        [u'нɛℓℓσ', u' ', u'ωσяℓ∂'])


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

def test_incremental_lexer_state():
    groups = ((b'one', b'hello'), (b'two', b'world'), (b'three', b' '),
              (b'unknown', b'.+'))
    ilexer = make_incremental_lexer(make_lexer(make_pattern(groups)))
    ilexer.send(None)

    def send(text):
        return list(token.text for token in ilexer.send(text))

    nose.tools.assert_is_none(get_state(ilexer))
    nose.tools.assert_equal(send(b'he'), [])
    nose.tools.assert_equal(send(b'llo w'), [b'hello', b' '])
    state = get_state(ilexer)
    nose.tools.assert_equal(state, b'w')
    nose.tools.assert_equal(send(b'orld'), [])
    nose.tools.assert_equal(send(None), [b'world'])
    set_state(ilexer, state)
    nose.tools.assert_equal(send(b'orld'), [])
    nose.tools.assert_equal(send(None), [b'world'])

# -*- coding: utf-8 -*-
"""Lexer based on a compiled regular expression."""

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

import collections
import re
import six


Token = collections.namedtuple("Token", "name text")


def latex_groups(binary=True):
    """List of token names, and the regular expressions they match."""
    binary_groups = (
        # comment: for ease, and for speed, we handle it as a token
        (b'comment', br'%.*?\n'),
        # control tokens
        # in latex, some control tokens skip following whitespace
        # ('control-word' and 'control-symbol')
        # others do not ('control-symbol-x')
        # XXX TBT says no control symbols skip whitespace (except '\ ')
        # XXX but tests reveal otherwise?
        (b'control_word', br'[\\][a-zA-Z]+'),
        (b'control_symbol', br'[\\][~' br"'" br'"` =^!]'),
        # TODO should only match ascii
        (b'control_symbol_x', br'[\\][^a-zA-Z]'),
        # parameter tokens
        # also support a lone hash so we can lex things like b'#a'
        (b'parameter', br'\#[0-9]|\#'),
        # any remaining characters; for ease we also handle space and
        # newline as tokens
        (b'space', br' '),
        (b'newline', br'\n'),
        (b'mathshift', br'[$][$]|[$]'),
        # note: some chars joined together to make it easier to detect
        # symbols that have a special function (i.e. --, ---, etc.)
        (b'chars',
         br'---|--|-|[`][`]'
         br"|['][']"
         br'|[?][`]|[!][`]'
         # separate chars because brackets are optional
         # e.g. fran\\c cais = fran\\c{c}ais in latex
         # so only way to detect \\c acting on c only is this way
         br'|[0-9a-zA-Z{}]'
         # we have to join everything else together to support
         # multibyte encodings: every token must be decodable!!
         # this means for instance that \\c öké is NOT equivalent to
         # \\c{ö}ké
         br'|[^ %#$\n\\]+'),
        # trailing garbage which we cannot decode otherwise
        # (such as a lone '\' at the end of a buffer)
        # is never emitted, but used internally by the buffer
        (b'unknown', br'.'),
    )
    if binary:
        return binary_groups
    else:
        return tuple(tuple(item.decode("ascii") for item in row)
                     for row in binary_groups)


def make_pattern(groups):
    is_binary = isinstance(groups[0][0], six.binary_type)
    if is_binary:
        pattern = b"|".join(b"(?P<" + name + b">" + regexp + b")"
                            for name, regexp in groups)
    else:
        pattern = u"|".join(u"(?P<" + name + u">" + regexp + u")"
                            for name, regexp in groups)
    return re.compile(pattern, re.DOTALL)


def make_lexer(pattern):
    def lexer(text):
        for match in pattern.finditer(text):
            yield Token(match.lastgroup, match.group(0))
    return lexer


def make_incremental_lexer(lexer):
    """A generator which acts as an incremental lexer by keeping the
    last matched token in a buffer.
    """
    def incremental_lexer():
        tokens = []
        buf = None
        while True:
            msg = yield tokens
            if msg is not None:
                tokens = list(lexer(buf.text + msg) if buf else lexer(msg))
                buf = tokens.pop() if tokens else None
            else:
                tokens = list(lexer(buf.text)) if buf else []
                buf = None
    return incremental_lexer()


def get_state(incremental_lexer):
    tokens = incremental_lexer.send(None)
    if tokens:
        assert len(tokens) == 1
        state = tokens[0].text
        incremental_lexer.send(state)
        return state
    else:
        return None


def set_state(incremental_lexer, state):
    incremental_lexer.send(None)
    incremental_lexer.send(state)

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
            yield Token(match.lastindex, match.group(0))
    return lexer


def make_incremental_lexer(lexer):
    """A generator which acts as an incremental lexer by keeping the
    last matched token in a buffer.
    """
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

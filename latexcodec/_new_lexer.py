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


Token = collections.namedtuple("Token", "group text")


def make_pattern(groups):
    """Compile a regular expression pattern from the given groups."""
    is_binary = isinstance(groups[0][0], six.binary_type)
    if is_binary:
        pattern = b"|".join(b"(?P<" + name + b">" + regexp + b")"
                            for name, regexp in groups)
    else:
        pattern = u"|".join(u"(?P<" + name + u">" + regexp + u")"
                            for name, regexp in groups)
    return re.compile(pattern, re.DOTALL)


def make_lexer(pattern):
    """Create a lexer function from a given compiled regular expression
    pattern.
    """
    def lexer(text):
        for match in pattern.finditer(text):
            yield Token(match.lastindex, match.group(0))
    return lexer


def _is_consumed(iterable):
    try:
        six.next(iterable)
    except StopIteration:
        return True
    else:
        return False


def make_incremental_lexer(lexer, func):
    """A generator which acts as an incremental lexer by keeping the last
    matched token in a buffer. For this to work, the lexer must be
    able to match incomplete tokens at the end of the input.
    """
    def ilexer(state, text):
        def init(tokens):
            # "nonlocal state" emulation through init.state
            # see http://stackoverflow.com/a/16032631/2863746
            try:
                previous_token = six.next(tokens)
                init.state = previous_token.text
            except StopIteration:
                return
            else:
                for token in tokens:
                    yield previous_token
                    init.state = token.text
                    previous_token = token

        if text is not None:
            init.state = state
            init_tokens = init(lexer((state + text) if state else text))
        else:
            init.state = None
            init_tokens = lexer(state) if state else ()
        result = func(init_tokens)
        assert _is_consumed(init_tokens)
        return result, init.state
    return ilexer

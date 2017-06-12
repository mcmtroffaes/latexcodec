Install the module with ``pip install latexcodec``, or from
source using ``python setup.py install``.

Minimal Example
---------------

Simply import the :mod:`latexcodec` module to enable ``"latex"``
to be used as an encoding:

.. code-block:: python

    import latexcodec
    text_latex = b"\\'el\\`eve"
    assert text_latex.decode("latex") == u"élève"
    text_unicode = u"ångström"
    assert text_unicode.encode("latex") == b'\\aa ngstr\\"om'

There are also a ``ulatex`` encoding for text transforms.
The simplest way to use this codec goes through the codecs module
(as for all text transform codecs on Python):

.. code-block:: python

    import codecs
    import latexcodec
    text_latex = u"\\'el\\`eve"
    assert codecs.decode(text_latex, "ulatex") == u"élève"
    text_unicode = u"ångström"
    assert codecs.encode(text_unicode, "ulatex") == u'\\aa ngstr\\"om'

By default, the LaTeX input is assumed to be ascii, as per standard LaTeX.
However, you can also specify an extra codec
as ``latex+<encoding>`` or ``ulatex+<encoding>``,
where ``<encoding>`` describes another encoding.
In this case characters will be
translated to and from that encoding whenever possible.
The following code snippet demonstrates this behaviour:

.. code-block:: python

    import latexcodec
    text_latex = b"\xfe"
    assert text_latex.decode("latex+latin1") == u"þ"
    assert text_latex.decode("latex+latin2") == u"ţ"
    text_unicode = u"ţ"
    assert text_unicode.encode("latex+latin1") == b'\\c t'  # ţ is not latin1
    assert text_unicode.encode("latex+latin2") == b'\xfe'   # but it is latin2

When encoding using the ``ulatex`` codec, you have the option to pass
through characters that cannot be encoded in the desired encoding, by
using the ``'keep'`` error. This can be a useful fallback option if
you want to encode as much as possible, whilst still retaining as much
as possible of the original code when encoding fails. If instead you
want to translate to LaTeX but keep as much of the unicode as
possible, use the ``ulatex+utf8`` codec, which should never fail.

.. code-block:: python

    import codecs
    import latexcodec
    text_unicode = u'⌨'  # \u2328 = keyboard symbol, currently not translated
    try:
        # raises a value error as \u2328 cannot be encoded into latex
        codecs.encode(text_unicode, "ulatex+ascii")
    except ValueError:
        pass
    assert codecs.encode(text_unicode, "ulatex+ascii", "keep") == u'⌨'
    assert codecs.encode(text_unicode, "ulatex+utf8") == u'⌨'

Limitations
-----------

* Not all unicode characters are registered. If you find any missing,
  please report them on the tracker:
  https://github.com/mcmtroffaes/latexcodec/issues

* Unicode combining characters are currently not handled.

* By design, the codec never removes curly brackets. This is because
  it is very hard to guess whether brackets are part of a command or
  not (this would require a full latex parser). Moreover, bibtex uses
  curly brackets as a guard against case conversion, in which case
  automatic removal of curly brackets may not be desired at all, even
  if they are not part of a command. Also see:
  http://stackoverflow.com/a/19754245/2863746

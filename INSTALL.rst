Install the module with ``pip install latexcodec``, or from
source using ``python setup.py install``.

Minimal Example
---------------

Simply import the :mod:`latexcodec` module to enable ``"latex"``
to be used as an encoding:

.. code-block:: python

    import latexcodec
    text_latex = br"\'el\`eve"
    assert text_latex.decode("latex") == u"élève"
    text_unicode = u"ångström"
    assert text_unicode.encode("latex") == br'\aa ngstr\"om'

By default, the LaTeX input is assumed to be ascii, as per standard LaTeX.
However, you can also specify an extra codec
as ``latex+<encoding>``, where ``<encoding>`` describes another encoding.
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

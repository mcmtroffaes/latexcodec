def test_install_example_1():
    import latexcodec  # noqa

    text_latex = b"\\'el\\`eve"
    assert text_latex.decode("latex") == "élève"
    text_unicode = "ångström"
    assert text_unicode.encode("latex") == b'\\aa ngstr\\"om'


def test_install_example_2():
    import codecs

    import latexcodec  # noqa

    text_latex = "\\'el\\`eve"
    assert codecs.decode(text_latex, "ulatex") == "élève"  # type: ignore
    text_unicode = "ångström"
    assert codecs.encode(text_unicode, "ulatex") == '\\aa ngstr\\"om'


def test_install_example_3():
    import latexcodec  # noqa

    text_latex = b"\xfe"
    assert text_latex.decode("latex+latin1") == "þ"
    assert text_latex.decode("latex+latin2") == "ţ"
    text_unicode = "ţ"
    assert text_unicode.encode("latex+latin1") == b"\\c t"  # ţ is not latin1
    assert text_unicode.encode("latex+latin2") == b"\xfe"  # but it is latin2


def test_install_example_4():
    import codecs

    import latexcodec  # noqa

    text_unicode = "⌨"  # \u2328 = keyboard symbol, currently not translated
    try:
        # raises a value error as \u2328 cannot be encoded into latex
        codecs.encode(text_unicode, "ulatex+ascii")
    except ValueError:
        pass
    assert codecs.encode(text_unicode, "ulatex+ascii", "keep") == "⌨"
    assert codecs.encode(text_unicode, "ulatex+utf8") == "⌨"

Install the module with ``pip install latexcodec``, or from
source using ``python setup.py install``.

Minimal Example
---------------

.. code-block:: python

   import latexcodec.codec
   latexcodec.codec.register()
   text_latex = br"\'el\`eve"
   assert text_latex.decode("latex+utf8") == u"élève"
   text_unicode = u"ångström"
   assert text_unicode.encode("latex+utf8") == br'\aa ngstr\"om'

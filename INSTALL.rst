Install the module with ``pip install latexcodec``, or from
source using ``python setup.py install``.

Minimal Example
---------------

.. code-block:: python

   import latexcodec
   text_latex = br"\'el\`eve"
   assert text_latex.decode("latex") == u"élève"
   text_unicode = u"ångström"
   assert text_unicode.encode("latex") == br'\aa ngstr\"om'

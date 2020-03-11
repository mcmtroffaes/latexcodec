# -*- coding: utf-8 -*-
#
# latexcodec documentation build configuration file, created by
# sphinx-quickstart on Wed Aug  3 15:45:22 2011.

from setuptools_scm import get_version
from pathlib import Path

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.imgmath',
    'sphinx.ext.viewcode']
source_suffix = '.rst'
master_doc = 'index'
project = u'latexcodec'
copyright = u'2011-2014, Matthias C. M. Troffaes'
version = get_version(Path(__file__).absolute().parent.parent)
exclude_patterns = ['_build']
pygments_style = 'sphinx'
html_theme = 'default'
htmlhelp_basename = 'latexcodecdoc'
latex_documents = [
    ('index', 'latexcodec.tex',
     u'latexcodec Documentation',
     u'Matthias C. M. Troffaes', 'manual'),
]
man_pages = [
    ('index', 'latexcodec', u'latexcodec Documentation',
     [u'Matthias C. M. Troffaes'], 1)
]
texinfo_documents = [
    ('index', 'latexcodec', u'latexcodec Documentation',
     u'Matthias C. M. Troffaes',
     'latexcodec', 'One line description of project.', 'Miscellaneous'),
]
intersphinx_mapping = {
    'python': ('http://docs.python.org/', None),
}

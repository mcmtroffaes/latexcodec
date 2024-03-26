# -*- coding: utf-8 -*-
#
# latexcodec documentation build configuration file, created by
# sphinx-quickstart on Wed Aug  3 15:45:22 2011.

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.imgmath",
    "sphinx.ext.viewcode",
]
source_suffix = ".rst"
master_doc = "index"
project = "latexcodec"
copyright = "2011-2024, Matthias C. M. Troffaes"
with open("../VERSION") as version_file:
    release = version_file.read().strip()
version = ".".join(release.split(".")[:2])
exclude_patterns = ["_build"]
pygments_style = "sphinx"
html_theme = "default"
htmlhelp_basename = "latexcodecdoc"
latex_documents = [
    (
        "index",
        "latexcodec.tex",
        "latexcodec Documentation",
        "Matthias C. M. Troffaes",
        "manual",
    ),
]
man_pages = [
    ("index", "latexcodec", "latexcodec Documentation", ["Matthias C. M. Troffaes"], 1)
]
texinfo_documents = [
    (
        "index",
        "latexcodec",
        "latexcodec Documentation",
        "Matthias C. M. Troffaes",
        "latexcodec",
        "One line description of project.",
        "Miscellaneous",
    ),
]
intersphinx_mapping = {
    "python": ("http://docs.python.org/", None),
}

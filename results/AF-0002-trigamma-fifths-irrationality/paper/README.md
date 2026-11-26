# Manuscript

Build from this directory (TeX Live 2023 or later; packages: amsart, lmodern,
microtype, hyperref, cleveref, mathtools, enumitem, booktabs):

```bash
latexmk -pdf main.tex
```

`latexmk -c` removes intermediate files. The committed `main.pdf` must be the output of
the committed sources.

Layout of the series: title page (title, author, abstract, MSC2020, keywords, date,
identifier, repository, short AI disclosure); table of contents on the next page; the
introduction on a fresh page; appendices; then the unnumbered sections
*Reproducibility and formal verification*, *Acknowledgements*, *AI-assisted research
disclosure*, and the references.

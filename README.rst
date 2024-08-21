======================================================
PackTex: Packaging LaTeX papers for journal and ArXiV
======================================================

These are my scripts for preparing an archive that can be uploaded to journals and/or ArXiV.

Features
--------

* collect files scattered across the file system into one folder
* condense all latex files into one file (required by some journals), remove potentially embarrassing latex comments
* condense bibtex bibliography to only used entries, remove comments and abstracts
* update bibtex bibliography entries with ADS

Install
-------

Some prerequisities for the optional steps:

    $ pip install bibmanager bibtexparser

And you need to download a copy of this repository. The instructions below
assume you stored it into /path/to/this/repo/.

Step 1: Self-contained directory
---------------------------------

To create a directory `package-mymanuscript.tex`, run::

    $ python3 /path/to/this/repo/packtex.py mymanuscript.tex

Run this from the directory where your tex file lives, so that relative and absolute paths make sense.

Different versions of your paper should have different tex file names.

In there, you can run pdflatex as usual::

    $ cd package-mymanuscript.tex
    $ pdflatex mymanuscript && bibtex mymanuscript && pdflatex mymanuscript && pdflatex mymanuscript

Step 2: Stripping bibtex (optional)
-----------------------------------

Next, we can optionally condense the bibtex bibliography to only used entries, removing comments and abstracts::

    $ python3 /path/to/this/repo/packbib.py mymanuscript.tex

This only makes changes inside `package-mymanuscript.tex`, combining the .bib files into one 
and including it instead in `mymanuscript.tex`.

Step 3: Upload-ready archive
--------------------

ADS presents images in its preview fetched from arxiv, so you can export all graphics to pngs, in a sensible order::

    $ j=0; for i in $(egrep 'File: .* Graphic file' mymanuscript.log|awk '{print $2}'); do ((j++)); convert -density 100 $i -background white -alpha remove -alpha off $(printf pngs/fig_%02d.png $j); done

Finally, you can create a tarball, excluding some log files (you may also want to exclude mymanuscript.pdf)::

    $ cd ..
    $ tar -czvf package-mymanuscript.tar.gz --exclude '*.log' --exclude '*.blg' --exclude '*.out' package-mymanuscript.tex/

Update bibtex to latest version
-------------------------------

Arxived papers get published, and the journals want us to use the latest publication information.

To update your bibtex library with ADS, we can take advantage of bibmanager as described at https://bibmanager.readthedocs.io/en/latest/):

First, reset bibm and make it forget everything.

    bibm reset
    bibm config ads_token $(cat ~/.ads/dev_key)

Next, we make a copy of the bibliography we want to update::

    cp /my/literature/directory/agn.bib /tmp/orig.bib

Optionally, if it is in ISO-8859-1, convert to UTF-8 first::

    iconv -f ISO-8859-1 -t UTF-8 </my/literature/directory/agn.bib > /tmp/orig.bib

Import into bibm. This forgets many fields, and the order of entries::

    bibm merge /tmp/orig.bib

Update from ADS, without changing the key names::

    bibm ads-update no

Export again to bibtex::

    bibm export /tmp/updated.bib

Merge only the important publication fields back into the original file, keeping all original fields and the original order::

    python3 /path/to/this/repo/bibupdatemerge.py /tmp/orig.bib /tmp/updated.bib /tmp/merged.bib

You can look at the changes made::

    diff -u /tmp/orig.bib /tmp/merged.bib

Finally, copy it back, overwriting the original file

    cp /tmp/merged.bib /my/literature/directory/agn.bib
    
    # or: 
    iconv -f ISO-8859-1 -t UTF-8 < /tmp/merged.bib > /my/literature/directory/agn.bib


#!/usr/bin/env python3
"""
Merges updated bibtex entries from another file.

See README for usage instructions.

Copyright (c) 2024, Johannes Buchner

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import sys
import bibtexparser

bib_orig = sys.argv[1]
bib_updated = sys.argv[2]
# read /tmp/new-utf8.bib and /tmp/agn.bib
library = {}
with open(bib_updated, encoding='ISO-8859-1') as fbib:
	for entry in bibtexparser.parse_string(fbib.read()).entries:
		if entry.key not in library:
			library[entry.key] = entry
del fbib

keys_to_copy = ['author', 'title', 'journal', 'keywords', 'year', 'month', 'volume', 'number', 'pages', 'eid', 'doi', 'url', 'adsurl']

with open(bib_orig, encoding='ISO-8859-1') as fbib:
	results = bibtexparser.parse_string(fbib.read())

for entry in results.entries:
	# updated entries
	if entry.key in library:
		for k in keys_to_copy:
			if k in library[entry.key] and not (k == 'author' and ' and et al.' in library[entry.key][k]):
				entry[k] = library[entry.key][k]

bibtex_format = bibtexparser.BibtexFormat()
bibtex_format.indent = '  '
bibtex_format.block_separator = '\n\n'
bibtexparser.write_file(sys.argv[3], results, bibtex_format=bibtex_format)


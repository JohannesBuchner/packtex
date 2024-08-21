"""
bibm reset
bibm config ads_token $(cat ~/.ads/dev_key)
cp /mnt/data/daten/PostDoc/literature/agn.bib /tmp/orig.bib
iconv -f ISO-8859-1 -t UTF-8 /tmp/orig.bib > /tmp/orig-utf8.bib
bibm merge /tmp/orig-utf8.bib
bibm export /tmp/reordered-utf8.bib
bibm ads-update no
bibm export /tmp/new-utf8.bib
python3 ~/Downloads/packtex/bibupdatemerge.py /tmp/orig-utf8.bib /tmp/new-utf8.bib /tmp/merged-utf8.bib
meld /tmp/orig-utf8.bib /tmp/merged-utf8.bib
iconv -f ISO-8859-1 -t UTF-8 /tmp/orig.bib > /tmp/orig-utf8.bib
### copy /tmp/merged-utf8.bib /mnt/data/daten/PostDoc/literature/ 
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

"""
# for each bib key, record changes
chunks = []
current_key = None
current_chunk = []
with open(bib_orig, encoding='ISO-8859-1') as fbib:
	for line in fbib:
		if line.startswith('@'):
			chunks.append((current_key, current_chunk))
			del current_key, current_chunk
			current_chunk = []
			current_key = line.split('{')[1].split(',')[0]
			print(current_key)
		current_chunk.append(line)
	chunks.append((current_key, current_chunk))
del fbib, current_key, current_chunk, line

for current_key, current_chunk in chunks:
	if current_key is not None and current_key in library:
		library_entry = library[current_key]
		newchunk = []
		# copy keys_to_copy, ignoring the original entry
		# but only the ones we have in the update
		# otherwise, keep as is
		keys_to_copy_here = [k for k in keys_to_copy if k in library_entry]
		for line in current_chunk:
			if ' = ' in line:
				key, oldvalue = line.strip().split(' = ', 1)
				if key in keys_to_copy_here and not (key == 'author' and ' and et al.' in library_entry[key]):
					continue
			newchunk.append(line)

		# inject the new entry before the last entry, so that we do not need to worry about the comma
		end_of_entries_position = newchunk.index("}\n")
		for key in keys_to_copy_here:
			newchunk.insert(end_of_entries_position - 1, "  %s = %s,\n" % (key, library_entry[key]))
		print("BEFORE:", current_key, "".join(current_chunk))
		print("NOW:", current_key, "".join(newchunk))
"""

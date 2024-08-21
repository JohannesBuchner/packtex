#!/usr/bin/env python3
"""
Package bibtex.

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
import re
import os
import subprocess

def countlines(filename, encoding='latin1'):
	with open(filename, 'r', encoding=encoding) as fin:
		return sum(1 for _ in fin)
	
filename = sys.argv[1]
filestem = filename.replace('.tex', '')
outdir = 'package-%s/' % filename
if not os.path.exists(outdir): os.mkdir(outdir)

# in outdir, run:
# $ pdflatex filename
files_before = [f for f in os.listdir(outdir) if os.path.isfile(os.path.join(outdir, f))]
#print(files_before)
with open(outdir + 'remove.rsc', 'w') as frsc:
	frsc.write("delete.field = { review }\n")
	frsc.write("delete.field = { abstract }\n")

subprocess.run(['pdflatex', '-interaction=batchmode', filestem], cwd=outdir, check=True)

files_after = [f for f in os.listdir(outdir) if os.path.isfile(os.path.join(outdir, f))]
#print(files_after)

print("stripping bibliography")
subprocess.run(['bibtool', '-r', 'remove.rsc', '-x', filestem + '.aux', '-o', 'ref.bib'], cwd=outdir, check=True)

# find bib files used
bibfiles = []
with open(outdir + filestem + '.aux', 'r', encoding='latin1') as faux:
	for line in faux:
		if line.startswith('\\bibdata'):
			for bib in line.rstrip().rstrip('}').split('\\bibdata{')[1].split(','):
				bibfiles.append(bib + '.bib')
		del line

for f in files_after:
	if f not in files_before:
		print("removing temporary file", f)
		os.unlink(os.path.join(outdir, f))

print("bibfiles to unite:", bibfiles)
if bibfiles == ['ref.bib']:
	print("packbib was already run, aborting!")
	sys.exit(0)

origlines = 0
for bibfile in bibfiles:
	print("removing file", bibfile)
	origlines += countlines(os.path.join(outdir, bibfile))
	os.unlink(os.path.join(outdir, bibfile))

print("rewriting", filename)
# then replace bibliography line with \bibliography{ref.bib}
regex = re.compile(r"\\bibliography{[^}]*}")
subst = "\\\\bibliography{ref}"
# and delete all .bib files
with open(outdir + filename, 'r', encoding='latin1') as fin:
	lines = []
	for line in fin:
		lines.append(regex.sub(subst, line))
		del line

with open(outdir + filename, 'w', encoding='latin1') as fout:
	for line in lines:
		fout.write(line)
		del line

print("stripped bibliography in ref.bib is %d lines, from %d total lines in %s" % (countlines(outdir + 'ref.bib'), origlines, ','.join(bibfiles)))


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


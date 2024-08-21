"""
Prepares a LaTeX paper with all its resources for an archive that can be uploaded
to a journal.
"""

import shutil
import sys
import os

filename = sys.argv[1]
outdir = 'package-%s/' % filename
if not os.path.exists(outdir): os.mkdir(outdir)
#l = open(filename).readlines()
outfile = open(outdir + filename, 'w', encoding='latin1')
file_ids = {}

def handle_resource(filepath):
	"""Copies file into the target folder."""
	if filepath not in file_ids:
		filename = os.path.basename(filepath)
		if filename.count('.') > 1: # remove additional "."
			prefix, suffix = filename.rsplit('.', maxsplit=1)
			prefix = prefix.replace('.', '_')
			filename = '%s.%s' % (prefix, suffix)
		
		# if we have same name already from a different folder
		# give it an alternative name
		if filename in file_ids.values():
			# add a number to it
			prefix, suffix = filename.rsplit('.', maxsplit=1)
			prefix = prefix.replace('.', '_')
			filename = '%s.%s' % (prefix, suffix)
			for i in range(100):
				filenameplus = '%s%d.%s' % (prefix, i, suffix)
				if filenameplus not in file_ids.values():
					filename = filenameplus
					break
		
		file_ids[filepath] = filename
	
	filename = file_ids[filepath]
	outfilename = outdir + filename
	print('copying resource %s from %s' % (filename, filepath))
	shutil.copyfile(filepath, outfilename)
	return filename

def handle_command(cmd, l, filepostfix = ''):
	"""Replace file-related command argument with new filename."""
	i = l.index(r'\%s{' % cmd) + len(r'\%s{' % cmd)
	n = l[i:].index('}')
	filename = handle_resource(l[i:i+n] + filepostfix)
	return '%s%s%s' % (l[:i], filename, l[i+n:])

def handle_command_multiple(cmd, l, filepostfix = ''):
	"""Replace multi-file command arguments with new filenames."""
	i = l.index(r'\%s{' % cmd) + len(r'\%s{' % cmd)
	n = l[i:].index('}')
	filenames = []
	for li in l[i:i+n].split(','):
		lout = handle_resource(li + filepostfix)
		filenames.append(lout.replace(filepostfix, ''))
	return '%s%s%s' % (l[:i], ','.join(filenames), l[i+n:])


def concat_file_lines(filename, remove_comments=False):
	"""inline \\input latex files into one long latex file."""
	for l in open(filename, 'r', encoding='latin1'):
		if '\\input{' in l:
			cmd = 'input'
			i = l.index(r'\%s{' % cmd) + len(r'\%s{' % cmd)
			n = l[i:].index('}')
			yield from concat_file_lines(l[i:i+n])
		else:
			parts = l.split('%')
			if remove_comments and len(parts) > 1 and not parts[0].endswith('\\'):
				yield parts[0]
			else:
				yield l

def rewrite_file(filename, remove_comments):
	for l in concat_file_lines(filename, remove_comments=remove_comments):
		l = l.replace(r'\altaffiltext', r'\altaffiliation')
		
		# copy images
		if '\\includegraphics' in l:
			# handle multiple includegraphics on the same line
			chunks = l.split('\\includegraphics')
			l2 = ''
			for i in range(1, len(chunks), 2):
				ll = chunks[i]
				# include [....] into before
				if ll.startswith('[') and ']' in ll:
					options, afteroptions = ll.split(']')
					ll = ll + '[' + options + ']'
					before, after = afteroptions.split('{', 1)
				else:
					before, after = ll.split('{', 1)
				filepath, post = after.split("}", 1)
				realfilepath = filepath.replace('\\lyxdot ', '.')
				if os.path.exists(realfilepath + '.pdf'):
					realfilepath = realfilepath + '.pdf'
				elif os.path.exists(realfilepath + '.eps'):
					realfilepath = realfilepath + '.eps'
				elif os.path.exists(realfilepath + '.png'):
					realfilepath = realfilepath + '.png'
				filename = handle_resource(realfilepath)
				l2 += chunks[i-1] + '\\includegraphics' + '%s{%s}%s' % (before, filename.replace('.pdf', ''), post)
			del l
			l = l2

		# for latex tables etc, but we do not search recursively; better to use input
		if '\\include{' in l:
			l = handle_command('include', l, filepostfix = '.tex')

		# handle bibliography
		if '\\bibliography{' in l:
			l = handle_command_multiple('bibliography', l, filepostfix='.bib')
		
		# copy over styles if they exist
		if l.startswith('\\documentclass'):
			before, after = l.split('{', 1)
			filepath, post = after.split("}", 1)
			realfilepath = filepath + '.cls'
			if os.path.exists(realfilepath):
				_ = handle_resource(realfilepath)

		# copy over bibtex styles if they exists
		if l.startswith('\\bibliographystyle'):
			before, after = l.split('{', 1)
			filepath, post = after.split("}", 1)
			realfilepath = filepath + '.bst'
			if os.path.exists(realfilepath):
				_ = handle_resource(realfilepath)
		
		outfile.write(l)
	outfile.close()

rewrite_file(filename, True)

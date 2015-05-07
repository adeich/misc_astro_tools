import argparse
import os
import re


# This program takes NGVS .cat files (fixed-width tablular data with a bunch of
# header lines we don't care about) and turns them into a single comma-delimited
# CSV file.

# Takes a list of names of NGVS files in CWD and writes content to 1 big csv file.
def make_csv_file_from_file_list(sOutputFileName, lFileList):

	# helper function to convert fixed-width line to csv line.
	def convert_fw_line_to_csv(sLine):
		spaces_regex = re.compile('[\s]+')
		# replace each occurrence of a space with a comma.
		sNewCSVLine = spaces_regex.subn(',', sLine.strip())[0]
		return sNewCSVLine

	# Get the column definitions once, from the first NGVS file.
	# Each NGVS file has an identical copy of these column defs.
	with open(lFileList[0]) as f_in:

		# collect column definitions.
		sCurrentLine = f_in.readline()
		oColumnNameRegex = re.compile('#[" "]+([^" "]+)[" "]+([^" "]+)[" "]*')
		lColumnNames = []
		while sCurrentLine[0] == '#':
			lColumnNames.append(oColumnNameRegex.search(sCurrentLine).group(2))
			sCurrentLine = f_in.readline()

		# add our own, single column.
		lColumnNames.append('source_file')

		sHeaderCSVline = '{}\n'.format(','.join(lColumnNames))

	# open the single output file (the CSV).
	with open(sOutputFileName, 'w') as f_out:
		# write the header line.
		f_out.write('{}\n'.format(sHeaderCSVline.strip()))


		# read through all .cat files, copying their data.
		for sFile in lFileList:
			print '> Reading from {}'.format(sFile)

			short_filename = os.path.basename(sFile)
			with open(sFile, 'r') as f_in:
				sCurrentLine = f_in.readline()

				# skip header rows.
				while sCurrentLine[0] == '#':
					sCurrentLine = f_in.readline()
				
				# run through rest of rows, copy each to output file.
				while not sCurrentLine == '':
					# Also, notice here that the final column value is the name of current input
					# file. This matches up with 'source_file' column, added above.
					f_out.write('{},{}\n'.format(convert_fw_line_to_csv(sCurrentLine), short_filename))
					sCurrentLine = f_in.readline()

	print '> Created "{}"'.format(sOutputFileName)	



# Within the specified 'source_directory', finds all files with '.cat' in their
# name and combines their data into one big CSV file.
def convert_all_cats_in_dir(output_filename, source_directory=None):
	if not source_directory:
		source_directory = os.getcwd()
	lAllFiles = os.listdir(source_directory)
	l_cat_files = [os.path.join(source_directory, sFile) for 
		sFile in lAllFiles if sFile.find('.cat') != -1]
	print '> found {} .cat files in {} ...'.format(len(l_cat_files), source_directory)
	make_csv_file_from_file_list(os.path.join(source_directory, output_filename), l_cat_files)
		

if __name__ == "__main__":
	# Get commandline arguments.
	parser = argparse.ArgumentParser(description='description')
	parser.add_argument('--csv_output_filename', '-f', type=str,
                   help='output CSV filename')
	parser.add_argument('--source_directory', '-d', type=str,
                   help='directory of NGVS .cat files')
	args = parser.parse_args()
  # Call main function.
	convert_all_cats_in_dir(source_directory=args.source_directory, output_filename=args.csv_output_filename)

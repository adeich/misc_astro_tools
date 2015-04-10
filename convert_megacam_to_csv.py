import argparse
import os
import re

# find all files with '.cat' in their name and make 1 big csv file.
def make_big_file_from_list(sOutputFileName, lFileList):

	# helper function to convert fixed-width line to csv line.
	def convert_fw_line_to_csv(sLine):
		spaces_regex = re.compile('[\s]+')
		# replace each occurrence of a space with a comma.
		sNewCSVLine = spaces_regex.subn(',', sLine.strip())[0]
		return sNewCSVLine

	# first, get the header data just once.
	with open(lFileList[0]) as f_in:

		# collect column definitions
		sCurrentLine = f_in.readline()
		oColumnNameRegex = re.compile('#[" "]+([^" "]+)[" "]+([^" "]+)[" "]*')
		lColumnNames = []
		while sCurrentLine[0] == '#':
			lColumnNames.append(oColumnNameRegex.search(sCurrentLine).group(2))
			sCurrentLine = f_in.readline()

		sHeaderCSVline = '{}\n'.format(','.join(lColumnNames))

	# open the output file.
	with open(sOutputFileName, 'w') as f_out:
		# write the header line.
		f_out.write('{}\n'.format(sHeaderCSVline.strip()))

		for sFile in lFileList:
			with open(sFile, 'r') as f_in:
				sCurrentLine = f_in.readline()

				# skip header rows.
				while sCurrentLine[0] == '#':
					sCurrentLine = f_in.readline()
				
				# run through rest of rows, copy each to output file.
				while not sCurrentLine == '':
					f_out.write('{}\n'.format(convert_fw_line_to_csv(sCurrentLine)))
					sCurrentLine = f_in.readline()

# Within the specified 'operating_directory', finds all files with '.cat' in their
# name and combines their data into one big CSV file.
def run_on_file_list(operating_directory, sOutputName):
	lAllFiles = os.listdir(operating_directory)
	l_csv_files = [os.path.join(operating_directory, sFile) for 
		sFile in lAllFiles if sFile.find('.cat?') != -1]
	make_big_file_from_list(os.path.join(operating_directory, sOutputName), l_csv_files)
	print 'finished.'	
		
		
# run on single, specified file. currently this function is not in use.
def main_func(sFileName):

	# open input file.
	with open(sFileName, 'r') as f_in:
		sCurrentLine = f_in.readline()

		# collect column definitions
		lColumnNames = []
		oColumnNameRegex = re.compile('#[" "]+([^" "]+)[" "]+([^" "]+)[" "]*')
		while sCurrentLine[0] == '#':
			lColumnNames.append(oColumnNameRegex.search(sCurrentLine).group(2))
			sCurrentLine = f_in.readline()

		# open output file
		if sFileName.find('.csv') == -1:
			raise BaseException("Filename needs '.csv' at the end")
		sOutputCSV = sFileName[:sFileName.find('.csv')] + '_topcat.csv'
		with open(sOutputCSV, 'w') as f_out:

			# write a header line
			f_out.write('{}\n'.format(','.join(lColumnNames)))
	
			spaces_regex = re.compile('[\s]+')
			while not sCurrentLine == '':
				# replace each section of contiguous spaces with a comma. 
				sNewCSVLine = spaces_regex.subn(',', sCurrentLine.strip())[0]
				f_out.write('{}\n'.format(sNewCSVLine))
				sCurrentLine = f_in.readline()
			print 'finished.'



if __name__ == "__main__":
	# Get commandline arguments.
	parser = argparse.ArgumentParser(description='description')
	parser.add_argument('directory', metavar='d', type=str,
                   help='directory')
	parser.add_argument('filename', metavar='f', type=str,
                   help='filename')
	args = parser.parse_args()
  # Call main function.
	run_on_file_list(args.directory, args.filename)

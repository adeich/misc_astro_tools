import numpy as np
import urllib2
import urllib
import os
import os.path
import argparse
import logging

#############
### USAGE ###
# To run this from the commandline, enter 
# $ python automated_css_search.py 187.70593 12.39112 100 
#
# These arguments are the RA, DEC, and search radius (example above is of M87).
# This particular run will create the following readout (over several seconds):
#
# >RA = 187.70593, DEC = 12.39112, Search Angle = 100 (arcmin).
# >request sent to CSC web server ...
# >data received...
# >Querying SDSS dr7 for 354 objects ...
# >data received...
# >After filtering, 8 CSS candidate(s) remain.
# >HTML document with thumbnails created: /Users/aaron/Documents/astr155/x-ray-match/results_for_RA187.70593_DEC12.39112_Rad100/webpage_RA187.70593_DEC12.39112_Rad100.html
#
# You can open the HTML file in a web browser and it will contain thumbnail-links to the DR7 navigate page.
# This program creates a directory for each search (named 'results_for_[RA]_[DEC]_[RADIUS]') and it puts
# all the resulting files in to this directory.
#
# Alternatively, if you're running this program from a python interpreter, you can call the function
# get_candidates(ra, dec, search_radius), which is what the commandline calls anyway.
#
# Be warned that this program is not smart about handling errors from the web servers 
# (e.g. server timeout; invalid RA/DEC; etc). If you're getting weird parse errors from 
# this program, go and try plugging in your same search parameters first into the Chandra
# and then DR7 search pages to make sure those searches are returning things. If this program is still
# giving you weird errors, feel free to email me at deichaaron@gmail.com
#####################################


# Makes url GET request from chandra database.
def load_CSC_SDSS_CSV(ra, dec, search_radius):

	sUrl = 'http://cxc.harvard.edu/cgi-gen/cda/CSC-SDSSxmatch.pl?where=&ra_cone={}&dec_cone={}&radius_cone={}&order=&format=tab&Query=+++Submit+Query+++'.format(ra, dec, search_radius)
	request = urllib2.Request(sUrl)
	print "request sent to CSC web server ..."
	response_string = urllib2.urlopen(request).read()
	print "data received..."
	
	if len(response_string) < 400:
		raise BaseException('0 results from Chandra with request URL {}'.format(sUrl)) 

	return response_string


# parses the web response from the chandra website. 
# returns a list of SDSS objIDs.
def parse_CSC_CSV(CSC_file_string, oFileNames):

	# save the unedited return from the web:
	with open(oFileNames['CSC_data'] + 'raw', 'w') as f:
		f.write(CSC_file_string)

	# split up string by newlines.
	lines = CSC_file_string.splitlines()

	# remove first 9 lines (html).
	lines = lines[9:]

	# remove the last 5 lines (html).
	lines = lines[:-5]

	# remove '<pre>' from the beginning of the (now) first line.
	lines[0] = lines[0][5:]

	# remove the (now) second line, which is just column data-type descriptions.
	del lines[1]

	sCSV_filename = oFileNames['CSC_data']
	
	# write remaining lines to file, so that numpy.genfromcsv can read it.
	# and so that we can visually inspect the data.
	with open(sCSV_filename, 'w') as f:
		for sLine in lines:
			f.write(sLine)
			f.write('\n') 

	# open same file up again, read-only, to transfer it to a recarray.
	with open(sCSV_filename, 'r') as f:
		data_in_recarray = np.recfromcsv(f, delimiter='\t')
	
	# all fields from CSC are available here, but for now we're just 
	# selecting the SDSS objID.
	return list(data_in_recarray['objid'])


# Loads specified objects from SDSS DR7 and returns a single recarray.
def load_SDSS_data(CSC_objID_list, ra, dec, search_radius, oFileNames):

	def create_SQL_query(CSC_objID_list, ra, dec, search_radius):
		query_str = 'SELECT objID,ra,dec,u,g,r,i,z,petroRad_r, type FROM PhotoObjAll WHERE objID IN '.format(ra, dec, search_radius)
		query_str = ' '.join([query_str, str(tuple(CSC_objID_list))])
		return query_str 

	def makeSDSS_post_request(sSQL_query):
		sURL = 'http://cas.sdss.org/dr7/en/tools/search/x_sql.asp'
		# for POST request
		values = {'cmd': sSQL_query,
							'format': 'csv'}
		data = urllib.urlencode(values)
		request = urllib2.Request(sURL, data)
		response = urllib2.urlopen(request)
		return response.read()

	sql_query_string = create_SQL_query(CSC_objID_list, ra, dec, search_radius)
	logging.debug(sql_query_string)
	print 'Querying SDSS dr7 for {} objects ...'.format(len(CSC_objID_list))
	sdss_data_string = makeSDSS_post_request(sql_query_string)
	logging.debug(sdss_data_string)
	print 'data received...'

	sSDSS_filename = oFileNames['SDSS_data']

	# save SDSS csv to file.	
	with open(sSDSS_filename, 'w') as f:
		f.write(sdss_data_string)

	# reopen same file to read into recarray.
	with open(sSDSS_filename, 'r') as f:
		sdss_rec_array = np.recfromcsv(f, delimiter=',')

	return sdss_rec_array


def filter_CSS_candidates(SDSS_data_recarray, oFileNames, petroRadRange=(0.,6.), 
		i_mag_range=(15.,19.4), color_range=(0.7, 1.3)):

	def IsObjectInCSSRegime(SDSS_object_line, petroRadRange=petroRadRange,
		i_mag_range=i_mag_range, color_range=color_range):
		g_mag = SDSS_object_line['g']
		i_mag = SDSS_object_line['i']
		g_i = g_mag - i_mag
		petroRad_r = SDSS_object_line['petrorad_r']
		object_type = SDSS_object_line['type']
		return ((i_mag > i_mag_range[0]) & (i_mag < i_mag_range[1])
			& (g_i > color_range[0]) & (g_i < color_range[1])
			& (object_type == 3) 
			& (petroRadRange[0] < petroRad_r) & (petroRad_r < petroRadRange[1]))

	# similar functionality to numpy.where(), but I find this more readable.
	CSS_candidate_indices = []
	for index, line_content in enumerate(SDSS_data_recarray):
		if IsObjectInCSSRegime(line_content):
			CSS_candidate_indices.append(index)

	print "After filtering, {} CSS candidate(s) remain.".format(len(CSS_candidate_indices))
	return SDSS_data_recarray[CSS_candidate_indices]

# generate a local webpage for allowing visual inspection of thumbnails.
def generate_webpage_of_results(candidates_recarray, oFileNames):
	lCandidates = [] # a list of dicts, each one containing associated data for each candidate.
	for sCandidateLine in candidates_recarray:
		ra = sCandidateLine['ra']
		dec = sCandidateLine['dec']
		sThumbnailImg = """http://skyservice.pha.jhu.edu/DR7/ImgCutout/getjpeg.aspx?ra={}&dec={}&scale=0.40&width=120&height=120&opt=""".format(ra, dec)
		sLink = """http://skyserver.sdss.org/dr7/en/tools/chart/navi.asp?ra={}&dec={}""".format(ra, dec)
		lCandidates.append({'thumb':sThumbnailImg, 'link':sLink, 
			'petrorad':sCandidateLine['petrorad_r'], 'ra':ra, 'dec': dec,
			'g_i':sCandidateLine['g'] - sCandidateLine['i'],
			'i':sCandidateLine['i']})

	with open(oFileNames['webpage'], 'w') as f:
		f.write("<html><head></head><body>\n")
		f.write("Click on thumbnails to go to their DR7 Navigate page.<br>\n")
		f.write("<table border=1 cellspacing=2 cellpadding=0>\n")	
		for candidate in lCandidates:
			f.write('<tr>')
			f.write("""<td><a href='{}'><img src='{}' width=120 height=120></a></td>""".format(candidate['link'], candidate['thumb']))
			f.write('<td>')
			f.write('ra, dec: {}, {}<br>\n'.format(candidate['ra'], candidate['dec']))
			f.write('petro_rad: {}<br>\n'.format(candidate['petrorad']))
			f.write('i: {}<br>\n'.format(candidate['i']))
			f.write('g - i: {}<br>\n'.format(candidate['g_i']))
			f.write('</td>')
			f.write('</tr>')
		f.write("""</table></body></html>""")
	
	print "HTML document with thumbnails created: {}".format(oFileNames['webpage'])


# High-level function. pulls from CSC database; parses.
# For CSC objects, pulls data from SDSS database; parses.
# Filters objects for color/magnitude, radius, etc.
# Finally, creates a little, local webpage for manual inspection
# of thumbnails.
def get_candidates(ra, dec, search_radius):

	# define names of files.
	sSearchID = 'RA{}_DEC{}_Rad{}'.format(ra, dec, search_radius)
	subdirectory_name = 'results_for_{}'.format(sSearchID)
	subdirectory_path = os.path.join(os.getcwd(), subdirectory_name)
	oFileNames = {
		'CSC_data': os.path.join(subdirectory_path, 'CSC_data_{}.csv'.format(sSearchID)),
		'SDSS_data': os.path.join(subdirectory_path, 'SDSS_data_{}.csv'.format(sSearchID)),
		'filtered_candidates': os.path.join(subdirectory_path, 'filtered_candidates_{}.csv'.format(sSearchID)),
		'webpage': os.path.join(subdirectory_path, 'webpage_{}.html'.format(sSearchID))}

	# If it doesn't already exist, create the directory to put these files in.
	if not os.path.exists(subdirectory_path):
		os.makedirs(subdirectory_path)
	# Create the log file.
	logging.basicConfig(filename=os.path.join(subdirectory_path, 'log.txt'),
		level=logging.DEBUG, filemode='w')

	# Load data and parse, saving along intermediate points.
	CSC_file_string = load_CSC_SDSS_CSV(ra, dec, search_radius)
	CSC_objID_list = parse_CSC_CSV(CSC_file_string, oFileNames)
	SDSS_data_recarray = load_SDSS_data(CSC_objID_list, ra, dec, search_radius, oFileNames)
	filtered_candidates_recarray = filter_CSS_candidates(SDSS_data_recarray, oFileNames)
	generate_webpage_of_results(filtered_candidates_recarray, oFileNames)
	

if __name__ == '__main__':

	# Get commandline arguments.
	parser = argparse.ArgumentParser(description='Calls both the Chandra and SDSS databases to look for CSS objects.')
	parser.add_argument('ra', metavar='ra', type=str, 
                   help='ra, as in "ra and dec"')
	parser.add_argument('dec', metavar='dec', type=str,
                   help='dec, as in "ra and dec"')
	parser.add_argument('angle', metavar='angle', type=str,
                   help='angle of search region (arcmin)')
	args = parser.parse_args()

	# Call main function.
	print "RA = {}, DEC = {}, Search Angle = {} (arcmin).".format(args.ra, args.dec, args.angle)
	get_candidates(args.ra, args.dec, args.angle)

from astropy.io import fits
from astropy.coordinates import match_coordinates_sky
from astropy.coordinates import SkyCoord
from astropy import units as u
import numpy as np
import quick_plot 

# Takes a list of column names and returns a dict containing each specified column. 
def get_data_from_fits(column_names=None, input_filename='nsa_matched_catalog.fits'):
	print 'loading {} columns from {} ...'.format(len(column_names), input_filename)
	hdulist = fits.open(input_filename)
	print '\tdone.'
	tbdata = hdulist[1].data

	#print(hdulist[1].header.values())
	#print(sorted(list(tbdata.dtype.names)))

	content_of_specified_columns = {}
	for column_name in column_names:
		try:
			content_of_specified_columns[column_name] = tbdata[column_name]
		except KeyError as e:
			raise BaseException("Column '{}' not found in file '{}' from list:\n {}".format(
				column_name, input_filename, sorted(list(tbdata.dtype.names))))

	return content_of_specified_columns


def get_data_from_csv(input_filename=None, column_names=None):
	# for reading header, open only the first line (so as not to have to read whole file).
	with open(input_filename, 'r') as f: 
		header_dict = {name: index for (index, name) in enumerate(f.next().strip().split(','))}

	# check that each specified column name is present in the header.
	for desired_column in column_names:
		if not desired_column in header_dict:
			raise BaseException("Column '{}' not found '{}' from list:\n{}".format(
				desired_column, input_filename, sorted(header_list)))

	# load specified columns into single array.
	print 'loading {} columns from {} ...'.format(len(column_names), input_filename)
	column_indices = [header_dict[column_name] for column_name in column_names]
	ndarray = np.genfromtxt(input_filename, dtype=None, delimiter=',', usecols=column_indices, skip_header=1)
	print '\tdone.'

	# put each column of ndarray into its own array in the return dict.
	content_of_specified_columns = {}
	for new_column_index, column_name in enumerate(column_names):
		content_of_specified_columns[column_name] = ndarray[''.join(['f', str(new_column_index)])]

	return content_of_specified_columns
	
# returns, for each object in NSA, index of closest object in GZoo; then angular separation. 
def match_coordinates(GZoo_RA, GZoo_DEC, NSA_RA, NSA_DEC):
 	
	print 'matching coordinates ... '  
	catalogcoord = SkyCoord(ra=GZoo_RA * u.degree, dec=GZoo_DEC * u.degree)
	matchcoord = SkyCoord(ra=NSA_RA * u.degree, 
    dec=NSA_DEC * u.degree)

	indices_into_GZoo, sep2d, dist3d = match_coordinates_sky(matchcoord, catalogcoord)

	# 1D array of angular distance of each NSA object to nearest GZoo neighbor (arcseconds).
	sep2d_array = np.array(sep2d.arcsecond)
	# 1D array, for each NSA object, index into GZoo of nearest object.
	indices_into_GZoo_array = np.array(indices_into_GZoo)

	# Combine these two arrays into a 2D array.
	#output_array = np.column_stack((sep2d_array, indices_into_GZoo_array))
	combined_array = np.rec.fromarrays((indices_into_GZoo, sep2d_array), 
		dtype=[('i', int),('angle', float)])
	
	print '\tdone.'
	return combined_array


def highest_level():

	# define filenames and column names.
	NSA_defs = {'filename': 'nsa_matched_catalog.fits',
		'column_names': ['RA', 'DEC']}
	GZoo_defs = {'filename': 'zoo2MainSpecz.csv',
		'column_names': ['ra', 'dec', 'dr8objid']} 

	# pull specified columns from NSA into memory.
	NSA_specified_column_data = get_data_from_fits(input_filename=NSA_defs['filename'], column_names=NSA_defs['column_names'])

	# pull specified columns from Galaxy Zoo into memory.
	GZoo_specified_column_data = get_data_from_csv(input_filename=GZoo_defs['filename'], column_names=GZoo_defs['column_names'])



	# perform coordinate match. Use coordinate match only to assign DR8IDs or 
	# whatever foreign key to all rows in NSA_defs.
	combined_array = match_coordinates(GZoo_specified_column_data['ra'], GZoo_specified_column_data['dec'],
		NSA_specified_column_data['RA'], NSA_specified_column_data['DEC'])

	#print '{} / {} matches have angle less than 1 arcsecond.'.format(len(matches), len(matched_coordinates_dict['sep2d']))
#	quick_plot.quick_histogram(matched_coordinates_dict['sep2d'], title="angular separation of nearest neighbor",
#		filename='sep2d.png', show_plot=False, nbins=5000, xlabel='degrees',
#		 ylabel='n objects', axis=[0, .1, 0, 2500])	

	# add DR8ID to all matched NSA data. 'Null' to all non-matched objects.
	return combined_array

#get_data_from_fits()

combined = highest_level()

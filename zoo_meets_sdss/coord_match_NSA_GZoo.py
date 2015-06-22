from astropy.io import fits
from astropy.coordinates import match_coordinates_sky
from astropy.coordinates import SkyCoord
from astropy import units as u
import numpy as np
import quick_plot 
from collections import OrderedDict

# Takes a list of column names and returns a recarray.
def get_data_from_fits(column_names=None, input_filename='nsa_matched_catalog.fits'):
	print 'loading columns {} from {} ...'.format(
		column_names, input_filename)
	hdulist = fits.open(input_filename)
	tbdata = hdulist[1].data

	# for printing out column definitions.
	#	print hdulist[1].columns.info()

	#print(hdulist[1].header.values())
	#print(sorted(list(tbdata.dtype.names)))

	# This is an OrderedDict to preserve initial ordering of columns.
	columns = OrderedDict()
	for column_name in column_names:
		try:
			columns[column_name] = tbdata[column_name]
		except KeyError as e:
			raise BaseException("Column '{}' not found in file '{}' from list:\n {}".format(
				column_name, input_filename, sorted(list(tbdata.dtype.names))))

	# transfer dict of columns (1D arrays) to recarray. Note implicit reliance on ordering
	# of dictionary items.
	output_array = np.rec.fromarrays(tuple(columns.values()),
		dtype=[(key, value.dtype) for (key, value) in zip(columns.keys(), columns.values())])

	print '\tdone. Loaded {} rows.'.format(len(output_array))
	return output_array



# reads csv file and for specified column names, returns a recarray.
def get_data_from_csv(input_filename=None, column_names=None):
	# for reading header, open only the first line (so as not to have to read whole file).
	with open(input_filename, 'r') as f: 
		header_dict = {name: index for (index, name) in enumerate(f.next().strip().split(','))}

	# This prints out all the column names.
	#print sorted([column_name for column_name in header_dict])

	# check that each specified column name is present in the header.
	for desired_column in column_names:
		if not desired_column in header_dict:
			raise BaseException("Column '{}' not found '{}' from list:\n{}".format(
				desired_column, input_filename, sorted(header_list)))

	# load specified columns into single array.
	print 'loading columns {} from {} ...'.format(column_names, input_filename)
	column_indices = [header_dict[column_name] for column_name in column_names]
	ndarray = np.genfromtxt(input_filename, dtype=None, delimiter=',', usecols=column_indices, skip_header=1)
	print '\tdone. Loaded {} rows.'.format(len(ndarray))

	# put each column of ndarray into its own array in the return dict.
	columns = OrderedDict()
	for new_column_index, column_name in enumerate(column_names):
		columns[column_name] = ndarray[''.join(['f', str(new_column_index)])]

	# transfer dict of columns (1D arrays) to recarray. Note implicit reliance on ordering
	# of dictionary items.
	output_array = np.rec.fromarrays(tuple(columns.values()),
		dtype=[(key, value.dtype) for (key, value) in zip(columns.keys(), columns.values())])

	return output_array 
	


# returns array containing, for each object in NSA, index of closest object in GZoo;
# also respective angular separation. 
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
	nearest_GZoo_obj_pointers = np.rec.fromarrays((indices_into_GZoo, sep2d_array), 
		dtype=[('index_into_GZoo', int),('arcseconds', float)])
	
	print '\tdone.'
	return nearest_GZoo_obj_pointers 



# Take all specified GZoo columns, NSA columns, and NSA->GZoo matching pointer array. 
# Returns a single rec array. In the future, this should be a done by a proper database.
def produce_combined_table(NSA_recarray, GZoo_recarray, NSA_to_GZoo_match_array, foreign_key,
	output_filename):
	#output_columns = list(map(lambda s: 'GZoo_' + s, GZoo_recarray.dtype.names)) + list(
	#	map(lambda s: 'NSA_' + s, NSA_recarray.dtype.names)) 

	def make_csv_string(GZoo_row, NSA_row, this_is_header_line=False):
		if this_is_header_line:
			output_columns = list(GZoo_recarray.dtype.names) + list(NSA_recarray.dtype.names)
			csv_string =  ','.join(output_columns)
		else:
			output_list = []
			output_list.extend([str(i) for i in GZoo_row])
			output_list.extend([str(i) for i in NSA_row]) 
			csv_string = ','.join(output_list)
		csv_string = ''.join([csv_string, '\n'])
		return csv_string

	with open(output_filename, 'w') as f:
		# write header line.
		f.write(make_csv_string(GZoo_row=GZoo_recarray[0],
			NSA_row=NSA_recarray[0], 
			this_is_header_line=True))

		# write each row in CSV format.
		for index_into_NSA, match_row in enumerate(NSA_to_GZoo_match_array):
			if match_row['arcseconds'] < 1.:
				index_into_GZoo = match_row['index_into_GZoo']
				f.write(make_csv_string(GZoo_recarray[index_into_GZoo], 
					NSA_recarray[index_into_NSA]))

	return ''


def make_new_NSA_fits_with_foreign_key():
	pass

def highest_level():

	# define filenames and column names.
	NSA_defs = {'filename': 'nsa_matched_catalog.fits',
		'column_names': ['NSAID','RA','DEC','Z','ZDIST','MASS','SERSIC_TH50','D4000','HAEW']}
	GZoo_defs = {'filename': 'zoo2MainSpecz.csv',
		'column_names': ['dr8objid','ra', 'dec','t01_smooth_or_features_a01_smooth_debiased','t04_spiral_a08_spiral_debiased']}
	foreign_key = 'dr8objid'
	output_filename = 'combined.csv'

	# pull specified columns from NSA into memory.
	NSA_specified_column_data = get_data_from_fits(input_filename=NSA_defs['filename'],
		column_names=NSA_defs['column_names'])

	# pull specified columns from Galaxy Zoo into memory.
	GZoo_specified_column_data = get_data_from_csv(input_filename=GZoo_defs['filename'], 
		column_names=GZoo_defs['column_names'])

	# perform coordinate match. Use coordinate match only to assign DR8IDs or 
	# whatever foreign key to all rows in NSA_defs.
	nearest_GZoo_obj_pointers = match_coordinates(GZoo_specified_column_data['ra'], GZoo_specified_column_data['dec'],
		NSA_specified_column_data['RA'], NSA_specified_column_data['DEC'])

	#print '{} / {} matches have angle less than 1 arcsecond.'.format(len(matches), len(matched_coordinates_dict['sep2d']))
#	quick_plot.quick_histogram(matched_coordinates_dict['sep2d'], title="angular separation of nearest neighbor",
#		filename='sep2d.png', show_plot=False, nbins=5000, xlabel='degrees',
#		 ylabel='n objects', axis=[0, .1, 0, 2500])	

	# add DR8ID to all matched NSA data. 'Null' to all non-matched objects.
	combined_table = produce_combined_table(NSA_specified_column_data, GZoo_specified_column_data, 
		NSA_to_GZoo_match_array=nearest_GZoo_obj_pointers, foreign_key=foreign_key,
		output_filename=output_filename)


	return combined_table

#get_data_from_fits()

combined = highest_level()
print combined

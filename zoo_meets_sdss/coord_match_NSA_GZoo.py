from astropy.io import fits
from astropy.coordinates import match_coordinates_sky
from astropy.coordinates import search_around_sky 
from astropy.coordinates import SkyCoord
import astropy.coordinates
from astropy import units as u
import numpy as np
import quick_plot 
from collections import OrderedDict

# Takes a list of column names and returns a recarray.
def get_data_from_fits(column_names=None, input_filename='nsa_matched_catalog.fits',
		write_to_csv_name=None):

	print 'loading columns {} from {} ...'.format(
		column_names, input_filename)

	# open and read the fits file.
	hdulist = fits.open(input_filename)
	tbdata = hdulist[1].data

	# for printing out column definitions.
	#	print hdulist[1].columns.info()
	# print(hdulist[1].header.values())
	# print(sorted(list(tbdata.dtype.names)))

	# This is an OrderedDict to preserve initial ordering of columns.
	columns = OrderedDict()

	# For each column specified, make its dict entry point to its respective
	# 1D recarray from the fits tbdata object.
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


	# write output_array to csv.
	if write_to_csv_name:
		np.savetxt(write_to_csv_name, output_array, delimiter=',',
			header=','.join(output_array.dtype.names))

	print '\tdone. Loaded {} rows.'.format(len(output_array))
	return output_array



# reads csv file and for specified column names, returns a recarray.
def get_data_from_csv(input_filename=None, column_names=None, write_to_csv_name=None):

	# Read only the header, then close the file.
	with open(input_filename, 'r') as f: 
		# create a dict where the keys are the column names and the values are the column number.
		header_dict = {name: index for (index, name) in enumerate(f.next().strip().split(','))}

	# This prints out all the column names.
	#print sorted([column_name for column_name in header_dict])

	# Check that each specified column name is present in the header.
	for desired_column in column_names:
		if not desired_column in header_dict:
			raise BaseException("Column '{}' not found '{}' from list:\n{}".format(
				desired_column, input_filename, sorted(header_list)))

	# Open file again and load specified columns into single array.
	print 'loading columns {} from {} ...'.format(column_names, input_filename)
	column_indices = [header_dict[column_name] for column_name in column_names]
	ndarray = np.genfromtxt(input_filename, dtype=None, delimiter=',', usecols=column_indices, skip_header=1)
	print '\tdone. Loaded {} rows.'.format(len(ndarray))

	# Put each column of ndarray into its own array in the return dict.
	# OrderedDict preserves the order of the columns.
	columns = OrderedDict()
	for new_column_index, column_name in enumerate(column_names):
		columns[column_name] = ndarray[''.join(['f', str(new_column_index)])]

	# Transfer the dict of columns (1D arrays) into a recarray. Note implicit reliance on ordering
	# of dictionary items.
	output_array = np.rec.fromarrays(tuple(columns.values()),
		dtype=[(key, value.dtype) for (key, value) in zip(columns.keys(), columns.values())])

	# Write output_array to csv for debugging purposes.
	if write_to_csv_name:
		np.savetxt(write_to_csv_name, output_array, delimiter=',',
		header=','.join(output_array.dtype.names))

	return output_array 
	

# For each object in "match" (ra/dec), a corresponding line in the output array should 
# point to the index of the nearest object in "catalog" (ra/dec).
def match_coordinates_original(ra_1, dec_1, ra_2, dec_2, max_arcsec_sep=10):
 	
	catalog_ra = ra_1; catalog_dec = dec_1
	match_ra = ra_2; match_dec = dec_2

	print 'matching coordinates ... '  
	catalogcoord = SkyCoord(ra=catalog_ra* u.degree, dec=catalog_dec * u.degree)
	matchcoord = SkyCoord(ra=match_ra * u.degree, 
    dec=match_dec * u.degree)

	indices_into_catalog, sep2d, dist3d = match_coordinates_sky(matchcoord, catalogcoord)

	# 1D array of angular distance of each NSA object to nearest GZoo neighbor (arcseconds).
	sep2d_array = np.array(sep2d.arcsecond)
	# 1D array, for each NSA object, index into GZoo of nearest object.
	indices_into_catalog_array = np.array(indices_into_catalog)

	# Combine these two arrays into a 2D array.
	nearest_catalog_obj_pointers = np.rec.fromarrays((indices_into_catalog, sep2d_array), 
		dtype=[('index_into_catalog', int),('DEICH_match_arcsec', float)])
	
	print '\tdone.'
	return nearest_catalog_obj_pointers



# For each object in "match" (ra/dec), a corresponding line in the output array should 
# point to the index of the nearest object in "catalog" (ra/dec).
def match_coordinates_1by1(ra_1, dec_1, ra_2, dec_2, max_arcsec_sep=10):
 	
	catalog_ra = ra_1; catalog_dec = dec_1
	match_ra = ra_2; match_dec = dec_2

	print 'matching coordinates ... '  
	catalogcoord = SkyCoord(ra=catalog_ra* u.degree, dec=catalog_dec * u.degree)

	indices_into_catalog = []
	for ra, dec in zip(match_ra, match_dec): 
		matchcoord = SkyCoord(ra=ra * u.degree, 
    	dec=dec * u.degree)
		indices_into_catalog, sep2d, dist3d = match_coordinates_sky(matchcoord, catalogcoord, storekdtree=True)
		indices_into_catalog.append([indices_into_catalog, sep2d.arcsecond])


	# Combine these two arrays into a 2D array.
	nearest_catalog_obj_pointers = np.rec.fromarrays((indices_into_catalog, sep2d_array), 
		dtype=[('index_into_catalog', int),('DEICH_match_arcsec', float)])
	
	print '\tdone.'
	return nearest_catalog_obj_pointers




# For each object in "match" (ra/dec), a corresponding line in the output array should 
# point to the index of the nearest object in "catalog" (ra/dec).
def match_coordinates(ra_1, dec_1, ra_2, dec_2, max_arcsec_sep=100):
 	
	print 'matching coordinates ... '  
	coordinates1 = SkyCoord(ra=ra_1 * u.degree, dec=dec_1 * u.degree)
	coordinates2 = SkyCoord(ra=ra_2 * u.degree, 
    dec=dec_2 * u.degree)
	#max_sep_angle = astropy.coordinates.Angle('0d0m{}s'.format(max_arcsec_sep))
	max_sep_angle = astropy.units.Quantity(value=max_arcsec_sep, unit=u.arcsecond)

	indices_into_coord1, indices_into_coord2, sep2d, dist3d = search_around_sky(coordinates1, coordinates2, max_sep_angle)

	# 1D array of angular distance of each NSA object to nearest GZoo neighbor (arcseconds).
	sep2d_array = np.array(sep2d.arcsecond)
	# 1D array, for each NSA object, index into GZoo of nearest object.

	# Combine these two arrays into a 2D array.
	nearest_coord1_obj_pointers = np.rec.fromarrays((np.array(indices_into_coord1), np.array(sep2d.arcsecond)), 
		dtype=[('index_into_catalog', int),('DEICH_match_arcsec', float)])
	
	print '\tdone.'
	return nearest_coord1_obj_pointers



# Take all specified GZoo columns, NSA columns, and the NSA->GZoo matching pointer array. 
# Returns a single rec array. In the future, this should be a done by a proper database.
def produce_combined_table(NSA_recarray, GZoo_recarray, NSA_to_GZoo_match_array, foreign_key,
	output_filename, additional_columns=['DEICH_match_arcsec']):
	#output_columns = list(map(lambda s: 'GZoo_' + s, GZoo_recarray.dtype.names)) + list(
	#	map(lambda s: 'NSA_' + s, NSA_recarray.dtype.names)) 

	def make_csv_string(GZoo_row, NSA_row, match_row, this_is_header_line=False):
		if this_is_header_line:
			output_columns = list(GZoo_recarray.dtype.names) + list(NSA_recarray.dtype.names) + additional_columns
			csv_string =  '{}\n'.format(','.join(output_columns))
		else:
			output_list = []
			output_list.extend([str(i) for i in GZoo_row])
			output_list.extend([str(i) for i in NSA_row]) 
			output_list.extend([str(i) for i in [match_row['DEICH_match_arcsec']]])
			csv_string = '{}\n'.format(','.join(output_list))
		return csv_string

	with open(output_filename, 'w') as f:
		# write header line.
		f.write(make_csv_string(GZoo_row=GZoo_recarray[0],
			NSA_row=NSA_recarray[0],
			match_row=NSA_to_GZoo_match_array[0], 
			this_is_header_line=True))

		# write each row in CSV format.
		for index_into_NSA, match_row in enumerate(NSA_to_GZoo_match_array):
			if match_row['DEICH_match_arcsec'] < 100000.:
				index_into_GZoo = match_row['index_into_catalog']
				f.write(make_csv_string(GZoo_recarray[index_into_GZoo], 
					NSA_recarray[index_into_NSA],
					match_row=match_row)) 

	return ''



def highest_level():

	# define filenames and column names.
	NSA_defs = {'filename': 'nsa_v0_1_2.fits',
		'column_names': ['NSAID','RA','DEC','Z','ZDIST','MASS','SERSIC_TH50','D4000','HAEW']}
	GZoo_defs = {'filename': 'zoo2MainSpecz.csv',
		'column_names': ['dr8objid','ra', 'dec','t01_smooth_or_features_a01_smooth_debiased','t04_spiral_a08_spiral_debiased'],
		'foreign_key': 'dr8objid'}
	output_filename = 'combined.csv'

	# pull specified columns from NSA into memory.
	NSA_specified_column_data = get_data_from_fits(input_filename=NSA_defs['filename'],
		column_names=NSA_defs['column_names'], write_to_csv_name="data_from_fits.csv")

	# pull specified columns from Galaxy Zoo into memory.
	GZoo_specified_column_data = get_data_from_csv(input_filename=GZoo_defs['filename'], 
		column_names=GZoo_defs['column_names'], write_to_csv_name="data_from_galaxy_zoo.csv")

	# perform coordinate match. Use coordinate match only to assign DR8IDs or 
	# whatever foreign key to all rows in NSA_defs.
	nearest_GZoo_obj_pointers = match_coordinates_original(ra_1=GZoo_specified_column_data['ra'], dec_1=GZoo_specified_column_data['dec'],
		ra_2=NSA_specified_column_data['RA'], dec_2=NSA_specified_column_data['DEC'])

	#print '{} / {} matches have angle less than 1 arcsecond.'.format(len(matches), len(matched_coordinates_dict['sep2d']))
#	quick_plot.quick_histogram(matched_coordinates_dict['sep2d'], title="angular separation of nearest neighbor",
#		filename='sep2d.png', show_plot=True, nbins=5000, xlabel='degrees', ylabel='n objects', axis=[0, .1, 0, 2500])	

	# add DR8ID to all matched NSA data. 'Null' to all non-matched objects.
	combined_table = produce_combined_table(NSA_specified_column_data, GZoo_specified_column_data, 
		NSA_to_GZoo_match_array=nearest_GZoo_obj_pointers, foreign_key=GZoo_defs['foreign_key'],
		output_filename=output_filename)


	return combined_table

#get_data_from_fits()

if __name__ == '__main__':
	combined = highest_level()

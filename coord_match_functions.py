from astropy.coordinates import SkyCoord
from astropy import units as u
import convert_megacam_to_csv
import os


def match_pairs_between_two_sets(new_coords, old_coords, RAcolumnname, DECcolumnname, maxdtheta):
	matchcoord = SkyCoord(ra=new_coords[RAcolumnname]*u.degree,
		dec=new_coords[DECcolumnname]*u.degree)
	catalogcoord = SkyCoord(ra=old_coords[RAcolumnname]*u.degree, 
		dec=old_coords[DECcolumnname]*u.degree)

	# Each of the following 3 vars has length of matchcoord.
	idx, sep2d, dist3d = astropy.coordinates.match_coordinates_sky(matchcoord, catalogcoord)

	# list for storing the new lines with the union of both sets of input columns.
	match_lines = []

	# Iterate through each closest object of matchcoord, adding the new matchline if the 
	# angular separation is below maxdtheta.
	for i, idx_sep2d in enumerate(zip(idx, sep2d)):
		if idx_sep2d[1] <= maxdtheta: 
			new_line = old_coords[idx_sep2d[0]] + new_coords[i]
	


# Takes list of NGVS files and copies each to a CSV format. Returns a list of the 
# new filenames. 
def convert_all_NGVS_cat_to_csv(NGVS_list):
	new_filenames = []
	for NGVS_file in NGVS_list:
		new_filename = NGVS_file.replace('.cat', '.csv')
		convert_megacam_to_csv.make_csv_file_from_file_list([NGVS_file], new_filename)
		new_filenames.append(new_filename)

	return new_filenames
		


# Takes a list of NGVS files, writes each file to an equivalent csv file,
# then matches the csv files in sequential sets of two, saving an intermediate
# matched csv file at each step.
def match_all(NGVS_file_list):

	# Convert all NGVS files in list to CSV files.
	csv_filenames = convert_all_NGVS_cat_to_csv(NGVS_file_list)

	previous_matched_file = None

	for index, filename in enumerate(csv_filenames):
		with open(filename, 'w') as input_file:
			pass





	array_of_all_matches = None
	return array_of_all_matches

def test():
	
	file_list = ['NGVS-1+0.G.cat', 'NGVS-1+0.I2.cat']

	matched_array = match_all(file_list)	

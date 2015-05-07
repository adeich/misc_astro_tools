from astropy.coordinates import match_coordinates_sky
from astropy.coordinates import SkyCoord
from astropy import units as u
import numpy as np



# for explanation, see https://astropy.readthedocs.org/en/stable/coordinates/matchsep.html
# and https://astropy.readthedocs.org/en/stable/api/astropy.coordinates.match_coordinates_sky.html#astropy.coordinates.match_coordinates_sky



def match_coordinates(match_RA, match_DEC, catalog_RA, catalog_DEC):
	
	matchcoord = SkyCoord(ra=match_RA * u.degree, dec=match_DEC * u.degree)
	catalogcoord = SkyCoord(ra=catalog_RA * u.degree, 
		dec=catalog_DEC * u.degree)

	idx, sep2d, dist3d = match_coordinates_sky(matchcoord, catalogcoord)


	return idx, sep2d, dist3d




def get_RA_DEC_from_CSV(csv_filename, RA_column_name, DEC_column_name):
	recarray = np.recfromcsv(csv_filename)
	RA = recarray[RA_column_name]
	DEC = recarray[DEC_column_name]

	return RA, DEC




def main(csv_filename_match, csv_filename_catalog):
	
	match_RA, match_DEC = get_RA_DEC_from_CSV(csv_filename_match, 'alpha_j2000', 'delta_j2000')
	catalog_RA, catalog_DEC = get_RA_DEC_from_CSV(csv_filename_catalog, 'alpha_j2000',
		'delta_j2000')

	idx, sep2d, dist3d = match_coordinates(match_RA, match_DEC, catalog_RA, catalog_DEC)

	print 'number of match objects: {}'.format(len(match_RA))
	print 'number of catalog objects: {}'.format(len(catalog_RA))
	print 'shape(idx) = {}'.format(np.shape(idx))
	print 'mean, std of angular separation: {}, {}'.format(np.mean(sep2d), np.std(sep2d))
		


main('I2.csv', 'G.csv')
			

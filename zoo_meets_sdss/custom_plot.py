import numpy as np
import matplotlib.pyplot as plt
import sys, os
sys.path.append(os.path.split(os.getcwd())[0])
import make_thumbnail_webpage
import coord_match_NSA_GZoo


def write_csv(filename, rec_array):
	with open(filename, 'w') as f:
		f.write('{}\n'.format(','.join(rec_array.dtype.names)))
		for line in rec_array:
			f.write('{}\n'.format(','.join([str(i) for i in line])))
	print '{} written.'.format(filename)

def plot_zdist_vs_sersic(non_matches, matches):
	plt.scatter(non_matches['zdist'], non_matches['sersic_th50'], color='blue', label='match > {} arcsecond'.format(match_cutoff))
	plt.scatter(matches['zdist'], matches['sersic_th50'], marker='*', color='black', label='match < {} arcsecond'.format(match_cutoff))

	plt.xlabel('zdist')
	plt.ylabel('sersic_th50')
	plt.legend()
	plt.title('NSA+GZoo by match angular separation')

	plt.show()


def plot_ra_vs_dec(non_matches, matches):
	plt.scatter(non_matches['ra'], non_matches['dec'], color='blue', label='match > {} arcsecond'.format(match_cutoff))
	plt.scatter(matches['ra'], matches['dec'], marker='*', color='black', label='match < {} arcsecond'.format(match_cutoff))

	plt.xlabel('ra')
	plt.ylabel('dec')
	plt.legend()
	plt.title('NSA+GZoo by ra/dec')

	plt.show()

def plot_ra_vs_dec(non_matches, matches):
	plt.scatter(non_matches['ra'], non_matches['dec'], color='blue', label='match > {} arcsecond'.format(match_cutoff))
	plt.scatter(matches['ra'], matches['dec'], marker='*', color='black', label='match < {} arcsecond'.format(match_cutoff))

	plt.xlabel('ra')
	plt.ylabel('dec')
	plt.legend()
	plt.title('NSA+GZoo by ra/dec')

	plt.show()
	
def plot_all_ra_vs_dec(matches):
	nsa_recarray = np.recfromcsv('data_from_fits.csv')
	gzoo_recarray = np.recfromcsv('data_from_galaxy_zoo.csv')

	plt.scatter(gzoo_recarray['ra'], gzoo_recarray['dec'], color='black', label="GZoo objects (black)", s=0.25)
	plt.scatter(nsa_recarray['ra'], nsa_recarray['dec'], color='blue', label="NSA objects (blue)", s=0.25)
	plt.scatter(matches['ra'], matches['dec'], color='yellow', label="actual matches (yellow)", s=0.25)

	plt.xlabel('ra')
	plt.ylabel('dec')
	plt.legend()
	plt.title('NSA+GZoo by ra/dec')

	plt.show()


def plot_histogram_of_match_distances(sorted_on_match_distance):
	plt.hist(sorted_on_match_distance['deich_match_arcsec'], 100)
	plt.xlabel('match separation (arcsec)')
	plt.ylabel('N')
	plt.suptitle('Histogram of closest matches ')

	plt.show()	


def plot_ra_dec_diff(rec, title=None):
	plt.scatter(rec['ra'] - rec['ra_1'], rec['dec'] - rec['dec_1'], s=0.25)
	plt.scatter([0], [0], color='red', marker='+', s=300)
	plt.scatter(np.mean(rec['ra'] - rec['ra_1']), np.mean(rec['dec'] - rec['dec_1']), color='green', marker='+', s=300)
	if title:
		plt.suptitle(title)
	plt.xlabel('NSA_ra - GZoo_ra')
	plt.ylabel('NSA_dec - GZoo_dec')

	plt.show()



# returns array containing, for each object in NSA, index of closest object in GZoo;
# also respective angular separation. 
def match_coordinates():
 	
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
		dtype=[('index_into_GZoo', int),('DEICH_match_arcsec', float)])
	
	print '\tdone.'
	return nearest_GZoo_obj_pointers 


class catalog:
	def __init__(self, catalog_rec, ra_name, dec_name):
		self.catalog_rec = catalog_rec
		self.ra_name = ra_name
		self.dec_name = dec_name

	def match_single(self, ra, dec):
		nearest_catalog_obj_pointers = coord_match_NSA_GZoo.match_coordinates(
			catalog_ra=self.catalog_rec[self.ra_name], catalog_dec=self.catalog_rec[self.dec_name],
			match_ra = np.array([ra]), match_dec = np.array([dec]))
		return self.catalog_rec[nearest_catalog_obj_pointers['index_into_catalog']]



def make_catalogs():
	print 'reading NSA...'
	NSA_rec = np.recfromcsv('data_from_fits.csv')
	print '\t...done.'

	print 'reading GZoo...'
	GZoo_rec = np.recfromcsv('data_from_galaxy_zoo.csv')
	print '\t...done.'

	GZoo_catalog = catalog(GZoo_rec, 'ra', 'dec')
	NSA_catalog = catalog(NSA_rec, 'ra', 'dec')

	return GZoo_catalog, NSA_catalog 


def look_at_matches():

	match_cutoff = 10. 

	a = np.recfromcsv('combined.csv')
	sorted_on_match_distance = np.sort(a, order='deich_match_arcsec')

	non_matches = a[np.where(a['deich_match_arcsec'] > match_cutoff)]
	matches = a[np.where((a['deich_match_arcsec'] < match_cutoff))]
	real_matches = matches[np.where(matches['zdist'] < 0.03)]
	real_non_matches = non_matches[np.where(non_matches['zdist'] < 0.03)]
	best_100_matches = sorted_on_match_distance[:100]
	worst_100_matches = sorted_on_match_distance[-100:]

	print "total objects: {}".format(len(a))
	print "Matches with dist < 10 arcsec: {}".format(len(matches))
	print "non-matches: {}".format(len(non_matches))
	print "matches sans distant objects: {}".format(len(real_matches))
	print "non-matches sans distant objects: {}".format(len(real_non_matches))

	#write_csv('nonmatches.csv', real_non_matches)
	#make_thumbnail_webpage.make_thumbnail_webpage(worst_100_matches, 'far_matches.html')
	#make_thumbnail_webpage.make_thumbnail_webpage(best_100_matches, 'close_matches.html')
	#plot_zdist_vs_sersic(non_matches, matches)
	#plot_ra_vs_dec(non_matches, matches)
	#plot_all_ra_vs_dec()
 	#plot_histogram_of_match_distances(sorted_on_match_distance[np.where(sorted_on_match_distance['deich_match_arcsec'] < 1000.)])
	#plot_ra_dec_diff(a, 'All Objects')
	#plot_ra_dec_diff(matches, 'Objects with match distance < 10 arcsec')


#GZoo_cat, NSA_cat = make_catalogs()	

if __name__ == '__main__':
	GZoo_cat, NSA_cat = make_catalogs()	

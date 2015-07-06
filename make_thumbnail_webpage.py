import numpy as np
import xml.etree.ElementTree as ET
import xml.dom.minidom

# generate an html file for allowing visual inspection of thumbnails.
def make_thumbnail_webpage(rec_array, output_filename):

	def make_DR7_a_tag(ra, dec):
		thumbnailURL = """http://skyservice.pha.jhu.edu/DR7/ImgCutout/getjpeg.aspx?ra={}&dec={}&scale=0.40&width=120&height=120&opt=""".format(ra, dec)
		link = """http://skyserver.sdss.org/dr7/en/tools/chart/navi.asp?ra={}&dec={}""".format(ra, dec)
		a_tag = """<a href='{}'><img src='{}' width=120 height=120></a>""".format(link, thumbnailURL)
		return a_tag

	def make_td_tag(content_string, is_header=False):
		tag = None
		if not is_header:
			tag = '<td>{}</td>'.format(content_string)
		else:
			tag = '<th>{}</th>'.format(content_string)
		return tag 

	with open(output_filename, 'w') as f:
    # intro HTML.
		f.write("<html><head>")
		f.write('<script type="text/javascript" src="http://spg.ucolick.org/tablesorter/jquery-latest.js"></script>')
		f.write('<script type="text/javascript" src="http://spg.ucolick.org/tablesorter/jquery.tablesorter.js"></script>')
		f.write('<script type="text/javascript" >$(document).ready(function(){$("#myTable").tablesorter();}); </script>')
		f.write('<link rel="stylesheet" type="text/css" href="http://spg.ucolick.org/tablesorter/themes/blue/style.css">')
		f.write("</head>\n")
		f.write("Click on thumbnails to go to their DR7 Navigate page.<br>\n")
		f.write('<table border=1 cellspacing=2 cellpadding=0 id="myTable" class="tablesorter">\n') 

    # make header row.
		f.write('<thead><tr>')
		for column_name in ['Thumbnail'] + list(rec_array.dtype.names):
			f.write(make_td_tag(column_name, is_header=True)) 
		f.write('</tr></thead>\n')

    # copy contents line by line.
		f.write('<tbody>')
		for line in rec_array:
			f.write('<tr>')

      # Add thumbnail element.
			f.write(make_td_tag(make_DR7_a_tag(line['ra'], line['dec'])))

      # Add all fields from recarray.
			for field in line:
				f.write(make_td_tag(str(field)))
			f.write('</tr>\n')

    # Ending HTML.
		f.write("""</tbody></table></body></html>""")

		print "HTML document with thumbnails created: {}".format(output_filename)


# The future version of this function, using a proper xml constructor.
def make_thumbnail_webpage_future(rec_array, filename):

	def make_DR7_a_tag(ra, dec):
		thumbnailURL = """http://skyservice.pha.jhu.edu/DR7/ImgCutout/getjpeg.aspx?ra={}&dec={}&scale=0.40&width=120&height=120&opt=""".format(ra, dec)
		link = """http://skyserver.sdss.org/dr7/en/tools/chart/navi.asp?ra={}&dec={}""".format(ra, dec)
		a_tag = """<a href='{}'><img src='{}' width=120 height=120></a>""".format(link, thumbnailURL)
		return a_tag

	html_element = ET.Element('html')

	head_element = ET.SubElement(html_element, 'head')
	for script_url in ['https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js', 
		'https://rawgit.com/christianbach/tablesorter/master/jquery.tablesorter.min.js']:
		ET.SubElement(head_element, 'script', attrib={'src': script_url, 'type': 'text/javascript'})

	body_element = ET.SubElement(html_element, 'body')

	table_element = ET.SubElement(body_element, 'table', attrib={'class': 'tablesorter', 
		'id': 'myTable'})

	thead_element = ET.SubElement(table_element, 'thead')
	thead_tr_element = ET.SubElement(thead_element, 'tr')

	# Fill the header row.
	for column_name in ['Thumbnail'] + list(rec_array.dtype.names):
		temp_pointer = ET.SubElement(thead_tr_element, 'th')
		temp_pointer.text = column_name

	# Write the main contents.
	tbody_element = ET.SubElement(table_element, 'tbody')
	for line in rec_array:
		current_row_element = ET.SubElement(tbody_element, 'tr')
		temp_pointer = ET.SubElement(current_row_element, 'td')
		temp_pointer.text = 'hello'# make_DR7_a_tag(line['ra'], line['dec']) 
		for field in line:
			temp_pointer = ET.SubElement(current_row_element, 'td')
			temp_pointer.text = str(field)


	return ET.tostring(html_element)



if __name__ == "__main__":
	recarray = np.recfromcsv('combined.csv')[:50]
	#print xml.dom.minidom.parseString(generate_webpage_of_results2(recarray, None)).toprettyxml()
	make_thumbnail_webpage(recarray, 'test_webpage.html')

from macbethLookTransfer import *
from colormath.color_conversions import convert_color
from colormath.color_objects import sRGBColor, XYZColor



def check_weighted_dest_color():
	# print "Checking check_weighted_dest_color"
	cloud = import_pointcloud(source_file = "./img/wedge_dslr.tif",
							  dest_file = "./img/wedge_dslr.tif")
	cloud = filter_duplicate_source_points(cloud)
	steps = [0, 63, 127, 191, 255]
	for r in steps:
		for g in steps:
			for b in steps:
				c = sRGBColor(r, g, b, is_upscaled=True)
				c = convert_color(c, XYZColor)
				new_c = weighted_dest_color(cloud, c )
				out = convert_color(new_c, sRGBColor)
				nr, ng, nb = out.get_upscaled_value_tuple()
				assert nr == r
				assert ng == g
				assert nb == b
	# print "\tPassed."


def check_image_to_dest_no_dither():
	# print "Checking check_image_to_dest_no_dither"
	cloud = import_pointcloud(source_file = "./img/wedge_dslr.tif",
							  dest_file = "./img/wedge_dslr.tif")
	cloud = filter_duplicate_source_points(cloud)

	source_image = imread("./img/rgbcmybgw.tif")
	dest_image = image_to_dest(cloud, source_image, dither_error=False)

	for row_number in range(len(source_image)):
		for column_number in range(len(source_image[0])):
			for channel in range(len(source_image[0][0])):
				assert source_image[row_number][column_number][channel] == dest_image[row_number][column_number][channel]
	# print "\tPassed."


def check_image_to_dest_dither():
	# print "Checking check_image_to_dest_dither"
	cloud = import_pointcloud(source_file = "./img/wedge_dslr.tif",
							  dest_file = "./img/wedge_dslr.tif")
	cloud = filter_duplicate_source_points(cloud)

	source_image = imread("./img/rgbcmybgw.tif")
	dest_image = image_to_dest(cloud, source_image, dither_error=True)

	for row_number in range(len(source_image)):
		for column_number in range(len(source_image[0])):
			for channel in range(len(source_image[0][0])):
				assert source_image[row_number][column_number][channel] == dest_image[row_number][column_number][channel]
	# print "\tPassed."




def run():
	check_weighted_dest_color()
	check_image_to_dest_no_dither()
	check_image_to_dest_dither()
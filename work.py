import numpy as np
from scipy.misc import imread
import matplotlib.pyplot as plt
from colormath.color_conversions import convert_color
from colormath.color_objects import sRGBColor, xyYColor
from pprint import pprint
import math

macbeth_patch_names = ["Dark skin", "Light skin", "Blue sky", "Foliage", "Blue flower", "Bluish green",
					   "Orange", "Purplish blue", "Moderate red", "Purple", "Yellow green", "Orange yellow",
					   "Blue", "Green", "Red", "Yellow", "Magenta", "Cyan",
					   "White", "Neutral 8", "Neutral 6.5", "Neutral 5", "Neutral 3.5", "Black"]

def import_pointcloud(source_file='', dest_file=''):

	source_image = imread(source_file)
	dest_image = imread(dest_file)
	cloud = []
	# assuming the wedge images contain 7 exposure steps
	source_levels = np.hsplit(source_image, 8)
	dest_levels = np.hsplit(dest_image, 8)
	for level_num in range(len(source_levels)):
		source_level = source_levels[level_num]
		dest_level = dest_levels[level_num]
		pixel_number = 0
		for row_number in range(len(source_level)):
			source_row = source_level[row_number]
			dest_row = dest_level[row_number]
			for column_number in range(len(source_row)):
				source_pixel = source_row[column_number]
				dest_pixel = dest_row[column_number]
				source_r = source_pixel[0]
				source_g = source_pixel[1]
				source_b = source_pixel[2]
				dest_r = dest_pixel[0]
				dest_g = dest_pixel[1]
				dest_b = dest_pixel[2]
				source_srgb = sRGBColor(source_r, source_g, source_b, is_upscaled=True)
				dest_srgb = sRGBColor(dest_r, dest_g, dest_b, is_upscaled=True)
				source_xyy = convert_color(source_srgb, xyYColor)
				dest_xyy = convert_color(dest_srgb, xyYColor)
				cloud.append({'level': level_num,
									 'color name': macbeth_patch_names[pixel_number],
									 'source color': source_xyy,
									 'dest color': dest_xyy })
				pixel_number += 1
	return cloud

def filter_pointcloud(pointcloud, levels=[], color_names=[]):

	filtered_cloud_levels = []
	if levels != []:
		for point in pointcloud:
			if point['level'] in levels:
				filtered_cloud_levels.append(point)
	else:
		filtered_cloud_levels = pointcloud
	filtered_cloud_colors = []
	if color_names != []:
		for point in filtered_cloud_levels:
			if point['color name'] in color_names:
				filtered_cloud_colors.append(point)
	else:
		filtered_cloud_colors = filtered_cloud_levels
	return filtered_cloud_colors

def filter_duplicate_source_points(pointcloud):

	filtered_cloud = []
	for i, point in enumerate(pointcloud):
		other_points = [x for j,x in enumerate(pointcloud) if j != i]
		duplicate = False
		for other_point in other_points:
			if point['source color'].get_value_tuple() == other_point['source color'].get_value_tuple():
				duplicate = True
		if not duplicate:
			filtered_cloud.append(point)

	return filtered_cloud

def distance(one_color, other_color):
	# Colors are colormath.color_objects.

	one_x, one_y, one_z = one_color.get_value_tuple()
	other_x, other_y, other_z = other_color.get_value_tuple()
	dist = math.sqrt(pow((one_x - other_x), 2) +
				     pow((one_y - other_y), 2) +
		   			 pow((one_z - other_z), 2))
	return dist

def main():
	# source = imread("./img/wedge_dslr.tif")
	# dest = imread("./img/wedge_instax.tif")

	#print source.dtype, source.shape


	# source_greys = source[3:4, 0:48]
	# source_levels = np.hsplit(source, 8)
	#plt.imshow(source, interpolation='nearest')

	cloud = import_pointcloud(source_file = "./img/wedge_dslr.tif",
							  dest_file = "./img/wedge_instax.tif")

	selected_colors = ['Red', 'Green', 'Blue', 'Cyan', 'Magenta', 'Yellow', 'Neutral 5', 'Black', 'White']
	selected_colors = ['Black', 'White', 'Neutral 5']
	selected_cloud = filter_pointcloud(cloud,  color_names=selected_colors)
	dedup = filter_duplicate_source_points(selected_cloud)
	for point in dedup:
		print point['level'], '\t', point['color name']

	# for point in dest_cloud:
	# 	if point['level'] == 0:
	# 		print point['color']


	# print source[0][0]
	# srgb = sRGBColor(source[0][0][0], source[0][0][2], source[0][0][2], is_upscaled=True)
	# print srgb
	# xyy = convert_color(srgb, xyYColor)
	# print xyy

	# 	plt.subplot(3, 3, i+1)
	# 	plt.imshow(level, interpolation='nearest')
	# plt.show()



	# s = sorted(source_greys)

	# for i in range(len(source_greys)):
	# 	print "starting a line"
	# 	line = source_greys[i]
	# 	for j in range(len(line)):
	# 		print source_greys[i][j], " ", s[i][j]


if __name__ == "__main__":
    main()


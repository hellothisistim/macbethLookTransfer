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

def import_pointcloud(filename):

	image = imread(filename)
	cloud = []
	# assuming the source image contains 7 exposure steps
	levels = np.hsplit(image, 8)
	for i, level in enumerate(levels):
		pixel_number = 0
		for row in level:
			for pixel in row:
				r = pixel[0]
				g = pixel[1]
				b = pixel[2]
				srgb = sRGBColor(r, g, b, is_upscaled=True)
				xyy = convert_color(srgb, xyYColor)
				cloud.append({'level': i,
									 'color name': macbeth_patch_names[pixel_number],
									 'color': xyy})
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



def distance(one_color, other_color):

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

	source_cloud = import_pointcloud("./img/wedge_dslr.tif")
	dest_cloud = import_pointcloud("./img/wedge_instax.tif")

	# pprint([p for p in source_cloud if p['level'] == 3])
	# pprint([p for p in dest_cloud if p['level'] == 3])

	selected_colors = ['Red', 'Green', 'Blue', 'Cyan', 'Magenta', 'Yellow', 'Grey 5']
	rgbcmyg_cloud = filter_pointcloud(source_cloud,  color_names=selected_colors)

	for i, point in enumerate(rgbcmyg_cloud):
		closest_dist = 10000
		closest_point = {}
		select_levels = [x for j,x in enumerate(dest_cloud) if x['level'] > 1 and x['level'] < 6 ]
		other_points = [x for j,x in enumerate(select_levels) if j!=i]
		for other_point in other_points:
			dist = distance(point['color'], other_point['color'])
			if dist < closest_dist:
				closest_dist = dist
				closest_point = other_point
		print closest_dist, '\t', point['color name'], point['level'], closest_point['color name'], closest_point['level']

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


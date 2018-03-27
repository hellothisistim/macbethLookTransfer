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

def closest(cloud, color, mode='source color'):
	# cloud is the pointcloud list, color is colormath.color_objects
	# mode is either "source color" or "dest color"

	smallest_distance_so_far = 10000
	for point in cloud:
		d = distance(color, point[mode])
		if d < smallest_distance_so_far:
			smallest_distance_so_far = d
			closest = point
	return closest

def octant_split(pointcloud, color):
	# Divide the pointcloud into octants around the given color, 
	# which is an instance from colormath.color_objects
	# Do not return empty octants.

	labeled_points = []
	color_tuple = color.get_value_tuple()
	for point in pointcloud:
		labeled_point = {'point': point}
		point_tuple = point['source color'].get_value_tuple()
		if point_tuple[0] >= color_tuple[0]:
			labeled_point['x_dir'] = '+'
		else:
			labeled_point['x_dir'] = '-'
		if point_tuple[1] >= color_tuple[1]:
			labeled_point['y_dir'] = '+'
		else:
			labeled_point['y_dir'] = '-'
		if point_tuple[2] >= color_tuple[2]:
			labeled_point['z_dir'] = '+'
		else:
			labeled_point['z_dir'] = '-'
		labeled_points.append(labeled_point)

	octants = [('+', '+', '+'), ('-', '+', '+'), ('-', '-', '+'), 
			   ('+', '-', '+'), ('+', '+', '-'), ('-', '+', '-'), 
			   ('-', '-', '-'), ('+', '-', '-'), ]
	split_octants = []
	for octant in octants:
		split_octants.append([labeled_point['point'] for labeled_point in labeled_points if (labeled_point['x_dir'], labeled_point['y_dir'], labeled_point['z_dir']) == octant])
	# remove empty octants
	out = tuple( [octant for octant in split_octants if octant != []] )

	return out

def closest_in_each_octant(pointcloud, color):

	octants = octant_split(pointcloud, color)
	out = [closest(i, color) for i in octants]
	return tuple(out)

def weighted_dest_color(pointcloud, color):

	nearest_points = closest_in_each_octant(pointcloud, color)
	total_weight = 0
	total_vector = (0, 0, 0)
	for point in nearest_points:
		total_weight += (1 / distance(color, point['source color']))
	for i, point in enumerate(nearest_points):
		# calculate vector from source color to destination color
		source = point['source color'].get_value_tuple()
		dest = point['dest color'].get_value_tuple()
		vector = np.subtract(dest, source)
		# weight vector and normalize
		weight = (1 / distance(color, point['source color'])) / total_weight
		# print 'distance:', distance(color, point['source color']), 'inverted:', 1/distance(color, point['source color']), 'weight:', weight
		# print vector
		weighted_vector = [ n * weight for n in vector]
		# print weighted_vector
		total_vector = np.add(total_vector, weighted_vector)
	# print total_vector
	dest_color = np.add(color.get_value_tuple(), total_vector)

	return xyYColor(dest_color[0], dest_color[1], dest_color[2] )	


def main():

	cloud = import_pointcloud(source_file = "./img/wedge_dslr.tif",
							  dest_file = "./img/wedge_instax.tif")

	source_image = imread("./img/KodakMarcie.jpg")

	selected_colors = ['Red', 'Green', 'Blue', 'Cyan', 'Magenta', 'Yellow', 'Neutral 5']
	selected_cloud = filter_pointcloud(cloud,  color_names=selected_colors)
	dedup = filter_duplicate_source_points(selected_cloud)

	target_srgb = sRGBColor(127, 127, 127, is_upscaled=True)
	target = convert_color(target_srgb, xyYColor)
	print 'target:', target
	# pprint( closest_in_each_octant(dedup, target) )
	print 'dest:', weighted_dest_color(dedup, target)


if __name__ == "__main__":
    main()


import numpy as np
from scipy.misc import imread, imsave
import matplotlib.pyplot as plt
from colormath.color_conversions import convert_color
from colormath.color_objects import sRGBColor, XYZColor
from pprint import pprint
import math
from copy import deepcopy

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
				source_xyz = convert_color(source_srgb, XYZColor)
				dest_xyz = convert_color(dest_srgb, XYZColor)
				cloud.append({'level': level_num,
									 'color name': macbeth_patch_names[pixel_number],
									 'source color': source_xyz,
									 'dest color': dest_xyz })
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

def filter_duplicate_source_points_dumb(pointcloud):

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

def pointcloud_contains_source_duplicates(pointcloud):
	for i, point in enumerate(pointcloud):
		other_points = [x for j,x in enumerate(pointcloud) if j != i]
		for other_point in other_points:
			if point['source color'].get_value_tuple() == other_point['source color'].get_value_tuple():
				return True
	return False

def filter_duplicate_source_points_per_level(pointcloud):
	# Removes the entire level if there are duplicate source colors in the level.
	filtered_cloud = []
	levels = []
	for point in pointcloud:
		if point['level'] not in levels:
			levels.append(point['level'])
	for i, level in enumerate(levels):
		these_points = filter_pointcloud(pointcloud, levels=[i])
		if not pointcloud_contains_source_duplicates(these_points):
			for point in these_points:
				filtered_cloud.append(point)
		else:
			# print 'dropping level', i
			pass
	return filtered_cloud

def filter_duplicate_source_points_smart(pointcloud):
	filtered_cloud = filter_duplicate_source_points_per_level(pointcloud)
	filtered_cloud = filter_duplicate_source_points_dumb(filtered_cloud)
	return filtered_cloud

def filter_duplicate_source_points(pointcloud):
	return filter_duplicate_source_points_smart(pointcloud)

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
		d = distance(color, point['source color'])
		if d == 0:
			return point['source color']
		else:
			total_weight += (1 / d)
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
	typ = type(color)
	return typ(dest_color[0], dest_color[1], dest_color[2], observer=color.observer, illuminant=color.illuminant)


def image_to_dest(pointcloud, image, dither_error=True):

	dest_image = np.zeros(image.shape, dtype="uint8")
	error_collection = np.zeros(image.shape)

	for row_number in range(len(image)):
		# print 'row:', row_number
		for column_number in range(len(image[0])):
				raw_rgb = image[row_number][column_number]
				srgb = sRGBColor(raw_rgb[0], raw_rgb[1], raw_rgb[2], is_upscaled=True)
				xyz = convert_color(srgb, XYZColor)
				dest_xyz = weighted_dest_color(pointcloud, xyz)
				dest_srgb = convert_color(dest_xyz, sRGBColor)
				if dither_error:
					r,g,b = np.add(dest_srgb.get_value_tuple(), error_collection[row_number][column_number])
				else:
					r,g,b = dest_srgb.get_value_tuple()
				# print 'xxx', dest_srgb, r, g, b
				# print dest_srgb.get_value_tuple()
				# print error_collection[row_number][column_number]
				upscaled_srgb = sRGBColor(r, g, b).get_upscaled_value_tuple()
				dest_image[row_number][column_number] = upscaled_srgb
				if dither_error:
					rounded_srgb = sRGBColor(upscaled_srgb[0], upscaled_srgb[1], upscaled_srgb[2], is_upscaled=True)
					rounding_error = np.subtract(dest_srgb.get_value_tuple(), rounded_srgb.get_value_tuple())
					# do Floyd-Steinberg dither
					# over
					try:
						error_collection[row_number][column_number + 1] += rounding_error * 7 / 16
					except IndexError:
						pass # It's the end of the line, don't worry about it.
					# down and back
					try:
						error_collection[row_number + 1][column_number - 1] += rounding_error * 3 / 16
					except IndexError:
						pass
					# down
					try:
						error_collection[row_number + 1][column_number] += rounding_error * 5 / 16
					except IndexError:
						pass
					# down and over
					try:
						error_collection[row_number + 1][column_number + 1] += rounding_error * 1 / 16
					except IndexError:
						pass
				dest_image[row_number][column_number] = upscaled_srgb
				# print dest_image[row_number][column_number], raw_rgb, upscaled_srgb

	# print "error collection:\n", error_collection
	return dest_image




if __name__ == "__main__":

	import checks
	checks.run()

	cloud = import_pointcloud(source_file = "./img/wedge_dslr.tif",
							  dest_file = "./img/wedge_instax.tif")
	# cloud = import_pointcloud(source_file = "./img/wedge_dslr.tif",
	# 						  dest_file = "./img/wedge_dslr.tif")

	selected_colors = ['Red', 'Green', 'Blue', 'Cyan', 'Magenta', 'Yellow', 'Neutral 5']
	# selected_colors = ["White", "Neutral 8", "Neutral 6.5", "Neutral 5", "Neutral 3.5", "Black"]
	# selected_colors = macbeth_patch_names
	selected_cloud = filter_pointcloud(cloud,  color_names=selected_colors)
	dedup = filter_duplicate_source_points(selected_cloud)



	source_image = imread("./img/lego.jpg")
	dest_image = image_to_dest(dedup, source_image, dither_error=True)

	cloud = import_pointcloud(source_file = "./img/wedge_dslr.tif",
							  dest_file = "./img/wedge_instax-tweaked2.tif")
	dedup = filter_duplicate_source_points(cloud)
	dest_two = image_to_dest(dedup, source_image, dither_error=True)

	# imsave("./out.jpg", dest_image)

	plt.figure(1)
	plt.subplot(221)
	plt.imshow(source_image, interpolation='nearest')
	plt.title('original')
	plt.subplot(222)
	plt.imshow(dest_image, interpolation='nearest')
	plt.title('wedge-instax')
	plt.subplot(223)
	plt.imshow(dest_two, interpolation='nearest')
	plt.title('wedge-instax-tweaked2')
	plt.subplot(224)

	cloud = import_pointcloud(source_file = "./img/wedge_dslr.tif",
							  dest_file = "./img/wedge_dslr.tif")
	dedup = filter_duplicate_source_points(cloud)
	dest_two = image_to_dest(dedup, source_image, dither_error=True)

	plt.imshow(dest_two, interpolation='nearest')
	plt.title('wedge_dslr')
	plt.show()



import numpy as np
from scipy.misc import imread
import matplotlib.pyplot as plt
from colormath.color_conversions import convert_color
from colormath.color_objects import sRGBColor, xyYColor
from pprint import pprint

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


def main():
	# source = imread("./img/wedge_dslr.tif")
	# dest = imread("./img/wedge_instax.tif")

	#print source.dtype, source.shape


	# source_greys = source[3:4, 0:48]
	# source_levels = np.hsplit(source, 8)
	#plt.imshow(source, interpolation='nearest')

	source_cloud = import_pointcloud("./img/wedge_dslr.tif")
	dest_cloud = import_pointcloud("./img/wedge_instax.tif")

	pprint([p for p in source_cloud if p['level'] == 3])
	pprint([p for p in dest_cloud if p['level'] == 3])

	#print source_cloud[0]['color']




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


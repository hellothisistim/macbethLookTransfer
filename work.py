import numpy as np
from scipy.misc import imread
import matplotlib.pyplot as plt

source = imread("./img/wedge_dslr.tif")
dest = imread("./img/wedge_instax.tif")

print source.dtype, source.shape


source_greys = source[3:4, 0:48]

# plt.imshow(source_greys, interpolation='nearest')
# plt.show()


s = sorted(source_greys)

for i in range(len(source_greys)):
	print "starting a line"
	line = source_greys[i]
	for j in range(len(line)):
		print source_greys[i][j], " ", s[i][j]



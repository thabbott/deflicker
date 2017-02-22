"""
deflicker.py
------------
Remove flicker from a series of images.

This scripts reads images from a specified directory to determine an RGB
"timeseries", smooths the RGB timeseries with a square filter of specified
width, and either outputs plots of the smoothed and unsmoothed RGB timeseries
or adjusts the RGB values of each image such that their RGB values match the
smoothed values.

To use this script, run ``python deflicker.py <directory> <width>
[options]``. ``<directory>`` should specify a path to a folder than contains
the image files that are to the deflickered. The image names must contain
numbers somewhere, and the images will included in the timeseries in ascending
numerical order. <width> specified the width (in images) of the square filter
used the smooth the image values. Other options include
    ``--plot <file>``:
        do not output images with adjusted means; instead, print a plot
        of the RGB timeseries before and after smoothing to a PNG image in
        ``<file>``. If ``<file>`` already exists, it may be overwritten.
    ``--adjust <output>``:
        output images with adjusted means in the directory specified by
        ``<output>``. If the directory is the same as ``<directory>``, the
        smoothing is done in-place and the input files are overwritten.

.. moduleauthor Tristan Abbott
"""

from libdeflicker import meanRGB, squareFilter, relaxToMean, toIntColor
import os
import re
import sys
from PIL import Image
from matplotlib import pyplot as plt
import numpy as np

if __name__ == "__main__":

    # Process input arguments
    if len(sys.argv) < 3:
        print 'Usage: python deflicker.py <directory> <width> [..]'
        exit(0)
    loc = sys.argv[1]
    w = int(sys.argv[2])
    __plot = False
    __adjust = False

    for ii in range(3, len(sys.argv)):
        a = sys.argv[ii]
        if a == '--plot':
            __plot = True
            __file = sys.argv[ii+1]
        elif a == '--adjust':
            __adjust = True
            __output = sys.argv[ii+1]

    # Just stop if not told to do anything
    if not (__plot or __adjust):
        print 'Exiting without doing anything'
        exit(0)

	# Get list of image names in order
    loc = sys.argv[1]
    f = os.listdir(loc)
    n = []
    ii = 0
    while ii < len(f):
        match = re.search('\d+', f[ii])
        if match is not None:
            n.append(int(match.group(0)))
            ii += 1
        else:
            f.pop(ii)
    n = np.array(n)
    i = np.argsort(n)
    f = [f[ii] for ii in i]

    # Load images and calculate smoothed RGB curves
    print 'Calculating smoothed sequence'
    n = len(f)
    rgb = np.zeros((n, 3))
    ii = 0
    for ff in f:
        img = np.asarray(Image.open('%s/%s' % (loc, ff))) / 255.
        rgb[ii,:] = meanRGB(img)
        ii += 1

    # Filter series
    rgbi = np.zeros(rgb.shape)
    for ii in range(0,3):
        rgbi[:,ii] = squareFilter(rgb[:,ii], w)

    # Print initial and filtered series
    if __plot:
        print 'Plotting smoothed and unsmoothed sequences in %s' % __file
        plt.subplot(1, 2, 1)
        plt.plot(rgb[:,0], 'r', rgb[:,1], 'g', rgb[:,2], 'b')
        plt.title('Unfiltered RGB sequence')
        plt.subplot(1, 2, 2)
        plt.plot(rgbi[:,0], 'r', rgbi[:,1], 'g', rgbi[:,2], 'b')
        plt.title('Filtered RGB sequence (w = %d)' % w)
        plt.savefig(__file)

    # Process images sequentially
    if __adjust:
        print 'Processing images'
        ii = 0
        for ff in f:
            img = np.asarray(Image.open('%s/%s' % (loc, ff))) / 255.
            relaxToMean(img, rgbi[ii,:])
            jpg = Image.fromarray(toIntColor(img))
            jpg.save('%s/%s' % (__output, ff))
            ii += 1

    print 'Finished'

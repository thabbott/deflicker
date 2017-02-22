# deflicker

Remove flicker from a series of images. This is useful if you want to combine a
series of images into a timelapse video.

This script reads images from a specified directory to determine an RGB
"timeseries", smooths the RGB timeseries with a square filter of specified
width, and either outputs plots of the smoothed and unsmoothed RGB timeseries
or adjusts the RGB values of each image such that their RGB values match the
smoothed values.

To use this script, run ``python deflicker.py <directory> <width>
[options]``. ``<directory>`` should specify a path to a folder than contains
the image files that are to the deflickered. The image names must contain
numbers somewhere, and the images will included in the timeseries in ascending
numerical order. ``<width>`` specifies the width (in images) of the square filter
used the smooth the image values. Other options include
    
``--plot <file>``:
        print a plot of the RGB timeseries before and after smoothing to a PNG image in
        ``<file>``. If ``<file>`` already exists, it may be overwritten.
    
``--adjust <output>``:
        output images with adjusted means in the directory specified by
        ``<output>``. If the directory is the same as ``<directory>``, the
        smoothing is done in-place and the input files are overwritten.

### Example
Assume images are in a directory "/data/pictures/source", you want to put
deflickered images in "/data/pictures/deflicker", and you want to plot the
RGB timeseries before and after smoothing in "/data/pictures/edits/df.png". You decide
that a filter with width 25 should be smooth but not too smooth. You should
run

```
$ python deflicker.py /data/pictures/source 25 --plot /data/pictures/edits/df.png --adjust /data/pictures/deflicker
```

### Dependencies
All the dependencies in this script should be satisfied if you install
[anaconda](https://www.continuum.io/downloads).

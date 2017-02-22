"""
libdeflicker.py
---------------
Library routines for image deflickering.

.. moduleauthor Tristan Abbott
"""

import numpy as np
from scipy import signal

def squareFilter(sig, w):
    """
    squareFilter(sig, w)
    --------------------
    Smooth a signal with a square filter.

    This function is just a wrapper for scipy.signal.convolve with a kernel
    given by ``np.ones(w)/w``.

    Parameters:
        sig: np.array
            Unsmoothed signal
        w: int
            Width of the filter

    Returns:
        np.array
            Smoothed signal
    """
    # Create filter
    win = np.ones(w)
    # Pad input
    sigp = np.concatenate(([np.tile(sig[0], w/2), sig,
        np.tile(sig[-1], w/2)]))
    # Filter
    return signal.convolve(sigp, win, mode =
               'same')[w/2:-w/2+1] / np.sum(win)

# Compute image-mean RGB values
def meanRGB(img, ii = -1):
    """
    meanRGB(img, ii = -1)
    ---------------------
    Compute image-mean RGB values.

    This function takes an np.array representation of an image (x and y in the
    first two dimensions and RGB values along the third dimension) and computes
    the image-average R,G, and B values.

    Parameters:
        img: np.array
            Array image representation. The first two dimensions should
            represent pixel positions, and each position in the third dimension
            can represent a particular pixel attribute, e.g. an R, G, or B
            value; an H, S, or V value, etc.
        ii: int, optional
            Specify a slice of the third dimension to average over. If a
            particular slice is specified, the function returns a scalar;
            otherwise, it returns an average over each slice in the third
            dimension of the input image. ``ii`` must be between ``0`` and
            ``img.shape[2]``, inclusive.

    Returns:
        np.array
            Average over the specified slice, if ``ii`` is given, or a 1D array
            of average over the first two dimensions for each slice in the
            third dimension.
    """
    if ii < 0:
        return np.array([np.mean(img[:,:,i]) for i in range(0,img.shape[2])])
    else:
        return np.mean(img[:,:,ii])

# Adjust pixel-by-pixel RGB values to converge to correct mean 
# by multiplying them by a uniform value.
def relaxToMean(img, rgb):
    """
    relaxToMean(img, rgb)
    ---------------------
    Uniformly adjust pixel-by-pixel attributes so their mean becomes a
    specified value.

    The adjustment is done by multiplying pixel attributes by a scaling factor
    that is unique to the attribute but uniform over all the pixels in the
    image. This function assumes that each
    attribute is described by a floating point number between 0 and 1,
    inclusive, and it will stop individual pixels from moving outside this range
    while others are being scaled.

    Parameters:
        img: np.array
            Array image representation. The first two dimensions should
            represent pixel positions, and each position in the third dimension
            can represent a particular pixel attribute, e.g. an R, G, or B
            value; an H, S, or V value, etc.
        rgb: np.array
            Desired image-mean values for each attribute included in ``img``.
            The linear indices of the values in this array should map in order
            to the attributes in the third dimension of ``img``.

    Returns:
        np.array
            ``img`` with each attribute multiplied by a factor (unique to the
            attribute but the same for that attribute in every pixel in the
            image) such that the image mean of that attribute is as specified
            in ``rgb``.

    """
    rgbi = meanRGB(img)
    fac = np.array([2. if i else 0.5 for i in rgbi < rgb])

    # Relax toward mean
    for ii in range(0,3):

        # Repeat until converged to mean
        while not np.isclose(rgbi[ii], rgb[ii]):

            # Compute ratio
            r = rgb[ii] / rgbi[ii]
            # Relax image
            img[:,:,ii] = np.minimum(1., img[:,:,ii] * r)
            # Update average
            rgbi[ii] = meanRGB(img, ii)

# Convert floating point colors to integer colors
def toIntColor(img, t = np.uint8):
    """
    toIntColor(img, t = np.uint8)
    -----------------------------
    Convert floating-point attributes to other types.

    This function takes an image with floating-point [0,1] representations of
    attributes and returns an near-equivalent image with attributes represented
    by a different type. It does so by scaling the floating point attributes by
    the maximum value representable by the new type and then converting the
    scaled floating point value to the new type (with rounding, if required).

    Parameters:
        img: np.array
            Array image representation. The first two dimensions should
            represent pixel positions, and each position in the third dimension
            can represent a particular pixel attribute, e.g. an R, G, or B
            value; an H, S, or V value, etc. The attributes must be represented
            as [0,1] floating point values.
        t: type, optional
            Type used to represent attributes in the new image. By default, the
            type is an unsigned 8 bit integer (``np.uint8``).
    Returns:
        np.array(dtype = t)
            Representation of the attributes of ``img`` using the type
            specified by ``t``.
    """
    scale = np.iinfo(t).max
    return np.round(img * scale).astype(t)

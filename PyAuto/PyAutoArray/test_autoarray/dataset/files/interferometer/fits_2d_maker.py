from astropy.io import fits
import numpy as np
from os import path

file_path = path.join(
    "{}".format(path.dirname(path.realpath(__file__))), "files", "array"
)

array = np.array([[1.0, 1.0, 1.0], [1.0, 2.0, 1.0], [1.0, 1.0, 1.0]])

fits.writeto(data=array, filename=path.join(file_path, "3x3_ones_central_two.fits"))
stop

array1 = np.ones((3, 3))
array2 = 2.0 * np.ones((3, 3))
array3 = 3.0 * np.ones((3, 3))
array4 = 4.0 * np.ones((3, 3))
array5 = 5.0 * np.ones((3, 3))
array6 = 6.0 * np.ones((3, 3))
array7 = 7.0 * np.ones((3, 3))
array8 = 8.0 * np.ones((3, 3))

fits.writeto(data=array2, filename=path.join(file_path, "3x3_twos.fits"))
fits.writeto(data=array3, filename=path.join(file_path, "3x3_threes.fits"))
fits.writeto(data=array4, filename=path.join(file_path, "3x3_fours.fits"))
fits.writeto(data=array5, filename=path.join(file_path, "3x3_fives.fits"))
fits.writeto(data=array6, filename=path.join(file_path, "3x3_sixes.fits"))
fits.writeto(data=array7, filename=path.join(file_path, "3x3_sevens.fits"))
fits.writeto(data=array8, filename=path.join(file_path, "3x3_eights.fits"))

hdu_list = fits.HDUList()
hdu_list.append(fits.ImageHDU(array1))
hdu_list.append(fits.ImageHDU(array2))
hdu_list.append(fits.ImageHDU(array3))
hdu_list.append(fits.ImageHDU(array4))
hdu_list.append(fits.ImageHDU(array5))
hdu_list.append(fits.ImageHDU(array6))
hdu_list.append(fits.ImageHDU(array7))
hdu_list.append(fits.ImageHDU(array8))

hdu_list.writeto(path.join(file_path, "3x3_multiple_hdu.fits"))

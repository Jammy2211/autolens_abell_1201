from os import path
import sys


""" AUTOLENS + DATA SETUP """
import autofit as af
import autolens as al


"""Setup the data based on the dataset folder structure."""

pixel_scales = 0.04

image = al.Array2D.from_fits(
    file_path="lens_subtracted_f390w.fits", pixel_scales=pixel_scales
)

image = image.resized_from((421, 421))

image.output_to_fits(file_path=path.join("dataset", "image_no_lens_light_padded.fits"))

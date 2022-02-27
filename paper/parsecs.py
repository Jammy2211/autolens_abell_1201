"""
Einstein Radii and Mass
=======================

This is a simple script for computing the Einstein Radii and Mass given known input parameters.

For errors, you`ll need to use the aggregator (autolens_workspace -> aggregator).
"""
# %matplotlib inline
# from pyprojroot import here
# workspace_path = str(here())
# %cd $workspace_path
# print(f"Working Directory has been set to `{workspace_path}`")

import autolens as al
from astropy import cosmology as cosmo

kpc_per_arcsec = al.util.cosmology.kpc_per_arcsec_from(
    redshift=0.169, cosmology=cosmo.Planck15
)

print(kpc_per_arcsec)

print(0.04 * kpc_per_arcsec)

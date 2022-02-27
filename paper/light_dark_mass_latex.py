from autoconf import conf
import autofit as af
import autolens as al
import autolens.plot as aplt

import numpy as np
from matplotlib.patches import Circle
import os
from os import path
import warnings

warnings.filterwarnings("ignore")

"""
__Database + Paths__
"""
workspace_path = os.getcwd()

config_path = path.join(workspace_path, "config")
conf.instance.push(new_path=config_path)

output_path = path.join(workspace_path, "output")

agg = af.Aggregator.from_database(
    filename="rjlens_no_lens_light.sqlite", completed_only=False
)

waveband = "f390w"
# waveband = "f814w"

agg = agg.order_by(agg.search.path_prefix)

"""
__Query__
"""
search_name = "mass_light_dark[1]_light[fixed]_mass[light_dark]_source_grad__stochastic"

# bulge_cls = al.mp.EllSersicRadialGradient
# disk_cls = al.mp.EllSersicRadialGradient
# envelope_cls = al.mp.EllSersicRadialGradient
# smbh_cls = None
# prefix = "x3 Sersic & "
#
# agg_query = agg.query(agg.search.name == search_name)
# agg_query = agg_query.query(agg_query.search.unique_tag == waveband)
# agg_query = agg_query.query(agg_query.model.galaxies.lens.bulge == bulge_cls)
# agg_query = agg_query.query(agg_query.model.galaxies.lens.disk == disk_cls)
# agg_query = agg_query.query(agg_query.model.galaxies.lens.envelope == envelope_cls)
# agg_query = agg_query.query(agg_query.model.galaxies.lens.smbh == smbh_cls)
#
# search_name = "mass_light_dark[1]_light[fixed]_mass[light_dark]_source_grad__stochastic"
#
# bulge_cls = al.mp.EllSersicRadialGradient
# disk_cls = al.mp.EllSersicRadialGradient
# envelope_cls = None
# smbh_cls = None
# prefix = "x2 Sersic & "
#
# agg_query = agg.query(agg.search.name == search_name)
# agg_query = agg_query.query(agg_query.search.unique_tag == waveband)
# agg_query = agg_query.query(agg_query.model.galaxies.lens.bulge == bulge_cls)
# agg_query = agg_query.query(agg_query.model.galaxies.lens.disk == disk_cls)
# agg_query = agg_query.query(agg_query.model.galaxies.lens.envelope == envelope_cls)
# agg_query = agg_query.query(agg_query.model.galaxies.lens.smbh == smbh_cls)
#
# search_name = "mass_light_dark[1]_light[fixed]_mass[light_dark]_source_grad_smbh__stochastic"
#
# bulge_cls = al.mp.EllSersicRadialGradient
# disk_cls = al.mp.EllSersicRadialGradient
# envelope_cls = al.mp.EllSersicRadialGradient
# smbh_cls = al.mp.PointMass
# prefix = "x3 Sersic + SMBH & "
#
# agg_query = agg.query(agg.search.name == search_name)
# agg_query = agg_query.query(agg_query.search.unique_tag == waveband)
# agg_query = agg_query.query(agg_query.model.galaxies.lens.bulge == bulge_cls)
# agg_query = agg_query.query(agg_query.model.galaxies.lens.disk == disk_cls)
# agg_query = agg_query.query(agg_query.model.galaxies.lens.envelope == envelope_cls)
# agg_query = agg_query.query(agg_query.model.galaxies.lens.smbh == smbh_cls)

search_name = (
    "mass_light_dark[1]_light[fixed]_mass[light_dark]_source_grad_smbh__stochastic"
)

bulge_cls = al.mp.EllSersicRadialGradient
disk_cls = al.mp.EllSersicRadialGradient
envelope_cls = None
smbh_cls = al.mp.PointMass
prefix = "x2 Sersic + SMBH & "

agg_query = agg.query(agg.search.name == search_name)
agg_query = agg_query.query(agg_query.search.unique_tag == waveband)
agg_query = agg_query.query(agg_query.model.galaxies.lens.bulge == bulge_cls)
agg_query = agg_query.query(agg_query.model.galaxies.lens.disk == disk_cls)
agg_query = agg_query.query(agg_query.model.galaxies.lens.envelope == envelope_cls)
agg_query = agg_query.query(agg_query.model.galaxies.lens.smbh == smbh_cls)

for samples, search in zip(agg_query.values("samples"), agg_query.values("search")):

    tracer_agg = al.agg.TracerAgg(aggregator=agg_query)
    tracer_list = list(tracer_agg.randomly_drawn_via_pdf_gen_from(total_samples=1000))

    galaxy_list = [tracer.galaxies[0] for tracer in tracer_list[0]]

    from autofit.non_linear.samples.pdf import quantile
    from autogalaxy.galaxy.stellar_dark_decomp import StellarDarkDecomp
    from astropy import cosmology as cosmo
    import math

    stellar_mass_angular_list = [
        StellarDarkDecomp(galaxy).stellar_mass_angular_within_circle_from(radius=np.inf)
        for galaxy in galaxy_list
    ]

    critical_surface_density = al.util.cosmology.critical_surface_density_between_redshifts_from(
        redshift_0=0.169, redshift_1=0.451, cosmology=cosmo.Planck15
    )

    stellar_mass_list = [
        stellar_mass_angular * critical_surface_density
        for stellar_mass_angular in stellar_mass_angular_list
    ]

    sigma = 3.0
    low_limit = (1 - math.erf(sigma / math.sqrt(2))) / 2

    median_stellar_mass = quantile(x=stellar_mass_list, q=0.5)[0]
    lower_stellar_mass = quantile(x=stellar_mass_list, q=low_limit)[0]
    upper_stellar_mass = quantile(x=stellar_mass_list, q=1 - low_limit)[0]

    print(
        " {:.4e} {:.4e} {:.4e}".format(
            median_stellar_mass, lower_stellar_mass, upper_stellar_mass
        )
    )

    kpc_per_arcsec = 2.96

    cen_radius = 4.75 / kpc_per_arcsec

    dark_fraction_list = [
        StellarDarkDecomp(galaxy).dark_fraction_at_radius_from(radius=cen_radius)
        for galaxy in galaxy_list
    ]
    sigma = 3.0
    low_limit = (1 - math.erf(sigma / math.sqrt(2))) / 2

    median_dark_fraction = quantile(x=dark_fraction_list, q=0.5)[0]
    lower_dark_fraction = quantile(x=dark_fraction_list, q=low_limit)[0]
    upper_dark_fraction = quantile(x=dark_fraction_list, q=1 - low_limit)[0]

    print(
        " {:.4f} {:.4f} {:.4f}".format(
            median_dark_fraction, lower_dark_fraction, upper_dark_fraction
        )
    )

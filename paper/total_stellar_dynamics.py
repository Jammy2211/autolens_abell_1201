from autoconf import conf
import autofit as af
import autolens as al
import autolens.plot as aplt

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
search_name = "mass_total[1]_mass[total]_source"

mass_cls = al.mp.EllPowerLaw
smbh_cls = None

# mass_cls = al.mp.EllPowerLawBroken
# smbh_cls = None
#
# mass_cls = al.mp.EllPowerLaw
# smbh_cls = al.mp.PointMass
#
# mass_cls = al.mp.EllPowerLawBroken
# smbh_cls = al.mp.PointMass

agg_query = agg.query(agg.search.name == search_name)
agg_query = agg_query.query(agg_query.search.unique_tag == waveband)
agg_query = agg_query.query(agg_query.search.name == search_name)
agg_query = agg_query.query(agg_query.model.galaxies.lens.mass == mass_cls)
agg_query = agg_query.query(agg_query.model.galaxies.lens.smbh == smbh_cls)


for samples, search in zip(agg_query.values("samples"), agg_query.values("search")):

    path_prefix = search.paths.path_prefix

    kpc_per_arcsec = 2.96

    cen_radius = 4.75 / kpc_per_arcsec

    tracer_agg = al.agg.TracerAgg(aggregator=agg_query)
    #   tracer_list = list(tracer_agg.randomly_drawn_via_pdf_gen_from(total_samples=100))
    tracer_list = [list(tracer_agg.max_log_likelihood_gen())]

    galaxy_list = [tracer.galaxies[0] for tracer in tracer_list[0]]

    from autofit.non_linear.samples.pdf import quantile
    from autogalaxy.galaxy.stellar_dark_decomp import StellarDarkDecomp
    from astropy import cosmology as cosmo
    import math

    mass_angular_list = [
        galaxy.mass_angular_within_circle_from(radius=cen_radius)
        for galaxy in galaxy_list
    ]

    critical_surface_density = al.util.cosmology.critical_surface_density_between_redshifts_from(
        redshift_0=0.169, redshift_1=0.451, cosmology=cosmo.Planck15
    )

    mass_list = [
        mass_angular * critical_surface_density for mass_angular in mass_angular_list
    ]

    sigma = 3.0
    low_limit = (1 - math.erf(sigma / math.sqrt(2))) / 2

    median_mass = quantile(x=mass_list, q=0.5)[0]
    lower_mass = quantile(x=mass_list, q=low_limit)[0]
    upper_mass = quantile(x=mass_list, q=1 - low_limit)[0]

    print(" {:.4e} {:.4e} {:.4e}".format(median_mass, lower_mass, upper_mass))

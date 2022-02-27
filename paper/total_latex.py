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
search_name = "mass_total[1]_mass[total]_source__stochastic"

# mass_cls = al.mp.EllPowerLaw
# smbh_cls = None
# prefix = "PL & "

mass_cls = al.mp.EllPowerLawBroken
smbh_cls = None
prefix = "BPL & "
#
# mass_cls = al.mp.EllPowerLaw
# smbh_cls = al.mp.PointMass
# prefix = "PL + SMBH & "
#
# mass_cls = al.mp.EllPowerLawBroken
# smbh_cls = al.mp.PointMass
# prefix = "BPL + SMBH & "

agg_query = agg.query(agg.search.name == search_name)
# agg_query = agg_query.query(agg_query.search.unique_tag == waveband)
# agg_query = agg_query.query(agg_query.search.name == search_name)
# agg_query = agg_query.query(agg_query.model.galaxies.lens.mass == mass_cls)
# agg_query = agg_query.query(agg_query.model.galaxies.lens.smbh == smbh_cls)


for samples, search in zip(agg_query.values("samples"), agg_query.values("search")):

    path_prefix = search.paths.path_prefix

    lens_name = f'{path_prefix.replace("/", "_")}'

    latex = af.text.Samples.latex(
        samples=samples, include_name=True, include_quickmath=True, prefix=prefix
    )

    print(f"{latex} \\\\[2pt] \n")

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
# search_name = "mass_light_dark[1]_light[fixed]_mass[light_dark]_source_grad__stochastic"

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

    path_prefix = search.paths.path_prefix

    lens_name = f'{path_prefix.replace("/", "_")}'

    latex = af.text.Samples.latex(
        samples=samples, include_name=True, include_quickmath=True, prefix=prefix
    )

    print(f"{latex} \\\\[2pt] \n")

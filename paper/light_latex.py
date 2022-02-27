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

agg = af.Aggregator.from_database(filename="rjlens.sqlite", completed_only=True)

# waveband = "f390w"
waveband = "f814w"

agg = agg.order_by(agg.search.path_prefix)

"""
__Query__
"""
search_name = "light[1]_light[parametric]"

bulge_cls = al.lp.EllSersic
disk_cls = None
envelope_cls = None
sersic_index_range = None
prefix = "Sersic x1 & "

# bulge_cls = al.lp.EllSersic
# disk_cls = al.lp.EllSersic
# envelope_cls = None
# sersic_index_range = [1.26483, 1.27485]
# prefix = "Sersic x2 & "

bulge_cls = al.lp.EllSersic
disk_cls = al.lp.EllSersic
envelope_cls = al.lp.EllSersic
sersic_index_range = None
prefix = "Sersic x3 & "

agg_query = agg

agg_query = agg_query.query(agg_query.search.unique_tag == waveband)
agg_query = agg_query.query(agg_query.search.name == search_name)
agg_query = agg_query.query(agg_query.model.galaxies.lens.bulge == bulge_cls)
agg_query = agg_query.query(agg_query.model.galaxies.lens.disk == disk_cls)
agg_query = agg_query.query(agg_query.model.galaxies.lens.envelope == envelope_cls)

if sersic_index_range is not None:
    agg_query = agg_query.query(
        agg_query.model.galaxies.lens.bulge.sersic_index > sersic_index_range[0]
    )
    agg_query = agg_query.query(
        agg_query.model.galaxies.lens.bulge.sersic_index < sersic_index_range[1]
    )


for samples, search in zip(agg_query.values("samples"), agg_query.values("search")):

    path_prefix = search.paths.path_prefix

    lens_name = f'{path_prefix.replace("/", "_")}'

    latex = af.text.Samples.latex(
        samples=samples, include_name=True, include_quickmath=True, prefix=prefix
    )

    print(f"{latex} \\\\[2pt] \n")

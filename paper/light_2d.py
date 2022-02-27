import os
from os import path
from autoconf import conf
import autofit as af
import autolens as al
import autolens.plot as aplt
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
plot_path = path.join(workspace_path, "paper", "images", "light_2d")

"""
__Grid__
"""

grid = al.Grid2D.uniform(shape_native=(400, 400), pixel_scales=0.04)

### ALL ALIGN ###


def plot_image(
    waveband,
    search_name,
    filename,
    title,
    component_list,
    bulge_cls,
    disk_cls=None,
    envelope_cls=None,
    sersic_index_range=None,
):

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

    tracer_agg = al.agg.TracerAgg(aggregator=agg_query)
    tracer = list(tracer_agg.max_log_likelihood_gen())[0]

    include = aplt.Include2D(light_profile_centres=False, mass_profile_centres=False)

    mat_plot_2d = aplt.MatPlot2D(
        cmap=aplt.Cmap(vmax=0.3),
        output=aplt.Output(filename=filename, path=plot_path, format=["png", "pdf"]),
    )

    galaxy_plotter = aplt.GalaxyPlotter(
        galaxy=tracer.galaxies[0],
        grid=grid,
        mat_plot_2d=mat_plot_2d,
        include_2d=include,
    )

    light_profile_plotters = [
        galaxy_plotter.light_profile_plotter_from(light_profile)
        for light_profile in galaxy_plotter.galaxy.light_profile_list
    ]

    for i, light_profile_plotter in enumerate(light_profile_plotters):

        light_profile_plotter.set_title(label=f"{title} Component {i+1} (F814W)")
        light_profile_plotter.set_filename(filename=f"{filename}_{component_list[i]}")

        light_profile_plotter.figures_2d(image=True)


waveband = "f814w"
search_name = "light[1]_light[parametric]"

plot_image(
    waveband=waveband,
    search_name=search_name,
    title="x1 Sersic",
    component_list=[1],
    bulge_cls=al.lp.EllSersic,
    disk_cls=None,
    envelope_cls=None,
    filename="light_2d_sersic_x1",
)

plot_image(
    waveband=waveband,
    search_name=search_name,
    title="x2 Sersic",
    component_list=[2, 1],
    bulge_cls=al.lp.EllSersic,
    disk_cls=al.lp.EllSersic,
    filename="light_2d_no_align_x2",
    sersic_index_range=[1.26483, 1.27485],
)

plot_image(
    waveband=waveband,
    search_name=search_name,
    title="x3 Sersic",
    component_list=[1, 2, 3],
    bulge_cls=al.lp.EllSersic,
    disk_cls=al.lp.EllSersic,
    envelope_cls=al.lp.EllSersic,
    filename="light_2d_no_align_x3",
)

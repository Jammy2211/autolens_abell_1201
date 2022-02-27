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

plot_path = path.join(workspace_path, "paper", "images", "light_dark_1d_base")

agg = af.Aggregator.from_database(filename="rjlens.sqlite", completed_only=False)

"""
__Grid__
"""
grid = al.Grid2D.uniform(shape_native=(100, 100), pixel_scales=0.04)

grid.radial_projected_shape_slim = 50


def plot_image(
    waveband,
    search_name,
    filename,
    bulge_cls,
    disk_cls=None,
    envelope_cls=None,
    sersic_index_range=None,
    legend_labels=None,
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

    include_1d = aplt.Include1D(einstein_radius=False, half_light_radius=False)

    mat_plot_1d = aplt.MatPlot1D(
        axis=aplt.Axis(extent=[None, None, 1e-1, 1e1]),
        yx_plot=aplt.YXPlot(plot_axis_type="semilogy"),
        output=aplt.Output(filename=filename, path=plot_path, format=["png", "pdf"]),
    )

    galaxy_plotter = aplt.GalaxyPlotter(
        galaxy=tracer.galaxies[0],
        grid=grid,
        mat_plot_1d=mat_plot_1d,
        include_1d=include_1d,
    )

    galaxy_plotter.figures_1d_decomposed(convergence=True, legend_labels=legend_labels)


waveband = "f814w"
search_name = "mass_light_dark[1]_light[parametric]_mass[light_dark]_source"

plot_image(
    waveband=waveband,
    search_name=search_name,
    bulge_cls=al.lmp.EllSersic,
    filename="light_1d_sersic_x1",
    legend_labels=["Total", "Dark Matter", "Sersic 1", None],
)

plot_image(
    waveband=waveband,
    search_name=search_name,
    bulge_cls=al.lmp.EllSersic,
    disk_cls=al.lmp.EllSersic,
    filename="light_1d_align_all_x2",
    sersic_index_range=[2.0, 2.5],
    legend_labels=["Total", "Dark Matter", "Sersic 1", "Sersic 2", None],
)

plot_image(
    waveband=waveband,
    search_name=search_name,
    bulge_cls=al.lmp.EllSersic,
    disk_cls=al.lmp.EllSersic,
    filename="light_1d_align_centre_x2",
    sersic_index_range=[1.095, 1.097],
    legend_labels=["Total", "Dark Matter", "Sersic 1", "Sersic 2", None],
)

plot_image(
    waveband=waveband,
    search_name=search_name,
    bulge_cls=al.lmp.EllSersic,
    disk_cls=al.lmp.EllSersic,
    filename="light_1d_no_align_x2",
    sersic_index_range=[1.273, 1.275],
    legend_labels=["Total", "Dark Matter", "Sersic 1", "Sersic 2", None],
)

plot_image(
    waveband=waveband,
    search_name=search_name,
    bulge_cls=al.lmp.EllSersic,
    disk_cls=al.lmp.EllSersic,
    envelope_cls=al.lmp.EllSersic,
    filename="light_1d_no_align_x3",
    legend_labels=["Total", "Dark Matter", "Sersic 1", "Sersic 2", "Sersic 3", None],
)

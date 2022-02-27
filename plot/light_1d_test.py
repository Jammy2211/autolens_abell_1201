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

agg = af.Aggregator.from_database(filename="rjlens_test.sqlite", completed_only=True)

plot_path = path.join(workspace_path, "paper", "images", "light_1d")

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

    tracer_list_gen = tracer_agg.randomly_drawn_from_pdf_gen(total_samples=50)

    galaxy_error_list = [
        tracer.galaxies[0] for tracer_list in tracer_list_gen for tracer in tracer_list
    ]

    include_1d = aplt.Include1D(einstein_radius=False, half_light_radius=False)

    mat_plot_1d = aplt.MatPlot1D(
        title=aplt.Title(label=f"Decomposed 1D Light Profiles ({waveband.upper()})"),
        axis=aplt.Axis(extent=[None, None, 1e-3, 10.0]),
        yx_plot=aplt.YXPlot(plot_axis_type="semilogy"),
        #     output=aplt.Output(filename=filename, path=plot_path, format=["png", "pdf"]),
    )

    galaxy_plotter = aplt.GalaxyPlotter(
        galaxy=tracer.galaxies[0],
        grid=grid,
        mat_plot_1d=mat_plot_1d,
        include_1d=include_1d,
        galaxy_error_list=galaxy_error_list,
    )

    galaxy_plotter.figures_1d_decomposed(image=True, legend_labels=legend_labels)


waveband = "f390w"
search_name = "light[1]_light[parametric]"

plot_image(
    waveband=waveband,
    search_name=search_name,
    bulge_cls=al.lp.EllSersic,
    disk_cls=al.lp.EllSersic,
    filename="light_1d_no_align_x2",
    #  sersic_index_range=[1.264, 1.266],
    legend_labels=["Total", "Sersic 1", "Sersic 2"],
)

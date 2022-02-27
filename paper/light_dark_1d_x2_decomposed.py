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

agg = af.Aggregator.from_database(
    filename="rjlens_no_lens_light.sqlite", completed_only=False
)

plot_path = path.join(workspace_path, "paper", "images", "light_dark_1d_x2_decomposed")

"""
__Grid__
"""
grid = al.Grid2D.uniform(shape_native=(100, 100), pixel_scales=0.04)

grid.radial_projected_shape_slim = 50


def plot_image(
    waveband,
    search_name,
    filename,
    envelope_cls=None,
    sersic_index_range=None,
    legend_labels=None,
):

    agg_query = agg

    agg_query = agg_query.query(agg_query.search.unique_tag == waveband)
    agg_query = agg_query.query(agg_query.search.name == search_name)
    # agg_query = agg_query.query(agg_query.model.galaxies.lens.bulge == bulge_cls)
    #  agg_query = agg_query.query(agg_query.model.galaxies.lens.disk == disk_cls)
    agg_query = agg_query.query(agg_query.model.galaxies.lens.envelope == envelope_cls)

    if sersic_index_range is not None:
        agg_query = agg_query.query(
            agg_query.model.galaxies.lens.bulge.sersic_index > sersic_index_range[0]
        )
        agg_query = agg_query.query(
            agg_query.model.galaxies.lens.bulge.sersic_index < sersic_index_range[1]
        )

    tracer_agg = al.agg.TracerAgg(aggregator=agg_query)
    tracer_list = list(tracer_agg.randomly_drawn_via_pdf_gen_from(total_samples=100))

    galaxy_list = [tracer.galaxies[0] for tracer in tracer_list[0]]

    include_1d = aplt.Include1D(einstein_radius=False, half_light_radius=False)

    mat_plot_1d = aplt.MatPlot1D(
        title=aplt.Title(
            label=f"Decomposed 1D Stellar / Dark Profiles ({waveband.upper()})"
        ),
        ylabel=aplt.YLabel(label="Convergence", labelpad=1.0),
        axis=aplt.Axis(extent=[None, None, 5e-1, 2.0e1]),
        yx_plot=aplt.YXPlot(plot_axis_type="semilogy"),
        output=aplt.Output(filename=filename, path=plot_path, format=["png", "pdf"]),
    )

    galaxy_plotter = aplt.GalaxyPDFPlotter(
        galaxy_pdf_list=galaxy_list,
        grid=grid,
        mat_plot_1d=mat_plot_1d,
        include_1d=include_1d,
    )

    galaxy_plotter.figures_1d_decomposed(convergence=True, legend_labels=legend_labels)


waveband = "f390w"

search_name = "mass_light_dark[1]_light[fixed]_mass[light_dark]_source"

plot_image(
    waveband=waveband,
    search_name=search_name,
    filename="light_dark_1d_x2",
    legend_labels=["Total", "Bulge", "Disk", "Dark Matter", None, None],
)

search_name = "mass_light_dark[1]_light[fixed]_mass[light_dark]_source_grad"

plot_image(
    waveband=waveband,
    search_name=search_name,
    filename="light_dark_1d_x2_grad",
    legend_labels=["Total", "Bulge", "Disk", "Dark Matter", None, None],
)

search_name = "mass_light_dark[1]_light[fixed]_mass[light_dark]_source_smbh"

plot_image(
    waveband=waveband,
    search_name=search_name,
    filename="light_dark_1d_x2_smbh",
    legend_labels=["Total", "Bulge", "Disk", "Dark Matter", None, None],
)

search_name = "mass_light_dark[1]_light[fixed]_mass[light_dark]_source_grad_smbh"

plot_image(
    waveband=waveband,
    search_name=search_name,
    filename="light_dark_1d_x2_grad_smbh",
    legend_labels=["Total", "Bulge", "Disk", "Dark Matter", None, None],
)

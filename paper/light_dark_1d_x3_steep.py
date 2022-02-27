from os import path
import os
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

plot_path = path.join(workspace_path, "paper", "images", "light_dark_1d_x3")

"""
__Grid__
"""
grid = al.Grid2D.uniform(shape_native=(100, 100), pixel_scales=0.04)

grid.radial_projected_shape_slim = 50


def galaxy_plotter_from(
    waveband,
    search_name,
    label,
    bulge_cls=al.mp.EllSersic,
    disk_cls=al.mp.EllSersic,
    envelope_cls=None,
    smbh_cls=None,
):

    agg_query = agg

    agg_query = agg_query.query(agg_query.search.unique_tag == waveband)
    agg_query = agg_query.query(agg_query.search.name == search_name)
    #  agg_query = agg_query.query(agg_query.model.galaxies.lens.bulge == bulge_cls)
    #  agg_query = agg_query.query(agg_query.model.galaxies.lens.disk == disk_cls)
    agg_query = agg_query.query(agg_query.model.galaxies.lens.envelope == envelope_cls)
    agg_query = agg_query.query(agg_query.model.galaxies.lens.smbh == smbh_cls)

    tracer_agg = al.agg.TracerAgg(aggregator=agg_query)
    tracer_list = list(tracer_agg.randomly_drawn_via_pdf_gen_from(total_samples=100))

    include_1d = aplt.Include1D(einstein_radius=False)

    mat_plot_1d = aplt.MatPlot1D(
        axis=aplt.Axis(extent=[None, None, 5e-1, 2.0e1]),
        yx_plot=aplt.YXPlot(plot_axis_type="semilogy", label=label),
        fill_between=aplt.FillBetween(alpha=0.3),
        ylabel=aplt.YLabel(label="Convergence", labelpad=1.0),
        title=aplt.Title(label=""),
        output=aplt.Output(
            filename=f"{waveband}_light_dark_1d_x3", path=plot_path, format="pdf"
        ),
    )

    galaxy_list = [tracer.galaxies[0] for tracer in tracer_list[0]]

    return aplt.GalaxyPDFPlotter(
        galaxy_pdf_list=galaxy_list,
        grid=grid,
        mat_plot_1d=mat_plot_1d,
        include_1d=include_1d,
    )


waveband = "f390w"

"""
Make Mass Profile Plotters.
"""

search_name = "mass_light_dark[1]_light[fixed]_mass[light_dark]_source_grad"

agg_query = agg

agg_query = agg_query.query(agg_query.search.unique_tag == waveband)
agg_query = agg_query.query(agg_query.search.name == search_name)
agg_query = agg_query.query(agg_query.model.galaxies.lens.envelope == None)

tracer_agg = al.agg.TracerAgg(aggregator=agg_query)
tracer_list = list(tracer_agg.randomly_drawn_via_pdf_gen_from(total_samples=100))

galaxy_grad_steep = list(tracer_agg.max_log_likelihood_gen())[0].galaxies[0]

galaxy_grad_steep.bulge.mass_to_light_gradient = 0.9
print(galaxy_grad_steep.bulge.mass_to_light_gradient)

include_1d = aplt.Include1D(einstein_radius=False)

mat_plot_1d = aplt.MatPlot1D(
    axis=aplt.Axis(extent=[None, None, 5e-1, 2.0e1]),
    yx_plot=aplt.YXPlot(
        plot_axis_type="semilogy", linestyle="--", label="Gradient MLR (Steep)"
    ),
    fill_between=aplt.FillBetween(alpha=0.3),
    ylabel=aplt.YLabel(label="Convergence", labelpad=1.0),
    title=aplt.Title(label=""),
    output=aplt.Output(
        filename=f"{waveband}_light_dark_1d_x2_steep", path=plot_path, format="pdf"
    ),
)

galaxy_grad_steep_plotter = aplt.GalaxyPlotter(
    galaxy=galaxy_grad_steep, grid=grid, mat_plot_1d=mat_plot_1d, include_1d=include_1d
)

agg_query = agg

agg_query = agg_query.query(agg_query.search.unique_tag == waveband)
agg_query = agg_query.query(agg_query.search.name == search_name)
agg_query = agg_query.query(agg_query.model.galaxies.lens.envelope == None)

tracer_agg = al.agg.TracerAgg(aggregator=agg_query)
tracer_list = list(tracer_agg.randomly_drawn_via_pdf_gen_from(total_samples=100))

galaxy_dark_steep = list(tracer_agg.max_log_likelihood_gen())[0].galaxies[0]

galaxy_dark_steep.dark = al.mp.SphNFWMCRScatterLudlow(
    centre=galaxy_dark_steep.dark.centre,
    #  elliptical_comps=galaxy_dark_steep.dark.elliptical_comps,
    mass_at_200=galaxy_dark_steep.dark.mass_at_200 / 100.0,
    scatter_sigma=4.0,
    #  inner_slope=2.0
)
print(galaxy_dark_steep.dark.inner_slope)

include_1d = aplt.Include1D(einstein_radius=False)

mat_plot_1d = aplt.MatPlot1D(
    axis=aplt.Axis(extent=[None, None, 5e-1, 2.0e1]),
    yx_plot=aplt.YXPlot(
        plot_axis_type="semilogy", linestyle="--", label="Dark (Steep)"
    ),
    fill_between=aplt.FillBetween(alpha=0.3),
    ylabel=aplt.YLabel(label="Convergence", labelpad=1.0),
    title=aplt.Title(label=""),
    output=aplt.Output(
        filename=f"{waveband}_light_dark_1d_x2_steep_c", path=plot_path, format="pdf"
    ),
)

galaxy_dark_steep_plotter = aplt.GalaxyPlotter(
    galaxy=galaxy_dark_steep, grid=grid, mat_plot_1d=mat_plot_1d, include_1d=include_1d
)

"""
Multi-Plots
"""

multi_plotter = aplt.MultiYX1DPlotter(
    plotter_list=[galaxy_grad_steep_plotter, galaxy_dark_steep_plotter]
)

multi_plotter.figure_1d(func_name="figures_1d", figure_name=f"convergence")

multi_plotter.plotter_list[0].mat_plot_1d.output._format = "png"
multi_plotter.figure_1d(func_name="figures_1d", figure_name=f"convergence")

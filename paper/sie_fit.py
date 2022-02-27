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

agg = af.Aggregator.from_database(filename="rjlens.sqlite", completed_only=False)

# waveband = "f390w"
waveband = "f814w"

plot_path = path.join(workspace_path, "paper", "images", "sie_fit", waveband)

vmax = 1.5
vmin = -1.5

if waveband in "f390w":
    vmax = 0.08
else:
    vmax = 0.2

grid = al.Grid2D.uniform(shape_native=(400, 400), pixel_scales=0.04)


def plot_fit(
    waveband,
    search_name,
    prefix,
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

    fit_imaging_agg = al.agg.FitImagingAgg(aggregator=agg_query)
    fit_imaging = list(fit_imaging_agg.max_log_likelihood_gen())[0]

    include_2d = aplt.Include2D(
        critical_curves=False,
        light_profile_centres=False,
        mass_profile_centres=False,
        mapper_data_pixelization_grid=False,
    )

    ### Data ###

    mat_plot_2d = aplt.MatPlot2D(
        title=aplt.Title(label=f"Data ({waveband.upper()})"),
        cmap=aplt.Cmap(vmin=0.0, vmax=vmax),
        output=aplt.Output(
            filename=f"{prefix}_data",
            path=plot_path,
            format=["png", "pdf"],
            format_folder=True,
        ),
    )

    fit_imaging_plotter = aplt.FitImagingPlotter(
        fit=fit_imaging, mat_plot_2d=mat_plot_2d, include_2d=include_2d
    )
    fit_imaging_plotter.figures_2d(image=True)

    visuals_2d = aplt.Visuals2D(
        critical_curves=[fit_imaging.tracer.critical_curves_from(grid=grid)[0]]
    )

    include_2d = aplt.Include2D(
        critical_curves=True,
        light_profile_centres=False,
        mass_profile_centres=False,
        mapper_data_pixelization_grid=False,
    )

    ### Model Image ###

    mat_plot_2d = aplt.MatPlot2D(
        title=aplt.Title(label=f"Model Image ({waveband.upper()})"),
        cmap=aplt.Cmap(vmin=0.0, vmax=vmax),
        output=aplt.Output(
            filename=f"{prefix}_image",
            path=plot_path,
            format=["png", "pdf"],
            format_folder=True,
        ),
    )

    fit_imaging_plotter = aplt.FitImagingPlotter(
        fit=fit_imaging,
        mat_plot_2d=mat_plot_2d,
        include_2d=include_2d,
        visuals_2d=visuals_2d,
    )
    fit_imaging_plotter.figures_2d(model_image=True)

    ### Lensed Source Reconstruction ###

    mat_plot_2d = aplt.MatPlot2D(
        title=aplt.Title(label=f"Model Lensed Source ({waveband.upper()})"),
        cmap=aplt.Cmap(vmin=0.0, vmax=vmax),
        output=aplt.Output(
            filename=f"{prefix}_source_image",
            path=plot_path,
            format=["png", "pdf"],
            format_folder=True,
        ),
    )

    fit_imaging_plotter = aplt.FitImagingPlotter(
        fit=fit_imaging,
        mat_plot_2d=mat_plot_2d,
        include_2d=include_2d,
        visuals_2d=visuals_2d,
    )
    fit_imaging_plotter.figures_2d_of_planes(plane_index=1, model_image=True)

    ### Source Recon ###

    include_2d = aplt.Include2D(
        critical_curves=False,
        light_profile_centres=False,
        mass_profile_centres=False,
        mapper_data_pixelization_grid=False,
        mapper_source_pixelization_grid=False,
        mapper_source_grid_slim=False,
    )

    visuals_2d = aplt.Visuals2D(
        caustics=[fit_imaging.tracer.caustics_from(grid=grid)[0]]
    )

    mat_plot_2d = aplt.MatPlot2D(
        title=aplt.Title(label=f"Source Reconstruction ({waveband.upper()})"),
        cmap=aplt.Cmap(vmin=-0.0, vmax=0.1),
        voronoi_drawer=aplt.VoronoiDrawer(edgecolor=None),
        output=aplt.Output(
            filename=f"{prefix}_source_recon",
            path=plot_path,
            format=["png", "pdf"],
            format_folder=True,
        ),
    )

    fit_imaging_plotter = aplt.FitImagingPlotter(
        fit=fit_imaging,
        mat_plot_2d=mat_plot_2d,
        include_2d=include_2d,
        visuals_2d=visuals_2d,
    )
    fit_imaging_plotter.figures_2d_of_planes(plane_index=1, plane_image=True)


search_name = "light[1]_light[parametric]"

if waveband in "f390w":

    plot_fit(
        waveband=waveband,
        search_name=search_name,
        bulge_cls=al.lp.EllSersic,
        disk_cls=al.lp.EllSersic,
        prefix="x2",
        sersic_index_range=[1.160, 1.162],  # f390w
    )

else:

    # plot_fit(
    #     waveband=waveband,
    #     search_name=search_name,
    #     bulge_cls=al.lp.EllSersic,
    #     disk_cls=al.lp.EllSersic,
    #     prefix="x2",
    #     sersic_index_range=[1.265, 1.270],  # f390w
    # )

    plot_fit(
        waveband=waveband,
        search_name=search_name,
        bulge_cls=al.lp.EllSersic,
        disk_cls=al.lp.EllSersic,
        envelope_cls=al.lp.EllSersic,
        prefix="x3",
    )

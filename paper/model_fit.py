"""
__Imports__
"""
import os
from os import path
import warnings

import numpy as np

warnings.filterwarnings("ignore")

import autofit as af
import autolens as al
import autolens.plot as aplt

from autoconf import conf

"""
__Paths__
"""
workspace_path = os.getcwd()

config_path = path.join(workspace_path, "config")
conf.instance.push(new_path=config_path)

output_path = path.join(workspace_path, "output")

"""
___Database__

Load the database, which is already built.
"""
aggregator = af.Aggregator.from_database(filename="rjlens.sqlite", completed_only=True)

"""
__Query__
"""
waveband = "f814w"
vmax_image = 1.0
vmax_source = 0.2

# waveband = "f390w"
# vmax_image = 0.05
# vmax_source = 0.05

unique_tag = aggregator.search.unique_tag
agg_query = aggregator.query(unique_tag == waveband)

name = aggregator.search.name
agg_query = agg_query.query(
    name == "source_inversion[4]_light[fixed]_mass[total]_source[inversion]"
)

print("Total Samples Objects via `name` model query = ", len(agg_query), "\n")

"""
__Plot Fit__
"""
fit_gen = al.agg.FitImaging(aggregator=agg_query)

plot_path = path.join(workspace_path, "paper", "images", "model_fit")

for fit in fit_gen:

    grid_critical_curves = al.Grid2D.uniform(
        shape_native=fit.imaging.shape_native, pixel_scales=fit.imaging.pixel_scales
    )

    critical_curves = [
        fit.tracer.tangential_critical_curve_from_grid(grid=grid_critical_curves)
    ]
    caustics = [fit.tracer.tangential_caustic_from_grid(grid=grid_critical_curves)]

    visuals_2d = aplt.Visuals2D(critical_curves=critical_curves)

    include_2d = aplt.Include2D(
        mapper_data_pixelization_grid=False,
        mapper_source_grid_slim=False,
        mapper_source_pixelization_grid=False,
        light_profile_centres=False,
        mass_profile_centres=False,
    )

    ### Image ###

    mat_plot_2d = aplt.MatPlot2D(
        title=aplt.Title(label=f"Image ({waveband.upper()})"),
        cmap=aplt.Cmap(vmax=vmax_image),
        ylabel=ylabel,
        output=aplt.Output(path=path.join(plot_path, waveband), format=["png", "pdf"]),
    )
    fit_imaging_plotter = aplt.FitImagingPlotter(
        fit=fit, mat_plot_2d=mat_plot_2d, include_2d=include_2d, visuals_2d=visuals_2d
    )
    fit_imaging_plotter.figures_2d(image=True)

    mat_plot_2d = aplt.MatPlot2D(
        title=aplt.Title(label=f"Model Image ({waveband.upper()})"),
        cmap=aplt.Cmap(vmax=vmax_image),
        ylabel=ylabel,
        output=aplt.Output(path=path.join(plot_path, waveband), format=["png", "pdf"]),
    )
    fit_imaging_plotter = aplt.FitImagingPlotter(
        fit=fit, mat_plot_2d=mat_plot_2d, include_2d=include_2d, visuals_2d=visuals_2d
    )
    fit_imaging_plotter.figures_2d(model_image=True)

    mat_plot_2d = aplt.MatPlot2D(
        title=aplt.Title(label=f"Model Lensed Source ({waveband.upper()})"),
        cmap=aplt.Cmap(vmin=0.0, vmax=vmax_source),
        ylabel=ylabel,
        output=aplt.Output(path=path.join(plot_path, waveband), format=["png", "pdf"]),
    )
    fit_imaging_plotter = aplt.FitImagingPlotter(
        fit=fit, mat_plot_2d=mat_plot_2d, include_2d=include_2d, visuals_2d=visuals_2d
    )
    fit_imaging_plotter.figures_2d_of_planes(plane_index=1, model_image=True)

    visuals_2d = aplt.Visuals2D(caustics=caustics)

    mat_plot_2d = aplt.MatPlot2D(
        title=aplt.Title(label=f"Reconstructed Source ({waveband.upper()})"),
        cmap=aplt.Cmap(vmin=0.0, vmax=vmax_source),
        ylabel=ylabel,
        output=aplt.Output(path=path.join(plot_path, waveband), format=["png", "pdf"]),
    )
    fit_imaging_plotter = aplt.FitImagingPlotter(
        fit=fit, mat_plot_2d=mat_plot_2d, include_2d=include_2d, visuals_2d=visuals_2d
    )
    fit_imaging_plotter.figures_2d_of_planes(plane_index=1, plane_image=True)

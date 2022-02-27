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

waveband = "f390w"
waveband = "f814w"

plot_path = path.join(
    workspace_path, "paper", "images", "total_mass_fit_fixed_centre", waveband
)

vmax = 1.5
vmin = -1.5

if waveband in "f390w":
    vmax_zoom = 0.04
else:
    vmax_zoom = 0.12


def plot_fit(waveband, search_name, mass_cls, tag, mass_label, smbh_cls=None):

    agg_query = agg

    agg_query = agg_query.query(agg_query.search.unique_tag == waveband)
    agg_query = agg_query.query(agg_query.search.name == search_name)
    agg_query = agg_query.query(agg_query.model.galaxies.lens.mass == mass_cls)
    agg_query = agg_query.query(agg_query.model.galaxies.lens.smbh == smbh_cls)

    fit_imaging_agg = al.agg.FitImagingAgg(aggregator=agg_query)
    fit_imaging = list(fit_imaging_agg.max_log_likelihood_gen())[0]

    include_2d = aplt.Include2D(
        critical_curves=False,
        light_profile_centres=False,
        mass_profile_centres=False,
        mapper_data_pixelization_grid=False,
    )

    ### Lensed Source Reconstruction ###

    mat_plot_2d = aplt.MatPlot2D(
        title=aplt.Title(label=f"{mass_label} Lensed Source ({waveband.upper()})"),
        output=aplt.Output(
            filename=f"{tag}_image", path=plot_path, format=["png", "pdf"]
        ),
    )

    fit_imaging_plotter = aplt.FitImagingPlotter(
        fit=fit_imaging, mat_plot_2d=mat_plot_2d, include_2d=include_2d
    )
    fit_imaging_plotter.figures_2d_of_planes(plane_index=1, model_image=True)

    ### Lensed Source Reconstruction (Zoomed) ###

    mat_plot_2d = aplt.MatPlot2D(
        title=aplt.Title(label=f"{mass_label} Counter Image ({waveband.upper()})"),
        cmap=aplt.Cmap(vmin=0.0, vmax=vmax_zoom),
        axis=aplt.Axis(extent=[-0.75, 0.25, -0.9, 0.1]),
        output=aplt.Output(
            filename=f"{tag}_image_zoomed", path=plot_path, format=["png", "pdf"]
        ),
    )

    fit_imaging_plotter = aplt.FitImagingPlotter(
        fit=fit_imaging, mat_plot_2d=mat_plot_2d, include_2d=include_2d
    )
    fit_imaging_plotter.figures_2d_of_planes(plane_index=1, model_image=True)

    ### Normalized Residual Map ###

    mat_plot_2d = aplt.MatPlot2D(
        title=aplt.Title(
            label=f"{mass_label} Normalized Residual Map ({waveband.upper()})"
        ),
        cmap=aplt.Cmap(vmin=vmin, vmax=vmax),
        output=aplt.Output(
            filename=f"{tag}_norm", path=plot_path, format=["png", "pdf"]
        ),
    )

    fit_imaging_plotter = aplt.FitImagingPlotter(
        fit=fit_imaging, mat_plot_2d=mat_plot_2d, include_2d=include_2d
    )
    fit_imaging_plotter.figures_2d(normalized_residual_map=True)

    ### Normalized Residual Map (Zoomed) ###

    mat_plot_2d = aplt.MatPlot2D(
        title=aplt.Title(
            label=f"{mass_label} Normalized Residual Map ({waveband.upper()})"
        ),
        cmap=aplt.Cmap(vmin=vmin, vmax=vmax),
        axis=aplt.Axis(extent=[-0.75, 0.25, -0.9, 0.1]),
        output=aplt.Output(
            filename=f"{tag}_norm_zoomed", path=plot_path, format=["png", "pdf"]
        ),
    )

    fit_imaging_plotter = aplt.FitImagingPlotter(
        fit=fit_imaging, mat_plot_2d=mat_plot_2d, include_2d=include_2d
    )
    fit_imaging_plotter.figures_2d(normalized_residual_map=True)

    sto


"""
Make Mass Profile Plotters.
"""

search_name = "mass_total[1]_mass[total]_source"

mass_profile_plotter_bpl = plot_fit(
    waveband=waveband,
    search_name=search_name,
    mass_cls=al.mp.EllPowerLawBroken,
    mass_label="BPL",
    tag="bpl",
)

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
    filename="rjlens_no_lens_light_update.sqlite", completed_only=False
)

waveband = "f390w"
# waveband = "f814w"

plot_path = path.join(
    workspace_path, "paper", "images", "total_mass_fit_smbh_fixed", waveband
)

vmax = 1.5
vmin = -1.5


def plot_fit(waveband, search_name, mass_label):

    einstein_radius = 0.2

    agg_query = agg

    agg_query = agg_query.query(agg_query.search.unique_tag == waveband)
    agg_query = agg_query.query(agg_query.search.name == search_name)
    agg_query = agg_query.query(
        agg_query.model.galaxies.lens.smbh.einstein_radius == einstein_radius
    )

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
        title=aplt.Title(
            label=f"{mass_label} Lensed Source w/ SMBH ({waveband.upper()})"
        ),
        output=aplt.Output(
            filename=f"{einstein_radius}_image", path=plot_path, format=["png", "pdf"]
        ),
    )

    fit_imaging_plotter = aplt.FitImagingPlotter(
        fit=fit_imaging, mat_plot_2d=mat_plot_2d, include_2d=include_2d
    )
    fit_imaging_plotter.figures_2d_of_planes(plane_index=1, model_image=True)

    ### Lensed Source Reconstruction (Zoomed) ###

    mat_plot_2d = aplt.MatPlot2D(
        title=aplt.Title(
            label=f"{mass_label} Counter Image w/ SMBH ({waveband.upper()})"
        ),
        axis=aplt.Axis(extent=[-0.75, 0.25, -0.9, 0.1]),
        output=aplt.Output(
            filename=f"{einstein_radius}_image_zoomed",
            path=plot_path,
            format=["png", "pdf"],
        ),
    )

    fit_imaging_plotter = aplt.FitImagingPlotter(
        fit=fit_imaging, mat_plot_2d=mat_plot_2d, include_2d=include_2d
    )
    fit_imaging_plotter.figures_2d_of_planes(plane_index=1, model_image=True)

    ### Normalized Residual Map ###

    mat_plot_2d = aplt.MatPlot2D(
        title=aplt.Title(
            label=f"{mass_label} Normalized Residual Map w/ SMBH ({waveband.upper()})"
        ),
        cmap=aplt.Cmap(vmin=vmin, vmax=vmax),
        output=aplt.Output(
            filename=f"{einstein_radius}_norm", path=plot_path, format=["png", "pdf"]
        ),
    )

    fit_imaging_plotter = aplt.FitImagingPlotter(
        fit=fit_imaging, mat_plot_2d=mat_plot_2d, include_2d=include_2d
    )
    fit_imaging_plotter.figures_2d(normalized_residual_map=True)

    ### Reconstruction ###

    mat_plot_2d = aplt.MatPlot2D(
        title=aplt.Title(
            label=f"{mass_label} Source Reconstruction w/ SMBH ({waveband.upper()})"
        ),
        cmap=aplt.Cmap(vmin=vmin, vmax=vmax),
        output=aplt.Output(
            filename=f"{einstein_radius}_norm", path=plot_path, format=["png", "pdf"]
        ),
    )

    fit_imaging_plotter = aplt.FitImagingPlotter(
        fit=fit_imaging, mat_plot_2d=mat_plot_2d, include_2d=include_2d
    )
    fit_imaging_plotter.figures_2d_of_planes(plane_index=0, plane_image=True)


"""
Make Mass Profile Plotters.
"""

search_name = "mass_total[1]_mass[total]_source_smbh_fixed"

mass_profile_plotter = plot_fit(
    waveband=waveband, search_name=search_name, mass_label="BPL"
)

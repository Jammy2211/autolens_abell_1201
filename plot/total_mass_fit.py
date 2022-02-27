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

output_path = path.join(
    path.sep, "Users", "Jammy", "Results", "projects", "rjlens", "output"
)

agg = af.Aggregator.from_database(filename="rjlens.sqlite", completed_only=True)

plot_path = path.join(workspace_path, "paper", "images", "total_mass_1d")

waveband = "f390w"
# waveband = "f814w"

plot_path = path.join(workspace_path, "plot", "images", "total_mass_fit", waveband)

vmax = 2.0
vmin = -2.0


def plot_fit(waveband, search_name, mass_cls, folder, smbh_cls=None):

    agg_query = agg

    agg_query = agg_query.query(agg_query.search.unique_tag == waveband)
    agg_query = agg_query.query(agg_query.search.name == search_name)
    agg_query = agg_query.query(agg_query.model.galaxies.lens.mass == mass_cls)
    agg_query = agg_query.query(agg_query.model.galaxies.lens.smbh == smbh_cls)

    fit_imaging = list(al.agg.FitImaging(aggregator=agg_query))[0]

    mat_plot_2d = aplt.MatPlot2D(
        output=aplt.Output(path=path.join(plot_path, folder), format="png")
    )

    fit_imaging_plotter = aplt.FitImagingPlotter(
        fit=fit_imaging, mat_plot_2d=mat_plot_2d
    )

    fit_imaging_plotter.figures_2d(model_image=True)
    fit_imaging_plotter.figures_2d_of_planes(
        plane_image=1, subtracted_image=True, model_image=True
    )

    mat_plot_2d = aplt.MatPlot2D(
        output=aplt.Output(path=path.join(plot_path, folder), format="pdf")
    )

    fit_imaging_plotter = aplt.FitImagingPlotter(
        fit=fit_imaging, mat_plot_2d=mat_plot_2d
    )

    fit_imaging_plotter.figures_2d(model_image=True)
    fit_imaging_plotter.figures_2d_of_planes(
        plane_image=1, subtracted_image=True, model_image=True
    )

    mat_plot_2d_norm = aplt.MatPlot2D(
        cmap=aplt.Cmap(vmin=vmin, vmax=vmax),
        output=aplt.Output(path=path.join(plot_path, folder), format="png"),
    )

    fit_imaging_plotter_norm = aplt.FitImagingPlotter(
        fit=fit_imaging, mat_plot_2d=mat_plot_2d_norm
    )
    fit_imaging_plotter_norm.figures_2d(normalized_residual_map=True)

    mat_plot_2d_norm = aplt.MatPlot2D(
        cmap=aplt.Cmap(vmin=vmin, vmax=vmax),
        output=aplt.Output(path=path.join(plot_path, folder), format="pdf"),
    )

    fit_imaging_plotter_norm = aplt.FitImagingPlotter(
        fit=fit_imaging, mat_plot_2d=mat_plot_2d_norm
    )
    fit_imaging_plotter_norm.figures_2d(normalized_residual_map=True)


"""
Make Mass Profile Plotters.
"""

search_name = "mass_total[1]_light[parametric]_mass[total]_source"

mass_profile_plotter_pl = plot_fit(
    waveband=waveband, search_name=search_name, mass_cls=al.mp.EllPowerLaw, folder="pl"
)
mass_profile_plotter_bpl = plot_fit(
    waveband=waveband,
    search_name=search_name,
    mass_cls=al.mp.EllPowerLawBroken,
    folder="bpl",
)
mass_profile_plotter_pl_smbh = plot_fit(
    waveband=waveband,
    search_name=search_name,
    mass_cls=al.mp.EllPowerLaw,
    smbh_cls=al.mp.PointMass,
    folder="pl_smbh",
)
mass_profile_plotter_bpl_smbh = plot_fit(
    waveband=waveband,
    search_name=search_name,
    mass_cls=al.mp.EllPowerLawBroken,
    smbh_cls=al.mp.PointMass,
    folder="bpl_smbh",
)

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

agg = af.Aggregator.from_database(
    filename="rjlens_no_lens_light.sqlite", completed_only=False
)

# waveband = "f390w"
waveband = "f814w"

if waveband in "f390w":
    vmax_zoom = 0.02
else:
    vmax_zoom = 0.06

if waveband in "f390w":
    vmax_no_zoom = 0.07
else:
    vmax_no_zoom = 0.15

plot_path = path.join(workspace_path, "paper", "images", "light_dark_fit_x2", waveband)

"""
__Grid__
"""
grid = al.Grid2D.uniform(shape_native=(100, 100), pixel_scales=0.04)

vmax = 2.5
vmin = -2.5


def plot_fit(
    waveband, search_name, mass_label, mass_tag, bulge_cls, disk_cls=None, smbh_cls=None
):

    agg_query = agg

    agg_query = agg_query.query(agg_query.search.unique_tag == waveband)
    agg_query = agg_query.query(agg_query.search.name == search_name)
    agg_query = agg_query.query(agg_query.model.galaxies.lens.bulge == bulge_cls)
    agg_query = agg_query.query(agg_query.model.galaxies.lens.disk == disk_cls)
    agg_query = agg_query.query(agg_query.model.galaxies.lens.envelope == None)
    agg_query = agg_query.query(agg_query.model.galaxies.lens.smbh == smbh_cls)

    fit_imaging_agg = al.agg.FitImagingAgg(aggregator=agg_query)
    fit_imaging = list(fit_imaging_agg.max_log_likelihood_gen())[0]

    include_2d = aplt.Include2D(
        critical_curves=False,
        light_profile_centres=False,
        mass_profile_centres=False,
        mapper_data_pixelization_grid=False,
    )

    patch_overlay = aplt.PatchOverlay(edgecolor="cy", alpha=0.7)
    visuals_2d = aplt.Visuals2D(patches=[Circle(xy=(0.0, 0.0), radius=0.3, fill=True)])

    ### Data ###

    mat_plot_2d = aplt.MatPlot2D(
        patch_overlay=patch_overlay,
        title=aplt.Title(label=f"Data ({waveband.upper()})"),
        cmap=aplt.Cmap(vmin=0.0, vmax=vmax_no_zoom),
        output=aplt.Output(
            filename=f"{mass_tag}_data",
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
    fit_imaging_plotter.figures_2d(image=True)

    ### Data (Zoomed) ###

    mat_plot_2d = aplt.MatPlot2D(
        patch_overlay=patch_overlay,
        title=aplt.Title(label=f"Data ({waveband.upper()})"),
        axis=aplt.Axis(extent=[-1.0, 0.5, -1.2, 0.3]),
        cmap=aplt.Cmap(vmin=0.0, vmax=vmax_zoom),
        output=aplt.Output(
            filename=f"{mass_tag}_data_zoomed",
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
    fit_imaging_plotter.figures_2d(image=True)

    ### Lensed Source Reconstruction ###

    mat_plot_2d = aplt.MatPlot2D(
        patch_overlay=patch_overlay,
        title=aplt.Title(label=f"{mass_label} Lensed Source ({waveband.upper()})"),
        cmap=aplt.Cmap(vmin=0.0, vmax=vmax_no_zoom),
        output=aplt.Output(
            filename=f"{mass_tag}_image",
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

    ### Lensed Source Reconstruction (Zoomed) ###

    mat_plot_2d = aplt.MatPlot2D(
        patch_overlay=patch_overlay,
        title=aplt.Title(label=f"{mass_label} Lensed Source ({waveband.upper()})"),
        axis=aplt.Axis(extent=[-1.0, 0.5, -1.2, 0.3]),
        cmap=aplt.Cmap(vmin=0.0, vmax=vmax_zoom),
        output=aplt.Output(
            filename=f"{mass_tag}_image_zoomed",
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

    ### Normalized Residual Map ###

    mat_plot_2d = aplt.MatPlot2D(
        patch_overlay=patch_overlay,
        title=aplt.Title(label=f"{mass_label} Residuals ({waveband.upper()})"),
        cmap=aplt.Cmap(vmin=vmin, vmax=vmax),
        output=aplt.Output(
            filename=f"{mass_tag}_norm",
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
    fit_imaging_plotter.figures_2d(normalized_residual_map=True)

    ### Normalized Residual Map (Zoomed) ###

    mat_plot_2d = aplt.MatPlot2D(
        patch_overlay=patch_overlay,
        title=aplt.Title(label=f"{mass_label} Residuals ({waveband.upper()})"),
        axis=aplt.Axis(extent=[-1.0, 0.5, -1.2, 0.3]),
        cmap=aplt.Cmap(vmin=vmin, vmax=vmax),
        output=aplt.Output(
            filename=f"{mass_tag}_norm_zoomed",
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
    fit_imaging_plotter.figures_2d(normalized_residual_map=True)

    ### Source Recon ###

    include_2d = aplt.Include2D(
        critical_curves=False,
        light_profile_centres=False,
        mass_profile_centres=False,
        mapper_data_pixelization_grid=False,
        mapper_source_pixelization_grid=False,
        mapper_source_grid_slim=False,
    )

    mat_plot_2d = aplt.MatPlot2D(
        title=aplt.Title(label=f"{mass_label} Source ({waveband.upper()})"),
        axis=aplt.Axis(extent=[0.1, 0.7, 0.4, 1.3]),
        cmap=aplt.Cmap(vmin=-0.0, vmax=0.1),
        voronoi_drawer=aplt.VoronoiDrawer(edgecolor=None),
        output=aplt.Output(
            filename=f"{mass_tag}_source_recon",
            path=plot_path,
            format=["png", "pdf"],
            format_folder=True,
        ),
    )

    fit_imaging_plotter = aplt.FitImagingPlotter(
        fit=fit_imaging, mat_plot_2d=mat_plot_2d, include_2d=include_2d
    )
    fit_imaging_plotter.figures_2d_of_planes(plane_index=1, plane_image=True)


"""
Plot fits.
"""

search_name = "mass_light_dark[1]_light[fixed]_mass[light_dark]_source"

# plot_fit(
#     waveband=waveband,
#     search_name=search_name,
#     bulge_cls=al.mp.EllSersic,
#     disk_cls=al.mp.EllSersic,
#     mass_label="Constant MLR",
#     mass_tag="const",
# )

plot_fit(
    waveband=waveband,
    search_name=f"{search_name}_grad",
    bulge_cls=al.mp.EllSersicRadialGradient,
    disk_cls=al.mp.EllSersicRadialGradient,
    mass_label="Without SMBH",
    mass_tag="grad",
)

# plot_fit(
#     waveband=waveband,
#     search_name=f"{search_name}_smbh",
#     bulge_cls=al.mp.EllSersic,
#     disk_cls=al.mp.EllSersic,
#     smbh_cls=al.mp.PointMass,
#     mass_label="Constant MLR + SMBH",
#     mass_tag="const_smbh",
# )

plot_fit(
    waveband=waveband,
    search_name=f"{search_name}_grad_smbh",
    bulge_cls=al.mp.EllSersicRadialGradient,
    disk_cls=al.mp.EllSersicRadialGradient,
    smbh_cls=al.mp.PointMass,
    mass_label="With SMBH",
    mass_tag="grad_smbh",
)

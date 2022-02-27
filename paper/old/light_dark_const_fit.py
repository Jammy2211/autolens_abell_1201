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

agg = af.Aggregator.from_database(filename="rjlens.sqlite", completed_only=False)

# waveband = "f390w"
waveband = "f814w"

plot_path = path.join(
    workspace_path, "paper", "images", "light_dark_base_fit", waveband
)

"""
__Grid__
"""
grid = al.Grid2D.uniform(shape_native=(100, 100), pixel_scales=0.04)

vmax = 1.5
vmin = -1.5


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

    fit_imaging = list(al.agg.FitImaging(aggregator=agg_query))[0]

    include_2d = aplt.Include2D(
        critical_curves=False, light_profile_centres=False, mass_profile_centres=False
    )

    ### Lensed Source Reconstruction ###

    mat_plot_2d = aplt.MatPlot2D(
        title=aplt.Title(label=f"Reconstructed Lensed Source ({waveband.upper()})"),
        output=aplt.Output(
            filename=f"{prefix}_image", path=path.join(plot_path), format=["png", "pdf"]
        ),
    )

    fit_imaging_plotter = aplt.FitImagingPlotter(
        fit=fit_imaging, mat_plot_2d=mat_plot_2d, include_2d=include_2d
    )
    fit_imaging_plotter.figures_2d_of_planes(plane_index=1, model_image=True)

    ### Normalized Residual Map ###

    mat_plot_2d = aplt.MatPlot2D(
        title=aplt.Title(label=f"Normalized Residual Map ({waveband.upper()})"),
        cmap=aplt.Cmap(vmin=vmin, vmax=vmax),
        output=aplt.Output(
            filename=f"{prefix}_norm", path=path.join(plot_path), format=["png", "pdf"]
        ),
    )

    fit_imaging_plotter = aplt.FitImagingPlotter(
        fit=fit_imaging, mat_plot_2d=mat_plot_2d, include_2d=include_2d
    )
    fit_imaging_plotter.figures_2d(normalized_residual_map=True)


"""
Plot fits.
"""

search_name = "mass_light_dark[1]_light[parametric]_mass[light_dark]_source"

plot_fit(
    waveband=waveband,
    search_name=search_name,
    bulge_cls=al.lmp.EllSersic,
    prefix="light_dark_fit_sersic_x1",
)

plot_fit(
    waveband=waveband,
    search_name=search_name,
    bulge_cls=al.lmp.EllSersic,
    disk_cls=al.lmp.EllSersic,
    prefix="light_dark_fit_align_all_x2",
    sersic_index_range=[2.0, 2.5],
)

plot_fit(
    waveband=waveband,
    search_name=search_name,
    bulge_cls=al.lmp.EllSersic,
    disk_cls=al.lmp.EllSersic,
    prefix="light_dark_fit_align_centre_x2",
    sersic_index_range=[1.095, 1.097],
)

plot_fit(
    waveband=waveband,
    search_name=search_name,
    bulge_cls=al.lmp.EllSersic,
    disk_cls=al.lmp.EllSersic,
    prefix="light_dark_fit_no_align_x2",
    sersic_index_range=[1.273, 1.275],
)

plot_fit(
    waveband=waveband,
    search_name=search_name,
    bulge_cls=al.lmp.EllSersic,
    disk_cls=al.lmp.EllSersic,
    envelope_cls=al.lmp.EllSersic,
    prefix="light_dark_fit_no_align_x3",
)

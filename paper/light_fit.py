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

agg = af.Aggregator.from_database(filename="rjlens.sqlite", completed_only=True)

waveband = "f390w"
# waveband = "f814w"

plot_path = path.join(workspace_path, "paper", "images", "light_fit", waveband)

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

    fit_imaging_agg = al.agg.FitImagingAgg(aggregator=agg_query)
    fit_imaging = list(fit_imaging_agg.max_log_likelihood_gen())[0]

    mat_plot_2d_norm = aplt.MatPlot2D(
        cmap=aplt.Cmap(vmin=vmin, vmax=vmax),
        title=aplt.Title(label=f"Normalized Residual Map ({waveband.upper()})"),
        output=aplt.Output(
            filename=f"{prefix}_norm", path=path.join(plot_path), format=["png", "pdf"]
        ),
    )

    fit_imaging_plotter_norm = aplt.FitImagingPlotter(
        fit=fit_imaging, mat_plot_2d=mat_plot_2d_norm
    )
    fit_imaging_plotter_norm.figures_2d(normalized_residual_map=True)


"""
Plot fits.
"""

search_name = "light[1]_light[parametric]"

# plot_fit(
#     waveband=waveband,
#     search_name=search_name,
#     bulge_cls=al.lp.EllSersic,
#     prefix="light_fit_sersic_x1",
#     sersic_index_range=[0.833, 0.835]
# )

plot_fit(
    waveband=waveband,
    search_name=search_name,
    bulge_cls=al.lp.EllSersic,
    disk_cls=al.lp.EllSersic,
    prefix="light_fit_align_all_x2",
    #    sersic_index_range=[0.987, 0.989],
    #   sersic_index_range=[2.207, 2.209]
    sersic_index_range=[0.49, 0.51],  # f390w
)

plot_fit(
    waveband=waveband,
    search_name=search_name,
    bulge_cls=al.lp.EllSersic,
    disk_cls=al.lp.EllSersic,
    prefix="light_fit_align_centre_x2",
    #    sersic_index_range=[0.833, 0.835],
    #   sersic_index_range=[1.382, 1.384]
    sersic_index_range=[1.149, 1.151],  # f390w
)

plot_fit(
    waveband=waveband,
    search_name=search_name,
    bulge_cls=al.lp.EllSersic,
    disk_cls=al.lp.EllSersic,
    prefix="light_fit_no_align_x2",
    #    sersic_index_range=[1.203, 1.205],
    #   sersic_index_range=[1.264, 1.266]
    sersic_index_range=[1.160, 1.162],  # f390w
)
#
# plot_fit(
#     waveband=waveband,
#     search_name=search_name,
#     bulge_cls=al.lp.EllSersic,
#     disk_cls=al.lp.EllSersic,
#     envelope_cls=al.lp.EllSersic,
#     prefix="light_fit_no_align_x3",
# )

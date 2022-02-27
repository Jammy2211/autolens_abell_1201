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

plot_path = path.join(workspace_path, "paper", "images", "all_1d")


"""

LDMM PLOTTERS

"""

agg = af.Aggregator.from_database(
    filename="rjlens_no_lens_light.sqlite", completed_only=False
)

"""
__Grid__
"""
grid = al.Grid2D.uniform(shape_native=(100, 100), pixel_scales=0.04)
grid.radial_projected_shape_slim = 50

waveband = "f390w"


def mass_profile_plotter_from(
    waveband,
    search_name,
    label,
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

        tracer_agg = al.agg.TracerAgg(aggregator=agg_query)
    tracer = list(tracer_agg.max_log_likelihood_gen())[0]

    include_1d = aplt.Include1D(einstein_radius=False)

    mat_plot_1d = aplt.MatPlot1D(
        axis=aplt.Axis(extent=[None, None, 1e-1, 1e2]),
        yx_plot=aplt.YXPlot(plot_axis_type="semilogy", label=label),
        title=aplt.Title(label="Convergence as a Function of Radius"),
        output=aplt.Output(
            filename=f"{waveband}_total_mass_1d", path=plot_path, format="pdf"
        ),
    )

    return aplt.GalaxyPlotter(
        galaxy=tracer.galaxies[0],
        grid=grid,
        mat_plot_1d=mat_plot_1d,
        include_1d=include_1d,
    )


"""
Make Mass Profile Plotters.
"""

search_name = "mass_light_dark[1]_light[fixed]_mass[light_dark]_source_grad"

mass_profile_plotter_ldm_sersic_x2 = mass_profile_plotter_from(
    waveband=waveband,
    search_name=search_name,
    bulge_cls=al.mp.EllSersicRadialGradient,
    disk_cls=al.mp.EllSersicRadialGradient,
    sersic_index_range=[1.26483, 1.26485],
    label="Decomposed (x2 Sersic) + Shear",
)
mass_profile_plotter_ldm_sersic_x3 = mass_profile_plotter_from(
    waveband=waveband,
    search_name=search_name,
    bulge_cls=al.mp.EllSersicRadialGradient,
    disk_cls=al.mp.EllSersicRadialGradient,
    envelope_cls=al.mp.EllSersicRadialGradient,
    label="Decomposed (x3 Sersic) + Shear",
)

search_name = "mass_light_dark[1]_light[fixed]_mass[light_dark]_source_smbh"

mass_profile_plotter_ldm_sersic_x2_smbh = mass_profile_plotter_from(
    waveband=waveband,
    search_name=search_name,
    bulge_cls=al.mp.EllSersic,
    disk_cls=al.mp.EllSersic,
    sersic_index_range=[2.20769, 2.20771],
    label="Decomposed (x2 Sersic) + Shear + SMBH",
)

mass_profile_plotter_ldm_sersic_x3_smbh = mass_profile_plotter_from(
    waveband=waveband,
    search_name=search_name,
    bulge_cls=al.mp.EllSersic,
    disk_cls=al.mp.EllSersic,
    envelope_cls=al.mp.EllSersic,
    label="Decomposed (x3 Sersic) + Shear + SMBH",
)


"""

TOTAL PLOTTERS

"""


agg = af.Aggregator.from_database(filename="rjlens.sqlite", completed_only=False)


def mass_profile_plotter_from(waveband, search_name, mass_cls, label, smbh_cls=None):

    agg_query = agg

    agg_query = agg_query.query(agg_query.search.unique_tag == waveband)
    agg_query = agg_query.query(agg_query.search.name == search_name)
    agg_query = agg_query.query(agg_query.model.galaxies.lens.mass == mass_cls)
    agg_query = agg_query.query(agg_query.model.galaxies.lens.smbh == smbh_cls)

        tracer_agg = al.agg.TracerAgg(aggregator=agg_query)
    tracer = list(tracer_agg.max_log_likelihood_gen())[0]

    include_1d = aplt.Include1D(einstein_radius=False)

    mat_plot_1d = aplt.MatPlot1D(
        axis=aplt.Axis(extent=[None, None, 1e-1, 1e2]),
        yx_plot=aplt.YXPlot(plot_axis_type="semilogy", label=label),
        title=aplt.Title(label="Convergence as a Function of Radius"),
        output=aplt.Output(
            filename=f"{waveband}_total_mass_1d", path=plot_path, format="pdf"
        ),
    )

    return aplt.MassProfilePlotter(
        mass_profile=tracer.galaxies[0].mass,
        grid=grid,
        mat_plot_1d=mat_plot_1d,
        include_1d=include_1d,
    )


search_name = "mass_total[1]_light[parametric]_mass[total]_source"

mass_profile_plotter_pl = mass_profile_plotter_from(
    waveband=waveband,
    search_name=search_name,
    mass_cls=al.mp.EllPowerLaw,
    label="Power Law + Shear",
)
mass_profile_plotter_bpl = mass_profile_plotter_from(
    waveband=waveband,
    search_name=search_name,
    mass_cls=al.mp.EllPowerLawBroken,
    label="Broken Power Law + Shear",
)

mass_profile_plotter_pl_smbh = mass_profile_plotter_from(
    waveband=waveband,
    search_name=search_name,
    mass_cls=al.mp.EllPowerLaw,
    smbh_cls=al.mp.PointMass,
    label="Power Law + Shear + SMBH",
)

mass_profile_plotter_bpl_smbh = mass_profile_plotter_from(
    waveband=waveband,
    search_name=search_name,
    mass_cls=al.mp.EllPowerLawBroken,
    smbh_cls=al.mp.PointMass,
    label="Broken Power Law + Shear + SMBH",
)

"""
Multi-Plots
"""

multi_plotter = aplt.MultiYX1DPlotter(
    plotter_list=[
        mass_profile_plotter_pl,
        mass_profile_plotter_bpl,
        mass_profile_plotter_ldm_sersic_x2,
        #      mass_profile_plotter_ldm_sersic_x3,
        mass_profile_plotter_pl_smbh,
        mass_profile_plotter_bpl_smbh,
        mass_profile_plotter_ldm_sersic_x2_smbh,
        #      mass_profile_plotter_ldm_sersic_x3_smbh,
    ]
)

multi_plotter.figure_1d(func_name="figures_1d", figure_name=f"convergence")

multi_plotter.plotter_list[0].mat_plot_1d.output._format = "png"
multi_plotter.figure_1d(func_name="figures_1d", figure_name=f"convergence")

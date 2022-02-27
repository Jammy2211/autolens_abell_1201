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
# waveband = "f814w"

plot_path = path.join(workspace_path, "paper", "images", "total_pdf", waveband)


def plot_pdf(waveband, search_name, mass_cls, tag, mass_label, smbh_cls=None):

    agg_query = agg

    agg_query = agg_query.query(agg_query.search.unique_tag == waveband)
    agg_query = agg_query.query(agg_query.search.name == search_name)
    agg_query = agg_query.query(agg_query.model.galaxies.lens.mass == mass_cls)
    agg_query = agg_query.query(agg_query.model.galaxies.lens.smbh == smbh_cls)

    samples = list(agg_query.values("samples"))[0]

    print(samples.model.prior_count)

    dynesty_plotter = aplt.DynestyPlotter(
        samples=samples,
        output=aplt.Output(
            filename=f"{tag}_image", path=plot_path, format=["png", "pdf"]
        ),
    )
    dynesty_plotter.cornerplot(
        #     show_titles=True, title_kwargs={"fontsize": 16},
        quantiles=[0.003, 0.5, 0.997],
        label_kwargs={"fontsize": 16},
        smooth=0.1,
    )


"""
Make Mass Profile Plotters.
"""

search_name = "mass_total[1]_mass[total]_source__stochastic"

# plot_pdf(
#     waveband=waveband,
#     search_name=search_name,
#     mass_cls=al.mp.EllPowerLaw,
#     mass_label="PL",
#     tag="pl",
# )
# plot_pdf(
#     waveband=waveband,
#     search_name=search_name,
#     mass_cls=al.mp.EllPowerLawBroken,
#     mass_label="BPL",
#     tag="bpl",
# )
# plot_pdf(
#     waveband=waveband,
#     search_name=search_name,
#     mass_cls=al.mp.EllPowerLaw,
#     smbh_cls=al.mp.PointMass,
#     mass_label="PL + SMBH",
#     tag="pl_smbh",
# )
plot_pdf(
    waveband=waveband,
    search_name=search_name,
    mass_cls=al.mp.EllPowerLawBroken,
    smbh_cls=al.mp.PointMass,
    mass_label="BPL + SMBH",
    tag="bpl_smbh",
)

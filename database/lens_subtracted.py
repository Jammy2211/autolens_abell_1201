"""
__Imports__
"""
import os
from os import path
import warnings

warnings.filterwarnings("ignore")

import autofit as af
import autolens as al
import autolens.plot as aplt

from autoconf import conf

"""
__Paths__
"""
workspace_path = path.join(path.sep, "Users", "Jammy", "Results", "projects", "rjlens")

config_path = path.join(workspace_path, "config")
conf.instance.push(new_path=config_path)

output_path = path.join(
    path.sep, "Users", "Jammy", "Results", "projects", "rjlens", "output"
)

"""
___Database__

Remove database is making a new build (you could delete manually via your mouse). Building the database is slow, so 
only do this when you redownload results. Things are fast working from an already built database.
"""
if path.exists(path.join("output", "rjlens.sqlite")):
    os.remove(path.join("output", "rjlens.sqlite"))

"""
Load the database. If the file `rjlens.sqlite` does not exist, it will be made by the method below, so its fine if
you run the code below before the file exists.
"""
aggregator = af.Aggregator.from_database(filename="rjlens.sqlite", completed_only=True)

"""
Add all results in the directory "output/rjlens" to the database, which we manipulate below via the aggregator.
Avoid rerunning this once the file `rjlens.sqlite` has been built.
"""
aggregator.add_directory(directory=path.join("output", "rjlens_lens_sub_f390w"))

"""
__Query__
"""
name = aggregator.search.name
agg_query = aggregator.query(name == "light[1]_light[parametric]")
print("Total Samples Objects via `name` model query = ", len(agg_query), "\n")

"""
__Output Lens Subtracted Image__
"""
# samples_gen = agg.values("samples")

fit_imaging_agg = al.agg.FitImagingAgg(aggregator=agg_query)
fit_gen = fit_imaging_agg.max_log_likelihood_gen()

plot_path = path.join(workspace_path, "plot", "lens_subtracted")

for fit, info in zip(fit_gen, agg_query.values("info")):

    mat_plot_2d = aplt.MatPlot2D(
        output=aplt.Output(
            path=plot_path, filename="lens_subtracted_f390w", format="png"
        )
    )
    fit_imaging_plotter = aplt.FitImagingPlotter(fit=fit, mat_plot_2d=mat_plot_2d)
    fit_imaging_plotter.figures_2d_of_planes(plane_index=1, subtracted_image=True)

    mat_plot_2d = aplt.MatPlot2D(
        output=aplt.Output(
            path=plot_path, filename="lens_subtracted_f390w", format="fits"
        )
    )
    fit_imaging_plotter = aplt.FitImagingPlotter(fit=fit, mat_plot_2d=mat_plot_2d)
    fit_imaging_plotter.figures_2d_of_planes(plane_index=1, subtracted_image=True)

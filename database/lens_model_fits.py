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
workspace_path = os.getcwd()

config_path = path.join(workspace_path, "config")
conf.instance.push(new_path=config_path)

output_path = path.join(workspace_path, "output")

"""
___Database__

Remove database is making a new build (you could delete manually via your mouse). Building the database is slow, so 
only do this when you redownload results. Things are fast working from an already built database.
"""
# if path.exists(path.join("output", "rjlens.sqlite")):
#     os.remove(path.join("output", "rjlens.sqlite"))

"""
Load the database. If the file `rjlens.sqlite` does not exist, it will be made by the method below, so its fine if
you run the code below before the file exists.
"""
aggregator = af.Aggregator.from_database(filename="rjlens.sqlite", completed_only=True)

"""
Add all results in the directory "output/rjlens" to the database, which we manipulate below via the aggregator.
Avoid rerunning this once the file `rjlens.sqlite` has been built.
"""
# aggregator.add_directory(directory=path.join("output", "rjlens"))

"""
__Query__
"""
name = aggregator.search.name
unique_tag = aggregator.search.unique_tag
agg_query = aggregator.query(unique_tag == "f814w")
agg_query = agg_query.query(name == "light[1]_light[parametric]")
print("Total Samples Objects via `name` model query = ", len(agg_query), "\n")

"""
__Output Lens Subtracted Image__
"""

tracer_agg = al.agg.TracerAgg(aggregator=agg_query)
tracer_gen = tracer_agg.max_log_likelihood_gen()

for tracer in tracer_gen:

    print()
    print()
    print()
    print()
    print()
    print()

    print(tracer.galaxies[0].bulge)
    print(tracer.galaxies[0].disk)
    print(tracer.galaxies[0].envelope)

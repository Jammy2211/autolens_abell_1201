from os import path
import sys
from time import sleep

sleep(int(sys.argv[3]))

"""
AUTOFIT + CONFIG SETUP
"""

from autoconf import conf

"""
Your username is in the path to where your dataset is stored on Cosma, so first lets input your username below.
"""
cosma_username = "pdtw24"
cosma_path = path.join(path.sep, "cosma7", "data", "dp004", "dc-nigh1", "autolens")
cosma_dataset_path = path.join(cosma_path, "dataset")
cosma_output_path = path.join(cosma_path, "output")

"""
Set the path to the workspace an config files on Cosma.
"""
workspace_path = path.join(path.sep, "cosma", "home", "dp004", "dc-nigh1", "rjlens")
config_path = path.join(workspace_path, "cosma", "config")

"""
Use this path to explicitly set the config path and set the output path to the Cosma output path.
"""
conf.instance.push(new_path=config_path, output_path=cosma_output_path)

sys.path.insert(0, workspace_path)
import slam

"""
AUTOLENS + DATA SETUP
"""
import autofit as af
import autolens as al

pixel_scales = 0.04

dataset_name = "rjlens"

dataset_filter = ["f390w", "f814w"]  # Index 0  # Index 1

dataset_filter = dataset_filter[int(sys.argv[1])]

dataset_path = path.join(cosma_dataset_path, dataset_name, dataset_filter)

imaging = al.Imaging.from_fits(
    image_path=path.join(dataset_path, "image.fits"),
    psf_path=path.join(dataset_path, "psf.fits"),
    noise_map_path=path.join(dataset_path, "noise_map.fits"),
    pixel_scales=pixel_scales,
)

positions = al.Grid2DIrregular.from_json(
    file_path=path.join(dataset_path, "positions.json")
)

mask = al.Mask2D.circular(
    shape_native=imaging.shape_native, pixel_scales=pixel_scales, radius=3.7
)

imaging = imaging.apply_mask(mask=mask)

imaging = imaging.apply_settings(
    settings=al.SettingsImaging(grid_class=al.Grid2DIterate, fractional_accuracy=0.9999)
)

"""
__Settings AutoFit__

The settings of autofit, which controls the output paths, parallelization, databse use, etc.
"""
settings_autofit = af.SettingsSearch(
    path_prefix=path.join(f"{dataset_name}"),
    unique_tag=dataset_filter,
    info=None,
    number_of_cores=int(sys.argv[2]),
    session=None,
)

"""
__HYPER SETUP__

The `SetupHyper` determines which hyper-mode features are used during the model-fit.
"""
setup_hyper = al.SetupHyper(
    hyper_galaxies_lens=False,
    hyper_galaxies_source=False,
    hyper_image_sky=None,
    hyper_background_noise=None,
)

"""
__SOURCE PARAMETRIC PIPELINE (with lens light)__

The SOURCE PARAMETRIC PIPELINE (with lens light) uses three searches to initialize a robust model for the 
source galaxy's light, which in this example:

 - Uses a parametric `EllSersic` bulge and `EllExponential` disk with centres aligned for the lens
 galaxy's light.

 - Uses an `EllIsothermal` model for the lens's total mass distribution with an `ExternalShear`.
"""
settings_lens = al.SettingsLens(positions_threshold=2.5)

analysis = al.AnalysisImaging(
    dataset=imaging, positions=positions, settings_lens=settings_lens
)

bulge = af.Model(al.lp.EllSersic)
disk = af.Model(al.lp.EllExponential)

bulge.centre_0 = af.GaussianPrior(mean=0.0, sigma=0.1)
bulge.centre_1 = af.GaussianPrior(mean=0.0, sigma=0.1)
disk.centre_0 = af.GaussianPrior(mean=0.0, sigma=0.1)
disk.centre_1 = af.GaussianPrior(mean=0.0, sigma=0.1)

bulge.centre = disk.centre

source_parametric_results = slam.source_parametric.with_lens_light(
    settings_autofit=settings_autofit,
    analysis=analysis,
    setup_hyper=setup_hyper,
    lens_bulge=bulge,
    lens_disk=disk,
    mass=af.Model(al.mp.EllIsothermal),
    shear=af.Model(al.mp.ExternalShear),
    source_bulge=af.Model(al.lp.EllSersic),
    redshift_lens=0.169,
    redshift_source=0.451,
)

"""
__SOURCE INVERSION PIPELINE (with lens light)__

The SOURCE INVERSION PIPELINE (with lens light) uses four searches to initialize a robust model for the `Inversion` 
that reconstructs the source galaxy's light. It begins by fitting a `VoronoiMagnification` pixelization with `Constant` 
regularization, to set up the model and hyper images, and then:

 - Uses a `VoronoiBrightnessImage` pixelization.

 - Uses an `AdaptiveBrightness` regularization.

 - Carries the lens redshift, source redshift and `ExternalShear` of the SOURCE PARAMETRIC PIPELINE through to the
 SOURCE INVERSION PIPELINE.

__Settings__:

 - Positions: We update the positions threshold to remove unphysical solutions from the `Inversion` model-fitting.
"""
settings_lens = al.SettingsLens(positions_threshold=0.5)

analysis = al.AnalysisImaging(
    dataset=imaging, positions=positions, settings_lens=settings_lens
)

source_inversion_results = slam.source_inversion.with_lens_light(
    settings_autofit=settings_autofit,
    analysis=analysis,
    setup_hyper=setup_hyper,
    source_parametric_results=source_parametric_results,
    pixelization=al.pix.VoronoiBrightnessImage,
    regularization=al.reg.AdaptiveBrightness,
)

"""
__LIGHT PARAMETRIC PIPELINE__

The LIGHT PARAMETRIC PIPELINE uses one search to fit a complex lens light model to a high level of accuracy, using the
lens mass model and source light model fixed to the maximum log likelihood result of the SOURCE PARAMETRIC PIPELINE.
In this example it:

 - Uses a parametric `EllSersic` bulge and `EllSersic` disk with centres aligned for the lens galaxy's 
 light [Do not use the results of the SOURCE PARAMETRIC PIPELINE to initialize priors].

 - Uses an `EllIsothermal` model for the lens's total mass distribution [fixed from SOURCE PARAMETRIC PIPELINE].

 - Uses an `Inversion` for the source's light [priors fixed from SOURCE INVERSION PIPELINE].

 - Carries the lens redshift, source redshift and `ExternalShear` of the SOURCE PIPELINE through to the MASS 
 PIPELINE [fixed values].
"""
imaging = imaging.apply_settings(
    settings=al.SettingsImaging(grid_class=al.Grid2DIterate, fractional_accuracy=0.9999)
)


analysis = al.AnalysisImaging(
    dataset=imaging,
    hyper_dataset_result=source_inversion_results.last,
    positions=positions,
)

lens_bulge = af.Model(al.lp.EllSersic)
lens_bulge.centre.centre_0 = af.GaussianPrior(mean=0.0, sigma=0.1)
lens_bulge.centre.centre_1 = af.GaussianPrior(mean=0.0, sigma=0.1)

lens_disk = af.Model(al.lp.EllSersic)
lens_disk.centre.centre_0 = af.GaussianPrior(mean=0.0, sigma=0.1)
lens_disk.centre.centre_1 = af.GaussianPrior(mean=0.0, sigma=0.1)

lens_envelope = af.Model(al.lp.EllSersic)
lens_envelope.centre.centre_0 = af.GaussianPrior(mean=0.0, sigma=0.1)
lens_envelope.centre.centre_1 = af.GaussianPrior(mean=0.0, sigma=0.1)

light_results = slam.light_parametric.with_lens_light(
    settings_autofit=settings_autofit,
    analysis=analysis,
    setup_hyper=setup_hyper,
    source_results=source_inversion_results,
    lens_bulge=lens_bulge,
    lens_disk=lens_disk,
    lens_envelope=lens_envelope,
)

"""
__MASS TOTAL PIPELINE (with lens light)__

The MASS TOTAL PIPELINE (with lens light) uses one search to fits a complex lens mass model to a high level of accuracy, 
using the lens mass model and source model of the SOURCE INVERSION PIPELINE to initialize the model priors and the lens 
light model of the LIGHT PARAMETRIC PIPELINE. In this example it:

 - Uses a parametric `EllSersic` bulge and `EllSersic` disk with centres aligned for the lens galaxy's 
 light [fixed from LIGHT PARAMETRIC PIPELINE].

 - Uses an `EllPowerLaw` model for the lens's total mass distribution [priors initialized from SOURCE 
 PARAMETRIC PIPELINE + centre unfixed from (0.0, 0.0)].

 - Uses an `Inversion` for the source's light [priors fixed from SOURCE INVERSION PIPELINE].

 - Carries the lens redshift, source redshift and `ExternalShear` of the SOURCE PIPELINE through to the MASS TOTAL 
 PIPELINE.

__Settings__:

 - Hyper: We may be using hyper features and therefore pass the result of the SOURCE INVERSION PIPELINE to use as the
 hyper dataset if required.

 - Positions: We update the positions and positions threshold using the previous model-fitting result (as described 
 in `chaining/examples/parametric_to_inversion.py`) to remove unphysical solutions from the `Inversion` model-fitting.


"""
settings_lens = al.SettingsLens(positions_threshold=0.5)


analysis = al.AnalysisImaging(
    dataset=imaging,
    hyper_dataset_result=source_inversion_results.last,
    positions=positions,
    settings_lens=settings_lens,
)

mass_results = slam.mass_total.with_lens_light(
    settings_autofit=settings_autofit,
    analysis=analysis,
    setup_hyper=setup_hyper,
    source_results=source_inversion_results,
    light_results=light_results,
    mass=af.Model(al.mp.EllPowerLaw),
    smbh=af.Model(al.mp.PointMass),
)

slam.extensions.stochastic_fit(result=mass_results.last, analysis=analysis)

import sys

sys.exit()

"""
Finish.
"""

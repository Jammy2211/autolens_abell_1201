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
    image_path=path.join(dataset_path, "image_no_lens_light_padded.fits"),
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
    path_prefix=path.join(f"{dataset_name}_no_lens_light"),
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

 - Uses a parametric `EllSersicRadialGradient` bulge and `EllExponential` disk with centres aligned for the lens
 galaxy's light.

 - Uses an `EllIsothermal` model for the lens's total mass distribution with an `ExternalShear`.
"""
analysis = al.AnalysisImaging(
    dataset=imaging,
    positions=positions,
    settings_lens=al.SettingsLens(positions_threshold=2.5)
)

source_parametric_results = slam.source_parametric.no_lens_light(
    settings_autofit=settings_autofit,
    analysis=analysis,
    setup_hyper=setup_hyper,
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
analysis = al.AnalysisImaging(
    dataset=imaging,
    positions=positions,
    settings_lens=al.SettingsLens(positions_threshold=0.5)
)

source_inversion_results = slam.source_inversion.no_lens_light(
    settings_autofit=settings_autofit,
    analysis=analysis,
    setup_hyper=setup_hyper,
    source_parametric_results=source_parametric_results,
    pixelization=al.pix.VoronoiBrightnessImage,
    regularization=al.reg.AdaptiveBrightness,
)

"""
__MASS LIGHT DARK PIPELINE (with lens light)__

The MASS LIGHT DARK PIPELINE (with lens light) uses one search to fits a complex lens mass model to a high level of 
accuracy, using the source model of the SOURCE PIPELINE and the lens light model of the LIGHT PARAMETRIC PIPELINE to 
initialize the model priors . In this example it:

 - Uses a parametric `EllSersicRadialGradient` bulge and `EllSersicRadialGradient` disk with centres aligned for the lens galaxy's 
 light and its stellar mass [12 parameters: fixed from LIGHT PARAMETRIC PIPELINE].

 - The lens galaxy's dark matter mass distribution is a `EllNFWMCRLudlow` whose centre is aligned with bulge of 
 the light and stellar mass mdoel above [5 parameters].

 - Uses an `Inversion` for the source's light [priors fixed from SOURCE INVERSION PIPELINE].

 - Carries the lens redshift, source redshift and `ExternalShear` of the SOURCE PARAMETRIC PIPELINE through to the MASS 
 LIGHT DARK PIPELINE.
 
__Settings__:

 - Hyper: We may be using hyper features and therefore pass the result of the SOURCE INVERSION PIPELINE to use as the
 hyper dataset if required.

 - Positions: We update the positions and positions threshold using the previous model-fitting result (as described 
 in `chaining/examples/parametric_to_inversion.py`) to remove unphysical solutions from the `Inversion` model-fitting.

"""
if dataset_filter == "f390w":

    settings_lens = al.SettingsLens(positions_threshold=0.4)

else:

    analysis = al.AnalysisImaging(
    dataset=imaging,
    hyper_dataset_result=source_inversion_results.last,
    positions=positions,
    settings_lens=al.SettingsLens(positions_threshold=0.5)
)

lens_bulge = af.Model(al.mp.EllSersicRadialGradient)
lens_disk = af.Model(al.mp.EllSersicRadialGradient)
lens_envelope = af.Model(al.mp.EllSersicRadialGradient)

lens_bulge.centre_0 = -0.0006154611154129346
lens_bulge.centre_1 = -0.004960662325223608
lens_bulge.elliptical_comps.elliptical_comps_0 = 0.050998359202023585
lens_bulge.elliptical_comps.elliptical_comps_1 = -0.04976623621064101
lens_bulge.intensity = 0.22526908061487236
lens_bulge.effective_radius = 0.455928074891426
lens_bulge.sersic_index = 1.2768598263929198

lens_disk.centre_0 = -0.06228295836743481
lens_disk.centre_1 = 0.12164078562455821
lens_disk.elliptical_comps.elliptical_comps_0 = 0.20043539172489935
lens_disk.elliptical_comps.elliptical_comps_1 = -0.11086131220129042
lens_disk.intensity = 0.026156558491107526
lens_disk.effective_radius = 4.5359095692722695
lens_disk.sersic_index = 1.160320152722782

lens_envelope.centre_0 = 0.3736114720401442
lens_envelope.centre_1 = -0.10689138680823886
lens_envelope.elliptical_comps.elliptical_comps_0 = 0.048392046642187124
lens_envelope.elliptical_comps.elliptical_comps_1 = -0.2563385693575622
lens_envelope.intensity = 0.002017210437540367
lens_envelope.effective_radius = 12.30895674927397
lens_envelope.sersic_index = 2.4313489183185295

dark = af.Model(al.mp.EllNFWMCRLudlow)

mass_results = slam.mass_light_dark.no_lens_light(
    settings_autofit=settings_autofit,
    analysis=analysis,
    setup_hyper=setup_hyper,
    source_results=source_inversion_results,
    lens_bulge=lens_bulge,
    lens_disk=lens_disk,
    lens_envelope=lens_envelope,
    dark=dark,
    suffix="grad",
)

slam.extensions.stochastic_fit(result=mass_results.last, analysis=analysis)

import sys

sys.exit()

"""
Finish.
"""

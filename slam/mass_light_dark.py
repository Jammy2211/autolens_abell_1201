import autofit as af
import autolens as al
from . import slam_util
from . import extensions

from typing import Optional, Tuple, Union


def with_lens_light(
    settings_autofit: af.SettingsSearch,
    analysis: Union[al.AnalysisImaging, al.AnalysisInterferometer],
    setup_hyper: al.SetupHyper,
    source_results: af.ResultsCollection,
    light_results: af.ResultsCollection,
    lens_bulge: af.Model = af.Model(al.lp.EllSersic),
    lens_disk: Optional[af.Model] = None,
    lens_envelope: Optional[af.Model] = None,
    dark: af.Model = af.Model(al.mp.EllNFWMCRLudlow),
    smbh: Optional[af.Model] = None,
    einstein_mass_range: Optional[Tuple[float, float]] = (0.01, 5.0),
    end_with_hyper_extension: bool = False,
    end_with_stochastic_extension: bool = False
) -> af.ResultsCollection:
    """
    The SLaM MASS LIGHT DARK PIPELINE for fitting imaging data with a lens light component.

    Parameters
    ----------
    analysis
        The analysis class which includes the `log_likelihood_function` and can be customized for the SLaM model-fit.
    setup_hyper
        The setup of the hyper analysis if used (e.g. hyper-galaxy noise scaling).
    source_results
        The results of the SLaM SOURCE PARAMETRIC PIPELINE or SOURCE INVERSION PIPELINE which ran before this pipeline.
    light_results
        The results of the SLaM LIGHT PARAMETRIC PIPELINE which ran before this pipeline.
    mass
        The `MassProfile` used to fit the lens galaxy mass in this pipeline.
    smbh
        The `MassProfile` used to fit the a super massive black hole in the lens galaxy.
    lens_bulge
        The `LightMassProfile` `Model` used to represent the light and stellar mass distribution of the lens galaxy's
        bulge (set to None to omit a bulge).
    lens_disk
        The `LightMassProfile` `Model` used to represent the light and stellar mass distribution of the lens galaxy's
        disk (set to None to omit a disk).
    lens_envelope
        The `LightMassProfile` `Model` used to represent the light and stellar mass distribution of the lens galaxy's
        envelope (set to None to omit an envelope).
    dark
        The `MassProfile` `Model` used to represent the dark matter distribution of the lens galaxy's (set to None to
        omit dark matter).
    einstein_mass_range
        The values a the estimate of the Einstein Mass in the LIGHT PIPELINE is multiplied by to set the lower and
        upper limits of the profile's mass-to-light ratio.
    end_with_hyper_extension
        If `True` a hyper extension is performed at the end of the pipeline. If this feature is used, you must be
        certain you have manually passed the new hyper images geneted in this search to the next pipelines.
    """

    """
    __Model + Search + Analysis + Model-Fit (Search 1)__

    In search 1 of the MASS LIGHT DARK PIPELINE we fit a lens model where:

     - The lens galaxy light and stellar mass is modeled using light and mass profiles [Priors on light model parameters
     initialized from LIGHT PIPELINE].
     - The lens galaxy dark mass is modeled using a dark mass distribution [No prior initialization].
     - The source galaxy's light is parametric or an inversion depending on the previous pipeline [Model and priors 
     initialized from SOURCE PIPELINE].

    This search aims to accurately estimate the lens mass model, using the improved mass model priors and source model 
    of the SOURCE PIPELINE and LIGHT PIPELINE.

    The `mass_to_light_ratio` prior of each light and stellar profile is set using the Einstein Mass estimate of the
    SOURCE PIPELINE, specifically using values which are 1% and 500% this estimate.

    The dark matter mass profile has the lens and source redshifts added to it, which are used to determine its mass
    from the mass-to-concentration relation of Ludlow et al.    
    """
    lens_bulge = slam_util.pass_light_and_mass_profile_priors(
        model=lens_bulge,
        result_light_component=light_results.last.model.galaxies.lens.bulge,
        result=light_results.last,
        einstein_mass_range=einstein_mass_range,
    )
    lens_disk = slam_util.pass_light_and_mass_profile_priors(
        model=lens_disk,
        result_light_component=light_results.last.model.galaxies.lens.disk,
        result=light_results.last,
        einstein_mass_range=einstein_mass_range,
    )
    lens_envelope = slam_util.pass_light_and_mass_profile_priors(
        model=lens_envelope,
        result_light_component=light_results.last.model.galaxies.lens.envelope,
        result=light_results.last,
        einstein_mass_range=einstein_mass_range,
    )

    dark.mass_at_200 = af.LogUniformPrior(lower_limit=1e11, upper_limit=1e15)
    dark.redshift_object = light_results.last.instance.galaxies.lens.redshift
    dark.redshift_source = light_results.last.instance.galaxies.source.redshift

    if smbh is not None:
        smbh.centre = lens_bulge.centre

    source = slam_util.source__from_result_model_if_parametric(
        result=source_results.last, setup_hyper=setup_hyper
    )

    model = af.Collection(
        galaxies=af.Collection(
            lens=af.Model(
                al.Galaxy,
                redshift=light_results.last.instance.galaxies.lens.redshift,
                bulge=lens_bulge,
                disk=lens_disk,
                envelope=lens_envelope,
                dark=dark,
                shear=source_results.last.model.galaxies.lens.shear,
                smbh=smbh,
                hyper_galaxy=setup_hyper.hyper_galaxy_lens_from(
                    result=light_results.last
                ),
            ),
            source=source,
        ),
        hyper_image_sky=setup_hyper.hyper_image_sky_from(
            result=light_results.last, as_model=True
        ),
        hyper_background_noise=setup_hyper.hyper_background_noise_from(
            result=light_results.last
        ),
    )

    search = af.DynestyStatic(
        name="mass_light_dark[1]_light[parametric]_mass[light_dark]_source",
        **settings_autofit.search_dict,
        nlive=300,
    )

    result_1 = search.fit(model=model, analysis=analysis, **settings_autofit.fit_dict)

    """
    __Hyper Extension__

    The above search may be extended with a hyper-search, if the SetupHyper has one or more of the following inputs:

     - The source is using an `Inversion`.
     - One or more `HyperGalaxy`'s are included.
     - The background sky is included via `hyper_image_sky` input.
     - The background noise is included via the `hyper_background_noise`.
    """

    if end_with_hyper_extension:

        result_1 = extensions.hyper_fit(
        setup_hyper=setup_hyper,
        result=result_1,
        analysis=analysis,
        include_hyper_image_sky=True,
    )

    if end_with_stochastic_extension:

        extensions.stochastic_fit(
            result=result_1, analysis=analysis, search_previous=search, **settings_autofit.fit_dict
        )

    return af.ResultsCollection([result_1])


def no_lens_light(
    settings_autofit: af.SettingsSearch,
    analysis: Union[al.AnalysisImaging, al.AnalysisInterferometer],
    setup_hyper: al.SetupHyper,
    source_results: af.ResultsCollection,
    lens_bulge: af.Model = af.Model(al.lp.EllSersic),
    lens_disk: Optional[af.Model] = None,
    lens_envelope: Optional[af.Model] = None,
    dark: af.Model = af.Model(al.mp.EllNFWMCRLudlow),
    smbh: Optional[af.Model] = None,
    einstein_mass_range: Optional[Tuple[float, float]] = (0.01, 5.0),
    end_with_hyper_extension: bool = False,
    end_with_stochastic_extension: bool = False,
    mass_clump=False,
    smbh_free_centre=False,
    smbh_free_centre_uniform=True,
    suffix: Optional[str] = None,
    nlive=300,
) -> af.ResultsCollection:
    """
    The SLaM MASS LIGHT DARK PIPELINE for fitting imaging data with a lens light component.

    Parameters
    ----------
    analysis
        The analysis class which includes the `log_likelihood_function` and can be customized for the SLaM model-fit.
    setup_hyper
        The setup of the hyper analysis if used (e.g. hyper-galaxy noise scaling).
    source_results
        The results of the SLaM SOURCE PARAMETRIC PIPELINE or SOURCE INVERSION PIPELINE which ran before this pipeline.
    light_results
        The results of the SLaM LIGHT PARAMETRIC PIPELINE which ran before this pipeline.
    mass
        The `MassProfile` used to fit the lens galaxy mass in this pipeline.
    smbh
        The `MassProfile` used to fit the a super massive black hole in the lens galaxy.
    lens_bulge
        The `LightMassProfile` `Model` used to represent the light and stellar mass distribution of the lens galaxy's
        bulge (set to None to omit a bulge).
    lens_disk
        The `LightMassProfile` `Model` used to represent the light and stellar mass distribution of the lens galaxy's
        disk (set to None to omit a disk).
    lens_envelope
        The `LightMassProfile` `Model` used to represent the light and stellar mass distribution of the lens galaxy's
        envelope (set to None to omit an envelope).
    dark
        The `MassProfile` `Model` used to represent the dark matter distribution of the lens galaxy's (set to None to
        omit dark matter).
    einstein_mass_range
        The values a the estimate of the Einstein Mass in the LIGHT PIPELINE is multiplied by to set the lower and
        upper limits of the profile's mass-to-light ratio.
    end_with_hyper_extension
        If `True` a hyper extension is performed at the end of the pipeline. If this feature is used, you must be
        certain you have manually passed the new hyper images geneted in this search to the next pipelines.
    """

    """
    __Model + Search + Analysis + Model-Fit (Search 1)__

    In search 1 of the MASS LIGHT DARK PIPELINE we fit a lens model where:

     - The lens galaxy light and stellar mass is modeled using light and mass profiles [Priors on light model parameters
     initialized from LIGHT PIPELINE].
     - The lens galaxy dark mass is modeled using a dark mass distribution [No prior initialization].
     - The source galaxy's light is parametric or an inversion depending on the previous pipeline [Model and priors 
     initialized from SOURCE PIPELINE].

    This search aims to accurately estimate the lens mass model, using the improved mass model priors and source model 
    of the SOURCE PIPELINE and LIGHT PIPELINE.

    The `mass_to_light_ratio` prior of each light and stellar profile is set using the Einstein Mass estimate of the
    SOURCE PIPELINE, specifically using values which are 1% and 500% this estimate.

    The dark matter mass profile has the lens and source redshifts added to it, which are used to determine its mass
    from the mass-to-concentration relation of Ludlow et al.    
    """

    if einstein_mass_range is not None:

        lens_bulge = slam_util.update_mass_to_light_ratio_prior(
            model=lens_bulge,
            result=source_results.last,
            einstein_mass_range=einstein_mass_range,
        )

        lens_disk = slam_util.update_mass_to_light_ratio_prior(
            model=lens_disk,
            result=source_results.last,
            einstein_mass_range=einstein_mass_range,
        )

        lens_envelope = slam_util.update_mass_to_light_ratio_prior(
            model=lens_envelope,
            result=source_results.last,
            einstein_mass_range=einstein_mass_range,
        )

    dark.mass_at_200 = af.LogUniformPrior(lower_limit=1e10, upper_limit=1e15)
    dark.redshift_object = source_results.last.instance.galaxies.lens.redshift
    dark.redshift_source = source_results.last.instance.galaxies.source.redshift

    if smbh is not None and not smbh_free_centre:

        smbh.centre = lens_bulge.centre

    elif smbh_free_centre and not smbh_free_centre_uniform:

        smbh.centre.centre_0 = af.GaussianPrior(mean=0.0, sigma=0.30)
        smbh.centre.centre_1 = af.GaussianPrior(mean=0.0, sigma=0.30)

    elif smbh_free_centre and smbh_free_centre_uniform:

        smbh.centre.centre_0 = af.UniformPrior(lower_limit=-0.15, upper_limit=0.15)
        smbh.centre.centre_1 = af.UniformPrior(lower_limit=-0.15, upper_limit=0.15)

    source = slam_util.source__from_result_model_if_parametric(
        result=source_results.last, setup_hyper=setup_hyper
    )

    if mass_clump:

        subhalo = af.Model(al.Galaxy, redshift=0.273, mass=al.mp.SphIsothermal)
        subhalo.mass.centre = (0.95, 3.6)

        model = af.Collection(
            galaxies=af.Collection(
                lens=af.Model(
                    al.Galaxy,
                    redshift=source_results.last.instance.galaxies.lens.redshift,
                    bulge=lens_bulge,
                    disk=lens_disk,
                    envelope=lens_envelope,
                    dark=dark,
                    shear=source_results.last.model.galaxies.lens.shear,
                    smbh=smbh,
                    hyper_galaxy=setup_hyper.hyper_galaxy_lens_from(
                        result=source_results.last
                    ),
                ),
                source=source,
                subhalo=subhalo,
            ),
            hyper_image_sky=setup_hyper.hyper_image_sky_from(
                result=source_results.last, as_model=True
            ),
            hyper_background_noise=setup_hyper.hyper_background_noise_from(
                result=source_results.last
            ),
        )

    else:

        model = af.Collection(
            galaxies=af.Collection(
                lens=af.Model(
                    al.Galaxy,
                    redshift=source_results.last.instance.galaxies.lens.redshift,
                    bulge=lens_bulge,
                    disk=lens_disk,
                    envelope=lens_envelope,
                    dark=dark,
                    shear=source_results.last.model.galaxies.lens.shear,
                    smbh=smbh,
                    hyper_galaxy=setup_hyper.hyper_galaxy_lens_from(
                        result=source_results.last
                    ),
                ),
                source=source,
            ),
            hyper_image_sky=setup_hyper.hyper_image_sky_from(
                result=source_results.last, as_model=True
            ),
            hyper_background_noise=setup_hyper.hyper_background_noise_from(
                result=source_results.last
            ),
        )

    name = "mass_light_dark[1]_light[fixed]_mass[light_dark]_source"

    if suffix is not None:
        name = f"{name}_{suffix}"

    search = af.DynestyStatic(name=name, **settings_autofit.search_dict, nlive=nlive)

    result_1 = search.fit(model=model, analysis=analysis, **settings_autofit.fit_dict)

    """
    __Hyper Extension__

    The above search may be extended with a hyper-search, if the SetupHyper has one or more of the following inputs:

     - The source is using an `Inversion`.
     - One or more `HyperGalaxy`'s are included.
     - The background sky is included via `hyper_image_sky` input.
     - The background noise is included via the `hyper_background_noise`.
    """

    if end_with_hyper_extension:

        result_1 = extensions.hyper_fit(
        setup_hyper=setup_hyper,
        result=result_1,
        analysis=analysis,
        include_hyper_image_sky=True,
    )

    if end_with_stochastic_extension:

        extensions.stochastic_fit(
            result=result_1, analysis=analysis, search_previous=search, **settings_autofit.fit_dict
        )

    return af.ResultsCollection([result_1])

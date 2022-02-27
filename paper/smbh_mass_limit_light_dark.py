import os
from os import path
import autolens as al
from astropy import cosmology as cosmo


def mass_from_einstein_radius(einstein_radius):

    smbh = al.mp.PointMass(einstein_radius=einstein_radius)

    grid = al.Grid2D.uniform(shape_native=(100, 100), pixel_scales=0.1)

    einstein_mass = smbh.einstein_mass_angular_from(grid=grid)

    critical_surface_density = al.util.cosmology.critical_surface_density_between_redshifts_from(
        redshift_0=0.169, redshift_1=0.451, cosmology=cosmo.Planck15
    )
    return einstein_mass * critical_surface_density


import matplotlib.pyplot as plt

"""F390W"""

smbh_einstein_radius = [
    0.2,
    0.3,
    0.4,
    0.5,
    0.6,
    0.625,
    0.65,
    0.675,
    0.7,
    0.725,
    0.75,
    0.775,
    0.8,
    0.9,
]
smbh_mass = [
    float(mass_from_einstein_radius(einstein_radius=einstein_radius))
    for einstein_radius in smbh_einstein_radius
]

f390w_evidence = [
    125639.33,  # 0.2
    125681.51,  # 0.3
    125655.42,  # 0.4
    125671.43,  # 0.5
    125614.98,  # 0.6
    125503.37,  # 0.625
    None,  # 0.65
    None,  # 0.675
    None,  # 0.7
    None,  # 0.725
    None,  # 0.75
    None,  # 0.775
    None,  # 0.8
    None,  # 0.9
]

print(smbh_mass)

f390w_pl_no_smbh = 125572.53
f390w_pl_with_smbh = 125707.20
# f390w_bpl_no_smbh = 125753.42
f390w_bpl_with_smbh = 125704.42

f390w_evidence_relative = [evi - f390w_bpl_with_smbh for evi in f390w_evidence]

"""F814W"""

smbh_mass = [
    float(mass_from_einstein_radius(einstein_radius=einstein_radius))
    for einstein_radius in smbh_einstein_radius
]

f814w_evidence = [
    78327.83,  # 0.2
    78325.41,  # 0.3
    78327.80,  # 0.4
    78329.24,  # 0.5
    78321.39,  # 0.6
    78324.05,  # 0.625
    78317.79,  # 0.65
    78131.14,  # 0.675
    None,  # 0.7
    None,  # 0.725
    None,  # 0.75
    None,  # 0.775
    None,  # 0.8
    None,  # 0.9
]

f814w_pl_no_smbh = 78301.58
f814w_pl_with_smbh = 78330.39
f814w_bpl_no_smbh = 78331.17
f814w_bpl_with_smbh = 78331.17

f814w_evidence_relative = [evi - f814w_bpl_with_smbh for evi in f814w_evidence]

plt.plot(smbh_mass, f390w_evidence_relative)
plt.scatter(smbh_mass, f390w_evidence_relative)
plt.plot(smbh_mass, f814w_evidence_relative)
plt.scatter(smbh_mass, f814w_evidence_relative)
plt.ylabel("Relative change in Bayesian Evidence")
plt.xlabel("SMBH Mass " r"$(M_{\rm \odot})$")

workspace_path = os.getcwd()
plot_path = path.join(workspace_path, "images", "total_smbh_limits")

plt.savefig(path.join(plot_path, f"total_smbh_limits.png"))
plt.savefig(path.join(plot_path, f"total_smbh_limits.pdf"))

plt.show()

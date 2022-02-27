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
    125706.18,  # 0.2
    125693.19,  # 0.3
    125686.63,  # 0.4
    125657.25,  # 0.5
    125676.59,  # 0.6
    125699.68,  # 0.625
    125655.86,  # 0.65
    125676.04,  # 0.675
    125636.15,  # 0.7
    125624.91,  # 0.725
    125648.55,  # 0.75
    125656.45,  # 0.775
    125617.61,  # 0.8
    125464.21,  # 0.9
]

print(smbh_mass)

f390w_bpl_no_smbh = 125699.90

f390w_evidence_relative = [evi - f390w_bpl_no_smbh for evi in f390w_evidence]

"""F814W"""

smbh_mass = [
    float(mass_from_einstein_radius(einstein_radius=einstein_radius))
    for einstein_radius in smbh_einstein_radius
]

f814w_evidence = [
    78331.80,  # 0.2
    78331.07,  # 0.3
    78330.86,  # 0.4
    78333.98,  # 0.5
    78328.55,  # 0.6
    78330.60,  # 0.625
    78327.52,  # 0.65
    78331.08,  # 0.675
    78330.57,  # 0.7
    78329.62,  # 0.725
    78327.57,  # 0.75
    78329.07,  # 0.775
    78325.08,  # 0.8
    78311.57,  # 0.9
]

f814w_bpl_no_smbh = 78331.17

f814w_evidence_relative = [evi - f814w_bpl_no_smbh for evi in f814w_evidence]

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

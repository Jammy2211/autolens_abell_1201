"""
Einstein Radii and Mass
=======================

This is a simple script for computing the Einstein Radii and Mass given known input parameters.

For errors, you`ll need to use the aggregator (autolens_workspace -> aggregator).
"""
# %matplotlib inline
# from pyprojroot import here
# workspace_path = str(here())
# %cd $workspace_path
# print(f"Working Directory has been set to `{workspace_path}`")

import autolens as al
from astropy import cosmology as cosmo

total_einstein_radius_pl = [0.5315, 0.3925, 0.6533]
total_einstein_radius_bpl = [0.5589, 0.4425, 0.6530]

for einstein_radius in total_einstein_radius_bpl:

    smbh = al.mp.PointMass(einstein_radius=einstein_radius)

    grid = al.Grid2D.uniform(shape_native=(100, 100), pixel_scales=0.1)

    einstein_mass = smbh.einstein_mass_angular_from(grid=grid)

    critical_surface_density = al.util.cosmology.critical_surface_density_between_redshifts_from(
        redshift_0=0.169, redshift_1=0.451, cosmology=cosmo.Planck15
    )
    einstein_mass_solar_mass = einstein_mass * critical_surface_density
    #  print("Einstein Mass (solMass) = ", einstein_mass_solar_mass)
    print("Einstein Mass (solMass) = ", "{:.4e}".format(einstein_mass_solar_mass))


for einstein_radius in total_einstein_radius_pl:

    smbh = al.mp.PointMass(einstein_radius=einstein_radius)

    grid = al.Grid2D.uniform(shape_native=(100, 100), pixel_scales=0.1)

    einstein_mass = smbh.einstein_mass_angular_from(grid=grid)

    critical_surface_density = al.util.cosmology.critical_surface_density_between_redshifts_from(
        redshift_0=0.169, redshift_1=0.451, cosmology=cosmo.Planck15
    )
    einstein_mass_solar_mass = einstein_mass * critical_surface_density
    #  print("Einstein Mass (solMass) = ", einstein_mass_solar_mass)
    print("Einstein Mass (solMass) = ", "{:.4e}".format(einstein_mass_solar_mass))

stop

light_dark_x3_einstein_radius = [0.5936, 0.5073, 0.6847]
light_dark_x2_einstein_radius = [0.3981, 0.2930, 0.4883]
light_dark_x3_grad_einstein_radius = [0.4180, 0.2515, 0.5085]
light_dark_x2_grad_einstein_radius = [0.4796, 0.3706, 0.5491]

smbh_mass_list = []

for einstein_radius in light_dark_x3_einstein_radius:

    smbh = al.mp.PointMass(einstein_radius=einstein_radius)

    grid = al.Grid2D.uniform(shape_native=(100, 100), pixel_scales=0.1)

    einstein_mass = smbh.einstein_mass_angular_from(grid=grid)

    critical_surface_density = al.util.cosmology.critical_surface_density_between_redshifts_from(
        redshift_0=0.169, redshift_1=0.451, cosmology=cosmo.Planck15
    )
    einstein_mass_solar_mass = einstein_mass * critical_surface_density

    smbh_mass_list.append(einstein_mass_solar_mass)

print(
    "Einstein Mass (solMass) = ",
    "{:.4e}^+{:.4e}_-{:.4e}".format(
        smbh_mass_list[0],
        smbh_mass_list[0] - smbh_mass_list[1],
        smbh_mass_list[2] - smbh_mass_list[0],
    ),
)
print()

smbh_mass_list = []

for einstein_radius in light_dark_x2_einstein_radius:

    smbh = al.mp.PointMass(einstein_radius=einstein_radius)

    grid = al.Grid2D.uniform(shape_native=(100, 100), pixel_scales=0.1)

    einstein_mass = smbh.einstein_mass_angular_from(grid=grid)

    critical_surface_density = al.util.cosmology.critical_surface_density_between_redshifts_from(
        redshift_0=0.169, redshift_1=0.451, cosmology=cosmo.Planck15
    )
    einstein_mass_solar_mass = einstein_mass * critical_surface_density

    smbh_mass_list.append(einstein_mass_solar_mass)

print(
    "Einstein Mass (solMass) = ",
    "{:.4e}^+{:.4e}_-{:.4e}".format(
        smbh_mass_list[0],
        smbh_mass_list[0] - smbh_mass_list[1],
        smbh_mass_list[2] - smbh_mass_list[0],
    ),
)
print()

smbh_mass_list = []

for einstein_radius in light_dark_x3_grad_einstein_radius:

    smbh = al.mp.PointMass(einstein_radius=einstein_radius)

    grid = al.Grid2D.uniform(shape_native=(100, 100), pixel_scales=0.1)

    einstein_mass = smbh.einstein_mass_angular_from(grid=grid)

    critical_surface_density = al.util.cosmology.critical_surface_density_between_redshifts_from(
        redshift_0=0.169, redshift_1=0.451, cosmology=cosmo.Planck15
    )
    einstein_mass_solar_mass = einstein_mass * critical_surface_density

    smbh_mass_list.append(einstein_mass_solar_mass)

print(
    "Einstein Mass (solMass) = ",
    "{:.4e}^+{:.4e}_-{:.4e}".format(
        smbh_mass_list[0],
        smbh_mass_list[0] - smbh_mass_list[1],
        smbh_mass_list[2] - smbh_mass_list[0],
    ),
)
print()

smbh_mass_list = []

for einstein_radius in light_dark_x2_grad_einstein_radius:

    smbh = al.mp.PointMass(einstein_radius=einstein_radius)

    grid = al.Grid2D.uniform(shape_native=(100, 100), pixel_scales=0.1)

    einstein_mass = smbh.einstein_mass_angular_from(grid=grid)

    critical_surface_density = al.util.cosmology.critical_surface_density_between_redshifts_from(
        redshift_0=0.169, redshift_1=0.451, cosmology=cosmo.Planck15
    )
    einstein_mass_solar_mass = einstein_mass * critical_surface_density

    smbh_mass_list.append(einstein_mass_solar_mass)

print(
    "Einstein Mass (solMass) = ",
    "{:.4e}^+{:.4e}_-{:.4e}".format(
        smbh_mass_list[0],
        smbh_mass_list[0] - smbh_mass_list[1],
        smbh_mass_list[2] - smbh_mass_list[0],
    ),
)
print()

# 2.5539 + 1.265 - 1.7483

Abell 1201: detection of an ultramassive black hole in a strong gravitational lens
==================================================================================

This repository contains result and scripts to accompany the paper "Abell 1201: detection of an ultramassive black hole in a strong gravitational lens":.

https://academic.oup.com/mnras/article-lookup/doi/10.1093/mnras/stad587

Structure
---------

The workspace includes the following main directories:

- ``PyAuto``: The PyAutoLens (and parent projects) source code used to generate the results and paper figures. Use
this via a GitHub clone to run the .sqlite files.
- ``paper``: The visualization scripts to produce paper plots.
- ``cosma``: The super computer scripts used to model Abell 1201.
- ``slam``: The SLaM pipelines used to model Abell 1201.

Zenodo
------

Due to GitHub file size limits the dynesty chains and images of each fit are stored at the following Zenodo link and mus tbe downloade separatley:

[INSERT ZENODO LINK]

The output folders from the Zenodo link are as follows:

- ``rjlens``: Model fit results to the image data which includes the lens light.
- ``rjlens_no_lens_light``: Model fit results to image data where the lens light has been subtracted (using the max likelihod model from ``rjlens``).
- ``rjlens_no_lens_light_fixed``: Model fit results for where the SMBH is fixed to incrementally larger values, to show how an upper limit can be placed on the SMBH.
- ``rjlens_no_lens_light_clump``: Model fit results for appendix E where the line-of-sight galaxy near the giant arc is included in the mass model.
- ``rjlens_no_lens_light_radial``: Model fit results for appendix G where the mass model has a core and large radial critical curve.
- ``rjlens_no_lens_light_pdf``: The specific results used to produce the PDF of SMBH mass.
- ``rjlens_no_lens_light_misc``: Other fits used in the paper, like those where the mass model centre is fixed to the bulge or the SMBH centre is free to vary.

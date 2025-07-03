"""Upsample each image to 2 times the resolution.

NOTE: This is important to preserve the single voxel level fine details such as the intracortical vessels
"""

import os
import subprocess
import numpy as np
import nibabel as nb
import glob

INDIR = "/Volumes/data_2/prediction_occlusion/Nifti/derivatives/sub-01/ses-01/anat/00_crop"

OUTDIR = "/Volumes/data_2/prediction_occlusion/Nifti/derivatives/sub-01/ses-01/anat/02_upsample"

# =============================================================================
NII_NAMES = sorted(glob.glob(f'{INDIR}/sub-01_ses-01_dir-*_run-0*_echo-*_me3depi_crop.nii.gz'))


PATH_PROGRAM = "/usr/local/bin/"

# =============================================================================
# Output directory
if not os.path.exists(OUTDIR):
    os.makedirs(OUTDIR)
print("  Output directory: {}\n".format(OUTDIR))

# =============================================================================
for i, f in enumerate(NII_NAMES):
    print("  Processing file {}...".format(i+1))
    # Prepare output
    basename, ext = f.split(os.extsep, 1)
    basename = os.path.basename(basename)
    out_file = os.path.join(OUTDIR, "{}_ups2X.nii.gz".format(basename))

    # Prepare command
    command = "{}/c3d {} ".format(PATH_PROGRAM, f)
    command += "-interpolation Cubic "
    command += "-resample 200% "
    command += "-o {}".format(out_file)
    # Execute command
    subprocess.run(command, shell=True, check=True)

print('\n\nFinished.')

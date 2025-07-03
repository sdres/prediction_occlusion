"""Reduce bounding box to decrease filesize.

NOTE: I have determined the ranges either in ITKSNAP or FSLEYES. The ranges
should be close to the cortex and excapsulate the whole cortex. Avoid putting
the boundaries too close (i.e. one voxel away) form the cortex. Give a bit of a
margin (e.g. 10-20 voxels).
"""

import os
import subprocess
import numpy as np
import nibabel as nb
import glob

INDIR = '/Volumes/data_2/prediction_occlusion/Nifti/sub-01/ses-01/anat'

OUTDIR = "/Volumes/data_2/prediction_occlusion/Nifti/derivatives/sub-01/ses-01/anat/00_crop"

# =============================================================================
runs = [1, 3]

for i, run_nr in enumerate(runs, start=1):
    NII_NAMES = sorted(glob.glob(f'{INDIR}/sub-01_ses-01_dir-*_run-0{run_nr}_echo-*_me3depi.nii.gz'))

    # -----------------------------------------------------------------------------
    # sub-01
    RANGE_X = [85, 405]  # xmin xsize
    RANGE_Y = [10, 560]  # ymin ysize
    RANGE_Z = [20, 359]  # zmin zsize

    # =============================================================================
    # Output directory
    if not os.path.exists(OUTDIR):
        os.makedirs(OUTDIR)
    print("  Output directory: {}\n".format(OUTDIR))

    # =============================================================================
    for i, f in enumerate(NII_NAMES):
        print("  Processing file {} ...".format(i+1))
        # Prepare output
        basename, ext = f.split(os.extsep, 1)
        basename = os.path.basename(basename)
        out_file = os.path.join(OUTDIR, "{}_crop.nii.gz".format(basename))

        # Prepare command
        command1 = "fslroi "
        command1 += "{} ".format(f)  # input
        command1 += "{} ".format(out_file)  # output
        command1 += "{} {} ".format(RANGE_X[0], RANGE_X[1])  # xmin xsize
        command1 += "{} {} ".format(RANGE_Y[0], RANGE_Y[1])  # ymin ysize
        command1 += "{} {} ".format(RANGE_Z[0], RANGE_Z[1])  # ymin ysize
        command1 += "0 -1 "  # tmin tsize
        # Execute command
        subprocess.run(command1, shell=True, check=True)

print('\n\nFinished.')

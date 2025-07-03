"""AVerage all functional runs"""

import os
import glob
import nibabel as nb
import numpy as np
import subprocess
import sys
sys.path.append('./code/misc')

# Set some paths
DATADIR = '/Users/sebastiandresbach/data/occludion_paradigm/Nifti'
DATADIR = '/Volumes/data_2/prediction_occlusion/BIDS'
# =============================================================================
# Do motion correction within runs
# =============================================================================

# Set subjects to work on
subs = ['sub-01']
# Set sessions to work on
sessions = ['ses-01']


for sub in subs:
    # Create subject-directory in derivatives if it does not exist
    subDir = f'{DATADIR}/derivatives/{sub}'

    for ses in sessions:
        # Create session-directory in derivatives if it does not exist
        sesDir = f'{subDir}/{ses}/func'


        # Look for individual runs within session
        # runs = sorted(glob.glob(f'{DATADIR}/{sub}/{ses}/func/VASO_TEST-01_23052025_VASO_fmri_nih5k_pt8_run_0*_RO_20250523154540_*.nii'))
        runs = sorted(glob.glob(f'{sesDir}/*_moco.nii.gz'))

        # Loop over individual runs
        for j, run in enumerate(runs):
            nii = nb.load(run)
            data = nii.get_fdata()

            if j == 0:
                affine = nii.affine
                header = nii.header
                new_data = data
            elif j > 0:
                new_data += data

        new_data /= len(runs)

        out_file = f'{sesDir}/sub-01_ses-ret_task-pRF_dir-AP_run-avg_part-mag_bold.nii.gz'
        img = nb.Nifti1Image(new_data, affine=affine, header=header)
        nb.save(img, out_file)

        mean = np.mean(new_data, axis=-1)
        out_file = f'{sesDir}/sub-01_ses-ret_task-pRF_dir-AP_run-avg_part-mag_bold_mean.nii.gz'
        img = nb.Nifti1Image(mean, affine=affine, header=header)
        nb.save(img, out_file)

        mask_file = f'{sesDir}/sub-01_ses-ret_task-pRF_dir-AP_run-01_part-mag_bold_moma.nii.gz'
        mask_nii = nb.load(mask_file)
        mask_data = mask_nii.get_fdata()


        mean_masked = mean * mask_data
        out_file = f'{sesDir}/sub-01_ses-ret_task-pRF_dir-AP_run-avg_part-mag_bold_mean_masked.nii.gz'
        img = nb.Nifti1Image(mean_masked, affine=affine, header=header)
        nb.save(img, out_file)

        for tp in range(new_data.shape[-1]):
            new_data[..., tp] = new_data[..., tp] * mask_data

        out_file = f'{sesDir}/sub-01_ses-ret_task-pRF_dir-AP_run-avg_part-mag_bold_masked.nii.gz'
        img = nb.Nifti1Image(new_data, affine=affine, header=header)
        nb.save(img, out_file)

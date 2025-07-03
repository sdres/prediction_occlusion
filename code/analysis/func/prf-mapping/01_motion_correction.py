"""Doing motion correction within runs"""

import ants
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
    if not os.path.exists(subDir):
        os.makedirs(subDir)
        print("Subject directory is created")

    for ses in sessions:
        # Create session-directory in derivatives if it does not exist
        sesDir = f'{subDir}/{ses}/func'
        if not os.path.exists(sesDir):
            os.makedirs(sesDir)
            print("Session directory is created")

        # Look for individual runs within session
        # runs = sorted(glob.glob(f'{DATADIR}/{sub}/{ses}/func/VASO_TEST-01_23052025_VASO_fmri_nih5k_pt8_run_0*_RO_20250523154540_*.nii'))
        runs = sorted(glob.glob(f'{DATADIR}/sub-01/ses-ret/func/sub-S1_ses-ret_task-pRF_dir-AP_run-0*_bold.nii.gz'))

        # Set folder for motion traces
        motionDir = f'{sesDir}/motionParameters'
        # Make folder to dump motion traces if it does not exist
        if not os.path.exists(motionDir):
            os.makedirs(motionDir)
            print("Motion directory is created")

        # Loop over individual runs
        for j, run in enumerate(runs):

            runnr = j + 1

            # Get a base name that we will use
            base = f'{sub}_ses-ret_task-pRF_dir-AP_run-0{runnr}_part-mag_bold'
            print(f'Processing run {base}')
            if j == 0:
                ref_base = base
            # Load data
            nii = nb.load(run)  # Load nifti
            header = nii.header  # Get header
            affine = nii.affine  # Get affine
            data = nii.get_fdata()  # Load data as array

            # Overwrite first 3 volumes with volumes 4,5,6
            new = np.concatenate((data[..., 3:6], data[..., 3:]), axis=3)
            img = nb.Nifti1Image(new, header=header, affine=affine)
            nb.save(img, f'{sesDir}/{base}.nii.gz')

            # Save mean image for quality control
            mean_img = np.mean(new, axis=-1)
            img = nb.Nifti1Image(mean_img, header=header, affine=affine)
            nb.save(img, f'{sesDir}/{base}_mean.nii.gz')

            if j == 0:
                # Make automatic motion mask
                print('Generating mask')
                command = f'3dAutomask -prefix {sesDir}/{base}_moma.nii.gz -peels 3 -dilate 2 {sesDir}/{base}.nii.gz'
                subprocess.run(command, shell=True)

                # Make reference image
                reference = np.mean(data[..., 3:6], axis=-1)
                # And save it
                img = nb.Nifti1Image(reference, header=header, affine=affine)
                nb.save(img, f'{sesDir}/{base}_reference.nii.gz')

            # Load reference in antsPy style
            fixed = ants.image_read(f'{sesDir}/{ref_base}_reference.nii.gz')

            # Get motion mask
            mask = ants.image_read(f'{sesDir}/{ref_base}_moma.nii.gz')

            # Load timeseries data in antsPy style
            ts = ants.image_read(f'{sesDir}/{base}.nii.gz')

            # Perform motion correction
            print(f'Starting with MOCO...')
            corrected = ants.motion_correction(ts, fixed=fixed, mask=mask)
            ants.image_write(corrected['motion_corrected'], f'{sesDir}/{base}_moco.nii.gz')

            # Save mean image for quality control
            nii = nb.load(f'{sesDir}/{base}_moco.nii.gz')  # Load nifti
            header = nii.header  # Get header
            affine = nii.affine  # Get affine
            data = nii.get_fdata()  # Load data as array
            mean_img = np.mean(data, axis=-1)
            img = nb.Nifti1Image(mean_img, header=header, affine=affine)
            nb.save(img, f'{sesDir}/{base}_moco_mean.nii.gz')

            # =================================================================
            # Saving motion traces
            print(f'Saving motion traces...')

            # Set folder for motion traces
            runMotionDir = f'{motionDir}/{base}'
            # Make folder to dump motion traces if it does not exist
            if not os.path.exists(runMotionDir):
                os.makedirs(runMotionDir)
                print("Runwise motion directory is created")

            # Save transformation matrix for later
            for vol, matrix in enumerate(corrected['motion_parameters']):
                mat = matrix[0]
                os.system(f"cp {mat} {runMotionDir}/{base}_vol{vol:03d}.mat")


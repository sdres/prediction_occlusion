"""Apply distortion correction to functional data"""

import subprocess
import os
import nibabel as nb
import numpy as np
import glob


# Set some paths
DATADIR = '/Volumes/data_2/prediction_occlusion/Nifti'
# DATADIR = '/Volumes/data_2/prediction_occlusion/BIDS'

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
        runs = sorted(glob.glob(f'{DATADIR}/{sub}/{ses}/func/sub-01_ses-01_task-prf_dir-PA_run-0*_bold.nii.gz'))

        # Loop over individual runs
        for j, run in enumerate(runs[::2]):

            runnr = j + 1

            # Remove last 5 volumes amd concatenate
            nii = nb.load(run)
            affine = nii.affine
            header = nii.header
            data = nii.get_fdata()

            # Get a base name that we will use
            if j == 0:
                base = f'{sub}_{ses}_task-distcorr_dir-AP_run-0{runnr}_bold'
                run_01 = data[...,:-5]
            if j == 1:
                base = f'{sub}_{ses}_task-distcorr_dir-PA_run-0{runnr}_bold'
                concat = np.concatenate((run_01, data[...,:-5]), axis=-1)

                img = nb.nifti1.Nifti1Image(concat, affine=affine, header=header)
                nb.save(img, f'{sesDir}/{sub}_{ses}_task-distcorr_dir-PAPA_run-concat_bold.nii.gz')

            print(f'Processing run {base}')


            img = nb.nifti1.Nifti1Image(data[...,:-5], affine=affine, header=header)
            nb.save(img, f'{sesDir}/{base}.nii.gz')


        # Make "design" file for topup

        with open(f"{sesDir}/{sub}_topup_info.txt", "w") as f:
            for i in range(10):
                if i < 5:
                    row = ['0', '1', '0', '0.0504896']
                else:
                    row = ['0', '-1', '0', '0.0504896']
                f.write(" ".join(row) + "\n")
        print('Calculate topup...')
        command = f'topup --imain={sesDir}/{sub}_{ses}_task-distcorr_dir-PAPA_run-concat_bold.nii.gz --datain={sesDir}/{sub}_topup_info.txt --config=b02b0.cnf --out={sesDir}/topup_results --iout={sesDir}/corrected'
        subprocess.run(command, shell=True)

        print('Apply topup...')
        command = f'applytopup --imain=/Volumes/data_2/prediction_occlusion/BIDS/derivatives/sub-01/ses-01/func/sub-01_ses-ret_task-pRF_dir-AP_run-avg_part-mag_bold.nii.gz --inindex=1 --datain={sesDir}/{sub}_topup_info.txt --topup={sesDir}/topup_results --method=jac --out=/Volumes/data_2/prediction_occlusion/BIDS/derivatives/sub-01/ses-01/func/sub-01_ses-ret_task-pRF_dir-AP_run-avg_part-mag_bold_disctorr'
        subprocess.run(command, shell=True)


        # Create new brain mask
        in_file = f'/Volumes/data_2/prediction_occlusion/BIDS/derivatives/sub-01/ses-01/func/sub-01_ses-ret_task-pRF_dir-AP_run-avg_part-mag_bold_disctorr.nii.gz'
        out_file = f'/Volumes/data_2/prediction_occlusion/BIDS/derivatives/sub-01/ses-01/func/sub-01_ses-ret_task-pRF_dir-AP_run-avg_part-mag_bold_disctorr_mask.nii.gz'

        command = f'3dAutomask -prefix {out_file} -peels 3 -dilate 2 {in_file}'
        subprocess.run(command, shell=True)

        # Apply new brain mask
        new_data = nb.load(in_file).get_fdata()
        mask_data = nb.load(out_file).get_fdata()
        for tp in range(new_data.shape[-1]):
            new_data[..., tp] = new_data[..., tp] * mask_data

        out_file = f'/Volumes/data_2/prediction_occlusion/BIDS/derivatives/sub-01/ses-01/func/sub-01_ses-ret_task-pRF_dir-AP_run-avg_part-mag_bold_disctorr_masked.nii.gz'
        img = nb.Nifti1Image(new_data[..., :-5], affine=affine, header=header)
        nb.save(img, out_file)

        command = f'fslmaths {out_file} -thr 0 {out_file}'
        subprocess.run(command, shell=True)

        mean_name = f'/Volumes/data_2/prediction_occlusion/BIDS/derivatives/sub-01/ses-01/func/sub-01_ses-ret_task-pRF_dir-AP_run-avg_part-mag_bold_disctorr_masked_mean.nii.gz'
        command = f'fslmaths {out_file} -Tmean {mean_name}'
        subprocess.run(command, shell=True)
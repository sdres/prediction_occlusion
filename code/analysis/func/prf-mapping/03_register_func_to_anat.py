"""Register functional to anatomical data"""
import subprocess
import os
import nibabel as nb
import numpy as np
import glob

# Set subjects to work on
subs = ['sub-01']
# Set sessions to work on
sessions = ['ses-01']
DATADIR = '/Volumes/data_2/prediction_occlusion/BIDS'


for sub in subs:
    # Create subject-directory in derivatives if it does not exist
    subDir = f'{DATADIR}/derivatives/{sub}'

    for ses in sessions:
        # Create session-directory in derivatives if it does not exist
        sesDir = f'{subDir}/{ses}/func'
        anat_dir = f'{DATADIR}/{sub}/ses-ret/anat'

        fixed = f'{anat_dir}/sub-S1_ses-ret_T1w.nii.gz'
        moving = f'{sesDir}/sub-01_ses-ret_task-pRF_dir-AP_run-avg_part-mag_bold_disctorr_masked_mean.nii.gz'

        # Set up ants command
        command = 'antsRegistration '
        command += f'--verbose 1 '
        command += f'--dimensionality 3 '
        command += f'--float 0 '
        command += f'--collapse-output-transforms 1 '
        command += f'--interpolation BSpline[5] '
        command += f'--output [{anat_dir}/registered1_,{anat_dir}/registered1_Warped.nii,1] '
        command += f'--use-histogram-matching 0 '
        command += f'--winsorize-image-intensities [0.005,0.995] '
        command += f'--initial-moving-transform {anat_dir}/sub-01_func-to-anat.txt '
        command += f'--transform SyN[0.1,3,0] '
        command += f'--metric CC[{fixed}, {moving},1,2] '
        command += f'--convergence [60x10,1e-6,10] '
        command += f'--shrink-factors 2x1 '
        command += f'--smoothing-sigmas 1x0vox '
        command += f'-x {anat_dir}/sub-S1_ses-ret_T1w_brain_mask_edited.nii.gz'

        # Run command
        subprocess.run(command, shell=True)

        # Prepare command to apply transform and check quality
        command = 'antsApplyTransforms '
        command += f'--interpolation BSpline[5] '
        command += f'-d 3 -i {moving} '
        command += f'-r {fixed} '
        command += f'-t {anat_dir}/registered1_1Warp.nii.gz '
        command += f'-t {anat_dir}/registered1_0GenericAffine.mat '
        command += f'-o {moving.split(".")[0]}_registered_new.nii'
        # Run command
        subprocess.run(command, shell=True)


# Apply transormation to individual volumes
fixed = f'{anat_dir}/sub-S1_ses-ret_T1w.nii.gz'

func_file = f'{sesDir}/sub-01_ses-ret_task-pRF_dir-AP_run-avg_part-mag_bold_masked.nii.gz'
nii = nb.load(func_file)
func_data = nii.get_fdata()
header = nii.header
affine = nii.affine

for vol in range(func_data.shape[-1]):
    volume_data = func_data[..., vol]
    # Save individual volumes
    vol_file = f'{sesDir}/sub-01_ses-ret_task-pRF_dir-AP_run-avg_part-mag_bold_masked_vol{vol:03d}.nii.gz'
    img = nb.Nifti1Image(volume_data, header=header, affine=affine)
    nb.save(img, vol_file)

    # Prepare command to apply transform and check quality
    command = 'antsApplyTransforms '
    command += f'--interpolation BSpline[5] '
    command += f'-d 3 -i {vol_file} '
    command += f'-r {fixed} '
    command += f'-t {anat_dir}/registered1_1Warp.nii.gz '
    command += f'-t {anat_dir}/registered1_0GenericAffine.mat '
    command += f'-o {vol_file.split(".")[0]}_registered.nii'
    # Run command
    subprocess.run(command, shell=True)


# =============================================================
# Assemble images of run
volumes = sorted(glob.glob(f'{sesDir}/sub-01_ses-ret_task-pRF_dir-AP_run-avg_part-mag_bold_masked_vol*_registered.nii'))

# Load first volume data
nii = nb.load(volumes[0])
affine = nii.affine
header = nii.header

data = nii.get_fdata()
new_shape = (data.shape[0], data.shape[1], data.shape[2], len(volumes))

new_data = np.zeros(new_shape)

for i, vol in enumerate(volumes):
    print(f'Adding volume {i}')
    data = nb.load(vol).get_fdata()

    new_data[..., i] = data

img = nb.Nifti1Image(new_data, header=header, affine=affine)
nb.save(img, f'{sesDir}/sub-01_ses-ret_task-pRF_dir-AP_run-avg_part-mag_bold_masked_registered.nii.gz')

# Remove individual volumes
# os.system(f'rm {sesDir}/sub-01_ses-ret_task-pRF_dir-AP_run-avg_part-mag_bold_masked_vol*_registered.nii')

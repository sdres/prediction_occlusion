"""Average echoes for before registration.

NOTE: The average echo image is used to determine the registration
tranformations because it has better SNR in most cases than either of the
echos.

"""
import glob
import os
import numpy as np
import nibabel as nb
import glob

INDIR = "/Volumes/data_2/prediction_occlusion/Nifti/derivatives/sub-01/ses-01/anat/02_upsample"
OUTDIR = "/Volumes/data_2/prediction_occlusion/Nifti/derivatives/sub-01/ses-01/anat/03_average_echoes"

# =============================================================================

for direction in ['AP', 'PA']:
    for run_nr in [1,3]:
        NII_NAMES = sorted(glob.glob(f'{INDIR}/sub-01_ses-01_dir-{direction}_run-0{run_nr}_echo-*_me3depi_crop_ups2X.nii.gz'))

        # =============================================================================
        # Output directory
        if not os.path.exists(OUTDIR):
            os.makedirs(OUTDIR)
        print("  Output directory: {}".format(OUTDIR))

        # =============================================================================
        # Average across echoes

        # Load first one
        nii = nb.load(NII_NAMES[0])
        data = np.squeeze(np.asanyarray(nii.dataobj))
        print(data.shape)
        # Load others
        for j in range(1, len(NII_NAMES)):
            # Load data
            nii_temp = nb.load(NII_NAMES[j])
            data += np.squeeze(np.asanyarray(nii_temp.dataobj))
            print(data.shape)
        data = data / len(NII_NAMES)

        # Make a new nifti
        img = nb.Nifti1Image(data, affine=nii.affine, header=nii.header)

        # Update data type in the header
        img.header.set_data_dtype(np.float32)

        basename, ext = nii.get_filename().split(os.extsep, 1)
        basename = os.path.basename(basename)
        out_name = f'{OUTDIR}/sub-01_ses-01_dir-{direction}_run-0{run_nr}_echo-avg_me3depi_crop_ups2X.nii.gz'
        nb.save(img, '{}.{}'.format(out_name, ext))

print('  Finished.')

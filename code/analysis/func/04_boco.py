'''

Standard VASO-pipeline things like:
- temporal upsampling
- BOLD-correction
- QA

'''

import subprocess
import glob
import os
import nibabel as nb
import numpy as np
import re
import sys

# Define current dir
ROOT = os.getcwd()
sys.path.append('./code/misc')

from findTr import *

UPFACTOR = 2  # Must be an even number so that nulled and not-nulled timecourses can match

ROOT = '/Users/sebastiandresbach/data/occludion_paradigm/Nifti'
afniPath = '/Users/sebastiandresbach/abin'
antsPath = '/Users/sebastiandresbach/ANTs/install/bin'

SUBS = ['sub-01']

# SESSIONS = ['ses-01', 'ses-02', 'ses-03', 'ses-04']
SESSIONS = ['ses-01']

for sub in SUBS:
    # Create subject-directory in derivatives if it does not exist
    subDir = f'{ROOT}/derivatives/{sub}'

    for ses in SESSIONS:
        print(f'Processing {ses}')

        outFolder = f'{ROOT}/derivatives/{sub}/{ses}/func'

        # tr = findTR(f'/Users/sebastiandresbach/data/occludion_paradigm/Nifti/derivatives/Log_protocol/run_02_INVERT_RO_ResponseLog.txt')
        # # tr = 3.8037987810094096
        # print(f'Effective TR: {tr} seconds')
        # tr = tr/UPFACTOR
        # print(f'Nominal TR will be: {tr} seconds')

        runs = sorted(
            glob.glob(
                f'{outFolder}/{sub}_{ses}_task-stim*_run-0*_part-mag_*moco.nii.gz'  # files
            )
            )


        for modality in ['bold']:
        # for modality in ['bold', 'cbv']:

            runs = sorted(
                glob.glob(
                    f'{outFolder}/{sub}_{ses}_task-stim*_run-0*_part-mag_{modality}_moco-reg.nii.gz'  # files
                )
            )
            if ses == 'ses-01':
                runs.insert(0, f'{outFolder}/{sub}_{ses}_task-stim_run-01_part-mag_{modality}_moco.nii.gz')

            for run in runs:
                runBase = os.path.basename(run).rsplit('.', 2)[0].split('_')

                tmp = runBase[0]
                for subString in runBase[1:-2]:
                    tmp = tmp + f'_{subString}'
                runBase = tmp

                print(f'Processing {runBase}_{modality}')

                tr = findTR(f'{ROOT}/derivatives/Log_protocol/{runBase[:-9]}.txt')
                # tr = 3.8037987810094096
                print(f'Effective TR: {tr} seconds')
                tr = tr / UPFACTOR
                print(f'Nominal TR will be: {tr} seconds')

                # =====================================================================
                # Temporal upsampling
                # =====================================================================
                # print(f'Temporally upsampling data with a factor of {UPFACTOR}.')
                # print(f'Input: {run}')
                # print(f'Ounput: {outFolder}/{runBase}_{modality}_intemp.nii.gz')
                # command = f'{afniPath}/3dUpsample '
                # command += f'-overwrite '
                # command += f'-datum short '
                # command += f'-prefix {outFolder}/{runBase}_{modality}_intemp.nii.gz '
                # command += f'-n {UPFACTOR} '
                # command += f'-input {run}'
                # subprocess.call(command, shell=True)

                # fix TR in header
                print('Fixing TR in header.')
                subprocess.call(
                    f'3drefit -TR {tr} '
                    + f'{outFolder}'
                    + f'/{runBase}_{modality}_intemp.nii.gz',
                    shell=True
                    )
                subprocess.call(
                    f'3drefit -TR {tr} '
                    + f'{outFolder}'
                    + f'/{runBase}_vaso_intemp.nii.gz',
                    shell=True
                    )

                # ==================================================================
                # Multiply first BOLD timepoint to match timing between cbv and bold
                # ==================================================================
                if modality == 'bold':
                    print('Multiply first BOLD volume.')

                    # The number of volumes we have to prepend depends on the
                    # upsampling factor.
                    nrPrepend = int(UPFACTOR/2)

                    nii = nb.load(
                        f'{outFolder}'
                        + f'/{runBase}_{modality}_intemp.nii.gz'
                        )

                    # Load data
                    data = nii.get_fdata()  # Get data
                    header = nii.header  # Get header
                    affine = nii.affine  # Get affine

                    # Make new array
                    newData = np.zeros(data.shape)

                    for i in range(data.shape[-1]):
                        if i < nrPrepend:
                            newData[:, :, :, i] = data[:, :, :, 0]
                        else:
                            newData[:, :, :, i] = data[:, :, :, i-nrPrepend]

                    # Save data
                    img = nb.Nifti1Image(newData.astype(int), header=header, affine=affine)
                    nb.save(img, f'{outFolder}'
                        + f'/{runBase}_{modality}_intemp.nii.gz'
                        )

            for run in runs:
                runBase = os.path.basename(run).rsplit('.', 2)[0].split('_')

                tmp = runBase[0]
                for subString in runBase[1:-2]:
                    tmp = tmp + f'_{subString}'
                runBase = tmp

                # ==========================================================================
                # BOLD-correction
                # ==========================================================================

                print(f'Doing BOCO for {runBase}')

                cbvFile = f'{outFolder}/{runBase}_cbv_intemp.nii.gz'
                boldFile = f'{outFolder}/{runBase}_bold_intemp.nii.gz'

                # Load data
                nii1 = nb.load(cbvFile).get_fdata()  # Load cbv data
                nii2 = nb.load(boldFile).get_fdata()  # Load BOLD data

                header = nb.load(cbvFile).header  # Get header
                affine = nb.load(cbvFile).affine  # Get affine

                # Divide VASO by BOLD for actual BOCO
                # new = np.divide(nii1[:,:,:,:-1], nii2[:,:,:,:-1])
                new = np.divide(nii1, nii2)

                # Clip range to -1.5 and 1.5. Values should be between 0 and 1 anyway.
                new[new > 1.5] = 1.5
                new[new < -1.5] = -1.5

                # Save bold-corrected VASO image
                img = nb.Nifti1Image(new, header=header, affine=affine)
                nb.save(
                    img, f'{outFolder}'
                    + f'/{runBase}_vaso_intemp.nii.gz'
                    )

            # # ==========================================================================
            # # QA
            # # ==========================================================================
            # print('\n')
            # print('Getting QA...')
            # for modality in ['bold_intemp', 'vaso_intemp']:
            #
            #     subprocess.run(
            #         f'{layniiPath}/LN_SKEW '
            #         + f'-input {outFolder}/{sub}_{ses}_task-stimulation_run-avg_part-mag_{modality}.nii.gz',
            #         shell=True
            #         )
            #
            # # FSL has some hickups with values between 0 and 1. Therefore, we multiply
            # # by 100.
            # subprocess.run(
            #     f'fslmaths '
            #     + f'{outFolder}/{sub}_{ses}_task-stimulation_run-avg_part-mag_vaso_intemp.nii.gz '
            #     + f'-mul 100 '
            #     + f'{outFolder}/{sub}_{ses}_task-stimulation_run-avg_part-mag_vaso_intemp.nii.gz '
            #     + f'-odt short',
            #     shell=True
            #     )

    print(f'Done with {sub}')



    # if skipLongITI:
    #
    #     # for modality in ['bold']:
    #     for modality in ['bold', 'cbv']:
    #
    #         # =====================================================================
    #         # Temporal upsampling
    #         # =====================================================================
    #
    #         command = f'{afniPath}/3dUpsample '
    #         command += f'-overwrite '
    #         command += f'-datum short '
    #         command += f'-prefix {subDir}/{sub}_ses-avg_task-stimulation_run-avg_part-mag_{modality}_intemp.nii.gz '
    #         command += f'-n {UPFACTOR} '
    #         command += f'-input {subDir}/{sub}_ses-avg_task-stimulation_run-avg_part-mag_{modality}.nii'
    #         subprocess.call(command, shell=True)
    #
    #
    #         # fix TR in header
    #         subprocess.call(
    #             f'3drefit -TR {tr} '
    #             + f'{subDir}'
    #             + f'/{sub}_ses-avg_task-stimulation_run-avg_part-mag_{modality}_intemp.nii.gz',
    #             shell=True
    #             )
    #
    #         # =====================================================================
    #         # Duplicate first BOLD timepoint to match timing between cbv and bold
    #         # =====================================================================
    #
    #         if modality == 'bold':
    #             nii = nb.load(
    #                 f'{subDir}'
    #                 + f'/{sub}_ses-avg_task-stimulation_run-avg_part-mag_{modality}_intemp.nii.gz'
    #                 )
    #
    #             # Load data
    #             data = nii.get_fdata()  # Get data
    #             header = nii.header  # Get header
    #             affine = nii.affine  # Get affine
    #
    #             # Make new array
    #             newData = np.zeros(data.shape)
    #
    #             for i in range(data.shape[-1]-1):
    #                 if i == 0:
    #                     newData[:,:,:,i]=data[:,:,:,i]
    #                 else:
    #                     newData[:,:,:,i]=data[:,:,:,i-1]
    #
    #             # Save data
    #             img = nb.Nifti1Image(newData.astype(int), header=header, affine=affine)
    #             nb.save(img, f'{subDir}'
    #                 + f'/{sub}_ses-avg_task-stimulation_run-avg_part-mag_{modality}_intemp.nii.gz'
    #                 )
    #
    #     # ==========================================================================
    #     # BOLD-correction
    #     # ==========================================================================
    #
    #     cbvFile = f'{subDir}/{sub}_ses-avg_task-stimulation_run-avg_part-mag_cbv_intemp.nii.gz'
    #     boldFile = f'{subDir}/{sub}_ses-avg_task-stimulation_run-avg_part-mag_bold_intemp.nii.gz'
    #
    #     # Load data
    #     nii1 = nb.load(cbvFile).get_fdata()  # Load cbv data
    #     nii2 = nb.load(boldFile).get_fdata()  # Load BOLD data
    #     header = nb.load(cbvFile).header  # Get header
    #     affine = nb.load(cbvFile).affine  # Get affine
    #
    #     # Divide VASO by BOLD for actual BOCO
    #     new = np.divide(nii1[:,:,:,:-1], nii2[:,:,:,:-1])
    #
    #     # Clip range to -1.5 and 1.5. Values should be between 0 and 1 anyway.
    #     new[new > 1.5] = 1.5
    #     new[new < -1.5] = -1.5
    #
    #     # Save bold-corrected VASO image
    #     img = nb.Nifti1Image(new, header=header, affine=affine)
    #     nb.save(
    #         img, f'{subDir}'
    #         + f'/{sub}_ses-avg_task-stimulation_run-avg_part-mag_vaso_intemp.nii.gz'
    #         )
    #
    #     # ==========================================================================
    #     # QA
    #     # ==========================================================================
    #     for modality in ['bold_intemp', 'vaso_intemp']:
    #         subprocess.run(
    #             f'{layniiPath}/LN_SKEW '
    #             + f'-input {subDir}/{sub}_ses-avg_task-stimulation_run-avg_part-mag_{modality}.nii.gz',
    #             shell=True
    #             )
    #
    #     # FSL has some hickups with values between 0 and 1. Therefore, we multiply
    #     # by 100.
    #     subprocess.run(
    #         f'fslmaths '
    #         + f'{subDir}/{sub}_ses-avg_task-stimulation_run-avg_part-mag_vaso_intemp.nii.gz '
    #         + f'-mul 100 '
    #         + f'{subDir}/{sub}_ses-avg_task-stimulation_run-avg_part-mag_vaso_intemp.nii.gz '
    #         + f'-odt short',
    #         shell=True
    #         )

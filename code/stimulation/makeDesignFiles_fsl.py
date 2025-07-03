"""Create design files for analysis in FSL"""

import pandas as pd
import subprocess
import os
import numpy as np
import glob


# define ROOT dir
ROOT = '/Users/sebastiandresbach/data/occludion_paradigm/Nifti'
OUT = '/Users/sebastiandresbach/data/occludion_paradigm/Nifti'
# define subjects to work on
subs = ['sub-01']

for sub in subs:
    # make folder to dump statistocal maps
    designFolder = f'{ROOT}/derivatives/design_files'

    # ==========================================================================================
    # Find sessions
    runs = sorted(glob.glob(f'{ROOT}/derivatives/{sub}/ses-*/func/{sub}_ses-*_task-*_run-0*_*part-mag*_cbv.nii.gz'))

    sessions = []
    for run in runs:
        for i in range(1, 99):
            if f'ses-0{i}' in run:
                ses = f'ses-0{i}'
                sessions.append(ses)

    # Remove duplicates
    sessions = sorted(set(sessions))

    for ses in sessions:
        runs = sorted(glob.glob(f'{ROOT}/derivatives/{sub}/{ses}/func/{sub}_{ses}_task-*_run-0*_*part-mag*_cbv.nii.gz'))
        for run in runs:
            base = os.path.basename(run).split('.')[0]

            # Get event file
            events = pd.read_csv(f'{ROOT}/{sub}/{ses}/func/{base}_events.tsv',
                                 sep='\t'
                                 )

            outFolder = f'{designFolder}/{sub}/{ses}'
            if not os.path.exists(outFolder):
                os.makedirs(outFolder)
                print("Output directory is created")

            for stimType in events['trial_type'].unique():
                tmp = events.loc[events['trial_type'] == stimType]
                tmp = tmp.round({'duration': 0})
                tmp = tmp.astype({'duration': 'int'})
                tmp['modulator'] = np.ones(len(tmp)).astype('int')
                tmp = tmp.drop('trial_type', axis=1)
                duration = np.mean(tmp['duration']).astype('int')

                outFile = f'{outFolder}/{base}.txt'

                tmp.to_csv(outFile, header=False, index=False, sep=' ')




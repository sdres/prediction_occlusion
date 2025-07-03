"""Generating event-files.tsv to be stored with data from log files"""

import numpy as np
import glob
import pandas as pd
import os
import re

# define ROOT dir
ROOT = '/Users/sebastiandresbach/data/occludion_paradigm/Nifti'
OUT = '/Users/sebastiandresbach/data/occludion_paradigm/Nifti'
# define subjects to work on
subs = ['sub-01']

for sub in subs:
    # get all runs of all sessions
    allRuns = sorted(glob.glob(f'{ROOT}/derivatives/{sub}/ses-*/func/{sub}_ses-*_task-*_run-0*_*part-mag*_cbv.nii.gz'))

    # Initiate list for sessions
    sessions = []
    # Find all sessions
    for run in allRuns:
        for i in range(1, 6):  # We had a maximum of 5 sessions
            if f'ses-0{i}' in run:
                sessions.append(f'ses-0{i}')

    sessions = set(sessions)

    for ses in sessions:
        runs = sorted(glob.glob(f'{ROOT}/derivatives/{sub}/ses-*/func/{sub}_ses-*_task-*_run-0*_*part-mag*_cbv.nii.gz'))

        for j, run in enumerate(runs, start=1):
            # get basename of current run
            base = os.path.basename(run).rsplit('.', 2)[0][:-4]
            # see session in which it was acquired

            log = f'code/stimulation/{sub}_{ses}_task-stim_run-0{j}.txt'
            logFile = pd.read_csv(log, usecols=[0])

            # Because the column definition will get hickups if empty colums are
            # present, we find line with first trigger to then load the file anew,
            # starting with that line
            for index, row in logFile.iterrows():
                if re.search('Keypress: 5', str(row)):
                    firstVolRow = index
                    break

            # define column names
            ColNames = ['startTime', 'type', 'event']
            # load logfile again, starting with first trigger
            logFile = pd.read_csv(log, sep='\t', skiprows=firstVolRow, names=ColNames)

            # initiate lists
            stimStart = []
            stimStop = []
            stimDurs = []

            # loop over lines and fine stimulation start and stop times
            for index, row in logFile.iterrows():
                if not logFile['event'][index] != logFile['event'][index]:
                    if re.search('CHECKERBOARD', logFile['event'][index]):
                        stimStart.append(logFile['startTime'][index])
                    if re.search('REST', logFile['event'][index]):
                        stimStop.append(logFile['startTime'][index])


            # convert lists to arrays and compute stimulation durations
            durs = np.asarray(stimStart) - np.asarray(stimStop)
            stim = [f'stim' for dur in durs]

            # make dataframe and save as text file
            design = pd.DataFrame({'onset': stimStart, 'duration': durs, 'trial_type': stim})
            for modality in ['bold', 'cbv']:
                design.to_csv(f'{OUT}/{sub}/{ses}/func/{base}_{modality}_events.tsv', sep='\t',  index=False)


# ==========================================================================================
# Check if events are the same within session
subs = ['sub-05', 'sub-06', 'sub-07', 'sub-09']

for sub in subs:
    # get all runs of all sessions
    allRuns = sorted(glob.glob(f'{ROOT}/{sub}/ses-*/func/{sub}_ses-*_task-*_run-0*_*part-mag*_cbv.nii.gz'))

    # Initiate list for sessions
    sessions = []
    # Find all sessions
    for run in allRuns:
        for i in range(1, 6):  # We had a maximum of 5 sessions
            if f'ses-0{i}' in run:
                sessions.append(f'ses-0{i}')

    sessions = set(sessions)

    for ses in sessions:
        runs = sorted(glob.glob(f'{ROOT}/{sub}/{ses}/func/{sub}_{ses}_task-*_run-0*_*part-mag*_cbv.nii.gz'))

        reference = pd.read_csv(f'{ROOT}/{sub}/{ses}/func/{sub}_{ses}_task-stimulation_run-01_part-mag_cbv_events.tsv')

        for run in runs[1:]:
            # get basename of current run
            base = os.path.basename(run).rsplit('.', 2)[0][:-4]
            # see session in which it was acquired

            runData = pd.read_csv(f'{ROOT}/{sub}/{ses}/func/{base}_cbv_events.tsv')
            if not np.sum(reference.trial_type == runData.trial_type) == 20:
                print(f'ERROR in {base}')

print('All good!')

import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


SUBS = ['sub-05', 'sub-06', 'sub-07', 'sub-08', 'sub-09']
ROOT = '/Users/sebastiandresbach/data/neurovascularCouplingVASO/Nifti'

# ============================================================================
# Set global plotting parameters

plt.style.use('dark_background')
PALETTE = {'bold': 'tab:orange', 'cbv': 'tab:blue'}

LW = 2
motionPalette = ['Set1', 'Set2']

FDs = pd.DataFrame()
for sub in SUBS:
    print(f'Working on {sub}')

    # =========================================================================
    # Look for sessions
    # Collectall runs across sessions (containing both nulled and notnulled images)
    allRuns = sorted(glob.glob(f'{ROOT}/{sub}/ses-*/func/{sub}_ses-0*_task-*run-0*_part-mag*.nii.gz'))

    # Initialte list for sessions
    sessions = []
    # Find all sessions
    for run in allRuns:
        for i in range(1, 6):  # We had a maximum of 2 sessions
            if f'ses-0{i}' in run:
                sessions.append(f'ses-0{i}')

    # Get rid of duplicates
    sessions = sorted(set(sessions))
    print(f'Found data from sessions: {sessions}')
    for ses in sessions:
        funcDir = f'{ROOT}/derivatives/{sub}/{ses}/func'

        # look for individual runs (containing both nulled and notnulled images)
        runs = sorted(glob.glob(f'{ROOT}/{sub}/{ses}/func/{sub}_{ses}_task-*run-0*_part-mag*.nii.gz'))

        # Set folder where motion traces were dumped
        motionDir = f'{funcDir}/motionParameters'

        for run in runs:
            base = os.path.basename(run).rsplit('.', 2)[0]

            parts = base.split('_')
            tmp = parts[0]
            for part in parts[1:-1]:
                tmp = tmp + '_' + part
            base = tmp

            print(f'Processing run {base}')

            # =========================================================================
            # Plotting FDs
            tmp = pd.read_csv(os.path.join(motionDir, f'{base}_FDs.csv'))
            tmpList = [base]*len(tmp)
            tmp['run'] = tmpList

            FDs = pd.concat((FDs, tmp))

nrVolsTotal = len(FDs)
print(f'the total numer of volumes is {nrVolsTotal}')

for modality in ['bold', 'cbv']:
    # Select volumes with excessive motion
    tmp = FDs.loc[(FDs['FD'] > 0.9) & (FDs['modality'] == modality)]

    maxMotion = np.max(tmp['FD'])
    print(f'maximum FD for {modality} is {maxMotion}')

    nrVolsExcessive = len(tmp)
    print(f'For {modality}, we found {nrVolsExcessive} volumes with motion > 0.9mm')

    nrRunsWithExcessive = len(tmp['run'].unique())

    print(f'For {modality}, {nrRunsWithExcessive} runs were affected')
percentVols = 92 / nrVolsTotal * 100
print(f'{percentVols:2f}% of volumes show motion above voxel size')

tmp = FDs.loc[(FDs['FD'] > 0.9)]

fig, (ax1) = plt.subplots(1, 1, figsize=(7.5, 5))
# sns.histplot(tmp, x='FD', linewidth=1, color='tab:red', bins=20)
sns.histplot(tmp, x='FD', linewidth=1, hue='modality', multiple='dodge', bins=20, palette=PALETTE)
ax1.set_ylabel(r'# Volumes', fontsize=24)
ax1.set_xlabel(r'FD [mm]', fontsize=24)
ax1.yaxis.set_tick_params(labelsize=18)
ax1.xaxis.set_tick_params(labelsize=18)

plt.legend(title='Modality', loc='upper right', labels=['Nulled', 'BOLD'], fontsize=18, title_fontsize=20)

fig.tight_layout()
plt.savefig(f'./results/runsGreater1mmFD.png', bbox_inches="tight")
plt.show()

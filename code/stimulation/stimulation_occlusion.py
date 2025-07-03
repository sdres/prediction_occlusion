# Import libraries

from tkinter import image_names

from psychopy import core , logging, event, visual, gui
from psychopy.hardware import keyboard
import numpy as np
import time
import os
import random
import glob
from PIL import Image
import random

def pseudorandomize_no_repeats(lst):
    if len(lst) <= 1:
        return lst[:]

    result = lst[:]
    max_attempts = 1000  # fail-safe in case of very repetitive inputs

    for _ in range(max_attempts):
        random.shuffle(result)
        if all(result[i] != result[i+1] for i in range(len(result)-1)):
            return result

    # Fallback if shuffle fails too many times
    raise ValueError("Could not pseudorandomize list without adjacent duplicates.")


# Load a keyboard to enable abortion.
defaultKeyboard = keyboard.Keyboard()

currPath = os.path.dirname(os.path.abspath(__file__))

# =============================================================================
# Initial experiment settings
# =============================================================================

# Set initial values
expName = 'occludion_paradigm'
expInfo = {'participant': 'sub-0x',
           'session': 'ses-0x',
           'run': 'run-0x'
           }

# Load a GUI in which the preset parameters can be changed.
dlg = gui.DlgFromDict(dictionary=expInfo,
                      sortKeys=False,
                      title=expName
                      )

if dlg.OK == False:
    core.quit()  # Abort if user pressed cancel

# Change directory to where this script is
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)

# Name and create specific subject folder
sub_folder_name = f"{expInfo['participant']}"
if not os.path.isdir(sub_folder_name):
    os.makedirs(sub_folder_name)

# Name and create specific session folder
ses_folder_name = f"{expInfo['participant']}/{expInfo['session']}"
if not os.path.isdir(ses_folder_name):
    os.makedirs(ses_folder_name)

# =============================================================================
# Prepare logfile

# Define a name so the log-file so it can be attributed to subject/session/run
logfile_name = (
    ses_folder_name
    + os.path.sep
    + f"{expInfo['participant']}"
    + f"_{expInfo['session']}"
    + f"_{expInfo['run']}"
    + '_occlusion'
    )

# Save a log file and set level for msg to be received
logfile = logging.LogFile(f'{logfile_name}.log', level=logging.INFO)

# Set console to receive warnings
logging.console.setLevel(logging.WARNING)

# =============================================================================
# Prepare monitor and window
# =============================================================================
# Set monitor information - CHECK WITH MPI
distance_monitor = 99  # [99] in scanner
width_monitor = 30  # [30] in scanner

#PixW = 1024.0  # [1024.0] at Leipzig Terra
#PixH = 768.0  # [768.0] at Leipzig Terra

pix_width = 1920  # [1024.0] at Maastricht
pix_height = 1200  # [768.0] at Maastricht

#
# pix_width = 1512  # MacBook
# pix_height = 982  # MacBook


#moni = monitors.Monitor('testMonitor', width=width_monitor, distance=distance_monitor)
#moni.setSizePix()  # [1920.0, 1080.0] in psychoph lab
# moni.setSizePix([pix_width, pix_height])  # [1920.0, 1080.0] in psychoph lab

# Log monitor info
logfile.write('PixelWidth=' + str(pix_width) + '\n')
logfile.write('PixelHeight=' + str(pix_height) + '\n')

# Get current date and time
date_now = time.strftime("%Y-%m-%d_%H.%M.%S")

background_color = [-0.5, -0.5, -0.5]  # from -1 (black) to 1 (white)

# Set screen:
win = visual.Window(size=(pix_width, pix_height),
                    screen=0,
                    winType='pyglet',  # winType : None, ‘pyglet’, ‘pygame’
                    allowGUI=True,
                    allowStencil=False,
                    fullscr=False,  # for psychoph lab: fullscr = True
                    # monitor=moni,
                    color=background_color,
                    colorSpace='rgb',
                    units='pix',
                    blendMode='avg'
                    )

logfile.write('Window setup done' + '\n')


# Set initial text
trigger_text = visual.TextStim(
    win=win,
    color='white',
    height=1,
    text='Experiment will start soon. Waiting for scanner'
    )

dot = visual.Circle(win, radius=6, fillColor='red', pos=(0, 0))

logfile.write('fixation setup done' + '\n')


# =============================================================================
# Initialize Visual stimulus
# =============================================================================

stim_folder = '/Users/sebastiandresbach/github/prediction_occlusion/code/stimulation/stimuli'
files = sorted(glob.glob(f'{stim_folder}/pilot/image_*.png'))

# image_ids = [np.int64(17), np.int64(11), np.int64(22), np.int64(23), np.int64(10)]
# image_ids = [np.int64(9), np.int64(17)]
# image_nrs = [10, 18]

images = []  # make list for stimuli
for i, file in enumerate(files):  # loop over frames

    img = Image.open(file)
    img_width, img_height = img.size

    # Get screen size
    # screen_width, screen_height = win.size

    # Scale the image to fit screen while maintaining aspect ratio
    scale_w = pix_width / img_width
    scale_h = pix_height / img_height
    scale = min(scale_w, scale_h)

    # Calculate new size
    new_width = int(img_width * scale)
    new_height = int(img_height * scale)

    images.append(visual.ImageStim(  # append frame to list
        win,
        pos=[0, 0],
        name=f'image {i}',
        image=file,
        units='pix',
        size=(new_width, new_height)
        )
        )


image_order = np.arange(len(files))
image_order = np.tile(image_order, 2)
image_order = pseudorandomize_no_repeats(image_order)
# print(image_order)


logfile.write(f'Image files: {files}\n')
logfile.write(f'Image order: {image_order}\n')

logfile.write('Stimuli setup done' + '\n')

# ================================================
# Set timings

nr_trials = len(image_order)

baseline_initial = 30  # In seconds
baseline_final = 30  # In seconds

duration_stimulation = 20
duration_rest = 30

duration_experiment_total = (
        baseline_initial
        + baseline_final
        + (duration_stimulation * nr_trials)
        + (duration_rest * nr_trials)
)


# ================================================
# Initialize attention task

min_number_targets = 1

# Compute maximum amount of targets
allowed_time = duration_experiment_total - 10  # Attention task will not be triggered in first or last 5 seconds
max_number_targets = int((allowed_time / 20))

# Choose random amount of targets between 2 and the maximum
target_times = []

for n in range(max_number_targets):
    if n == 0:
        target_time = np.random.uniform(10, 20, 1)
        target_times.append(target_time)
    elif n > 0:
        target_time = np.random.uniform(10, 20, 1)
        target_time += target_times[n-1]
        if not target_time > (duration_experiment_total-10):
            target_times.append(target_time)

target_time = np.random.uniform(10, 20, 1)
target_time += target_times[-1]
if not target_time > (duration_experiment_total - 10):
    if not target_time < target_times[-1]:
        target_times.append(target_time)

number_targets = len(target_times)
logfile.write(f'Target times: {target_times}\n')


nTR = 0  # total TR counter
nTR1 = 0  # even TR counter = BOLD
nTR2 = 0  # odd TR counter = VASO


# ================================================
# Start of Experiment

global_time = core.Clock()
fmri_time = core.Clock()
logging.setDefaultClock(fmri_time)

global_time.reset()
fmri_time.reset()

trial_time = core.Clock()
stimulation_time = core.Clock()

target_time = core.Clock()
detected_targets = 0

trigger_text.draw()
win.flip()
run_experiment = False

# Waiting for scanner and start at first trigger
event.waitKeys(
    keyList=["5"],
    timeStamped=False
    )

fmri_time.reset()  # reset time for experiment
target_time.reset()

nTR += 1  # update total TR counter
nTR1 += 1  # update odd (VASO) TR counter

logging.data(
    'StartOfRun '
    + str(expInfo['participant'])
    + '_'
    + str(expInfo['session'])
    + '_'
    + str(expInfo['run'])
    )

logging.data(
    'TR '
    + str(nTR)
    + ' | TR1 '
    + str(nTR1)
    + ' | TR2 '
    + str(nTR2)
    )

run_experiment = True

# Draw initial fixation dot
# fixation_dot_surround.draw()
# fixation_dot.draw()
dot.draw()
win.flip()

target_switch = False
targets_switches = 0
response_time = core.Clock()

wait_trigger = False  # wait for VASO trigger in stimulation
# Start with initial baseline
logging.data('Initial baseline' + '\n')
while fmri_time.getTime() < baseline_initial:


    if not targets_switches >= number_targets:
        if target_time.getTime() > target_times[targets_switches]:
            if targets_switches % 2 == 0:
                dot.color = 'green'
            elif targets_switches % 2 != 0:
                dot.color = 'red'
            # target_time.reset()
            targets_switches += 1
            response_time.reset()
            target_switch = True


    # Evaluate keys
    for keys in event.getKeys():
        if keys[0] in ['escape', 'q']:
            win.close()
            core.quit()

        elif keys in ['5']:
            nTR = nTR + 1
            if nTR % 2 == 1:  # odd TRs
                nTR1 = nTR1 + 1

            elif nTR % 2 == 0:
                nTR2 = nTR2 + 1

            logging.data(
                'TR '
                + str(nTR)
                + ' | TR1 '
                + str(nTR1)
                + ' | TR2 '
                + str(nTR2)
                )

wait_trigger = True
while wait_trigger:
    for keys in event.getKeys():

        if target_switch:
            if response_time.getTime() <= 2:
                if keys in ['1']:
                    logging.data('Target detected')
                    detected_targets += 1
                    target_switch = False
            elif response_time.getTime() > 2:
                logging.data('Target not detected')
                target_switch = False


        if keys[0] in ['escape', 'q']:
            win.close()
            core.quit()

        elif keys in ['5']:
            nTR = nTR + 1
            if nTR % 2 == 1:  # odd TRs
                nTR1 = nTR1 + 1
                wait_trigger = False


            elif nTR % 2 == 0:
                nTR2 = nTR2 + 1

            logging.data(
                'TR '
                + str(nTR)
                + ' | TR1 '
                + str(nTR1)
                + ' | TR2 '
                + str(nTR2)
            )

print_counter = 0
trials_done = 0
stimulus_switch = False

trial_time.reset()
stimulation_time.reset()

while run_experiment:
    # -------------------------------------------------------------------------
    # Attention task
    # -------------------------------------------------------------------------

    if not targets_switches >= number_targets:
        if target_time.getTime() > target_times[targets_switches]:
            if targets_switches % 2 == 0:
                dot.color = 'green'
            elif targets_switches % 2 != 0:
                dot.color = 'red'
            # target_time.reset()
            targets_switches += 1
            response_time.reset()
            target_switch = True

    # -------------------------------------------------------------------------
    # Present images
    # -------------------------------------------------------------------------

    # Execute stimulation part only if there is a stimulus still to be presented and none is currently presented
    if (trials_done < nr_trials) and (not stimulus_switch):

        if trial_time.getTime() >= 0 and not trial_time.getTime() > duration_stimulation:

            if not wait_trigger:
                # If we haven't started the stimulation start now
                if not stimulus_switch:

                    current_image_idx = image_order[trials_done]
                    current_image = images[current_image_idx]
                    logging.data('')
                    logging.data(f'stimulation started')
                    logging.data(f'Presenting image {files[current_image_idx]}')
                    logging.data('')

                    # Turn on switch that we are presenting a stimulus
                    stimulus_switch = True
                    wait_trigger = True

    # Check whether we reached the end of the stimulation
    if stimulation_time.getTime() > duration_stimulation:
        # Turn off stimulation if yes
        if stimulus_switch:
            stimulus_switch = False
            # sd.stop()
            logging.data('')
            logging.data(f'stimulation stopped')
            logging.data('')
            # trials_done += 1


    # Draw fixation dot and current stimulus (if applicable)
    if stimulus_switch:
        current_image.draw()

    dot.draw()
    win.flip()

    # Check whether we have reached the end of the entire trial
    # this INCLUDES the rest period
    if trial_time.getTime() > (duration_stimulation + duration_rest):
        if print_counter == 0:
            logging.data(f'waiting for trigger')
            print_counter += 1

        if not wait_trigger:
            logging.data(f'')
            logging.data(f'Trial complete')
            trial_time.reset()
            stimulation_time.reset()
            print_counter = 0
            trials_done += 1
            if trials_done > nr_trials:
                run_experiment = False


    for keys in event.getKeys():
        if target_switch:
            if response_time.getTime() <= 2:
                if keys in ['1']:
                    logging.data('Target detected')
                    detected_targets += 1
                    target_switch = False
            elif response_time.getTime() > 2:
                logging.data('Target not detected')
                target_switch = False

        if keys in ['escape', 'q']:
            win.close()
            core.quit()

        elif keys in ['5']:
            nTR = nTR + 1

            if nTR % 2 == 1:  # odd TRs
                nTR1 = nTR1 + 1
                if trial_time.getTime() > (duration_stimulation + duration_rest):
                    wait_trigger = False
            elif nTR % 2 == 0:
                nTR2 = nTR2 + 1

            logging.data('TR ' + str(nTR) + ' | TR1 ' + str(nTR1) + ' | TR2 '
                         + str(nTR2))

final_rest_time = core.Clock()

while final_rest_time.getTime() < baseline_final:

    if not targets_switches >= number_targets:
        if target_time.getTime() > target_times[targets_switches]:
            if targets_switches % 2 == 0:
                dot.color = 'green'
            elif targets_switches % 2 != 0:
                dot.color = 'red'
            # target_time.reset()
            targets_switches += 1
            response_time.reset()
            target_switch = True


    for keys in event.getKeys():
        if target_switch:
            if response_time.getTime() <= 2:
                if keys in ['1']:
                    logging.data('Target detected')
                    detected_targets += 1
                    target_switch = False
            elif response_time.getTime() > 2:
                logging.data('Target not detected')
                target_switch = False

        if keys in ['escape', 'q']:
            win.close()
            core.quit()

        elif keys in ['5']:
            nTR = nTR + 1

            if nTR % 2 == 1:  # odd TRs
                nTR1 = nTR1 + 1
                if trial_time.getTime() > (duration_stimulation + duration_rest):
                    wait_trigger = False
            elif nTR % 2 == 0:
                nTR2 = nTR2 + 1

            logging.data('TR ' + str(nTR) + ' | TR1 ' + str(nTR1) + ' | TR2 '
                         + str(nTR2))


logging.data(
    'End of run '
    + str(expInfo['participant']) + '_'
    + str(expInfo['session']) + '_'
    + str(expInfo['run']) + '\n'
    )


# %%  TARGET DETECTION RESULTS
# calculate target detection results

win.flip()

# Detection ratio
detect_ratio = detected_targets / targets_switches
logging.data('Ratio of detected targets: ' + str(detect_ratio))

# Display target detection results to participant
resultText = 'You have detected %i out of %i targets.' % (detected_targets,
                                                          targets_switches)


logging.data(resultText)
# Also display a motivational slogan
if detect_ratio >= 0.95:
    feedbackText = 'Excellent! Keep up the good work'
elif detect_ratio < 0.95 and detect_ratio >= 0.85:
    feedbackText = 'Well done! Keep up the good work'
elif detect_ratio < 0.85 and detect_ratio >= 0.65:
    feedbackText = 'Please try to focus more'
else:
    feedbackText = 'You really need to focus more!'

target_text = visual.TextStim(
    win=win,
    color='white',
    height=1,
    pos=(0.0, 0.0),
    autoLog=False,
    )

target_text.setText(resultText + '\n' + feedbackText)

logfile.write(str(resultText) + '\n')
logfile.write(str(feedbackText) + '\n')

target_text.draw()
win.flip()
core.wait(5)

win.close()
core.quit()

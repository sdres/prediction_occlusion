
from psychopy import sound, core, prefs, logging, event, visual, gui, monitors
from psychopy.hardware import emulator, keyboard
import numpy as np
import time
import os
import random
import glob
from PIL import Image

# Load a keyboard to enable abortion.
defaultKeyboard = keyboard.Keyboard()

# =============================================================================
# Prepare monitor and window
# =============================================================================

# Set monitor information - CHECK WITH MPI
distance_monitor = 99  # [99] in scanner
width_monitor = 30  # [30] in scanner


pix_width = 1512  # MacBook
pix_height = 982  # MacBook

#moni = monitors.Monitor('Built-in Display', width=width_monitor, distance=distance_monitor)

# # Log monitor info
# logfile.write('MonitorDistance=' + str(distance_monitor) + 'cm' + '\n')
# logfile.write('MonitorWidth=' + str(width_monitor) + 'cm' + '\n')
# logfile.write('PixelWidth=' + str(pix_width) + '\n')
# logfile.write('PixelHeight=' + str(pix_height) + '\n')

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



# =============================================================================
# Initialize Visual stimulus
# =============================================================================

stim_folder = '/Users/sebastiandresbach/github/prediction_occlusion/code/stimulation/stimuli'
files = sorted(glob.glob(f'{stim_folder}/image_*.png'))

# image_ids = [11]

images = []  # make list for frames
for i, file in enumerate(files):  # loop over frames
    img = Image.open(file)
    img_width, img_height = img.size

    # Get screen size
    # screen_width, screen_height = win.size

    # Scale the image to fit screen while maintaining aspect ratio
    scale_w = pix_width / img_width
    scale_h = pix_height / img_height
    scale = min(scale_w, scale_h)


    #
    # # Scale the image to fit screen while maintaining aspect ratio
    # scale_w = screen_width / img_width
    # scale_h = screen_height / img_height
    # scale = min(scale_w, scale_h)

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

current_image = images[0]
current_image.draw()

win.flip()

core.wait(4)

win.close()
core.quit()

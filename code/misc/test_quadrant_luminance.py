"""Test the luminance of the quadrants for each scene"""

from PIL import Image
import numpy as np
import glob
import matplotlib.pyplot as plt
import itertools

# Test the overall luminance of the images
images = sorted(glob.glob("code/stimulation/stimuli/image_*_nonocc.png"))
for image in images:
    img = Image.open(image)
    img_array = np.array(img)
    print(np.mean(img_array))



# ========================================================
# Test the luminance of the remaining quadrants
images = sorted(glob.glob("code/stimulation/stimuli/image_*_nonocc.png"))

luminances = []
for i, image in enumerate(images):
    print(f'image {i+1}')
    img = Image.open(image)
    img_array = np.array(img)
    h, w = img_array.shape[:2]

    img_array[h//2:, w//2:] = 0
    remaining_lum = np.mean(img_array)
    luminances.append(remaining_lum)

variance = np.std(luminances)
mean = np.mean(luminances)
median = np.median(luminances)

np.min(luminances)
np.max(luminances)
(np.max(luminances)-np.min(luminances))/2

plt.hist(luminances)
plt.show()

# Step 1: Generate all unique index pairs (i, j)
index_pairs = list(itertools.combinations(range(len(luminances)), 2))

# Step 2: Compute differences using indices
differences = [(float(luminances[j] - luminances[i])) for (i, j) in index_pairs]

# Step 3: Absolute differences
abs_differences = [abs(d) for d in differences]

# Step 4: Min, max, and midpoint of absolute differences
min_abs_diff = min(abs_differences)
max_abs_diff = max(abs_differences)
mid_abs_diff = (min_abs_diff + max_abs_diff) / 2

# Step 5: Find pair(s) closest to midpoint
closest_to_mid = []
min_distance_to_mid = float('inf')

for (i, j), diff in zip(index_pairs, differences):
    abs_diff = abs(diff)
    distance = abs(abs_diff - mid_abs_diff)
    if distance < min_distance_to_mid:
        closest_to_mid = [((i, j), (luminances[i], luminances[j]), diff)]
        min_distance_to_mid = distance
    elif distance == min_distance_to_mid:
        closest_to_mid.append(((i, j), (luminances[i], luminances[j]), diff))

# Step 6: Output result
print("Midpoint of absolute differences:", round(mid_abs_diff, 4))
print("Closest pair(s) to midpoint (showing up to 5):")
for (i, j), (v1, v2), diff in closest_to_mid[:5]:
    print(f"Indices: ({i}, {j}) → Values: ({round(v1, 3)}, {round(v2, 3)}) → Difference: {round(diff, 3)}")

# ========================================================
# Test the luminance of the quadrants
images = sorted(glob.glob("code/stimulation/stimuli/image_*_nonocc.png"))

variances = []
for i, image in enumerate(images[:1]):
    print(f'image {i+1}')
    img = Image.open(image)
    img_array = np.array(img)
    h, w = img_array.shape[:2]
    # Set top-left quadrant to 0 (black)

    q1 = np.mean(img_array[:h//2, :w//2])
    q2 = np.mean(img_array[h//2:, w//2:])
    q3 = np.mean(img_array[:h//2, w//2:])
    q4 = np.mean(img_array[h//2:, :w//2])

    im = Image.fromarray(img_array[h//2:, w//2:])
    im.save("code/stimulation/stimuli/image_01_nonocc_q2.png")

    # Determine variance in luminance across quadrants
    quadrant_luminances = np.asarray([q1, q2, q3, q4])
    variance = np.var(quadrant_luminances)
    variances.append(variance)

variances = np.asarray(variances)

# N images with smalest variance
n = 5
idx = np.argpartition(variances, n)
vals = variances[idx[:n]]

idxs = [np.where(variances == i)[0][0] for i in vals]

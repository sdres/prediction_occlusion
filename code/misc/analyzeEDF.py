import re
import numpy as np
import matplotlib.pyplot as plt

# ---- CONFIG ----
asc_file = '/Users/sebastiandresbach/Downloads/SD1_20250618T122156.asc'  # <- Replace with your actual file

res_x, res_y = 1920, 1080
diag_inch = 23.8
dist_cm = 63
TR_sec = 1
deviation_thresh = 1  # degrees

# ---- LOAD AND PARSE ASC FILE ----
timestamps, gx, gy = [], [], []
bad_count = 0

with open(asc_file, 'r') as f:
    for line in f:
        match = re.match(r'^(\d+)\s+([\d.]+)\s+([\d.]+)', line)
        if match:
            t_str, x_str, y_str = match.groups()
            if x_str != '.' and y_str != '.':
                try:
                    t = float(t_str)
                    x = float(x_str)
                    y = float(y_str)
                    if x > 0 and y > 0:
                        timestamps.append(t)
                        gx.append(x)
                        gy.append(y)
                except ValueError:
                    bad_count += 1
            else:
                bad_count += 1

print(f"Loaded {len(gx)} valid samples, skipped {bad_count} invalid.")

timestamps = np.array(timestamps)
gx = np.array(gx)
gy = np.array(gy)

# ---- SCREEN GEOMETRY ----
aspect = res_x / res_y
diag_cm = diag_inch * 2.54
height_cm = (diag_cm**2 / (1 + aspect**2))**0.5
width_cm = height_cm * aspect
px_per_cm_x = res_x / width_cm
px_per_cm_y = res_y / height_cm

# ---- CONVERT TO VISUAL ANGLE (DEGREES) ----
x_cm = (gx - res_x / 2) / px_per_cm_x
y_cm = (gy - res_y / 2) / px_per_cm_y
x_deg = np.degrees(np.arctan2(x_cm, dist_cm))
y_deg = np.degrees(np.arctan2(y_cm, dist_cm))

# ---- SAMPLING RATE AND DURATION ----
dt = np.diff(timestamps)
sampling_rate = round(1000 / np.median(dt))
duration_sec = (timestamps[-1] - timestamps[0]) / 1000
print(f"Estimated sampling rate: {sampling_rate} Hz")
print(f"Total duration: {duration_sec:.2f} seconds")

# ---- MEAN GAZE PER SECOND ----
t0 = timestamps[0]
t_rel = (timestamps - t0) / 1000
n_sec = int(np.ceil(duration_sec))
mean_per_sec = np.full((n_sec, 2), np.nan)

for sec in range(n_sec):
    idx = (t_rel >= sec) & (t_rel < sec + 1)
    if np.any(idx):
        mean_per_sec[sec, 0] = np.nanmean(x_deg[idx])
        mean_per_sec[sec, 1] = np.nanmean(y_deg[idx])

# ---- MEAN GAZE PER TR & DEVIATION CHECK ----
n_trs = int(np.ceil(duration_sec / TR_sec))
deviation_flags = np.zeros(n_trs, dtype=bool)

for tr in range(n_trs):
    t_start = tr * TR_sec
    t_end = (tr + 1) * TR_sec
    idx = (t_rel >= t_start) & (t_rel < t_end)
    
    if np.any(idx):
        mean_x = np.nanmean(x_deg[idx])
        mean_y = np.nanmean(y_deg[idx])
        if abs(mean_x) > deviation_thresh or abs(mean_y) > deviation_thresh:
            deviation_flags[tr] = True

n_deviated = deviation_flags.sum()
perc_deviated = 100 * n_deviated / n_trs
print(f"TRs with mean gaze > {deviation_thresh}°: {n_deviated}/{n_trs} ({perc_deviated:.1f}%)")

# ---- PLOTTING ----
fig, axs = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

# Plot 1: Mean gaze per second
axs[0].plot(range(n_sec), mean_per_sec[:, 0], label='X°', color='blue')
axs[0].plot(range(n_sec), mean_per_sec[:, 1], label='Y°', color='red')
axs[0].set_ylabel('Mean gaze (°)')
axs[0].legend()
axs[0].set_title('Mean Gaze Position Over Time')

# Plot 2: Deviation flags per TR
tr_times = np.arange(n_trs) * TR_sec + TR_sec / 2
axs[1].stem(tr_times, deviation_flags.astype(int), basefmt=" ", linefmt='k-', markerfmt='ko')
axs[1].set_ylim(-0.1, 1.1)
axs[1].set_ylabel(f'Mean > {deviation_thresh}°')
axs[1].set_xlabel('Time (s)')
axs[1].set_title(f'TRs with Mean Gaze Deviation > {deviation_thresh}° ({perc_deviated:.1f}%)')

plt.tight_layout()
plt.show()
# Meeting notes
Here, notes will be collected of things that were discussed, have to be done, or may be important in the future

## Meeting Ale & Seb & Renzo 30.04.2025 afternoon
We discussed the sequence with Renzo. A new version VASO version (v. nih5k) exists and Renzo has tested protocol (protocol pdf added to scanning folder).
- Key parameters are 0.8 mm iso, 26 slices, 3677 ms pairTR
- FA 45 degrees is ambitious (SAR) - might work with pTx, might lead to issues with sTx
- Dual polarity is implemented, and we discussed to acquire data in 4 ways with averaging in preprocessing (e.g. beta maps):
  1. left (regular)
  2. right (invert RO in special card)
  3. alternating, left first (dual polarity in special card)
  4. alternating, right first (dual polarity AND invert RO in special card)

Finally, we iterated the morning discussion with Jan. We were both sceptical whether the naturalistic images within the log-bar stimulus for prf mapping would not drag attention (and saccades).
We will test this with the eye tracker.

We set the following TODOs:
- ~~Seb contacts Luca as pilot participant~~
- ~~Seb sends email to Tyler~~
- ~~Seb checks visual angle on screen in original Muckli study~~
  - In Smith & Muckli 2010 The entire stimulus spanned 22.5 × 18° of visual angle
  - occluded region spanned 11 × 9° of visual angle
  - 20 % smaller in Muckli 2015 (so 17.6 × 14.4 ° of visual angle) 
- Ale schedules practical session with Jan about eyetracker and prf mapping
- Ale and Seb check eye tracker hardware in Maastricht and Leipzig
- ~~Ale imports protocol on 7T (maybe requires new sequence version install)~~
- Seb asks Rainer about potential complications with respect to screen size (06.05.2025)

## Meeting Jan & Ale & Seb 30.04.2025 morning
We discussed retinotopic mapping approaches and how to best collect the data. Briefly:
1. Select participants that are experienced with psychophysics experiments
2. Use a fixation grid instead of a fixation cross (see Puckett et al. [2016] Figure 1.)
3. Screen participants (important!)
   - Use the actual fixation task (dot changing color) together with the prf mapping stimuli
   - Use eyetracking (outside the scanner)
   - Whenever participant moves eyes too much (threshold TBD, maybe 1/2 deg away from center) let them know. Jan talked about "trials" in his case, which does not apply here. but maybe we can use simply time?
4. We ditched the idea of doing the curser tracking task (presented by Jan in the context of crowding task during welcome presentation)
5. Also for main experiment, present stimuli (or occluded quadrant) in random locations to prevent "predictive" saccade
6. The prf mapping will be done with the "new" log-bar stimulus (greater width in periphery and filled with naturalistic images). Takes approx. 5 min/run
7. Acquisition will be whole brain 1.8 mm isotropic GE-BOLD

Papers that were mentioned:
Benson, Winawer (2018) Bayesian model for prf mapping 
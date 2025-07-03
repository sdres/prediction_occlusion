#!/bin/bash


# step 1
docker run --rm -it \
-v /Volumes/data_2/prediction_occlusion:/base nipy/heudiconv:latest \
-d /base/DICOM/sub-{subject}/ses-{session}/*.IMA \
-o /base/Nifti/ \
-f convertall \
-s 01 \
-ss 01 \
-c none \
--overwrite


# step 2
# make heuristics file


# step 3
docker run --rm -it \
-v /Volumes/data_2/prediction_occlusion:/base nipy/heudiconv:latest \
-d /base/DICOM/sub-{subject}/ses-{session}/*.IMA \
-o /base/Nifti/ \
-f /base/Nifti/code/heudiconv_heuristic.py \
-s 01 \
-ss 01 \
-c dcm2niix \
-b --overwrite

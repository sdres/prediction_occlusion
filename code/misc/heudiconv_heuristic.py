#!/usr/bin/python
import os


def create_key(template, outtype=('nii.gz',), annotation_classes=None):
    if template is None or not template:
        raise ValueError('Template must be a valid format string')
    return template, outtype, annotation_classes


def infotodict(seqinfo):

    """Heuristic evaluator for determining which runs belong where
    allowed template fields - follow python string module:
    item: index within category
    subject: participant id
    seqitem: run number during scanning
    subindex: sub index within group
    """

    # MP2RAGE
    mp2rageInv1Mag = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_inv-1_run-0{item:01d}_MP2RAGE')
    # mp2rageInv1Phase = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_inv-1_part-phase_run-0{item:01d}_MP2RAGE')
    mp2rageInv2Mag = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_inv-2_run-0{item:01d}_MP2RAGE')
    # mp2rageInv2Phase = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_inv-2_part-phase_run-0{item:01d}_MP2RAGE')
    mp2rageUniMag = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_uni_run-0{item:01d}_MP2RAGE')
    # mp2rageUniPhase = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_uni_part-phase_run-0{item:01d}_MP2RAGE')
    mp2rageT1Mag = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_t1_run-0{item:01d}_MP2RAGE')
    # mp2rageT1Phase = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_t1_part-phase_run-0{item:01d}_MP2RAGE')
    #
    # PRF
    # For the distortion correction
    prf_magn_pa = create_key(
        'sub-{subject}/{session}/func/sub-{subject}_{session}_task-prf_dir-PA_run-0{item:01d}_part-mag_bold')
    # For the main runs
    prf_magn = create_key(
        'sub-{subject}/{session}/func/sub-{subject}_{session}_task-prf_dir-AP_run-0{item:01d}_part-mag_bold')

    # ME 3D-EPI
    me3depi_mag_ap = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_dir-AP_run-0{item:01d}_part-mag_me3depi')
    me3depi_mag_pa = create_key(
        'sub-{subject}/{session}/anat/sub-{subject}_{session}_dir-PA_run-0{item:01d}_part-mag_me3depi')

    # # VASO
    # vasoMagn = create_key('sub-{subject}/{session}/func/sub-{subject}_{session}_task-stim_run-0{item:01d}_part-mag_cbv')
    # # vasoPhs = create_key('sub-{subject}/{session}/func/sub-{subject}_{session}_task-stimulation_run-0{item:01d}_part-phase_cbv')
    # boldMagn = create_key('sub-{subject}/{session}/func/sub-{subject}_{session}_task-stim_run-0{item:01d}_part-mag_bold')
    # # boldPhs = create_key('sub-{subject}/{session}/func/sub-{subject}_{session}_task-stimulation_run-0{item:01d}_part-phase_bold')

    # VASO


    info = {
            # PRF mapping
            prf_magn_pa: [],
            prf_magn: [],

            # # High-res FUNC
            # vasoMagn: [],
            # boldMagn:[],
            #
            # ME 3D-EPI
            me3depi_mag_ap: [],
            me3depi_mag_pa: [],

            # MP2RAGE
            mp2rageInv1Mag: [],
            # mp2rageInv1Phase: [],
            mp2rageInv2Mag: [],
            # mp2rageInv2Phase: [],
            mp2rageUniMag: [],
            # mp2rageUniPhase: [],
            mp2rageT1Mag: [],
            # mp2rageT1Phase: []
            }

    for idx, s in enumerate(seqinfo):
        if s.protocol_name == 'PRF_cmrr_mbep2d_bold_1pt8_G2_MB3_PA_run1':
            if s.dim4 == 10:
                info[prf_magn_pa].append(s.series_id)

        elif s.protocol_name == 'PRF_cmrr_mbep2d_bold_1pt8_G2_MB3_AP_run1':
            if s.dim4 == 300:
                info[prf_magn].append(s.series_id)


        elif s.series_description == 'dzne_ep3d_0p35_iso_3_echo_not_RO':
            info[me3depi_mag_ap].append(s.series_id)
        elif s.series_description == 'dzne_ep3d_0p35_iso_3_echo_invRO':
            info[me3depi_mag_pa].append(s.series_id)

        # MP2RAGE
        elif s.dim3 == 240:
            if 'INV1' in s.series_description:
                info[mp2rageInv1Mag].append(s.series_id)
            elif 'INV2' in s.series_description:
                info[mp2rageInv2Mag].append(s.series_id)
            elif 'UNI' in s.series_description:
                info[mp2rageUniMag].append(s.series_id)
            elif 'T1' in s.series_description:
                info[mp2rageT1Mag].append(s.series_id)


    return info
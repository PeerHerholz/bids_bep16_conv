import argparse
import os
from pathlib import Path
from bids_bep16_conv.converters import dipy_dti, dipy_csd
from bids_bep16_conv.utils import validate_input_dir, create_dataset_description
from bids import BIDSLayout


# define parser to collect required inputs
def get_parser():

    __version__ = open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                    '_version.py')).read()

    parser = argparse.ArgumentParser(description='a BIDS app for converting DWI pipeline outputs to BEP16-conform derivative datasets')
    parser.add_argument('bids_dir', action='store', type=Path, help='The directory with the input dataset '
                        'formatted according to the BIDS standard.')
    parser.add_argument('analysis_level', help='Level of the analysis that will be performed. '
                        'Multiple participant level analyses can be run independently '
                        '(in parallel) using the same output_dir.',
                        choices=['participant', 'group'])
    parser.add_argument('--participant_label',
                        help='The label(s) of the participant(s) that should be analyzed. '
                        'The label corresponds to sub-<participant_label> from the BIDS spec '
                        '(so it does not include "sub-"). If this parameter is not '
                        'provided all subjects should be analyzed. Multiple '
                        'participants can be specified with a space separated list.',
                        nargs="+")
    parser.add_argument('--software', help='Software package to use.',
                        choices=['dipy', 'mrtrix'])
    parser.add_argument('--analysis', help='Analaysis to run.',
                        choices=['DTI', 'CSD'])
    parser.add_argument('--skip_bids_validation', default=True,
                        help='Assume the input dataset is BIDS compliant and skip the validation \
                             (default: True).',
                        action="store_true")
    parser.add_argument('-v', '--version', action='version',
                        version='BIDS-App version {}'.format(__version__))

    return parser


# define the CLI
def run_bids_bep16_conv():

    # get arguments from parser
    args = get_parser().parse_args()

    # special variable set in the container
    if os.getenv('IS_DOCKER'):
        exec_env = 'singularity'
        cgroup = Path('/proc/1/cgroup')
        if cgroup.exists() and 'docker' in cgroup.read_text():
            exec_env = 'docker'
    else:
        exec_env = 'local'

    # check if BIDS validation should be run or skipped
    if args.skip_bids_validation:
        print("Input data will not be checked for BIDS compliance.")
    else:
        print("Making sure the input data is BIDS compliant "
              "(warnings can be ignored in most cases).")
        validate_input_dir(exec_env, args.bids_dir, args.participant_label)

    # intialize BIDS dataset layout
    layout = BIDSLayout(args.bids_dir, derivatives=True)

    # intialize empty subject list
    subjects_to_analyze = []

    # check analysis level and gather subject list
    if args.analysis_level == "participant":
        if args.participant_label:
            subjects_to_analyze = args.participant_label
        else:
            print("No participant label indicated. Please do so.")
    else:
        subjects_to_analyze = layout.get(return_type='id', target='subject')

    # check if indicated participants are missing and if so, provide a list of them
    list_part_prob = []
    for part in subjects_to_analyze:
        if part not in layout.get_subjects():
            list_part_prob.append(part)
    if len(list_part_prob) >= 1:
        raise Exception("The participant(s) you indicated are not present in the BIDS dataset, please check again."
                        "This refers to:")
        print(list_part_prob)

    # gather sessions that should be analyzed and provide a respective update
    sessions_to_analyze = layout.get(return_type='id', target='session')

    if not sessions_to_analyze:
        print('Processing data from one session.')
    else:
        print('Processing data from %s sessions:' % str(len(sessions_to_analyze)))
        print(sessions_to_analyze)

    # loop over subjects and run analysis, as well as subsequent output conversion
    for subject_label in subjects_to_analyze:
        # get needed files and check if data from multiple sessions should be gathered
        if not sessions_to_analyze:
            list_dwi_nii_gz = layout.get(subject=subject_label, extension='nii.gz', suffix='dwi',
                                         return_type='filename')
            list_dwi_bval = layout.get(subject=subject_label, extension='bval', suffix='dwi',
                                       return_type='filename')
            list_dwi_bvec = layout.get(subject=subject_label, extension='bvec', suffix='dwi',
                                       return_type='filename')
            list_dwi_mask = layout.get(subject=subject_label, extension='nii.gz', suffix='mask',
                                       return_type='filename')
        else:
            list_dwi_nii_gz = layout.get(subject=subject_label, extension='nii.gz', suffix='dwi',
                                         return_type='filename', session=sessions_to_analyze)
            list_dwi_bval = layout.get(subject=subject_label, extension='bval', suffix='dwi',
                                       return_type='filename', session=sessions_to_analyze)
            list_dwi_bvec = layout.get(subject=subject_label, extension='bvec', suffix='dwi',
                                       return_type='filename', session=sessions_to_analyze)
            list_dwi_mask = layout.get(subject=subject_label, extension='nii.gz', suffix='mask',
                                       return_type='filename', session=sessions_to_analyze)

        # loop over respective sets of files
        for dwi_nii_gz, bval, bvec, mask in zip(list_dwi_nii_gz, list_dwi_bval, list_dwi_bvec, list_dwi_mask):
            # check if software argument was provided, if not raise error and indicate problem
            if args.software is None:
                raise Exception("Please indicate the software you want to use for processing."
                                "For DIPY use: --software dipy and for mrtrix use: --software mrtrix.")
            # check if analysis argument was provided, if not raise error and indicate problem
            if args.analysis is None:
                raise Exception("Please indicate the analysis you want to run."
                                "For DTI use: --analysis DTI")

            # if dipy was selected, run DIPY and define output path in derivatives folder respectively
            if args.software == "dipy":
                outpath = str(args.bids_dir) + '/derivatives/dipy/sub-' + subject_label
                if sessions_to_analyze:
                    outpath += '/ses-' + dwi_nii_gz.split('/')[-1].split('_')[1].split('-')[1] + '/'
                # if DTI analysis should be run, setup and run dipy_dti function
                if args.analysis == "DTI":
                    dipy_dti(dwi_nii_gz, bval, bvec,
                             mask, outpath)
                # if CSD analysis should be run, setup and run dipy_csd function
                elif args.analysis == "CSD":
                    dipy_csd(dwi_nii_gz, bval, bvec,
                             mask, outpath)
                # create the respective dataset_description.json file for the run analysis
                create_dataset_description("dipy", args.bids_dir)


# run the CLI
if __name__ == "__main__":

    run_bids_bep16_conv()

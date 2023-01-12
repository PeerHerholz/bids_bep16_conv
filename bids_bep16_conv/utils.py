import os
import sys
from pathlib import Path
import json
import importlib_resources
from shutil import copy


def validate_input_dir(exec_env, bids_dir, participant_label):
    """
    Validate BIDS directory and structure via the BIDS-validator.
    
    Functionality copied from fmriprep.

    Parameters
    ----------
    exec_env : str
        Environment bids_bep16_conv is run in.
    bids_dir : str
        Path to BIDS root directory.
    participant_label: str
        Label(s) of subject to be checked (without 'sub-').
    """

    import tempfile
    import subprocess
    validator_config_dict = {
        "ignore": [
            "EVENTS_COLUMN_ONSET",
            "EVENTS_COLUMN_DURATION",
            "TSV_EQUAL_ROWS",
            "TSV_EMPTY_CELL",
            "TSV_IMPROPER_NA",
            "VOLUME_COUNT_MISMATCH",
            "BVAL_MULTIPLE_ROWS",
            "BVEC_NUMBER_ROWS",
            "DWI_MISSING_BVAL",
            "INCONSISTENT_SUBJECTS",
            "INCONSISTENT_PARAMETERS",
            "BVEC_ROW_LENGTH",
            "B_FILE",
            "PARTICIPANT_ID_COLUMN",
            "PARTICIPANT_ID_MISMATCH",
            "TASK_NAME_MUST_DEFINE",
            "PHENOTYPE_SUBJECTS_MISSING",
            "STIMULUS_FILE_MISSING",
            "DWI_MISSING_BVEC",
            "EVENTS_TSV_MISSING",
            "TSV_IMPROPER_NA",
            "ACQTIME_FMT",
            "Participants age 89 or higher",
            "DATASET_DESCRIPTION_JSON_MISSING",
            "FILENAME_COLUMN",
            "WRONG_NEW_LINE",
            "MISSING_TSV_COLUMN_CHANNELS",
            "MISSING_TSV_COLUMN_IEEG_CHANNELS",
            "MISSING_TSV_COLUMN_IEEG_ELECTRODES",
            "UNUSED_STIMULUS",
            "CHANNELS_COLUMN_SFREQ",
            "CHANNELS_COLUMN_LOWCUT",
            "CHANNELS_COLUMN_HIGHCUT",
            "CHANNELS_COLUMN_NOTCH",
            "CUSTOM_COLUMN_WITHOUT_DESCRIPTION",
            "ACQTIME_FMT",
            "SUSPICIOUSLY_LONG_EVENT_DESIGN",
            "SUSPICIOUSLY_SHORT_EVENT_DESIGN",
            "MALFORMED_BVEC",
            "MALFORMED_BVAL",
            "MISSING_TSV_COLUMN_EEG_ELECTRODES",
            "MISSING_SESSION"
        ],
        "error": ["NO_T1W"],
        "ignoredFiles": ['/dataset_description.json', '/participants.tsv']
    }
    # Limit validation only to data from requested participants
    if participant_label:
        all_subs = set([s.name[4:] for s in bids_dir.glob('sub-*')])
        selected_subs = set([s[4:] if s.startswith('sub-') else s
                             for s in participant_label])
        bad_labels = selected_subs.difference(all_subs)
        if bad_labels:
            error_msg = 'Data for requested participant(s) label(s) not found. Could ' \
                        'not find data for participant(s): %s. Please verify the requested ' \
                        'participant labels.'
            if exec_env == 'docker':
                error_msg += ' This error can be caused by the input data not being ' \
                             'accessible inside the docker container. Please make sure all ' \
                             'volumes are mounted properly (see https://docs.docker.com/' \
                             'engine/reference/commandline/run/#mount-volume--v---read-only)'
            if exec_env == 'singularity':
                error_msg += ' This error can be caused by the input data not being ' \
                             'accessible inside the singularity container. Please make sure ' \
                             'all paths are mapped properly (see https://www.sylabs.io/' \
                             'guides/3.0/user-guide/bind_paths_and_mounts.html)'
            raise RuntimeError(error_msg % ','.join(bad_labels))

        ignored_subs = all_subs.difference(selected_subs)
        if ignored_subs:
            for sub in ignored_subs:
                validator_config_dict["ignoredFiles"].append("/sub-%s/**" % sub)
    with tempfile.NamedTemporaryFile('w+') as temp:
        temp.write(json.dumps(validator_config_dict))
        temp.flush()
        try:
            subprocess.check_call(['bids-validator', bids_dir, '-c', temp.name])
        except FileNotFoundError:
            print("bids-validator does not appear to be installed", file=sys.stderr)


def create_dataset_description(software, out_dir):
    """
    Create dataset_description.json file for applied software/pipeline.

    Parameters
    ----------
    software : str
        The applied software.
    bids_dir : str
        Path to BIDS root directory.

    Returns
    -------
    Generated dataset_description.json file in derivatives/<software> directory
    under specified BIDS root directory.

    Examples
    --------
    Create dataset_description.json for DIPY.

    >>> create_dataset_description('dipy','/home/user/BIDS_dataset/derivatives')
    """

    # define the output path under derivatives within BIDS root
    dataset_description_path = Path(os.path.join(out_dir, software))

    # check if output path exists, if not create it
    if not dataset_description_path.exists():
        os.makedirs(dataset_description_path)

    # define empty dictionary
    dataset_description = {}

    # if dipy was used, fill dictionary with respectively needed information
    if software == 'dipy':
        import dipy
        
        dataset_description["Name"] = "Dipy output"
        dataset_description["BIDSVersion"] = "PLEASE ADD"
        dataset_description["PipelineDescription"] = {"Name" : "Dipy",
                                                      "Version": dipy.__version__,
                                                      "CodeURL": "https://github.com/dipy/dipy"}
        dataset_description["HowToAcknowledge"] = "PLEASE ADD"
        dataset_description["SourceDatasetsURLs"] = "PLEASE ADD"
        dataset_description["License"] = "PLEASE ADD"
        
    # save the created dictionary as json file in specified output path
    with open(str(str(dataset_description_path) + '/dataset_description.json'), 'w') as outfile:
        json.dump(dataset_description, outfile, indent=4)


def copy_BEP16_metadata_json_template(path):
    """
    Copy the BEP16 metadata template to a dedicated location.

    Parameters
    ----------
    path : str
        Path to where the template should be copied.

    Returns
    -------
    A message indicating from where the template will be copied to which path.

    Examples
    --------
    Copy the template to the `Desktop` located under `/home/user/Desktop`.

    >>> copy_BEP16_metadata_json_template('/home/user/Desktop')
    """

    # get the path of the BEP16 metadata template
    json_metadata = importlib_resources.files(__name__).joinpath('data/metadata_templates/BEP16_metadata_template.json')

    # print a little informative message
    print('JSON metadata template is located: %s & will be copied to: %s' % (json_metadata, path))

    # copy the BEP16 metadata template to the desired path
    copy(json_metadata, path)

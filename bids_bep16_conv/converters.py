import os
import json
import warnings
import importlib_resources
import dipy
import mrtrix3
import nibabel as nb


def dipy_bep16_dti(dwi_nii_gz, bval, bvec, mask, out_path, json_metadata=None):
    """
    Restructure DIPY DTI outcomes following BIDS BEP16 conventions.

    Parameters
    ----------
    dwi_nii_gz : str
        The `_dwi.nii(.gz)` file of the preprocessed DWI used as input for DIPY.
    bval : str
        The `_dwi.bval` file of the preprocessed DWI used as input for DIPY.
    bvec : str
        The `_dwi.bvec` file of the preprocessed DWI used as input for DIPY.
    mask : str
        The `_mask.nii.gz` file of the preprocessed DWI used as input for DIPY.
    out_path : str
        Path to the files processed by DIPY, starting at the BIDS root directory.
    json_metadata : str, optional
        Path to JSON metadata file containing metadata information required for BEP16.
        If no file is provided, the resulting json sidecar metadata files will contain values indicated in the respective DIPI DTI metadata template and need to be checked manually.

    Examples
    --------
    Apply the conversion to data processed by DIPY's DTI CLI and previously preprocessed by
    QSIprep, both located in a respective derivatives directory. Here, no json metadata file
    is provided by the user and thus, the resulting json metadata sidecar files will
    contain values indicated in the respective DIPI DTI metadata template and need to be checked manually.

    >>> dipy_bep16_dti('bids_root/derivatives/QSIprep/sub-01/dwi/sub-01_desc-preproc_dwi.nii.gz',
                   'bids_root/derivatives/QSIprep/sub-01/dwi/sub-01_desc-preproc_dwi.bval',
                   'bids_root/derivatives/QSIprep/sub-01/dwi/sub-01_desc-preproc_dwi.bvec',
                   'bids_root/derivatives/dipy/sub-01/dwi/')

    Apply the conversion to data processed by DIPY's DTI CLI and previously preprocessed by
    QSIprep, both located in a respective derivatives directory. Here, a json metadata file
    is provided by the user and thus, the resulting json metadata sidecar files will be
    based on the respectively provided information. It's stored at the top of the respective
    derivative directory, ie "dipy".

    >>> dipy_bep16_dti('bids_root/derivatives/QSIprep/sub-01/dwi/sub-01_desc-preproc_dwi.nii.gz',
                   'bids_root/derivatives/QSIprep/sub-01/dwi/sub-01_desc-preproc_dwi.bval',
                   'bids_root/derivatives/QSIprep/sub-01/dwi/sub-01_desc-preproc_dwi.bvec',
                   'bids_root/derivatives/dipy/sub-01/dwi/'
                   'bids_root/derivatives/dipy/analysis_metadata.json')
    """

    # get the file naming pattern (ie subject, session, etc.) based on the input data
    file_name_pattern = dwi_nii_gz.split('/')[-1].split('_desc')[0]

    # change the working directory to the location of the files obtained via DIPY
    os.chdir(out_path)

    # get a list of all files and sort it
    file_list = os.listdir('.')
    file_list.sort

    # loop over all files to conduct the respectively required conversion
    for file in file_list:

        # check if json_metadata was provided by the user
        # if not, issue a warning and get the template with placeholders
        if json_metadata is None:
            warnings.warn('You did not provide a json file containing the metadata '
                          'for your analysis. Thus, the json files produced '
                          'during the conversion will contain based on the DIPY docs '
                          'and you should remember to check them out respectively!')
            json_metadata = importlib_resources.files(__name__).joinpath('data/metadata_templates/BEP16_metadata_template_DIPY_DTI.json')

        # load the json_metadata file, either provided by the user or the template one
        with open(json_metadata, 'r') as user_metadata:
            user_metadata = json.load(user_metadata)

        # the tensor file needs to be treated differently, so we need to check
        # when it appears and when it does, run the dedicated conversion
        if file == 'tensors.nii.gz':

            # renaming the tensor file following BEP16
            os.rename(file, '%s_param-tensor_model.nii.gz' % file_name_pattern)

            # initialize an empty dictionary for the tensor file's JSON sidecar file
            tensor_model_json = {}

            # add required keys and respectively needed information
            tensor_model_json["Name"] = user_metadata["Name"]
            tensor_model_json["BIDSVersion"] = "PLEASE ADD"
            tensor_model_json["GeneratedBy"] = user_metadata["GeneratedBy"]
            tensor_model_json["GeneratedBy"][0]["Version"] = dipy.__version__
            tensor_model_json["HowToAcknowledge"] = "PLEASE ADD"
            tensor_model_json["SourceDatasetsURLs"] = "PLEASE ADD"
            tensor_model_json["License"] = "PLEASE ADD"
            tensor_model_json["ModelDescription"] = user_metadata["ModelDescription"]
            tensor_model_json["ModelURL"] = user_metadata["ModelURL"]
            tensor_model_json["OrientationRepresentation"] = user_metadata["OrientationRepresentation"]
            tensor_model_json["ReferenceAxes"] = user_metadata["ReferenceAxes"]
            tensor_model_json["Parameters"] = user_metadata["Parameters"]

            # get and add the sources of the files, for now automatically based on DIPY input
            if 'derivatives' in dwi_nii_gz:
                source_pattern_start = 'bids:derivatives:'
                source_pattern_start += dwi_nii_gz.split('derivatives/')[1].split('/')[0]

                source_pattern_dwi = source_pattern_start + ':' + \
                    dwi_nii_gz.split('derivatives/')[1][dwi_nii_gz.split('derivatives/')[1].find('/') + 1:]

                source_pattern_bval = source_pattern_start + ':' + \
                    bval.split('derivatives/')[1][bval.split('derivatives/')[1].find('/') + 1:]

                source_pattern_bvec = source_pattern_start + ':' + \
                    bvec.split('derivatives/')[1][bvec.split('derivatives/')[1].find('/') + 1:]

                source_pattern_mask = source_pattern_start + ':' + \
                    mask.split('derivatives/')[1][mask.split('derivatives/')[1].find('/') + 1:]

                tensor_model_json["sources"] = [source_pattern_dwi, source_pattern_bval,
                                                source_pattern_bvec, source_pattern_mask]
            else:
                warnings.warn('The files do not seem to be stored under "derivatives" and thus'
                              'the sources can not be automatically derived. Please make sure '
                              'to add them manually.')
                tensor_model_json["sources"] = []

            # save the dictionary to the required JSON sidecar file for the tensor file
            with open(str(str(out_path) + '/%s_param-tensor_model.json' % file_name_pattern), 'w') as outfile:
                json.dump(tensor_model_json, outfile, indent=4)

        # if files other than the tensor image are processed, the same conversion routines can be applied
        else:

            # rename the file according to BEP16
            os.rename(file, '%s_param-%s_mdp.nii.gz' % (file_name_pattern, file.split('.')[0]))

            # initialize an empty dictionary for the param file's JSON sidecar file
            param_model_json = {}

            # add required keys and respectively needed information
            param_model_json["Name"] = user_metadata["Name"]
            param_model_json["BIDSVersion"] = "PLEASE ADD"
            param_model_json["GeneratedBy"] = user_metadata["GeneratedBy"]
            param_model_json["GeneratedBy"][0]["Version"] = dipy.__version__
            param_model_json["HowToAcknowledge"] = "PLEASE ADD"
            param_model_json["SourceDatasetsURLs"] = "PLEASE ADD"
            param_model_json["License"] = "PLEASE ADD"
            param_model_json["OrientationRepresentation"] = user_metadata["OrientationRepresentation"]
            param_model_json["ReferenceAxes"] = user_metadata["ReferenceAxes"]
            param_model_json["AntipodalSymmetry"] = user_metadata["AntipodalSymmetry"]

            if file == 'rgb.nii.gz':
                param_model_json["OrientationRepresentation"] = "dec"

            # get and add the sources of the files, for now automatically based on DIPY input
            if 'derivatives' in dwi_nii_gz:
                source_pattern_start = 'bids:derivatives:'
                source_pattern_start += dwi_nii_gz.split('derivatives/')[1].split('/')[0]

                source_pattern_dwi = source_pattern_start + ':' + \
                    dwi_nii_gz.split('derivatives/')[1][dwi_nii_gz.split('derivatives/')[1].find('/') + 1:]

                source_pattern_bval = source_pattern_start + ':' + \
                    bval.split('derivatives/')[1][bval.split('derivatives/')[1].find('/') + 1:]

                source_pattern_bvec = source_pattern_start + ':' + \
                    bvec.split('derivatives/')[1][bvec.split('derivatives/')[1].find('/') + 1:]

                source_pattern_mask = source_pattern_start + ':' + \
                    mask.split('derivatives/')[1][mask.split('derivatives/')[1].find('/') + 1:]

                param_model_json["sources"] = [source_pattern_dwi, source_pattern_bval,
                                               source_pattern_bvec, source_pattern_mask]
            else:
                warnings.warn('The files do not seem to be stored under "derivatives" and thus'
                              'the sources can not be automatically derived. Please make sure '
                              'to add them manually.')
                param_model_json["sources"] = []

            # save the dictionary to the required JSON sidecar file for the tensor file
            param_name = file.split('.')[0]
            with open(str(str(out_path) + '/%s_param-%s_mdp.json' % (file_name_pattern, param_name)), 'w') as outfile:
                json.dump(param_model_json, outfile, indent=4)


def mrtrix_bep16_dti(dwi_nii_gz, bval, bvec, mask, out_path, json_metadata=None):
    """
    Restructure MRTRIX DTI outcomes following BIDS BEP16 conventions.

    Parameters
    ----------
    dwi_nii_gz : str
        The `_dwi.nii(.gz)` file of the preprocessed DWI used as input for MRTRIX.
    bval : str
        The `_dwi.bval` file of the preprocessed DWI used as input for MRTRIX.
    bvec : str
        The `_dwi.bvec` file of the preprocessed DWI used as input for MRTRIX.
    mask : str
        The `_mask.nii.gz` file of the preprocessed DWI used as input for MRTRIX.
    out_path : str
        Path to the files processed by MRTRIX, starting at the BIDS root directory.
    json_metadata : str, optional
        Path to JSON metadata file containing metadata information required for BEP16.
        If no file is provided, the resulting json sidecar metadata files will contain values indicated in the respective MRTRIX DTI metadata template and need to be checked manually.

    Examples
    --------
    Apply the conversion to data processed by MRTRIX's dwi2tensor & tensor2metric CLI and previously preprocessed by
    QSIprep, both located in a respective derivatives directory. Here, no json metadata file
    is provided by the user and thus, the resulting json metadata sidecar files will
    contain values indicated in the respective MRTRIX DTI metadata template and need to be checked manually.

    >>> mrtrix_bep16_dti('bids_root/derivatives/QSIprep/sub-01/dwi/sub-01_desc-preproc_dwi.nii.gz',
                   'bids_root/derivatives/QSIprep/sub-01/dwi/sub-01_desc-preproc_dwi.bval',
                   'bids_root/derivatives/QSIprep/sub-01/dwi/sub-01_desc-preproc_dwi.bvec',
                   'bids_root/derivatives/dipy/sub-01/dwi/')

    Apply the conversion to data processed by MRTRIX's dwi2tensor & tensor2metric CLI and previously preprocessed by
    QSIprep, both located in a respective derivatives directory. Here, a json metadata file
    is provided by the user and thus, the resulting json metadata sidecar files will be
    based on the respectively provided information. It's stored at the top of the respective
    derivative directory, ie "mrtrix".

    >>> mrtrix_bep16_dti('bids_root/derivatives/QSIprep/sub-01/dwi/sub-01_desc-preproc_dwi.nii.gz',
                         'bids_root/derivatives/QSIprep/sub-01/dwi/sub-01_desc-preproc_dwi.bval',
                         'bids_root/derivatives/QSIprep/sub-01/dwi/sub-01_desc-preproc_dwi.bvec',
                         'bids_root/derivatives/dipy/sub-01/dwi/'
                         'bids_root/derivatives/dipy/analysis_metadata.json')
    """

    # get the file naming pattern (ie subject, session, etc.) based on the input data
    file_name_pattern = dwi_nii_gz.split('/')[-1].split('_desc')[0]
    print(file_name_pattern)

    # change the working directory to the location of the files obtained via DIPY
    os.chdir(out_path)

    # get a list of all files and sort it
    file_list = os.listdir('.')
    file_list.sort

    # loop over all files to conduct the respectively required conversion
    for file in file_list:

        # check if json_metadata was provided by the user
        # if not, issue a warning and get the template with placeholders
        if json_metadata is None:
            warnings.warn('You did not provide a json file containing the metadata '
                          'for your analysis. Thus, the json files produced '
                          'during the conversion will contain based on the DIPY docs '
                          'and you should remember to check them out respectively!')
            json_metadata = importlib_resources.files(__name__).joinpath('data/metadata_templates/BEP16_metadata_template_MRTRIX_DTI.json')

        # load the json_metadata file, either provided by the user or the template one
        with open(json_metadata, 'r') as user_metadata:
            user_metadata = json.load(user_metadata)

        # the tensor file needs to be treated differently, so we need to check
        # when it appears and when it does, run the dedicated conversion
        if 'tensor' in file:

            # initialize an empty dictionary for the tensor file's JSON sidecar file
            tensor_model_json = {}

            # add required keys and respectively needed information
            tensor_model_json["Name"] = user_metadata["Name"]
            tensor_model_json["BIDSVersion"] = "PLEASE ADD"
            tensor_model_json["GeneratedBy"] = user_metadata["GeneratedBy"]
            tensor_model_json["GeneratedBy"][0]["Version"] = mrtrix3.__version__
            tensor_model_json["HowToAcknowledge"] = "PLEASE ADD"
            tensor_model_json["SourceDatasetsURLs"] = "PLEASE ADD"
            tensor_model_json["License"] = "PLEASE ADD"
            tensor_model_json["ModelDescription"] = user_metadata["ModelDescription"]
            tensor_model_json["ModelURL"] = user_metadata["ModelURL"]
            tensor_model_json["OrientationRepresentation"] = user_metadata["OrientationRepresentation"]
            tensor_model_json["ReferenceAxes"] = user_metadata["ReferenceAxes"]
            tensor_model_json["Parameters"] = user_metadata["Parameters"]

            # get and add the sources of the files, for now automatically based on MRTRIX input
            if 'derivatives' in dwi_nii_gz:
                source_pattern_start = 'bids:derivatives:'
                source_pattern_start += dwi_nii_gz.split('derivatives/')[1].split('/')[0]

                source_pattern_dwi = source_pattern_start + ':' + \
                    dwi_nii_gz.split('derivatives/')[1][dwi_nii_gz.split('derivatives/')[1].find('/') + 1:]

                source_pattern_bval = source_pattern_start + ':' + \
                    bval.split('derivatives/')[1][bval.split('derivatives/')[1].find('/') + 1:]

                source_pattern_bvec = source_pattern_start + ':' + \
                    bvec.split('derivatives/')[1][bvec.split('derivatives/')[1].find('/') + 1:]

                source_pattern_mask = source_pattern_start + ':' + \
                    mask.split('derivatives/')[1][mask.split('derivatives/')[1].find('/') + 1:]

                tensor_model_json["sources"] = [source_pattern_dwi, source_pattern_bval,
                                                source_pattern_bvec, source_pattern_mask]
            else:
                warnings.warn('The files do not seem to be stored under "derivatives" and thus'
                              'the sources can not be automatically derived. Please make sure '
                              'to add them manually.')
                tensor_model_json["sources"] = []

            # save the dictionary to the required JSON sidecar file for the tensor file
            with open(str(str(out_path) + '/%s_param-tensor_model.json' % file_name_pattern), 'w') as outfile:
                json.dump(tensor_model_json, outfile, indent=4)

        # if files other than the tensor image are processed, the same conversion routines can be applied
        else:

            # initialize an empty dictionary for the param file's JSON sidecar file
            param_model_json = {}

            # add required keys and respectively needed information
            param_model_json["Name"] = user_metadata["Name"]
            param_model_json["BIDSVersion"] = "PLEASE ADD"
            param_model_json["GeneratedBy"] = user_metadata["GeneratedBy"]
            param_model_json["GeneratedBy"][0]["Version"] = mrtrix3.__version__
            param_model_json["HowToAcknowledge"] = "PLEASE ADD"
            param_model_json["SourceDatasetsURLs"] = "PLEASE ADD"
            param_model_json["License"] = "PLEASE ADD"
            param_model_json["OrientationRepresentation"] = user_metadata["OrientationRepresentation"]
            param_model_json["ReferenceAxes"] = user_metadata["ReferenceAxes"]
            param_model_json["AntipodalSymmetry"] = user_metadata["AntipodalSymmetry"]

            # get and add the sources of the files, for now automatically based on MRTRIX input
            if 'derivatives' in dwi_nii_gz:
                source_pattern_start = 'bids:derivatives:'
                source_pattern_start += dwi_nii_gz.split('derivatives/')[1].split('/')[0]

                source_pattern_dwi = source_pattern_start + ':' + \
                    dwi_nii_gz.split('derivatives/')[1][dwi_nii_gz.split('derivatives/')[1].find('/') + 1:]

                source_pattern_bval = source_pattern_start + ':' + \
                    bval.split('derivatives/')[1][bval.split('derivatives/')[1].find('/') + 1:]

                source_pattern_bvec = source_pattern_start + ':' + \
                    bvec.split('derivatives/')[1][bvec.split('derivatives/')[1].find('/') + 1:]

                source_pattern_mask = source_pattern_start + ':' + \
                    mask.split('derivatives/')[1][mask.split('derivatives/')[1].find('/') + 1:]

                param_model_json["sources"] = [source_pattern_dwi, source_pattern_bval,
                                               source_pattern_bvec, source_pattern_mask]
            else:
                warnings.warn('The files do not seem to be stored under "derivatives" and thus'
                              'the sources can not be automatically derived. Please make sure '
                              'to add them manually.')
                param_model_json["sources"] = []

            # save the dictionary to the required JSON sidecar file for the tensor file
            param_name = file.split('param-')[1].split('_')[0]
            with open(str(str(out_path) + '/%s_param-%s_mdp.json' % (file_name_pattern, param_name)), 'w') as outfile:
                json.dump(param_model_json, outfile, indent=4)


def fsl_bep16_dti(dwi_nii_gz, bval, bvec, mask, out_path, json_metadata=None):
    """
    Restructure FSL DTI outcomes following BIDS BEP16 conventions.

    Parameters
    ----------
    dwi_nii_gz : str
        The `_dwi.nii(.gz)` file of the preprocessed DWI used as input for MRTRIX.
    bval : str
        The `_dwi.bval` file of the preprocessed DWI used as input for MRTRIX.
    bvec : str
        The `_dwi.bvec` file of the preprocessed DWI used as input for MRTRIX.
    mask : str
        The `_mask.nii.gz` file of the preprocessed DWI used as input for MRTRIX.
    out_path : str
        Path to the files processed by FSL, starting at the BIDS root directory.
    json_metadata : str, optional
        Path to JSON metadata file containing metadata information required for BEP16.
        If no file is provided, the resulting json sidecar metadata files will contain values indicated in the respective FSL DTI metadata template and need to be checked manually.

    Examples
    --------
    Apply the conversion to data processed by FSL's dtifit CLI and previously preprocessed by
    QSIprep, both located in a respective derivatives directory. Here, no json metadata file
    is provided by the user and thus, the resulting json metadata sidecar files will
    contain values indicated in the respective FSL DTI metadata template and need to be checked manually.

    >>> fsl_bep16_dti('bids_root/derivatives/QSIprep/sub-01/dwi/sub-01_desc-preproc_dwi.nii.gz',
                      'bids_root/derivatives/QSIprep/sub-01/dwi/sub-01_desc-preproc_dwi.bval',
                      'bids_root/derivatives/QSIprep/sub-01/dwi/sub-01_desc-preproc_dwi.bvec',
                      'bids_root/derivatives/dipy/sub-01/dwi/')

    Apply the conversion to data processed by FSL's dtifit CLI and previously preprocessed by
    QSIprep, both located in a respective derivatives directory. Here, a json metadata file
    is provided by the user and thus, the resulting json metadata sidecar files will be
    based on the respectively provided information. It's stored at the top of the respective
    derivative directory, ie "fsl".

    >>> fsl_bep16_dti('bids_root/derivatives/QSIprep/sub-01/dwi/sub-01_desc-preproc_dwi.nii.gz',
                      'bids_root/derivatives/QSIprep/sub-01/dwi/sub-01_desc-preproc_dwi.bval',
                      'bids_root/derivatives/QSIprep/sub-01/dwi/sub-01_desc-preproc_dwi.bvec',
                      'bids_root/derivatives/dipy/sub-01/dwi/'
                      'bids_root/derivatives/dipy/analysis_metadata.json')
    """

    # get the file naming pattern (ie subject, session, etc.) based on the input data
    file_name_pattern = dwi_nii_gz.split('/')[-1].split('_desc')[0]
    print(file_name_pattern)

    # change the working directory to the location of the files obtained via DIPY
    os.chdir(out_path)

    # get a list of all files and sort it
    file_list = os.listdir('.')
    file_list.sort

    eigenvector_list = []

    # check if json_metadata was provided by the user
    # if not, issue a warning and get the template with placeholders
    if json_metadata is None:
        warnings.warn('You did not provide a json file containing the metadata '
                      'for your analysis. Thus, the json files produced '
                      'during the conversion will contain based on the DIPY docs '
                      'and you should remember to check them out respectively!')
        json_metadata = importlib_resources.files(__name__).joinpath('data/metadata_templates/BEP16_metadata_template_FSL_DTI.json')

    # loop over all files to conduct the respectively required conversion
    for file in file_list:

        # load the json_metadata file, either provided by the user or the template one
        with open(json_metadata, 'r') as user_metadata:
            user_metadata = json.load(user_metadata)

        # the tensor file needs to be treated differently, so we need to check
        # when it appears and when it does, run the dedicated conversion
        if 'tensor' in file:

            # rename the file according to BEP16
            os.rename(file, '%s_param-tensor_model.nii.gz' % file_name_pattern)

            # initialize an empty dictionary for the tensor file's JSON sidecar file
            tensor_model_json = {}

            # add required keys and respectively needed information
            tensor_model_json["Name"] = user_metadata["Name"]
            tensor_model_json["BIDSVersion"] = "PLEASE ADD"
            tensor_model_json["GeneratedBy"] = user_metadata["GeneratedBy"]
            tensor_model_json["HowToAcknowledge"] = "PLEASE ADD"
            tensor_model_json["SourceDatasetsURLs"] = "PLEASE ADD"
            tensor_model_json["License"] = "PLEASE ADD"
            tensor_model_json["ModelDescription"] = user_metadata["ModelDescription"]
            tensor_model_json["ModelURL"] = user_metadata["ModelURL"]
            tensor_model_json["OrientationRepresentation"] = user_metadata["OrientationRepresentation"]
            tensor_model_json["ReferenceAxes"] = user_metadata["ReferenceAxes"]
            tensor_model_json["Parameters"] = user_metadata["Parameters"]

            # get and add the sources of the files, for now automatically based on FSL input
            if 'derivatives' in dwi_nii_gz:
                source_pattern_start = 'bids:derivatives:'
                source_pattern_start += dwi_nii_gz.split('derivatives/')[1].split('/')[0]

                source_pattern_dwi = source_pattern_start + ':' + \
                    dwi_nii_gz.split('derivatives/')[1][dwi_nii_gz.split('derivatives/')[1].find('/') + 1:]

                source_pattern_bval = source_pattern_start + ':' + \
                    bval.split('derivatives/')[1][bval.split('derivatives/')[1].find('/') + 1:]

                source_pattern_bvec = source_pattern_start + ':' + \
                    bvec.split('derivatives/')[1][bvec.split('derivatives/')[1].find('/') + 1:]

                source_pattern_mask = source_pattern_start + ':' + \
                    mask.split('derivatives/')[1][mask.split('derivatives/')[1].find('/') + 1:]

                tensor_model_json["sources"] = [source_pattern_dwi, source_pattern_bval,
                                                source_pattern_bvec, source_pattern_mask]
            else:
                warnings.warn('The files do not seem to be stored under "derivatives" and thus'
                              'the sources can not be automatically derived. Please make sure '
                              'to add them manually.')
                tensor_model_json["sources"] = []

            # save the dictionary to the required JSON sidecar file for the tensor file
            with open(str(str(out_path) + '/%s_param-tensor_model.json' % file_name_pattern), 'w') as outfile:
                json.dump(tensor_model_json, outfile, indent=4)

        # if MD, MO or S0 files are processed, the same conversion routines can be applied
        elif 'MD' in file or 'MO' in file or 'S0' in file or 'FA' in file:

            # get the parameter name based on the file type
            if 'S0' in file:
                param_name = 'bzero'
            elif 'FA' in file:
                param_name = 'fa'
            elif 'MD' in file:
                param_name = 'md'
            elif 'MO' in file:
                param_name = 'mode'

            # rename the file according to BEP16
            os.rename(file, '%s_param-%s_mdp.nii.gz' % (file_name_pattern, param_name))

            # initialize an empty dictionary for the param file's JSON sidecar file
            param_model_json = {}

            # add required keys and respectively needed information
            param_model_json["Name"] = user_metadata["Name"]
            param_model_json["BIDSVersion"] = "PLEASE ADD"
            param_model_json["GeneratedBy"] = user_metadata["GeneratedBy"]
            param_model_json["HowToAcknowledge"] = "PLEASE ADD"
            param_model_json["SourceDatasetsURLs"] = "PLEASE ADD"
            param_model_json["License"] = "PLEASE ADD"
            param_model_json["OrientationRepresentation"] = user_metadata["OrientationRepresentation"]
            param_model_json["ReferenceAxes"] = user_metadata["ReferenceAxes"]
            param_model_json["AntipodalSymmetry"] = user_metadata["AntipodalSymmetry"]

            # get and add the sources of the files, for now automatically based on FSL input
            if 'derivatives' in dwi_nii_gz:
                source_pattern_start = 'bids:derivatives:'
                source_pattern_start += dwi_nii_gz.split('derivatives/')[1].split('/')[0]

                source_pattern_dwi = source_pattern_start + ':' + \
                    dwi_nii_gz.split('derivatives/')[1][dwi_nii_gz.split('derivatives/')[1].find('/') + 1:]

                source_pattern_bval = source_pattern_start + ':' + \
                    bval.split('derivatives/')[1][bval.split('derivatives/')[1].find('/') + 1:]

                source_pattern_bvec = source_pattern_start + ':' + \
                    bvec.split('derivatives/')[1][bvec.split('derivatives/')[1].find('/') + 1:]

                source_pattern_mask = source_pattern_start + ':' + \
                    mask.split('derivatives/')[1][mask.split('derivatives/')[1].find('/') + 1:]

                param_model_json["sources"] = [source_pattern_dwi, source_pattern_bval,
                                               source_pattern_bvec, source_pattern_mask]
            else:
                warnings.warn('The files do not seem to be stored under "derivatives" and thus'
                              'the sources can not be automatically derived. Please make sure '
                              'to add them manually.')
                param_model_json["sources"] = []

            # save the dictionary to the required JSON sidecar file for the tensor file
            with open(str(str(out_path) + '/%s_param-%s_mdp.json' % (file_name_pattern, param_name)), 'w') as outfile:
                json.dump(param_model_json, outfile, indent=4)
        
        # if file is eigenvalue, remove it
        elif 'L1' in file or 'L2' in file or 'L3' in file:
            os.remove(file)

        # if file is eigenvector, append it to eigenvector list
        elif 'V1' in file or 'V2' in file or 'V3' in file:

            eigenvector_list.append(file)
          
    eigenvector_image = nb.concat_images(eigenvector_list)

    [os.remove(evec_image) for evec_image in eigenvector_list]

    nb.save(eigenvector_image, '%s_param-evec_mdp.nii.gz' % file_name_pattern)

    # initialize an empty dictionary for the param file's JSON sidecar file
    param_model_json = {}

    # add required keys and respectively needed information
    param_model_json["Name"] = user_metadata["Name"]
    param_model_json["BIDSVersion"] = "PLEASE ADD"
    param_model_json["GeneratedBy"] = user_metadata["GeneratedBy"]
    param_model_json["HowToAcknowledge"] = "PLEASE ADD"
    param_model_json["SourceDatasetsURLs"] = "PLEASE ADD"
    param_model_json["License"] = "PLEASE ADD"
    param_model_json["OrientationRepresentation"] = user_metadata["OrientationRepresentation"]
    param_model_json["ReferenceAxes"] = user_metadata["ReferenceAxes"]
    param_model_json["AntipodalSymmetry"] = user_metadata["AntipodalSymmetry"]

    # get and add the sources of the files, for now automatically based on FSL input
    if 'derivatives' in dwi_nii_gz:
        source_pattern_start = 'bids:derivatives:'
        source_pattern_start += dwi_nii_gz.split('derivatives/')[1].split('/')[0]

        source_pattern_dwi = source_pattern_start + ':' + \
            dwi_nii_gz.split('derivatives/')[1][dwi_nii_gz.split('derivatives/')[1].find('/') + 1:]

        source_pattern_bval = source_pattern_start + ':' + \
            bval.split('derivatives/')[1][bval.split('derivatives/')[1].find('/') + 1:]

        source_pattern_bvec = source_pattern_start + ':' + \
            bvec.split('derivatives/')[1][bvec.split('derivatives/')[1].find('/') + 1:]

        source_pattern_mask = source_pattern_start + ':' + \
            mask.split('derivatives/')[1][mask.split('derivatives/')[1].find('/') + 1:]

        param_model_json["sources"] = [source_pattern_dwi, source_pattern_bval,
                                       source_pattern_bvec, source_pattern_mask]
    else:
        warnings.warn('The files do not seem to be stored under "derivatives" and thus'
                      'the sources can not be automatically derived. Please make sure '
                      'to add them manually.')
        param_model_json["sources"] = []

    # save the dictionary to the required JSON sidecar file for the tensor file
    with open(str(str(out_path) + '/%s_param-evec_mdp.json' % file_name_pattern), 'w') as outfile:
        json.dump(param_model_json, outfile, indent=4)

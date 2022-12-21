import os
import requests
from tqdm.auto import tqdm
from pathlib import Path, PosixPath
import seedir as sd
import shutil
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import ptitprince as pt
from json import load, dump


def get_HBN_qc(dataset_path=None, return_df=False):
    """
    Download the QSIprep's participants.tsv file obtained for the HBN
    dataset from S3. This file contains important QC measure that are
    used to define example participants for BIDS BEP-16.

    Parameters
    ----------
    dataset_path : string
        Path where the file will be saved. If None, the file will be saved
        in the current working directory. Default = None.
    return_df : bool
        Indicate if the function should return the path to the downloaded file
        or a Pandas DataFrame containing the file's content. Default = False.

    Returns
    -------
    qsi_qc_file_local : PosixPath or Pandas DataFrame
        Either a PosixPath indicating the path to the downloaded file or a
        Pandas DataFrame. Dependent on the return_df argument.

    Examples
    --------
    Download the file without specifying a path and not loading it into a Pandas DataFrame.

    >>> get_HBN_qc(dataset_path=None, return_df=False)

    Download the file, specifying a path and loading it into a Pandas DataFrame.

    >>> get_HBN_qc(dataset_path='/home/user/Desktop', return_df=True)
    """

    # check if path where to save the file was provided, if not
    # save it to the current directory
    if dataset_path is None:
        path = Path(os.curdir + '/bids_bep16_datasets/HBN')
    else:
        path = Path(dataset_path + '/bids_bep16_datasets/HBN')

    # in either case: check if path exists and if not, create it
    if not path.exists():
        os.makedirs(path)

    # define the full path by combining path and dedicated file name
    download_path = Path(os.path.join(path, ('source-HBN_desc-qsiprep_participants.tsv')))

    # if the file does not already exist, download it from s3
    if not download_path.exists():

        # provide a little update message
        print('Data will be downloaded to %s' % download_path)

        # specify url to file on S3 bucket
        qsi_qc_file_s3 = "https://fcp-indi.s3.amazonaws.com/data/Projects/HBN/BIDS_curated/derivatives/qsiprep/participants.tsv"

        # download and save the file, updating the user on the download progress
        with requests.get(qsi_qc_file_s3, stream=True) as participants_file:

            # get total size of file for download updates
            participants_file_size = int(participants_file.headers.get('Content-Length'))

            # implement progress bar via tqdm
            with tqdm.wrapattr(participants_file.raw, "read", total=participants_file_size, desc="")as raw:

                # save the output to the file specified before
                with open(f"{download_path}", 'wb')as output:
                    shutil.copyfileobj(raw, output)
        
        qsi_qc_file_local = download_path

    # if the file already exists, set the respective path
    else:

        # provide a little update message
        print('Data already existing at %s' % download_path)

        qsi_qc_file_local = download_path

    # if a Pandas DataFrame should be returned, read the downloaded/existing file
    if return_df:
        qsi_qc_file_local = pd.read_table(qsi_qc_file_local)

    # return either the path to the file or the corresponding Pandas DataFrame
    return qsi_qc_file_local


def eval_HBN_qc(HBN_qc_file_df, n_high_participants=5, visualize=True, return_sorted_df=False):
    """
    Evaluate QSIprep's participants.tsv file obtained for the HBN
    dataset regarding QC.

    Parameters
    ----------
    HBN_qc_file_df : string or Pandas DataFrame
        Either a string indicating the path of the file or
        a corresponding Pandas DataFrame. will be saved.
    n_high_participants : int
        Integer indicating how many of the participants with
        the best QC sure should be displayed.
    visualize: bool
        Indicate if the distribution of QC scores should be
        displayed via a raincloud plot.
    return_sorted_df: bool
        Indicate if the DataFrame should be sorted by QC scores
        in a descending manner and returned.

    Returns
    -------
    HBN_qc_file_df_n_high : Pandas Series
        A Pandas Series indicating the participants with the highest
        QC scores with the amount being defined by n_high_participants.
    HBN_qc_file_df: Pandas DataFrame
        The DataFrame, sorted by QC scores. Returned only if
        return_sorted_df is set to True.
    fig : :class:`~matplotlib.figure.Figure`
        A :class:`~matplotlib.figure.Figure` containing a
        raincloud plot of the QC scores.

    Examples
    --------
    Get the participants with the 10 highest QC scores and do not show the plot nor return the sorted DataFrame.

    >>> eval_HBN_qc(HBN_qc_file_df, n_high_participants=10, visualize=False, return_sorted_df=False)

    Get the participants with the 3 highest QC scores and do show the plot and return the sorted DataFrame.

    >>> eval_HBN_qc(HBN_qc_file_df, n_high_participants=3, visualize=True, return_sorted_df=True)

    """

    # if HBN_qc_file_df is a str or PosixPath, read it into a DataFrame via Pandas
    if isinstance(HBN_qc_file_df, str) or isinstance(HBN_qc_file_df, PosixPath):
        HBN_qc_file_df = pd.read_table(HBN_qc_file_df)

    # sort the DataFrame based on QC scores
    HBN_qc_file_df = HBN_qc_file_df.sort_values(by='dl_qc_score', ascending=False)

    # get the participants with the n highest QC scores & print the information
    HBN_qc_file_df_n_high = HBN_qc_file_df['subject_id'].head(n=n_high_participants)

    print("The %s participants with the highest QC score are: \n%s" % (str(n_high_participants),
                                                                       HBN_qc_file_df_n_high))

    # if the data should be visualized, create a raincloud plot of the QC scores
    if visualize:

        # initialize the figure
        f, ax = plt.subplots(figsize=(17, 5))

        # create a raincloud plot & set plot details
        ax = pt.RainCloud(x=HBN_qc_file_df['dl_qc_score'], data=HBN_qc_file_df['subject_id'],
                          scale="area")
        ax.set_xlim(HBN_qc_file_df['dl_qc_score'].min() - 0.1, HBN_qc_file_df['dl_qc_score'].max() + 0.1)
        ax.set_ylabel("HBN")
        ax.set_xlabel("QSIPREP - DL QC Score")
        sns.despine(offset=5)

    if return_sorted_df:
        return HBN_qc_file_df


def download_HBN(dataset_path=None):
    """
    Download the QSIprep outcomes obtained for the HBN dataset subset
    provided on OSF. Currently this entails sub-NDAREK918EC2.

    Parameters
    ----------
    dataset_path : string
        Path where the file will be saved. If None, the file will be saved
        in the current working directory. Default = None.

    Returns
    -------
    path : PosixPath
        A PosixPath indicating the path to the downloaded dataset.

    Examples
    --------
    Download the HBN dataset to the current directory.

    >>> download_HBN(dataset_path=None)

    Download the dataset to a specific path, e.g. the user's Desktop.

    >>> download_HBN(dataset_path='/home/user/Desktop')
    """

    # check if path where to save the file was provided, if not
    # save it to the current directory
    if dataset_path is None:
        path = Path(os.curdir + '/bids_bep16_datasets/HBN/derivatives/QSIprep/sub-NDAREK918EC2/ses-HBNsiteSI/dwi')
    else:
        path = Path(dataset_path + '/bids_bep16_datasets/HBN/derivatives/QSIprep/sub-NDAREK918EC2/ses-HBNsiteSI/dwi')

    # in either case: check if path exists and if not, create it
    if not path.exists():
        os.makedirs(path)

    # define list of HBN files that should be downloaded
    HBN_files = ['sub-NDAREK918EC2_ses-HBNsiteSI_acq-64dir_space-T1w_desc-preproc_dwi.bval',
                 'sub-NDAREK918EC2_ses-HBNsiteSI_acq-64dir_space-T1w_desc-preproc_dwi.bvec',
                 'sub-NDAREK918EC2_ses-HBNsiteSI_acq-64dir_space-T1w_desc-preproc_dwi.nii.gz',
                 'sub-NDAREK918EC2_ses-HBNsiteSI_acq-64dir_space-T1w_desc-brain_mask.nii.gz',
                 'sub-NDAREK918EC2_ses-HBNsiteSI_acq-64dir_space-T1w_desc-preproc_dwi.json',
                 'QSIprep/dataset_description.json',
                 'HBN/dataset_description.json'
                 ]

    # define list of HBN files URLs
    HBN_file_urls = ['https://osf.io/hjvub/download', 'https://osf.io/vq46r/download',
                     'https://osf.io/9dfx3/download', 'https://osf.io/y5xr6/download',
                     'https://osf.io/2h7db/download', 'https://osf.io/4mx5v/download',
                     'https://osf.io/n73ke/download']

    # loop over files and download them if not already existing
    for file, url in zip(HBN_files, HBN_file_urls):

        # define the file-specific download path

        # if QSIprep dataset descriptor, change path
        if file == 'QSIprep/dataset_description.json':
            download_path = Path(os.path.join(path.parents[2], file.split('/')[1]))
        # if HBN dataset descriptor, change path
        elif file == 'HBN/dataset_description.json':
            download_path = Path(os.path.join(path.parents[4], file.split('/')[1]))
        else:
            download_path = Path(os.path.join(path, file))

        # if the file does not already exist, download it from OSF
        if not download_path.exists():

            # provide a little update
            print('Downloading %s' % file)

            # download and save the file, updating the user on the download progress
            with requests.get(url, stream=True) as HBN_file:

                # get total size of file for download updates
                participants_file_size = int(HBN_file.headers.get('Content-Length'))

                # implement progress bar via tqdm
                with tqdm.wrapattr(HBN_file.raw, "read", total=participants_file_size, desc="") as raw:

                    # save the output to the file specified before
                    with open(f"{download_path}", 'wb') as output:
                        shutil.copyfileobj(raw, output)

            # HBN QSIprep misses json files, thus they need to be created in a two-step approach
            # 1. get the raw data json file and rename it to be BIDS conform
            # 2. add provenance information
            if file == 'sub-NDAREK918EC2_ses-HBNsiteSI_acq-64dir_space-T1w_desc-preproc_dwi.json':

                # define provenance information, right now hard coded, will be adapted later after there are
                # more example datasets
                prov_info = {
                    "Sources": ["bids:raw:sub-NDAREK918EC2/ses-HBNsiteSI/dwi/sub-NDAREK918EC2_ses-HBNsiteSI_acq-64dir_dwi.nii.gz",
                                "bids:raw:sub-NDAREK918EC2/ses-HBNsiteSI/dwi/sub-NDAREK918EC2_ses-HBNsiteSI_acq-64dir_dwi.bval",
                                "bids:raw:sub-NDAREK918EC2/ses-HBNsiteSI/dwi/sub-NDAREK918EC2_ses-HBNsiteSI_acq-64dir_dwi.bvec",
                                "bids:raw:sub-NDAREK918EC2/ses-HBNsiteSI/anat/sub-NDAREK918EC2_ses-HBNsiteSI_T1w.nii.gz",
                                "bids:raw:sub-NDAREK918EC2/ses-HBNsiteSI/fmap/sub-NDAREK918EC2_ses-HBNsiteSI_magnitude1.nii.gz",
                                "bids:raw:sub-NDAREK918EC2/ses-HBNsiteSI/fmap/sub-NDAREK918EC2_ses-HBNsiteSI_magnitude2.nii.gz",
                                "bids:raw:sub-NDAREK918EC2/ses-HBNsiteSI/fmap/sub-NDAREK918EC2_ses-HBNsiteSI_phasediff.nii.gz"
                                ],
                    "SpatialReference": "bids:raw:sub-NDAREK918EC2/ses-HBNsiteSI/anat/sub-NDAREK918EC2_ses-HBNsiteSI_T1w.nii.gz"
                }

                # open & load the downloaded raw data json file
                f = open(str(download_path), 'r', encoding='utf-8')

                meta_json = load(f)

                # add the provenance information
                meta_json.update(prov_info)

                # save the udpated json file
                with open(str(download_path), 'w') as outfile:
                    dump(meta_json, outfile, indent=4, sort_keys=True)

        else:

            # provide a little update message that the file already exists at the defined path
            print('%s already existing at %s' % (file, path))

    # provide a little update message showing the existing files
    print('The following HBN files are available:')
    sd.seedir(path.parents[4])

    return path

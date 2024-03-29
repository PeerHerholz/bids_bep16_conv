from pathlib import Path
import os
from ..datasets import get_HBN_qc, eval_HBN_qc, download_HBN
import pandas as pd


def test_get_HBN_qc():

    # test if file size matches
    HBN_qc_file = get_HBN_qc()
    actual_size = Path(HBN_qc_file).stat().st_size
    expected_size = 210607
    assert actual_size == expected_size

    # test if DataFrame is returned
    HBN_qc_file = get_HBN_qc(return_df=True)
    actual_type = type(HBN_qc_file)
    expected_type = pd.core.frame.DataFrame
    assert actual_type == expected_type

    # test if DataFrame columns match
    HBN_qc_file_df = HBN_qc_file
    actual_columns = HBN_qc_file_df.columns.to_list()
    expected_columns = ['subject_id', 'scan_site_id',
                        'sex', 'age', 'ehq_total',
                        'commercial_use', 'full_pheno',
                        'expert_qc_score', 'xgb_qc_score',
                        'xgb_qsiprep_qc_score', 'dl_qc_score',
                        'site_variant']
    assert actual_columns == expected_columns


def test_evaluate_HBN_qc():

    # test if type of returned information matches
    HBN_qc_file = pd.read_table(get_HBN_qc())
    HBN_qc_file_eval = eval_HBN_qc(HBN_qc_file, return_sorted_df=True)
    actual_type = type(HBN_qc_file_eval['dl_qc_score'].head(n=5))
    expected_type = pd.core.series.Series
    assert actual_type == expected_type

    # test if n high participants match
    actual_qc_scores = HBN_qc_file_eval['dl_qc_score'].head(n=5).to_list()
    expected_qc_scores = [1.0, 1.0, 1.0, 0.999, 0.999]
    assert actual_qc_scores == expected_qc_scores


def test_download_HBN():

    # test if all files are downloaded

    HBN_qsiprep_dwi_files = download_HBN()
    dataset_file_dir = os.listdir(HBN_qsiprep_dwi_files.parents[2])
    dataset_file = [f for f in dataset_file_dir if os.path.isfile(str(HBN_qsiprep_dwi_files.parents[2]) + '/' + f)]
    dataset_file_HBN = [f for f in dataset_file_dir if os.path.isfile(str(HBN_qsiprep_dwi_files.parents[4]) + '/' + f)]
    actual_files = sorted(os.listdir(HBN_qsiprep_dwi_files)) + dataset_file + dataset_file_HBN
    expected_files = ['sub-NDARYM277DEA_ses-HBNsiteCBIC_acq-64dir_space-T1w_desc-brain_mask.nii.gz',
                      'sub-NDARYM277DEA_ses-HBNsiteCBIC_acq-64dir_space-T1w_desc-preproc_dwi.bval',
                      'sub-NDARYM277DEA_ses-HBNsiteCBIC_acq-64dir_space-T1w_desc-preproc_dwi.bvec',
                      'sub-NDARYM277DEA_ses-HBNsiteCBIC_acq-64dir_space-T1w_desc-preproc_dwi.json',
                      'sub-NDARYM277DEA_ses-HBNsiteCBIC_acq-64dir_space-T1w_desc-preproc_dwi.nii.gz',
                      'dataset_description.json',
                      'dataset_description.json']
    assert actual_files == expected_files



from pathlib import Path
from ..datasets import get_HBN_qc, eval_HBN_qc
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
    

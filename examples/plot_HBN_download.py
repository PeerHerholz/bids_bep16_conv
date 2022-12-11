# -*- coding: utf-8 -*-
"""
Fetching the HBN example dataset
================================
This example demonstrates how to use :mod:`bids_bep16_conv.datasets` to fetch
the HBN example dataset.
"""

###############################################################################
# Much of the functionality of the ``bids_bep16_conv`` toolbox relies on downloading
# candidate example datasets. Each dataset has its own functions to check and evaluate QC
# files to find suitable participants, as well as dedicated download functions that will obtain
# the data from the BIDS connectivity OSF project. The respective files differ between example datasets
# and respectively utilized pipeline/workflow but are obtained in a way that they confirm
# to BIDS common derivatives, specifically as input for tools that generate BEP16-related output.
#
# Here we show how the HBN example dataset was generated and can be assessed, via describing the respective
# workflow and utilized ``functions``.
#
# The ``HBN dataset`` and its derivatives are provided openly via the `FCP-INDI AWS bucket <https://fcp-indi.s3.amazonaws.com/index.html#data/Projects/HBN/>`_, entailing various
# pipeline/workflow outputs. Here, we are going to focus on the preprocessing conducted via ``QSIprep``.
# 
# At first, we need to find a suitable ``participant``, in terms of overall data quality, Luckily, ``QSIprep``
# provides a respective file that includes a ``quality control score`` for each ``participant``.
# Using the :func:`datasets.get_HBN_qc` function we can obtain and check this file: 

from bids_bep16_conv import datasets

HBN_qc_file = datasets.get_HBN_qc(return_df=True)
print(HBN_qc_file)

###############################################################################
# What we get is a :class:`~pandas.DataFrame` entailing the content of ``QSIprep``'s ``participant.tsv`` file.
# In contains various ``demographic variables`` but also the ``Quality Control scores`` we are interested in.
# In order to make the respective evaluation more straightforward, we can use the :func:`datasets.get_HBN_qc` function,
# which will sort the :class:`~pandas.DataFrame` based on the ``dl_qc_score`` variable. We can furthermore indicate how 
# many ``participants`` with the highest score, as well as if the sorted :class:`~pandas.DataFrame`
# and a ``raincloud plot`` of the ``dl_qc_score`` variable across the ``dataset`` should be returned.
#
# Here, we going to get the ``participants`` that have the ``3`` highest scores, the sorted :class:`~pandas.DataFrame` and the ``raincloud plot``.

HBN_qc_participants_df_sorted = datasets.eval_HBN_qc(HBN_qc_file,
                                                     n_high_participants=3,
                                                     visualize=True, return_sorted_df=True)

###############################################################################
# As you can see in the ``raincloud plot``, the score has a rather interesting distribution but the
# above obtained :class:`~pandas.Series` indicates that ``participant`` ``sub-NDAREK918EC2`` has the
# highest ``dl_qc_score``. Thus, this `participant's QSIprep outputs <https://fcp-indi.s3.amazonaws.com/index.html#data/Projects/HBN/BIDS_curated/derivatives/qsiprep/sub-NDAREK918EC2/>`_ 
# were downloaded from the `FCP-INDI AWS bucket <https://fcp-indi.s3.amazonaws.com/index.html#data/Projects/HBN/>`_ and subsequently 
# uploaded to the `dataset component <https://osf.io/bz2vj/>`_ of the `BIDS connectivity project <https://pestillilab.github.io/bids-connectivity/>`_ `OSF project <https://osf.io/u4g5p/#!>`_
# for access and management.
# 
# That being said, we can use :func:`datasets.download_HBN` ``function`` to download the respective ``data``, for example
# to our ``Desktop``. 

HBN_dataset_path = datasets.download_HBN()

###############################################################################
# Importantly, this ``function`` does not only obtain the ``participant``'s ``QSIprep`` output, but
# also obtains the ``dataset_description.json`` and generates the ``data json sidecar`` ``file`` required by `BIDS common derivatives <https://bids-specification.readthedocs.io/en/stable/05-derivatives/02-common-data-types.html>`_.
# The latter is achieved by downloading the `respective raw data json sidecar file <https://fcp-indi.s3.amazonaws.com/index.html#data/Projects/HBN/BIDS_curated/sub-NDAREK918EC2/ses-HBNsiteSI/dwi/>`_ and appending the needed ``inheritance-related`` & ``spatial reference-related`` information.
#
# With that, we have a feasible ``HBN sub-dataset``, confirming to `BIDS common derivatives <https://bids-specification.readthedocs.io/en/stable/05-derivatives/02-common-data-types.html>`_, as well as
# `inputs required by BEP16 <https://github.com/bids-standard/bids-bep016/pull/24/files>`_ and respective further processing.


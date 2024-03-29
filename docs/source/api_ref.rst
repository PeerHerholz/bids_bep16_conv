.. _api_ref:

.. currentmodule:: bids_bep16_conv

Reference API
=============

.. contents:: **List of modules**
   :local:

.. _ref_datasets:

:mod:`bids_bep16_conv.datasets` - Dataset tools
-----------------------------------------------
.. automodule:: bids_bep16_conv.datasets
   :no-members:
   :no-inherited-members:

.. currentmodule:: bids_bep16_conv.datasets

.. autosummary::
   :template: function.rst
   :toctree: generated/

   bids_bep16_conv.datasets.get_HBN_qc
   bids_bep16_conv.datasets.eval_HBN_qc
   bids_bep16_conv.datasets.download_HBN

.. _ref_processing:

:mod:`bids_bep16_conv.processing` - Pipeline tools
---------------------------------------------------------------
.. automodule:: bids_bep16_conv.processing
   :no-members:
   :no-inherited-members:

.. currentmodule:: bids_bep16_conv.processing

.. autosummary::
   :template: function.rst
   :toctree: generated/

   bids_bep16_conv.processing.dipy_dti
   bids_bep16_conv.processing.dipy_csd
   bids_bep16_conv.processing.mrtrix_dti
   bids_bep16_conv.processing.fsl_dti

:mod:`bids_bep16_conv.converters` - Conversion tools
---------------------------------------------------------------
.. automodule:: bids_bep16_conv.converters
   :no-members:
   :no-inherited-members:

.. currentmodule:: bids_bep16_conv.converters

.. autosummary::
   :template: function.rst
   :toctree: generated/

   bids_bep16_conv.converters.dipy_bep16_dti
   bids_bep16_conv.converters.mrtrix_bep16_dti
   bids_bep16_conv.converters.fsl_bep16_dti

.. _ref_utils:

:mod:`bids_bep16_conv.utils` - Utility functions
------------------------------------------------
.. automodule:: bids_bep16_conv.utils
   :no-members:
   :no-inherited-members:

.. currentmodule:: bids_bep16_conv.utils

.. autosummary::
   :template: function.rst
   :toctree: generated/

   bids_bep16_conv.utils.validate_input_dir
   bids_bep16_conv.utils.create_dataset_description
   bids_bep16_conv.utils.copy_BEP16_metadata_json_template

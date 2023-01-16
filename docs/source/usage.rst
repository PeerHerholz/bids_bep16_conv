.. _usage:

==========
Usage
==========



Execution and the BIDS format
=============================

The general input of ``bids_bep16_conv`` is a path to the ``derivative`` ``DWI dataset`` that should
be further processed and its outputs subsequently structured according to BEP16. 
The input (``derivative``) ``dataset`` is required to be in valid :abbr:`BIDS (Brain Imaging Data
Structure)` format.
We highly recommend that you validate your dataset before you run ``bids_bep16_conv``
with the free, online `BIDS Validator <http://bids-standard.github.io/bids-validator/>`_.
However, the `BIDS Validator` is also run at the beginning of ``bids_bep16_conv`` and will
you make you aware of possible problems and/or inconsistencies.
The exact command to run ``bids_bep16_conv`` depends on the Installation method.
The common parts of the command follow the `BIDS-Apps
<https://github.com/BIDS-Apps>`_ definition.
Here's a very conceptual example: ::

    bids_bep16_conv bids_root/ analysis_level optional_arguments

However, it is important to note that ``bids_bep16_conv`` is a special case of a ``BIDS-App``
in that it aims to fascilitate the development of BEP16 and potential adjacent software packges.
As ``bids_bep16_conv`` focuses on ``BEP16`` and is intended to be run after the initial ``DWI`` ``preprocessing``
(e.g. via ``QSIprep``) it entails a ``derivative`` of ``derivatives`` application, it generates ``intermediate files``, ie 
files that will be further ``processed``.

Command-Line Arguments
======================
.. argparse::
  :ref: bids_bep16_conv.run_bids_bep16_conv.get_parser
  :prog: bids_bep16_conv
  :nodefault:
  :nodefaultconst:

Example Call(s)
---------------

Below you'll find two examples calls that hopefully help
you to familiarize yourself with ``bids_bep16_conv`` and its options.

Example 1
~~~~~~~~~

.. code-block:: bash

    bids_bep16_conv \
    /home/user/bids/ \
    participant \
    --participant_label 01 \
    --software dipy \
    --analysis DTI \ 
    --metadata /bids_dataset/code/dipy/DTI/analysis_metadata.json

Here's what's in this call:

- The 1st positional argument is the BIDS directory (``/home/user/bids``)
- The 2nd positional argument specifies whether we are running participant-
  or group-level mode. In more detail, if only a certain or all participants
  should be de-identified. You can choose between ``participant`` and ``group``.
  Here we choose ``participant``.
- The 3rd positional argument defines the ``subject id``, thus which specific
  participant should be de-identified. In this case, we choose ``01``.
- The 4th positional argument specifies which software should be used to run the subsequently
  specified analysis. You can choose between ``dipy`` and ``mrtrix``.
  In this example we choose ``dipy``.
- The 5th positional argument specifies the analysis that should be run and generate the outputs that
  will be restructured to be ``BEP16``-conform.
  You have the options ``DTI`` or ``CSD``.
  Here we chose ``DTI``.
- The 6th positional argument indicates the path to the JSON file that contains metadata information
  concerning the analysis. It will be used to generate and fill the JSON sidecar files of the 
  images obtained through the analysis.    

Example 2
~~~~~~~~~

.. code-block:: bash

    bids_bep16_conv \
    /home/peer/bids/ \
    group \
    --software mrtrix \
    --analysis DTI \ 

Here's what's in this call:

- The 1st positional argument again is the BIDS directory (``/home/user/bids``)
- The 2nd positional argument once more specifies whether we are running participant-
  or group-level mode. In more detail, if only a certain or all participants
  should be de-identified. You can choose between ``participant`` and ``group``.
  Here we choose ``group``. Hence, all participants will be de-identified and
  we don't need to specific a ``--participant_label`` as in Example 1.
- The 4th positional argument specifies which software should be used to run the subsequently
  specified analysis. You can choose between ``dipy`` and ``mrtrix``.
  This time we choose ``mrtrix``.
- The 5th positional argument specifies the analysis that should be run and generate the outputs that
  will be restructured to be ``BEP16``-conform.
  You have the options ``DTI`` or ``CSD``.
  Here we chose ``DTI``.

In contrast to Example 1, we didn't indicate a JSON metadata file concerning the analysis parameters.
Thus, the resulting JSON sidecar files will only contain placeholders that need to be filled out
manually. 

Example 3
~~~~~~~~~

.. code-block:: bash

    bids_bep16_conv \
    --download_dataset HBN \
    --download_path /user/home \ 

Here's what's in this call:

- The 1st positional argument indicates that we would like to download one of the example datasets. 
  You currently only have the option ``HBN``.
- The 2nd positional argument specifies the path the example dataset should be downloaded to.
  Here, for example, ``/user/home``.

Support and communication
=========================

The documentation of this project is found here: https://peerherholz.github.io/bids_bep16_conv.

All bugs, concerns and enhancement requests for this software can be submitted here:
https://github.com/peerherholz/bids_bep16_conv/issues.

If you have a problem or would like to ask a question about how to use ``bids_bep16_conv``,
please submit a question to `NeuroStars.org <http://neurostars.org/tags/bids_bep16_conv>`_ with an ``bids_bep16_conv`` tag.
NeuroStars.org is a platform similar to StackOverflow but dedicated to neuroinformatics.

All previous ``bids_bep16_conv`` questions are available here:
http://neurostars.org/tags/bids_bep16_conv/

Not running on a local machine? - Data transfer
===============================================

If you intend to run ``bids_bep16_conv`` on a remote system, you will need to
make your data available within that system first.

Please contact you local system administrator regarding
possible and favourable transfer options (e.g., `rsync <https://rsync.samba.org/>`_
or `FileZilla <https://filezilla-project.org/>`_).

A very comprehensive approach would be `Datalad
<http://www.datalad.org/>`_, which will handle data transfers with the
appropriate settings and commands.
Datalad also performs version control over your data.
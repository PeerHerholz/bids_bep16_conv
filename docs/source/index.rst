
============================
BIDS BEP-16 Conversion tools
============================

.. image:: https://github.com/PeerHerholz/bids_bep16_conv/actions/workflows/docs.yml/badge.svg
        :target: https://github.com/PeerHerholz/bids_bep16_conv/actions/workflows/docs.yml

.. image:: https://img.shields.io/pypi/v/bids_bep16_conv.svg
        :target: https://pypi.python.org/pypi/bids_bep16_conv

.. image:: https://img.shields.io/docker/pulls/peerherholz/bids_bep16_conv
    :alt: Dockerpulls
    :target: https://cloud.docker.com/u/peerherholz/repository/docker/peerherholz/bids_bep16_conv

.. image:: https://img.shields.io/github/repo-size/PeerHerholz/bids_bep16_conv.svg
        :target: https://github.com/PeerHerholz/bids_bep16_conv.zip

.. image:: https://img.shields.io/github/issues/PeerHerholz/bids_bep16_conv.svg
        :target: https://github.com/PeerHerholz/bids_bep16_conv/issues

.. image:: https://img.shields.io/github/issues-pr/PeerHerholz/bids_bep16_conv.svg
        :target: https://github.com/PeerHerholz/bids_bep16_conv/pulls

.. image:: https://img.shields.io/github/license/PeerHerholz/bids_bep16_conv.svg
        :target: https://github.com/PeerHerholz/bids_bep16_conv

A small package to implement conversions between `BIDS <https://bids.neuroimaging.io/>`_ BEP-16 (Diffusion Derivatives) compliant datasets and other/existing software outputs.

Introduction
============

``bids_bep16_conv`` aims to provide a set of tools for working with
`BIDS BEP-16`, specifically example datasets. In more detail, it includes
functionality to `access` and `convert` `example datasets`, as well as `convert`
outputs from different software libraries to and from `BEP-16` compliant data.

This documentation showcases the respective functionality and provides details concerning
its application and modules.
If you still have questions after going through provided here you can refer to 
the :ref:`api_ref` or ask a question on `GitHub <https://github.com/PeerHerholz/bids_bep16_conv/issues>`_.


Contents
========
.. toctree::
   :maxdepth: 1

   installation
   usage
   auto_examples/index
   api_ref
   release-history
   min_versions

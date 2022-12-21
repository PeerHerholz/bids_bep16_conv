============
Installation
============

In general, there are two distinct ways to install and use ``bids_bep16_conv``:
either through virtualization/container technology, that is `Docker`_ or
`Singularity`_, or in a `Bare metal version (Python 3.8+)`_.
Using a container method is highly recommended as they entail entire operating systems through kernel level virtualization and
thus include all software necessary to run ``bids_bep16_conv``, while at the same time presenting a lightweight alternative to virtual machines.
Once you are ready to run ``bids_bep16_conv``, see `Usage <./usage.rst>`_ for details.

Docker
======

In order to run ```bids_bep16_conv``` in a Docker container, Docker must be `installed
<https://docs.docker.com/engine/installation/>`_ on your system.
Once Docker is installed, you can get ``bids_bep16_conv`` through running the following
command in the terminal of your choice:

.. code-block:: bash

    docker pull peerherholz/bids_bep16_conv:version

Where ``version`` is the specific version of ``bids_bep16_conv`` you would like to use. For example, if you want 
to employ the ``latest``/most up to date ``version`` you can either run 

.. code-block:: bash

    docker pull peerherholz/bids_bep16_conv:latest

or the same command withouth the ``:latest`` tag, as ``Docker`` searches for the ``latest`` tag by default.
However, as the ``latest`` version is subject to changes and not necessarily in synch with the most recent ``numbered version``, it 
is recommend to utilize the latter to ensure reproducibility. For example, if you want to employ ``bids_bep16_conv v0.0.1`` the command would look as follows:

.. code-block:: bash

    docker pull peerherholz/bids_bep16_conv:v0.0.1

.. note::

   As of November 2020, `images older than 6 months will be deleted from Dockerhub
   <https://www.docker.com/pricing/retentionfaq>`_. As this is very problematic for everything
   reproducibility and version control, every version of the ``bids_bep16_conv images`` are additionally
   uploaded on `OSF <https://osf.io/x4dku/>`_ and can be installed as outlined further below.

After the command finished (it may take a while depending on your internet connection),
you can run ``bids_bep16_conv`` like this:

.. code-block:: bash

    $ docker run -ti --rm \
        -v path/to/your/bids_dataset:/bids_dataset:ro \
        peerherholz/bids_bep16_conv:latest \
        /bids_dataset \
        participant \
        --participant_label label \
        --software dipy \
        --analysis DTI \

Please have a look at the examples under `Usage <./usage.rst>`_ to get more information
about and familiarize yourself with ``bids_bep16_conv``'s functionality.


Singularity
===========

For security reasons, many HPCs (e.g., TACC) do not allow Docker containers, but support
allow `Singularity <https://github.com/singularityware/singularity>`_ containers. Depending
on the ``Singularity`` version available to you, there are two options to get ``bids_bep16_conv`` as
a ``Singularity image``.

Preparing a Singularity image (Singularity version >= 2.5)
----------------------------------------------------------
If the version of Singularity on your HPC is modern enough you can create a ``Singularity
image`` directly on the HCP.
This is as simple as: 

.. code-block:: bash

    $ singularity build /my_images/bids_bep16_conv-<version>.simg docker://peerherholz/bids_bep16_conv:<version>

Where ``<version>`` should be replaced with the desired version of ``bids_bep16_conv`` that you want to download.
For example, if you want to use ``bids_bep16_conv v0.0.4``, the command would look as follows.

.. code-block:: bash

    $ singularity build /my_images/bids_bep16_conv-v0.0.4.simg docker://peerherholz/bids_bep16_conv:v0.0.4


Preparing a Singularity image (Singularity version < 2.5)
---------------------------------------------------------
In this case, start with a machine (e.g., your personal computer) with ``Docker`` installed and
the use `docker2singularity <https://github.com/singularityware/docker2singularity>`_ to
create a ``Singularity image``. You will need an active internet connection and some time. 

.. code-block:: bash

    $ docker run --privileged -t --rm \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -v /absolute/path/to/output/folder:/output \
        singularityware/docker2singularity \
        peerherholz/bids_bep16_conv:<version>

Where ``<version>`` should be replaced with the desired version of ```bids_bep16_conv``` that you want
to download and ``/absolute/path/to/output/folder`` with the absolute path where the created ``Singularity image``
should be stored. Sticking with the example of ``bids_bep16_conv v0.0.4`` this would look as follows:

.. code-block:: bash

    $ docker run --privileged -t --rm \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -v /absolute/path/to/output/folder:/output \
        singularityware/docker2singularity \
        peerherholz/bids_bep16_conv:v0.0.4

Beware of the back slashes, expected for Windows systems. The above command would translate to Windows systems as follows:

.. code-block:: bash

    $ docker run --privileged -t --rm \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -v D:\host\path\where\to\output\singularity\image:/output \
        singularityware/docker2singularity \
        peerherholz/bids_bep16_conv:<version>


You can then transfer the resulting ``Singularity image`` to the HPC, for example, using ``scp``. ::

    $ scp peerherholz_bids_bep16_conv<version>.simg <user>@<hcpserver.edu>:/my_images

Where ``<version>`` should be replaced with the version of ``bids_bep16_conv`` that you used to create the ``Singularity image``, ``<user>``
with your ``user name`` on the HPC and ``<hcpserver.edu>`` with the address of the HPC.  

Running a Singularity Image
---------------------------

If the data to be preprocessed is also on the HPC, you are ready to run bids_bep16_conv. 

.. code-block:: bash

    $ singularity run --cleanenv /my_images/bids_bep16_conv-<version>.simg \
        path/to/your/bids_dataset \
        participant \
        --participant-label label \
        --deid defacing_algorithm

.. note::

    Make sure to check the name of the created ``Singularity image`` as that might
    diverge based on the method you used. Here and going forward it is assumed that you used ``Singularity >= 2.5``
    and thus ``bids_bep16_conv-<version>.simg`` instead of ``peerherholz_bids_bep16_conv<version>.simg``.   


.. note::

   Singularity by default `exposes all environment variables from the host inside
   the container <https://github.com/singularityware/singularity/issues/445>`_.
   Because of this your host libraries (such as nipype) could be accidentally used
   instead of the ones inside the container - if they are included in ``PYTHONPATH``.
   To avoid such situation we recommend using the ``--cleanenv`` singularity flag
   in production use. For example: ::

    $ singularity run --cleanenv /my_images/bids_bep16_conv-<version>.simg \
        path/to/your/bids_dataset \
        participant \
        --participant-label label \
        --software dipy \
        --analysis DTI


   or, unset the ``PYTHONPATH`` variable before running: ::

    $ unset PYTHONPATH; singularity /my_images/bids_bep16_conv-<version>.simg \
        path/to/your/bids_dataset \
        participant \
        --participant-label label \
        --software dipy \
        --analysis DTI

.. note::

   Depending on how ``Singularity`` is configured on your cluster it might or might not
   automatically ``bind`` (``mount`` or ``expose``) ``host folders`` to the container.
   If this is not done automatically you will need to ``bind`` the necessary folders using
   the ``-B <host_folder>:<container_folder>`` ``Singularity`` argument.
   For example: ::

    $ singularity run --cleanenv -B path/to/bids_dataset/on_host:/bids_dataset \
        /my_images/bids_bep16_conv-<version>.simg \
        bids_dataset \
        participant \
        --participant-label label \
        --software dipy \
        --analysis DTI

Bare metal version (Python 3.8+)
===========================================

``bids_bep16_conv`` is written using Python 3.8 (or above).
Until the first official version/release will be provided, `bids_bep16_conv`'s bare metal version can be installed by opening a terminal and running the following:

.. code-block:: bash

    git clone https://github.com/peerherholz/bids_bep16_conv.git
    cd bids_bep16_conv
    pip install .

Please note that you need to have at least `Python 3.8` installed.

Check your installation with the ``--version`` argument:

.. code-block:: bash

    $ bids_bep16_conv --version

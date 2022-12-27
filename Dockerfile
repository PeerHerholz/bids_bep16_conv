# Generated by: Neurodocker version 0.7.0+0.gdc97516.dirty
# Latest release: Neurodocker version 0.9.1
# Timestamp: 2022/12/26 13:40:23 UTC
# 
# Thank you for using Neurodocker. If you discover any issues
# or ways to improve this software, please submit an issue or
# pull request on our GitHub repository:
# 
#     https://github.com/ReproNim/neurodocker

FROM neurodebian:stretch-non-free

USER root

ARG DEBIAN_FRONTEND="noninteractive"

ENV LANG="en_US.UTF-8" \
    LC_ALL="en_US.UTF-8" \
    ND_ENTRYPOINT="/neurodocker/startup.sh"
RUN export ND_ENTRYPOINT="/neurodocker/startup.sh" \
    && apt-get update -qq \
    && apt-get install -y -q --no-install-recommends \
           apt-utils \
           bzip2 \
           ca-certificates \
           curl \
           locales \
           unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen \
    && dpkg-reconfigure --frontend=noninteractive locales \
    && update-locale LANG="en_US.UTF-8" \
    && chmod 777 /opt && chmod a+s /opt \
    && mkdir -p /neurodocker \
    && if [ ! -f "$ND_ENTRYPOINT" ]; then \
         echo '#!/usr/bin/env bash' >> "$ND_ENTRYPOINT" \
    &&   echo 'set -e' >> "$ND_ENTRYPOINT" \
    &&   echo 'export USER="${USER:=`whoami`}"' >> "$ND_ENTRYPOINT" \
    &&   echo 'if [ -n "$1" ]; then "$@"; else /usr/bin/env bash; fi' >> "$ND_ENTRYPOINT"; \
    fi \
    && chmod -R 777 /neurodocker && chmod a+s /neurodocker

ENTRYPOINT ["/neurodocker/startup.sh"]

ARG DEBIAN_FRONTEND="noninteractive"

ENV CONDA_DIR="/opt/miniconda-latest" \
    PATH="/opt/miniconda-latest/bin:$PATH"
RUN export PATH="/opt/miniconda-latest/bin:$PATH" \
    && echo "Downloading Miniconda installer ..." \
    && conda_installer="/tmp/miniconda.sh" \
    && curl -fsSL --retry 5 -o "$conda_installer" https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && bash "$conda_installer" -b -p /opt/miniconda-latest \
    && rm -f "$conda_installer" \
    && conda update -yq -nbase conda \
    && conda config --system --prepend channels conda-forge \
    && conda config --system --set auto_update_conda false \
    && conda config --system --set show_channel_urls true \
    && sync && conda clean -y --all && sync \
    && conda create -y -q --name bids_bep16_conv \
    && conda install -y -q --name bids_bep16_conv \
           "python=3.8" \
    && sync && conda clean -y --all && sync \
    && bash -c "source activate bids_bep16_conv \
    &&   pip install --no-cache-dir  \
             "dipy"" \
    && rm -rf ~/.cache/pip/* \
    && sync \
    && sed -i '$isource activate bids_bep16_conv' $ND_ENTRYPOINT

RUN bash -c 'source activate bids_bep16_conv && conda install -c mrtrix3 mrtrix3'

COPY [".", "/home/bids_bep16_conv"]

RUN bash -c 'source activate bids_bep16_conv && cd /home/bids_bep16_conv && pip install -e .'

ENV IS_DOCKER="1"

WORKDIR /tmp/

ENTRYPOINT ["/neurodocker/startup.sh", "bids_bep16_conv"]

RUN echo '{ \
    \n  "pkg_manager": "apt", \
    \n  "instructions": [ \
    \n    [ \
    \n      "base", \
    \n      "neurodebian:stretch-non-free" \
    \n    ], \
    \n    [ \
    \n      "arg", \
    \n      { \
    \n        "DEBIAN_FRONTEND": "noninteractive" \
    \n      } \
    \n    ], \
    \n    [ \
    \n      "miniconda", \
    \n      { \
    \n        "version": "latest", \
    \n        "conda_install": [ \
    \n          "python=3.8" \
    \n        ], \
    \n        "pip_install": [ \
    \n          "dipy" \
    \n        ], \
    \n        "create_env": "bids_bep16_conv", \
    \n        "activate": true \
    \n      } \
    \n    ], \
    \n    [ \
    \n      "run_bash", \
    \n      "source activate bids_bep16_conv && conda install -c mrtrix3 mrtrix3" \
    \n    ], \
    \n    [ \
    \n      "copy", \
    \n      [ \
    \n        ".", \
    \n        "/home/bids_bep16_conv" \
    \n      ] \
    \n    ], \
    \n    [ \
    \n      "run_bash", \
    \n      "source activate bids_bep16_conv && cd /home/bids_bep16_conv && pip install -e ." \
    \n    ], \
    \n    [ \
    \n      "env", \
    \n      { \
    \n        "IS_DOCKER": "1" \
    \n      } \
    \n    ], \
    \n    [ \
    \n      "workdir", \
    \n      "/tmp/" \
    \n    ], \
    \n    [ \
    \n      "entrypoint", \
    \n      "/neurodocker/startup.sh  bids_bep16_conv" \
    \n    ] \
    \n  ] \
    \n}' > /neurodocker/neurodocker_specs.json

#Generate Dockerfile.

#!/bin/sh

 set -e

generate_docker() {
  docker run --rm kaczmarj/neurodocker:0.6.0 generate docker \
             --base neurodebian:stretch-non-free \
             --pkg-manager apt \
             --arg DEBIAN_FRONTEND=noninteractive \
             --miniconda \
               version=latest \
               conda_install="python=3.8" \
               pip_install="dipy" \
               create_env='bids_bep16_conv' \
               activate=true \
            --copy . /home/bids_bep16_conv \
            --run-bash "source activate bids_bep16_conv && cd /home/bids_bep16_conv && pip install -e ." \
            --env IS_DOCKER=1 \
            --workdir '/tmp/' \
            --entrypoint "/neurodocker/startup.sh  bids_bep16_conv"
}

# generate files
generate_docker > Dockerfile

# check if images should be build locally or not
if [ $1 = local ]; then
    echo "docker image will be build locally"
    # build image using the saved files
    docker build -t bids_bep16_conv:local .
else
  echo "Image(s) won't be build locally."
fi            



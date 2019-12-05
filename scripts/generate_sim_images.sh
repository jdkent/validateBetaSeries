#!/bin/sh

set -e

# Generate Dockerfile.
# traits has additional gcc compiler dependencies that conda installs
generate_docker() {
  docker run --rm jdkent/neurodocker:dev generate docker \
    --base=codercom/code-server:2.1692-vsc1.39.2 \
    --pkg-manager=apt \
    --ants version=2.2.0 \
    --user=coder \
    --workdir="/home/coder" \
    --env "SHELL=/bin/bash" \
    --copy . /home/coder/project \
    --miniconda create_env='vbs' \
                conda_install='python=3.7 traits pytest flake8' \
                pip_install='-e /home/coder/project/code/' \
    --run "conda init" \
    --run 'code-server --install-extension eamodio.gitlens && code-server --install-extension ms-python.python' \
    --entrypoint '/neurodocker/startup.sh code-server --auth none /home/coder/project'

}

generate_docker > Dockerfile

docker build -t jdkent/vbs:dev .
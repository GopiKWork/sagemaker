
#FROM ubuntu:18.04
FROM amazonlinux:2

MAINTAINER Amazon AI <sage-learner@amazon.com>

#RUN apt-get -y update && apt-get install -y --no-install-recommends \
#         wget \
#    && rm -rf /var/lib/apt/lists/*

#RUN wget -O - https://fsx-lustre-client-repo-public-keys.s3.amazonaws.com/fsx-ubuntu-public-key.asc | gpg --dearmor | sudo tee /usr/share/keyrings/fsx-ubuntu-public-key.gpg >/dev/null

#RUN apt install -y lustre-client-modules-$(uname -r)
#RUN apt install -y linux-aws lustre-client-modules-aws && sudo reboot
RUN amazon-linux-extras install -y lustre

ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE

# Set up the entrypoint
COPY preload-fsx.sh /opt/preload-fsx.sh

#ENTRYPOINT nohup find /opt/ml/input/data/train/ -type f -print0 | xargs -0 -n 1 lfs hsm_restore
ENTRYPOINT /opt/preload-fsx.sh

FROM handsonsecurity/seed-ubuntu:large
  
RUN apt-get update \
    && apt-get install -y openssh-server openssh-client \
    && apt-get clean \
    && mkdir -p /run/sshd \
    && echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config

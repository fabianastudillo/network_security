FROM fabianastudillo/labsecuc:latest
  
RUN apt-get update \
    && apt-get install -y kmod openssh-server openssh-client \
    && apt-get clean \
    && mkdir -p /run/sshd \
    && echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config

FROM handsonsecurity/seed-ubuntu:small

# Install SSH server and sudo in a single layer to minimize image size
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        openssh-server \
        sudo && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Create student user with home directory and sudo privileges
RUN useradd -m -s /bin/bash student && \
    echo 'student:student' | chpasswd && \
    usermod -aG sudo student

# Configure SSH
RUN mkdir /var/run/sshd && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    echo 'root:root' | chpasswd

# Expose SSH port
EXPOSE 22

# Start SSH service
CMD ["/usr/sbin/sshd", "-D"]
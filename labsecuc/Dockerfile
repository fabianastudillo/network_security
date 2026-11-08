# Imagen única para el atacante y los hosts de la P-05, sin depender de la SEED VM.
#
# Reúne lo que en el diseño de SEED se repartía entre dos sitios:
#   - handsonsecurity/seed-ubuntu:large  -> herramientas de red, telnetd, Scapy
#   - SEED VM (src-vm/base.sh, python.sh) -> gcc + libpcap-dev para el Conjunto 2
#
# Se construye desde ubuntu, así que funciona en amd64 y en arm64 (Mac Apple Silicon).
FROM ubuntu:26.04
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get -y install --no-install-recommends \
        # Herramientas de red (las de seed-ubuntu:large)
        arping conntrack curl dnsutils iproute2 iptables iputils-ping \
        mtr-tiny net-tools netcat-openbsd procps traceroute \
        # Servidor y cliente Telnet (Tarea 2.1C, captura de contraseñas)
        openbsd-inetd telnet telnetd \
        # Cliente y servidor SSH (contraste cifrado frente a Telnet)
        openssh-client openssh-server \
        # Captura y análisis dentro del contenedor
        tcpdump tshark \
        # Conjunto 1: Python + Scapy
        python3 python3-scapy \
        # Conjunto 2: programas en C/C++ con pcap, raw sockets y OpenSSL
        gcc g++ libc6-dev libpcap-dev libssl-dev make \
        # Utilidades
        nano vim-tiny less unzip \
        # Multiplexor de terminal y prompt "hacker"
        tmux git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Starship: el prompt de la captura (los símbolos !N ?N son su git_status).
# Se descarga el binario estático según la arquitectura (amd64 / arm64), sin
# tuberías curl|sh: se extrae sólo el binario del tarball oficial.
RUN set -eux; \
    arch="$(dpkg --print-architecture)"; \
    case "$arch" in \
        amd64) target="x86_64-unknown-linux-gnu" ;; \
        arm64) target="aarch64-unknown-linux-gnu" ;; \
        *) echo "arquitectura no soportada: $arch" >&2; exit 1 ;; \
    esac; \
    curl -fsSL "https://github.com/starship/starship/releases/latest/download/starship-${target}.tar.gz" \
        | tar -xz -C /usr/local/bin starship; \
    starship --version

# Configuración compartida de Starship y de tmux con la marca UCuenca
# (cápsulas azul/rojo/gris del Kit de Marca 2026).
COPY starship.toml /etc/starship.toml
COPY tmux.conf /etc/tmux.conf

# En Ubuntu recientes (24.04 / 26.04) telnetd no se registra solo en inetd:
# sin esta línea, "openbsd-inetd start" arranca sin servicios y Telnet rechaza.
RUN echo 'telnet stream tcp nowait root /usr/sbin/telnetd telnetd' >> /etc/inetd.conf

# Las claves de host SSH no se hornean en la imagen: si no, todos los
# contenedores compartirían la misma identidad. Se generan al arrancar
# (ssh-keygen -A en el command del docker-compose).
RUN rm -f /etc/ssh/ssh_host_*

# Usuario "seed" con contraseña "dees", igual que en SEED (login por Telnet).
# Se borra el usuario "ubuntu" de la imagen base para que seed tenga UID 1000.
RUN userdel -r ubuntu \
    && useradd -m -s /bin/bash seed \
    && echo "root:dees" | chpasswd \
    && echo "seed:dees" | chpasswd

COPY bashrc /home/seed/.bashrc
COPY bashrc /root/.bashrc

WORKDIR /volumes
CMD ["/bin/bash"]

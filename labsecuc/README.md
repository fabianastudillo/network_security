# labsecuc

Imagen Docker para las prácticas de **Seguridad en Redes** (laboratorios estilo SEED)
de la Universidad de Cuenca. Reúne en una sola imagen las herramientas que el diseño
original de SEED repartía entre `handsonsecurity/seed-ubuntu:large` y la máquina
virtual SEED, y añade un entorno de terminal cómodo (tmux + prompt Starship).

- **Base:** `ubuntu:26.04`
- **Arquitectura:** `linux/amd64`
- **Usuario:** `seed` / contraseña `dees` (también `root` / `dees`)

## Qué incluye

**Herramientas de red:** `arping`, `conntrack`, `curl`, `dnsutils`, `iproute2`,
`iptables`, `iputils-ping`, `mtr-tiny`, `net-tools`, `netcat-openbsd`, `traceroute`.

**Servicios para las prácticas:** `telnetd` + `openbsd-inetd` (Tarea 2.1C, captura de
contraseñas), cliente/servidor `openssh`.

**Captura y análisis:** `tcpdump`, `tshark`.

**Programación de los conjuntos de tareas:** Python 3 + Scapy (Conjunto 1) y
`gcc`/`libc6-dev`/`libpcap-dev`/`make` para los programas en C con raw sockets (Conjunto 2).

**Terminal:** `tmux` (arranca solo al entrar por terminal interactiva) y el prompt
[Starship](https://starship.rs) con la identidad de la **Universidad de Cuenca**
(Kit de Marca 2026): cápsulas azul `#002856` dominante, rojo `#a51008` de acento y
gris para los metadatos. Los glifos powerline y los semicírculos de las cápsulas
requieren una Nerd Font en la terminal del anfitrión.

## Uso

```bash
docker pull fabianastudillo/labsecuc:large
docker run --rm -it fabianastudillo/labsecuc:large bash
```

Al entrar por terminal interactiva se abre tmux automáticamente. Los `docker-compose`
que lanzan `bash -c "..."` no se ven afectados (ese arranque solo ocurre en shells
interactivas).

### En un docker-compose

Reemplaza la imagen base de SEED por esta:

```yaml
services:
  hostA:
    image: fabianastudillo/labsecuc:large
    tty: true
    cap_add: [ALL]
```

## Etiquetas

| Tag      | Descripción                                  |
|----------|----------------------------------------------|
| `latest` | Última build (base `ubuntu:26.04`).          |
| `large`  | Alias de `latest` (nombre análogo al de SEED). |
| `1.5`    | Prompt y barra tmux con la marca UCuenca (cápsulas azul/rojo/gris). |
| `1.4`    | Prompt estilo p10k lean (marco de dos líneas). |
| `1.3`    | Prompt pastel powerline (ruta con iconos + git). |
| `1.2`    | Prompt de dos líneas + barra de tmux pulida. |
| `1.1`    | Release sobre `ubuntu:26.04`.                |
| `1.0`    | Release sobre `ubuntu:24.04`.                |

## Construir localmente

```bash
docker build -t labsecuc:latest .
```

## Notas

- Las claves de host SSH no se hornean en la imagen: se generan al arrancar
  (`ssh-keygen -A`) para que cada contenedor tenga identidad propia.
- `telnetd` se registra en `/etc/inetd.conf` porque en Ubuntu 24.04 no se autoinscribe.

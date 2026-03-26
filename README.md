# Network Security Lab Repository

Repositorio con prácticas, ejemplos y laboratorios del curso de ciberseguridad / seguridad de redes de la Universidad de Cuenca.

## Descripción

Este proyecto reúne material práctico orientado a distintos temas de seguridad informática, incluyendo:

- desbordamiento de búfer
- DNS local y DNS rebinding
- firewalls y filtrado de paquetes
- cifrado con clave pública y clave secreta
- funciones hash
- sniffing y spoofing
- ataques TCP
- túneles VPN

El objetivo del repositorio es centralizar ejemplos de código, configuraciones y entornos de laboratorio para facilitar el estudio y la experimentación.

## Estructura principal

### Laboratorios y temas

- **Buffer_Overflow/**: ejemplos en C sobre vulnerabilidades de memoria y pila.
- **DNS_Local/**: laboratorio de DNS local con contenedores y archivos de configuración.
- **DNS_Rebinding/**: entorno de pruebas para ataques de DNS rebinding.
- **Firewall/**: ejercicios de firewall, módulo de kernel y filtro de paquetes.
- **One_Way_Hash/**: material relacionado con funciones hash de una sola vía.
- **Public_Key_Encryption/**: ejemplos de criptografía asimétrica, incluyendo Diffie-Hellman.
- **Secret_Key_Encryption/**: ejercicios de criptografía simétrica y oráculos de cifrado.
- **Sniffing_Spoofing/**: laboratorio para análisis y manipulación de tráfico.
- **TCP_Attacks/**: ejemplos y pruebas de ataques sobre TCP.
- **VPN_Tunnel/**: laboratorio de túneles VPN.

### Archivos destacados

- **README.md**: descripción general del repositorio.
- **natas.md**: notas o material complementario.

## Tecnologías utilizadas

En este repositorio se usan principalmente:

- **C / C++**
- **Python**
- **Docker / Docker Compose**
- **HTML, CSS y JavaScript**
- configuraciones de red y servicios DNS

## Cómo usar este repositorio

1. Explora la carpeta del tema que quieras estudiar.
2. Revisa los archivos `README.md` internos cuando existan.
3. Levanta los laboratorios basados en Docker desde sus carpetas `Labsetup/` o `LabSetup/`.
4. Ejecuta y modifica los ejemplos de código según tus necesidades académicas.

## Requisitos sugeridos

Para trabajar con la mayoría de los laboratorios, se recomienda tener instalado:

- Docker
- Docker Compose
- Python 3
- compilador GCC / G++
- entorno Linux o compatible

## Propósito académico

Este repositorio tiene un enfoque académico y educativo. Su contenido está orientado al aprendizaje, la experimentación controlada y la comprensión de conceptos de seguridad informática.

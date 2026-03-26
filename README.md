<div align="center">

# Network Security Lab Repository

Repositorio académico con prácticas, ejemplos y laboratorios de **seguridad informática** y **seguridad de redes** de la **Universidad de Cuenca**.

![C](https://img.shields.io/badge/C-Labs-blue?style=for-the-badge&logo=c)
![Python](https://img.shields.io/badge/Python-Scripts-yellow?style=for-the-badge&logo=python)
![Docker](https://img.shields.io/badge/Docker-Lab_Environment-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Security](https://img.shields.io/badge/Focus-Network_Security-critical?style=for-the-badge)

</div>

---

## Descripción general

Este repositorio centraliza material práctico para estudiar conceptos clave de ciberseguridad mediante código, configuraciones, entornos aislados y laboratorios reproducibles.

### Temas cubiertos

- Buffer Overflow
- DNS local
- DNS Rebinding
- Firewalls y filtrado de paquetes
- Criptografía simétrica
- Criptografía asimétrica
- Funciones hash
- Sniffing y Spoofing
- Ataques TCP
- Túneles VPN

---

## Contenido del repositorio

| Carpeta | Descripción |
|---|---|
| **Buffer_Overflow/** | Ejemplos en C sobre memoria, pila y vulnerabilidades por desbordamiento. |
| **DNS_Local/** | Laboratorio de DNS local con contenedores, zonas y configuración de servidor. |
| **DNS_Rebinding/** | Entorno de pruebas para ataques de DNS rebinding y aplicaciones de demostración. |
| **Firewall/** | Ejercicios de firewall, módulo de kernel y filtrado de paquetes. |
| **One_Way_Hash/** | Material relacionado con funciones hash de una sola vía. |
| **Public_Key_Encryption/** | Ejemplos de criptografía asimétrica, incluyendo Diffie-Hellman. |
| **Secret_Key_Encryption/** | Prácticas de cifrado simétrico, análisis y oráculos de cifrado. |
| **Sniffing_Spoofing/** | Laboratorio para captura, análisis y manipulación de tráfico. |
| **TCP_Attacks/** | Ejemplos y pruebas relacionadas con ataques a nivel TCP. |
| **VPN_Tunnel/** | Laboratorio de túneles VPN y pruebas de conectividad. |

### Archivos destacados

- **README.md**: vista general del proyecto.
- **natas.md**: apuntes o material adicional.

---

## Tecnologías utilizadas

Este repositorio combina varias herramientas y lenguajes según el tipo de laboratorio:

- **C / C++** para ejercicios de bajo nivel y seguridad de memoria.
- **Python** para automatización, scripts y pruebas de red.
- **Docker / Docker Compose** para entornos de laboratorio reproducibles.
- **HTML, CSS y JavaScript** para interfaces de demostración.
- **Servicios DNS y configuración de red** para simulaciones realistas.

---

## Cómo usar este repositorio

### 1. Explorar un tema

Ingresa a la carpeta del laboratorio que deseas estudiar y revisa sus archivos principales.

### 2. Revisar documentación interna

Cuando exista documentación local, consulta los archivos `README.md` dentro de cada módulo.

### 3. Levantar laboratorios

Muchos ejercicios utilizan Docker. En esos casos, usa las carpetas `Labsetup/` o `LabSetup/` para iniciar el entorno.

### 4. Ejecutar y modificar ejemplos

Prueba los scripts, compila los ejemplos y adapta el código según el objetivo de la práctica.

---

## Requisitos sugeridos

Para trabajar con la mayoría de los laboratorios se recomienda contar con:

- **Docker**
- **Docker Compose**
- **Python 3**
- **GCC / G++**
- **Linux** o un entorno compatible

---

## Enfoque académico

> Este repositorio está orientado al aprendizaje, la experimentación controlada y la comprensión de conceptos de seguridad informática en un contexto académico.

Su contenido está pensado para:

- reforzar teoría con práctica
- montar entornos de prueba reproducibles
- analizar comportamientos de protocolos y sistemas
- comprender ataques y mecanismos de defensa

---

## Nota

Usa este material únicamente en entornos autorizados, controlados y con fines educativos.

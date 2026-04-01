<div align="center">

# SEED Labs - Laboratorio de Packet Sniffing y Spoofing

Laboratorio basado en SEED Labs para prácticas de **sniffing** y **spoofing** de paquetes de red usando contenedores Docker.

![Docker](https://img.shields.io/badge/Docker-Lab_Environment-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-Scripts-yellow?style=for-the-badge&logo=python)
![Security](https://img.shields.io/badge/Focus-Network_Security-critical?style=for-the-badge)

</div>

---

## Topología de red

```
        10.9.0.0/24                          192.168.60.0/24
 ┌─────────┬──────────┐               ┌──────────┬──────────┐
 │         │          │               │          │          │
10.9.0.1  10.9.0.5  10.9.0.6    192.168.60.1  .60.5    .60.6
attacker   hostA     hostB        hostC       hostD     hostE
                      │               │
                   10.9.0.11───192.168.60.11
                          Router
```

| Contenedor | Red              | IP             |
|------------|------------------|----------------|
| attacker   | 10.9.0.0/24      | 10.9.0.1       |
| hostA      | 10.9.0.0/24      | 10.9.0.5       |
| hostB      | 10.9.0.0/24      | 10.9.0.6       |
| router     | ambas            | 10.9.0.11 / 192.168.60.11 |
| hostC      | 192.168.60.0/24  | 192.168.60.1   |
| hostD      | 192.168.60.0/24  | 192.168.60.5   |
| hostE      | 192.168.60.0/24  | 192.168.60.6   |

---

## Requisitos

- **Docker**
- **Docker Compose**

---

## Uso

### 1. Cargar los aliases de Docker

```bash
source alias.sh
```

### 2. Construir y levantar los contenedores

```bash
dcbuild
dcup
```

### 3. Verificar los contenedores en ejecución

```bash
dockps
```

### 4. Acceder a un contenedor

```bash
docksh <ID>
```

### 5. Detener los contenedores

```bash
dcdown
```

---

## Estructura del proyecto

```
.
├── alias.sh              # Aliases para Docker Compose y contenedores
├── docker-compose.yml    # Definición de servicios y redes
├── volumes/              # Carpeta compartida entre todos los contenedores
│                           (montada en /volumes dentro de cada contenedor)
└── README.md
```

---

## Volumen compartido

La carpeta `volumes/` se monta en `/volumes` dentro de todos los contenedores. Coloca aquí los scripts de Python u otros archivos que necesites compartir entre los hosts.

---

> Este laboratorio está orientado al aprendizaje y la experimentación controlada en un contexto académico. Úsalo únicamente en entornos autorizados y con fines educativos.

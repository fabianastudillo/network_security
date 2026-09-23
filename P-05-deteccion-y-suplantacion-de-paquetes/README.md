# P-05 · Detección y Suplantación de Paquetes

> Práctica del **Manual de Prácticas** de Seguridad en Redes · INGE-00107 · Universidad de Cuenca.  
> Documento generado desde el manual: no lo edite a mano (véase el [índice de prácticas](../practicas/README.md)).

| Campo | Valor |
| --- | --- |
| **Asignatura** | Seguridad en Redes |
| **Docente** | Dr. Fabián Astudillo-Salinas |
| **Unidad** | 500 – Detección y suplantación de paquetes |
| **Código** | INGE-00107 |
| **Modalidad** | Presencial |
| **Valoración** | 10 puntos |
| **Grupos** | Máx. 3 estudiantes |
| **Entrega** | Según calendario |
| **ABET** | SO4 – Responsabilidad Ética y Profesional (PI 4.1 y PI 4.2) — representa el 30 % de la valoración |

## Marco Teórico

Los fundamentos teóricos sintetizados en esta sección se basan en [1], [2], [3]; se recomienda consultar dichas fuentes para una exposición más profunda. El procedimiento de laboratorio adapta el *Packet Sniffing and Spoofing Lab* de SEED [3].

### Sniffing y spoofing

El **sniffing** (captura de paquetes) y el **spoofing** (suplantación) son dos conceptos fundamentales en seguridad de redes y, a la vez, dos amenazas importantes. Herramientas como **Wireshark**, **Tcpdump**, **Netwox** y **Scapy** las implementan; tan importante como usarlas es comprender *cómo* funcionan internamente. Esta práctica cubre: cómo funcionan el sniffing y el spoofing, la captura de paquetes con la biblioteca `pcap` y con Scapy, el spoofing con *raw sockets* y con Scapy, y la manipulación de paquetes con Scapy.

> [!NOTE]
> **Dos conjuntos de tareas**
>
> La práctica tiene dos conjuntos independientes: el **Conjunto 1** usa **Scapy** (Python, pocas líneas) y el **Conjunto 2** consiste en escribir programas en **C** desde cero (con `pcap` y *raw sockets*), para entender en profundidad cómo operan las herramientas. El Conjunto 2 requiere una sólida base de programación.

**Objetivo general**
Implementar programas de sniffing y spoofing, con Scapy (Python) y desde cero en C (`pcap` y *raw sockets*), comprendiendo los mecanismos subyacentes de la captura y la suplantación de paquetes.
**Objetivos específicos**

- **OE1.** Capturar paquetes con Scapy aplicando filtros BPF y suplantar paquetes ICMP con IP origen arbitraria.
- **OE2.** Implementar un *traceroute* y un programa *sniff-and-spoof* con Scapy.
- **OE3.** Escribir un sniffer en C con la biblioteca `pcap` (filtros y captura de contraseñas).
- **OE4.** Escribir un programa de spoofing en C con *raw sockets* y combinar ambas técnicas (sniff-and-spoof en C).

## Actividades previas

Antes de la sesión de laboratorio, cada estudiante debe completar las siguientes actividades preparatorias:

- **AP1.** Leer el marco teórico de esta práctica y las referencias citadas para resolver dudas conceptuales antes de ingresar al laboratorio.
- **AP2.** Verificar que el entorno virtual (VMs SEED/Kali y red NAT) esté operativo conforme al capítulo *Configuración del Entorno: SEED VM en VirtualBox*.
- **AP3.** Tomar una *snapshot* del estado inicial de cada VM involucrada en la práctica para poder revertir cambios.
- **AP4.** Revisar la Sección [Seguridad y normas generales del laboratorio](../practicas/00-normas-generales.md#seguridad-y-normas-generales-del-laboratorio) (Seguridad y normas generales del laboratorio).
- **AP5.** Preparar la bitácora digital (plantilla provista o documento propio) para registrar comandos, capturas y observaciones durante la sesión.

## Materiales y Equipos

| Recurso | Descripción |
| --- | --- |
| SEED Ubuntu 20.04 VM | Entorno de laboratorio SEED |
| Docker + Docker Compose | Atacante y dos hosts (A/B) en una LAN |
| Python 3 + Scapy | Conjunto 1 (sniffing/spoofing en Python) |
| GCC + `libpcap` | Conjunto 2 (sniffer en C, *raw sockets*) |
| Wireshark / Tcpdump | Análisis y verificación de tráfico |

> [!NOTE]
> **Provisión de materiales**
>
> El estudiante adquiere o instala por su cuenta el equipo personal (laptop), las máquinas virtuales (VirtualBox, SEED VM, Kali Linux, contenedores Docker) y todo el software listado arriba. El laboratorio de la Carrera de Telecomunicaciones provee el espacio físico, el mobiliario y **acceso a Internet supervisado** para la descarga de imágenes, paquetes y consulta de documentación durante la sesión. El laboratorio no entrega equipos de cómputo personales ni licencias de software.

## Entorno de Laboratorio

> **Figura 1.** Topología del laboratorio P-05 (*Lab environment setup*): atacante y dos hosts (A/B) en la LAN `10.9.0.0/24` (adaptado de la Fig. 1 del SEED Packet Sniffing and Spoofing Lab).  
> *(diagrama vectorial; se reproduce en el PDF del manual)*

Levante la topología con `docker-compose` (alias `dcbuild`, `dcup`, `dockps`, `docksh`). El contenedor atacante usa `network_mode: host` para poder husmear el tráfico de los demás contenedores. Antes de programar, obtenga el nombre de la interfaz de la red `10.9.0.0/24` en la VM (suele empezar por `br-`):

**Listado 1.** Obtener el nombre de la interfaz

```bash
$ ifconfig | grep -B1 10.9.0.1     # busca la interfaz br-... con IP 10.9.0.1
$ docker network ls                # alternativamente, el ID de la red seed-net
```

## Consideraciones de seguridad

Antes de iniciar el procedimiento, revise la Sección [Seguridad y normas generales del laboratorio](../practicas/00-normas-generales.md#seguridad-y-normas-generales-del-laboratorio) (Seguridad y normas generales del laboratorio). Para esta práctica se destacan los siguientes riesgos y precauciones específicas:

- **Aislamiento de red obligatorio**: las herramientas ofensivas y los tráficos manipulados deben permanecer dentro de las VMs y la red NAT del laboratorio. Está prohibido ejecutar comandos de esta práctica contra la red institucional, redes públicas o equipos de terceros.
- **Snapshots y reversibilidad**: tome una instantánea antes de ejecutar comandos potencialmente destructivos (modificación de `iptables`, tablas ARP/ruteo, `/etc/hosts`, `rc.local`, claves, certificados, etc.).
- **Marco legal**: el uso de las herramientas fuera del entorno autorizado puede tipificarse como delito informático (COIP Arts. 229 y 234; Ley Orgánica de Protección de Datos Personales). Véase el warningbox de la Sección [Seguridad y normas generales del laboratorio](../practicas/00-normas-generales.md#seguridad-y-normas-generales-del-laboratorio).
- **Riesgos eléctricos y ergonomía**: aplique las pausas activas y las verificaciones eléctricas de las Secciones *Riesgos eléctricos* y *Ergonomía* dentro de Sección [Seguridad y normas generales del laboratorio](../practicas/00-normas-generales.md#seguridad-y-normas-generales-del-laboratorio) (Art. 37 y Art. 38 del Reglamento UC-CU-REG-006-2024).

> [!WARNING]
> **Riesgos específicos de la práctica**
>
> Antes de avanzar, el estudiante debe identificar y discutir con el docente cualquier riesgo adicional propio de esta práctica (por ejemplo: pérdida de conectividad de la VM atacante, denegación de servicio inducida sobre el host, generación accidental de tráfico ruidoso que sature la red NAT). Documente estos riesgos y las medidas de mitigación en la bitácora.

## Procedimiento

El procedimiento se divide en dos conjuntos independientes. El **Conjunto 1** usa Scapy; ejecútelo con privilegio de `root` (el spoofing lo requiere) e importe los módulos con `from scapy.all import *`.

### Conjunto 1 — Sniffing y spoofing con Scapy

#### Tarea 1.1 — Captura de paquetes (sniffing)

##### Tarea 1.1A — Programa básico.

Escriba un *sniffer* que invoque una función *callback* por cada paquete capturado. Ejecútelo con y sin privilegio de `root` y explique la diferencia.

**Listado 2.** Sniffer básico con Scapy

```python
#!/usr/bin/env python3
from scapy.all import *

def print_pkt(pkt):
    pkt.show()

pkt = sniff(iface='br-...', filter='icmp', prn=print_pkt)
```

##### Tarea 1.1B — Filtros BPF.

Repita la captura aplicando, por separado, los siguientes filtros (sintaxis *Berkeley Packet Filter*):

- Solo paquetes ICMP.
- Paquetes TCP de una IP concreta y con puerto destino 23.
- Paquetes hacia/desde una subred concreta (p. ej. `128.230.0.0/16`; no use la subred de su propia VM).

#### Tarea 1.2 — Suplantación de paquetes ICMP

Scapy permite fijar cualquier campo del paquete. Suplante un *ICMP echo request* con IP origen arbitraria; con Wireshark, verifique que el destino responde con un *echo reply* a la IP falsificada.

**Listado 3.** Spoofing de un ICMP echo request

```python
>>> from scapy.all import *
>>> a = IP()
>>> a.dst = '10.0.2.3'      # IP destino
>>> b = ICMP()              # por defecto, echo request
>>> p = a/b                 # el operador / apila las capas
>>> send(p)
```

#### Tarea 1.3 — Traceroute

Estime la distancia (número de routers) hasta un destino: envíe paquetes incrementando el TTL desde 1; cada router que lo descarta devuelve un ICMP *time exceeded*, revelando su IP, hasta alcanzar el destino.

**Listado 4.** Traceroute con Scapy (una ronda)

```python
a = IP()
a.dst = '1.2.3.4'
a.ttl = 3            # incrementar 1, 2, 3, ... en cada ronda
b = ICMP()
send(a/b)
```

#### Tarea 1.4 — Sniff-and-spoof

Combine ambas técnicas: el programa husmea la LAN y, ante cualquier *echo request* (sea cual sea el destino), responde inmediatamente con un *echo reply* suplantado; así un `ping` siempre recibe respuesta. Pruebe con tres destinos y explique (use ARP y enrutamiento):

**Listado 5.** Destinos a probar con ping

```bash
ping 1.2.3.4     # host inexistente en Internet
ping 10.9.0.99   # host inexistente en la LAN
ping 8.8.8.8     # host existente en Internet
```

**Listado 6.** Sniff-and-spoof: responder pings

```python
#!/usr/bin/env python3
from scapy.all import *

def spoof_reply(pkt):
    if ICMP in pkt and pkt[ICMP].type == 8:    # echo request
        ip   = IP(src=pkt[IP].dst, dst=pkt[IP].src, ihl=pkt[IP].ihl)
        icmp = ICMP(type=0, id=pkt[ICMP].id, seq=pkt[ICMP].seq)
        data = pkt[Raw].load if Raw in pkt else b''
        send(ip/icmp/data, verbose=0)

sniff(iface='br-...', filter='icmp', prn=spoof_reply)
```

### Conjunto 2 — Programas en C (pcap y raw sockets)

Compile el código C en la VM anfitriona y ejecútelo dentro del contenedor atacante; copie el binario con `docker cp <bin> <id>:/tmp`.

#### Tarea 2.1 — Sniffer con la biblioteca pcap

##### Tarea 2.1A — Cómo funciona un sniffer.

Un sniffer con `pcap` sigue una secuencia simple: abrir la sesión, compilar y fijar el filtro, y capturar. Complete el programa para imprimir las IP origen/destino de cada paquete; ejecútelo con `root` y explique por qué se requiere ese privilegio.

**Listado 7.** Sniffer con libpcap (esqueleto)

```c
#include <pcap.h>
#include <stdio.h>
#include <stdlib.h>

void got_packet(u_char *args, const struct pcap_pkthdr *header,
                const u_char *packet)
{
    printf("Got a packet\n");
}

int main()
{
    pcap_t *handle;
    char errbuf[PCAP_ERRBUF_SIZE];
    struct bpf_program fp;
    char filter_exp[] = "icmp";
    bpf_u_int32 net;

    // 1) abrir sesión en la NIC (cambie "eth3" por su interfaz br-...)
    handle = pcap_open_live("eth3", BUFSIZ, 1, 1000, errbuf);
    // 2) compilar y fijar el filtro BPF
    pcap_compile(handle, &fp, filter_exp, 0, net);
    if (pcap_setfilter(handle, &fp) != 0) {
        pcap_perror(handle, "Error:"); exit(EXIT_FAILURE);
    }
    // 3) capturar paquetes
    pcap_loop(handle, -1, got_packet, NULL);
    pcap_close(handle);
    return 0;
}
// Compilar:  gcc -o sniff sniff.c -lpcap
```

##### Tarea 2.1B — Filtros.

Escriba filtros `pcap` para: (1) ICMP entre dos hosts concretos; (2) TCP con puerto destino en el rango 10–100.

##### Tarea 2.1C — Captura de contraseñas.

Modifique el sniffer para imprimir la parte de datos de los paquetes TCP y capture la contraseña cuando alguien usa `telnet` en la red monitorizada.

#### Tarea 2.2 — Spoofing con raw sockets

Los *raw sockets* dan control total sobre la construcción del paquete. El proceso tiene cuatro pasos: (1) crear el socket, (2) fijar la opción de socket, (3) construir el paquete y (4) enviarlo.

**Listado 8.** Spoofing con raw socket (esqueleto)

```c
int sd;
struct sockaddr_in sin;
char buffer[1024];

// IPPROTO_RAW indica que la cabecera IP ya está incluida
sd = socket(AF_INET, SOCK_RAW, IPPROTO_RAW);
if (sd < 0) { perror("socket() error"); exit(-1); }
sin.sin_family = AF_INET;

// Construir aquí el paquete IP en buffer[]:
//   - cabecera IP, cabecera TCP/UDP/ICMP, datos
//   - atención al orden de bytes red/host

// Enviar el paquete (ip_len = tamaño real del paquete)
if (sendto(sd, buffer, ip_len, 0,
           (struct sockaddr *)&sin, sizeof(sin)) < 0) {
    perror("sendto() error"); exit(-1);
}
```

**Tarea 2.2A:** escriba el programa de spoofing y demuestre con Wireshark que envía paquetes IP suplantados. **Tarea 2.2B:** suplante un *ICMP echo request* en nombre de otra máquina hacia un host remoto vivo y compruebe que el *echo reply* vuelve. Responda: (Q4) ¿se puede fijar el campo *longitud* a un valor arbitrario?; (Q5) ¿hay que calcular el *checksum* de la cabecera IP?; (Q6) ¿por qué se requiere `root`?

#### Tarea 2.3 — Sniff-and-spoof en C

Combine ambas técnicas en C: el programa husmea la LAN y, ante cualquier *echo request*, responde con un *echo reply* suplantado, de modo que un `ping` a cualquier IP X siempre reciba respuesta.

##### Guía: paquetes en raw sockets y orden de bytes.

El paquete se construye en un *buffer*; conviene mapearlo a estructuras (`struct ipheader`, `udpheader`, etc.) para acceder a sus campos. Recuerde convertir los datos multibyte al **orden de red** (*big endian*) con `htons()`/`htonl()` (y `ntohs()`/`ntohl()` al leer), y usar `inet_addr()`/`inet_aton()` para las direcciones IP.

## Recolección y análisis de datos

Durante la ejecución del procedimiento, registre en su bitácora los datos solicitados a continuación. Las tablas siguientes (o equivalentes en su informe) forman parte del entregable, conforme a la Sección [Directrices generales para el informe técnico](../practicas/00-normas-generales.md#directrices-generales-para-el-informe-técnico) (Directrices generales para el informe técnico).

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

- **P1.** ¿Por qué un programa de sniffing/spoofing requiere privilegio de `root`? ¿Dónde falla si se ejecuta sin él?
- **P2.** Resuma la secuencia de llamadas esenciales de un sniffer con `pcap` y explique el papel del **modo promiscuo** (parámetro de `pcap_open_live`).
- **P3.** En el *sniff-and-spoof* (Tarea 1.4), explique con ARP y enrutamiento por qué `ping 1.2.3.4`, `ping 10.9.0.99` y `ping 8.8.8.8` se comportan de forma distinta.
- **P4.** Con raw sockets: ¿se puede fijar el campo *longitud* a un valor arbitrario? ¿Hay que calcular el *checksum* de la cabecera IP? (Tareas 2.2, Q4–Q5).
- **P5.** ¿Por qué hay que respetar el **orden de bytes de red** al construir paquetes en C? Mencione las funciones de conversión.
- **P6.** ¿Qué medidas contrarrestan el IP spoofing en redes modernas (p. ej. *ingress/egress filtering*, BCP 38)?

## Actividad ABET — SO4: Responsabilidad Ética y Profesional

Esta actividad mide el **Student Outcome 4 (SO4)** de la Carrera de Telecomunicaciones requerido para la acreditación ABET: *habilidad para reconocer las responsabilidades éticas y profesionales en situaciones de ingeniería y emitir juicios fundamentados, considerando el impacto global, económico, medioambiental y social de las soluciones propuestas.* Representa el **30 %** de la valoración total de la práctica y evalúa los indicadores PI 4.1 y PI 4.2 mediante las preguntas SO4-1 y SO4-2.

- **SO4-1.** **[PI 4.1 — 15 %] Ética y responsabilidad profesional ante la captura inadvertida de credenciales**
  Un técnico de red usa un analizador de paquetes para diagnosticar un problema de rendimiento en la red corporativa y captura inadvertidamente credenciales de usuarios en texto claro (sesiones Telnet/FTP). Analice:

  - **a)** Las **responsabilidades éticas y legales** del técnico ante esta captura no intencional (COIP Art. 229, LOPDP).
  - **b)** El **procedimiento ético correcto**: qué hacer con los datos capturados, a quién informar y cómo documentar el incidente sin vulnerar la privacidad adicional.
  - **c)** Cómo **distinguir entre sniffing autorizado** (diagnóstico de red) y no autorizado (espionaje), y las implicaciones legales de cada caso.
- **SO4-2.** **[PI 4.2 — 15 %] Impacto económico, social y ambiental de un sniffing malicioso en un hospital**
  Un empleado malintencionado realiza sniffing pasivo en la red de un hospital ecuatoriano durante 30 días, capturando historias clínicas y credenciales de 5 000 pacientes. Analice de manera integral las siguientes dimensiones:

  - **a)** **Económico:** multas bajo la LOPDP, costos de notificación a afectados, litigios y pérdida de contratos con aseguradoras.
  - **b)** **Social:** exposición de datos de salud sensibles, estigmatización de pacientes, erosión de la confianza en el sistema de salud digital.
  - **c)** **Ambiental:** energía consumida en la respuesta al incidente y en el rediseño de la infraestructura de red.
  - **d)** **Contramedidas:** dos técnicas (cifrado end-to-end, segmentación de red/VLANs) y una política organizacional, citando HIPAA, ISO/IEC 27001 o NIST SP 800-45.

## Discusión y conclusiones

A partir de los datos recolectados y del análisis realizado, elabore una discusión que responda al menos a las siguientes preguntas guía:

- **DC1.** ¿Se alcanzaron los objetivos planteados? Justifique cada uno con evidencia experimental concreta (capturas, métricas, salidas de comandos).
- **DC2.** ¿Qué limitaciones impone el entorno virtualizado a los resultados? ¿Cómo se trasladarían las observaciones a un escenario real de producción?
- **DC3.** ¿Qué contramedidas o controles de seguridad mitigan el ataque o refuerzan la defensa estudiada? Cite al menos una buena práctica de la industria, una RFC o un estándar (ISO/IEC, IEEE, NIST) pertinente.
- **DC4.** ¿Qué errores se cometieron durante la práctica y qué recomendaciones daría a futuros estudiantes para evitarlos?

Cierre con **conclusiones** (3–5 viñetas) que resuman los hallazgos principales y los vinculen explícitamente con los *Resultados de Aprendizaje* de la asignatura.

## Entregables

1. **Informe técnico** detallado con capturas que describan lo realizado y observado en cada tarea de ambos conjuntos: sniffer y spoofing con Scapy (1.1–1.4) y los programas en C (2.1–2.3), incluyendo capturas Wireshark y la explicación de cada fragmento de código (adjuntar sin explicar no recibe puntaje). Bibliografía IEEE (≥3 fuentes).
2. **Código fuente** comentado: scripts Scapy (sniffer, spoofing, traceroute, sniff-and-spoof) y programas en C (sniffer `pcap` y spoofing con *raw sockets*).
3. **Respuestas a la Actividad ABET – SO4** (preguntas SO4-1 y SO4-2), integradas en el informe técnico con extensión de 1–2 páginas por pregunta y las fuentes citadas según norma IEEE.

## Rúbrica de Evaluación

**Tabla 3.** Rúbrica — P-05 (10 puntos)

| Criterio | Peso | Indicador | Descripción |
| --- | --- | --- | --- |
| Scapy: sniffing/spoofing | 18 % | Tareas 1.1–1.3 | Captura con filtros BPF, spoofing ICMP y traceroute funcionando. |
| Scapy: sniff-and-spoof | 10 % | Tarea 1.4 | `ping` responde a IPs inexistentes; observaciones explicadas. |
| C: sniffer con pcap | 18 % | Tarea 2.1 | Sniffer en C con filtros; IPs (y contraseña Telnet) capturadas. |
| C: spoofing raw sockets | 14 % | Tareas 2.2–2.3 | Paquetes IP/ICMP suplantados con *raw sockets*; sniff-and-spoof en C. |
| Análisis | 10 % | Preguntas respondidas | Respuestas técnicas con fundamento. |
| **ABET – SO4: Responsabilidad Ética y Profesional (30 %)** |   |   |   |
| PI 4.1 – Ética profesional | 15 % | Respuesta ética fundamentada | Aplica principios éticos y legales al escenario del incidente; la cadena de notificación está justificada. |
| PI 4.2 – Impacto integral | 15 % | Análisis de impacto | Evalúa impacto económico, social y ambiental con contramedidas técnicas y organizacionales, citando al menos un estándar internacional. |

**Tabla 4.** Escala ABET SO4 — P-05

| PI | No cumple<br>(0–59 %) | Cumple parcialmente<br>(60–69 %) | Cumple<br>(70–79 %) | Supera<br>(80–89 %) | Supera ampliamente<br>(90–100 %) |
| --- | --- | --- | --- | --- | --- |
| 4.1 | No aplica principios éticos ni profesionales al evaluar la situación de incidente. | Aplica de manera inconsistente los principios éticos; el análisis legal es superficial o erróneo. | Aplica de manera básica los principios éticos; menciona el marco legal ecuatoriano sin análisis profundo. | Aplica coherentemente su juicio ético y profesional; integra el COIP y la LOPDP con argumentación clara. | Aplica de manera ejemplar e integral su juicio ético; argumenta cada decisión con evidencia y normativas citadas con precisión. |
| 4.2 | No considera ninguno de los tres impactos (económico, social, ambiental). | Considera parcialmente uno o dos de los impactos; las contramedidas no citan estándares. | Considera los tres impactos de forma adecuada; propone contramedidas pertinentes con al menos un estándar citado. | Integra los tres impactos con análisis detallado y contramedidas bien fundamentadas en estándares internacionales. | Realiza una evaluación exhaustiva de los tres impactos; las contramedidas son innovadoras y se respaldan en múltiples estándares. |

## Referencias

1. Biondi, Philippe and Scapy community, «Scapy --- Packet manipulation library». 2024. <https://scapy.net>.
2. Wireshark Foundation, «Wireshark Network Protocol Analyzer». 2024. <https://www.wireshark.org>.
3. Du, Wenliang, «Computer & Internet Security: A Hands-on Approach». Independently published, 2019.

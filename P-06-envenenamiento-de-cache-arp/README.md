<div align="center">

# P-06 · Envenenamiento de Caché ARP

![Docker](https://img.shields.io/badge/Docker-Lab_Environment-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-Scripts-yellow?style=for-the-badge&logo=python)
![Security](https://img.shields.io/badge/Focus-Network_Security-critical?style=for-the-badge)

</div>

> Práctica del **Manual de Prácticas** de Seguridad en Redes · INGE-00107 · Universidad de Cuenca.  
> Documento generado desde el manual: no lo edite a mano (véase el [índice de prácticas](../practicas/README.md)).

> [!NOTE]
> El entorno de esta práctica todavía no está publicado en esta carpeta.

| Campo | Valor |
| --- | --- |
| **Asignatura** | Seguridad en Redes |
| **Docente** | Dr. Fabián Astudillo-Salinas |
| **Unidad** | 500 – Detección y suplantación |
| **Código** | INGE-00107 |
| **Modalidad** | Presencial |
| **Valoración** | 10 puntos |
| **Grupos** | Máx. 3 estudiantes |
| **Entrega** | Según calendario |
| **ABET** | SO4 – Responsabilidad Ética y Profesional (PI 4.1 y PI 4.2) — representa el 30 % de la valoración |

## Marco Teórico

Los fundamentos teóricos sintetizados en esta sección se basan en [1], [2]; se recomienda consultar dichas fuentes para una exposición más profunda. El procedimiento de laboratorio adapta el *ARP Cache Poisoning Attack Lab* de SEED [2].

### El protocolo ARP y el envenenamiento de caché

El **ARP** (Address Resolution Protocol) descubre la dirección de enlace (MAC) asociada a una dirección IP dentro de una LAN. Es un protocolo muy simple que **no implementa ninguna medida de seguridad**: cualquier máquina puede enviar respuestas ARP con información falsa. El **envenenamiento de caché ARP** (ARP cache poisoning) explota esto para engañar a la víctima e insertar asociaciones IP→MAC falsas en su caché, de modo que su tráfico se redirige hacia el atacante, habilitando un ataque **Man-In-The-Middle (MITM)**. Esta práctica cubre: el protocolo ARP, el ataque de envenenamiento de caché ARP, el ataque MITM y la programación con Scapy.

El entorno de laboratorio usa tres contenedores en la red `10.9.0.0/24`: Host A (`10.9.0.5`), Host B (`10.9.0.6`) y Host M atacante (`10.9.0.105`); el ataque está limitado a la LAN.

**Objetivo general**
Usar Scapy para lanzar un ataque de envenenamiento de caché ARP y, sobre esa base, ejecutar un ataque MITM que intercepte y modifique sesiones Telnet y Netcat entre dos víctimas.
**Objetivos específicos**

- **OE1.** Construir paquetes ARP con Scapy y envenenar la caché usando tres métodos: ARP *request*, ARP *reply* y ARP *gratuitous*.
- **OE2.** Comparar el éxito del ataque cuando la entrada ya existe o no en la caché de la víctima.
- **OE3.** Envenenar las cachés de A y B y convertir a M en MITM (con/sin reenvío IP) para una sesión Telnet.
- **OE4.** Interceptar y modificar el contenido de una sesión Telnet (reemplazo de caracteres) y de una sesión Netcat (reemplazo de texto).

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
| Docker + Docker Compose | Host A, Host B y atacante M en una LAN |
| Python 3 + Scapy | Construcción de paquetes ARP y MITM |
| netcat (`nc`) + telnet | Tráfico de prueba entre A y B |
| Wireshark / Tcpdump | Verificación del ataque |

> [!NOTE]
> **Provisión de materiales**
>
> El estudiante adquiere o instala por su cuenta el equipo personal (laptop), las máquinas virtuales (VirtualBox, SEED VM, Kali Linux, contenedores Docker) y todo el software listado arriba. El laboratorio de la Carrera de Telecomunicaciones provee el espacio físico, el mobiliario y **acceso a Internet supervisado** para la descarga de imágenes, paquetes y consulta de documentación durante la sesión. El laboratorio no entrega equipos de cómputo personales ni licencias de software.

## Entorno de Laboratorio

> **Figura 1.** Topología del laboratorio P-06 (*Lab environment setup*): Host A, Host B y el atacante M en la LAN `10.9.0.0/24` (adaptado de la Fig. 1 del SEED ARP Cache Poisoning Attack Lab).  
> *(diagrama vectorial; se reproduce en el PDF del manual)*

Levante la topología con `docker-compose` (alias `dcbuild`, `dcup`, `dockps`, `docksh`). El contenedor atacante usa `privileged: true` para poder modificar parámetros del kernel con `sysctl` (p. ej. el reenvío IP) y `network_mode: host`/ `tcpdump` para husmear el tráfico de la LAN.

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

### Tarea 1 — Envenenamiento de caché ARP

El objetivo es que A añada una entrada falsa a su caché ARP, de modo que la IP de B (`10.9.0.6`) quede asociada a la MAC de M. Inspeccione la caché con `arp -n` antes y después. El paquete ARP se construye con Scapy apilando `Ether` y `ARP` (use `ls(ARP)` y `ls(Ether)` para ver los campos):

**Listado 1.** Estructura de un paquete ARP en Scapy

```python
#!/usr/bin/env python3
from scapy.all import *

E = Ether()
A = ARP()
A.op = 1            # 1 = ARP request; 2 = ARP reply

pkt = E/A
sendp(pkt)
```

Pruebe los **tres métodos** y reporte si cada uno funciona:

- **Tarea 1.A (ARP request).** En M, construya un *ARP request* que mapee la IP de B a la MAC de M, envíelo a A y verifique la caché.
- **Tarea 1.B (ARP reply).** En M, construya un *ARP reply* que mapee la IP de B a la MAC de M. Pruébelo en dos escenarios: *(1)* la IP de B **ya** está en la caché de A; *(2)* la IP de B **no** está en la caché de A (elimínela con `arp -d a.b.c.d`).
- **Tarea 1.C (ARP gratuitous).** En M, construya un paquete ARP *gratuitous* (un ARP request especial para actualizar las cachés de los demás) y láncelo en los dos escenarios de 1.B. Sus características: la IP origen y destino son la misma (la del emisor); la MAC destino (en cabecera ARP y Ethernet) es la de difusión (`ff:ff:ff:ff:ff:ff`); no se espera respuesta.

**Listado 2.** Inspeccionar/limpiar la caché ARP de la víctima

```bash
$ arp -n               # ver la caché ARP
$ arp -d 10.9.0.6      # borrar una entrada (para el escenario 2)
```

### Tarea 2 — Ataque MITM sobre Telnet

A y B se comunican por Telnet (cuenta `seed`, contraseña `dees`) y M quiere interceptar y modificar sus datos (Figura 2).

> **Figura 2.** Ataque MITM contra Telnet: M intercepta el paquete de A, cambia su *payload* (S→Z) y lo reenvía a B (adaptado de la Fig. 2 del SEED ARP Cache Poisoning Attack Lab).  
> *(diagrama vectorial; se reproduce en el PDF del manual)*

**Paso 1 (Envenenar ambas cachés).** M envenena las cachés de A y B (la IP del otro queda asociada a la MAC de M); así todo el tráfico A↔B pasa por M. Reenvíe los paquetes falsos de forma **constante** (p. ej. cada 5 s) para que no los reemplacen los reales.

**Listado 3.** Envenenamiento continuo de A y B

```python
import time
from scapy.all import *

def poison(target_ip, target_mac, spoof_ip):
    pkt = Ether(dst=target_mac)/ARP(op=2, pdst=target_ip,
              hwdst=target_mac, psrc=spoof_ip)   # psrc: IP a suplantar
    sendp(pkt, verbose=0)

while True:
    poison('10.9.0.5', 'MAC_de_A', '10.9.0.6')   # a A: B->MAC_M
    poison('10.9.0.6', 'MAC_de_B', '10.9.0.5')   # a B: A->MAC_M
    time.sleep(5)
```

**Paso 2 (Prueba).** Con el reenvío IP de M **apagado** (`sysctl net.ipv4.ip_forward=0`), haga ping entre A y B y observe (Wireshark) qué ocurre.

**Paso 3 (Reenvío IP).** Active el reenvío (`sysctl net.ipv4.ip_forward=1`) y repita; ahora M reenvía los paquetes y A y B se comunican a través de M.

**Paso 4 (Ataque MITM).** Establezca la sesión Telnet de A a B con el reenvío activo; luego **desactívelo** y ejecute el programa de *sniff-and-spoof* para reemplazar cada carácter por `Z`. Ajuste el filtro para no capturar los paquetes generados por el propio programa.

**Listado 4.** Sniff-and-spoof para el MITM (esqueleto)

```python
#!/usr/bin/env python3
from scapy.all import *

IP_A = "10.9.0.5";  MAC_A = "02:42:0a:09:00:05"
IP_B = "10.9.0.6";  MAC_B = "02:42:0a:09:00:06"

def spoof_pkt(pkt):
    if pkt[IP].src == IP_A and pkt[IP].dst == IP_B:
        newpkt = IP(bytes(pkt[IP]))
        del(newpkt.chksum); del(newpkt[TCP].payload); del(newpkt[TCP].chksum)
        if pkt[TCP].payload:
            data = pkt[TCP].payload.load
            newdata = data   # <-- los estudiantes implementan el reemplazo
            send(newpkt/newdata)
        else:
            send(newpkt)
    elif pkt[IP].src == IP_B and pkt[IP].dst == IP_A:
        newpkt = IP(bytes(pkt[IP]))
        del(newpkt.chksum); del(newpkt[TCP].chksum)
        send(newpkt)          # tráfico de B->A: sin cambios

f = 'tcp'
pkt = sniff(iface='eth0', filter=f, prn=spoof_pkt)
```

> [!NOTE]
> **Comportamiento de Telnet**
>
> En Telnet, cada carácter tecleado genera un paquete TCP; el servidor lo hace *eco* de vuelta y el cliente lo muestra. Por eso, si M cambia el carácter a `Z` durante el viaje, el cliente mostrará `Z` aunque no sea lo tecleado.

### Tarea 3 — Ataque MITM sobre Netcat

Repita el ataque, pero ahora A y B se comunican con `netcat` (servidor en B: `nc -lp 9090`; cliente en A: `nc 10.9.0.6 9090`). Cada línea que A escribe viaja a B; reemplace cada aparición de su **nombre** por una secuencia de ``A'' de la **misma longitud** (para no alterar el número de secuencia TCP). Use su nombre real.

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

- **P1.** Compare los tres métodos (ARP request, reply y gratuitous): ¿cuáles funcionan cuando la entrada **ya** existe en la caché y cuáles cuando **no** existe? Justifique con sus resultados (Tareas 1.A–1.C).
- **P2.** Explique por qué funciona el ARP *gratuitous* para envenenar cachés y cuáles son sus tres características distintivas.
- **P3.** ¿Por qué es necesario reenviar los paquetes ARP de forma **continua** durante el MITM?
- **P4.** En el MITM, ¿qué papel juega el reenvío IP (`ip_forward`)? ¿Qué diferencia hay entre dejarlo activo o desactivarlo al ejecutar el sniff-and-spoof?
- **P5.** En el ataque a Netcat, ¿por qué el reemplazo debe conservar la **misma longitud**? ¿Qué pasaría si cambiara?
- **P6.** ¿Por qué el ataque ARP está limitado a la LAN y qué contramedidas existen (p. ej. *Dynamic ARP Inspection*, entradas estáticas)?

## Actividad ABET — SO4: Responsabilidad Ética y Profesional

Esta actividad mide el **Student Outcome 4 (SO4)** de la Carrera de Telecomunicaciones requerido para la acreditación ABET: *habilidad para reconocer las responsabilidades éticas y profesionales en situaciones de ingeniería y emitir juicios fundamentados, considerando el impacto global, económico, medioambiental y social de las soluciones propuestas.* Representa el **30 %** de la valoración total de la práctica y evalúa los indicadores PI 4.1 y PI 4.2 mediante las preguntas SO4-1 y SO4-2.

- **SO4-1.** **[PI 4.1 — 15 %] Ética y responsabilidad profesional ante un ataque MITM por ARP poisoning**
  Un ingeniero de redes detecta tráfico ARP anómalo en la red corporativa que indica un ataque Man-in-the-Middle activo contra la sesión de administración de un servidor crítico. Tiene la capacidad técnica de contraatacar (envenenamiento inverso) pero no está autorizado. Analice:

  - **a)** Las **acciones de contención éticas y legales** (sin contraataque no autorizado).
  - **b)** La **cadena de notificación**: a quién informar, en qué orden y con qué documentación.
  - **c)** El **marco legal ecuatoriano** (COIP Arts. 229 y 234) aplicable tanto al atacante como a un ingeniero que tomara acciones ofensivas sin autorización.
- **SO4-2.** **[PI 4.2 — 15 %] Impacto económico, social y ambiental de un ARP poisoning en una cooperativa de ahorro**
  Un ataque ARP poisoning exitoso en la red de una cooperativa de ahorro y crédito ecuatoriana con 80 000 socios intercepta credenciales de banca en línea durante 4 horas. Analice de manera integral las siguientes dimensiones:

  - **a)** **Económico:** fraudes directos, costos de respuesta al incidente, multas de la Superintendencia de Economía Popular y Solidaria, y daños a la reputación.
  - **b)** **Social:** robo de identidad financiera, erosión de la confianza en las cooperativas, impacto en poblaciones rurales que dependen de estos servicios.
  - **c)** **Ambiental:** consumo energético adicional de la respuesta al incidente y del rediseño de la infraestructura de red (switches gestionados, DAI).
  - **d)** **Contramedidas:** dos técnicas (Dynamic ARP Inspection, cifrado de tráfico TLS) y una política organizacional, citando IEEE 802.1X, ISO/IEC 27033 o NIST SP 800-153.

## Discusión y conclusiones

A partir de los datos recolectados y del análisis realizado, elabore una discusión que responda al menos a las siguientes preguntas guía:

- **DC1.** ¿Se alcanzaron los objetivos planteados? Justifique cada uno con evidencia experimental concreta (capturas, métricas, salidas de comandos).
- **DC2.** ¿Qué limitaciones impone el entorno virtualizado a los resultados? ¿Cómo se trasladarían las observaciones a un escenario real de producción?
- **DC3.** ¿Qué contramedidas o controles de seguridad mitigan el ataque o refuerzan la defensa estudiada? Cite al menos una buena práctica de la industria, una RFC o un estándar (ISO/IEC, IEEE, NIST) pertinente.
- **DC4.** ¿Qué errores se cometieron durante la práctica y qué recomendaciones daría a futuros estudiantes para evitarlos?

Cierre con **conclusiones** (3–5 viñetas) que resuman los hallazgos principales y los vinculen explícitamente con los *Resultados de Aprendizaje* de la asignatura.

## Entregables

1. **Informe técnico** detallado con capturas que describan lo realizado y observado en cada tarea (1–3): la caché ARP antes y después de cada método (1.A–1.C, con ambos escenarios), la evidencia del MITM en Telnet (carácter mostrado como `Z`) y en Netcat (nombre reemplazado). Incluya capturas Wireshark y explique cada fragmento de código (adjuntar sin explicar no recibe puntaje). Bibliografía IEEE (≥3 fuentes).
2. **Código fuente** comentado: el envenenamiento ARP (tres métodos) y el programa de *sniff-and-spoof* del MITM.
3. **Respuestas a la Actividad ABET – SO4** (preguntas SO4-1 y SO4-2), integradas en el informe técnico con extensión de 1–2 páginas por pregunta y las fuentes citadas según norma IEEE.

## Rúbrica de Evaluación

**Tabla 3.** Rúbrica — P-06 (10 puntos)

| Criterio | Peso | Indicador | Descripción |
| --- | --- | --- | --- |
| Envenenamiento ARP | 21 % | Caché modificada | Tarea 1: las tres variantes (request, reply, gratuitous) probadas en ambos escenarios y documentadas con `arp -n`. |
| MITM Telnet | 25 % | Carácter reemplazado | Tarea 2: ambas cachés envenenadas; el carácter tecleado en A se muestra como `Z` en el cliente Telnet. |
| MITM Netcat | 10 % | Nombre reemplazado | Tarea 3: el nombre propio se reemplaza en el flujo Netcat sin romper la conexión. |
| Análisis | 14 % | Preguntas respondidas | Respuestas técnicas con fundamento. |
| **ABET – SO4: Responsabilidad Ética y Profesional (30 %)** |   |   |   |
| PI 4.1 – Ética profesional | 15 % | Respuesta ética fundamentada | Aplica principios éticos y legales al escenario del incidente; la cadena de notificación está justificada. |
| PI 4.2 – Impacto integral | 15 % | Análisis de impacto | Evalúa impacto económico, social y ambiental con contramedidas técnicas y organizacionales, citando al menos un estándar internacional. |

**Tabla 4.** Escala ABET SO4 — P-06

| PI | No cumple<br>(0–59 %) | Cumple parcialmente<br>(60–69 %) | Cumple<br>(70–79 %) | Supera<br>(80–89 %) | Supera ampliamente<br>(90–100 %) |
| --- | --- | --- | --- | --- | --- |
| 4.1 | No aplica principios éticos ni profesionales al evaluar la situación de incidente. | Aplica de manera inconsistente los principios éticos; el análisis legal es superficial o erróneo. | Aplica de manera básica los principios éticos; menciona el marco legal ecuatoriano sin análisis profundo. | Aplica coherentemente su juicio ético y profesional; integra el COIP y la LOPDP con argumentación clara. | Aplica de manera ejemplar e integral su juicio ético; argumenta cada decisión con evidencia y normativas citadas con precisión. |
| 4.2 | No considera ninguno de los tres impactos (económico, social, ambiental). | Considera parcialmente uno o dos de los impactos; las contramedidas no citan estándares. | Considera los tres impactos de forma adecuada; propone contramedidas pertinentes con al menos un estándar citado. | Integra los tres impactos con análisis detallado y contramedidas bien fundamentadas en estándares internacionales. | Realiza una evaluación exhaustiva de los tres impactos; las contramedidas son innovadoras y se respaldan en múltiples estándares. |

## Referencias

1. Plummer, David C., «An Ethernet Address Resolution Protocol». RFC 826, 1982.
2. Du, Wenliang, «Computer & Internet Security: A Hands-on Approach». Independently published, 2019.

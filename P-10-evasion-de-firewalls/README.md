<div align="center">

# P-10 · Evasión de Firewalls

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
| **Unidad** | 700 – Firewalls |
| **Código** | INGE-00107 |
| **Modalidad** | Presencial |
| **Valoración** | 10 puntos |
| **Grupos** | Máx. 3 estudiantes |
| **Entrega** | Según calendario |
| **ABET** | SO4 – Responsabilidad Ética y Profesional (PI 4.1 y PI 4.2) — representa el 30 % de la valoración |

## Marco Teórico

Los fundamentos teóricos sintetizados en esta sección se basan en [1], [2], [3]; se recomienda consultar dichas fuentes para una exposición más profunda. El procedimiento de laboratorio adapta el *Firewall Evasion Lab* de SEED [3].

### Evasión de firewalls mediante tunneling

Hay situaciones en que los firewalls son demasiado restrictivos. Muchas empresas e instituciones aplican *egress filtering*, bloqueando que los usuarios internos alcancen ciertos sitios o servicios (juegos, redes sociales, etc.). La técnica más común para evadir estas restricciones es el **tunneling**, que oculta el verdadero propósito del tráfico encapsulándolo dentro de otra conexión permitida. Esta práctica cubre los siguientes temas:

- **Evasión de firewalls** (firewall evasion).
- **Reenvío de puertos** (port forwarding) estático y dinámico con SSH.
- **Túnel SSH** (SSH tunneling) y proxy SOCKS.
- **VPN** para evadir filtros de entrada y de salida.

La red de laboratorio usa dos segmentos: `10.8.0.0/24` (red externa) y `192.168.20.0/24` (red interna), separados por un router/firewall. El host `10.8.0.1` (la propia VM) actúa como gateway a Internet; el enrutamiento ya está configurado.

> [!NOTE]
> **Nota ética**
>
> Las técnicas de evasión se estudian para comprender sus límites y diseñar mejores defensas. Aplicarlas para violar políticas legítimas de una organización puede constituir una falta o un delito.

**Objetivo general**
Aplicar técnicas de tunneling (reenvío de puertos estático y dinámico, proxy SOCKS y VPN) para evadir, de forma controlada, las reglas de filtrado de entrada y de salida de un firewall, y compararlas.
**Objetivos específicos**

- **OE1.** Comprender la configuración del router (NAT y reglas de ingress/egress) y añadir reglas de bloqueo.
- **OE2.** Crear un túnel de reenvío de puertos **estático** con SSH.
- **OE3.** Crear un túnel de reenvío de puertos **dinámico** (proxy SOCKS) y usarlo desde navegador, `curl` y un cliente Python.
- **OE4.** Construir una **VPN** con SSH para evadir el filtrado de entrada y de salida.
- **OE5.** Comparar el proxy SOCKS5 y la VPN como técnicas de tunneling.

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
| SEED Ubuntu 20.04 VM | Con cliente SSH y Firefox |
| Docker + Docker Compose | Red de dos segmentos (externa/interna) con router |
| OpenSSH | Túneles SSH (`-L`, `-D`, `-R`, `-w`) |
| curl + Python (`socks`) | Pruebas del proxy SOCKS5 |
| iptables | NAT y reglas de firewall en el router |

> [!NOTE]
> **Provisión de materiales**
>
> El estudiante adquiere o instala por su cuenta el equipo personal (laptop), las máquinas virtuales (VirtualBox, SEED VM, Kali Linux, contenedores Docker) y todo el software listado arriba. El laboratorio de la Carrera de Telecomunicaciones provee el espacio físico, el mobiliario y **acceso a Internet supervisado** para la descarga de imágenes, paquetes y consulta de documentación durante la sesión. El laboratorio no entrega equipos de cómputo personales ni licencias de software.

## Entorno de Laboratorio

> **Figura 1.** Topología del laboratorio P-10 (*Network setup*): red externa `10.8.0.0/24` y red interna `192.168.20.0/24` separadas por el router/firewall (adaptado de la Fig. 1 del SEED Firewall Evasion Lab).  
> *(diagrama vectorial; se reproduce en el PDF del manual)*

### Tarea 0 — Configuración del router (NAT y firewall)

El contenedor router ya viene configurado vía `docker-compose.yml`. Conviene conocer su configuración. El **NAT** reescribe la IP origen del tráfico saliente por `eth0` (excepto el destinado a `10.8.0.0/24`); verifique los nombres de interfaz con `ip -br address` (la conectada a `10.8.0.0/24` suele ser `eth0`).

**Listado 1.** NAT y reglas de firewall del router

```bash
# NAT (enmascaramiento de salida por eth0)
iptables -t nat -A POSTROUTING ! -d 10.8.0.0/24 -j MASQUERADE -o eth0

# Filtrado de ENTRADA (ingress): solo permitir SSH
iptables -A FORWARD -i eth0 -p tcp -m conntrack \
         --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A FORWARD -i eth0 -p tcp --dport 22 -j ACCEPT
iptables -A FORWARD -i eth0 -p tcp -j DROP

# Filtrado de SALIDA (egress): bloquear www.example.com
iptables -A FORWARD -i eth1 -d 93.184.216.0/24 -j DROP
```

Las tres primeras reglas `FORWARD` permiten paquetes TCP de conexiones establecidas/relacionadas y nuevas conexiones SSH (puerto 22), y descartan el resto del TCP entrante. La última regla (egress) impide que los hosts internos alcancen `93.184.216.0/24` (`www.example.com`).

**Tarea de laboratorio.** Bloquee **dos sitios web más** añadiendo reglas de egress al router (las usará en tareas posteriores). Recuerde que los sitios populares tienen varias IP que cambian con el tiempo. Inicie los contenedores y verifique que las reglas de entrada y salida funcionan como se espera.

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

### Tarea 1 — Reenvío de puertos estático

El firewall impide que máquinas externas se conecten a cualquier servidor TCP de la red interna, salvo el servidor SSH. Para evadir esta restricción se usa el **reenvío de puertos estático**: con `ssh` se crea un túnel entre el host A (red externa) y el host B (red interna), de modo que los datos recibidos en el puerto X de A se envían a B y, desde allí, al destino T en su puerto Y.

**Listado 2.** Reenvío de puertos estático con SSH

```bash
$ ssh -4NT -L <IP_A>:<puerto_X>:<IP_T>:<puerto_Y>  <usuario>@<IP_B>
# -4: solo IPv4   -N: no ejecutar comando remoto   -T: sin pseudo-terminal
```

Para la IP de A se suele usar `0.0.0.0` (escucha en todas las interfaces); use `127.0.0.1` (o omita la IP) para limitar el túnel a la interfaz de *loopback*.

**Tarea de laboratorio.** Use reenvío estático para crear un túnel entre la red externa y la interna y haga `telnet` al servidor en `B1` desde `A`, `A1` y `A2`. Responda: (1) ¿cuántas conexiones TCP intervienen en todo el proceso? (capture con Wireshark/`tcpdump` e identifíquelas); (2) ¿por qué este túnel evade la regla del firewall?

### Tarea 2 — Reenvío de puertos dinámico (proxy SOCKS)

El reenvío estático envía los datos a un destino fijo. Para alcanzar *múltiples* destinos sin crear un túnel por cada uno se usa el **reenvío dinámico**, que convierte un extremo del túnel en un **proxy SOCKS**.

#### Tarea 2.1 — Establecer el reenvío dinámico

**Listado 3.** Reenvío dinámico y prueba con curl

```bash
# En B (que actúa como proxy); A es el otro extremo del túnel
$ ssh -4NT -D <IP_B>:<puerto_X>  <usuario>@<IP_A>

# Probar con curl usando proxy SOCKS5 (socks5h resuelve el DNS en el proxy)
$ curl --proxy socks5h://<IP_B>:<puerto_X>  <URL_bloqueada>
```

**Tarea de laboratorio.** Demuestre que puede visitar los sitios bloqueados con `curl` desde `B`, `B1` y `B2`. Responda: (1) ¿qué máquina establece la conexión real con el servidor web? (2) ¿cómo sabe esa máquina a qué servidor conectarse?

#### Tarea 2.2 — Probar el túnel con el navegador

Como la VM anfitriona está conectada a la red interna (`192.168.20.1`), puede usar Firefox para probar el túnel. Configure el proxy SOCKS en `about:preferences` → *Network Settings* → *Settings* (Figura 2).

> **Figura 2.** Configuración del proxy SOCKS v5 en Firefox: método *Manual proxy configuration*, host y puerto del proxy SOCKS (adaptado de la Fig. 2 del SEED Firewall Evasion Lab).  
> *(diagrama vectorial; se reproduce en el PDF del manual)*

**Tarea de laboratorio.** Con el proxy configurado, navegue a cualquier sitio bloqueado. (1) Ejecute `tcpdump` en el router e identifique el tráfico del reenvío de puertos. (2) Rompa el túnel SSH e intente navegar; describa lo observado. *Limpieza:* al terminar, quite el proxy en Firefox (*No proxy*).

#### Tarea 2.3 — Cliente SOCKS en Python

En el reenvío dinámico el destino final no se fija al crear el túnel; la aplicación debe indicárselo al proxy mediante el protocolo **SOCKS**. Firefox y `curl` lo soportan de forma nativa; `telnet` no. Implemente un cliente SOCKS simple en Python:

**Listado 4.** Cliente SOCKS5 en Python

```python
#!/usr/bin/env python3
import socks

s = socks.socksocket()
s.set_proxy(socks.SOCKS5, "<IP del proxy>", <puerto del proxy>)
s.connect(("<IP o hostname del servidor>", <puerto del servidor>))

hostname = "www.example.com"
req = b"GET / HTTP/1.0\r\nHost: " + hostname.encode('utf-8') + b"\r\n\r\n"
s.sendall(req)
response = s.recv(2048)
while response:
    print(response.split(b"\r\n"))
    response = s.recv(2048)
```

**Tarea de laboratorio.** Complete el programa y úselo para acceder a `http://www.example.com` desde `B`, `B1` y `B2` (solo HTTP; HTTPS exige el *handshake* TLS).

### Tarea 3 — Red privada virtual (VPN)

La VPN también permite evadir el firewall. En lugar de OpenVPN se usa la *VPN del pobre*: SSH. El servidor SSH ya tiene habilitado `PermitRootLogin yes` y `PermitTunnel yes` en `/etc/ssh/sshd_config`. La opción `-w 0:0` crea una interfaz `tun0` en cliente y servidor y las une por una conexión TCP cifrada.

#### Tarea 3.1 — Evadir el firewall de entrada

**Listado 5.** Crear y configurar el túnel VPN (SSH)

```bash
# ssh -w 0:0 root@<IP_servidor_VPN> \
      -o "PermitLocalCommand=yes" \
      -o "LocalCommand= ip addr add 192.168.53.88/24 dev tun0 && \
                        ip link set tun0 up" \
      -o "RemoteCommand=ip addr add 192.168.53.99/24 dev tun0 && \
                        ip link set tun0 up"
# root@<IP_servidor_VPN> password: dees
```

**Tarea de laboratorio.** Cree una VPN entre `A` y `B`, con `B` como servidor VPN. Tras la configuración, demuestre que puede hacer `telnet` a `B`, `B1` y `B2` desde la red externa. Capture la traza y explique por qué los paquetes no son bloqueados por el firewall.

#### Tarea 3.2 — Evadir el firewall de salida

Para evadir el filtrado de salida (sitios bloqueados), se usa la VPN como en Tarea 2, pero con tunneling completo. Aquí `B` es el cliente VPN y `A` el servidor VPN. El problema: los paquetes que salen por el túnel tienen IP origen `192.168.53.88`; al pasar por el NAT de VirtualBox y volver, la red `192.168.53.0/24` es desconocida y la respuesta se descarta. La solución es montar un **NAT en el servidor VPN** (A) para que el origen se reescriba con su IP (`10.8.0.99`):

**Listado 6.** NAT en el servidor VPN

```bash
# iptables -t nat -A POSTROUTING -j MASQUERADE -o eth0
```

**Tarea de laboratorio.** Cree la VPN entre `B` y `A` (con `A` como servidor VPN) y demuestre que desde `B`, `B1` y `B2` se alcanzan los sitios bloqueados. Capture la traza y explique por qué el firewall ya no los bloquea.

### Tarea 4 — Comparación entre proxy SOCKS5 y VPN

Tanto el proxy SOCKS5 (reenvío dinámico) como la VPN se usan para crear túneles que evaden firewalls y protegen las comunicaciones; muchos proveedores de ``VPN'' en realidad ofrecen solo un proxy SOCKS5. A partir de su experiencia en esta práctica, compare ambas tecnologías: en qué capa operan, qué tráfico tunelizan (por aplicación vs. todo el sistema), rendimiento, facilidad de configuración, y ventajas y desventajas de cada una.

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

- **P1.** Explique la diferencia entre reenvío de puertos **estático** (`-L`) y **dinámico** (`-D`). ¿Cuándo conviene cada uno?
- **P2.** En la Tarea 1, ¿cuántas conexiones TCP intervienen en el reenvío estático y por qué la regla del firewall no las bloquea?
- **P3.** ¿Qué es el protocolo SOCKS y por qué el reenvío dinámico lo necesita? ¿Por qué `telnet` no puede usar un proxy SOCKS directamente, pero sí `curl` o Firefox?
- **P4.** ¿Qué diferencia hay entre `socks5` y `socks5h` en `curl` respecto a la resolución DNS?
- **P5.** En la Tarea 3.2, ¿por qué fue necesario configurar un NAT en el servidor VPN? ¿Qué pasaría con los paquetes de retorno sin él?
- **P6.** Compare el proxy SOCKS5 y la VPN como técnicas de tunneling: capa de operación, alcance del tráfico tunelizado y casos de uso.
- **P7.** ¿Cómo puede un firewall de inspección profunda (DPI) detectar tráfico tunelizado, y qué políticas organizacionales reducen el riesgo de evasión?

## Actividad ABET — SO4: Responsabilidad Ética y Profesional

Esta actividad mide el **Student Outcome 4 (SO4)** de la Carrera de Telecomunicaciones requerido para la acreditación ABET: *habilidad para reconocer las responsabilidades éticas y profesionales en situaciones de ingeniería y emitir juicios fundamentados, considerando el impacto global, económico, medioambiental y social de las soluciones propuestas.* Representa el **30 %** de la valoración total de la práctica y evalúa los indicadores PI 4.1 y PI 4.2 mediante las preguntas SO4-1 y SO4-2.

- **SO4-1.** **[PI 4.1 — 15 %] Ética y responsabilidad profesional ante una solicitud de omisión en un informe de pentest**
  Un consultor de seguridad descubre durante un pentest autorizado que puede evadir el firewall del cliente mediante tunelización DNS. Al presentar el hallazgo, el cliente (gerente de TI) pide que NO se incluya en el informe final para ``no alarmar a la junta directiva antes de la auditoría ABET''. Analice:

  - **a)** Las responsabilidades éticas del consultor ante esta solicitud de omisión.
  - **b)** Los principios de honestidad e integridad profesional aplicables y por qué la omisión podría considerarse negligencia o complicidad.
  - **c)** Las consecuencias legales (responsabilidad civil, LOPDP, COIP) si un tercero explotara la vulnerabilidad omitida y causara daños, y si se demostrara que el consultor la conocía.
- **SO4-2.** **[PI 4.2 — 15 %] Impacto integral de la evasión de firewall mediante tunelización**
  Un atacante usa tunelización DNS e ICMP para evadir el firewall de una empresa tecnológica ecuatoriana y exfiltrar propiedad intelectual (código fuente, algoritmos propietarios) durante 6 meses sin detección. Analice:

  - **a)** **Económico:** pérdida de ventaja competitiva, costos de litigios por propiedad intelectual, pérdida de contratos y daño a la reputación de la empresa.
  - **b)** **Social:** pérdida de empleos si la empresa pierde competitividad, impacto en la confianza del ecosistema tecnológico ecuatoriano para la inversión extranjera.
  - **c)** **Ambiental:** consumo energético de los sistemas de monitoreo y de la respuesta al incidente.
  - **d)** **Contramedidas:** dos técnicas (DPI/Deep Packet Inspection, DNS Firewall/RPZ) y una política organizacional, citando NIST SP 800-94r1, RFC 5358 o ISO/IEC 27001.

## Discusión y conclusiones

A partir de los datos recolectados y del análisis realizado, elabore una discusión que responda al menos a las siguientes preguntas guía:

- **DC1.** ¿Se alcanzaron los objetivos planteados? Justifique cada uno con evidencia experimental concreta (capturas, métricas, salidas de comandos).
- **DC2.** ¿Qué limitaciones impone el entorno virtualizado a los resultados? ¿Cómo se trasladarían las observaciones a un escenario real de producción?
- **DC3.** ¿Qué contramedidas o controles de seguridad mitigan el ataque o refuerzan la defensa estudiada? Cite al menos una buena práctica de la industria, una RFC o un estándar (ISO/IEC, IEEE, NIST) pertinente.
- **DC4.** ¿Qué errores se cometieron durante la práctica y qué recomendaciones daría a futuros estudiantes para evitarlos?

Cierre con **conclusiones** (3–5 viñetas) que resuman los hallazgos principales y los vinculen explícitamente con los *Resultados de Aprendizaje* de la asignatura.

## Entregables

1. **Informe técnico** detallado con capturas que describan lo realizado y observado en cada tarea (0–4): reglas de firewall añadidas, comandos SSH de reenvío estático/dinámico/VPN, capturas Wireshark/`tcpdump` que identifiquen las conexiones del túnel, y la evidencia de acceso a los servicios/sitios bloqueados. Explique cada comando (adjuntar sin explicar no recibe puntaje). Bibliografía IEEE (≥3 fuentes).
2. **Código y configuración**: el cliente SOCKS5 en Python completado y los comandos/reglas de la VPN (Tareas 3.1 y 3.2).
3. **Respuestas a la Actividad ABET – SO4** (preguntas SO4-1 y SO4-2), integradas en el informe técnico con extensión de 1–2 páginas por pregunta y las fuentes citadas según norma IEEE.

## Rúbrica de Evaluación

**Tabla 3.** Rúbrica — P-10 (10 puntos)

| Criterio | Peso | Indicador | Descripción |
| --- | --- | --- | --- |
| Setup y firewall (T0) | 7 % | Reglas añadidas | Router operativo; se bloquean dos sitios adicionales y se verifican las reglas de ingress/egress. |
| Reenvío estático (T1) | 14 % | Telnet via túnel | `telnet` a `B1` desde A/A1/A2 vía túnel SSH; conexiones TCP identificadas. |
| Reenvío dinámico (T2) | 21 % | Proxy SOCKS5 | Sitios bloqueados accesibles con `curl`, navegador y cliente Python SOCKS. |
| VPN (T3) | 18 % | Ingress y egress | Túnel VPN evade el filtrado de entrada y de salida (con NAT en el servidor VPN). |
| Comparación y análisis | 10 % | Preguntas respondidas | Comparación SOCKS5 vs. VPN y respuestas con fundamento técnico. |
| **ABET – SO4: Responsabilidad Ética y Profesional (30 %)** |   |   |   |
| PI 4.1 – Ética profesional | 15 % | Respuesta ética fundamentada | Aplica principios éticos y legales al escenario del incidente; la cadena de notificación está justificada. |
| PI 4.2 – Impacto integral | 15 % | Análisis de impacto | Evalúa impacto económico, social y ambiental con contramedidas técnicas y organizacionales, citando al menos un estándar internacional. |

**Tabla 4.** Escala ABET SO4 — P-10

| PI | No cumple<br>(0–59 %) | Cumple parcialmente<br>(60–69 %) | Cumple<br>(70–79 %) | Supera<br>(80–89 %) | Supera ampliamente<br>(90–100 %) |
| --- | --- | --- | --- | --- | --- |
| 4.1 | No aplica principios éticos ni profesionales al evaluar la situación de incidente. | Aplica de manera inconsistente los principios éticos; el análisis legal es superficial o erróneo. | Aplica de manera básica los principios éticos; menciona el marco legal ecuatoriano sin análisis profundo. | Aplica coherentemente su juicio ético y profesional; integra el COIP y la LOPDP con argumentación clara. | Aplica de manera ejemplar e integral su juicio ético; argumenta cada decisión con evidencia y normativas citadas con precisión. |
| 4.2 | No considera ninguno de los tres impactos (económico, social, ambiental). | Considera parcialmente uno o dos de los impactos; las contramedidas no citan estándares. | Considera los tres impactos de forma adecuada; propone contramedidas pertinentes con al menos un estándar citado. | Integra los tres impactos con análisis detallado y contramedidas bien fundamentadas en estándares internacionales. | Realiza una evaluación exhaustiva de los tres impactos; las contramedidas son innovadoras y se respaldan en múltiples estándares. |

## Referencias

1. Cheswick, William and Bellovin, Steven and Rubin, Aviel, «Firewalls and Internet Security: Repelling the Wily Hacker». Addison-Wesley, 2003.
2. Kizza, Joseph Migga, «Guide to Computer Network Security». Springer, 2017.
3. Du, Wenliang, «Computer & Internet Security: A Hands-on Approach». Independently published, 2019.

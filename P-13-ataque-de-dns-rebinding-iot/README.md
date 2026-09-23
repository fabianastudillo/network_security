<div align="center">

# P-13 · Ataque de DNS Rebinding (IoT)

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
| **Unidad** | 800 – Sistema DNS y ataques |
| **Código** | INGE-00107 |
| **Modalidad** | Presencial |
| **Valoración** | 10 puntos |
| **Grupos** | Máx. 3 estudiantes |
| **Entrega** | Según calendario |
| **ABET** | SO4 – Responsabilidad Ética y Profesional (PI 4.1 y PI 4.2) — representa el 30 % de la valoración |

## Marco Teórico

Los fundamentos teóricos sintetizados en esta sección se basan en [1]; se recomienda consultar dicha fuente para una exposición más profunda. El procedimiento de laboratorio adapta el *DNS Rebinding Attack Lab* de SEED [1].

### Política del mismo origen (SOP) y su evasión

La **Política del Mismo Origen** (Same-Origin Policy, SOP) impide que el código JavaScript de una página interactúe con un servidor de *origen* distinto. La SOP se basa en el **nombre de host** (no en la dirección IP): si el código se sirve desde `www.attacker32.com`, solo puede comunicarse con `www.attacker32.com`, pero *nada* restringe a qué IP resuelve ese nombre. El **DNS rebinding** explota precisamente esto: el atacante, que controla el servidor de nombres de su dominio, cambia la asociación nombre→IP de `www.attacker32.com` para *reapuntarla* a la IP del dispositivo víctima, sin violar la SOP.

### Ataque a dispositivos IoT detrás de un firewall

Muchos dispositivos **IoT** exponen una interfaz web sin autenticación fuerte y están protegidos por un firewall: no son accesibles desde el exterior. Sin embargo, cuando un usuario de la red interna visita el sitio del atacante, el código JavaScript del atacante se ejecuta *dentro* del navegador del usuario y, por tanto, dentro de la red interna. La SOP impide que ese código hable directamente con el IoT; el DNS rebinding sortea esa protección para que el código del atacante pueda leer información del IoT y controlarlo (en esta práctica, fijar la temperatura de un termostato a un valor peligroso).

### El dispositivo IoT simulado

El IoT es un termostato con un servidor web que expone dos APIs: `password` (devuelve la contraseña actual) y `temperature` (fija la temperatura, requiere la contraseña). La contraseña **no** autentica: protege contra *CSRF*. Por eso un simple ataque CSRF no basta y se necesita el DNS rebinding: el código debe *leer* la respuesta de la API (la contraseña), lo que la SOP normalmente prohíbe.

> [!NOTE]
> El ataque se realiza contra un IoT simulado en un entorno aislado. Dirigirlo contra dispositivos o redes reales es ilegal.

**Objetivo general**
Demostrar el ataque de DNS rebinding para evadir la Política del Mismo Origen y controlar un dispositivo IoT (termostato) situado tras un firewall, fijando su temperatura a un valor peligroso.
**Objetivos específicos**

- **OE1.** Levantar el entorno (red interna con IoT y red externa con el atacante) y configurar la VM del usuario.
- **OE2.** Comprobar experimentalmente la protección de la SOP en el navegador.
- **OE3.** Evadir la SOP modificando el código JavaScript del atacante.
- **OE4.** Ejecutar el *DNS rebinding* reescribiendo la zona del atacante para reapuntar el nombre a la IP del IoT.
- **OE5.** Automatizar el ataque para fijar la temperatura sin intervención del usuario.

## Actividades previas

Antes de la sesión de laboratorio, cada estudiante debe completar las siguientes actividades preparatorias:

- **AP1.** Repasar el funcionamiento del DNS y la Política del Mismo Origen, y las referencias citadas.
- **AP2.** Verificar que el entorno virtual (VM SEED y contenedores Docker) esté operativo conforme al capítulo *Configuración del Entorno*.
- **AP3.** Tomar una *snapshot* del estado inicial de cada VM involucrada en la práctica para poder revertir cambios.
- **AP4.** Revisar la Sección [Seguridad y normas generales del laboratorio](../README.md#seguridad-y-normas-generales-del-laboratorio) (Seguridad y normas generales del laboratorio).
- **AP5.** Preparar la bitácora digital para registrar comandos, capturas y observaciones durante la sesión.

## Materiales y Equipos

| Recurso | Descripción |
| --- | --- |
| SEED Ubuntu 20.04 VM | VM del usuario (víctima) con Firefox |
| SEED `Labsetup.zip` | Topología y `docker-compose.yml` del DNS Rebinding Lab |
| Docker + Docker Compose | Contenedores: IoT, router/firewall, DNS local, NS y web del atacante |
| BIND 9 (`rndc`, `dig`) | Servidor de nombres del atacante y consultas |
| Firefox + JavaScript | Navegador de la víctima y código del atacante |

> [!NOTE]
> **Provisión de materiales**
>
> El estudiante adquiere o instala por su cuenta el equipo personal (laptop), las máquinas virtuales (VirtualBox, SEED VM, Kali Linux, contenedores Docker) y todo el software listado arriba. El laboratorio de la Carrera de Telecomunicaciones provee el espacio físico, el mobiliario y **acceso a Internet supervisado** para la descarga de imágenes, paquetes y consulta de documentación durante la sesión. El laboratorio no entrega equipos de cómputo personales ni licencias de software.

## Entorno de Laboratorio

Se usan seis máquinas en dos redes (Figura 1): una **red interna** (hogar, `192.168.60.0/24`) con la VM del usuario y el servidor IoT, protegida por el router/firewall (que bloquea todo el tráfico externo hacia `192.168.60.80`); y una **red externa** (`10.9.0.0/24`) con el servidor DNS local y los contenedores del atacante (servidor de nombres y servidor web del dominio `attacker32.com`).

> **Figura 1.** Topología del laboratorio P-13 (*Lab environment setup*): red interna con el IoT protegido por el firewall y red externa con el atacante (adaptado de la Fig. 1 del SEED DNS Rebinding Lab).  
> *(diagrama vectorial; se reproduce en el PDF del manual)*

## Consideraciones de seguridad

Antes de iniciar el procedimiento, revise la Sección [Seguridad y normas generales del laboratorio](../README.md#seguridad-y-normas-generales-del-laboratorio) (Seguridad y normas generales del laboratorio). Para esta práctica se destacan los siguientes riesgos y precauciones específicas:

- **Aislamiento de red obligatorio**: el ataque debe ejecutarse solo contra el IoT simulado del laboratorio. Está prohibido dirigirlo contra dispositivos, dominios o redes reales.
- **Snapshots y reversibilidad**: tome una instantánea antes de modificar `/etc/hosts`, `/etc/resolv.conf`, la configuración de Firefox o las zonas de BIND.
- **Marco legal**: el acceso no autorizado a dispositivos ajenos y la manipulación de DNS pueden tipificarse como delito informático (COIP Arts. 229 y 234; LOPDP). Véase el warningbox de la Sección [Seguridad y normas generales del laboratorio](../README.md#seguridad-y-normas-generales-del-laboratorio).
- **Riesgos eléctricos y ergonomía**: aplique las pausas activas y verificaciones de las Secciones *Riesgos eléctricos* y *Ergonomía* dentro de Sección [Seguridad y normas generales del laboratorio](../README.md#seguridad-y-normas-generales-del-laboratorio).

> [!WARNING]
> **Riesgos específicos de la práctica**
>
> El ataque fija el termostato a un valor peligroso. En un dispositivo real esto podría causar daños físicos. Realícelo únicamente sobre el IoT simulado y documente las medidas de contención en la bitácora.

## Procedimiento

### Configuración del entorno

Levante la topología con `docker-compose` (alias `dcbuild`, `dcup`, `dockps`, `docksh`) y configure la VM del usuario con los siguientes pasos.

- **Paso 0 — Desactivar DNS over HTTPS.** En Firefox: `Settings` → `Privacy & Security` → `DNS over HTTPS` → `off` (de lo contrario la resolución no pasa por el DNS local).
- **Paso 1 — Reducir la caché DNS de Firefox.** En `about:config`, fije `network.dnsCacheExpiration` a `10` (por defecto 60); reinicie Firefox.
- **Paso 2 — Editar `/etc/hosts`.** Añada el nombre del IoT y elimine cualquier entrada previa de `attacker32.com`.
- **Paso 3 — DNS local.** Fije `10.9.0.53` como resolvedor.

**Listado 1.** Configuración de la VM del usuario

```bash
# /etc/hosts: nombre del servidor IoT
192.168.60.80  www.seedIoT32.com

# DNS local (resolv.conf.d/head) y aplicar
nameserver 10.9.0.53
$ sudo resolvconf -u
```

### Prueba del entorno

Verifique la resolución y el acceso al IoT y al sitio del atacante:

**Listado 2.** Pruebas de la configuración

```bash
$ dig www.attacker32.com      # debe dar 10.9.0.180 (web del atacante)
$ dig ns.attacker32.com       # debe dar 10.9.0.153 (NS del atacante)
# En el navegador del usuario:
#   http://www.seedIoT32.com    -> termostato
#   http://www.attacker32.com   -> sitio del atacante
```

### Tarea 1 — Comprender la protección de la SOP

En la VM del usuario, abra en ventanas separadas las tres URLs. La primera muestra la temperatura actual del termostato; la segunda y la tercera son *idénticas* (un botón que fija la temperatura a 99 C) pero una proviene del IoT y la otra del atacante (Figura 2).

**Listado 3.** Las tres URLs del experimento

```bash
URL 1:  http://www.seedIoT32.com
URL 2:  http://www.seedIoT32.com/change
URL 3:  http://www.attacker32.com/change
```

> **Figura 2.** Las páginas web del experimento: (a) el termostato del IoT y (b) la página del botón que fija la temperatura (adaptado de la Fig. 2 del SEED DNS Rebinding Lab).  
> *(diagrama vectorial; se reproduce en el PDF del manual)*

Pulse el botón en la segunda y la tercera página y describa qué ocurre: ¿cuál *sí* fija la temperatura y cuál no? Revise la consola web (`Web Developer` → `Web Console`) y explique por qué la SOP hace fallar a la página del atacante.

### Tarea 2 — Evadir la protección de la SOP

Como la SOP se basa en el *nombre de host*, mientras la URL siga siendo `www.attacker32.com` se cumple la política, aunque ese nombre se reapunte a otra IP. El ataque tiene dos pasos.

**Paso 1 — Modificar el JavaScript.** En el servidor web del atacante, edite `change.js` para que las peticiones se dirijan al *mismo* origen (`www.attacker32.com`) y reinicie el contenedor:

**Listado 4.** Apuntar el código al mismo origen

```bash
// /app/rebind_server/templates/js/change.js
let url_prefix = 'http://www.attacker32.com'

$ docker container restart <id-de-attacker-www>
```

**Paso 2 — DNS rebinding.** Reescriba la zona del atacante para que `www.attacker32.com` resuelva a la IP del IoT (`192.168.60.80`); así la petición del botón llegará al IoT cumpliendo la SOP. Use un TTL corto para que la caché expire pronto.

**Listado 5.** Zona del atacante (zone_attacker32.com)

```
$TTL 1000
@   IN  SOA  ns.attacker32.com. admin.attacker32.com. (
              2008111001 8H 2H 4W 1D )
@   IN  NS   ns.attacker32.com.
@   IN  A    10.9.0.22
www IN  A    10.9.0.22     <-- reapuntar a 192.168.60.80 para el rebinding
ns  IN  A    10.9.0.21
*   IN  A    10.9.0.22
```

**Listado 6.** Recargar la zona y limpiar la caché

```bash
# rndc reload attacker32.com      # en el NS del atacante
# rndc flush                       # en el DNS local (antes de atacar)
```

Si ambos pasos están correctos, pulsar el botón de la página `change` de `www.attacker32.com` fijará la temperatura del termostato. Aporte evidencia del éxito.

### Tarea 3 — Automatizar el ataque

Es poco realista que el usuario pulse el botón. Cargue la página automatizada del atacante, que muestra un temporizador de 10 a 0; al llegar a 0, su JavaScript envía la petición de temperatura y reinicia el contador. Usando DNS rebinding, debe fijar el termostato a 88 C sin intervención del usuario.

**Listado 7.** Página automatizada del ataque

```bash
http://www.attacker32.com
```

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
| Error SOP en consola (Tarea 1) |   |   |
| Temperatura fijada (Tarea 2) |   |   |
| Temperatura fijada automáticamente (Tarea 3) |   |   |

**Pautas para el análisis de los datos recolectados:**

- Contraste los resultados observados con el comportamiento esperado según el marco teórico; explique las diferencias.
- Relacione el TTL de la zona y la caché del navegador/DNS con el tiempo que tarda en surtir efecto el *rebinding*.
- Documente con capturas el cambio de la asociación nombre→IP antes y después del ataque.

## Preguntas de Análisis

- **P1.** ¿En qué se basa la Política del Mismo Origen y por qué el hecho de que use el nombre de host (no la IP) habilita el DNS rebinding?
- **P2.** En la Tarea 1, ¿por qué la página servida desde `attacker32.com` no puede fijar la temperatura, pero la servida desde `seedIoT32.com` sí? Apóyese en el mensaje de la consola web.
- **P3.** Explique el rol del **TTL** de la zona y de la caché DNS del navegador en el éxito y la velocidad del ataque. ¿Por qué se reduce `network.dnsCacheExpiration`?
- **P4.** ¿Por qué el firewall no impide este ataque, si bloquea el acceso externo al IoT?
- **P5.** En este IoT, la contraseña protege contra CSRF pero no autentica. ¿Por qué un ataque CSRF simple no basta y sí se necesita el DNS rebinding?
- **P6.** Proponga al menos dos contramedidas contra el DNS rebinding (p. ej. *DNS pinning*, validación del encabezado `Host`, filtrado de IP privadas en respuestas DNS).

## Actividad ABET — SO4: Responsabilidad Ética y Profesional

Esta actividad mide el **Student Outcome 4 (SO4)** de la Carrera de Telecomunicaciones requerido para la acreditación ABET: *habilidad para reconocer las responsabilidades éticas y profesionales en situaciones de ingeniería y emitir juicios fundamentados, considerando el impacto global, económico, medioambiental y social de las soluciones propuestas.* Representa el **30 %** de la valoración total de la práctica y evalúa los indicadores PI 4.1 y PI 4.2 mediante las preguntas SO4-1 y SO4-2.

- **SO4-1.** **[PI 4.1 — 15 %] Ética y responsabilidad profesional ante una vulnerabilidad de DNS rebinding sin respuesta del fabricante**
  Un investigador de seguridad descubre una vulnerabilidad de DNS rebinding que afecta a millones de routers domésticos de una marca popular presente en el mercado ecuatoriano. El fabricante no responde a la notificación inicial en 30 días y no hay un canal oficial de reporte de vulnerabilidades (Bug Bounty). Evalúe:

  - **a)** Las opciones de divulgación responsable: vías alternativas al fabricante (CERT nacional, ARCOTEL, prensa técnica) cuando el canal directo falla.
  - **b)** Los principios éticos de protección al usuario final (millones de hogares en riesgo) frente a la responsabilidad de no publicar un exploit activo.
  - **c)** El marco legal ecuatoriano aplicable: COIP, LOPDP y las responsabilidades del fabricante ante una vulnerabilidad de seguridad conocida y no parchada.
- **SO4-2.** **[PI 4.2 — 15 %] Impacto integral de un ataque masivo de DNS rebinding en dispositivos IoT domésticos**
  Un ataque de DNS rebinding masivo compromete 100 000 dispositivos IoT domésticos (cámaras de seguridad, routers, asistentes de voz) en Ecuador, permitiendo al atacante acceder a redes privadas hogareñas durante 2 semanas. Analice:

  - **a)** **Económico:** costos de reemplazo o actualización de dispositivos afectados, pérdidas por vigilancia no autorizada de hogares (para robo físico), litigios contra fabricantes.
  - **b)** **Social:** violación masiva de la privacidad del hogar, riesgo de vigilancia de menores, erosión de la confianza en los dispositivos IoT de consumo.
  - **c)** **Ambiental:** impacto ambiental del reemplazo masivo de dispositivos IoT (residuos electrónicos, e-waste) y del consumo energético del botnet IoT generado.
  - **d)** **Contramedidas:** dos técnicas (DNS rebinding protection en resolvedores, TTL mínimo configurado) y una política organizacional, citando RFC 8910, NIST SP 800-213 o OWASP IoT Project.

## Discusión y conclusiones

A partir de los datos recolectados y del análisis realizado, elabore una discusión que responda al menos a las siguientes preguntas guía:

- **DC1.** ¿Se alcanzaron los objetivos planteados? Justifique cada uno con evidencia experimental concreta (capturas, métricas, salidas de comandos).
- **DC2.** ¿Qué limitaciones impone el entorno virtualizado a los resultados? ¿Cómo se trasladarían las observaciones a un escenario real de producción?
- **DC3.** ¿Qué contramedidas o controles de seguridad mitigan el ataque o refuerzan la defensa estudiada? Cite al menos una buena práctica de la industria, una RFC o un estándar (ISO/IEC, IEEE, NIST) pertinente.
- **DC4.** ¿Qué errores se cometieron durante la práctica y qué recomendaciones daría a futuros estudiantes para evitarlos?

Cierre con **conclusiones** (3–5 viñetas) que resuman los hallazgos principales y los vinculen explícitamente con los *Resultados de Aprendizaje* de la asignatura.

## Entregables

1. **Informe técnico** detallado con capturas que describan lo realizado y observado en cada tarea (1–3): pantallas del termostato, mensaje de la consola web (SOP), zona modificada, salidas de `dig` antes/después del rebinding y evidencia del cambio de temperatura (manual y automático). Explique cada fragmento de código/configuración (adjuntar sin explicar no recibe puntaje). Bibliografía IEEE (≥3 fuentes).
2. **Archivos modificados**: `change.js` y la zona `zone_attacker32.com`.
3. **Respuestas a la Actividad ABET – SO4** (preguntas SO4-1 y SO4-2), integradas en el informe técnico con extensión de 1–2 páginas por pregunta y las fuentes citadas según norma IEEE.

## Rúbrica de Evaluación

**Tabla 3.** Rúbrica — P-13 (10 puntos)

| Criterio | Peso | Indicador | Descripción |
| --- | --- | --- | --- |
| Entorno y pruebas | 11 % | Configuración correcta | VM del usuario y contenedores operativos; `dig` y navegador confirman el acceso al IoT y al atacante. |
| Comprensión de la SOP | 14 % | Experimento Tarea 1 | Demuestra y explica con la consola web por qué la SOP bloquea la página del atacante. |
| Evasión de la SOP | 21 % | Rebinding manual | Tarea 2: `change.js` y zona modificados; el botón fija la temperatura vía rebinding (evidencia). |
| Ataque automatizado | 14 % | Temperatura fijada | Tarea 3: el termostato se fija a 88 C sin intervención del usuario. |
| Análisis | 10 % | Preguntas respondidas | Respuestas con fundamento técnico (TTL, contramedidas). |
| **ABET – SO4: Responsabilidad Ética y Profesional (30 %)** |   |   |   |
| PI 4.1 – Ética profesional | 15 % | Respuesta ética fundamentada | Aplica principios éticos y legales al escenario del incidente; la cadena de notificación está justificada. |
| PI 4.2 – Impacto integral | 15 % | Análisis de impacto | Evalúa impacto económico, social y ambiental con contramedidas técnicas y organizacionales, citando al menos un estándar internacional. |

**Tabla 4.** Escala ABET SO4 — P-13

| PI | No cumple<br>(0–59 %) | Cumple parcialmente<br>(60–69 %) | Cumple<br>(70–79 %) | Supera<br>(80–89 %) | Supera ampliamente<br>(90–100 %) |
| --- | --- | --- | --- | --- | --- |
| 4.1 | No aplica principios éticos ni profesionales al evaluar la situación de incidente. | Aplica de manera inconsistente los principios éticos; el análisis legal es superficial o erróneo. | Aplica de manera básica los principios éticos; menciona el marco legal ecuatoriano sin análisis profundo. | Aplica coherentemente su juicio ético y profesional; integra el COIP y la LOPDP con argumentación clara. | Aplica de manera ejemplar e integral su juicio ético; argumenta cada decisión con evidencia y normativas citadas con precisión. |
| 4.2 | No considera ninguno de los tres impactos (económico, social, ambiental). | Considera parcialmente uno o dos de los impactos; las contramedidas no citan estándares. | Considera los tres impactos de forma adecuada; propone contramedidas pertinentes con al menos un estándar citado. | Integra los tres impactos con análisis detallado y contramedidas bien fundamentadas en estándares internacionales. | Realiza una evaluación exhaustiva de los tres impactos; las contramedidas son innovadoras y se respaldan en múltiples estándares. |

## Referencias

1. Du, Wenliang, «Computer & Internet Security: A Hands-on Approach». Independently published, 2019.

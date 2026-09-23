# P-14 · Infraestructura DNS

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

Los fundamentos teóricos sintetizados en esta sección se basan en [1]; se recomienda consultar dicha fuente para una exposición más profunda. El procedimiento de laboratorio adapta el *DNS Infrastructure Lab* de SEED [1].

### La infraestructura del DNS

El **DNS** (Domain Name System) traduce nombres de host a direcciones IP (y viceversa) mediante un proceso de *resolución* en el que participan muchos servidores de nombres organizados jerárquicamente: los servidores **raíz** (`.`), los de dominio de primer nivel o **TLD** (p. ej. `com`, `edu`) y los servidores de **dominio** de segundo nivel (p. ej. `example.com`). En conjunto forman una infraestructura esencial de Internet. A diferencia de las demás prácticas de la unidad, **esta no es de ataque**: construye desde cero una infraestructura DNS en miniatura (Figura 1) que sirve de base para comprender los ataques DNS (P-11, P-12, P-13) y las defensas (P-15, DNSSEC).

### Resolución directa e inversa

En la **resolución directa** (*forward lookup*) se obtiene la IP a partir del nombre; en la **inversa** (*reverse lookup*) se obtiene el nombre a partir de la IP, usando el dominio especial `in-addr.arpa` y registros `PTR`. El **resolvedor** (servidor DNS local) realiza la resolución *recursiva* para el cliente: si no tiene la respuesta en su caché, consulta iterativamente a la raíz, al TLD y al servidor de dominio. Los servidores raíz, TLD y de dominio se configuran como **no recursivos** (solo responden lo que conocen); el resolvedor local, como **recursivo**.

> **Figura 1.** Infraestructura DNS simplificada a construir: la máquina usuario consulta al resolvedor local, que recorre la jerarquía raíz → TLD → dominio (adaptado de la Fig. 1 del SEED DNS Infrastructure Lab).  
> *(diagrama vectorial; se reproduce en el PDF del manual)*

**Objetivo general**
Construir una infraestructura DNS jerárquica completa (servidores de dominio, TLD, raíz, resolvedor local y cliente) dentro del SEED Internet Emulator, y habilitar tanto la resolución directa como la inversa.
**Objetivos específicos**

- **OE1.** Configurar los servidores de dominio (`example.com` y `<apellido>2026.edu`).
- **OE2.** Configurar los servidores TLD (`com` maestro/esclavo y `edu`) y los servidores raíz.
- **OE3.** Configurar el resolvedor local (recursivo, con `root.hints`) y el cliente.
- **OE4.** Verificar la resolución completa con `dig` y trazas de paquetes en el mapa del emulador.
- **OE5.** Configurar la resolución inversa (`in-addr.arpa`, registros `PTR`).

## Actividades previas

Antes de la sesión de laboratorio, cada estudiante debe completar las siguientes actividades preparatorias:

- **AP1.** Repasar el funcionamiento del DNS (jerarquía, registros SOA, NS, A, PTR) y las referencias citadas.
- **AP2.** Verificar que el entorno (VM SEED y el SEED Internet Emulator) esté operativo conforme al capítulo *Configuración del Entorno*.
- **AP3.** Tomar una *snapshot* del estado inicial para poder revertir cambios.
- **AP4.** Revisar la Sección [Seguridad y normas generales del laboratorio](../practicas/00-normas-generales.md#seguridad-y-normas-generales-del-laboratorio) (Seguridad y normas generales del laboratorio).
- **AP5.** Preparar la bitácora digital para registrar comandos, capturas y observaciones durante la sesión.

## Materiales y Equipos

| Recurso | Descripción |
| --- | --- |
| SEED Ubuntu 20.04 VM | Entorno de laboratorio SEED |
| SEED Internet Emulator | Emulador con la infraestructura DNS y el mapa web (`localhost:8080`) |
| SEED `Labsetup.zip` | Archivos de contenedores (carpeta `output/`) |
| BIND 9 (`named`, `dig`) | Servidores de nombres y consultas |
| `getzone.sh` / `sendzone.sh` | Copiar zonas entre host y contenedor |

> [!NOTE]
> **Provisión de materiales**
>
> El estudiante adquiere o instala por su cuenta el equipo personal (laptop), las máquinas virtuales (VirtualBox, SEED VM) y todo el software listado arriba. El laboratorio de la Carrera de Telecomunicaciones provee el espacio físico, el mobiliario y **acceso a Internet supervisado** para la descarga de imágenes, paquetes y consulta de documentación durante la sesión. El laboratorio no entrega equipos de cómputo personales ni licencias de software.

## Entorno de Laboratorio

La práctica se realiza dentro del **SEED Internet Emulator**. Tras iniciar la emulación, el mapa de la red emulada se consulta en `http://localhost:8080/map.html`, donde se pueden visualizar hosts, routers y redes, aplicar filtros tipo `tcpdump` para animar el tráfico y reproducir eventos. Cada servidor de nombres es un contenedor; sus nombres incluyen el término `DNS` y su IP:

**Listado 1.** Servidores de nombres del emulador

```bash
$ dockps | grep DNS
as150h-DNS-Root-A-10.150.0.72       # Raíz A (maestro)
as160h-DNS-Root-B-10.160.0.72       # Raíz B
as151h-DNS-COM-A-10.151.0.72        # TLD com (maestro)
as161h-DNS-COM-B-10.161.0.72        # TLD com (esclavo)
as152h-DNS-EDU-10.152.0.71          # TLD edu
as154h-DNS-Example-10.154.0.71      # dominio example.com
as162h-DNS-AAAAA-10.162.0.72        # dominio <apellido>2026.edu
as153h-Global_DNS-1-10.153.0.53     # resolvedor local 1
as163h-Global_DNS-2-10.163.0.53     # resolvedor local 2
```

> [!NOTE]
> **Copiar archivos de zona**
>
> Los archivos de zona están en `/etc/bind/zones` dentro de cada contenedor. Para no perder los cambios al detener los contenedores, se copian al host con `getzone.sh` (usa una palabra clave del nombre del contenedor) y se devuelven con `sendzone.sh` (que además reinicia el servicio `named`).
>
> ```bash
> $ ./getzone.sh  Example example.com.   # -> Example_example.com
> $ ./sendzone.sh Example example.com.   # copia de vuelta y reinicia named
> ```

## Consideraciones de seguridad

Antes de iniciar el procedimiento, revise la Sección [Seguridad y normas generales del laboratorio](../practicas/00-normas-generales.md#seguridad-y-normas-generales-del-laboratorio) (Seguridad y normas generales del laboratorio). Para esta práctica se destacan los siguientes riesgos y precauciones específicas:

- **Aislamiento de red obligatorio**: toda la configuración se realiza dentro del emulador SEED. No modifique servidores DNS reales ni la configuración de red del anfitrión fuera del laboratorio.
- **Snapshots y reversibilidad**: tome una instantánea antes de editar archivos de configuración (`named.conf.zones`, zonas, `root.hints`, `resolv.conf`).
- **Marco legal**: aunque esta práctica no es ofensiva, la manipulación de infraestructura DNS ajena puede tipificarse como delito informático (COIP Arts. 229 y 234; LOPDP).
- **Riesgos eléctricos y ergonomía**: aplique las pausas activas y verificaciones de las Secciones *Riesgos eléctricos* y *Ergonomía* dentro de Sección [Seguridad y normas generales del laboratorio](../practicas/00-normas-generales.md#seguridad-y-normas-generales-del-laboratorio).

> [!WARNING]
> **Riesgos específicos de la práctica**
>
> Un error en los archivos de configuración hará que `named` no inicie. Verifique la sintaxis y el *número de serie* del SOA tras cada cambio, y documente en la bitácora las incidencias y su solución.

## Procedimiento

Se configura la infraestructura **de abajo hacia arriba**: primero los servidores de dominio (Tarea 1), luego los TLD (Tarea 2), después la raíz (Tarea 3), el resolvedor local (Tarea 4) y el cliente (Tarea 5). Finalmente se habilita la resolución inversa (Tarea 6). Tras cada cambio en BIND, reinicie el servidor con `service named restart` y, en los maestros, incremente el número de serie del SOA.

### Tarea 1 — Configurar el servidor de dominio

#### Tarea 1.a — Nameserver de `example.com`

Añada la zona en `/etc/bind/named.conf.zones` del contenedor `Example` y cree el archivo de zona con los registros SOA, NS y al menos cuatro registros A.

**Listado 2.** Entrada de zona en named.conf.zones

```
zone "example.com" {
    type master;
    allow-update { any; };
    file "/etc/bind/zones/example.com.";   // archivo de zona
};
```

**Listado 3.** Archivo de zona example.com.

```
$TTL 300
$ORIGIN example.com.
@ SOA ns1.example.com. admin.example.com. 1635647622 900 900 1800 60

@                NS   ns1.example.com.
ns1.example.com. A    10.154.0.71

www              A    10.154.0.72
abc              A    10.154.0.73
```

**Listado 4.** Reiniciar y probar example.com

```bash
# service named restart
# Probar directamente al nameserver (aún no hay infraestructura completa):
$ dig @10.154.0.71 www.example.com
```

#### Tarea 1.b — Nameserver de otro dominio

Configure un segundo dominio con el formato `<apellido><año>.edu` (p. ej. `<apellido>2026.edu`) en el contenedor vacío cuyo nombre contiene la palabra clave `AAAAA` (`10.162.0.72`).

### Tarea 2 — Configurar los servidores TLD

Los TLD `com` (maestro `COM-A` y esclavo `COM-B`) y `edu` deben registrar a sus dominios con un par de registros **NS** y **A**. Solo se edita la zona en el maestro; el esclavo se sincroniza por transferencia de zona.

**Listado 5.** Configuración maestro/esclavo de com

```
// Maestro (COM-A)
zone "com." { type master; allow-transfer { any; }; ...};
// Esclavo (COM-B)
zone "com." { type slave; masters { 10.151.0.72; }; ... };
```

Los TLD se configuran como **no recursivos** (`recursion no`): solo indican el nameserver del dominio consultado, sin resolver por el cliente.

**Listado 6.** named.conf.options del TLD (no recursivo)

```
options {
    directory "/var/cache/bind";
    recursion no;
    dnssec-validation no;
    empty-zones-enable no;
    allow-query  { any; };
    allow-update { any; };
};
```

**Listado 7.** Probar los servidores TLD

```bash
# dig @10.151.0.72 www.example.com          # COM-A
# dig @10.161.0.72 www.example.com          # COM-B (esclavo)
# dig @10.152.0.72 www.<apellido>2026.edu   # EDU
```

### Tarea 3 — Configurar los servidores raíz

Hay dos servidores raíz (`Root-A` `10.150.0.72` y `Root-B` `10.160.0.72`), sincronizados manualmente con contenido idéntico. Registre los TLD `com` y `edu` en la zona raíz (par NS + A) en ambos servidores y reinicie.

**Listado 8.** Probar los servidores raíz

```bash
$ dig @<root-ip>  <cualquiernombre>.com
$ dig @<root-ip>  <cualquiernombre>.edu
$ dig @<root-ip>  com
$ dig @<root-ip>  edu
```

### Tarea 4 — Configurar el resolvedor local

El resolvedor local (`Global_DNS-1` `10.153.0.53` y `Global_DNS-2` `10.163.0.53`) sí es **recursivo**. Para iniciar la resolución iterativa necesita conocer las IP de los servidores raíz, indicadas en el archivo `root.hints`.

**Listado 9.** Habilitar recursión en el resolvedor

```
options {
    recursion yes;
    ...
};
```

**Listado 10.** Zona hint y archivo root.hints

```
zone "." {
    type hint;
    file "/usr/share/dns/root.hints";
};
// root.hints
.     NS  ns1.
.     NS  ns2.
ns1.  A   10.150.0.72
ns2.  A   10.160.0.72
```

**Experimento.** Cambie en `root.hints` las IP de los servidores raíz por valores erróneos (p. ej. `72`→`75`) y observe cómo se rompe la resolución; restaure los valores al terminar.

**Listado 11.** Probar el resolvedor

```bash
# dig @10.153.0.53  example.com
# dig @10.163.0.53  example.com
```

### Tarea 5 — Configurar el cliente

Para que el sistema use el resolvedor sin la opción `@ip`, añada el resolvedor como primer `nameserver` en `/etc/resolv.conf` de los hosts de `AS-155`:

**Listado 12.** /etc/resolv.conf del cliente

```
nameserver 10.153.0.53
nameserver 10.163.0.53
```

**Listado 13.** Probar la infraestructura completa

```bash
# dig www.example.com
# dig www.<apellido>2026.edu
```

Use el mapa del emulador con el filtro `udp and dst port 53` para capturar y *reproducir* la traza de paquetes de la resolución recursiva (raíz → TLD → dominio).

### Tarea 6 — Resolución inversa (`in-addr.arpa`)

La resolución inversa obtiene el nombre a partir de la IP. Configure el soporte para la red `10.154.0.0/24` (dominio `example.com`):

1. En los servidores raíz, registre la zona `in-addr.arpa`.
2. Aloje la zona `in-addr.arpa` (p. ej. en el nameserver `com`) y delegue `154.10.in-addr.arpa` a su servidor.
3. Cree la zona `154.10.in-addr.arpa` con registros `PTR` para `example.com`.

**Listado 14.** Zona de resolución inversa con registros PTR

```
$TTL 300
$ORIGIN 154.10.in-addr.arpa.
@ SOA ns1.example.com. admin.example.com. 1635647622 900 900 1800 60

@                NS  ns1.example.com.
ns1.example.com. A   10.154.0.71

71.0   IN  PTR  ns1.example.com.
72.0   IN  PTR  www.example.com.
73.0   IN  PTR  abc.example.com.
```

**Listado 15.** Probar la resolución inversa

```bash
# dig -x 10.154.0.71
# dig -x 10.154.0.72
# dig -x 10.154.0.73
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
| Resolución directa (www.example.com) |   |   |
| Saltos en la traza recursiva |   |   |
| Resolución inversa (dig -x) |   |   |

**Pautas para el análisis de los datos recolectados:**

- Contraste la traza de paquetes observada con el proceso de resolución recursiva esperado (raíz → TLD → dominio).
- Explique el efecto de la caché del resolvedor en consultas repetidas.
- Documente el experimento de `root.hints` (IP erróneas) y su impacto en la resolución.

## Preguntas de Análisis

- **P1.** Describa el proceso de resolución recursiva completo para `www.example.com`, indicando qué servidor responde en cada paso.
- **P2.** ¿Por qué los servidores raíz y TLD se configuran como *no recursivos* y el resolvedor local como *recursivo*?
- **P3.** ¿Qué función cumple el archivo `root.hints`? ¿Qué ocurrió en el experimento al alterar las IP de los servidores raíz?
- **P4.** Explique el par de registros `NS` + `A` que un dominio debe registrar en su zona padre (TLD), y por qué es necesario.
- **P5.** ¿Cómo funciona la resolución inversa? Explique el papel del dominio `in-addr.arpa` y de los registros `PTR`.
- **P6.** ¿Qué papel juega el número de serie del SOA en la sincronización maestro/esclavo (p. ej. `com`)?
- **P7.** Relacione esta infraestructura con los ataques de las prácticas P-11, P-12 y P-13: ¿qué eslabón se ataca en cada caso?

## Actividad ABET — SO4: Responsabilidad Ética y Profesional

Esta actividad mide el **Student Outcome 4 (SO4)** de la Carrera de Telecomunicaciones requerido para la acreditación ABET: *habilidad para reconocer las responsabilidades éticas y profesionales en situaciones de ingeniería y emitir juicios fundamentados, considerando el impacto global, económico, medioambiental y social de las soluciones propuestas.* Representa el **30 %** de la valoración total de la práctica y evalúa los indicadores PI 4.1 y PI 4.2 mediante las preguntas SO4-1 y SO4-2.

- **SO4-1.** **[PI 4.1 — 15 %] Ética y responsabilidad profesional ante un error de configuración en DNS autoritativo**
  Un ingeniero que administra los servidores DNS autoritativos del dominio principal de un ministerio ecuatoriano (.gob.ec) comete un error en la configuración de las zonas durante un mantenimiento programado, causando que el dominio quede irresolvible durante 2 horas. Analice:

  - **a)** Las **responsabilidades éticas del ingeniero**: reporte inmediato al responsable de TI y a la autoridad regulatoria vs. resolución silenciosa del error.
  - **b)** La importancia del **change management** y los procedimientos de rollback para operaciones críticas de DNS, y el principio de responsabilidad (accountability) en ingeniería.
  - **c)** Las **consecuencias legales** bajo la Ley Orgánica del Servicio Público (LOSEP) y el COIP si el error causó daños cuantificables a la prestación de servicios públicos digitales.
- **SO4-2.** **[PI 4.2 — 15 %] Impacto integral de un fallo en la infraestructura del TLD nacional**
  Un fallo en la infraestructura del TLD nacional (.ec), causado por un ataque coordinado sobre los servidores DNS raíz del ccTLD, deja sin servicio a 50 000 dominios ecuatorianos durante 6 horas (bancos, tiendas en línea, portales gubernamentales, instituciones educativas). Analice:

  - **a)** **Económico:** pérdidas acumuladas de todos los servicios digitales afectados, multas regulatorias, costos de recuperación de la infraestructura DNS nacional.
  - **b)** **Social:** interrupción de trámites gubernamentales en línea, paralización del comercio electrónico nacional, acceso nulo a servicios de salud y educación en línea.
  - **c)** **Ambiental:** consumo energético de la respuesta al incidente y de la implementación de infraestructura DNS anycast de respaldo.
  - **d)** **Contramedidas:** proponga **dos contramedidas técnicas** (servidores DNS anycast secundarios, DNSSEC para el TLD) y **una política organizacional**, citando RFC 7706, NIST SP 800-81r2 o ISO/IEC 27031.

## Discusión y conclusiones

A partir de los datos recolectados y del análisis realizado, elabore una discusión que responda al menos a las siguientes preguntas guía:

- **DC1.** ¿Se alcanzaron los objetivos planteados? Justifique cada uno con evidencia experimental concreta (capturas, métricas, salidas de comandos).
- **DC2.** ¿Qué limitaciones impone el entorno emulado a los resultados? ¿Cómo se trasladarían las observaciones a un escenario real de producción?
- **DC3.** ¿Qué controles de seguridad (p. ej. DNSSEC, limitación de transferencias de zona) reforzarían esta infraestructura? Cite al menos una RFC o estándar (ISO/IEC, IEEE, NIST) pertinente.
- **DC4.** ¿Qué errores se cometieron durante la práctica y qué recomendaciones daría a futuros estudiantes para evitarlos?

Cierre con **conclusiones** (3–5 viñetas) que resuman los hallazgos principales y los vinculen explícitamente con los *Resultados de Aprendizaje* de la asignatura.

## Entregables

1. **Informe técnico** detallado con capturas que describan lo realizado y observado en cada tarea (1–6): archivos de zona y configuración, salidas de `dig` (directas e inversas) y la traza de paquetes del mapa del emulador. Explique cada fragmento de configuración (adjuntar sin explicar no recibe puntaje). Bibliografía IEEE (≥3 fuentes).
2. **Archivos de zona y configuración** de los servidores de dominio, TLD, raíz, resolvedor y de la zona inversa, incluido el dominio propio (`<apellido>2026.edu`).
3. **Respuestas a la Actividad ABET – SO4** (preguntas SO4-1 y SO4-2), integradas en el informe técnico con extensión de 1–2 páginas por pregunta y las fuentes citadas según norma IEEE.

## Rúbrica de Evaluación

**Tabla 3.** Rúbrica — P-14 (10 puntos)

| Criterio | Peso | Indicador | Descripción |
| --- | --- | --- | --- |
| Servidores de dominio | 14 % | Zonas configuradas | Tarea 1: `example.com` y `<apellido>2026.edu` resuelven directamente (`dig @ip`). |
| TLD y raíz | 18 % | Delegaciones | Tareas 2–3: pares NS+A registrados; `com`/`edu` y la raíz responden correctamente. |
| Resolvedor y cliente | 21 % | Resolución completa | Tareas 4–5: `dig www.example.com` resuelve vía la infraestructura; traza recursiva en el mapa. |
| Resolución inversa | 10 % | Registros PTR | Tarea 6: `dig -x` devuelve el nombre correcto. |
| Análisis | 7 % | Preguntas respondidas | Respuestas con fundamento técnico. |
| **ABET – SO4: Responsabilidad Ética y Profesional (30 %)** |   |   |   |
| PI 4.1 – Ética profesional | 15 % | Respuesta ética fundamentada | Aplica principios éticos y legales al escenario del incidente; la cadena de notificación está justificada. |
| PI 4.2 – Impacto integral | 15 % | Análisis de impacto | Evalúa impacto económico, social y ambiental con contramedidas técnicas y organizacionales, citando al menos un estándar internacional. |

**Tabla 4.** Escala ABET SO4 — P-14

| PI | No cumple<br>(0–59 %) | Cumple parcialmente<br>(60–69 %) | Cumple<br>(70–79 %) | Supera<br>(80–89 %) | Supera ampliamente<br>(90–100 %) |
| --- | --- | --- | --- | --- | --- |
| 4.1 | No aplica principios éticos ni profesionales al evaluar la situación de incidente. | Aplica de manera inconsistente los principios éticos; el análisis legal es superficial o erróneo. | Aplica de manera básica los principios éticos; menciona el marco legal ecuatoriano sin análisis profundo. | Aplica coherentemente su juicio ético y profesional; integra el COIP y la LOPDP con argumentación clara. | Aplica de manera ejemplar e integral su juicio ético; argumenta cada decisión con evidencia y normativas citadas con precisión. |
| 4.2 | No considera ninguno de los tres impactos (económico, social, ambiental). | Considera parcialmente uno o dos de los impactos; las contramedidas no citan estándares. | Considera los tres impactos de forma adecuada; propone contramedidas pertinentes con al menos un estándar citado. | Integra los tres impactos con análisis detallado y contramedidas bien fundamentadas en estándares internacionales. | Realiza una evaluación exhaustiva de los tres impactos; las contramedidas son innovadoras y se respaldan en múltiples estándares. |

## Referencias

1. Du, Wenliang, «Computer & Internet Security: A Hands-on Approach». Independently published, 2019.

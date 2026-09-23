<div align="center">

# P-15 · Extensiones de Seguridad DNS (DNSSEC)

![Docker](https://img.shields.io/badge/Docker-Lab_Environment-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-Scripts-yellow?style=for-the-badge&logo=python)
![Security](https://img.shields.io/badge/Focus-Network_Security-critical?style=for-the-badge)

</div>

> Práctica del **Manual de Prácticas** de Seguridad en Redes · INGE-00107 · Universidad de Cuenca.  
> Documento generado desde el manual: no lo edite a mano (véase el [índice de prácticas](../README.md)).

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

Los fundamentos teóricos sintetizados en esta sección se basan en [1], [2], [3], [4]; se recomienda consultar dichas fuentes para una exposición más profunda. El procedimiento de laboratorio adapta el *DNSSEC Lab* de SEED [4].

### DNS y por qué necesita protección

El **DNS** (Domain Name System) traduce nombres de dominio a direcciones IP mediante una jerarquía de servidores: la zona **raíz** (`.`), los dominios de primer nivel o **TLD** (p. ej. `edu`), los dominios (p. ej. `example.edu`) y sus subdominios. El DNS original no autentica las respuestas, por lo que es vulnerable al **envenenamiento de caché**: un atacante puede inyectar datos falsos (estudiado en la práctica P-11).

### DNSSEC y cómo funciona

**DNSSEC** (DNS Security Extensions) es un conjunto de extensiones que añade **autenticación** e **integridad** a los datos del DNS. Con DNSSEC, todas las respuestas de una zona protegida van **firmadas digitalmente**; al verificar la firma, el resolvedor comprueba si la información es auténtica. Así, el envenenamiento de caché es derrotado: cualquier dato falso (de un paquete falsificado o de un servidor malicioso) no supera la verificación de firma. DNSSEC **no cifra** las consultas: solo garantiza autenticidad e integridad, no confidencialidad.

### Gestión de claves: ZSK y KSK

Cada zona usa **dos** pares de claves (cada par tiene clave pública y privada):

- **ZSK** (Zone Signing Key): firma los registros de la zona. Puede rotarse con frecuencia para mayor seguridad. En el archivo de clave se marca con el valor `256`.
- **KSK** (Key Signing Key): firma únicamente el registro de la ZSK. Su información se publica en la zona padre, por lo que rota con poca frecuencia. Se marca con `257` (opción `-f KSK`) y suele usar una clave más larga (p. ej. 2048 frente a 1024 bits de la ZSK).

El esquema de dos claves evita actualizar la zona padre cada vez que rota la ZSK: basta firmar la nueva ZSK con la KSK.

### Cadena de confianza y registro DS

DNSSEC introduce nuevos tipos de registro: **DNSKEY** (claves públicas), **RRSIG** (firmas de los registros), **DS** (Delegation Signer) y **NSEC/NSEC3** (negación de existencia). El registro **DS** se coloca en la zona *padre* y contiene el *hash* de la KSK de la zona hija, junto con un *key tag* que la identifica; así el padre avala la KSK del hijo. Encadenando los DS desde la raíz hasta el dominio hoja se forma la **cadena de confianza** (Figura 1). Como la raíz no tiene padre, su clave pública (KSK) se distribuye por un canal seguro y se configura como **trust anchor** (ancla de confianza) en el resolvedor.

> **Figura 1.** Cadena de confianza DNSSEC: cada zona padre publica el registro DS (hash de la KSK del hijo), encadenando la confianza desde la raíz.  
> *(diagrama vectorial; se reproduce en el PDF del manual)*

**Objetivo general**
Configurar una infraestructura DNS jerárquica (raíz, `edu`, `example.edu` y resolvedor local) con DNSSEC habilitado en cada servidor, estableciendo una cadena de confianza completa que proteja las respuestas DNS frente a falsificación.
**Objetivos específicos**

- **OE1.** Generar las claves ZSK y KSK y firmar la zona `example.edu`.
- **OE2.** Configurar el servidor `edu` y publicar el registro DS de `example.edu`.
- **OE3.** Configurar el servidor raíz y publicar el DS de `edu`.
- **OE4.** Configurar el resolvedor local con el *trust anchor* de la raíz y validar la cadena de confianza (flag `ad`).
- **OE5.** Demostrar que una respuesta falsificada es detectada y rechazada por el resolvedor con DNSSEC activado.

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
| Docker + Docker Compose | Infraestructura DNS: raíz, `edu`, `example.edu` y resolvedor local |
| `bind9utils` | `dnssec-keygen`, `dnssec-signzone` (instalar en la VM anfitriona) |
| `dig` (dnsutils) | Consultas DNSSEC con la opción `+dnssec` |

> [!NOTE]
> **Provisión de materiales**
>
> El estudiante adquiere o instala por su cuenta el equipo personal (laptop), las máquinas virtuales (VirtualBox, SEED VM, Kali Linux, contenedores Docker) y todo el software listado arriba. El laboratorio de la Carrera de Telecomunicaciones provee el espacio físico, el mobiliario y **acceso a Internet supervisado** para la descarga de imágenes, paquetes y consulta de documentación durante la sesión. El laboratorio no entrega equipos de cómputo personales ni licencias de software.

## Entorno de Laboratorio

> **Figura 2.** Topología del laboratorio P-15 (*Lab environment setup*): infraestructura DNS simplificada con todos los servidores en la LAN 10.9.0.0/24.  
> *(diagrama vectorial; se reproduce en el PDF del manual)*

Se provee una mini infraestructura DNS, cada servidor de nombres alojado en un contenedor. Por simplicidad, todos están en la misma LAN; en el mundo real estarían dispersos en Internet, pero su configuración es equivalente. Las herramientas DNSSEC se instalan en la VM anfitriona (no dentro del contenedor) y los resultados se copian al contenedor correspondiente con `docker cp`.

**Listado 1.** Instalar herramientas y copiar archivos al contenedor

```bash
# Instalar las herramientas DNSSEC en la VM anfitriona
$ sudo apt-get install bind9utils

# Copiar un archivo a la carpeta /tmp del contenedor
$ docker cp xyz <docker id>:/tmp
# Copiar un archivo /tmp/abc desde el contenedor
$ docker cp <docker id>:/tmp/abc .
```

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

Se configurará DNSSEC en cada servidor de nombres, de abajo hacia arriba de la jerarquía: primero `example.edu`, luego `edu`, después la raíz y finalmente el resolvedor local. Use `docker-compose` para construir e iniciar los contenedores.

### Tarea 1 — Configurar el dominio `example.edu`

Ingrese a la carpeta del contenedor del servidor de nombres de `example.edu`; en ella se editarán los archivos para que el servidor soporte DNSSEC.

#### Tarea 1.a — Generar las claves de `example.edu`

Genere dos pares de claves: la **ZSK** y la **KSK**. Ambas usan el algoritmo `RSASHA256`; la KSK duplica el tamaño de clave por su rol más sensible. La opción `-f KSK` marca la clave con `257` (KSK); sin ella se marca `256` (ZSK).

**Listado 2.** Generar ZSK y KSK para example.edu

```bash
# ZSK (clave de firma de zona, 1024 bits)
$ dnssec-keygen -a RSASHA256 -b 1024 example.edu
# KSK (clave de firma de claves, 2048 bits)
$ dnssec-keygen -a RSASHA256 -b 2048 -f KSK example.edu
```

#### Tarea 1.b — Firmar la zona de `example.edu`

Firme el archivo de zona con `dnssec-signzone`. La opción `-S` busca automáticamente las claves de firma en la carpeta actual (o la indicada con `-K`); `-e` fija la fecha de expiración de las firmas (formato `YYYYMMDDHHMMSS`; por defecto sería solo un mes).

**Listado 3.** Firmar la zona example.edu

```bash
$ dnssec-signzone -e 20501231000000 -S -o example.edu example.edu.db
```

Se genera un nuevo archivo `example.edu.db.signed` con los registros añadidos (DNSKEY, RRSIG, NSEC). Indique al servidor que use ese archivo firmado editando `named.conf.seedlabs`:

**Listado 4.** Usar la zona firmada en named.conf.seedlabs

```bash
zone "example.edu" {
    type master;
    file "/etc/bind/example.edu.db.signed";
};
```

#### Tarea 1.c — Pruebas

Reconstruya e inicie los contenedores y consulte con `dig`. La opción `+dnssec` activa el bit DO (DNSSEC OK), pidiendo al servidor los registros DNSSEC asociados. En el laboratorio, `10.9.0.65` es la IP del servidor `example.edu`.

**Listado 5.** Consultar registros DNSSEC de example.edu

```bash
# Formato general:  dig @servidor nombre tipo +dnssec
$ dig @10.9.0.65 example.edu DNSKEY +dnssec
$ dig @10.9.0.65 example.edu NS +dnssec
$ dig @10.9.0.65 www.example.edu A +dnssec
```

### Tarea 2 — Configurar el servidor `edu`

El procedimiento es análogo al de la Tarea 1, pero además la zona padre `edu` debe avalar a `example.edu` mediante su registro DS.

#### Tarea 2.a — Encontrar y añadir el registro DS

Al firmar `example.edu` se generó el registro DS de su KSK en el archivo `dsset-example.edu.` El registro DS contiene un *key tag* () que identifica la clave referenciada, y el *digest* (), que es el hash unidireccional de la KSK:

**Listado 6.** Ejemplo de registro DS

```
example.edu.  IN DS 10246  8  2  563D...(omitido)...1D59D1
                    (1)             (2)
```

#### Tarea 2.b — Configurar el servidor `edu`

Siga la Tarea 1 para generar ZSK/KSK y firmar la zona `edu`, pero **antes de firmar** incluya el registro DS de la zona delegada. En lugar de copiar el contenido, conviene usar `$INCLUDE` (si rota la KSK del hijo, el nombre del archivo DS no cambia y no hay que tocar la zona padre):

**Listado 7.** Incluir el registro DS en la zona edu

```
$INCLUDE ../edu.example/dsset-example.edu.
```

#### Tarea 2.c — Pruebas

Reconstruya los contenedores y consulte el servidor `edu` (`10.9.0.60`). Explique cada registro de la respuesta.

**Listado 8.** Consultar registros DNSSEC de edu

```bash
$ dig @10.9.0.60 edu DNSKEY +dnssec
$ dig @10.9.0.60 edu NS +dnssec
$ dig @10.9.0.60 example.edu +dnssec
```

### Tarea 3 — Configurar el servidor raíz

El procedimiento es el mismo de la tarea anterior. Recuerde añadir el registro DS de la zona `edu` al archivo de zona de la raíz **antes** de firmarla. Pruebe contra el servidor raíz (`10.9.0.30`):

**Listado 9.** Consultar registros DNSSEC de la raíz

```bash
$ dig @10.9.0.30 . DNSKEY +dnssec
$ dig @10.9.0.30 . NS +dnssec
$ dig @10.9.0.30 edu +dnssec
$ dig @10.9.0.30 example.edu +dnssec
```

### Tarea 4 — Configurar el resolvedor (DNS local)

El servidor DNS local realiza la resolución completa y la validación DNSSEC. Como la raíz no tiene padre, su clave pública (KSK) se configura como **trust anchor**. BIND 9 trae anclas integradas, pero pueden sobrescribirse en `/etc/bind/bind.keys` con la KSK de *nuestra* raíz (use la KSK, no la ZSK):

**Listado 10.** Definir el trust anchor de la raíz

```
trust-anchors {
    . initial-key 257 3 8 " <KSK de la raíz> ";
};
```

Habilite la validación DNSSEC en `named.conf.options` del resolvedor local:

**Listado 11.** Habilitar la validación DNSSEC

```
dnssec-validation auto;
dnssec-enable yes;
```

#### Prueba de la cadena de confianza

Consulte al resolvedor local (`10.9.0.53`). Si todo está bien, la respuesta trae la dirección IP y el **flag `ad`** (*authentic data*), que indica que la validación DNSSEC fue exitosa.

**Listado 12.** Validación a través del resolvedor local

```bash
$ dig @10.9.0.53 www.example.edu +dnssec
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 37130
;; flags: qr rd ra ad; QUERY: 1, ANSWER: 2, AUTHORITY: 0, ...
;; ANSWER SECTION:
www.example.edu.   259200  IN  A      1.2.3.5
www.example.edu.   259200  IN  RRSIG  ... <firma>
```

#### Experimento: detección de respuestas falsas

Diseñe un experimento que demuestre que, cuando la respuesta es falsa, el resolvedor local la detecta y muestra un error. No es necesario un ataque real: basta con modificar (o corromper) algún registro existente sin regenerar su firma, y observar que la validación falla y el flag `ad` desaparece.

### Tarea 5 — Añadir otro servidor de dominio

Suponga que posee un dominio dentro de `edu` y quiere un servidor de nombres con DNSSEC para él. Se dispone de un contenedor de reserva con BIND9 instalado. Configure ese servidor para que soporte DNSSEC; el dominio debe contener su **apellido** y el **año** de la práctica (p. ej. `smith2026.edu`). No es necesario registrar el dominio en el mundo real: solo se monta dentro de la infraestructura DNS del laboratorio.

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

- **P1.** ¿Cuál es la diferencia entre ZSK y KSK, y por qué se usa un esquema de dos claves en lugar de una sola? Relacione su respuesta con los valores `256`/`257` de los archivos de clave.
- **P2.** Explique el registro **DS**: ¿qué contiene (key tag y digest), en qué zona se publica y cómo encadena la confianza desde la raíz hasta `example.edu`?
- **P3.** ¿Qué registros nuevos introduce DNSSEC y qué función cumple cada uno? (DNSKEY, RRSIG, DS, NSEC/NSEC3).
- **P4.** ¿Qué es un *trust anchor* y por qué es imprescindible para la zona raíz? ¿Qué pasaría si se configurara con la ZSK en vez de la KSK de la raíz?
- **P5.** En la salida de `dig`, ¿qué significa el flag `ad`? En su experimento de la Tarea 4, ¿cómo cambia la respuesta cuando se corrompe un registro o su firma?
- **P6.** ¿Por qué DNSSEC *no* cifra las consultas DNS? ¿Qué tecnología aporta confidencialidad (p. ej. DoT/DoH)?
- **P7.** Explique por qué el ataque de envenenamiento de caché de la práctica P-11 fracasa cuando la zona objetivo está protegida con DNSSEC y validada por el resolvedor.

## Actividad ABET — SO4: Responsabilidad Ética y Profesional

Esta actividad mide el **Student Outcome 4 (SO4)** de la Carrera de Telecomunicaciones requerido para la acreditación ABET: *habilidad para reconocer las responsabilidades éticas y profesionales en situaciones de ingeniería y emitir juicios fundamentados, considerando el impacto global, económico, medioambiental y social de las soluciones propuestas.* Representa el **30 %** de la valoración total de la práctica y evalúa los indicadores PI 4.1 y PI 4.2 mediante las preguntas SO4-1 y SO4-2.

- **SO4-1.** **[PI 4.1 — 15 %] Ética y responsabilidad profesional cuando la recomendación de implementar DNSSEC es rechazada**
  Un ingeniero de telecomunicaciones recomienda formalmente implementar DNSSEC en el dominio de su empresa (institución financiera) tras identificar vulnerabilidades de envenenamiento de caché. El director de TI rechaza la propuesta argumentando ``costo operativo elevado y complejidad innecesaria''. El ingeniero sabe que sin DNSSEC el dominio es vulnerable. Analice:

  - **a)** Las **responsabilidades éticas del ingeniero** cuando su recomendación técnica es rechazada: escalar la decisión, documentar formalmente el riesgo aceptado o renunciar.
  - **b)** Los **principios de responsabilidad profesional y protección al usuario final** que fundamentan la insistencia en adoptar DNSSEC.
  - **c)** Las **implicaciones legales** (LOPDP, Ley General de Instituciones del Sistema Financiero) si un ataque de envenenamiento de caché resulta en daños a clientes y se demuestra que el ingeniero reportó el riesgo y fue ignorado.
- **SO4-2.** **[PI 4.2 — 15 %] Impacto integral de un ataque de envenenamiento de caché contra el portal tributario por ausencia de DNSSEC**
  La ausencia de DNSSEC en los servidores DNS del Servicio de Rentas Internas (SRI) de Ecuador permite que un atacante realice envenenamiento de caché y redirija el portal de declaraciones tributarias a un sitio de phishing durante 4 horas. Analice:

  - **a)** **Económico:** pérdidas directas de contribuyentes que ingresan datos bancarios en el sitio falso, costos de respuesta del SRI, multas del organismo de control.
  - **b)** **Social:** compromiso de información tributaria de miles de contribuyentes, paralización de trámites fiscales urgentes, erosión de la confianza en los servicios digitales del Estado.
  - **c)** **Ambiental:** consumo energético de la respuesta al incidente y de la implementación retroactiva de DNSSEC en la infraestructura del SRI.
  - **d)** **Contramedidas:** proponga **dos contramedidas técnicas** (DNSSEC + DANE, DNS-over-HTTPS) y **una política organizacional**, citando RFC 4033, RFC 7671 o NIST SP 800-81r2.

## Discusión y conclusiones

A partir de los datos recolectados y del análisis realizado, elabore una discusión que responda al menos a las siguientes preguntas guía:

- **DC1.** ¿Se alcanzaron los objetivos planteados? Justifique cada uno con evidencia experimental concreta (capturas, métricas, salidas de comandos).
- **DC2.** ¿Qué limitaciones impone el entorno virtualizado a los resultados? ¿Cómo se trasladarían las observaciones a un escenario real de producción?
- **DC3.** ¿Qué contramedidas o controles de seguridad mitigan el ataque o refuerzan la defensa estudiada? Cite al menos una buena práctica de la industria, una RFC o un estándar (ISO/IEC, IEEE, NIST) pertinente.
- **DC4.** ¿Qué errores se cometieron durante la práctica y qué recomendaciones daría a futuros estudiantes para evitarlos?

Cierre con **conclusiones** (3–5 viñetas) que resuman los hallazgos principales y los vinculen explícitamente con los *Resultados de Aprendizaje* de la asignatura.

## Entregables

1. **Informe técnico** detallado con capturas que describan lo realizado y observado en cada tarea (1–5): generación de claves, firma de zonas, registros DS, configuración del *trust anchor* y salidas de `dig +dnssec`. Explique cada fragmento de código/configuración relevante (adjuntar sin explicar no recibe puntaje). Las observaciones interesantes o sorprendentes deben justificarse. Bibliografía IEEE (≥3 fuentes).
2. **Evidencia del experimento** de la Tarea 4 mostrando que una respuesta falsa es detectada (pérdida del flag `ad` o error de validación).
3. **Archivos de configuración** de las zonas firmadas, `named.conf` y el *trust anchor*, incluido el dominio propio (`<apellido><año>.edu`) de la Tarea 5.
4. **Respuestas a la Actividad ABET – SO4** (preguntas SO4-1 y SO4-2), integradas en el informe técnico con extensión de 1–2 páginas por pregunta y las fuentes citadas según norma IEEE.

## Rúbrica de Evaluación

**Tabla 3.** Rúbrica — P-15 (10 puntos)

| Criterio | Peso | Indicador | Descripción |
| --- | --- | --- | --- |
| Zona example.edu | 14 % | Claves y firma | ZSK/KSK generadas; zona firmada con DNSKEY/RRSIG visibles en `dig` (Tarea 1). |
| Servidores edu y raíz | 18 % | Registros DS | DS de la zona hija publicado e incluido en el padre; firmas correctas (Tareas 2–3). |
| Cadena de confianza | 21 % | Flag `ad` | Resolvedor local con *trust anchor*; respuestas validadas con flag `ad` (Tarea 4). |
| Detección de falsos | 10 % | Respuesta rechazada | Experimento que demuestra la detección de una respuesta corrompida (Tarea 4). |
| Dominio propio y análisis | 7 % | Tarea 5 y preguntas | Servidor `<apellido><año>.edu` con DNSSEC y respuestas con fundamento técnico. |
| **ABET – SO4: Responsabilidad Ética y Profesional (30 %)** |   |   |   |
| PI 4.1 – Ética profesional | 15 % | Respuesta ética fundamentada | Aplica principios éticos y legales al escenario del incidente; la cadena de notificación está justificada. |
| PI 4.2 – Impacto integral | 15 % | Análisis de impacto | Evalúa impacto económico, social y ambiental con contramedidas técnicas y organizacionales, citando al menos un estándar internacional. |

**Tabla 4.** Escala ABET SO4 — P-15

| PI | No cumple<br>(0–59 %) | Cumple parcialmente<br>(60–69 %) | Cumple<br>(70–79 %) | Supera<br>(80–89 %) | Supera ampliamente<br>(90–100 %) |
| --- | --- | --- | --- | --- | --- |
| 4.1 | No aplica principios éticos ni profesionales al evaluar la situación de incidente. | Aplica de manera inconsistente los principios éticos; el análisis legal es superficial o erróneo. | Aplica de manera básica los principios éticos; menciona el marco legal ecuatoriano sin análisis profundo. | Aplica coherentemente su juicio ético y profesional; integra el COIP y la LOPDP con argumentación clara. | Aplica de manera ejemplar e integral su juicio ético; argumenta cada decisión con evidencia y normativas citadas con precisión. |
| 4.2 | No considera ninguno de los tres impactos (económico, social, ambiental). | Considera parcialmente uno o dos de los impactos; las contramedidas no citan estándares. | Considera los tres impactos de forma adecuada; propone contramedidas pertinentes con al menos un estándar citado. | Integra los tres impactos con análisis detallado y contramedidas bien fundamentadas en estándares internacionales. | Realiza una evaluación exhaustiva de los tres impactos; las contramedidas son innovadoras y se respaldan en múltiples estándares. |

## Referencias

1. Arends, Roy and others, «DNS Security Introduction and Requirements». RFC 4033, 2005.
2. Arends, Roy and others, «Resource Records for the DNS Security Extensions». RFC 4034, 2005.
3. Arends, Roy and others, «Protocol Modifications for the DNS Security Extensions». RFC 4035, 2005.
4. Du, Wenliang, «Computer & Internet Security: A Hands-on Approach». Independently published, 2019.

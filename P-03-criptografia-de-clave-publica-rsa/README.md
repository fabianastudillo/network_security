<div align="center">

# P-03 · Criptografía de Clave Pública (RSA)

![Docker](https://img.shields.io/badge/Docker-Lab_Environment-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-Scripts-yellow?style=for-the-badge&logo=python)
![Security](https://img.shields.io/badge/Focus-Network_Security-critical?style=for-the-badge)

</div>

> Práctica del **Manual de Prácticas** de Seguridad en Redes · INGE-00107 · Universidad de Cuenca.  
> Documento generado desde el manual: no lo edite a mano (véase el [índice de prácticas](../practicas/README.md)).

> [!TIP]
> Apuntes de comandos del docente para esta práctica: [`NOTAS.md`](NOTAS.md).

| Campo | Valor |
| --- | --- |
| **Asignatura** | Seguridad en Redes |
| **Docente** | Dr. Fabián Astudillo-Salinas |
| **Unidad** | 300 – Criptografía de clave pública |
| **Código** | INGE-00107 |
| **Modalidad** | Presencial |
| **Valoración** | 10 puntos |
| **Grupos** | Máx. 3 estudiantes |
| **Entrega** | Según calendario |
| **ABET** | SO4 – Responsabilidad Ética y Profesional (PI 4.1 y PI 4.2) — representa el 30 % de la valoración |

## Marco Teórico

Los fundamentos teóricos sintetizados en esta sección se basan en [1], [2], [3]; se recomienda consultar dichas fuentes para una exposición más profunda.

### El algoritmo RSA

RSA (Rivest–Shamir–Adleman) es uno de los primeros criptosistemas de clave pública y el más ampliamente utilizado para comunicación segura. El algoritmo genera dos números primos aleatorios grandes p y q, y luego los utiliza para generar pares de claves: **clave pública** (e, n) para cifrar y verificar firmas, y **clave privada** (d, n) para descifrar y firmar. La seguridad se basa en la dificultad computacional de factorizar n = p · q donde p y q son primos grandes.

Los números involucrados en RSA típicamente tienen más de 512 bits de longitud, por lo que no pueden manipularse con operadores aritméticos simples de 32 o 64 bits; se requieren bibliotecas de aritmética de enteros de tamaño arbitrario como `OpenSSL BN` o la biblioteca `Crypto` de Python.

### Autenticación SSH con clave pública

SSH (*Secure Shell*) soporta autenticación basada en clave pública como alternativa más segura a las contraseñas. El usuario genera un par de claves asimétricas: la **clave pública** se deposita en el servidor (`/.ssh/authorized_keys`) y la **clave privada** permanece en la máquina del cliente. Al conectarse, el servidor genera un desafío cifrado con la clave pública; solo quien posea la clave privada puede responderlo, sin que la clave privada viaje por la red.

El archivo `/.ssh/config` permite definir alias de conexión con parámetros predeterminados (host, usuario, clave, puerto), simplificando el uso cotidiano de SSH.

### Firma digital y certificados X.509

Una **firma digital** es el cifrado del hash del mensaje con la clave privada; el receptor verifica con la clave pública. Los **certificados X.509** vinculan una clave pública a una identidad y están firmados por una Autoridad Certificadora (CA). La cadena de certificados permite verificar la autenticidad de un servidor sin conocerlo previamente: basta confiar en la CA raíz que firmó al emisor intermedio que a su vez firmó el certificado del servidor.

**Objetivo general**
Aplicar criptografía de clave pública en escenarios reales: autenticación SSH sin contraseña, operaciones RSA con OpenSSL y verificación manual de certificados X.509.
**Objetivos específicos**

- **OE1.** Generar un par de claves RSA e inspeccionar sus parámetros con OpenSSL.
- **OE2.** Implementar cifrado, descifrado y firma digital RSA con OpenSSL.
- **OE3.** Configurar autenticación SSH basada en clave pública.
- **OE4.** Verificar manualmente la firma de un certificado X.509 real usando `openssl asn1parse` y `sha256sum`.

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
| SEED Ubuntu 20.04 VM | Entorno Linux con GCC y OpenSSL preinstalados |
| OpenSSL (línea de comandos) | Generación de claves RSA, cifrado, firma y análisis de certificados X.509 |
| Cliente SSH | Para autenticación con clave pública a la VM del laboratorio |
| Compilador GCC | Para compilar programas en C con BigNum |

> [!NOTE]
> **Provisión de materiales**
>
> El estudiante adquiere o instala por su cuenta el equipo personal (laptop), las máquinas virtuales (VirtualBox, SEED VM, Kali Linux, contenedores Docker) y todo el software listado arriba. El laboratorio de la Carrera de Telecomunicaciones provee el espacio físico, el mobiliario y **acceso a Internet supervisado** para la descarga de imágenes, paquetes y consulta de documentación durante la sesión. El laboratorio no entrega equipos de cómputo personales ni licencias de software.

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

### Tarea 1 — Generación de claves RSA con OpenSSL

1. Genere un par de claves RSA de 2048 bits:

   **Listado 1.** Generación de par de claves RSA

   ```bash
   $ openssl genrsa -out private.pem 2048
   $ openssl rsa -in private.pem -pubout -out public.pem
   ```
2. Inspeccione los parámetros de la clave privada (módulo n, exponentes e y d, primos p y q):

   **Listado 2.** Inspección de parámetros RSA

   ```bash
   $ openssl rsa -in private.pem -text -noout
   ```
3. Identifique en la salida los campos `modulus`, `publicExponent`, `privateExponent`, `prime1` y `prime2`. Verifique que el exponente público vale 65537 (0x10001), el valor estándar por ser eficiente y seguro.

### Tarea 2 — Cifrado y descifrado RSA

1. Cree un archivo de texto breve (RSA solo puede cifrar mensajes menores al tamaño de la clave):

   ```bash
   $ echo "Mensaje secreto de prueba" > message.txt
   ```
2. Cifre el archivo con la clave pública:

   **Listado 3.** Cifrado RSA con clave pública

   ```bash
   $ openssl rsautl -encrypt -inkey public.pem -pubin \
       -in message.txt -out message.enc
   ```
3. Descifre con la clave privada y verifique que el resultado coincide con el mensaje original:

   **Listado 4.** Descifrado RSA con clave privada

   ```bash
   $ openssl rsautl -decrypt -inkey private.pem \
       -in message.enc -out message_dec.txt
   $ cat message_dec.txt
   ```

### Tarea 3 — Firma digital

1. Calcule el hash SHA-256 del archivo y fírmelo con la clave privada:

   **Listado 5.** Generación de firma digital RSA

   ```bash
   $ openssl dgst -sha256 -sign private.pem \
       -out message.sig message.txt
   ```
2. Verifique la firma con la clave pública:

   **Listado 6.** Verificación de firma digital

   ```bash
   $ openssl dgst -sha256 -verify public.pem \
       -signature message.sig message.txt
   ```
3. Modifique `message.txt` y vuelva a intentar la verificación. Explique por qué falla.

### Tarea 4 — Autenticación SSH con clave pública

En lugar de autenticarse con contraseña, SSH puede usar un par de claves asimétricas. La clave privada queda protegida en el cliente y la clave pública se deposita en el servidor.

1. Conéctese inicialmente a la VM del laboratorio con contraseña (usuario `student`, contraseña `student`):

   ```bash
   $ ssh student@<IP_VM>
   ```
2. En su **máquina local**, genere un par de claves RSA de 2048 bits (omita el paso si ya dispone de `/.ssh/id_rsa`):

   **Listado 7.** Generación del par de claves SSH

   ```bash
   $ ssh-keygen -t rsa -b 2048
   ```

   Cuando se solicite la ruta, pulse Enter para usar la ubicación predeterminada (`/.ssh/id_rsa`). Puede dejar la passphrase vacía para este laboratorio.
3. Copie la clave pública a la VM del laboratorio:

   **Listado 8.** Copia de clave pública al servidor

   ```bash
   $ ssh-copy-id student@<IP_VM>
   ```

   Este comando añade el contenido de `/.ssh/id_rsa.pub` al archivo `/.ssh/authorized_keys` del servidor.
4. Verifique que ahora se conecta **sin contraseña**:

   ```bash
   $ ssh student@<IP_VM>
   ```
5. Si la clave privada no está en la ubicación predeterminada, especifíquela con la opción `-i`:

   ```bash
   $ ssh -i /ruta/a/clave_privada student@<IP_VM>
   ```
6. Asegúrese de que los permisos del archivo de clave privada sean correctos (SSH rechaza claves con permisos demasiado permisivos):

   ```bash
   $ chmod 600 ~/.ssh/id_rsa
   ```

### Tarea 5 — Configurar el archivo `/.ssh/config`

El archivo `/.ssh/config` permite definir alias de conexión con sus parámetros, evitando escribir la IP y el usuario en cada conexión.

1. Cree o edite el archivo `/.ssh/config` con el siguiente contenido, sustituyendo la IP de su VM:

   **Listado 9.** Ejemplo de archivo /.ssh/config

   ```
   Host seedvm
       HostName <IP_VM>
       User student
       IdentityFile ~/.ssh/id_rsa
   ```
2. Ajuste los permisos del archivo de configuración:

   ```bash
   $ chmod 600 ~/.ssh/config
   ```
3. Verifique que puede conectarse usando el alias:

   ```bash
   $ ssh seedvm
   ```

### Tarea 6 — Verificación manual de un certificado X.509

En esta tarea verificaremos manualmente la firma de un certificado X.509 real. Un certificado contiene datos sobre una clave pública y la firma de la CA sobre esos datos. El objetivo es reproducir el proceso de verificación paso a paso usando solo OpenSSL, sin delegar la verificación al propio `openssl verify`.

##### Paso 1 — Descargar la cadena de certificados.

Usaremos `www.example.org` como referencia; los estudiantes deben elegir un servidor diferente (nota: `www.example.com` comparte el mismo certificado que `www.example.org`).

**Listado 10.** Descarga de la cadena de certificados

```bash
$ openssl s_client -connect www.example.org:443 -showcerts
```

La salida incluye dos certificados delimitados por `-----BEGIN CERTIFICATE-----` y `-----END CERTIFICATE-----`. Copie cada bloque (incluyendo las líneas de delimitación) en dos archivos: `c0.pem` (certificado del servidor) y `c1.pem` (certificado de la CA intermedia).

Si el servidor devuelve un único certificado, fue firmado por una CA raíz cuyos certificados puede obtener desde Firefox: `Editar` → `Preferencias` → `Privacidad y seguridad` → `Ver certificados`.

##### Paso 2 — Extraer la clave pública `(e, n)` del emisor.

**Listado 11.** Extracción de parámetros RSA del emisor

```bash
# Modulo n:
$ openssl x509 -in c1.pem -noout -modulus

# Todos los campos (para encontrar el exponente e):
$ openssl x509 -in c1.pem -text -noout
```

##### Paso 3 — Extraer la firma del certificado del servidor.

**Listado 12.** Extracción e impresión de la firma

```bash
$ openssl x509 -in c0.pem -text -noout
...
Signature Algorithm: sha256WithRSAEncryption
    84:a8:9a:11:a7:d8:bd:0b:26:7e:52:24:7b:b2:55:9d:ea:30:
    89:51:08:87:6f:a9:ed:10:ea:5b:3e:0b:c7:2d:47:04:4e:dd:
    ...
```

Copie el bloque hexadecimal de la firma en un archivo `signature` y elimine espacios y dos puntos para obtener la cadena hexadecimal:

```bash
$ cat signature | tr -d '[:space:]:'
84a89a11a7d8bd0b267e52247bb2559dea30...
```

**Nota:** si el algoritmo de firma del certificado no es RSA, elija otro servidor.

##### Paso 4 — Extraer el cuerpo del certificado.

La CA firma el hash del cuerpo del certificado (excluyendo el bloque de firma). El formato X.509 usa ASN.1; `openssl asn1parse` permite inspeccionar la estructura y localizar los offsets exactos.

**Listado 13.** Análisis ASN.1 del certificado

```bash
$ openssl asn1parse -i -in c0.pem
        0:d=0  hl=4 l=1522 cons: SEQUENCE
        4:d=1  hl=4 l=1242 cons:  SEQUENCE        <- cuerpo
    ...
     1250:d=1  hl=2 l=  13 cons:  SEQUENCE        <- bloque de firma
```

El campo que comienza en el offset 4 es el cuerpo; extraígalo y calcule su hash SHA-256:

**Listado 14.** Extracción del cuerpo y cálculo del hash

```bash
$ openssl asn1parse -i -in c0.pem -strparse 4 \
    -out c0_body.bin -noout
$ sha256sum c0_body.bin
```

##### Paso 5 — Verificar la firma.

Ahora dispone de: la clave pública del emisor (e, n), la firma de la CA y el hash del cuerpo del certificado. Implemente un programa (en C o Python) que verifique si la firma es válida aplicando la operación m = firma^e mod n y comparando el resultado con el hash calculado. **No use `openssl verify` para esta verificación**; el objetivo es que el estudiante implemente la operación manualmente.

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

- **P1.** Explique el proceso matemático de generación de claves RSA (p, q, n, φ(n), e, d).
- **P2.** ¿Por qué RSA no se usa directamente para cifrar datos de gran tamaño? ¿Qué esquema híbrido se utiliza en la práctica?
- **P3.** Describa el proceso de autenticación SSH con clave pública. ¿Qué ventaja de seguridad ofrece frente a la autenticación con contraseña?
- **P4.** Explique qué información contiene un certificado X.509 y el rol de la CA en la cadena de confianza.
- **P5.** Al verificar manualmente el certificado, ¿qué relación matemática existe entre la firma, el hash y la clave pública de la CA?

## Actividad ABET — SO4: Responsabilidad Ética y Profesional

Esta actividad mide el **Student Outcome 4 (SO4)** de la Carrera de Telecomunicaciones requerido para la acreditación ABET: *habilidad para reconocer las responsabilidades éticas y profesionales en situaciones de ingeniería y emitir juicios fundamentados, considerando el impacto global, económico, medioambiental y social de las soluciones propuestas.* Representa el **30 %** de la valoración total de la práctica y evalúa los indicadores PI 4.1 y PI 4.2 mediante las preguntas SO4-1 y SO4-2.

- **SO4-1.** **[PI 4.1 — 15 %] Ética y responsabilidad profesional ante el descubrimiento de claves RSA débiles en hospitales públicos**
  Un investigador ecuatoriano descubre que un software de historia clínica electrónica usado por 30 hospitales públicos genera claves RSA de 512 bits con semilla predecible. El fabricante exige un NDA y promete corregirlo en 18 meses. Analice:

  - **a)** La **posición ética**: responsible disclosure vs. full disclosure vs. silencio.
  - **b)** Los **principios de salud pública y bienestar** que pesan en la decisión (datos de pacientes en riesgo).
  - **c)** El **marco legal ecuatoriano** (COIP Art. 229, LOPDP) y cómo equilibrar protección de datos con divulgación responsable.
- **SO4-2.** **[PI 4.2 — 15 %] Impacto integral de la rotura de claves RSA en la infraestructura digital ecuatoriana**
  La rotura de claves RSA de 1024 bits compromete los certificados SSL/TLS de 10 000 sitios web ecuatorianos (bancos, universidades, entidades gubernamentales). Analice:

  - **a)** **Económico:** costos de revocación/renovación masiva de certificados, pérdidas por intercepción.
  - **b)** **Social:** desconfianza en servicios digitales, acceso de terceros a comunicaciones privadas.
  - **c)** **Ambiental:** energía consumida en la regeneración masiva de claves y actualización de PKI.
  - **d)** **Contramedidas:** dos técnicas (RSA ≥3072 bits, ECDSA) y una política organizacional, citando NIST SP 800-57, RFC 8446 o ISO/IEC 9594.

## Discusión y conclusiones

A partir de los datos recolectados y del análisis realizado, elabore una discusión que responda al menos a las siguientes preguntas guía:

- **DC1.** ¿Se alcanzaron los objetivos planteados? Justifique cada uno con evidencia experimental concreta (capturas, métricas, salidas de comandos).
- **DC2.** ¿Qué limitaciones impone el entorno virtualizado a los resultados? ¿Cómo se trasladarían las observaciones a un escenario real de producción?
- **DC3.** ¿Qué contramedidas o controles de seguridad mitigan el ataque o refuerzan la defensa estudiada? Cite al menos una buena práctica de la industria, una RFC o un estándar (ISO/IEC, IEEE, NIST) pertinente.
- **DC4.** ¿Qué errores se cometieron durante la práctica y qué recomendaciones daría a futuros estudiantes para evitarlos?

Cierre con **conclusiones** (3–5 viñetas) que resuman los hallazgos principales y los vinculen explícitamente con los *Resultados de Aprendizaje* de la asignatura.

## Entregables

1. **Informe técnico** con capturas de pantalla de cada tarea, análisis de resultados y respuestas a las preguntas de análisis. Bibliografía IEEE (≥3 fuentes).
2. **Programa** (C o Python) que verifique manualmente la firma de un certificado X.509 usando la clave pública del emisor.
3. **Respuestas a la Actividad ABET – SO4** (preguntas SO4-1 y SO4-2), integradas en el informe técnico con extensión de 1–2 páginas por pregunta y las fuentes citadas según norma IEEE.

## Rúbrica de Evaluación

**Tabla 3.** Rúbrica — P-03 (10 puntos)

| Criterio | Peso | Indicador | Descripción |
| --- | --- | --- | --- |
| Operaciones OpenSSL | 18 % | Comandos correctos | Generación de claves, cifrado, descifrado y firma RSA sin errores. |
| SSH clave pública | 17 % | Conexión sin contraseña | Autenticación SSH con clave pública funcionando; archivo `config` configurado correctamente. |
| Verificación X.509 | 21 % | Hash y firma coinciden | Programa que extrae el cuerpo del certificado, calcula el hash y verifica la firma RSA de la CA. |
| Análisis | 14 % | Preguntas respondidas | Respuestas con fundamento teórico adecuado. |
| **ABET – SO4: Responsabilidad Ética y Profesional (30 %)** |   |   |   |
| PI 4.1 – Ética profesional | 15 % | Respuesta ética fundamentada | Aplica principios éticos y legales al escenario del incidente; la cadena de notificación está justificada. |
| PI 4.2 – Impacto integral | 15 % | Análisis de impacto | Evalúa impacto económico, social y ambiental con contramedidas técnicas y organizacionales, citando al menos un estándar internacional. |

**Tabla 4.** Escala ABET SO4 — P-03

| PI | No cumple<br>(0–59 %) | Cumple parcialmente<br>(60–69 %) | Cumple<br>(70–79 %) | Supera<br>(80–89 %) | Supera ampliamente<br>(90–100 %) |
| --- | --- | --- | --- | --- | --- |
| 4.1 | No aplica principios éticos ni profesionales al evaluar la situación de incidente. | Aplica de manera inconsistente los principios éticos; el análisis legal es superficial o erróneo. | Aplica de manera básica los principios éticos; menciona el marco legal ecuatoriano sin análisis profundo. | Aplica coherentemente su juicio ético y profesional; integra el COIP y la LOPDP con argumentación clara. | Aplica de manera ejemplar e integral su juicio ético; argumenta cada decisión con evidencia y normativas citadas con precisión. |
| 4.2 | No considera ninguno de los tres impactos (económico, social, ambiental). | Considera parcialmente uno o dos de los impactos; las contramedidas no citan estándares. | Considera los tres impactos de forma adecuada; propone contramedidas pertinentes con al menos un estándar citado. | Integra los tres impactos con análisis detallado y contramedidas bien fundamentadas en estándares internacionales. | Realiza una evaluación exhaustiva de los tres impactos; las contramedidas son innovadoras y se respaldan en múltiples estándares. |

## Referencias

1. Ylonen, Tatu and Lonvick, Chris, «The Secure Shell (SSH) Transport Layer Protocol». RFC 4253, 2006.
2. Cooper, David and others, «Internet X.509 Public Key Infrastructure Certificate and Certificate Revocation List (CRL) Profile». RFC 5280, 2008.
3. OpenSSL Project, «OpenSSL Cryptography and SSL/TLS Toolkit». 2024. <https://www.openssl.org>.

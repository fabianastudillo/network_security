<div align="center">

# P-02 · Criptografía de Clave Secreta

![Docker](https://img.shields.io/badge/Docker-Lab_Environment-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-Scripts-yellow?style=for-the-badge&logo=python)
![Security](https://img.shields.io/badge/Focus-Network_Security-critical?style=for-the-badge)

</div>

> Práctica del **Manual de Prácticas** de Seguridad en Redes · INGE-00107 · Universidad de Cuenca.  
> Documento generado desde el manual: no lo edite a mano (véase el [índice de prácticas](../README.md)).

> [!TIP]
> Apuntes de comandos del docente para esta práctica: [`NOTAS.md`](NOTAS.md).

| Campo | Valor |
| --- | --- |
| **Asignatura** | Seguridad en Redes |
| **Docente** | Dr. Fabián Astudillo-Salinas |
| **Unidad** | 300 – Criptografía de clave secreta |
| **Código** | INGE-00107 |
| **Modalidad** | Presencial |
| **Valoración** | 10 puntos |
| **Grupos** | Máx. 3 estudiantes |
| **Entrega** | Según calendario |
| **ABET** | SO4 – Responsabilidad Ética y Profesional (PI 4.1 y PI 4.2) — representa el 30 % de la valoración |

## Marco Teórico

Los fundamentos teóricos sintetizados en esta sección se basan en [1], [2]; se recomienda consultar dichas fuentes para una exposición más profunda.

### Cifrado de clave secreta

El **cifrado de clave secreta** (simétrico) usa la misma clave para cifrar y descifrar. Los algoritmos principales son DES (56 bits, obsoleto) y AES (128/192/256 bits, estándar actual).

### Modos de operación

**Tabla 1.** Modos de operación de cifrado por bloques

| Modo | Sigla | Características |
| --- | --- | --- |
| Electronic Codebook | ECB | Cada bloque cifrado independientemente; inseguro para datos con patrones |
| Cipher Block Chaining | CBC | XOR con el bloque cifrado anterior; necesita IV |
| Cipher Feedback | CFB | Convierte cifrado de bloque en flujo |
| Output Feedback | OFB | Genera keystream independiente del texto plano |
| Counter | CTR | Contador cifrado + XOR; paralelizable |

> [!NOTE]
> **Vector de Inicialización (IV)**
>
> El IV garantiza que dos mensajes iguales produzcan cifrados distintos. Debe ser aleatorio e impredecible; nunca debe reutilizarse con la misma clave.

**Objetivo general**
Explorar los conceptos clave de criptografía simétrica implementando cifrado y descifrado con distintos algoritmos y modos, y analizar vulnerabilidades derivadas de errores comunes de implementación.
**Objetivos específicos**

- **OE1.** Aplicar análisis de frecuencias para descifrar textos cifrados con cifrados monoalfabéticos.
- **OE2.** Implementar cifrado y descifrado con diferentes algoritmos y modos (AES, Blowfish, ECB, CBC, CFB, OFB) usando OpenSSL.
- **OE3.** Comparar los efectos de los modos ECB y CBC al cifrar imágenes BMP y demostrar visualmente la debilidad del modo ECB.
- **OE4.** Explorar el relleno (*padding*) PKCS#5 en cifrados por bloques y su efecto en el tamaño de los archivos cifrados.
- **OE5.** Analizar la propagación de errores en texto cifrado corrupto bajo distintos modos de operación.
- **OE6.** Entender los riesgos del reúso y la predecibilidad del IV, e implementar un ataque de texto en claro conocido sobre OFB.
- **OE7.** Explotar un IV predecible en modo CBC usando un oráculo de cifrado para revelar un mensaje secreto.

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
| SEED Ubuntu 20.04 VM | Máquina virtual del laboratorio SEED |
| Docker y Docker Compose | Para levantar el oráculo de cifrado (Tarea 6.3) |
| OpenSSL | Cifrado/descifrado por línea de comandos |
| Bless (editor hexadecimal) | Para editar bytes en archivos binarios |
| Python 3 | Scripts de análisis de frecuencias y XOR |
| GCC | Compilar programas con la biblioteca Crypto |
| `LabSetup` | Textos cifrados, imagen BMP, scripts y archivos Docker. Disponible en <https://github.com/fabianastudillo/network_security/tree/main/Secret_Key_Encryption> |

> [!NOTE]
> **Provisión de materiales**
>
> El estudiante adquiere o instala por su cuenta el equipo personal (laptop), las máquinas virtuales (VirtualBox, SEED VM, Kali Linux, contenedores Docker) y todo el software listado arriba. El laboratorio de la Carrera de Telecomunicaciones provee el espacio físico, el mobiliario y **acceso a Internet supervisado** para la descarga de imágenes, paquetes y consulta de documentación durante la sesión. El laboratorio no entrega equipos de cómputo personales ni licencias de software.

> [!NOTE]
> **Archivos del laboratorio**
>
> Descarga `Labsetup.zip` desde el repositorio del curso:
> <https://github.com/fabianastudillo/network_security/tree/main/Secret_Key_Encryption>
> Incluye: texto cifrado para análisis de frecuencias (uno por grupo), imagen `pic_original.bmp`, scripts `freq.py` y `sample_code.py`, lista de palabras en inglés y archivos Docker.

## Entorno de laboratorio

El contenedor Docker solo es necesario para la Tarea 6.3 (oráculo de cifrado). Para el resto de tareas no hace falta levantarlo.

##### Configuración del contenedor.

Descomprime `Labsetup.zip`, entra en la carpeta `Labsetup` y ejecuta:

```bash
docker-compose build   # Construir imagen del contenedor
docker-compose up -d   # Iniciar en segundo plano
docker-compose down    # Apagar el contenedor
```

Los alias preconfigurados en la VM SEEDUbuntu son:

```bash
dcbuild   # docker-compose build
dcup      # docker-compose up
dcdown    # docker-compose down
```

Para abrir una terminal dentro de un contenedor en ejecución:

```bash
dockps            # Lista contenedores: <id> <nombre>
docksh <id>       # Abre bash en el contenedor con ese ID
```

> [!NOTE]
> No es necesario escribir el ID completo del contenedor; basta con los primeros caracteres mientras sean únicos.

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

### Tarea 1 — Análisis de frecuencias

El cifrado monoalfabético sustituye cada letra siempre por la misma letra, lo que lo hace vulnerable al análisis de frecuencias. Se te proporciona un texto cifrado (uno diferente por grupo) en la carpeta compartida de la práctica. Tu objetivo es recuperar el texto original, que es un artículo en inglés.

##### Cómo se generó el texto cifrado.

1. Se generó una clave de sustitución permutando el alfabeto:

   ```bash
   echo {a..z} | sed 's/ /\n/g' | shuf | tr '\n' ' ' | sed 's/ //g'
   ```
2. Se preprocesó el artículo (minúsculas, sin puntuación ni números):

   ```bash
   tr [:upper:] [:lower:] < article.txt > lowercase.txt
   tr -cd '[a-z][\n][:space:]' < lowercase.txt > plaintext.txt
   ```
3. Se aplicó la sustitución con `tr`:

   ```bash
   tr 'abcdefghijklmnopqrstuvwxyz' 'sxtrwinqbedpvgkfmalhyuojzc' \
      < plaintext.txt > ciphertext.txt
   ```

##### Análisis de frecuencias con `freq.py`.

El script `freq.py` (en `Labsetup/Files`) calcula n-gramas del archivo `ciphertext.txt`:

```bash
$ ./freq.py
-------------------------------------
1-gram (top 20):
n: 488
y: 373
...
2-gram (top 20):
yt: 115
tn: 89
...
3-gram (top 20):
ytn: 78
vup: 30
...
```

##### Sustitución incremental.

A medida que identifiques letras con alta probabilidad, sustitúyelas por mayúsculas para distinguir texto en claro del texto cifrado:

```bash
tr 'aet' 'XGE' < in.txt > out.txt
```

> [!NOTE]
> **Recursos de referencia**
>
> - Frecuencias en inglés: <https://en.wikipedia.org/wiki/Frequency_analysis>
> - Bigramas: <https://en.wikipedia.org/wiki/Bigram>
> - Trigramas: <https://en.wikipedia.org/wiki/Trigram>

### Tarea 2 — Cifrado con diferentes algoritmos y modos

Usa el comando `openssl enc` para cifrar y descifrar un archivo. Prueba **al menos 3 cifrados distintos**, por ejemplo: `-aes-128-cbc`, `-bf-cbc`, `-aes-128-cfb`.

```bash
openssl enc -ciphertype -e -in plain.txt -out cipher.bin \
            -K  00112233445566778889aabbccddeeff \
            -iv 0102030405060708
```

Opciones principales del comando:

```
  -in  <file>   archivo de entrada
  -out <file>   archivo de salida
  -e            cifrar
  -d            descifrar
  -K/-iv        clave/IV en hexadecimal
  -[pP]         imprime el IV/clave (con -P solo imprime y sale)
```

Consulta `man enc` para ver todos los cifrados disponibles.

### Tarea 3 — Modo de cifrado: ECB vs. CBC

1. Cifra `pic_original.bmp` usando AES en modo ECB y en modo CBC.
2. Los primeros 54 bytes de un archivo BMP son la cabecera. Para poder visualizar la imagen cifrada, reemplaza la cabecera del archivo cifrado con la de la imagen original:

   ```bash
   head -c 54 pic_original.bmp > header
   tail -c +55 pic_ecb.bmp     > body
   cat header body > pic_ecb_view.bmp
   ```
3. Abre las imágenes resultantes con `eog` (visor de la VM):

   ```bash
   eog pic_ecb_view.bmp &
   ```
4. Responde: ¿Puedes deducir información de la imagen original a partir del cifrado ECB? ¿Y del CBC? Explica tus observaciones.
5. Repite el experimento con una imagen BMP de tu elección y reporta tus observaciones.

### Tarea 4 — Relleno (*padding*)

1. Cifra un mismo archivo con los modos ECB, CBC, CFB y OFB. ¿Qué modos añaden relleno y cuáles no? Justifica.
2. Crea tres archivos de 5, 10 y 16 bytes respectivamente:

   ```bash
   echo -n "12345"            > f1.txt   # 5 bytes
   echo -n "1234567890"       > f2.txt   # 10 bytes
   echo -n "1234567890123456" > f3.txt   # 16 bytes
   ```

   Cífralos con AES-128-CBC y reporta el tamaño de cada archivo cifrado.
3. Para observar el relleno PKCS#5 añadido, descifra los archivos con la opción `-nopad` (no elimina el relleno al descifrar) y muestra el resultado en hexadecimal:

   ```bash
   openssl enc -aes-128-cbc -d -nopad -in f1.enc -out f1_dec.bin -K <clave> -iv <iv>
   xxd f1_dec.bin
   ```

   Compara los bytes de relleno observados con la especificación PKCS#5: el valor de cada byte de relleno es igual al número de bytes añadidos.

### Tarea 5 — Propagación de errores en texto cifrado corrupto

Antes de ejecutar el experimento, **predice** cuánta información recuperarás al descifrar un archivo en el que el byte 55 del texto cifrado fue dañado (un solo bit cambiado), para cada uno de los modos ECB, CBC, CFB y OFB. Después verifica tus predicciones.

1. Crea un archivo de texto plano de al menos 1000 bytes.
2. Cífralo con AES-128 en cada uno de los modos indicados.
3. Usa `bless` para cambiar un bit del byte 55 en el archivo cifrado.
4. Descifra el archivo corrupto con la clave e IV originales y observa cuánto texto en claro se recupera correctamente.
5. Explica tus resultados comparando con la teoría de cada modo.

### Tarea 6 — Vector de inicialización (IV) y errores comunes

#### Tarea 6.1 — Unicidad del IV

Cifra el mismo texto en claro dos veces: una con IVs distintos y otra con el mismo IV. Describe las diferencias en el texto cifrado resultante y explica por qué el IV **nunca** debe reutilizarse bajo la misma clave.

#### Tarea 6.2 — Ataque con IV reutilizado (modo OFB)

En el modo OFB, si se usa el mismo IV con la misma clave, el flujo de clave (*keystream*) es idéntico. Dado que conoces `P1` y `C1`, puedes recuperar `P2` a partir de `C2`:

```
Texto en claro  (P1): This is a known message!
Texto cifrado   (C1): a469b1c502c1cab966965e50425438e1bb1b5f9037a4c159

Texto en claro  (P2): (desconocido)
Texto cifrado   (C2): bf73bcd3509299d566c35b5d450337e1bb175f903fafc159
```

Usa el script `sample_code.py` (en `Labsetup/Files`) que implementa XOR sobre cadenas ASCII y hexadecimales:

```python
def xor(first, second):
    return bytearray(x^y for x,y in zip(first, second))

MSG   = "A message"
HEX_1 = "aabbccddeeff1122334455"
HEX_2 = "1122334455778800aabbdd"

D1 = bytes(MSG, 'utf-8')
D2 = bytearray.fromhex(HEX_1)
D3 = bytearray.fromhex(HEX_2)

print(xor(D1, D2).hex())
print(xor(D2, D3).hex())
```

Responde también: si se usa CFB en lugar de OFB, ¿cuánto de `P2` puede revelarse?

#### Tarea 6.3 — IV predecible en modo CBC (oráculo)

Bob cifra mensajes con AES-128-CBC usando IVs predecibles. Eva sabe que el mensaje secreto es *Yes* o *No* y puede pedirle a Bob que cifre cualquier mensaje. Tu objetivo es determinar cuál es el mensaje secreto.

> [!WARNING]
> **Requiere Docker**
>
> Levanta el contenedor antes de esta tarea: `dcup`. Verifica con `dockps`.

Conéctate al oráculo:

```bash
nc 10.9.0.80 3000
```

Ejemplo de sesión:

```
Bob's secret message is either "Yes" or "No", without quotations.
Bob's ciphertext: 54601f27c6605da997865f62765117ce
The IV used    : d27d724f59a84d9b61c0f2883efa7bbc
Next IV        : d34c739f59a84d9b61c0f2883efa7bbc
Your plaintext : 11223344aabbccdd
Your ciphertext: 05291d3169b2921f08fe34449ddc3611
Next IV        : cd9f1ee659a84d9b61c0f2883efa7bbc
Your plaintext : <tu entrada>
```

El oráculo revela el *siguiente IV* antes de recibir tu texto en claro. Diseña un mensaje de prueba tal que, si el secreto es *Yes*, el texto cifrado resultante sea igual al texto cifrado del secreto de Bob. Explica detalladamente tu estrategia y muestra los cálculos.

## Recolección y análisis de datos

Durante la ejecución del procedimiento, registre en su bitácora los datos solicitados a continuación. Las tablas siguientes (o equivalentes en su informe) forman parte del entregable, conforme a la Sección [Directrices generales para el informe técnico](../README.md#directrices-generales-para-el-informe-técnico) (Directrices generales para el informe técnico).

**Tabla 2.** Bitácora de comandos y observaciones

| # | Comando / Acción | Salida u observación relevante |
| --- | --- | --- |
| 1 |   |   |
| 2 |   |   |
| 3 |   |   |
| 4 |   |   |
| 5 |   |   |

**Tabla 3.** Resultados clave / métricas obtenidas

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

- **P1.** ¿Por qué el modo ECB es inseguro para cifrar datos con patrones? Justifica con el resultado del experimento de la imagen BMP.
- **P2.** Explica la diferencia entre padding PKCS#5 y padding nulo. ¿Por qué algunos modos no requieren relleno?
- **P3.** ¿Cómo afecta un error de un bit en el byte 55 del texto cifrado a la recuperación del texto en claro en ECB, CBC, CFB y OFB? Compara teoría con los resultados experimentales.
- **P4.** ¿Por qué el IV debe ser aleatorio e impredecible? Ilustra con el ataque de la Tarea 6.3.
- **P5.** En la Tarea 6.2, ¿por qué con OFB se puede recuperar todo `P2` pero con CFB solo una parte? Explica matemáticamente.
- **P6.** Compare AES-128 y AES-256: diferencias en seguridad, número de rondas y rendimiento.

## Actividad ABET — SO4: Responsabilidad Ética y Profesional

Esta actividad mide el **Student Outcome 4 (SO4)** de la Carrera de Telecomunicaciones requerido para la acreditación ABET: *habilidad para reconocer las responsabilidades éticas y profesionales en situaciones de ingeniería y emitir juicios fundamentados, considerando el impacto global, económico, medioambiental y social de las soluciones propuestas.* Representa el **30 %** de la valoración total de la práctica y evalúa los indicadores PI 4.1 y PI 4.2 mediante las preguntas SO4-1 y SO4-2.

- **SO4-1.** **[PI 4.1 — 15 %] Ética y responsabilidad profesional ante el uso de cifrado obsoleto en banca**
  Un ingeniero audita un banco regional ecuatoriano y descubre que su aplicación de banca móvil usa cifrado DES (56 bits) para transacciones. El banco se niega a actualizar argumentando que ``nunca ha habido problemas''. Analice:

  - **a)** Las **responsabilidades éticas y profesionales** del ingeniero ante esta situación.
  - **b)** Los **principios de no maleficencia, beneficencia y transparencia** que obligan a revelar el riesgo.
  - **c)** El **marco legal** (LOPDP, responsabilidad civil) si el banco sufre una brecha y se demuestra que el ingeniero conocía la vulnerabilidad y no la reportó formalmente.
- **SO4-2.** **[PI 4.2 — 15 %] Impacto integral de un ataque de fuerza bruta sobre DES en un banco ecuatoriano**
  Un ataque de fuerza bruta exitoso sobre el cifrado DES de un banco regional ecuatoriano expone 50 000 transacciones de clientes durante 12 horas. Analice:

  - **a)** **Económico:** costos de fraude, multas de la Superintendencia de Bancos, migración a cifrado seguro.
  - **b)** **Social:** pérdida de confianza, riesgo de robo de identidad, inequidad de acceso a servicios seguros.
  - **c)** **Ambiental:** energía consumida en la respuesta al incidente y en la migración de sistemas legados.
  - **d)** **Contramedidas:** dos técnicas (AES-256, TLS 1.3) y una política organizacional, citando FIPS 197, RFC 8446 o ISO/IEC 18033.

## Discusión y conclusiones

A partir de los datos recolectados y del análisis realizado, elabore una discusión que responda al menos a las siguientes preguntas guía:

- **DC1.** ¿Se alcanzaron los objetivos planteados? Justifique cada uno con evidencia experimental concreta (capturas, métricas, salidas de comandos).
- **DC2.** ¿Qué limitaciones impone el entorno virtualizado a los resultados? ¿Cómo se trasladarían las observaciones a un escenario real de producción?
- **DC3.** ¿Qué contramedidas o controles de seguridad mitigan el ataque o refuerzan la defensa estudiada? Cite al menos una buena práctica de la industria, una RFC o un estándar (ISO/IEC, IEEE, NIST) pertinente.
- **DC4.** ¿Qué errores se cometieron durante la práctica y qué recomendaciones daría a futuros estudiantes para evitarlos?

Cierre con **conclusiones** (3–5 viñetas) que resuman los hallazgos principales y los vinculen explícitamente con los *Resultados de Aprendizaje* de la asignatura.

## Entregables

1. **Informe técnico** con resultados de cada tarea, código fuente comentado, capturas de pantalla y análisis de resultados. Bibliografía IEEE (≥3 fuentes).
2. **Código Python** del ataque de texto plano conocido (Tarea 6.2) y del ataque al oráculo (Tarea 6.3).
3. **Respuestas a la Actividad ABET – SO4** (preguntas SO4-1 y SO4-2), integradas en el informe técnico con extensión de 1–2 páginas por pregunta y las fuentes citadas según norma IEEE.

## Rúbrica de Evaluación

**Tabla 4.** Rúbrica — P-02 (10 puntos)

| Criterio | Peso | Nivel alto (9–10) | Nivel medio (6–8) / bajo (0–5) |
| --- | --- | --- | --- |
| Análisis de frecuencias (T1) | 11 % | Descifra el texto completo con justificación del proceso | Descifra parcialmente / sin justificación |
| Cifrado con OpenSSL (T2) | 10 % | Prueba ≥3 cifrados, documenta parámetros y resultados | Prueba menos de 3 o sin análisis comparativo |
| ECB vs. CBC – imagen (T3) | 11 % | Demuestra visualmente la debilidad del ECB; explica la diferencia | Genera imágenes sin análisis o con análisis superficial |
| Padding y propagación (T4–T5) | 10 % | Observa y explica correctamente relleno y propagación de errores | Resultados sin justificación teórica |
| Ataques con IV (T6) | 14 % | Implementa los ataques OFB y CBC con cálculos correctos | Implementación parcial o errónea |
| Informe y presentación | 14 % | Informe bien estructurado, conclusiones fundamentadas, responde preguntas con precisión | Informe incompleto o con conclusiones insuficientes |
| **ABET – SO4: Responsabilidad Ética y Profesional (30 %)** |   |   |   |
| PI 4.1 – Ética profesional | 15 % | Aplica principios éticos y legales al escenario del incidente; la cadena de notificación está justificada. | Análisis ético superficial o incompleto; no referencia el marco legal ecuatoriano. |
| PI 4.2 – Impacto integral | 15 % | Evalúa impacto económico, social y ambiental con contramedidas técnicas y organizacionales, citando al menos un estándar internacional. | Considera uno o dos impactos; contramedidas sin referencia a estándares. |

**Tabla 5.** Escala ABET SO4 — P-02

| PI | No cumple<br>(0–59 %) | Cumple parcialmente<br>(60–69 %) | Cumple<br>(70–79 %) | Supera<br>(80–89 %) | Supera ampliamente<br>(90–100 %) |
| --- | --- | --- | --- | --- | --- |
| 4.1 | No aplica principios éticos ni profesionales al evaluar la situación de incidente. | Aplica de manera inconsistente los principios éticos; el análisis legal es superficial o erróneo. | Aplica de manera básica los principios éticos; menciona el marco legal ecuatoriano sin análisis profundo. | Aplica coherentemente su juicio ético y profesional; integra el COIP y la LOPDP con argumentación clara. | Aplica de manera ejemplar e integral su juicio ético; argumenta cada decisión con evidencia y normativas citadas con precisión. |
| 4.2 | No considera ninguno de los tres impactos (económico, social, ambiental). | Considera parcialmente uno o dos de los impactos; las contramedidas no citan estándares. | Considera los tres impactos de forma adecuada; propone contramedidas pertinentes con al menos un estándar citado. | Integra los tres impactos con análisis detallado y contramedidas bien fundamentadas en estándares internacionales. | Realiza una evaluación exhaustiva de los tres impactos; las contramedidas son innovadoras y se respaldan en múltiples estándares. |

## Referencias

1. Du, Wenliang, «Computer & Internet Security: A Hands-on Approach». Independently published, 2019.
2. OpenSSL Project, «OpenSSL Cryptography and SSL/TLS Toolkit». 2024. <https://www.openssl.org>.

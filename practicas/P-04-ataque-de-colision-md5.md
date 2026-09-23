# P-04 · Ataque de Colisión MD5

> Práctica del **Manual de Prácticas** de Seguridad en Redes · INGE-00107 · Universidad de Cuenca.  
> Documento generado desde el manual: no lo edite a mano (véase [`practicas/README.md`](README.md)).

| Campo | Valor |
| --- | --- |
| **Asignatura** | Seguridad en Redes |
| **Docente** | Dr. Fabián Astudillo-Salinas |
| **Unidad** | 400 – Funciones hash de una vía |
| **Código** | INGE-00107 |
| **Modalidad** | Presencial |
| **Valoración** | 10 puntos |
| **Grupos** | Máx. 3 estudiantes |
| **Entrega** | Según calendario |
| **ABET** | SO4 – Responsabilidad Ética y Profesional (PI 4.1 y PI 4.2) — representa el 30 % de la valoración |

## Marco Teórico

Los fundamentos teóricos sintetizados en esta sección se basan en [1], [2]; se recomienda consultar dichas fuentes para una exposición más profunda.

### Funciones hash unidireccionales

Una función hash segura debe satisfacer dos propiedades fundamentales: la **propiedad unidireccional** (*one-way property*) y la **propiedad de resistencia a colisiones** (*collision-resistance property*).

La propiedad unidireccional garantiza que, dado un valor hash h, es computacionalmente inviable encontrar una entrada M tal que hash(M) = h. La propiedad de resistencia a colisiones garantiza que es computacionalmente inviable encontrar dos entradas distintas M_1 y M_2 tales que hash(M_1) = hash(M_2).

### Colisiones en MD5

En la sesión rump del congreso CRYPTO 2004, Xiaoyun Wang y coautores demostraron un ataque de colisión contra MD5. En febrero de 2017, CWI Amsterdam y Google Research anunciaron el ataque *SHAttered*, que rompe la resistencia a colisiones de SHA-1. Estas vulnerabilidades demuestran que MD5 y SHA-1 **no deben utilizarse** en aplicaciones donde la integridad criptográfica sea crítica.

### Arquitectura iterativa de MD5 y propiedad de sufijo

MD5 divide la entrada en bloques de 64 bytes y calcula el hash de forma iterativa mediante una función de compresión que combina cada bloque con el Valor Hash Intermedio (IHV) de la iteración anterior. El IHV de la primera iteración (IHV_0) es un valor fijo; el IHV final es el hash resultante. La Figura 1 ilustra este proceso.

> **Figura 1.** Funcionamiento del algoritmo MD5: cadena iterativa de funciones de compresión.  
> *(diagrama vectorial; se reproduce en el PDF del manual)*

Esta arquitectura genera la siguiente propiedad fundamental:

> [!NOTE]
> **Propiedad de sufijo de MD5**
>
> Si MD5(M) = MD5(N), entonces para cualquier cadena T: MD5(M ‖ T) = MD5(N ‖ T) donde ‖ denota concatenación. Agregar el mismo sufijo a dos mensajes con igual hash MD5 produce dos salidas con el mismo hash.

**Objetivo general**
Demostrar el impacto real de los ataques de colisión contra MD5, generando archivos y programas ejecutables que comparten el mismo hash MD5 pero tienen contenidos o comportamientos distintos.
**Objetivos específicos**

- **OE1.** Utilizar la herramienta `md5collgen` para producir dos archivos distintos con el mismo hash MD5.
- **OE2.** Verificar y explotar la propiedad de sufijo de MD5 mediante experimentos prácticos.
- **OE3.** Construir dos ejecutables con el mismo hash MD5 pero diferente contenido en su arreglo de datos.
- **OE4.** Diseñar dos programas con comportamientos opuestos (benigno/malicioso) que compartan el mismo hash MD5.

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
| SEED Ubuntu 20.04 VM | Entorno de laboratorio con `md5collgen` preinstalado |
| `md5collgen` | Herramienta de generación rápida de colisiones MD5 (Marc Stevens). Binario en `/usr/bin/md5collgen`; fuentes en <https://www.win.tue.nl/hashclash/> |
| `bless` | Editor hexadecimal (preinstalado en la VM SEED) |
| `md5sum` | Utilidad de línea de comandos para calcular hashes MD5 |
| GCC | Compilador C para las Tareas 3 y 4 |

> [!NOTE]
> **Provisión de materiales**
>
> El estudiante adquiere o instala por su cuenta el equipo personal (laptop), las máquinas virtuales (VirtualBox, SEED VM, Kali Linux, contenedores Docker) y todo el software listado arriba. El laboratorio de la Carrera de Telecomunicaciones provee el espacio físico, el mobiliario y **acceso a Internet supervisado** para la descarga de imágenes, paquetes y consulta de documentación durante la sesión. El laboratorio no entrega equipos de cómputo personales ni licencias de software.

> [!NOTE]
> **md5collgen fuera de la VM SEED**
>
> Si trabaja en su propia máquina y `md5collgen` no está disponible, descargue el código fuente desde <https://www.win.tue.nl/hashclash/> o instale el paquete `md5deep` que incluye herramientas compatibles.

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

### Tarea 1 — Dos archivos distintos con el mismo hash MD5

El programa `md5collgen` acepta un archivo de prefijo arbitrario y produce dos salidas (`out1.bin` y `out2.bin`) que comparten el prefijo seguido de relleno y un bloque de colisión de 128 bytes. La Figura 2 ilustra el proceso.

> **Figura 2.** Generación de colisión MD5 a partir de un prefijo con `md5collgen`.  
> *(diagrama vectorial; se reproduce en el PDF del manual)*

1. Cree un archivo de prefijo con contenido arbitrario:

   **Listado 1.** Crear el prefijo

   ```bash
   echo "Prefijo de prueba para colision MD5" > prefix.txt
   ```
2. Genere los dos archivos con colisión de hash:

   **Listado 2.** Generar colisión MD5

   ```bash
   md5collgen -p prefix.txt -o out1.bin out2.bin
   ```
3. Verifique que los archivos son distintos pero comparten el mismo hash:

   **Listado 3.** Verificar diferencia y hash MD5

   ```bash
   diff out1.bin out2.bin
   md5sum out1.bin
   md5sum out2.bin
   ```
4. Abra ambos archivos en `bless` y describa las diferencias a nivel hexadecimal.

> [!WARNING]
> **Tamaño del prefijo**
>
> Si la longitud del prefijo no es múltiplo de 64 bytes, `md5collgen` agrega relleno automáticamente antes de generar el bloque de colisión. Experimente con un prefijo de exactamente 64 bytes y observe qué cambia en la salida.

### Tarea 2 — Propiedad de sufijo de MD5

Esta tarea demuestra experimentalmente que si dos archivos tienen el mismo hash MD5, agregar el mismo sufijo a ambos produce dos nuevos archivos que también tienen el mismo hash MD5.

1. Use `out1.bin` y `out2.bin` de la Tarea 1 como punto de partida.
2. Cree un sufijo común:

   **Listado 4.** Crear sufijo común

   ```bash
   echo "Sufijo comun para ambos archivos" > suffix.txt
   ```
3. Concatene el sufijo a cada archivo y verifique que el hash MD5 se mantiene igual:

   **Listado 5.** Aplicar sufijo y verificar hash

   ```bash
   cat out1.bin suffix.txt > combined1.bin
   cat out2.bin suffix.txt > combined2.bin
   md5sum combined1.bin
   md5sum combined2.bin
   ```
4. Diseñe su propio experimento adicional que confirme esta propiedad con un sufijo diferente y reporte sus observaciones.

### Tarea 3 — Dos ejecutables con el mismo hash MD5

En esta tarea construirá dos versiones de un programa en C cuyos ejecutables compilados comparten el mismo hash MD5, pero cuyo arreglo `xyz` tiene contenidos distintos (y por tanto producen salidas diferentes).

##### Programa base.

**Listado 6.** Programa base con arreglo xyz

```c
#include <stdio.h>

unsigned char xyz[200] = {
  /* Rellene con valores de su eleccion */
};

int main() {
  int i;
  for (i = 0; i < 200; i++) {
    printf("
  }
  printf("\n");
  return 0;
}
```

Rellene `xyz` con un valor localizable en el binario (p. ej. `0x41`, el código ASCII de `A`):

**Listado 7.** Arreglo relleno con 0x41 para facilitar su localización en el binario

```c
unsigned char xyz[200] = {
  0x41, 0x41, 0x41, 0x41, 0x41, 0x41, 0x41, 0x41, 0x41, 0x41,
  /* ... repetir hasta completar 200 elementos ... */
};
```

##### Procedimiento de generación.

El ejecutable compilado se divide en tres partes: un prefijo (múltiplo de 64 bytes), una región de 128 bytes (donde reside el arreglo) y un sufijo (el resto del programa). Ver Figura 3.

> **Figura 3.** División del ejecutable en prefijo, región de colisión (128 bytes) y sufijo.  
> *(diagrama vectorial; se reproduce en el PDF del manual)*

1. Compile el programa:

   **Listado 8.** Compilar el programa base

   ```bash
   gcc -o a.out prog.c
   ```
2. Localice con `bless` la posición del bloque de 200 bytes `0x41` en el binario. Anote el desplazamiento de inicio (debe ser múltiplo de 64) y llámelo `N`.
3. Extraiga el prefijo y el sufijo:

   **Listado 9.** Dividir el ejecutable en prefijo y sufijo

   ```bash
   head -c <N>       a.out > prefix
   tail -c +<N+129>  a.out > suffix
   ```
4. Genere los dos bloques de colisión a partir del prefijo:

   **Listado 10.** Generar bloques P y Q para el ejecutable

   ```bash
   md5collgen -p prefix -o P Q
   ```
5. Ensamble dos ejecutables completos:

   **Listado 11.** Ensamblar y verificar los ejecutables

   ```bash
   cat P suffix > prog1.out
   cat Q suffix > prog2.out
   chmod +x prog1.out prog2.out
   md5sum prog1.out prog2.out
   ./prog1.out
   ./prog2.out
   ```

Las herramientas `head` y `tail` son útiles para dividir archivos binarios. Algunos ejemplos:

**Listado 12.** Uso de head y tail para dividir archivos binarios

```bash
head -c 3200  a.out > prefix      # primeros 3200 bytes
tail -c 100   a.out > suffix      # ultimos 100 bytes
tail -c +3301 a.out > suffix      # desde el byte 3301 en adelante
```

### Tarea 4 — Programas con comportamientos distintos

Esta tarea lleva la Tarea 3 al escenario de un ataque real: dos programas que ejecutan **ramas de código completamente diferentes** (una benigna y otra maliciosa) con el mismo hash MD5.

##### Concepto del ataque.

Usted desarrolla software benigno y lo envía a certificación. La autoridad lo valida e incluye su hash MD5 en el certificado. Como su programa malicioso comparte ese hash, el certificado también es válido para él: quien confíe en el certificado descargará el programa malicioso creyendo que es el original.

##### Diseño del programa.

Use dos arreglos `X` e `Y`: si sus contenidos son iguales se ejecuta el código benigno; si difieren, el malicioso.

**Listado 13.** Estructura del programa benigno/malicioso

```c
#include <stdio.h>
#include <string.h>

unsigned char X[200] = { 0x41, /* ... 200 bytes ... */ };
unsigned char Y[200] = { 0x41, /* ... 200 bytes ... */ };

int main() {
  if (memcmp(X, Y, 200) == 0) {
    printf("Comportamiento BENIGNO: todo en orden.\n");
  } else {
    printf("Comportamiento MALICIOSO: accion no autorizada.\n");
  }
  return 0;
}
```

##### Estrategia de colisión.

El ejecutable se divide en cuatro partes: prefijo → arreglo `X` (128 bytes de colisión) → sección intermedia → arreglo `Y` (128 bytes de colisión) → sufijo.

- **Versión benigna:** `X` = `Y` = P ⇒ `memcmp` retorna 0 ⇒ código benigno.
- **Versión maliciosa:** `X` = P, `Y` = Q (con P ≠ Q) ⇒ `memcmp` retorna distinto de 0 ⇒ código malicioso.

Ambas versiones tienen el mismo hash MD5 gracias a la propiedad de sufijo. La Figura 4 ilustra la estructura binaria de ambas versiones.

> **Figura 4.** Estructura de los dos programas con comportamientos distintos y el mismo hash MD5.  
> *(diagrama vectorial; se reproduce en el PDF del manual)*

> [!WARNING]
> **Solo con fines educativos**
>
> El código ``malicioso'' debe limitarse a imprimir un mensaje diferente o realizar una acción completamente inocua. Bajo ninguna circunstancia implemente código destructivo real. El objetivo es demostrar el concepto, no crear *malware*.

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

- **P1.** ¿Por qué MD5 ya no se considera seguro como función hash criptográfica? ¿Qué alternativas recomienda el NIST (p. ej. SHA-256, SHA-3)?
- **P2.** Explique la diferencia entre una *colisión de prefijo elegido* (*chosen-prefix collision*) y una colisión ordinaria. ¿Por qué la primera es más peligrosa en la práctica?
- **P3.** En la Tarea 1, ¿cuántos bytes exactamente difieren entre `out1.bin` y `out2.bin`? ¿Por qué precisamente esos bytes?
- **P4.** Describa un escenario real en el que un atacante podría usar un ataque de colisión MD5 para comprometer un sistema de distribución de software firmado digitalmente.
- **P5.** ¿Por qué SHA-256 o SHA-3 son resistentes a los mismos ataques que afectan a MD5? Explique en términos de longitud del hash y complejidad computacional del ataque.

## Actividad ABET — SO4: Responsabilidad Ética y Profesional

Esta actividad mide el **Student Outcome 4 (SO4)** de la Carrera de Telecomunicaciones requerido para la acreditación ABET: *habilidad para reconocer las responsabilidades éticas y profesionales en situaciones de ingeniería y emitir juicios fundamentados, considerando el impacto global, económico, medioambiental y social de las soluciones propuestas.* Representa el **30 %** de la valoración total de la práctica y evalúa los indicadores PI 4.1 y PI 4.2 mediante las preguntas SO4-1 y SO4-2.

- **SO4-1.** **[PI 4.1 — 15 %] Ética y responsabilidad profesional ante el uso de MD5 en sistemas de contratación pública**
  Un ingeniero descubre que el sistema de firma digital del Servicio Nacional de Contratación Pública (SERCOP) usa MD5 para verificar la integridad de contratos. El responsable de TI minimiza el riesgo. Analice:

  - **a)** La **responsabilidad ética** del ingeniero para escalar el reporte (cadena de notificación, organismos reguladores como el MINTEL o la ARCOTEL).
  - **b)** Los **principios éticos** que justifican la insistencia en corregir la vulnerabilidad (responsabilidad profesional, interés público).
  - **c)** Las **consecuencias legales** bajo el COIP y la legislación de contratación pública si se produjera una falsificación explotando esta vulnerabilidad.
- **SO4-2.** **[PI 4.2 — 15 %] Impacto integral de una colisión MD5 en una licitación pública**
  Un atacante explota colisiones MD5 para crear un par de documentos —contrato legítimo y fraudulento— con el mismo hash, logrando que una firma digital válida sea aceptada para el contrato fraudulento en una licitación pública por USD 5 millones. Analice:

  - **a)** **Económico:** pérdidas directas por fraude, costos de investigación forense y litigios, paralización de procesos de contratación.
  - **b)** **Social:** erosión de la confianza en los sistemas digitales del Estado, afectación de licitaciones legítimas y competidores honestos.
  - **c)** **Ambiental:** energía consumida en la auditoría masiva de contratos digitales existentes.
  - **d)** **Contramedidas:** dos técnicas (SHA-3, SHA-256) y una política organizacional, citando FIPS 202, RFC 6151 o ISO/IEC 10118.

## Discusión y conclusiones

A partir de los datos recolectados y del análisis realizado, elabore una discusión que responda al menos a las siguientes preguntas guía:

- **DC1.** ¿Se alcanzaron los objetivos planteados? Justifique cada uno con evidencia experimental concreta (capturas, métricas, salidas de comandos).
- **DC2.** ¿Qué limitaciones impone el entorno virtualizado a los resultados? ¿Cómo se trasladarían las observaciones a un escenario real de producción?
- **DC3.** ¿Qué contramedidas o controles de seguridad mitigan el ataque o refuerzan la defensa estudiada? Cite al menos una buena práctica de la industria, una RFC o un estándar (ISO/IEC, IEEE, NIST) pertinente.
- **DC4.** ¿Qué errores se cometieron durante la práctica y qué recomendaciones daría a futuros estudiantes para evitarlos?

Cierre con **conclusiones** (3–5 viñetas) que resuman los hallazgos principales y los vinculen explícitamente con los *Resultados de Aprendizaje* de la asignatura.

## Entregables

1. **Informe técnico en PDF**: descripción del procedimiento, capturas de pantalla de cada tarea, análisis de resultados, respuestas a las preguntas y bibliografía IEEE (≥3 fuentes).
2. **Artefactos**: `out1.bin` y `out2.bin` de la Tarea 1; ejecutables colisionantes de la Tarea 3; par benigno/malicioso de la Tarea 4.
3. **Respuestas a la Actividad ABET – SO4** (preguntas SO4-1 y SO4-2), integradas en el informe técnico con extensión de 1–2 páginas por pregunta y las fuentes citadas según norma IEEE.

## Rúbrica de Evaluación

1.4

**Tabla 3.** Rúbrica — P-04 (10 puntos)

| Criterio | Peso | Indicador | Descripción |
| --- | --- | --- | --- |
| Tarea 1 | 14 % | Colisión generada | Dos archivos con el mismo MD5 verificados con `md5sum`; bytes distintos identificados en `bless`. |
| Tarea 2 | 11 % | Propiedad de sufijo | Experimento diseñado y ejecutado correctamente; hash idéntico tras agregar el sufijo. |
| Tarea 3 | 21 % | Ejecutables colisionantes | Dos ejecutables con el mismo MD5 y salidas distintas; proceso documentado paso a paso. |
| Tarea 4 | 14 % | Comportamiento dual | Par benigno/malicioso funcional con el mismo hash MD5; estrategia de colisión explicada. |
| Análisis | 10 % | Preguntas respondidas | Respuestas con profundidad técnica y referencias adecuadas. |
| **ABET – SO4: Responsabilidad Ética y Profesional (30 %)** |   |   |   |
| PI 4.1 – Ética profesional | 15 % | Respuesta ética fundamentada | Aplica principios éticos y legales al escenario del incidente; la cadena de notificación está justificada. |
| PI 4.2 – Impacto integral | 15 % | Análisis de impacto | Evalúa impacto económico, social y ambiental con contramedidas técnicas y organizacionales, citando al menos un estándar internacional. |

1.25

**Tabla 4.** Escala ABET SO4 — P-04

| PI | No cumple<br>(0–59 %) | Cumple parcialmente<br>(60–69 %) | Cumple<br>(70–79 %) | Supera<br>(80–89 %) | Supera ampliamente<br>(90–100 %) |
| --- | --- | --- | --- | --- | --- |
| 4.1 | No aplica principios éticos ni profesionales al evaluar la situación de incidente. | Aplica de manera inconsistente los principios éticos; el análisis legal es superficial o erróneo. | Aplica de manera básica los principios éticos; menciona el marco legal ecuatoriano sin análisis profundo. | Aplica coherentemente su juicio ético y profesional; integra el COIP y la LOPDP con argumentación clara. | Aplica de manera ejemplar e integral su juicio ético; argumenta cada decisión con evidencia y normativas citadas con precisión. |
| 4.2 | No considera ninguno de los tres impactos (económico, social, ambiental). | Considera parcialmente uno o dos de los impactos; las contramedidas no citan estándares. | Considera los tres impactos de forma adecuada; propone contramedidas pertinentes con al menos un estándar citado. | Integra los tres impactos con análisis detallado y contramedidas bien fundamentadas en estándares internacionales. | Realiza una evaluación exhaustiva de los tres impactos; las contramedidas son innovadoras y se respaldan en múltiples estándares. |

## Referencias

1. Wang, Xiaoyun and Yu, Hongbo, «How to Break MD5 and Other Hash Functions». Springer, Advances in Cryptology -- EUROCRYPT 2005, 2005.
2. Stevens, Marc, «On Collisions for MD5». 2007.

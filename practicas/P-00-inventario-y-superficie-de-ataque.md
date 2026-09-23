# P-00 · Inventario y Superficie de Ataque

> Práctica del **Manual de Prácticas** de Seguridad en Redes · INGE-00107 · Universidad de Cuenca.  
> Documento generado desde el manual: no lo edite a mano (véase el [índice de prácticas](README.md)).

| Campo | Valor |
| --- | --- |
| **Asignatura** | Seguridad en Redes |
| **Docente** | Dr. Fabián Astudillo-Salinas |
| **Unidad** | 100 – Introducción a la seguridad de redes |
| **Código** | INGE-00107 |
| **Modalidad** | Presencial |
| **Valoración** | 10 puntos |
| **Grupos** | Máx. 3 estudiantes |
| **Entrega** | Según calendario |
| **ABET** | SO4 – Responsabilidad Ética y Profesional (PI 4.1 y PI 4.2) — representa el 30 % de la valoración |

## Marco Teórico

### Qué es la superficie de ataque

La **superficie de ataque** de un sistema es el conjunto de puntos por los que un atacante puede intentar entrar o extraer información: puertos abiertos, servicios expuestos, interfaces de administración, credenciales por defecto y cuentas con más privilegios de los necesarios. Reducirla es la medida de seguridad más barata que existe, porque lo que no está expuesto no se ataca.

El inventario es el paso previo: no se puede proteger lo que no se sabe que existe. Los marcos de referencia lo ponen primero por esa razón — la función *Identify* del NIST Cybersecurity Framework 2.0 y el primer control del CIS Controls v8 son, literalmente, inventariar activos y software.

### Las tres propiedades y el no repudio

Toda decisión de seguridad se justifica contra una de estas propiedades:

- **Confidencialidad**: solo accede quien debe. La rompe una captura pasiva o un directorio expuesto.
- **Integridad**: el dato llega como salió. La rompe una modificación en tránsito o un binario alterado.
- **Disponibilidad**: el servicio responde cuando se lo necesita. La rompe una denegación de servicio.
- **No repudio**: quien actuó no puede negarlo. Necesita firma y registro auditable.

### Riesgo: impacto por probabilidad

El riesgo no es la vulnerabilidad: es la combinación del impacto de que algo ocurra con la probabilidad de que ocurra. Frente a cada riesgo hay cuatro tratamientos posibles —mitigar, transferir, aceptar o evitar— y la decisión se documenta. «Ignorar» no es una de ellas.

### Herramientas de inventario

| Herramienta | Para qué |
| --- | --- |
| `nmap -sn` | Descubrir hosts vivos sin escanear puertos |
| `nmap -sV` | Identificar servicios y versiones |
| `ss -tulpn` | Ver qué escucha en el propio equipo y qué proceso lo abre |
| `systemctl` | Servicios activos y habilitados al arranque |
| `ip a`, `ip r` | Interfaces, direcciones y rutas |

**Objetivo general**
Levantar el inventario de activos y servicios de una red propia, estimar el riesgo asociado y proponer una reducción de la superficie de ataque.

**Objetivos específicos**

- **OE1.** Descubrir los hosts activos de la red del laboratorio y documentarlos.
- **OE2.** Identificar servicios, versiones y puertos expuestos en cada host.
- **OE3.** Determinar qué escucha en el propio equipo y qué proceso lo abre.
- **OE4.** Construir una matriz de riesgo con impacto, probabilidad y tratamiento.
- **OE5.** Proponer y verificar al menos dos medidas de reducción de superficie.

## Actividades previas

Antes de la sesión de laboratorio, cada estudiante debe completar las siguientes actividades preparatorias:

- **AP1.** Leer el marco teórico de esta práctica y repasar la unidad 100 del curso.
- **AP2.** Verificar que el entorno virtual (VMs SEED/Kali y red NAT) esté operativo conforme al capítulo *Configuración del Entorno: SEED VM en VirtualBox*.
- **AP3.** Tomar una *snapshot* del estado inicial de cada VM.
- **AP4.** Revisar la Sección [Seguridad y normas generales del laboratorio](00-normas-generales.md#seguridad-y-normas-generales-del-laboratorio) (Seguridad y normas generales del laboratorio).
- **AP5.** Preparar la bitácora digital para registrar comandos y observaciones.

## Materiales y Equipos

| Recurso | Descripción |
| --- | --- |
| SEED VM / Kali Linux | VM desde la que se inventaría |
| Segunda VM o contenedor | Objetivo del inventario, en la misma red NAT |
| Nmap ≥ 7.9 | Descubrimiento de hosts y servicios |
| `iproute2` (`ss`, `ip`) | Inventario local |
| Hoja de cálculo | Registro del inventario y de la matriz de riesgo |

> [!WARNING]
> **Solo sobre redes propias**
>
> El inventario se hace **únicamente** sobre las máquinas virtuales del laboratorio o sobre la red doméstica del estudiante. Escanear la red de la universidad, de un proveedor o de un tercero sin autorización escrita está tipificado en los Arts. 229 y 234 del COIP.

## Consideraciones de seguridad

Antes de iniciar el procedimiento, revise la Sección [Seguridad y normas generales del laboratorio](00-normas-generales.md#seguridad-y-normas-generales-del-laboratorio). Adicionalmente:

- El escaneo se limita al rango de la red NAT del laboratorio o a la red propia del estudiante.
- Los resultados pueden revelar servicios vulnerables de equipos personales: se anonimiza cualquier dirección que no sea del laboratorio antes de entregarlos.
- No se intenta acceder a ningún servicio descubierto; esta práctica es de reconocimiento, no de explotación.

## Procedimiento

### Paso 1 — Descubrimiento de hosts

1. Determine el rango de la red NAT con `ip a` e `ip r`.
2. Ejecute `sudo nmap -sn 10.9.0.0/24` (ajuste el rango) y anote los hosts vivos con su MAC y fabricante.
3. Repita con `-PR` (ARP ping) y compare: ¿aparecen los mismos hosts? Explique la diferencia.

### Paso 2 — Servicios y versiones

1. Sobre cada host descubierto, ejecute `sudo nmap -sV -p- --open <host>`.
2. Registre puerto, protocolo, servicio, versión y estado en la Tabla 1.
3. Para cada servicio, indique si es necesario para la función del host o si está ahí por omisión.

### Paso 3 — Inventario local

1. En su propia VM ejecute `ss -tulpn` y `systemctl list-units --type=service --state=running`.
2. Contraste lo que ve desde fuera (Paso 2) con lo que ve desde dentro: ¿hay servicios escuchando solo en `127.0.0.1`? ¿Alguno escucha en `0.0.0.0` sin necesidad?

### Paso 4 — Matriz de riesgo

Para los cinco servicios más expuestos, complete la Tabla 2: amenaza asociada, impacto (alto/medio/bajo), probabilidad, riesgo resultante y tratamiento elegido con su justificación.

### Paso 5 — Reducción y verificación

1. Aplique al menos dos medidas: detener o deshabilitar un servicio innecesario, restringirlo a `localhost`, o filtrarlo con `iptables`.
2. Repita el escaneo del Paso 2 y demuestre, con la salida de Nmap antes y después, que la superficie se redujo.
3. Anote qué dejó de funcionar, si algo dejó de funcionar.

## Recolección y análisis de datos

**Tabla 1.** Inventario de servicios expuestos

| Host | Puerto | Servicio | Versión | ¿Necesario? Justificación |
| --- | --- | --- | --- | --- |
|   |   |   |   |   |
|   |   |   |   |   |
|   |   |   |   |   |
|   |   |   |   |   |

**Tabla 2.** Matriz de riesgo

| Servicio | Impacto | Probabilidad | Riesgo | Tratamiento y justificación |
| --- | --- | --- | --- | --- |
|   |   |   |   |   |
|   |   |   |   |   |
|   |   |   |   |   |

**Tabla 3.** Reducción de la superficie de ataque

| Medida | Puertos antes | Puertos después | Efecto colateral observado |
| --- | --- | --- | --- |
|   |   |   |   |
|   |   |   |   |

## Preguntas de Análisis

- **P1.** ¿Qué propiedad de seguridad (confidencialidad, integridad, disponibilidad o no repudio) viola cada uno de los tres servicios que más riesgo obtuvieron en su matriz?
- **P2.** ¿Por qué `nmap -sn` puede no ver un host que sí existe? Dé dos razones técnicas.
- **P3.** ¿Qué diferencia encontró entre la vista externa (Nmap) y la interna (`ss`)? ¿Qué explica esa diferencia?
- **P4.** Un servicio escucha en `0.0.0.0:3306` en una máquina de desarrollo. ¿Qué tratamiento del riesgo aplicaría y por qué?
- **P5.** ¿Qué medida de las que aplicó tuvo mejor relación entre reducción de superficie y efecto colateral?
- **P6.** ¿Cómo mantendría este inventario actualizado en una organización de 200 equipos? Nombre un mecanismo concreto.

## Actividad ABET — SO4: Responsabilidad Ética y Profesional

Esta actividad mide el **Student Outcome 4 (SO4)** de la Carrera de Telecomunicaciones requerido para la acreditación ABET. Representa el **30 %** de la valoración total de la práctica y evalúa los indicadores PI 4.1 y PI 4.2 mediante las preguntas SO4-1 y SO4-2.

- **SO4-1.** **[PI 4.1 — 15 %] Ética del reconocimiento sobre redes que no son propias**
  Al inventariar su red doméstica, el estudiante descubre que el escaneo alcanzó también la red del vecino, mal segmentada por el proveedor, y que allí hay una cámara IP con credenciales por defecto. Redacte una respuesta ética y profesional que incluya:

  - **a)** La **decisión correcta** sobre qué hacer con esa información y con los datos ya capturados, y su fundamentación profesional.
  - **b)** El **canal de notificación** apropiado (titular, proveedor, CSIRT) y por qué no corresponde «probar» el acceso para confirmar el hallazgo.
  - **c)** El **marco legal ecuatoriano** aplicable (COIP Arts. 229 y 234; LOPDP) tanto al escaneo no autorizado como a la divulgación de lo encontrado.
- **SO4-2.** **[PI 4.2 — 15 %] Impacto de una superficie de ataque no gestionada en una institución educativa**
  Una universidad mantiene 400 equipos con servicios heredados expuestos (SMB, RDP y bases de datos sin filtrar) porque «siempre han funcionado así». Analice de manera integral:

  - **a)** **Económico:** costo de un incidente de *ransomware* propagado por esos servicios frente al costo de gestionarlos.
  - **b)** **Social:** datos de estudiantes y docentes expuestos, interrupción del semestre y consecuencias bajo la LOPDP.
  - **c)** **Ambiental:** equipos que habría que reemplazar o reinstalar y consumo energético de la respuesta al incidente.
  - **d)** **Contramedidas:** dos técnicas (p. ej. segmentación, inventario automatizado) y una política organizacional, citando NIST CSF 2.0, CIS Controls v8 o ISO/IEC 27001.

## Discusión y conclusiones

Cierre con una lectura de su propia red: qué encontró que no esperaba, qué decidió no tocar y por qué, y qué haría distinto si el inventario fuera de una organización con usuarios reales.

## Entregables

1. Informe técnico de 4 páginas siguiendo las directrices de la Sección [Directrices generales para el informe técnico](00-normas-generales.md#directrices-generales-para-el-informe-técnico).
2. Tablas 1 a 3 completas, con las direcciones ajenas al laboratorio anonimizadas.
3. Salidas de Nmap antes y después de la reducción, anotadas.
4. Respuestas SO4-1 y SO4-2 en una sección propia del informe.
5. Bitácora con los comandos ejecutados y sus marcas de tiempo.

## Rúbrica de Evaluación

**Tabla 4.** Rúbrica — P-00 (10 puntos)

| Criterio | Peso | Nivel alto (9–10) | Nivel medio (6–8) / bajo (0–5) |
| --- | --- | --- | --- |
| Descubrimiento de hosts | 14 % | Identifica todos los hosts vivos y explica la diferencia entre las técnicas de descubrimiento | Lista hosts sin contrastar técnicas o con omisiones |
| Inventario de servicios | 21 % | Registra puerto, servicio y versión de cada host y contrasta la vista externa con la interna | Inventario incompleto o sin contraste entre Nmap y `ss` |
| Matriz de riesgo | 21 % | Justifica impacto y probabilidad; el tratamiento elegido es coherente con el riesgo estimado | Valores asignados sin justificación o tratamiento incoherente |
| Reducción verificada | 14 % | Aplica al menos dos medidas y las demuestra con salidas de Nmap antes y después, anotando efectos colaterales | Aplica medidas sin evidencia comparable o sin analizar el efecto |
| **ABET – SO4: Responsabilidad Ética y Profesional (30 %)** |   |   |   |
| PI 4.1 – Ética profesional | 15 % | Decide correctamente sobre el hallazgo en red ajena, justifica el canal de notificación y cita el marco legal ecuatoriano | Decisión sin fundamento profesional o sin referencia legal |
| PI 4.2 – Impacto integral | 15 % | Evalúa impacto económico, social y ambiental con contramedidas técnicas y organizacionales, citando un estándar internacional | Análisis parcial de impactos o sin contramedidas fundamentadas |

**Tabla 5.** Escala ABET SO4 — P-00

| PI | No cumple<br>(0–59 %) | Cumple parcialmente<br>(60–69 %) | Cumple<br>(70–79 %) | Supera<br>(80–89 %) | Supera ampliamente<br>(90–100 %) |
| --- | --- | --- | --- | --- | --- |
| 4.1 | No reconoce que el escaneo alcanzó una red ajena ni plantea qué hacer con los datos capturados. | Reconoce el problema pero propone acciones inconsistentes; no distingue entre notificar y comprobar el acceso. | Decide no acceder al equipo y notificar; menciona el marco legal ecuatoriano sin desarrollarlo. | Decide correctamente sobre el hallazgo y los datos, elige el canal de notificación adecuado e integra el COIP y la LOPDP con argumentación clara. | Fundamenta cada decisión con normativa citada con precisión y con criterios de divulgación responsable aplicables a un profesional en ejercicio. |
| 4.2 | No considera ninguno de los tres impactos (económico, social, ambiental) de la superficie expuesta. | Considera parcialmente uno o dos de los impactos; las contramedidas no citan estándares. | Considera los tres impactos de forma adecuada; propone contramedidas pertinentes con al menos un estándar citado. | Integra los tres impactos con análisis detallado y contramedidas técnicas y organizacionales fundamentadas en estándares internacionales. | Realiza una evaluación exhaustiva de los tres impactos y sustenta las contramedidas en varios estándares (NIST CSF 2.0, CIS Controls v8, ISO/IEC 27001). |

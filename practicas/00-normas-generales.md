# Presentación del Manual

> Capítulo del **Manual de Prácticas** de Seguridad en Redes · INGE-00107 · Universidad de Cuenca.  
> Documento generado desde el manual: no lo edite a mano.

Este *Manual de Prácticas* es el documento guía de la componente **Aprendizaje Práctico Experimental (APE)** de la asignatura **Seguridad en Redes** (INGE-00107), Nivel 7 de la Carrera de Telecomunicaciones de la Universidad de Cuenca, período 202667-PA02 (septiembre 2026 – febrero 2027).

La asignatura enseña los principios fundamentales de la seguridad de redes a través del estudio de ataques reales. Los estudiantes aprenden cómo funcionan esos ataques y cómo prevenirlos y detectarlos. El enfoque es *aprender haciendo*: cada práctica reproduce un escenario controlado en el que se ejecutan y analizan distintos tipos de ataques.

## Estructura de las prácticas

**Tabla 1.** Estructura de cada práctica

| Sección | Contenido |
| --- | --- |
| Marco teórico | Fundamentos para contextualizar la práctica. |
| Objetivos | Competencias que se desarrollan (RdA alineados al sílabo). |
| Materiales | Software, máquinas virtuales y otros recursos requeridos. |
| Procedimiento | Pasos detallados de configuración y ejecución del laboratorio. |
| Análisis | Preguntas de reflexión y experimentación adicional. |
| Entregables | Documentos o artefactos que el grupo debe entregar. |
| Rúbrica | Criterios y ponderaciones de evaluación. |

## Carga horaria

**Tabla 2.** Componentes de aprendizaje — Seguridad en Redes (INGE-00107)

| Componente | Horas |
| --- | --- |
| Aprendizaje Contacto Docente (ACD) | 32 |
| Aprendizaje Práctico Experimental (APE) | 32 |
| Aprendizaje Autónomo (AA) | 32 |
| **Total** | **96** |

## Resultados de aprendizaje

- **RdA1.** Ser capaz de explicar los principios de seguridad de redes.
- **RdA2.** Ser capaz de explicar cómo funcionan varios ataques.
- **RdA3.** Ser capaz de describir y generalizar varias vulnerabilidades de red.
- **RdA4.** Ser capaz de detectar vulnerabilidades en la red usando herramientas especializadas.
- **RdA5.** Ser capaz de aplicar principios de seguridad de redes para resolver problemas reales.

## Seguridad y normas generales del laboratorio

Esta sección recopila las normas académicas, de seguridad ocupacional y de uso ético que aplican a *todas* las prácticas del manual. Cada práctica se remite a esta sección desde su apartado *Consideraciones de seguridad* y añade allí los riesgos específicos que correspondan.

El marco normativo de referencia es el **Reglamento Interno de Higiene y Seguridad de la Universidad de Cuenca** [1], código `UC-CU-REG-006-2024`, vigente desde el 24 de enero de 2025 (Acta 028 del Consejo Universitario). Para las herramientas ofensivas también aplican el Código Orgánico Integral Penal [2], la Ley Orgánica de Protección de Datos Personales [3] y la regulación sectorial de ARCOTEL [4].

### Normas académicas

- Presentarse puntualmente con los materiales y la preparación previa indicados en cada práctica.
- Ejecutar los ataques y herramientas ofensivas **únicamente dentro de los entornos virtualizados aislados** (máquinas SEED, Docker y redes NAT de VirtualBox) que se especifican en cada práctica; nunca en la red institucional, en redes de producción ni contra terceros sin autorización escrita.
- Entregar un **único informe por grupo** (máximo 3 integrantes) siguiendo las (Sección [Directrices generales para el informe técnico](#directrices-generales-para-el-informe-técnico)).
- Citar todas las fuentes consultadas en formato IEEE. El plagio o el uso no declarado de herramientas de IA generativa implica calificación de cero y reporte al Consejo Directivo de la Facultad.

### Riesgos eléctricos (Art. 37 del Reglamento)

Las estaciones del laboratorio operan con tensión de red 120 V c.a. y los equipos personales se conectan al sistema eléctrico del aula. Para prevenir choques, cortocircuitos y conatos de incendio, todo participante debe:

- No sobrecargar tomacorrientes con regletas o adaptadores múltiples; un único equipo por toma siempre que sea posible.
- Verificar el estado de cables, enchufes y cargadores antes de conectarlos; no usar cables con aislamiento dañado.
- No manipular ni intentar reparar instalaciones eléctricas o equipos sin antes verificar que estén desenergizados; reportar cualquier anomalía al encargado del laboratorio.
- Apagar y desconectar los equipos personales al finalizar la sesión.
- No introducir líquidos ni alimentos en el área de trabajo.

### Equipo de protección personal y conducta (Art. 9.a)

Las prácticas de este manual son íntegramente computacionales y no involucran sustancias químicas, radiaciones ni elementos mecánicos peligrosos, por lo que *no* se requiere EPP especializado. No obstante, conforme al Art. 9.a del Reglamento se exige:

- Vestimenta cerrada y calzado adecuado al ingresar al laboratorio.
- Mantener libres los pasillos, rutas de evacuación, extintores y puertas de emergencia (Art. 37, Riesgos Locativos).
- Conocer la ubicación del extintor, el botiquín y la salida de emergencia más cercana al puesto de trabajo.

### Gestión de residuos (Art. 9.d)

Aunque las prácticas no generan residuos químicos, sí pueden producir residuos electrónicos menores (pendrives defectuosos, cables, baterías) y residuos comunes (papel, plástico). De acuerdo con el Art. 9.d:

- Clasificar y depositar los residuos comunes en los contenedores rotulados del laboratorio (orgánico, reciclable, no reciclable).
- Entregar los residuos electrónicos al encargado del laboratorio para su disposición a través del área de Gestión Ambiental de la Universidad de Cuenca.
- No abandonar dispositivos personales ni soportes con información sensible en el aula al finalizar la sesión.

### Plan de emergencia (Arts. 46–47)

La Universidad de Cuenca cuenta con un Plan de Emergencias y Contingencias aprobado por el Benemérito Cuerpo de Bomberos Voluntarios de Cuenca. En caso de sismo, incendio o evacuación:

- Suspender la actividad, dejar el equipo encendido sin desconectar cables y seguir las indicaciones del docente.
- Evacuar por la ruta señalizada hasta el punto de encuentro de la Facultad de Ingeniería sin correr, sin retroceder por objetos personales y manteniendo la calma.
- Reportar cualquier accidente al docente y al encargado del laboratorio para activar el protocolo correspondiente (Art. 8.c).

### Ergonomía (Art. 38)

Las sesiones de laboratorio implican uso prolongado de pantalla y teclado. Para prevenir lesiones músculo-esqueléticas y fatiga visual:

- Realizar pausas activas de 5 minutos cada 50 minutos de trabajo frente a la pantalla.
- Mantener la pantalla a la altura de los ojos y a una distancia aproximada de 50–70 cm; ajustar la silla de forma que muñecas y antebrazos queden alineados con el teclado.
- Garantizar iluminación adecuada sin reflejos directos sobre la pantalla.
- Reportar al docente cualquier molestia o condición ergonómica deficiente para su corrección.

### Uso ético y responsable de herramientas de auditoría

Las prácticas del manual emplean herramientas de seguridad ofensiva (Nmap, Metasploit, Scapy, hping3, WPScan, Gobuster, Hydra, John, Sqlmap, etc.) cuyo uso fuera del entorno autorizado puede constituir un delito informático en el Ecuador.

> [!WARNING]
> **Marco legal — LOPDP y COIP**
>
> La ejecución de las herramientas y técnicas aquí descritas **únicamente está autorizada dentro de las máquinas virtuales, contenedores y redes aisladas** provistas por el docente. Su uso contra cualquier sistema, red o dato sin autorización expresa del titular puede tipificarse, según corresponda, como:
>
> - **COIP Art. 229** — Revelación ilegal de bases de datos (privacidad de la información).
> - **COIP Art. 234** — Acceso no consentido a un sistema informático, telemático o de telecomunicaciones.
> - **Ley Orgánica de Protección de Datos Personales (LOPDP)** — Tratamiento ilícito de datos personales.
> - Sanciones administrativas adicionales de ARCOTEL en redes de telecomunicaciones.
>
> El estudiante declara conocer este marco legal al ejecutar las prácticas. La Universidad de Cuenca no se responsabiliza por usos fuera del entorno controlado del laboratorio.

## Directrices generales para el informe técnico

Salvo que la práctica indique otra cosa, cada grupo entrega un informe técnico que sigue los lineamientos descritos a continuación.

### Formato y extensión

- Formato PDF, tamaño A4, márgenes 2,5 cm.
- Tipografía sans-serif de 11 pt, interlineado 1,15.
- Extensión: 8–15 páginas (sin contar portada, índice ni anexos), salvo indicación específica en la práctica.
- Cada figura y tabla numerada y referenciada en el texto.

### Estructura mínima

1. **Portada**: título de la práctica, asignatura, código, integrantes, paralelo, docente, fecha.
2. **Resumen** (máx. 200 palabras): objetivo, metodología, resultados principales y conclusión.
3. **Introducción**: contexto y problema abordado.
4. **Marco teórico**: fundamentos con citas IEEE.
5. **Materiales y métodos**: entorno, herramientas, topología.
6. **Resultados**: tablas de recolección de datos y evidencias (capturas, comandos, salidas).
7. **Discusión**: interpretación, comparación con literatura, limitaciones.
8. **Conclusiones y recomendaciones**.
9. **Contribución de cada integrante**: tabla con una fila por integrante en la que consten las tareas concretas que realizó —montaje del entorno, ejecución de cada paso del procedimiento, análisis de los datos, redacción de cada sección— y el porcentaje aproximado de participación. La tabla la acuerda todo el grupo. Esta sección es obligatoria en todos los informes.
10. **Referencias** en formato IEEE (mínimo 3 fuentes verificables; libros, papers o estándares antes que blogs).
11. **Anexos** (opcional): código fuente, capturas completas, archivos `.pcap`, evidencias adicionales.

### Figuras, tablas y código

- Toda figura/tabla debe llevar caption descriptivo y numeración consecutiva, y ser referenciada en el texto antes de aparecer.
- Las capturas de pantalla deben tener resolución legible y ocultar información personal (nombres de usuario reales, IPs públicas propias, etc.).
- El código se incluye en bloques monoespaciados (no como imagen) con resaltado de sintaxis; los fragmentos extensos van en anexo.

### Política de uso de IA generativa

El uso de asistentes de IA (ChatGPT, Claude, Copilot, etc.) está permitido únicamente para apoyo en redacción, depuración menor y consulta de conceptos. **No está permitido** delegar a la IA la generación de hallazgos, conclusiones o discusiones. Cada informe debe declarar explícitamente, en una sección final o nota al pie, las herramientas de IA utilizadas y la naturaleza del uso. La omisión de esta declaración se considera falta de probidad académica.

## Mapa de prácticas del curso

**Tabla 3.** Prácticas programadas por unidad temática del sílabo

| Cód. | Unidad | Práctica | Herramienta |
| --- | --- | --- | --- |
| P-00 | 100. Introducción a la seguridad | Inventario y superficie de ataque | Nmap / ss / iptables |
| P-01 | 200. Pentesting | Pentesting con ColdDBox (VulnHub) | Kali / Metasploit |
| P-02 | 300. Criptografía | Criptografía de clave secreta | OpenSSL / Python |
| P-03 | 300. Criptografía | Criptografía de clave pública (RSA) | OpenSSL / C |
| P-04 | 400. Funciones hash | Ataque de colisión MD5 | md5collgen / bless |
| P-05 | 500. Sniffing/Spoofing | Detección y suplantación de paquetes | Scapy / Wireshark |
| P-06 | 500. Sniffing/Spoofing | Envenenamiento de caché ARP | Scapy / Docker |
| P-07 | 600. TCP | Ataque de redirección ICMP | Scapy / Docker |
| P-08 | 600. TCP | Ataques al protocolo TCP | Scapy / Docker |
| P-09 | 700. Firewalls | Exploración de firewalls (Netfilter e iptables) | LKM / Netfilter / iptables / Docker |
| P-10 | 700. Firewalls | Evasión de firewalls | SSH tunneling / VPN |
| P-11 | 800. DNS | Ataques al DNS local | Scapy / Bind9 |
| P-12 | 800. DNS | Ataques al DNS remoto (Kaminsky) | Scapy / C / Bind9 |
| P-13 | 800. DNS | Ataque de DNS rebinding (IoT) | Bind9 / JavaScript / Docker |
| P-14 | 800. DNS | Infraestructura DNS (raíz/TLD/dominio) | Bind9 / SEED Emulator |
| P-15 | 800. DNS | Extensiones de seguridad DNS (DNSSEC) | DNSSEC / Bind9 |
| P-16 | 900. VPN | Túnel VPN desde cero | TUN/TAP / Python |
| P-17 | 900. VPN | Redes privadas virtuales | OpenVPN / Docker |

## Referencias

1. Universidad de Cuenca, «Reglamento Interno de Higiene y Seguridad de la Universidad de Cuenca». UC-CU-REG-006-2024, Acta 028, Consejo Universitario; vigente desde 24-01-2025, 2024.
2. Asamblea Nacional del Ecuador, «Código Orgánico Integral Penal (COIP)». Arts. 229 y 234 (delitos informáticos), 2014.
3. Asamblea Nacional del Ecuador, «Ley Orgánica de Protección de Datos Personales (LOPDP)». Registro Oficial Quinto Suplemento No. 459, 2021.
4. ARCOTEL, «Agencia de Regulación y Control de las Telecomunicaciones». 2024. <https://www.arcotel.gob.ec>.

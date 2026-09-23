<div align="center">

# P-17 · Redes Privadas Virtuales

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
| **Unidad** | 900 – Redes privadas virtuales |
| **Código** | INGE-00107 |
| **Modalidad** | Presencial |
| **Valoración** | 10 puntos |
| **Grupos** | Máx. 3 estudiantes |
| **Entrega** | Según calendario |
| **ABET** | SO4 – Responsabilidad Ética y Profesional (PI 4.1 y PI 4.2) — representa el 30 % de la valoración |

## Marco Teórico

Los fundamentos teóricos sintetizados en esta sección se basan en [1], [2], [3]; se recomienda consultar dichas fuentes para una exposición más profunda. El procedimiento de laboratorio adapta el *VPN Lab* de SEED [1], en el que el estudiante implementa una VPN simple denominada `miniVPN`.

### VPN completa: del túnel a la VPN segura

Una **VPN** (Virtual Private Network) crea un ámbito privado de comunicaciones, es decir, una extensión segura de una red privada sobre una red insegura como Internet. Una VPN puede construirse sobre **IPSec** o sobre **TLS/SSL** (Transport Layer Security / Secure Socket Layer): son dos enfoques fundamentalmente distintos. Esta práctica se concentra en las VPN basadas en **TLS/SSL**.

En la práctica P-16 se construyó únicamente la parte de *tunneling* (sin cifrado). Un túnel IP **no es todavía una VPN**: para llamarlo VPN hay que protegerlo, garantizando **confidencialidad** (mediante cifrado) e **integridad** (mediante un Código de Autenticación de Mensaje, MAC), además de **autenticar** a los dos extremos. Esta práctica añade esos elementos sobre el túnel TUN/TAP.

### Conceptos clave

El diseño de una VPN TLS/SSL ejercita varios principios de seguridad:

- **TUN/TAP e IP tunneling**: interfaz virtual de red que permite capturar paquetes IP (TUN, capa 3) o tramas Ethernet (TAP, capa 2) en espacio de usuario, encapsularlos y reenviarlos.
- **Enrutamiento**: las tablas de rutas dirigen el tráfico destinado a la red privada hacia la interfaz `tun0`.
- **Criptografía de clave pública, PKI y certificados X.509**: el servidor presenta un certificado emitido por una Autoridad Certificadora (CA) que el cliente valida [3].
- **Programación TLS/SSL**: se establece una sesión TLS sobre TCP entre los dos extremos del túnel [2], [4].
- **Autenticación**: el cliente autentica al servidor (vía certificado) y el servidor autentica al usuario (vía contraseña contra el archivo `/etc/shadow`).

> [!NOTE]
> **Relación con la P-16**
>
> La P-16 (*VPN Tunneling Lab*) cubre solo el túnel sin cifrado. Esta práctica (*VPN Lab*) es la versión **integral**: parte del túnel TUN/TAP y le añade cifrado TLS, autenticación con certificados y soporte de múltiples clientes. Se recomienda completar antes las prácticas de PKI y TLS.

**Objetivo general**
Implementar y demostrar una VPN TLS/SSL completa (`miniVPN`) que parta de un túnel TUN/TAP y añada cifrado, autenticación mutua basada en certificados X.509 y contraseñas, y soporte de múltiples clientes.
**Objetivos específicos**

- **OE1.** Configurar las tres VMs (cliente, gateway/servidor y host interno) y verificar la conectividad inicial.
- **OE2.** Crear el túnel VPN con TUN/TAP y configurar el enrutamiento en cliente, servidor y host interno.
- **OE3.** Cifrar el túnel reemplazando el canal UDP por una sesión TLS/SSL sobre TCP.
- **OE4.** Autenticar al servidor VPN mediante certificados X.509 y a una CA propia, distinguiendo un caso exitoso y uno fallido.
- **OE5.** Autenticar al cliente VPN con usuario/contraseña contra el archivo `shadow`.
- **OE6.** Soportar múltiples clientes simultáneos mediante procesos hijo, IPC con *pipes* y `select()`.

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
| SEED Ubuntu 20.04 VM | Tres VMs: cliente, gateway/servidor y host interno |
| VirtualBox | Redes *NAT Network* e *Internal Network* |
| `vpnclient`/`vpnserver` | Programas de muestra del túnel TUN/TAP (SEED) |
| `tlsclient`/`tlsserver` | Programas de muestra TLS/SSL (SEED) |
| OpenSSL | PKI, certificados X.509 y biblioteca TLS |
| Wireshark | Análisis de tráfico cifrado |

> [!NOTE]
> **Provisión de materiales**
>
> El estudiante adquiere o instala por su cuenta el equipo personal (laptop), las máquinas virtuales (VirtualBox, SEED VM, Kali Linux, contenedores Docker) y todo el software listado arriba. El laboratorio de la Carrera de Telecomunicaciones provee el espacio físico, el mobiliario y **acceso a Internet supervisado** para la descarga de imágenes, paquetes y consulta de documentación durante la sesión. El laboratorio no entrega equipos de cómputo personales ni licencias de software.

## Entorno de Laboratorio

> **Figura 1.** Topología del laboratorio P-17 (*VM setup*): cliente VPN (Host U), gateway/servidor VPN y host interno (Host V).  
> *(diagrama vectorial; se reproduce en el PDF del manual)*

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

Se implementará `miniVPN`, una VPN simple para Linux. Se parte de los programas de muestra `vpnclient`/`vpnserver` (túnel TUN/TAP) y `tlsclient`/`tlsserver` (TLS), provistos por SEED, y se completan según cada tarea.

### Tarea 1 — Configuración de las VMs

Se requieren tres VMs (Figura 1): **Cliente VPN** (también Host U), **Gateway** (Servidor VPN) y **Host V** dentro de la red privada. Cliente y gateway se conectan a la misma LAN mediante el adaptador *NAT Network* (simula Internet); el gateway y Host V se conectan mediante el adaptador *Internal Network*.

Como la *Internal Network* de VirtualBox no provee DHCP, Host V (y la segunda interfaz del gateway) deben configurarse con **IP estática**. En el applet de red elija `Edit Connections`, seleccione la conexión correcta (verifique la MAC contra `ifconfig`), abra la pestaña `IPv4 Settings`, cambie el método a `Manual` y agregue la dirección (p. ej. `192.168.60.1/24` en el gateway y `192.168.60.101/24` en Host V).

> [!NOTE]
> **Prueba previa al túnel (*Pre-Tunnel Test*)**
>
> Antes de montar la VPN, desde Host U haga `ping` a Host V y explique la observación: Host V **no** es directamente alcanzable desde Host U porque está aislado en la red interna.

### Tarea 2 — Crear el túnel VPN con TUN/TAP

La tecnología habilitante de las VPN TLS/SSL es TUN/TAP. Los programas `vpnclient` y `vpnserver` son los dos extremos del túnel y se comunican por un socket (TCP o UDP; en el código de muestra se usa UDP). Cada extremo se conecta a su sistema anfitrión mediante una interfaz TUN, por la que (1) obtiene paquetes IP del anfitrión para enviarlos por el túnel y (2) recibe paquetes del túnel y los reinyecta en el kernel, que los reenvía a su destino final (Figura 2).

> **Figura 2.** Extremos de la VPN: `vpnclient` y `vpnserver` unidos por un túnel sobre Internet (adaptado de la Fig. 3 del SEED VPN Lab).  
> *(diagrama vectorial; se reproduce en el PDF del manual)*

#### Paso 1 — Ejecutar el servidor VPN

Al iniciar `vpnserver` aparece una interfaz `tun0` (visible con `ifconfig -a`); el programa bloquea esperando conexiones, así que use otra terminal para configurarla. Habilite el reenvío IP para que el gateway actúe como tal.

**Listado 1.** Ejecutar y configurar el servidor VPN

```bash
$ sudo ./vpnserver
# En otra ventana:
$ sudo ifconfig tun0 192.168.53.1/24 up
$ sudo sysctl net.ipv4.ip_forward=1
```

#### Paso 2 — Ejecutar el cliente VPN

**Listado 2.** Ejecutar y configurar el cliente VPN

```bash
# En la VM cliente (la IP del servidor está fija en el programa):
$ sudo ./vpnclient
# En otra ventana:
$ sudo ifconfig tun0 192.168.53.5/24 up
```

#### Paso 3 — Enrutamiento en cliente y servidor

Dirija hacia `tun0` el tráfico destinado a la red privada. La ruta de la red `192.168.53.0/24` suele añadirse automáticamente al asignar la IP a `tun0`.

**Listado 3.** Rutas hacia la red privada

```bash
# En Host U (cliente):
$ sudo route add -net 192.168.60.0/24 tun0
```

#### Paso 4 — Enrutamiento en Host V

Cuando Host V responde a un paquete de Host U, el tráfico de retorno debe volver al servidor VPN. Determine la IP origen de los paquetes que llegan de U a V (esa será la IP destino en la respuesta) y añada la ruta correspondiente con `route` para que el retorno entre al túnel.

#### Paso 5 — Probar el túnel

Acceda a Host V desde Host U y capture con Wireshark las interfaces del cliente, identificando qué paquetes pertenecen al túnel y cuáles no.

**Listado 4.** Pruebas de conectividad por el túnel

```bash
# En Host U:
$ ping   192.168.60.101
$ telnet 192.168.60.101
```

#### Paso 6 — Prueba de ruptura del túnel

Con la sesión `telnet` activa, rompa el túnel deteniendo `vpnclient`/`vpnserver`; escriba en la ventana `telnet` y observe. Reconecte el túnel: ¿la conexión TCP se rompió o se reanuda? Explique.

### Tarea 3 — Cifrar el túnel (TLS/SSL)

Hasta aquí existe un túnel IP, pero **no protegido**. Para llamarlo VPN hay que asegurar *confidencialidad* (cifrado) e *integridad* (MAC). TLS se construye normalmente sobre TCP, por lo que primero se reemplaza el canal UDP del código de muestra por un canal **TCP** y luego se establece una sesión **TLS** entre los dos extremos (programas `tlsclient`/`tlsserver`). En la demostración, capture con Wireshark el tráfico *dentro* del túnel y muestre que va cifrado.

**Listado 5.** Reconocer y descifrar TLS en Wireshark

```bash
# Edit -> Preferences -> Protocols -> TLS: agregar el puerto del servidor
#   SSL/TLS Ports: 443,4433
# Para depurar, cargar la clave privada del servidor (RSA key list):
#   IP, Port=4433, Protocol=tls, Key File=server-key.pem
```

### Tarea 4 — Autenticar el servidor VPN

Antes de establecer la VPN, el cliente debe **autenticar al servidor** para asegurarse de que no es fraudulento. Se usan certificados de clave pública: el servidor obtiene un certificado de una CA y el cliente lo valida [3]. La verificación tiene tres partes: (1) el certificado del servidor es válido; (2) el servidor es el dueño del certificado; y (3) el servidor es el *servidor pretendido* (coincide el *hostname* solicitado por el usuario, que **no** debe estar fijo en el código). Demuestre un caso **exitoso** (servidor correcto) y uno **fallido** (servidor distinto al pretendido).

Genere su propia CA (use su apellido en el nombre del servidor para diferenciar su trabajo). Para que el cliente confíe en un certificado, coloque el certificado de la CA en `./ca_client` y cree un enlace simbólico cuyo nombre sea el *hash* del sujeto:

**Listado 6.** Preparar el certificado de la CA en el cliente

```bash
$ openssl x509 -in GeoTrustGlobalCA.pem -noout -subject_hash
2c543cd1
$ ln -s GeoTrustGlobalCA.pem 2c543cd1.0
# Probar contra el propio servidor y contra un HTTPS real:
$ ./tlsclient vpnlabserver.com 4433
$ ./tlsclient www.google.com 443
```

Como el *hostname* del servidor lo escribe el usuario en la línea de comandos, debe obtenerse su dirección IP en tiempo de ejecución con `getaddrinfo()` (el antiguo `gethostbyname()` no soporta IPv6):

**Listado 7.** Resolver el hostname con getaddrinfo()

```python
struct addrinfo hints, *result;
hints.ai_family = AF_INET;          // solo IPv4
int error = getaddrinfo("www.example.com", NULL, &hints, &result);
if (error) { fprintf(stderr, "getaddrinfo: 
struct sockaddr_in *ip = (struct sockaddr_in *) result->ai_addr;
printf("IP Address: 
freeaddrinfo(result);
```

### Tarea 5 — Autenticar el cliente VPN

Acceder a la red privada es un privilegio: solo usuarios autorizados (con cuenta válida en el servidor) deben poder establecer el túnel. El servidor solicita **usuario y contraseña** y los verifica contra el archivo `/etc/shadow`: obtiene el registro con `getspnam()`, aplica `crypt()` a la contraseña recibida y compara con el hash almacenado. La contraseña **no** debe ser visible al teclear (use `getpass()`) ni estar fija en el código.

**Listado 8.** Autenticación contra el archivo shadow (login.c)

```python
#include <shadow.h>
#include <crypt.h>
int login(char *user, char *passwd) {
    struct spwd *pw;
    char *epasswd;
    pw = getspnam(user);                 // requiere privilegio root
    if (pw == NULL) return -1;
    epasswd = crypt(passwd, pw->sp_pwdp);
    if (strcmp(epasswd, pw->sp_pwdp)) return -1;  // no coincide
    return 1;                            // autenticado
}
// Compilar:  gcc login.c -lcrypt   (¡-lcrypt, no -lcrypto!)
```

### Tarea 6 — Soportar múltiples clientes

Un servidor VPN real atiende varios túneles a la vez, cada uno con su propia sesión TLS. Una implementación típica crea un **proceso hijo** por túnel (Figura 3). En el sentido túnel → TUN, cada hijo recibe el paquete y lo escribe en `tun0`. En el sentido inverso (un paquete llega a `tun0` desde la red privada), el **proceso padre** debe decidir *a qué túnel* corresponde y enviárselo al hijo adecuado mediante IPC (p. ej. *pipes*).

> **Figura 3.** Soporte de múltiples clientes: un proceso hijo por túnel y el padre decidiendo el destino de cada paquete (adaptado de la Fig. 4 del SEED VPN Lab).  
> *(diagrama vectorial; se reproduce en el PDF del manual)*

**IPC con *pipe*.** El padre crea un *pipe* con `pipe()`; tras `fork()`, escribe en `fd[1]` y el hijo lee de `fd[0]`:

**Listado 9.** Comunicación padre–hijo con pipe

```python
int fd[2];  pipe(fd);
if (fork() > 0) {            // padre
    close(fd[0]);
    write(fd[1], string, strlen(string)+1);
} else {                     // hijo
    close(fd[1]);
    nbytes = read(fd[0], readbuffer, sizeof(readbuffer));
}
```

**Monitoreo con `select()`.** Cada hijo debe vigilar a la vez el *pipe* y el socket; el padre, el socket y la interfaz TUN. Se usa `select()` para no malgastar CPU:

**Listado 10.** Vigilar varios descriptores con select()

```python
fd_set readFDSet;
FD_ZERO(&readFDSet);
FD_SET(sockfd, &readFDSet);
FD_SET(tunfd,  &readFDSet);
select(FD_SETSIZE, &readFDSet, NULL, NULL, NULL);
if (FD_ISSET(sockfd, &readFDSet)) { /* leer del socket */ }
if (FD_ISSET(tunfd,  &readFDSet)) { /* leer de tun0   */ }
```

### Flujo de paquetes en la VPN (ejemplo con `telnet`)

Para comprender cómo viaja un paquete por la `miniVPN`, considere `telnet 192.168.60.101` desde Host U. El paquete original (`IP/TCP/Data`) se enruta hacia `tun0`, el programa VPN lo **cifra** y lo coloca como *payload* de un nuevo datagrama; el kernel le antepone una nueva cabecera (`New IP/UDP`) y lo envía por la interfaz física. En el otro extremo se realiza el proceso inverso: descifrado y reinyección en `tun0` para que el kernel lo enrute a su destino final (Figura 4).

> **Figura 4.** Encapsulamiento en la VPN: el paquete original se cifra y viaja como *payload* de un nuevo paquete (adaptado de la Fig. 5 del SEED VPN Lab).  
> *(diagrama vectorial; se reproduce en el PDF del manual)*

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

- **P1.** ¿Por qué un túnel IP (P-16) no constituye todavía una VPN? ¿Qué propiedades de seguridad añade el cifrado TLS para convertirlo en una VPN?
- **P2.** En la Tarea 4, ¿qué líneas de código verifican (a) que el certificado del servidor es válido, (b) que el servidor es dueño del certificado y (c) que es el servidor pretendido? ¿Qué línea detiene el *handshake* si la verificación falla?
- **P3.** ¿Por qué el *hostname* del servidor no debe estar fijo en el código y debe resolverse con `getaddrinfo()`?
- **P4.** Describa el ataque *Man-in-the-Middle* contra la VPN y explique cómo la autenticación del servidor por certificado lo derrota.
- **P5.** ¿Qué líneas envían el usuario/contraseña al servidor y cuáles consultan el archivo `shadow`? ¿Por qué se compila con `-lcrypt` y no con `-lcrypto`?
- **P6.** Con soporte de múltiples clientes, ¿cómo decide el proceso padre a qué túnel pertenece un paquete que llega por `tun0`? ¿Por qué se requiere IPC (*pipe*) y `select()`?
- **P7.** Envíe un paquete grande (`ping -s`, tamaño >3000) de Host U a Host V y explique lo observado en Wireshark (fragmentación respecto al MTU de `tun0`).
- **P8.** ¿Cuál es la diferencia entre las interfaces TUN y TAP, y entre una VPN basada en TLS/SSL y una basada en IPSec?

## Actividad ABET — SO4: Responsabilidad Ética y Profesional

Esta actividad mide el **Student Outcome 4 (SO4)** de la Carrera de Telecomunicaciones requerido para la acreditación ABET: *habilidad para reconocer las responsabilidades éticas y profesionales en situaciones de ingeniería y emitir juicios fundamentados, considerando el impacto global, económico, medioambiental y social de las soluciones propuestas.* Representa el **30 %** de la valoración total de la práctica y evalúa los indicadores PI 4.1 y PI 4.2 mediante las preguntas SO4-1 y SO4-2.

- **SO4-1.** **[PI 4.1 — 15 %] Ética y responsabilidad profesional ante el uso no autorizado de VPN comercial en una empresa**
  Un empleado de una empresa ecuatoriana instala sin autorización una VPN comercial gratuita en su laptop corporativa para evadir los controles de seguridad del proxy corporativo y acceder a redes sociales bloqueadas. El departamento de TI descubre la práctica al analizar el tráfico de red. Analice:

  - **a)** Las **responsabilidades éticas y profesionales del empleado** (políticas de uso aceptable, lealtad a la empresa, privacidad del empleado).
  - **b)** Las **responsabilidades del departamento de TI** al gestionar la situación: procedimiento disciplinario, educación vs. sanción.
  - **c)** Los **riesgos de seguridad** que introduce el uso no autorizado de VPN comerciales gratuitas (potencial exfiltración de datos corporativos al proveedor de VPN) y el **marco legal ecuatoriano** aplicable (LOPDP, COIP) para ambas partes.
- **SO4-2.** **[PI 4.2 — 15 %] Impacto integral del compromiso de un proveedor de VPN corporativo**
  El proveedor de VPN corporativo utilizado por 200 empresas ecuatorianas es comprometido por un atacante estatal, quien obtiene acceso a los servidores de VPN y descifra el tráfico registrado de los últimos 15 días, afectando comunicaciones confidenciales de sus clientes empresariales. Analice:

  - **a)** **Económico:** daños por exposición de secretos comerciales, costos de migración a otro proveedor, litigios contra el proveedor de VPN, pérdida de contratos.
  - **b)** **Social:** exposición de comunicaciones internas de ONG, medios de comunicación y entidades gubernamentales, riesgos para periodistas y activistas que usaban el servicio.
  - **c)** **Ambiental:** consumo energético de la migración masiva de infraestructura VPN y del proceso de análisis forense distribuido.
  - **d)** **Contramedidas:** proponga **dos contramedidas técnicas** (VPN autogestionada con WireGuard/OpenVPN, Zero Trust Architecture) y **una política organizacional**, citando RFC 8446, NIST SP 800-207 o ISO/IEC 27036 (seguridad en relaciones con proveedores).

## Discusión y conclusiones

A partir de los datos recolectados y del análisis realizado, elabore una discusión que responda al menos a las siguientes preguntas guía:

- **DC1.** ¿Se alcanzaron los objetivos planteados? Justifique cada uno con evidencia experimental concreta (capturas, métricas, salidas de comandos).
- **DC2.** ¿Qué limitaciones impone el entorno virtualizado a los resultados? ¿Cómo se trasladarían las observaciones a un escenario real de producción?
- **DC3.** ¿Qué contramedidas o controles de seguridad mitigan el ataque o refuerzan la defensa estudiada? Cite al menos una buena práctica de la industria, una RFC o un estándar (ISO/IEC, IEEE, NIST) pertinente.
- **DC4.** ¿Qué errores se cometieron durante la práctica y qué recomendaciones daría a futuros estudiantes para evitarlos?

Cierre con **conclusiones** (3–5 viñetas) que resuman los hallazgos principales y los vinculen explícitamente con los *Resultados de Aprendizaje* de la asignatura.

## Entregables

1. **Informe técnico** que describa el diseño y la implementación de la `miniVPN`, cómo se probaron sus funcionalidades y su seguridad, con capturas Wireshark que demuestren: (a) el túnel funcional (`ping`/`telnet`), (b) que el tráfico va *cifrado*, y (c) la defensa frente a un ataque MITM. Indique las líneas de código relevantes con su explicación. Bibliografía IEEE (≥3 fuentes).
2. **Código fuente** de `vpnclient`/`vpnserver` modificados (TLS, autenticación de servidor y cliente, soporte multicliente) y la configuración de las tres VMs.
3. **Video de demostración** (*checklist* del SEED VPN Lab): estado inicial, prueba previa, creación del túnel, pruebas `ping`/`telnet`, ruptura del túnel, paquete grande, configuración TLS y prueba MITM.
4. **Respuestas a la Actividad ABET – SO4** (preguntas SO4-1 y SO4-2), integradas en el informe técnico con extensión de 1–2 páginas por pregunta y las fuentes citadas según norma IEEE.

## Rúbrica de Evaluación

**Tabla 3.** Rúbrica — P-17 (10 puntos)

| Criterio | Peso | Indicador | Descripción |
| --- | --- | --- | --- |
| Túnel TUN/TAP | 14 % | Túnel funcional | `ping`/`telnet` de Host U a Host V por el túnel; enrutamiento correcto en las tres VMs. |
| Cifrado TLS | 18 % | Tráfico cifrado | Canal TCP+TLS operativo; Wireshark muestra el *payload* cifrado (no legible). |
| Autenticación servidor | 14 % | Certificado validado | Caso exitoso y caso fallido; defensa demostrada ante MITM. |
| Autenticación cliente | 10 % | Login por shadow | Usuario/contraseña verificados; sin contraseñas visibles ni fijas en el código. |
| Multicliente y análisis | 14 % | Varios túneles y preguntas | Soporte de múltiples clientes y respuestas con fundamento técnico. |
| **ABET – SO4: Responsabilidad Ética y Profesional (30 %)** |   |   |   |
| PI 4.1 – Ética profesional | 15 % | Respuesta ética fundamentada | Aplica principios éticos y legales al escenario del incidente; la cadena de notificación está justificada. |
| PI 4.2 – Impacto integral | 15 % | Análisis de impacto | Evalúa impacto económico, social y ambiental con contramedidas técnicas y organizacionales, citando al menos un estándar internacional. |

**Tabla 4.** Escala ABET SO4 — P-17

| PI | No cumple<br>(0–59 %) | Cumple parcialmente<br>(60–69 %) | Cumple<br>(70–79 %) | Supera<br>(80–89 %) | Supera ampliamente<br>(90–100 %) |
| --- | --- | --- | --- | --- | --- |
| 4.1 | No aplica principios éticos ni profesionales al evaluar la situación de incidente. | Aplica de manera inconsistente los principios éticos; el análisis legal es superficial o erróneo. | Aplica de manera básica los principios éticos; menciona el marco legal ecuatoriano sin análisis profundo. | Aplica coherentemente su juicio ético y profesional; integra el COIP y la LOPDP con argumentación clara. | Aplica de manera ejemplar e integral su juicio ético; argumenta cada decisión con evidencia y normativas citadas con precisión. |
| 4.2 | No considera ninguno de los tres impactos (económico, social, ambiental). | Considera parcialmente uno o dos de los impactos; las contramedidas no citan estándares. | Considera los tres impactos de forma adecuada; propone contramedidas pertinentes con al menos un estándar citado. | Integra los tres impactos con análisis detallado y contramedidas bien fundamentadas en estándares internacionales. | Realiza una evaluación exhaustiva de los tres impactos; las contramedidas son innovadoras y se respaldan en múltiples estándares. |

## Referencias

1. Du, Wenliang, «Computer & Internet Security: A Hands-on Approach». Independently published, 2019.
2. Rescorla, Eric, «The Transport Layer Security (TLS) Protocol Version 1.3». RFC 8446, 2018.
3. Cooper, David and others, «Internet X.509 Public Key Infrastructure Certificate and Certificate Revocation List (CRL) Profile». RFC 5280, 2008.
4. OpenSSL Project, «OpenSSL Cryptography and SSL/TLS Toolkit». 2024. <https://www.openssl.org>.

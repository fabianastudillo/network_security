# P-16 · Túnel VPN desde Cero

> Práctica del **Manual de Prácticas** de Seguridad en Redes · INGE-00107 · Universidad de Cuenca.  
> Documento generado desde el manual: no lo edite a mano (véase [`practicas/README.md`](README.md)).

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

Los fundamentos teóricos sintetizados en esta sección se basan en [1], [2]; se recomienda consultar dichas fuentes para una exposición más profunda. El procedimiento de laboratorio adapta el *VPN Lab: The Container Version* de SEED Labs [3].

### ¿Qué es una VPN?

Una **VPN** (Virtual Private Network) es una red privada construida sobre una red pública, generalmente Internet. Los equipos dentro de una VPN pueden comunicarse de forma segura, como si estuvieran en una red privada físicamente aislada, aunque su tráfico atraviese una red pública. Las VPN permiten, por ejemplo, que empleados accedan de forma segura a la intranet corporativa durante un viaje, o que una organización extienda su red privada entre sitios geográficamente distantes.

El tipo de VPN más común se construye sobre la **capa de transporte**. Todo programa VPN real consta de dos piezas esenciales: el **tunneling** (encapsulamiento) y el **cifrado**. Esta práctica se concentra exclusivamente en el *tunneling*, para comprender la tecnología de túnel sin la complejidad del cifrado.

> [!NOTE]
> Esta práctica implementa solo la parte de *tunneling*: el túnel **no está cifrado**. La práctica P-17 aborda VPNs completas que incorporan cifrado y autenticación (OpenVPN/TLS).

### La interfaz virtual TUN/TAP

**TUN** y **TAP** son controladores virtuales del kernel que implementan dispositivos de red enteramente por software. **TAP** (de *network tap*) simula un dispositivo Ethernet y opera con paquetes de capa 2 (tramas Ethernet); **TUN** (de *network TUNnel*) simula un dispositivo de capa de red y opera con paquetes de capa 3 (paquetes IP). Con TUN/TAP es posible crear interfaces de red virtuales.

Un programa de espacio de usuario se asocia a la interfaz TUN/TAP. Los paquetes que el sistema operativo envía a través de esa interfaz son entregados al programa; y los paquetes que el programa escribe en la interfaz son inyectados en la pila de red del kernel, como si llegaran desde una fuente externa. El programa usa las llamadas estándar `read()` y `write()` para recibir y enviar paquetes.

### Tunneling IP y enrutamiento

El *IP tunneling* consiste en colocar el paquete IP recibido de la interfaz TUN dentro del campo de *payload* de un nuevo paquete (en esta práctica, un datagrama UDP) y enviarlo a otra máquina. Es decir, se coloca el paquete original dentro de un paquete nuevo. La implementación del túnel es simple programación cliente/servidor sobre UDP.

Para que el tráfico hacia la red privada fluya por el túnel se requiere configurar el **enrutamiento**: las rutas dirigen los paquetes destinados a la red remota hacia la interfaz TUN, donde el programa de espacio de usuario los captura y encapsula.

**Objetivo general**
Construir desde cero una VPN de túnel (sin cifrado) en Python usando la interfaz TUN, replicando el flujo del *VPN Lab* de SEED, para comprender los mecanismos internos del tunneling IP y el enrutamiento.
**Objetivos específicos**

- **OE1.** Levantar la topología de contenedores (cliente, servidor/router y host privado) y verificar la conectividad inicial.
- **OE2.** Crear, nombrar y configurar una interfaz TUN en Linux con Python, y leer/escribir paquetes IP desde espacio de usuario.
- **OE3.** Encapsular el paquete IP dentro de un datagrama UDP (cliente) y reenviarlo al servidor VPN a través del túnel.
- **OE4.** Configurar el servidor VPN (interfaz TUN, reenvío IP) y el enrutamiento para alcanzar la red privada `192.168.60.0/24`.
- **OE5.** Manejar el tráfico en ambas direcciones usando `select()`.
- **OE6.** Extender el escenario a una VPN entre dos redes privadas y experimentar con la interfaz TAP (capa 2).

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
| SEED `Labsetup.zip` | Topología y archivos `docker-compose` del VPN Lab |
| Docker + Docker Compose | Topología con cliente, servidor VPN y host destino |
| Python 3 + Scapy | Implementación del túnel TUN/TAP |
| Wireshark / tcpdump | Captura de paquetes encapsulados |

> [!NOTE]
> **Provisión de materiales**
>
> El estudiante adquiere o instala por su cuenta el equipo personal (laptop), las máquinas virtuales (VirtualBox, SEED VM, Kali Linux, contenedores Docker) y todo el software listado arriba. El laboratorio de la Carrera de Telecomunicaciones provee el espacio físico, el mobiliario y **acceso a Internet supervisado** para la descarga de imágenes, paquetes y consulta de documentación durante la sesión. El laboratorio no entrega equipos de cómputo personales ni licencias de software.

## Entorno de Laboratorio

> **Figura 1.** Topología del laboratorio P-16: túnel VPN entre Host U y red privada.  
> *(diagrama vectorial; se reproduce en el PDF del manual)*

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

El laboratorio se ejecuta sobre contenedores Docker. Descargue `Labsetup.zip` desde el sitio de SEED, descomprímalo e ingrese a la carpeta `Labsetup`. El archivo `docker-compose.yml` define la topología de la Figura 1.

### Tarea 1 — Configuración de la red

Construya e inicie la topología de contenedores y verifique la conectividad. La SEED VM ya incluye alias para Docker Compose y para abrir una *shell* dentro de un contenedor.

**Listado 1.** Levantar la topología y abrir una shell

```bash
# Construir e iniciar los contenedores
$ dcbuild        # alias de: docker-compose build
$ dcup           # alias de: docker-compose up

# En otra terminal: listar contenedores y entrar a uno
$ dockps         # alias de: docker ps --format "{{.ID}} {{.Names}}"
b1004832e275  hostA-10.9.0.5     (Host U / Cliente VPN)
0af4ea7a3e2e  router             (Servidor VPN / Router)
9652715c8e0a  hostB-192.168.60.5 (Host V)

$ docksh b1      # alias de: docker exec -it <id> /bin/bash
```

> [!NOTE]
> **Captura de paquetes**
>
> Puede usar `tcpdump -i eth0 -n` dentro de un contenedor, o ejecutar `tcpdump`/Wireshark en la VM seleccionando la interfaz `br-...` de la red Docker correspondiente.

**Pruebas de conectividad inicial.** Verifique que:

- Host U puede comunicarse con el Servidor VPN.
- El Servidor VPN puede comunicarse con Host V.
- Host U *no* puede comunicarse directamente con Host V (la red `192.168.60.0/24` no es alcanzable aún).
- Con `tcpdump` en el router puede capturar tráfico en cada red.

### Tarea 2 — Crear y configurar la interfaz TUN

El túnel se construye sobre la tecnología TUN. El siguiente programa base (`tun.py`) crea una interfaz TUN; lo modificaremos a lo largo de la práctica.

**Listado 2.** Creación de una interfaz TUN (`tun.py`)

```python
#!/usr/bin/env python3
import fcntl, struct, os, time
from scapy.all import *

TUNSETIFF = 0x400454ca
IFF_TUN   = 0x0001
IFF_TAP   = 0x0002
IFF_NO_PI = 0x1000

# Crear la interfaz tun
tun = os.open("/dev/net/tun", os.O_RDWR)
ifr = struct.pack('16sH', b'tun
ifname_bytes = fcntl.ioctl(tun, TUNSETIFF, ifr)

# Obtener el nombre de la interfaz
ifname = ifname_bytes.decode('UTF-8')[:16].strip("\x00")
print("Interface Name: {}".format(ifname))

while True:
    time.sleep(10)
```

#### Tarea 2.a — Nombre de la interfaz

Haga el programa ejecutable y ejecútelo como `root` en Host U. Quedará bloqueado; desde otra *shell* liste las interfaces y observe que aparece `tun0`. Modifique `tun.py` para que el prefijo del nombre sea su **apellido** (p. ej. `smith`) en lugar de `tun`.

**Listado 3.** Ejecutar y observar la interfaz TUN

```bash
# chmod a+x tun.py
# tun.py
# ip address          # debe aparecer una interfaz tun0
```

#### Tarea 2.b — Activar la interfaz TUN

La interfaz aún no es utilizable: hay que asignarle una dirección IP y levantarla. Puede hacerlo manualmente o automatizarlo dentro del programa.

**Listado 4.** Configuración manual de la interfaz

```bash
# ip addr add 192.168.53.99/24 dev tun0
# ip link set dev tun0 up
```

**Listado 5.** Automatizar la configuración en tun.py

```python
os.system("ip addr add 192.168.53.99/24 dev {}".format(ifname))
os.system("ip link set dev {} up".format(ifname))
```

#### Tarea 2.c — Leer de la interfaz TUN

Todo lo que sale de la interfaz TUN es un paquete IP. Convierta los datos recibidos en un objeto Scapy `IP` e imprima un resumen. Reemplace el bucle `while` de `tun.py` por:

**Listado 6.** Leer paquetes de la interfaz TUN

```python
while True:
    # Obtener un paquete de la interfaz tun
    packet = os.read(tun, 2048)
    if packet:
        ip = IP(packet)
        print(ip.summary())
```

Experimente y describa sus observaciones:

- En Host U, haga `ping` a una IP de la red `192.168.53.0/24`. ¿Qué imprime el programa? ¿Por qué?
- En Host U, haga `ping` a una IP de la red interna `192.168.60.0/24`. ¿Imprime algo? ¿Por qué?

#### Tarea 2.d — Escribir en la interfaz TUN

Lo que la aplicación escribe en la interfaz aparece en el kernel como un paquete IP. El ejemplo construye un paquete y lo inyecta en la interfaz:

**Listado 7.** Escribir un paquete en la interfaz TUN

```python
# Enviar un paquete falsificado por la interfaz tun
newip  = IP(src='1.2.3.4', dst=ip.src)
newpkt = newip/ip.payload
os.write(tun, bytes(newpkt))
```

Modifique el código para que, si el paquete leído es una solicitud *ICMP echo request*, construya el *echo reply* correspondiente y lo escriba en la interfaz; presente evidencia de que funciona. Pruebe también escribir datos arbitrarios (no un paquete IP) y reporte lo observado.

### Tarea 3 — Enviar el paquete IP al servidor por un túnel

Ahora se coloca el paquete leído de la interfaz TUN dentro del *payload* de un datagrama UDP y se envía al Servidor VPN (IP tunneling).

**Programa servidor (`tun_server.py`).** Servidor UDP estándar que escucha en el puerto `9090`, interpreta el payload como un paquete IP y muestra su origen/destino.

**Listado 8.** Servidor del túnel (`tun_server.py`)

```python
#!/usr/bin/env python3
from scapy.all import *

IP_A = "0.0.0.0"
PORT = 9090

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((IP_A, PORT))

while True:
    data, (ip, port) = sock.recvfrom(2048)
    print("{}:{} --> {}:{}".format(ip, port, IP_A, PORT))
    pkt = IP(data)
    print("   Inside: {} --> {}".format(pkt.src, pkt.dst))
```

**Programa cliente (`tun_client.py`).** Es `tun.py` renombrado; en lugar de imprimir el paquete, lo envía por UDP al servidor. `SERVER_IP` y `SERVER_PORT` son la dirección y puerto del servidor.

**Listado 9.** Cliente del túnel (`tun_client.py`)

```python
# Crear un socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    # Obtener un paquete de la interfaz tun
    packet = os.read(tun, 2048)
    if packet:
        # Enviar el paquete por el túnel
        sock.sendto(packet, (SERVER_IP, SERVER_PORT))
```

**Pruebas.** Ejecute el servidor en VPN Server y el cliente en Host U. Haga `ping` a una IP de `192.168.53.0/24`: ¿qué muestra el servidor? Para alcanzar la red privada `192.168.60.0/24` hay que enrutar ese tráfico hacia la interfaz TUN del cliente:

**Listado 10.** Enrutar la red privada por el túnel

```bash
# ip route add <network> dev <interface> via <router ip>
# ip route add 192.168.60.0/24 dev tun0
```

Demuestre que al hacer `ping` a una IP de `192.168.60.0/24`, los paquetes ICMP son recibidos por `tun_server.py` a través del túnel.

### Tarea 4 — Configurar el servidor VPN

Tras recibir el paquete del túnel, el servidor debe entregarlo al kernel para que lo enrute a su destino final. Esto requiere una interfaz TUN en el servidor (como en la Tarea 2). Modifique `tun_server.py` para:

1. Crear y configurar una interfaz TUN.
2. Obtener los datos del socket y tratarlos como un paquete IP.
3. Escribir el paquete en la interfaz TUN.

Antes de ejecutarlo, habilite el **reenvío IP** para que el servidor actúe como gateway (ya configurado en el contenedor `router` vía `docker-compose.yml`):

**Listado 11.** Habilitar reenvío IP (sysctl)

```bash
sysctls:
    - net.ipv4.ip_forward=1
```

**Prueba.** Haga `ping` a Host V desde Host U. Es suficiente con mostrar (Wireshark/`tcpdump`) que los paquetes ICMP *llegan* a Host V; aún no regresarán a Host U.

### Tarea 5 — Manejo de tráfico en ambas direcciones

El túnel es por ahora unidireccional. Para tunelizar también el tráfico de retorno, cliente y servidor deben leer de *dos* descriptores (la interfaz TUN y el socket) sin malgastar CPU. Se usa `select()` para monitorizar ambos a la vez:

**Listado 12.** Monitorizar TUN y socket con select()

```python
# Se asume que sock y tun ya fueron creados.
while True:
    # Bloquea hasta que al menos una interfaz esté lista
    ready, _, _ = select.select([sock, tun], [], [])
    for fd in ready:
        if fd is sock:
            data, (ip, port) = sock.recvfrom(2048)
            pkt = IP(data)
            print("From socket <==: {} --> {}".format(pkt.src, pkt.dst))
            os.write(tun, bytes(pkt))
        if fd is tun:
            packet = os.read(tun, 2048)
            pkt = IP(packet)
            print("From tun  ==>: {} --> {}".format(pkt.src, pkt.dst))
            sock.sendto(packet, (SERVER_IP, SERVER_PORT))
```

Complete el código en cliente y servidor. Con esto el túnel VPN (sin cifrar) queda completo. Muestre evidencia en Wireshark con `ping` y `telnet`, señalando cómo fluyen los paquetes.

### Tarea 6 — Experimento de ruptura del túnel

Desde Host U, abra una sesión `telnet` a Host V. Manteniéndola activa, **rompa** el túnel deteniendo `tun_client.py` o `tun_server.py`. Escriba en la ventana `telnet`: ¿aparece lo que teclea? ¿Qué ocurre con la conexión TCP? Reconecte luego ambos programas (reconfigurando interfaz TUN y rutas) y observe qué sucede con la conexión `telnet` una vez restablecido el túnel. Explique.

### Tarea 7 — Experimento de enrutamiento en Host V

En una VPN real el tráfico de retorno debe volver por el mismo túnel. En esta topología, Host V enruta por defecto todo (excepto `192.168.60.0/24`) hacia el servidor VPN. Para simular un escenario donde Host V está a varios saltos, elimine la entrada por defecto y añada una ruta específica de retorno hacia el servidor VPN:

**Listado 13.** Ajustar el enrutamiento de retorno en Host V

```bash
# ip route del default
# ip route add <network prefix> via <router ip>
```

### Tarea 8 — VPN entre dos redes privadas

En esta tarea se monta una VPN entre *dos* redes privadas (Figura 2), usando un archivo de composición distinto:

**Listado 14.** Usar la segunda topología

```bash
$ docker-compose -f docker-compose2.yml build
$ docker-compose -f docker-compose2.yml up
$ docker-compose -f docker-compose2.yml down
```

> **Figura 2.** Topología de la Tarea 8: VPN entre dos redes privadas.  
> *(diagrama vectorial; se reproduce en el PDF del manual)*

El objetivo es que el tráfico entre ambas redes privadas viaje por el túnel VPN. Reutilice el código anterior y configure el enrutamiento en ambos extremos. Aporte pruebas (Wireshark/`tcpdump`) de que los paquetes entre las dos redes efectivamente pasan por el túnel.

### Tarea 9 — Experimento con la interfaz TAP

A diferencia de TUN (capa 3, paquetes IP), el extremo de kernel de la interfaz **TAP** se conecta a la capa MAC, por lo que las tramas incluyen la cabecera Ethernet y se pueden recibir tramas ARP. Para crear una TAP se usa `IFF_TAP` en lugar de `IFF_TUN`; el resto del código es igual.

**Listado 15.** Crear y leer de una interfaz TAP

```python
tap = os.open("/dev/net/tun", os.O_RDWR)
ifr = struct.pack('16sH', b'tap
ifname_bytes = fcntl.ioctl(tap, TUNSETIFF, ifr)
ifname = ifname_bytes.decode('UTF-8')[:16].strip("\x00")

while True:
    packet = os.read(tap, 2048)
    if packet:
        ether = Ether(packet)
        print(ether.summary())
```

Configure la TAP como una TUN, haga `ping` a una IP de `192.168.53.0/24` y reporte sus observaciones. Como extensión, cuando reciba una solicitud ARP, genere la respuesta ARP correspondiente y escríbala en la interfaz TAP:

**Listado 16.** Responder solicitudes ARP en la TAP

```python
while True:
    packet = os.read(tap, 2048)
    if packet:
        ether = Ether(packet)
        print(ether.summary())

        # Enviar una respuesta ARP falsificada
        FAKE_MAC = "aa:bb:cc:dd:ee:ff"
        if ARP in ether and ether[ARP].op == 1:
            arp      = ether[ARP]
            newether = Ether(dst=ether.src, src=FAKE_MAC)
            newarp   = ARP(psrc=arp.pdst, hwsrc=FAKE_MAC,
                           pdst=arp.psrc, hwdst=ether.src, op=2)
            newpkt   = newether/newarp
            print("***** Fake response: {}".format(newpkt.summary()))
            os.write(tap, bytes(newpkt))
```

Pruebe con `arping` sobre la interfaz TAP y verifique que obtiene respuesta:

**Listado 17.** Probar la respuesta ARP con arping

```bash
# arping -I tap0 192.168.53.33
# arping -I tap0 1.2.3.4
```

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

- **P1.** ¿Cuál es la diferencia entre las interfaces TUN y TAP? Relacione su respuesta con lo observado en las Tareas 2 y 9.
- **P2.** En la Tarea 2.c, ¿por qué al hacer `ping` a `192.168.53.0/24` el programa imprime paquetes, pero no al hacer `ping` a `192.168.60.0/24` (antes de añadir la ruta)? Explique el rol de la tabla de enrutamiento.
- **P3.** Explique cómo los paquetes IP son encapsulados dentro del túnel UDP (IP tunneling). Apóyese en una captura de Wireshark.
- **P4.** ¿Por qué el túnel necesita manejar el tráfico en *ambas* direcciones y por qué se emplea `select()` en lugar de lecturas bloqueantes secuenciales?
- **P5.** En la Tarea 6, ¿qué le ocurre a la conexión TCP de `telnet` cuando el túnel se rompe y luego se restablece? ¿Por qué la conexión sobrevive (o no)?
- **P6.** ¿Por qué el MTU de la interfaz TUN debe ser menor que el de la interfaz física?
- **P7.** ¿Cómo se añadiría cifrado a este túnel? Mencione la biblioteca criptográfica y compare esta implementación con OpenVPN (similitudes y diferencias) [4].

## Actividad ABET — SO4: Responsabilidad Ética y Profesional

Esta actividad mide el **Student Outcome 4 (SO4)** de la Carrera de Telecomunicaciones requerido para la acreditación ABET: *habilidad para reconocer las responsabilidades éticas y profesionales en situaciones de ingeniería y emitir juicios fundamentados, considerando el impacto global, económico, medioambiental y social de las soluciones propuestas.* Representa el **30 %** de la valoración total de la práctica y evalúa los indicadores PI 4.1 y PI 4.2 mediante las preguntas SO4-1 y SO4-2.

- **SO4-1.** **[PI 4.1 — 15 %] Ética y responsabilidad profesional ante una exposición accidental de la interfaz de gestión VPN**
  Un ingeniero implementa un túnel VPN entre dos sedes corporativas. Después del despliegue en producción, descubre que por error dejó expuesta la interfaz de gestión del servidor VPN (puerto de administración) a Internet durante 48 horas. Un compañero sugiere no reportarlo para ``no generar alarma'' ya que ``nadie lo notó''. Analice:

  - **a)** Las **responsabilidades éticas del ingeniero**: cuándo, a quién y cómo reportar el error.
  - **b)** Los **principios de honestidad profesional y rendición de cuentas** que hacen inaceptable la ocultación, incluso cuando no se detectó explotación activa.
  - **c)** El **marco legal** (LOPDP, responsabilidad civil y contractual) si se comprueba posteriormente que la ventana de exposición fue aprovechada por un tercero.
- **SO4-2.** **[PI 4.2 — 15 %] Impacto integral de una implementación insegura de VPN en una empresa de salud**
  Una implementación insegura de VPN (sin autenticación mutua, claves hardcodeadas) en una empresa de salud ecuatoriana permite que un atacante intercepte el tráfico de telemedicina de 10 000 pacientes durante 48 horas, accediendo a consultas médicas en tiempo real. Analice:

  - **a)** **Económico:** multas bajo la LOPDP, costos de notificación a pacientes afectados, litigios por negligencia y daño reputacional.
  - **b)** **Social:** violación de la privacidad médica de pacientes, riesgo de discriminación (datos de enfermedades crónicas, salud mental) y erosión de la confianza en la telemedicina como herramienta de inclusión sanitaria.
  - **c)** **Ambiental:** consumo energético de la respuesta al incidente y del rediseño seguro de la infraestructura VPN.
  - **d)** **Contramedidas:** proponga **dos contramedidas técnicas** (autenticación mutua con certificados, Perfect Forward Secrecy) y **una política organizacional**, citando RFC 8446, NIST SP 800-77r1 o ISO/IEC 27001 con controles de A.10 (Criptografía).

## Discusión y conclusiones

A partir de los datos recolectados y del análisis realizado, elabore una discusión que responda al menos a las siguientes preguntas guía:

- **DC1.** ¿Se alcanzaron los objetivos planteados? Justifique cada uno con evidencia experimental concreta (capturas, métricas, salidas de comandos).
- **DC2.** ¿Qué limitaciones impone el entorno virtualizado a los resultados? ¿Cómo se trasladarían las observaciones a un escenario real de producción?
- **DC3.** ¿Qué contramedidas o controles de seguridad mitigan el ataque o refuerzan la defensa estudiada? Cite al menos una buena práctica de la industria, una RFC o un estándar (ISO/IEC, IEEE, NIST) pertinente.
- **DC4.** ¿Qué errores se cometieron durante la práctica y qué recomendaciones daría a futuros estudiantes para evitarlos?

Cierre con **conclusiones** (3–5 viñetas) que resuman los hallazgos principales y los vinculen explícitamente con los *Resultados de Aprendizaje* de la asignatura.

## Entregables

1. **Informe técnico** detallado con capturas de pantalla que describan lo realizado y observado en cada tarea (1–9), incluyendo capturas Wireshark/`tcpdump` del tráfico encapsulado y la explicación del flujo de los paquetes (`ping` y `telnet`). Las observaciones interesantes o sorprendentes deben explicarse. Bibliografía IEEE (≥3 fuentes).
2. **Código fuente** comentado de `tun_client.py` y `tun_server.py` (con `select()`), y del experimento TAP/ARP. Adjuntar código sin explicación no recibe puntaje.
3. **Respuestas a la Actividad ABET – SO4** (preguntas SO4-1 y SO4-2), integradas en el informe técnico con extensión de 1–2 páginas por pregunta y las fuentes citadas según norma IEEE.

## Rúbrica de Evaluación

1.4

**Tabla 3.** Rúbrica — P-16 (10 puntos)

| Criterio | Peso | Indicador | Descripción |
| --- | --- | --- | --- |
| Red e interfaz TUN | 11 % | Topología y TUN operativas | Contenedores levantados; `tun.py` crea, nombra y configura la interfaz (Tareas 1–2). |
| Túnel y servidor | 24 % | Tunneling bidireccional | Cliente/servidor encapsulan en UDP; reenvío IP y `select()` funcionando; `ping` llega a Host V (Tareas 3–5). |
| Enrutamiento | 11 % | Rutas configuradas | Tráfico hacia `192.168.60.0/24` fluye por el túnel; retorno enrutado (Tareas 3, 7). |
| VPN entre redes y TAP | 10 % | Escenarios extendidos | VPN entre dos redes privadas y experimento TAP/ARP documentados (Tareas 8–9). |
| Análisis e informe | 14 % | Evidencia y preguntas | Capturas que muestran el flujo; preguntas respondidas con fundamento técnico. |
| **ABET – SO4: Responsabilidad Ética y Profesional (30 %)** |   |   |   |
| PI 4.1 – Ética profesional | 15 % | Respuesta ética fundamentada | Aplica principios éticos y legales al escenario del incidente; la cadena de notificación está justificada. |
| PI 4.2 – Impacto integral | 15 % | Análisis de impacto | Evalúa impacto económico, social y ambiental con contramedidas técnicas y organizacionales, citando al menos un estándar internacional. |

1.25

**Tabla 4.** Escala ABET SO4 — P-16

| PI | No cumple<br>(0–59 %) | Cumple parcialmente<br>(60–69 %) | Cumple<br>(70–79 %) | Supera<br>(80–89 %) | Supera ampliamente<br>(90–100 %) |
| --- | --- | --- | --- | --- | --- |
| 4.1 | No aplica principios éticos ni profesionales al evaluar la situación de incidente. | Aplica de manera inconsistente los principios éticos; el análisis legal es superficial o erróneo. | Aplica de manera básica los principios éticos; menciona el marco legal ecuatoriano sin análisis profundo. | Aplica coherentemente su juicio ético y profesional; integra el COIP y la LOPDP con argumentación clara. | Aplica de manera ejemplar e integral su juicio ético; argumenta cada decisión con evidencia y normativas citadas con precisión. |
| 4.2 | No considera ninguno de los tres impactos (económico, social, ambiental). | Considera parcialmente uno o dos de los impactos; las contramedidas no citan estándares. | Considera los tres impactos de forma adecuada; propone contramedidas pertinentes con al menos un estándar citado. | Integra los tres impactos con análisis detallado y contramedidas bien fundamentadas en estándares internacionales. | Realiza una evaluación exhaustiva de los tres impactos; las contramedidas son innovadoras y se respaldan en múltiples estándares. |

## Referencias

1. Kent, Stephen and Seo, Karen, «Security Architecture for the Internet Protocol». RFC 4301, 2005.
2. Stallings, William, «Network Security Essentials: Applications and Standards». Pearson, 2017.
3. Du, Wenliang, «Computer & Internet Security: A Hands-on Approach». Independently published, 2019.
4. OpenVPN Inc., «OpenVPN Community Documentation». 2024. <https://openvpn.net/community-resources/>.

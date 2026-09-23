# P-09 · Exploración de Firewalls (Netfilter e iptables)

> Práctica del **Manual de Prácticas** de Seguridad en Redes · INGE-00107 · Universidad de Cuenca.  
> Documento generado desde el manual: no lo edite a mano (véase [`practicas/README.md`](README.md)).

| Campo | Valor |
| --- | --- |
| **Asignatura** | Seguridad en Redes |
| **Docente** | Dr. Fabián Astudillo-Salinas |
| **Unidad** | 700 – Firewalls |
| **Código** | INGE-00107 |
| **Modalidad** | Presencial |
| **Valoración** | 10 puntos |
| **Grupos** | Máx. 3 estudiantes |
| **Entrega** | Según calendario |
| **ABET** | SO4 – Responsabilidad Ética y Profesional (PI 4.1 y PI 4.2) — representa el 30 % de la valoración |

## Marco Teórico

Los fundamentos teóricos sintetizados en esta sección se basan en [1], [2]; se recomienda consultar dichas fuentes para una exposición más profunda. El procedimiento de laboratorio adapta el *Firewall Exploration Lab* de SEED [3].

### Módulos del Kernel Linux (LKM)

El procesamiento de paquetes en un firewall ocurre dentro del kernel. En el pasado, implementar un firewall exigía modificar y recompilar el kernel completo. Los sistemas Linux modernos ofrecen dos mecanismos que evitan esto: los **Módulos del Kernel Cargables** (*Loadable Kernel Modules*, LKM) y **Netfilter**.

Un LKM permite agregar o quitar funcionalidad del kernel en tiempo de ejecución, sin reiniciar el equipo. La parte de filtrado de paquetes de un firewall puede implementarse como un LKM.

### Netfilter y sus hooks

**Netfilter** está diseñado para facilitar la manipulación de paquetes por parte de usuarios autorizados. Lo logra implementando cinco puntos de enganche (*hooks*) dentro del kernel Linux, insertados en distintos lugares del camino que siguen los paquetes entrantes y salientes:

- `NF_INET_PRE_ROUTING` — paquetes recién llegados, antes del enrutamiento.
- `NF_INET_LOCAL_IN` — paquetes destinados a este host.
- `NF_INET_FORWARD` — paquetes que serán reenviados.
- `NF_INET_LOCAL_OUT` — paquetes generados localmente.
- `NF_INET_POST_ROUTING` — paquetes a punto de salir.

Para conectarse a un hook, se registra una función propia (dentro del LKM) en la estructura correspondiente de Netfilter. Cuando llega un paquete, la función es invocada y puede decidir si el paquete se acepta (`NF_ACCEPT`) o se descarta (`NF_DROP`).

### Antecedentes de iptables

Linux ya trae un firewall incorporado, también basado en Netfilter, llamado **iptables**. Técnicamente, la parte del kernel se llama *Xtables*, mientras que `iptables` es el programa de espacio de usuario que lo configura; sin embargo, `iptables` se usa habitualmente para referirse a ambos. Mientras que en la primera parte de esta práctica se *implementa* un firewall propio con Netfilter, en la segunda se *usa* el firewall ya integrado en Linux.

`iptables` organiza todas las reglas en una estructura jerárquica: **tabla** → **cadena** → **regla**. Hay tres tablas principales:

**Tabla 1.** Tablas y cadenas de iptables

| Tabla | Cadenas | Función |
| --- | --- | --- |
| `filter` | `INPUT`, `FORWARD`, `OUTPUT` | Filtrado de paquetes |
| `nat` | `PREROUTING`, `INPUT`, `OUTPUT`, `POSTROUTING` | Modificación de direcciones de red |
| `mangle` | `PREROUTING`, `INPUT`, `FORWARD`, `OUTPUT`, `POSTROUTING` | Modificación del contenido del paquete |

Cada cadena corresponde a un hook de Netfilter. La cadena `FORWARD` se ejecuta en el hook `NF_INET_FORWARD`, y la cadena `INPUT` en el hook `NF_INET_LOCAL_IN`.

> [!NOTE]
> **Nota sobre contenedores**
>
> Dado que todos los contenedores comparten el mismo kernel, los módulos del kernel son globales: si se carga un módulo desde un contenedor, afecta a todos los contenedores y al host. Por ello, los módulos del kernel (Tarea 1) se cargan directamente en la VM anfitriona (host VM), mientras que las tareas de iptables (Tareas 2–5) se ejecutan dentro de los contenedores.

**Objetivo general**
Comprender cómo funcionan los firewalls implementando uno propio con Módulos del Kernel Cargables (LKM) y Netfilter, y configurando reglas *stateless* y *stateful* con iptables, además de aplicaciones avanzadas (limitación de tráfico y balanceo de carga).
**Objetivos específicos**

- **OE1.** Compilar y cargar un módulo del kernel simple, y registrar funciones hook en Netfilter desde un LKM.
- **OE2.** Bloquear tráfico UDP, ICMP y Telnet mediante hooks de Netfilter y explorar en qué condición se invoca cada uno de los cinco hooks.
- **OE3.** Proteger el router, la red interna y los servidores internos con reglas iptables *stateless* (cadenas INPUT y FORWARD).
- **OE4.** Implementar un firewall *stateful* con el módulo conntrack.
- **OE5.** Limitar la tasa de tráfico con el módulo limit.
- **OE6.** Configurar balanceo de carga UDP con el módulo statistic.

## Entorno de Laboratorio

En esta práctica se usa la SEED Ubuntu 20.04 VM. La topología de contenedores Docker (Figura 1) se utiliza como entorno de prueba: los módulos del kernel (Tarea 1) se cargan en la VM anfitriona, y las reglas iptables (Tareas 2–5) se configuran dentro del contenedor **Router** (`10.9.0.11` / `192.168.60.11`).

> **Figura 1.** Topología del laboratorio P-09: LAN externa `10.9.0.0/24` y LAN interna `192.168.60.0/24` separadas por el router/firewall (adaptado de la Fig. 1 del SEED Firewall Exploration Lab).  
> *(diagrama vectorial; se reproduce en el PDF del manual)*

### Configuración del entorno con Docker

Descargue `Labsetup.zip` del sitio del laboratorio, descomprímalo y levante los contenedores:

**Listado 1.** Levantar el entorno y acceder a un contenedor

```bash
$ dcbuild        # docker-compose build (construir las imágenes)
$ dcup           # docker-compose up    (iniciar los contenedores)
$ dockps         # listar contenedores  (alias de docker ps)
$ docksh <id>    # shell en el contenedor (alias de docker exec)
```

## Actividades previas

- **AP1.** Leer el marco teórico de esta práctica y las referencias citadas.
- **AP2.** Verificar que la SEED Ubuntu 20.04 VM esté operativa con los *kernel headers* instalados (`sudo apt install linux-headers-$(uname -r)`).
- **AP3.** Verificar que Docker y Docker Compose estén instalados y funcionales (`docker-compose up`).
- **AP4.** Tomar una *snapshot* de la VM antes de iniciar la práctica.
- **AP5.** Revisar la Sección [Seguridad y normas generales del laboratorio](00-normas-generales.md#seguridad-y-normas-generales-del-laboratorio) (Seguridad y normas generales del laboratorio) y el manual de iptables (`man iptables`).

## Materiales y Equipos

| Recurso | Descripción |
| --- | --- |
| SEED Ubuntu 20.04 VM | Con *kernel headers* instalados |
| Docker + Docker Compose | Topología de red del laboratorio |
| GCC + `make` | Compilación de módulos del kernel |
| iptables + conntrack | Firewall stateless/stateful y seguimiento de conexiones |
| netcat (`nc`) | Generación de tráfico de prueba |
| Archivos del laboratorio | `Labsetup.zip` (SEED website) |

> [!NOTE]
> **Provisión de materiales**
>
> El estudiante adquiere o instala por su cuenta el equipo personal (laptop), las máquinas virtuales (VirtualBox, SEED VM, contenedores Docker) y todo el software listado arriba. El laboratorio de la Carrera de Telecomunicaciones provee el espacio físico, el mobiliario y **acceso a Internet supervisado** para la descarga de imágenes, paquetes y documentación. No se entregan equipos personales ni licencias de software.

## Consideraciones de seguridad

Antes de iniciar, revise la Sección [Seguridad y normas generales del laboratorio](00-normas-generales.md#seguridad-y-normas-generales-del-laboratorio). Para esta práctica se destacan:

- **Riesgo de crash del kernel**: modificar el kernel con un módulo defectuoso puede colgarlo. Haga *backup* frecuente de sus archivos. Asegúrese de llamar a `nf_unregister_net_hook` en la función de limpieza (`removeFilter`) para cada hook registrado; de lo contrario, al descargar el módulo se producirá un *kernel panic*.
- **Restauración de iptables**: al terminar cada tarea, restaure la tabla `filter` (`iptables -F`, `iptables -P OUTPUT ACCEPT`, `iptables -P INPUT ACCEPT`) o reinicie el contenedor con `docker restart <ID>`.
- **Aislamiento de red obligatorio**: todo el tráfico de prueba debe permanecer dentro de la VM y los contenedores. Prohibido ejecutar comandos contra redes externas.
- **Snapshots**: tome una instantánea antes de cargar cualquier módulo del kernel o cambiar la política por defecto.
- **Marco legal**: COIP Arts. 229 y 234; Ley Orgánica de Protección de Datos Personales.

> [!WARNING]
> **Riesgos específicos de la práctica**
>
> Un hook registrado y no desregistrado correctamente provoca un *kernel panic* al hacer `rmmod`: verifique siempre que `removeFilter` desregistre **todos** los hooks. Asimismo, aplicar una política por defecto DROP sin las reglas adecuadas puede dejar al contenedor sin conectividad: tenga preparado el comando de restauración. Docker gestiona la tabla `nat`; **no** ejecute `iptables -t nat -F`, pues rompería los contenedores (use `iptables -F` para limpiar solo la tabla `filter`).

## Procedimiento

### Tarea 1 — Implementar un firewall simple

#### Tarea 1.A — Implementar un módulo del kernel simple

LKM permite agregar nuevos módulos al kernel en tiempo de ejecución. El siguiente módulo imprime `"Hello World!"` al cargarse y `"Bye-bye World!"` al quitarse. Los mensajes no aparecen en pantalla; se escriben en `/var/log/syslog` y se pueden ver con `dmesg`.

**Listado 2.** hello.c — módulo básico (incluido en los archivos del laboratorio)

```c
#include <linux/module.h>
#include <linux/kernel.h>

int initialization(void)
{
    printk(KERN_INFO "Hello World!\n");
    return 0;
}

void cleanup(void)
{
    printk(KERN_INFO "Bye-bye World!.\n");
}

module_init(initialization);
module_exit(cleanup);
```

Para compilarlo, cree un archivo `Makefile` con el siguiente contenido (asegúrese de usar tabulaciones, no espacios, antes de `make`):

**Listado 3.** Makefile para hello.c

```makefile
obj-m += hello.o

all:
    make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules

clean:
    make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean
```

Ejecute `make` para compilar. El módulo resultante es `hello.ko`. Luego use los siguientes comandos:

**Listado 4.** Cargar, listar y quitar el módulo

```bash
$ sudo insmod hello.ko      # cargar el módulo
$ lsmod | grep hello        # listar módulos
$ sudo rmmod hello          # quitar el módulo
$ dmesg                     # ver los mensajes del kernel
$ sudo dmesg                # (Ubuntu 22.04 requiere superusuario)
```

También puede usar `modinfo hello.ko` para ver información del módulo.

> [!NOTE]
> **Nota para Apple Silicon (Ubuntu 22.04)**
>
> Si `gcc-12` no está instalado, instálelo con:
> `sudo apt install gcc-12`

**Tarea:** Compile este módulo del kernel en su VM y ejecútelo. Muestre los resultados en el informe. *No use contenedores para esta tarea.*

#### Tarea 1.B — Implementar un firewall simple con Netfilter

En esta tarea se escribe el programa de filtrado de paquetes como un LKM y se inserta en el camino de procesamiento de paquetes del kernel mediante Netfilter.

##### Registro de funciones hook en Netfilter.

Para registrar un hook se prepara una estructura de datos `nf_hook_ops` y se establecen los parámetros necesarios: el nombre de la función () y el número de hook (). El número de hook es uno de los cinco definidos en Netfilter; la función especificada será invocada cuando un paquete alcance ese punto. Tras preparar la estructura, se adjunta el hook a Netfilter ().

**Listado 5.** Listing 2: Registrar funciones hook en netfilter

```c
static struct nf_hook_ops hook1, hook2;

int registerFilter(void) {
    printk(KERN_INFO "Registering filters.\n");

    // Hook 1
    hook1.hook     = printInfo;               /* (1) */
    hook1.hooknum  = NF_INET_LOCAL_IN;        /* (2) */
    hook1.pf       = PF_INET;
    hook1.priority = NF_IP_PRI_FIRST;
    nf_register_net_hook(&init_net, &hook1);  /* (3) */

    // Hook 2
    hook2.hook     = blockUDP;
    hook2.hooknum  = NF_INET_POST_ROUTING;
    hook2.pf       = PF_INET;
    hook2.priority = NF_IP_PRI_FIRST;
    nf_register_net_hook(&init_net, &hook2);

    return 0;
}

void removeFilter(void) {
    printk(KERN_INFO "The filters are being removed.\n");
    nf_unregister_net_hook(&init_net, &hook1);
    nf_unregister_net_hook(&init_net, &hook2);
}

module_init(registerFilter);
module_exit(removeFilter);
```

> [!NOTE]
> **Diferencia entre Ubuntu 16.04 y 20.04**
>
> **Listado 6.** APIs de registro según versión de Ubuntu
>
> ```c
> // Registro de hook:
> nf_register_hook(&nfho);                // Ubuntu 16.04
> nf_register_net_hook(&init_net, &nfho); // Ubuntu 20.04
>
> // Desregistro de hook:
> nf_unregister_hook(&nfho);                // Ubuntu 16.04
> nf_unregister_net_hook(&init_net, &nfho); // Ubuntu 20.04
> ```

##### Funciones hook.

Cuando Netfilter invoca una función hook, le pasa tres argumentos, incluyendo un puntero al paquete actual (`skb`). En la línea se obtiene el número de hook del argumento `state`. En la línea se usa `ip_hdr()` para obtener el puntero a la cabecera IP y luego `%pI4` para imprimir las IPs en la línea .

**Listado 7.** Listing 3: Función hook de ejemplo (imprime información del paquete)

```c
unsigned int printInfo(void *priv, struct sk_buff *skb,
                       const struct nf_hook_state *state)
{
    struct iphdr *iph;
    char *hook;

    switch (state->hook) {                       /* (1) */
      case NF_INET_LOCAL_IN:
            printk("*** LOCAL_IN"); break;
      .. (código omitido) ...
    }

    iph = ip_hdr(skb);                           /* (2) */
    printk("   
           &(iph->saddr), &(iph->daddr));        /* (3) */
    return NF_ACCEPT;
}
```

Para obtener cabeceras de otros protocolos:

**Listado 8.** Obtener cabeceras de protocolos

```c
struct iphdr   *iph   = ip_hdr(skb)   // #include <linux/ip.h>
struct tcphdr  *tcph  = tcp_hdr(skb)  // #include <linux/tcp.h>
struct udphdr  *udph  = udp_hdr(skb)  // #include <linux/udp.h>
struct icmphdr *icmph = icmp_hdr(skb) // #include <linux/icmp.h>
```

##### Bloqueo de paquetes.

Para bloquear un paquete, la función hook debe retornar `NF_DROP`; de lo contrario, retorna `NF_ACCEPT`. El siguiente ejemplo bloquea paquetes UDP cuyo destino sea `8.8.8.8` y puerto `53` (consultas DNS al servidor de Google):

**Listado 9.** Listing 4: Ejemplo de bloqueo de UDP

```c
unsigned int blockUDP(void *priv, struct sk_buff *skb,
                      const struct nf_hook_state *state)
{
    struct iphdr  *iph;
    struct udphdr *udph;
    u32   ip_addr;
    char  ip[16] = "8.8.8.8";

    // Convierte la IP a 32 bits
    in4_pton(ip, -1, (u8 *)&ip_addr, '\0', NULL); /* (1) */

    iph = ip_hdr(skb);
    if (iph->protocol == IPPROTO_UDP) {
        udph = udp_hdr(skb);
        if (iph->daddr == ip_addr &&
            ntohs(udph->dest) == 53) {           /* (2) */
            printk(KERN_DEBUG "****Dropping 
                               &(iph->daddr), port);
            return NF_DROP;                       /* (3) */
        }
    }
    return NF_ACCEPT;                             /* (4) */
}
```

En la línea se convierte la IP en formato *dotted decimal* (`1.2.3.4`) a un número binario de 32 bits (`0x01020304`), para poder compararlo con el valor binario almacenado en el paquete. La línea compara la IP y el puerto destino con los valores de la regla. Si coinciden, se retorna `NF_DROP` (); de lo contrario, `NF_ACCEPT` ().

##### Tareas a realizar.

El código de ejemplo completo se llama `seedFilter.c` e incluye un `Makefile`; ambos están en la carpeta `Files/packet_filter` de los archivos del laboratorio. Realice cada una de las siguientes tareas de forma independiente:

1. **Compile, cargue y pruebe el filtro UDP.** Compile `seedFilter.c` con el `Makefile` provisto, cárguelo en el kernel y demuestre que el firewall funciona. Use el siguiente comando para generar paquetes UDP hacia `8.8.8.8` (servidor DNS de Google); si el firewall funciona, la solicitud será bloqueada:

   **Listado 10.** Probar el bloqueo de DNS

   ```bash
   dig @8.8.8.8 www.example.com
   ```
2. **Explore los cinco hooks de Netfilter.** Conecte la función `printInfo` a **todos** los hooks de Netfilter. Use sus resultados experimentales para explicar en qué condición es invocado cada hook:

   **Listado 11.** Macros de los cinco hooks

   ```c
   NF_INET_PRE_ROUTING
   NF_INET_LOCAL_IN
   NF_INET_FORWARD
   NF_INET_LOCAL_OUT
   NF_INET_POST_ROUTING
   ```
3. **Bloquee ping y Telnet.** Implemente dos hooks adicionales para: (1) impedir que otras computadoras hagan ping a la VM, y (2) impedir que otras computadoras se conecten por Telnet (puerto TCP 23). Use dos funciones hook distintas, pero regístrelas en el **mismo** hook de Netfilter. Para probar, desde el contenedor `10.9.0.5`:

   **Listado 12.** Prueba desde el contenedor externo

   ```bash
   ping 10.9.0.1
   telnet 10.9.0.1
   ```

   La dirección `10.9.0.1` es la IP asignada a la VM; puede estar codificada de forma fija en las reglas.

### Tarea 2 — Reglas de firewall sin estado (iptables)

A partir de aquí se usa el firewall integrado de Linux. La estructura general de un comando es:

**Listado 13.** Estructura general de iptables

```bash
iptables -t <tabla> -<operación> <cadena> <regla> -j <destino>
         ---------- -------------------- ------- ------------
           Tabla          Cadena          Regla      Acción
```

**Listado 14.** Comandos iptables de referencia

```bash
# Listar reglas de una tabla (sin números de línea)
iptables -t nat -L -n
# Listar con números de línea
iptables -t filter -L -n --line-numbers
# Eliminar la regla número 2 de la cadena INPUT
iptables -t filter -D INPUT 2
# Descartar todo paquete entrante que coincida con <regla>
iptables -t filter -A INPUT <regla> -j DROP
```

#### Tarea 2.A — Proteger el Router

En esta tarea configuramos reglas para impedir que máquinas externas accedan al contenedor **Router**, excepto mediante ping. Ejecute los siguientes comandos **en el contenedor Router**:

**Listado 15.** Reglas para proteger el Router

```bash
iptables -A INPUT  -p icmp --icmp-type echo-request -j ACCEPT
iptables -A OUTPUT -p icmp --icmp-type echo-reply   -j ACCEPT
iptables -P OUTPUT DROP     # política por defecto OUTPUT: DROP
iptables -P INPUT  DROP     # política por defecto INPUT:  DROP
```

Desde `10.9.0.5`, verifique:

1. ¿Puede hacer ping al Router?
2. ¿Puede conectarse por Telnet al Router? (hay un servidor Telnet activo en todos los contenedores; cuenta `seed`, contraseña `dees`).

Reporte su observación y explique cada regla.

**Limpieza.** Antes de la siguiente tarea, restaure la tabla:

**Listado 16.** Restaurar tabla filter

```bash
iptables -F
iptables -P OUTPUT ACCEPT
iptables -P INPUT  ACCEPT
```

#### Tarea 2.B — Proteger la Red Interna

Configuraremos reglas en la cadena FORWARD del Router para proteger la red interna `192.168.60.0/24`. Las cadenas INPUT y OUTPUT tienen dirección clara, pero FORWARD es bidireccional: todos los paquetes entre redes internas y externas la atraviesan. Para indicar la dirección use `-i xyz` (entrada por interfaz `xyz`) o `-o xyz` (salida). Identifique los nombres de interfaz con `ip addr`.

Implemente las siguientes restricciones para el tráfico ICMP:

1. Los hosts externos **no** pueden hacer ping a los hosts internos.
2. Los hosts externos **sí** pueden hacer ping al Router.
3. Los hosts internos **sí** pueden hacer ping a los externos.
4. Todos los demás paquetes entre redes interna y externa deben ser bloqueados.

Use la opción `-p icmp` con sus parámetros. Ejecute `"iptables -p icmp -h"` para ver las opciones. Ejemplo:

**Listado 17.** Ejemplo: bloquear echo-request en FORWARD

```bash
iptables -A FORWARD -p icmp --icmp-type echo-request -j DROP
```

Incluya en el informe las capturas que demuestren que el firewall funciona. Al terminar, limpie la tabla o reinicie el contenedor.

#### Tarea 2.C — Proteger Servidores Internos

Queremos proteger los servidores TCP dentro de `192.168.60.0/24`. Los objetivos son:

1. Todos los hosts internos corren un servidor Telnet (puerto 23). Los hosts externos solo pueden acceder al servidor Telnet de `192.168.60.5`, no al de los otros hosts internos.
2. Los hosts externos no pueden acceder a otros servidores internos.
3. Los hosts internos pueden acceder a todos los servidores internos.
4. Los hosts internos no pueden acceder a servidores externos.
5. **No** se permite usar el mecanismo de seguimiento de conexiones (conntrack) en esta tarea.

Use la opción `-p tcp` con sus parámetros. Ejecute `"iptables -p tcp -h"` para ver las opciones. Ejemplo:

**Listado 18.** Ejemplo: permitir TCP desde eth0 con puerto origen 5000

```bash
iptables -A FORWARD -i eth0 -p tcp --sport 5000 -j ACCEPT
```

Al terminar, limpie la tabla o reinicie el contenedor.

### Tarea 3 — Seguimiento de Conexiones y Firewall con Estado

Los firewalls sin estado (Tarea 2) inspeccionan cada paquete de forma independiente. Sin embargo, los paquetes suelen ser parte de una conexión TCP o de un flujo ICMP/UDP relacionado. Tratarlos independientemente puede llevar a reglas incorrectas o complicadas. Un **firewall con estado** mantiene información de estado de cada conexión.

#### Tarea 3.A — Experimento con el Seguimiento de Conexiones

Para implementar firewalls stateful necesitamos seguir las conexiones. El módulo `conntrack` del kernel lo hace. Verifique la información de seguimiento de conexiones en el contenedor Router:

**Listado 19.** Ver tabla de conexiones

```bash
# conntrack -L
```

El objetivo es usar experimentos para entender el concepto de ``conexión'' en este mecanismo, especialmente para ICMP y UDP (que, a diferencia de TCP, no tienen conexiones formales). Para cada experimento, describa su observación y explíquela. ¿Cuánto tiempo persiste el estado de la conexión?

- **Experimento ICMP:**

  **Listado 20.** Experimento ICMP con conntrack

  ```bash
  // Desde 10.9.0.5, enviar paquetes ICMP:
  # ping 192.168.60.5
  ```
- **Experimento UDP:**

  **Listado 21.** Experimento UDP con conntrack

  ```bash
  // En 192.168.60.5, iniciar servidor UDP netcat:
  # nc -lu 9090
  // En 10.9.0.5, enviar paquetes UDP:
  # nc -u 192.168.60.5 9090
  <escriba algo y presione Enter>
  ```
- **Experimento TCP:**

  **Listado 22.** Experimento TCP con conntrack

  ```bash
  // En 192.168.60.5, iniciar servidor TCP netcat:
  # nc -l 9090
  // En 10.9.0.5, conectar con TCP:
  # nc 192.168.60.5 9090
  <escriba algo y presione Enter>
  ```

#### Tarea 3.B — Configurar un Firewall con Estado

Ahora configuraremos reglas basadas en el estado de la conexión. La opción `-m conntrack` indica el uso del módulo conntrack. `–ctstate ESTABLISHED,RELATED` indica que el paquete pertenece a una conexión existente o relacionada:

**Listado 23.** Regla stateful: permitir paquetes de conexiones establecidas

```bash
iptables -A FORWARD -p tcp -m conntrack \
         --ctstate ESTABLISHED,RELATED -j ACCEPT
```

Esta regla no cubre los paquetes SYN (que inician una conexión nueva y no pertenecen a ninguna conexión establecida). Sin ellos no se puede crear ninguna conexión. Agregue una regla para aceptar SYN entrantes al puerto 8080 desde la interfaz `eth0`:

**Listado 24.** Aceptar SYN para conexiones nuevas al puerto 8080

```bash
iptables -A FORWARD -p tcp -i eth0 --dport 8080 --syn \
         -m conntrack --ctstate NEW -j ACCEPT
```

Finalmente, establezca la política por defecto de FORWARD en DROP:

**Listado 25.** Política por defecto DROP en FORWARD

```bash
iptables -P FORWARD DROP
```

**Tareas:**

1. Reescriba las reglas de la Tarea 2.C usando el mecanismo de seguimiento de conexiones. Esta vez, **permita que los hosts internos visiten cualquier servidor externo** (lo cual no era posible en la Tarea 2.C). Escriba las reglas con conntrack.
2. Piense cómo implementar las mismas reglas *sin* conntrack (no es necesario implementarlas, solo describa el razonamiento).
3. Compare ambos enfoques: ventajas y desventajas de cada uno.

Al terminar, limpie todas las reglas.

### Tarea 4 — Limitación del Tráfico de Red

Además de bloquear paquetes, iptables puede **limitar la cantidad** de paquetes que atraviesan el firewall. Esto se hace con el módulo `limit`. Ejecute `"iptables -m limit -h"` para ver el manual:

**Listado 26.** Ayuda del módulo limit

```bash
$ iptables -m limit -h
limit match options:
--limit avg    max promedio: por defecto 3/hora
               [Paquetes por segundo a menos que siga /sec /minute /hour /day]
--limit-burst  número para coincidir en ráfaga, por defecto 5
```

Ejecute los siguientes comandos en el Router y luego haga ping a `192.168.60.5` desde `10.9.0.5`. Describa su observación y explique si la segunda regla es necesaria o no, y por qué:

**Listado 27.** Limitar tráfico desde 10.9.0.5

```bash
iptables -A FORWARD -s 10.9.0.5 -m limit \
         --limit 10/minute --limit-burst 5 -j ACCEPT

iptables -A FORWARD -s 10.9.0.5 -j DROP
```

Realice el experimento con y sin la segunda regla y explique la diferencia.

### Tarea 5 — Balanceo de Carga

iptables es muy poderoso y tiene muchas aplicaciones más allá del firewall. En esta tarea lo usaremos para **balancear carga** entre tres servidores UDP en la red interna.

Primero, inicie el servidor en cada uno de los tres hosts internos (la opción `-k` permite recibir datagramas de múltiples hosts):

**Listado 28.** Iniciar servidores UDP en hosts internos

```bash
nc -luk 8080
```

El módulo `statistic` implementa el balanceo. Ejecute `"iptables -m statistic -h"` para ver sus modos: `random` y `nth`.

#### Modo nth (round-robin)

En el Router, la siguiente regla aplica a todos los paquetes UDP al puerto 8080. El modo `nth` con `–every 3 –packet 0` selecciona 1 de cada 3 paquetes (el primero) y cambia su IP y puerto destino a `192.168.60.5:8080`:

**Listado 29.** Balanceo de carga round-robin: primer servidor

```bash
iptables -t nat -A PREROUTING -p udp --dport 8080      \
         -m statistic --mode nth --every 3 --packet 0  \
         -j DNAT --to-destination 192.168.60.5:8080
```

Los paquetes que no coinciden con esta regla continúan sin modificación. Si envía un paquete UDP al puerto 8080 del Router, verá que uno de cada tres llega a `192.168.60.5`. Para probarlo, desde `10.9.0.5`:

**Listado 30.** Probar el balanceo de carga

```bash
// Desde 10.9.0.5:
echo hello | nc -u 10.9.0.11 8080
<Ctrl-C>
```

Agregue las reglas necesarias para que los tres hosts internos reciban aproximadamente la misma cantidad de paquetes. Explique las reglas.

#### Modo random

Implemente el balanceo usando el modo `random`. La siguiente regla selecciona un paquete con probabilidad P (reemplace P por un valor numérico):

**Listado 31.** Balanceo de carga con modo random

```bash
iptables -t nat -A PREROUTING -p udp --dport 8080       \
         -m statistic --mode random --probability P     \
         -j DNAT --to-destination 192.168.60.5:8080
```

Use este modo para implementar reglas de balanceo de carga que den a cada servidor interno aproximadamente el mismo tráfico. Explique los valores de P elegidos.

## Recolección y análisis de datos

Durante la ejecución del procedimiento, registre en su bitácora los datos solicitados a continuación. Las tablas siguientes forman parte del entregable, conforme a la Sección [Directrices generales para el informe técnico](00-normas-generales.md#directrices-generales-para-el-informe-técnico).

**Tabla 2.** Bitácora de comandos y observaciones — P-09

| # | Comando / Acción | Salida u observación relevante |
| --- | --- | --- |
| 1 | T1.A: `make` + `insmod hello.ko` + `dmesg` |   |
| 2 | T1.B: `seedFilter.ko` + `dig @8.8.8.8` |   |
| 3 | T1.B: printInfo en los 5 hooks; bloqueo ping/Telnet |   |
| 4 | T2: reglas INPUT/FORWARD (router, red, servidores) |   |
| 5 | T3: `conntrack -L` + reglas stateful |   |
| 6 | T4: `limit 10/minute` |   |
| 7 | T5: balanceo nth/random |   |

**Tabla 3.** Resultados clave / métricas obtenidas — P-09

| Métrica o evidencia | Valor | Comentario / unidad |
| --- | --- | --- |
| DNS bloqueado (`dig @8.8.8.8`) | Sí / No |   |
| Hooks invocados (ping desde externo) |   |   |
| Ping/Telnet bloqueados (Netfilter) | Sí / No |   |
| Ping bloqueado hacia host interno (iptables) | Sí / No |   |
| Estado ICMP/UDP/TCP en conntrack (duración) |   |   |
| Paquetes por servidor (balanceo nth/random) |   |   |

**Pautas para el análisis de los datos recolectados:**

- Explique en qué hook fue invocada `printInfo` para cada tipo de paquete (entrante, saliente, reenviado) y justifíquelo con el diagrama de Netfilter.
- Contraste cada regla iptables con el comportamiento observado y el marco teórico; explique las diferencias y anomalías.
- Para la Tarea 5, cuantifique la distribución del tráfico entre servidores y evalúe si es uniforme.

## Preguntas de Análisis

- **P1.** ¿Qué ventajas ofrece un LKM respecto a modificar y recompilar el kernel completo?
- **P2.** Explique los cinco hooks de Netfilter e indique cuál se invoca primero para un paquete destinado a la misma máquina.
- **P3.** Explique la función de `in4_pton` y por qué no se puede comparar directamente la cadena `"8.8.8.8"` con `iph->daddr`. ¿Qué diferencia hay entre `NF_DROP` y `NF_ACCEPT`?
- **P4.** ¿Qué relación existe entre las cadenas de iptables (`INPUT`, `FORWARD`, `OUTPUT`) y los hooks de Netfilter de la primera parte?
- **P5.** Explique la diferencia entre un firewall *stateless* y uno *stateful*. ¿En qué caso es necesario usar conntrack?
- **P6.** ¿Por qué la cadena FORWARD es bidireccional y cómo se usa `-i`/`-o` para distinguir la dirección?
- **P7.** En la Tarea 3.B, ¿por qué se necesita una regla adicional para los paquetes SYN además de la regla ESTABLISHED,RELATED?
- **P8.** ¿Qué diferencia hay entre `–limit` y `–limit-burst`? Explique cómo funciona el balanceo con el modo `nth` y cómo elegir las probabilidades del modo `random` con tres servidores.

## Actividad ABET — SO4: Responsabilidad Ética y Profesional

Esta actividad mide el **Student Outcome 4 (SO4)** de la Carrera de Telecomunicaciones requerido para la acreditación ABET: *habilidad para reconocer las responsabilidades éticas y profesionales en situaciones de ingeniería y emitir juicios fundamentados, considerando el impacto global, económico, medioambiental y social de las soluciones propuestas.* Representa el **30 %** de la valoración total de la práctica y evalúa los indicadores PI 4.1 y PI 4.2 mediante las preguntas SO4-1 y SO4-2.

- **SO4-1.** **[PI 4.1 — 15 %] Ética y responsabilidad profesional ante un error de configuración de firewall en infraestructura crítica**
  Un administrador de red configura reglas de iptables en el firewall de un hospital ecuatoriano y, por un error de orden en las reglas FORWARD, bloquea accidentalmente el servicio de telemedicina que atiende a 2 000 pacientes rurales diariamente. El error se descubre 3 horas después. Analice:

  - **a)** Las responsabilidades éticas del ingeniero: reporte inmediato vs. resolución silenciosa.
  - **b)** La cadena de notificación interna: a quién informar y en qué plazo, considerando que hay vidas en riesgo (pacientes sin acceso a telemedicina).
  - **c)** Las medidas preventivas éticas y técnicas para evitar errores críticos en configuraciones de firewall en infraestructura de salud (change management, entornos de prueba).
- **SO4-2.** **[PI 4.2 — 15 %] Impacto integral de una mala configuración de firewall en infraestructura de servicios públicos**
  Una empresa de servicios públicos (agua potable) configura incorrectamente su firewall, exponiendo los sistemas SCADA de control de potabilización a Internet durante 72 horas. Un atacante accede pero no causa daño físico; solo exfiltra datos de configuración. Analice:

  - **a)** **Económico:** costos de auditoría forense, refuerzo de la infraestructura, posibles multas de la ARCOTEL/entidades reguladoras de infraestructura crítica.
  - **b)** **Social:** riesgo potencial para la salud pública si un atacante hubiera modificado dosificaciones de cloro, pérdida de confianza en la seguridad de servicios esenciales.
  - **c)** **Ambiental:** consumo energético del incidente de seguridad y de las medidas de refuerzo (redundancia, sistemas de detección de intrusiones OT).
  - **d)** **Contramedidas:** dos técnicas (segmentación OT/IT, listas blancas en Netfilter) y una política organizacional, citando IEC 62443, NIST SP 800-82r3 o ISO/IEC 27019.

## Discusión y conclusiones

A partir de los datos recolectados y del análisis realizado, elabore una discusión que responda al menos a las siguientes preguntas guía:

- **DC1.** ¿Se alcanzaron los objetivos planteados? Justifique cada uno con evidencia experimental concreta (salidas de `dmesg`, reglas iptables, capturas, comportamiento del tráfico).
- **DC2.** ¿Qué limitaciones impone el entorno virtualizado? ¿Cómo cambiaría el comportamiento en un equipo físico en producción?
- **DC3.** ¿Qué estándares o buenas prácticas de la industria (RFC 2979, NIST SP 800-41, ISO/IEC 27033) se relacionan con el filtrado de paquetes a nivel de kernel y con las reglas implementadas?
- **DC4.** ¿Qué errores se cometieron durante la práctica y qué recomendaciones daría a futuros estudiantes para evitarlos?

Cierre con **conclusiones** (3–5 viñetas) que resuman los hallazgos principales vinculados a los *Resultados de Aprendizaje* de la asignatura.

## Entregables

1. **Informe técnico** con el código fuente del LKM, capturas de `dmesg`, todas las reglas iptables aplicadas, capturas de prueba y el análisis de cada tarea (1–5). Explique cada fragmento de código/regla (adjuntar sin explicar no recibe puntaje). Bibliografía IEEE (≥3 fuentes).
2. **Código fuente** comentado de `hello.c` y `seedFilter.c`, y **script de reglas iptables** comentado para las Tareas 2.C y 3.B.
3. **Respuestas a la Actividad ABET – SO4** (preguntas SO4-1 y SO4-2), integradas en el informe técnico con extensión de 1–2 páginas por pregunta y las fuentes citadas según norma IEEE.

## Rúbrica de Evaluación

1.4

**Tabla 4.** Rúbrica — P-09 (10 puntos)

| Criterio | Peso | Indicador | Descripción |
| --- | --- | --- | --- |
| Firewall con Netfilter (T1) | 18 % | LKM y hooks | `hello.ko` y `seedFilter.ko` funcionales; DNS, ping y Telnet bloqueados; los 5 hooks documentados sin *kernel panic*. |
| Reglas stateless (T2) | 17 % | INPUT/FORWARD | Router, red interna y servidores internos protegidos correctamente. |
| Firewall stateful (T3) | 14 % | conntrack activo | Tabla conntrack documentada; reglas ESTABLISHED/RELATED y NEW funcionales. |
| Limitación y balanceo (T4–T5) | 11 % | limit y statistic | Límite de paquetes verificado; tres servidores reciben tráfico equitativo (nth y random). |
| Análisis e informe | 10 % | Preguntas respondidas | Respuestas con fundamento técnico. |
| **ABET – SO4: Responsabilidad Ética y Profesional (30 %)** |   |   |   |
| PI 4.1 – Ética profesional | 15 % | Respuesta ética fundamentada | Aplica principios éticos y legales al escenario del incidente; la cadena de notificación está justificada. |
| PI 4.2 – Impacto integral | 15 % | Análisis de impacto | Evalúa impacto económico, social y ambiental con contramedidas técnicas y organizacionales, citando al menos un estándar internacional. |

1.25

**Tabla 5.** Escala ABET SO4 — P-09

| PI | No cumple<br>(0–59 %) | Cumple parcialmente<br>(60–69 %) | Cumple<br>(70–79 %) | Supera<br>(80–89 %) | Supera ampliamente<br>(90–100 %) |
| --- | --- | --- | --- | --- | --- |
| 4.1 | No aplica principios éticos ni profesionales al evaluar la situación de incidente. | Aplica de manera inconsistente los principios éticos; el análisis legal es superficial o erróneo. | Aplica de manera básica los principios éticos; menciona el marco legal ecuatoriano sin análisis profundo. | Aplica coherentemente su juicio ético y profesional; integra el COIP y la LOPDP con argumentación clara. | Aplica de manera ejemplar e integral su juicio ético; argumenta cada decisión con evidencia y normativas citadas con precisión. |
| 4.2 | No considera ninguno de los tres impactos (económico, social, ambiental). | Considera parcialmente uno o dos de los impactos; las contramedidas no citan estándares. | Considera los tres impactos de forma adecuada; propone contramedidas pertinentes con al menos un estándar citado. | Integra los tres impactos con análisis detallado y contramedidas bien fundamentadas en estándares internacionales. | Realiza una evaluación exhaustiva de los tres impactos; las contramedidas son innovadoras y se respaldan en múltiples estándares. |

## Referencias

1. The Netfilter Project, «netfilter/iptables project». 2024. <https://www.netfilter.org>.
2. Cheswick, William and Bellovin, Steven and Rubin, Aviel, «Firewalls and Internet Security: Repelling the Wily Hacker». Addison-Wesley, 2003.
3. Du, Wenliang, «Computer & Internet Security: A Hands-on Approach». Independently published, 2019.

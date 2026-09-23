# Prácticas de Seguridad en Redes

Las 18 prácticas del **Manual de Prácticas** de Seguridad en Redes · INGE-00107 · Universidad de Cuenca. Las instrucciones de cada
una están en el `README.md` de su carpeta, junto al entorno del laboratorio: se ven
al abrir la carpeta, sin salir de ella.

> [!IMPORTANT]
> Esas instrucciones **se generan desde el manual** (`main.tex`) con
> `scripts/practicas/manual_a_markdown.py`. Cualquier corrección se hace en el
> manual y se regenera; lo que se edite a mano se pierde en la siguiente
> regeneración. El PDF con el formato oficial, los diagramas y la bibliografía
> completa está en el Aula Virtual, sección *Bienvenida y guía del curso*.

## Antes de empezar

Lea las [normas generales del laboratorio](00-normas-generales.md): seguridad, marco legal,
carga horaria y las directrices del informe técnico. Se aplican a **todas** las
prácticas y cada una las da por sabidas.

## Índice

| Código | Práctica | Unidad | Entorno |
| --- | --- | --- | --- |
| **P-00** | [Inventario y Superficie de Ataque](../P-00-inventario-y-superficie-de-ataque) | 100 – Introducción a la seguridad de redes | no aplica |
| **P-01** | [Introducción al Pentesting](../P-01-introduccion-al-pentesting) | 200 – Introducción a pentesting | pendiente |
| **P-02** | [Criptografía de Clave Secreta](../P-02-criptografia-de-clave-secreta) | 300 – Criptografía de clave secreta | Docker |
| **P-03** | [Criptografía de Clave Pública (RSA)](../P-03-criptografia-de-clave-publica-rsa) | 300 – Criptografía de clave pública | Docker |
| **P-04** | [Ataque de Colisión MD5](../P-04-ataque-de-colision-md5) | 400 – Funciones hash de una vía | pendiente |
| **P-05** | [Detección y Suplantación de Paquetes](../P-05-deteccion-y-suplantacion-de-paquetes) | 500 – Detección y suplantación de paquetes | Docker |
| **P-06** | [Envenenamiento de Caché ARP](../P-06-envenenamiento-de-cache-arp) | 500 – Detección y suplantación | pendiente |
| **P-07** | [Ataque de Redirección ICMP](../P-07-ataque-de-redireccion-icmp) | 600 – Ataques al protocolo TCP | pendiente |
| **P-08** | [Ataques al Protocolo TCP](../P-08-ataques-al-protocolo-tcp) | 600 – Ataques al protocolo TCP | Docker |
| **P-09** | [Exploración de Firewalls (Netfilter e iptables)](../P-09-exploracion-de-firewalls-netfilter-e-iptables) | 700 – Firewalls | Docker |
| **P-10** | [Evasión de Firewalls](../P-10-evasion-de-firewalls) | 700 – Firewalls | pendiente |
| **P-11** | [Ataques al DNS Local](../P-11-ataques-al-dns-local) | 800 – Sistema DNS y ataques | Docker |
| **P-12** | [Ataques al DNS Remoto (Kaminsky)](../P-12-ataques-al-dns-remoto-kaminsky) | 800 – Sistema DNS y ataques | pendiente |
| **P-13** | [Ataque de DNS Rebinding (IoT)](../P-13-ataque-de-dns-rebinding-iot) | 800 – Sistema DNS y ataques | Docker |
| **P-14** | [Infraestructura DNS](../P-14-infraestructura-dns) | 800 – Sistema DNS y ataques | pendiente |
| **P-15** | [Extensiones de Seguridad DNS (DNSSEC)](../P-15-extensiones-de-seguridad-dns-dnssec) | 800 – Sistema DNS y ataques | pendiente |
| **P-16** | [Túnel VPN desde Cero](../P-16-tunel-vpn-desde-cero) | 900 – Redes privadas virtuales | Docker |
| **P-17** | [Redes Privadas Virtuales](../P-17-redes-privadas-virtuales) | 900 – Redes privadas virtuales | pendiente |

La columna **Entorno** dice qué hay en la carpeta: `Docker` si trae el laboratorio
listo para levantar, `código` si trae material de apoyo, `pendiente` si todavía no
se ha publicado y `no aplica` si la práctica se hace sobre la red del propio
laboratorio.

## Cómo se usa

1. Levante el entorno con lo que haya en la carpeta (`Labsetup/`, `docker-compose.yml`).
2. Siga el **Procedimiento**; el código de los listados es el mismo que el del manual.
3. Registre lo pedido en **Recolección y análisis de datos** y responda las
   **Preguntas de Análisis** y la **Actividad ABET**.
4. Entregue en el Aula Virtual lo que indique **Entregables**; la **Rúbrica** dice
   cómo se califica.

> [!WARNING]
> Todo el material es para uso **exclusivo en el entorno de laboratorio autorizado**.
> Ejecutar estas herramientas contra redes o equipos de terceros sin autorización
> escrita puede constituir delito (COIP, Arts. 229 y 234).

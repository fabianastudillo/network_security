"""
ElGamal Public Key Encryption – Animated Visualization
Genera frames estáticos para visualizar paso a paso.
Salva como PNG y genera GIF animado.
"""

import random
import hashlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from PIL import Image
import os

# ─────────────────────────────────────────────
# Crypto core
# ─────────────────────────────────────────────

def symmetric_encrypt(key_bytes, plaintext):
    keystream = b""
    counter = 0
    while len(keystream) < len(plaintext):
        keystream += hashlib.sha256(key_bytes + counter.to_bytes(4, "big")).digest()
        counter += 1
    return bytes(a ^ b for a, b in zip(plaintext, keystream))

def derive_key(K):
    return hashlib.sha256(K.to_bytes((K.bit_length() + 7) // 8, "big")).digest()

# ─────────────────────────────────────────────
# Parameters
# ─────────────────────────────────────────────
p = 2357
g = 2
x = random.randint(2, p - 2)
gx_mod_p = pow(g, x, p)

y = random.randint(2, p - 2)
gy_mod_p = pow(g, y, p)

K_bob   = pow(gx_mod_p, y, p)
K_alice = pow(gy_mod_p, x, p)

message = "Hola Alice!"
plaintext_bytes = message.encode()
key_bytes = derive_key(K_bob)
C = symmetric_encrypt(key_bytes, plaintext_bytes)
C_hex = C.hex()[:20] + "..."

recovered = symmetric_encrypt(derive_key(K_alice), C).decode()

# ─────────────────────────────────────────────
# Color palette
# ─────────────────────────────────────────────
BG        = "#0f1117"
ALICE_COL = "#4fc3f7"   # light blue
BOB_COL   = "#ef9a9a"   # light red
KEY_COL   = "#a5d6a7"   # green
MSG_COL   = "#fff176"   # yellow
CIPHER_COL= "#ce93d8"   # purple
TEXT_COL  = "#e0e0e0"
DIM_COL   = "#424242"

# ─────────────────────────────────────────────
# Layout constants
# ─────────────────────────────────────────────
ALICE_X = 2.5
BOB_X   = 11.5
MID_X   = 7.0

def rounded_box(ax, x, y, w, h, color, alpha=0.15, lw=2):
    box = FancyBboxPatch((x - w/2, y - h/2), w, h,
                         boxstyle="round,pad=0.1",
                         linewidth=lw, edgecolor=color,
                         facecolor=color, alpha=alpha)
    ax.add_patch(box)

def label_box(ax, x, y, w, h, title, lines, title_color, line_color=TEXT_COL, alpha=0.18):
    rounded_box(ax, x, y, w, h, title_color, alpha=alpha)
    ax.text(x, y + h/2 - 0.28, title, ha="center", va="top",
            fontsize=10, fontweight="bold", color=title_color,
            fontfamily="monospace")
    for i, line in enumerate(lines):
        ax.text(x, y + h/2 - 0.62 - i*0.38, line, ha="center", va="top",
                fontsize=8.5, color=line_color, fontfamily="monospace")

def draw_arrow(ax, x1, y, x2, label, color, lw=2.0):
    ax.annotate("", xy=(x2, y), xytext=(x1, y),
                arrowprops=dict(arrowstyle="->", color=color, lw=lw))
    ax.text((x1+x2)/2, y + 0.18, label, ha="center", va="bottom",
            fontsize=8.5, color=color, fontfamily="monospace",
            bbox=dict(boxstyle="round,pad=0.2", fc=BG, ec=color, alpha=0.8, lw=1))

def create_figure(step_idx, steps):
    """Create and return a figure for a given step."""
    fig, ax = plt.subplots(figsize=(14, 8), facecolor=BG)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis("off")
    ax.set_facecolor(BG)
    
    step = steps[step_idx]
    phase = step["phase"]

    # ── Header ───────────────────────────────
    ax.text(MID_X, 7.6, step["title"], ha="center", va="center",
            fontsize=14, fontweight="bold", color=TEXT_COL, fontfamily="monospace")
    ax.text(MID_X, 7.15, step["subtitle"], ha="center", va="center",
            fontsize=9, color=DIM_COL, fontfamily="monospace", style="italic")

    # ── Alice avatar ─────────────────────────
    alice_alpha = 1.0 if phase in ("init","alice_keygen","send_pubkey","alice_decrypt","done","send_cipher") else 0.35
    ax.text(ALICE_X, 6.5, "[ALICE]", ha="center", va="center", fontsize=20, 
            fontweight="bold", alpha=alice_alpha, color=ALICE_COL, fontfamily="monospace")
    ax.text(ALICE_X, 5.9, "Alice", ha="center", va="center",
            fontsize=12, fontweight="bold", color=ALICE_COL, alpha=alice_alpha)

    # ── Bob avatar ───────────────────────────
    bob_alpha = 1.0 if phase in ("init","bob_encrypt","send_pubkey","send_cipher","done") else 0.35
    ax.text(BOB_X, 6.5, "[BOB]", ha="center", va="center", fontsize=20,
            fontweight="bold", alpha=bob_alpha, color=BOB_COL, fontfamily="monospace")
    ax.text(BOB_X, 5.9, "Bob", ha="center", va="center",
            fontsize=12, fontweight="bold", color=BOB_COL, alpha=bob_alpha)

    # ── Channel line ─────────────────────────
    ax.plot([ALICE_X + 0.6, BOB_X - 0.6], [5.55, 5.55],
            color=DIM_COL, lw=1, ls="--", alpha=0.4)
    ax.text(MID_X, 5.35, "Canal publico (inseguro)", ha="center",
            fontsize=7.5, color=DIM_COL, alpha=0.5, fontfamily="monospace")

    # ────────────────── PHASES ───────────────

    if phase == "init":
        label_box(ax, ALICE_X, 3.8, 4.5, 2.4, "Parametros publicos",
                  [f"Prime  p = {p}", f"Generator  g = {g}",
                   "Conocidos por todos"], ALICE_COL, alpha=0.12)
        label_box(ax, BOB_X, 3.8, 4.5, 2.4, "Parametros publicos",
                  [f"Prime  p = {p}", f"Generator  g = {g}",
                   "Conocidos por todos"], BOB_COL, alpha=0.12)

    elif phase == "alice_keygen":
        label_box(ax, ALICE_X, 3.5, 4.8, 3.6, "[*] Generacion de Claves",
                  [f"Privada: x = {x}  (SECRETO)",
                   "",
                   f"g^x mod p =",
                   f"  {g}^{x} mod {p}",
                   f"  = {gx_mod_p}",
                   "",
                   f"Publica: (g={g}, p={p},",
                   f"         g^x mod p={gx_mod_p})"],
                  ALICE_COL, alpha=0.18)

    elif phase == "send_pubkey":
        label_box(ax, ALICE_X, 4.5, 4.5, 1.6, "Clave Publica",
                  [f"g={g},  p={p}",
                   f"g^x mod p = {gx_mod_p}"], ALICE_COL, alpha=0.18)
        draw_arrow(ax, ALICE_X + 2.3, 4.5, BOB_X - 2.3,
                   "Clave Publica ->", ALICE_COL, lw=2.5)
        label_box(ax, BOB_X, 3.0, 4.5, 1.6, "Bob recibe",
                  [f"g={g},  p={p}",
                   f"g^x mod p = {gx_mod_p}"], BOB_COL, alpha=0.18)

    elif phase == "bob_encrypt":
        label_box(ax, BOB_X, 3.5, 4.8, 4.2, "[*] Cifrado por Bob",
                  [f"Mensaje M = \"{message}\"",
                   "",
                   f"Aleatorio:  y = {y}",
                   f"g^y mod p = {gy_mod_p}",
                   "",
                   f"K = (g^x mod p)^y mod p",
                   f"  = {gx_mod_p}^{y} mod {p}",
                   f"  = {K_bob}",
                   "",
                   f"C = ENCRYPT_K(M)"],
                  BOB_COL, alpha=0.18)

    elif phase == "send_cipher":
        draw_arrow(ax, BOB_X - 2.3, 4.8, ALICE_X + 2.3,
                   f"<- C, g^y mod p={gy_mod_p}", BOB_COL, lw=2.5)
        label_box(ax, MID_X, 3.6, 5.0, 2.6, "Mensaje transmitido",
                  [f"g^y mod p = {gy_mod_p}",
                   f"C (hex) = {C_hex}",
                   "",
                   "Solo Alice puede descifrar C"],
                  CIPHER_COL, alpha=0.15)

    elif phase == "alice_decrypt":
        label_box(ax, ALICE_X, 3.2, 4.8, 4.6, "[*] Descifrado por Alice",
                  [f"Recibe: g^y mod p = {gy_mod_p}",
                   f"         C = {C_hex}",
                   "",
                   f"K = (g^y mod p)^x mod p",
                   f"  = {gy_mod_p}^{x} mod {p}",
                   f"  = {K_alice}",
                   "",
                   "M = DECRYPT_K(C)",
                   f'  = \"{recovered}\"'],
                  ALICE_COL, alpha=0.18)

    elif phase == "done":
        rounded_box(ax, MID_X, 4.0, 6.2, 1.3, KEY_COL, alpha=0.2, lw=2)
        ax.text(MID_X, 4.0, f"[KEY]  Clave secreta compartida  K = {K_alice}",
                ha="center", va="center",
                fontsize=11, fontweight="bold", color=KEY_COL, fontfamily="monospace")

        rounded_box(ax, MID_X, 2.6, 6.2, 1.1, MSG_COL, alpha=0.2, lw=2)
        ax.text(MID_X, 2.6, f'[MSG]  Mensaje recuperado: \"{recovered}\"',
                ha="center", va="center",
                fontsize=12, fontweight="bold", color=MSG_COL, fontfamily="monospace")

        ax.text(ALICE_X, 2.0, f"K = {K_alice}", ha="center",
                fontsize=8, color=KEY_COL, fontfamily="monospace")
        ax.text(BOB_X, 2.0, f"K = {K_bob}", ha="center",
                fontsize=8, color=KEY_COL, fontfamily="monospace")
        ax.text(MID_X, 1.5, f"K_Alice == K_Bob  ->  {'OK' if K_alice == K_bob else 'ERROR'}",
                ha="center", fontsize=10, color=KEY_COL, fontfamily="monospace",
                fontweight="bold")

    # ── Step indicator ────────────────────────
    for i, s in enumerate(steps):
        col = ALICE_COL if i == step_idx else DIM_COL
        marker = "*" if i == step_idx else "-"
        ax.text(1.2 + i * 1.7, 0.5, f"[{marker}] {i+1}",
                ha="center", va="center", fontsize=9, color=col, fontfamily="monospace")

    plt.tight_layout(pad=0)
    return fig


# ─────────────────────────────────────────────
# Steps definition
# ─────────────────────────────────────────────
steps = [
    {"title": "ElGamal - Cifrado de Clave Publica",
     "subtitle": f"Parametros publicos:  p = {p},  g = {g}",
     "phase": "init"},
    
    {"title": "Paso 1 . Alice genera sus claves",
     "subtitle": "Alice elige su clave privada x de forma aleatoria",
     "phase": "alice_keygen"},
    
    {"title": "Paso 2 . Alice envia su clave publica a Bob",
     "subtitle": "La clave publica viaja por un canal inseguro",
     "phase": "send_pubkey"},
    
    {"title": "Paso 3 . Bob cifra el mensaje",
     "subtitle": "Bob genera y aleatorio y calcula la clave secreta compartida K",
     "phase": "bob_encrypt"},
    
    {"title": "Paso 4 . Bob envia el texto cifrado a Alice",
     "subtitle": f"Bob envia: (C, g^y mod p = {gy_mod_p})",
     "phase": "send_cipher"},
    
    {"title": "Paso 5 . Alice descifra el mensaje",
     "subtitle": "Alice recupera K y aplica DECRYPT_K(C)",
     "phase": "alice_decrypt"},
    
    {"title": "OK Comunicacion completada",
     "subtitle": f"Alice recupero: \"{recovered}\"",
     "phase": "done"},
]

# ─────────────────────────────────────────────
# Generate frames and save
# ─────────────────────────────────────────────
output_dir = "elgamal_frames"
os.makedirs(output_dir, exist_ok=True)

print(f"Generando {len(steps)} frames...")
images = []

for i, step in enumerate(steps):
    print(f"  Paso {i+1}/{len(steps)}: {step['phase']}...", end=" ")
    fig = create_figure(i, steps)
    filename = f"{output_dir}/frame_{i:02d}_{step['phase']}.png"
    fig.savefig(filename, facecolor=BG, dpi=100, bbox_inches="tight")
    plt.close(fig)
    images.append(Image.open(filename))
    print("OK")

# ─────────────────────────────────────────────
# Create animated GIF
# ─────────────────────────────────────────────
print("\nCreando GIF animado...")
gif_path = "elgamal_animation.gif"
images[0].save(
    gif_path,
    save_all=True,
    append_images=images[1:],
    duration=2800,  # 2.8 segundos por frame
    loop=0,
    optimize=False
)
print(f"GIF guardado: {gif_path}")

# ─────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────
print("\n" + "="*60)
print("GENERACION COMPLETADA")
print("="*60)
print(f"\nFrames PNG en directorio: {output_dir}/")
print(f"GIF animado: {gif_path}")
print(f"\nParametros usados:")
print(f"  Primo p = {p}")
print(f"  Generador g = {g}")
print(f"  Clave privada Alice x = {x} (SECRETO)")
print(f"  g^x mod p = {gx_mod_p}")
print(f"  y aleatorio = {y}")
print(f"  g^y mod p = {gy_mod_p}")
print(f"  Clave compartida K = {K_alice}")
print(f"  Mensaje = '{message}'")
print(f"  Mensaje recuperado = '{recovered}'")
print(f"\nVerificacion: {'OK' if K_alice == K_bob else 'ERROR'}")
print("="*60)

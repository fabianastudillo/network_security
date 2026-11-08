"""
ElGamal Public Key Encryption – Animated Visualization
Emulates the communication between Alice and Bob step by step.
"""

import random
import hashlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from matplotlib.animation import FuncAnimation
import matplotlib.gridspec as gridspec

# ─────────────────────────────────────────────
# Crypto core (same as elgamal.py)
# ─────────────────────────────────────────────

def symmetric_encrypt(key_bytes: bytes, plaintext: bytes) -> bytes:
    keystream = b""
    counter = 0
    while len(keystream) < len(plaintext):
        keystream += hashlib.sha256(key_bytes + counter.to_bytes(4, "big")).digest()
        counter += 1
    return bytes(a ^ b for a, b in zip(plaintext, keystream))

def derive_key(K: int) -> bytes:
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
C_hex = C.hex()[:20] + "…"

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
ARROW_COL = "#ffffff"
TEXT_COL  = "#e0e0e0"
DIM_COL   = "#424242"

# ─────────────────────────────────────────────
# Figure layout
# ─────────────────────────────────────────────
fig = plt.figure(figsize=(14, 8), facecolor=BG)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 14)
ax.set_ylim(0, 8)
ax.axis("off")
ax.set_facecolor(BG)

# ─────────────────────────────────────────────
# Static layout helpers
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
    return box

def label_box(ax, x, y, w, h, title, lines, title_color, line_color=TEXT_COL, alpha=0.18):
    rounded_box(ax, x, y, w, h, title_color, alpha=alpha)
    ax.text(x, y + h/2 - 0.28, title, ha="center", va="top",
            fontsize=10, fontweight="bold", color=title_color,
            fontfamily="monospace")
    for i, line in enumerate(lines):
        ax.text(x, y + h/2 - 0.62 - i*0.38, line, ha="center", va="top",
                fontsize=8.5, color=line_color, fontfamily="monospace")

def draw_arrow(ax, x1, y, x2, label, color, lw=2.0, style="->"):
    ax.annotate("", xy=(x2, y), xytext=(x1, y),
                arrowprops=dict(arrowstyle=style, color=color, lw=lw))
    ax.text((x1+x2)/2, y + 0.18, label, ha="center", va="bottom",
            fontsize=8.5, color=color, fontfamily="monospace",
            bbox=dict(boxstyle="round,pad=0.2", fc=BG, ec=color, alpha=0.8, lw=1))

# ─────────────────────────────────────────────
# Step definitions
# ─────────────────────────────────────────────
steps = [
    # step 0 – title
    {
        "title": "ElGamal – Cifrado de Clave Pública",
        "subtitle": f"Parámetros públicos:  p = {p},  g = {g}",
        "phase": "init",
    },
    # step 1 – Alice key gen
    {
        "title": "Paso 1 · Alice genera sus claves",
        "subtitle": "Alice elige su clave privada x de forma aleatoria",
        "phase": "alice_keygen",
    },
    # step 2 – send public key
    {
        "title": "Paso 2 · Alice envía su clave pública a Bob",
        "subtitle": "La clave pública viaja por un canal inseguro",
        "phase": "send_pubkey",
    },
    # step 3 – Bob encrypt
    {
        "title": "Paso 3 · Bob cifra el mensaje",
        "subtitle": "Bob genera y aleatorio y calcula la clave secreta compartida K",
        "phase": "bob_encrypt",
    },
    # step 4 – send ciphertext
    {
        "title": "Paso 4 · Bob envía el texto cifrado a Alice",
        "subtitle": f"Bob envía: (C, gʸ mod p = {gy_mod_p})",
        "phase": "send_cipher",
    },
    # step 5 – Alice decrypt
    {
        "title": "Paso 5 · Alice descifra el mensaje",
        "subtitle": "Alice recupera K y aplica DECRYPT_K(C)",
        "phase": "alice_decrypt",
    },
    # step 6 – done
    {
        "title": "✓ Comunicación completada",
        "subtitle": f'Alice recuperó: "{recovered}"',
        "phase": "done",
    },
]

current_step = [0]
artists = []

# ─────────────────────────────────────────────
# Draw helpers
# ─────────────────────────────────────────────

def clear_artists():
    for a in artists:
        try:
            a.remove()
        except Exception:
            pass
    artists.clear()

def add(artist):
    artists.append(artist)
    return artist


def draw_frame(step_idx):
    clear_artists()
    step = steps[step_idx]
    phase = step["phase"]

    # ── Header ───────────────────────────────
    add(ax.text(MID_X, 7.6, step["title"], ha="center", va="center",
                fontsize=14, fontweight="bold", color=TEXT_COL, fontfamily="monospace"))
    add(ax.text(MID_X, 7.15, step["subtitle"], ha="center", va="center",
                fontsize=9, color=DIM_COL, fontfamily="monospace", style="italic"))

    # ── Alice avatar ─────────────────────────
    alice_alpha = 1.0 if phase in ("init","alice_keygen","send_pubkey","alice_decrypt","done","send_cipher") else 0.35
    add(ax.text(ALICE_X, 6.5, "👩", ha="center", va="center", fontsize=32, alpha=alice_alpha))
    add(ax.text(ALICE_X, 5.9, "Alice", ha="center", va="center",
                fontsize=12, fontweight="bold", color=ALICE_COL, alpha=alice_alpha))

    # ── Bob avatar ───────────────────────────
    bob_alpha = 1.0 if phase in ("init","bob_encrypt","send_pubkey","send_cipher","done") else 0.35
    add(ax.text(BOB_X, 6.5, "👨", ha="center", va="center", fontsize=32, alpha=bob_alpha))
    add(ax.text(BOB_X, 5.9, "Bob", ha="center", va="center",
                fontsize=12, fontweight="bold", color=BOB_COL, alpha=bob_alpha))

    # ── Channel line ─────────────────────────
    add(ax.plot([ALICE_X + 0.6, BOB_X - 0.6], [5.55, 5.55],
                color=DIM_COL, lw=1, ls="--", alpha=0.4)[0])
    add(ax.text(MID_X, 5.35, "Canal público (inseguro)", ha="center",
                fontsize=7.5, color=DIM_COL, alpha=0.5, fontfamily="monospace"))

    # ────────────────── PHASES ───────────────

    if phase == "init":
        label_box(ax, ALICE_X, 3.8, 4.5, 2.4, "Parámetros públicos",
                  [f"Prime  p = {p}", f"Generator  g = {g}",
                   "Conocidos por todos"], ALICE_COL, alpha=0.12)
        label_box(ax, BOB_X, 3.8, 4.5, 2.4, "Parámetros públicos",
                  [f"Prime  p = {p}", f"Generator  g = {g}",
                   "Conocidos por todos"], BOB_COL, alpha=0.12)
        artists.extend(fig.get_axes())   # keep axes

    elif phase == "alice_keygen":
        label_box(ax, ALICE_X, 3.5, 4.8, 3.6, "🔑 Generación de Claves",
                  [f"Privada: x = {x}  (SECRETO)",
                   "",
                   f"gˣ mod p =",
                   f"  {g}^{x} mod {p}",
                   f"  = {gx_mod_p}",
                   "",
                   f"Pública: (g={g}, p={p},",
                   f"         gˣ mod p={gx_mod_p})"],
                  ALICE_COL, alpha=0.18)

    elif phase == "send_pubkey":
        # Alice box (dim)
        label_box(ax, ALICE_X, 4.5, 4.5, 1.6, "Clave Pública",
                  [f"g={g},  p={p}",
                   f"gˣ mod p = {gx_mod_p}"], ALICE_COL, alpha=0.18)
        # Arrow Alice → Bob
        draw_arrow(ax, ALICE_X + 2.3, 4.5, BOB_X - 2.3,
                   "Clave Pública →", ALICE_COL, lw=2.5)
        # Bob receives
        label_box(ax, BOB_X, 3.0, 4.5, 1.6, "Bob recibe",
                  [f"g={g},  p={p}",
                   f"gˣ mod p = {gx_mod_p}"], BOB_COL, alpha=0.18)

    elif phase == "bob_encrypt":
        label_box(ax, BOB_X, 3.5, 4.8, 4.2, "🔒 Cifrado por Bob",
                  [f"Mensaje M = \"{message}\"",
                   "",
                   f"Aleatorio:  y = {y}",
                   f"gʸ mod p = {gy_mod_p}",
                   "",
                   f"K = (gˣ mod p)ʸ mod p",
                   f"  = {gx_mod_p}^{y} mod {p}",
                   f"  = {K_bob}",
                   "",
                   f"C = ENCRYPT_K(M)"],
                  BOB_COL, alpha=0.18)

    elif phase == "send_cipher":
        # cipher arrow Bob → Alice
        draw_arrow(ax, BOB_X - 2.3, 4.8, ALICE_X + 2.3,
                   f"← C, gʸ mod p={gy_mod_p}", BOB_COL, lw=2.5, style="<-")
        label_box(ax, MID_X, 3.6, 5.0, 2.6, "Mensaje transmitido",
                  [f"gʸ mod p = {gy_mod_p}",
                   f"C (hex) = {C_hex}",
                   "",
                   "Solo Alice puede descifrar C"],
                  CIPHER_COL, alpha=0.15)

    elif phase == "alice_decrypt":
        label_box(ax, ALICE_X, 3.2, 4.8, 4.6, "🔓 Descifrado por Alice",
                  [f"Recibe: gʸ mod p = {gy_mod_p}",
                   f"         C = {C_hex}",
                   "",
                   f"K = (gʸ mod p)ˣ mod p",
                   f"  = {gy_mod_p}^{x} mod {p}",
                   f"  = {K_alice}",
                   "",
                   "M = DECRYPT_K(C)",
                   f'  = "{recovered}"'],
                  ALICE_COL, alpha=0.18)

    elif phase == "done":
        # shared key highlight
        rounded_box(ax, MID_X, 4.0, 6.2, 1.3, KEY_COL, alpha=0.2, lw=2)
        add(ax.text(MID_X, 4.0, f"🔑  Clave secreta compartida  K = {K_alice}",
                    ha="center", va="center",
                    fontsize=11, fontweight="bold", color=KEY_COL, fontfamily="monospace"))

        rounded_box(ax, MID_X, 2.6, 6.2, 1.1, MSG_COL, alpha=0.2, lw=2)
        add(ax.text(MID_X, 2.6, f'✉  Mensaje recuperado: "{recovered}"',
                    ha="center", va="center",
                    fontsize=12, fontweight="bold", color=MSG_COL, fontfamily="monospace"))

        add(ax.text(ALICE_X, 2.0, f"K = {K_alice}", ha="center",
                    fontsize=8, color=KEY_COL, fontfamily="monospace"))
        add(ax.text(BOB_X, 2.0, f"K = {K_bob}", ha="center",
                    fontsize=8, color=KEY_COL, fontfamily="monospace"))
        add(ax.text(MID_X, 1.5, f"K_Alice == K_Bob  →  {'✓ IGUALES' if K_alice == K_bob else '✗ ERROR'}",
                    ha="center", fontsize=10, color=KEY_COL, fontfamily="monospace",
                    fontweight="bold"))

    # ── Step indicator ────────────────────────
    for i, s in enumerate(steps):
        col = ALICE_COL if i == step_idx else DIM_COL
        add(ax.text(1.2 + i * 1.7, 0.5, f"{'●' if i == step_idx else '○'} {i+1}",
                    ha="center", va="center", fontsize=9, color=col, fontfamily="monospace"))

    # ── Navigation hint ───────────────────────
    add(ax.text(MID_X, 0.18, "← / → teclas  |  clic para avanzar",
                ha="center", fontsize=8, color=DIM_COL, fontfamily="monospace"))

    fig.canvas.draw_idle()


# ─────────────────────────────────────────────
# Interaction
# ─────────────────────────────────────────────

def on_key(event):
    if event.key in ("right", " ", "enter"):
        current_step[0] = min(current_step[0] + 1, len(steps) - 1)
    elif event.key == "left":
        current_step[0] = max(current_step[0] - 1, 0)
    draw_frame(current_step[0])

def on_click(event):
    if event.inaxes == ax:
        current_step[0] = min(current_step[0] + 1, len(steps) - 1)
        draw_frame(current_step[0])

fig.canvas.mpl_connect("key_press_event", on_key)
fig.canvas.mpl_connect("button_press_event", on_click)

# ─────────────────────────────────────────────
# Auto-advance animation
# ─────────────────────────────────────────────

def auto_advance(frame):
    if current_step[0] < len(steps) - 1:
        current_step[0] += 1
        draw_frame(current_step[0])

ani = FuncAnimation(fig, auto_advance, frames=len(steps) - 1,
                    interval=2800, repeat=False)

# ─────────────────────────────────────────────
# Launch
# ─────────────────────────────────────────────
draw_frame(0)
plt.title("")
fig.suptitle("")
plt.tight_layout(pad=0)
plt.show()

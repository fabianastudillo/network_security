"""
ElGamal Public Key Encryption Scheme
Emulates the communication between Alice (receiver) and Bob (sender).

Scheme:
  Alice generates: public key (g, p, g^x mod p) and private key (g, p, x)
  Bob encrypts:    K = (g^x mod p)^y mod p = g^xy mod p
                   Ciphertext C = ENCRYPT_K(M)
  Alice decrypts:  K = (g^y mod p)^x mod p = g^xy mod p
                   Plaintext M = DECRYPT_K(C)
"""

import random
import hashlib
import os

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def is_primitive_root(g: int, p: int) -> bool:
    """Check if g is a primitive root modulo the prime p."""
    required = set(range(1, p))
    generated = {pow(g, exp, p) for exp in range(1, p)}
    return generated == required


def find_primitive_root(p: int) -> int:
    """Return the smallest primitive root modulo prime p."""
    for g in range(2, p):
        if is_primitive_root(g, p):
            return g
    raise ValueError(f"No primitive root found for p={p}")


def symmetric_encrypt(key_bytes: bytes, plaintext: bytes) -> bytes:
    """
    Simple XOR stream cipher keyed by repeated SHA-256 hash of K.
    Used to emulate ENCRYPT_K(M).
    """
    keystream = b""
    counter = 0
    while len(keystream) < len(plaintext):
        keystream += hashlib.sha256(key_bytes + counter.to_bytes(4, "big")).digest()
        counter += 1
    return bytes(p ^ k for p, k in zip(plaintext, keystream))


def symmetric_decrypt(key_bytes: bytes, ciphertext: bytes) -> bytes:
    """
    XOR is its own inverse: DECRYPT_K(C) = ENCRYPT_K(C).
    Used to emulate DECRYPT_K(C).
    """
    return symmetric_encrypt(key_bytes, ciphertext)


def derive_key(K: int) -> bytes:
    """Derive a symmetric key from the shared secret K."""
    return hashlib.sha256(K.to_bytes((K.bit_length() + 7) // 8, "big")).digest()


# ─────────────────────────────────────────────
# Alice – Key Generation
# ─────────────────────────────────────────────

class Alice:
    def __init__(self, p: int, g: int):
        """
        p : large prime
        g : primitive root modulo p
        x : Alice's private exponent (secret)
        """
        self.p = p
        self.g = g
        self.x = random.randint(2, p - 2)          # private key component
        self.gx_mod_p = pow(g, self.x, p)           # g^x mod p  (public)

    @property
    def public_key(self) -> dict:
        return {"g": self.g, "p": self.p, "gx_mod_p": self.gx_mod_p}

    def decrypt(self, C: bytes, gy_mod_p: int) -> bytes:
        """
        Compute K = (g^y mod p)^x mod p = g^xy mod p
        Return DECRYPT_K(C)
        """
        K = pow(gy_mod_p, self.x, self.p)
        key_bytes = derive_key(K)
        return symmetric_decrypt(key_bytes, C)


# ─────────────────────────────────────────────
# Bob – Encryption
# ─────────────────────────────────────────────

class Bob:
    def __init__(self, alice_public_key: dict):
        self.g = alice_public_key["g"]
        self.p = alice_public_key["p"]
        self.gx_mod_p = alice_public_key["gx_mod_p"]

    def encrypt(self, message: bytes) -> tuple[bytes, int]:
        """
        1. Generate random y
        2. Compute K = (g^x mod p)^y mod p = g^xy mod p
        3. Compute C = ENCRYPT_K(M)
        Returns (C, g^y mod p)
        """
        y = random.randint(2, self.p - 2)                # random ephemeral key
        K = pow(self.gx_mod_p, y, self.p)                # shared secret
        gy_mod_p = pow(self.g, y, self.p)                 # sent to Alice
        key_bytes = derive_key(K)
        C = symmetric_encrypt(key_bytes, message)
        return C, gy_mod_p


# ─────────────────────────────────────────────
# Simulation
# ─────────────────────────────────────────────

def simulate(message: str, p: int = 2357, g: int = None):
    separator = "=" * 60

    print(separator)
    print("  ElGamal Public Key Encryption – Alice ↔ Bob")
    print(separator)

    # ── Domain parameters ──────────────────────────────────────
    if g is None:
        g = find_primitive_root(p)

    print(f"\n[Domain Parameters]")
    print(f"  Prime p          = {p}")
    print(f"  Generator g      = {g}  (primitive root mod p)")

    # ── Alice: Key Generation ──────────────────────────────────
    alice = Alice(p, g)
    print(f"\n[Alice – Key Generation]")
    print(f"  Private key  x         = {alice.x}  (SECRET)")
    print(f"  Public key   g^x mod p = {alice.gx_mod_p}")
    print(f"  → Alice broadcasts public key: (g={g}, p={p}, g^x mod p={alice.gx_mod_p})")

    # ── Bob: Encryption ────────────────────────────────────────
    bob = Bob(alice.public_key)
    plaintext_bytes = message.encode("utf-8")
    C, gy_mod_p = bob.encrypt(plaintext_bytes)

    print(f"\n[Bob – Encryption]")
    print(f"  Original message M = \"{message}\"")
    print(f"  Ephemeral value  g^y mod p = {gy_mod_p}")
    print(f"  Ciphertext C (hex) = {C.hex()}")
    print(f"  → Bob sends to Alice: (C, g^y mod p={gy_mod_p})")

    # ── Alice: Decryption ──────────────────────────────────────
    recovered_bytes = alice.decrypt(C, gy_mod_p)
    recovered_message = recovered_bytes.decode("utf-8")

    print(f"\n[Alice – Decryption]")
    print(f"  Shared secret K = (g^y mod p)^x mod p = g^xy mod p")
    print(f"  Recovered plaintext M = \"{recovered_message}\"")

    # ── Verification ───────────────────────────────────────────
    success = recovered_message == message
    print(f"\n[Verification]")
    print(f"  Original  : \"{message}\"")
    print(f"  Recovered : \"{recovered_message}\"")
    print(f"  Match      : {'✓ SUCCESS' if success else '✗ FAILURE'}")
    print(separator)


if __name__ == "__main__":
    # You can change the message and the prime p here.
    # p must be prime; a larger prime is more secure.
    simulate(
        message="Hello Bob, this is Alice!",
        p=2357,      # small prime for demonstration (use 2048-bit in practice)
        g=2,         # primitive root mod 2357
    )

    print()

    simulate(
        message="Secret message: meet at noon.",
        p=7919,
        g=None,      # auto-detect primitive root
    )

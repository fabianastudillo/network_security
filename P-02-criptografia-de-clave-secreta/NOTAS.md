# Cifrado por sustitución monoalfabética

```bash
# Encriptación
$ tr 'a-z' 'vgapnbrtmosicuxejhqyzflkdw' < plaintext > ciphertext
# Desencriptación
$ tr 'vgapnbrtmosicuxejhqyzflkdw' 'a-z' < plaintext > ciphertext
```

# Data Encryption Standard (DES)

## Modo Electronic Codebook (ECB)
Usando el comando openssl enc

```bash
$ openssl enc -aes-128-ecb -e -in archivoplano.txt -out cifrado.txt -K 00112233445566778899AABB
$ openssl enc -aes-128-ecb -d -in cifrado.txt -out archivoplano2.txt -K 00112233445566778899AABB
```

- La opción -e indica encriptación
- La opción -d indica desencriptación
- La opción -K es usado para especificar la clave de encriptación/desencriptación

## Modo Cipher Block Chaining (CBC)

Usando el comando openssl enc para encriptar el mismo texto, con la misma clave, y con diferente IV

```bash
$ openssl enc -aes-128-cbc -e -in archivoplano.txt -out cifrado1.txt -K 00112233445566778899AABB -iv 000102030405060708090a0b0c0d0e0f
$ openssl enc -aes-128-cbc -e -in archivoplano.txt -out cifrado2.txt -K 00112233445566778899AABB -iv 000102030405060708090a0b0c0d0e0e
```

- La opción -iv es usada para especificar el vector de inicialización (IV)

## Modo Cipher Feedback (CFB)

Usando el comando openssl enc para comparar los modos de encriptación CBC y CFB

```bash
$ openssl enc -aes-128-cbc -e -in archivoplano.txt -out cifrado1.txt -K 00112233445566778899AABB -iv 000102030405060708090a0b0c0d0e0f
$ openssl enc -aes-128-cfb -e -in archivoplano.txt -out cifrado2.txt -K 00112233445566778899AABB -iv 000102030405060708090a0b0c0d0e0f
$ ls -l archivoplano.txt cifrado1.txt cifrado2.txt
```

## Experimento de padding

- El archivo plano tiene un tamaño de 9 bytes.
- El tamaño del archivo cifrado (cifrado.bin) llega a tener 16 bytes.

```bash
$ echo -n "123456789" > archivoplano.txt
$ openssl enc -aes-128-cbc -e -in archivoplano.txt -out cifrado.bin -K 00112233445566778899AABBCCDDEEFF -iv 000102030405060708090a0b0c0d0e0f
$ ls -ld cifrado.bin
$ openssl enc -aes-128-cbc -d -in cifrado.bin -out archivoplano2.txt -K 00112233445566778899aabbccddeeff -iv 000102030405060708
$ ls -ld archivoplano2.txt
```

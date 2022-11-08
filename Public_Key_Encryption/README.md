# Comandos para el hash de una vía


## Linux utility programas

```bash
$ md5sum file.c
$ sha256sum file.c
```

## Comando openssl

```bash
$ openssl dgst -sha256 file.c
$ openssl sha256 file.c
$ openssl dgst -md5 file.c
$ openssl md5 file.c
```

# Verificación de integridad

```bash
$ echo -n "Hello world" | sha256sum
$ echo -n "Hallo world" | sha256sum
```

# Crear contraseñas desde la línea de comandos

```bash
$ openssl passwd -6 -salt xyz password
```

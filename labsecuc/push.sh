#!/usr/bin/env bash
# Sube la imagen labsecuc a Docker Hub (arquitectura amd64).
#
# Uso:
#   docker login                 # una sola vez, pide usuario y contraseña/token
#   ./push.sh <usuario-dockerhub> [tag]
#
# Ejemplo:
#   ./push.sh fabianastudillo          -> fabianastudillo/labsecuc:latest y :large
#   ./push.sh fabianastudillo v1       -> fabianastudillo/labsecuc:v1 y :large
set -euo pipefail

USER="${1:-}"
TAG="${2:-latest}"
[ -n "$USER" ] || { echo "Falta el usuario de Docker Hub. Uso: ./push.sh <usuario> [tag]" >&2; exit 1; }

REPO="$USER/labsecuc"
DIR="$(cd "$(dirname "$0")" && pwd)"

# 1) Verifica que haya sesión iniciada en Docker Hub.
if ! docker system info 2>/dev/null | grep -q "Username:"; then
    echo "No hay sesión en Docker Hub. Ejecuta primero: docker login" >&2
    exit 1
fi

# 2) Construye la imagen (amd64) con los dos tags.
docker build -t "$REPO:$TAG" -t "$REPO:large" "$DIR"

# 3) Empuja ambos tags.
docker push "$REPO:$TAG"
docker push "$REPO:large"

echo "Listo: subida $REPO:$TAG y $REPO:large (amd64)."

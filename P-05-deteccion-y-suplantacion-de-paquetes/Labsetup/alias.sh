#!/bin/bash

# Aliases for Docker Compose commands
alias dcbuild='docker-compose build'
alias dcup='docker-compose up -d'
alias dcdown='docker-compose down'

# Aliases for Docker container interaction
alias dockps='docker ps --format "{{.ID}}  {{.Names}}"'
docksh() { docker exec -it "$1" /bin/bash; }

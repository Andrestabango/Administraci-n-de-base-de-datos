#!/usr/bin/env bash
# ============================================================================
# 01_install_docker.sh  ·  Instala Docker CE en Red Hat 8.10
# Remueve Podman/Buildah (que vienen por defecto en RHEL) e instala
# Docker CE desde el repositorio oficial. Habilita el servicio y agrega
# al usuario actual al grupo docker.
# Uso (como usuario con sudo):  ./01_install_docker.sh
# ============================================================================
set -euo pipefail

echo ">> [1/6] Removiendo Podman y Buildah si estan presentes"
sudo dnf remove -y podman buildah || true

echo ">> [2/6] Instalando dnf-plugins-core"
sudo dnf install -y dnf-plugins-core

echo ">> [3/6] Agregando repositorio oficial de Docker CE"
sudo dnf config-manager \
  --add-repo https://download.docker.com/linux/centos/docker-ce.repo

echo ">> [4/6] Instalando Docker CE, CLI, containerd y compose plugin"
sudo dnf install -y \
  docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin

echo ">> [5/6] Habilitando e iniciando el servicio Docker"
sudo systemctl enable --now docker

echo ">> [6/6] Agregando al usuario $USER al grupo docker"
sudo usermod -aG docker "$USER"

echo "------------------------------------------------------------"
echo " Docker CE instalado. Cierra sesion y vuelve a entrar para"
echo " que el grupo 'docker' tome efecto. Verifica con:"
echo "    docker --version && docker compose version"
echo "------------------------------------------------------------"

#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ "$(uname -m)" != x86_64 ]]; then
    echo "This image requires an x86-64 Unraid host." >&2
    exit 1
fi
command -v docker >/dev/null
if [[ -x /usr/local/emhttp/plugins/ps5-dump-forge/service ]]; then
    echo "Wait for Forge jobs to finish, then uninstall the old .plg before installing the container." >&2
    exit 1
fi
docker build --build-arg FORGE_VERSION=0.5.6 -t ps5-dump-forge:local .
config=/mnt/user/appdata/ps5-dump-forge-docker
if [[ ! -d "$config" ]]; then
    install -d -m 0775 -o 99 -g 100 "$config"
fi
install -d /boot/config/plugins/dockerMan/templates-user
install -m 0644 unraid-template.xml /boot/config/plugins/dockerMan/templates-user/my-ps5-dump-forge.xml
echo "Image and template ready. In Unraid Docker, choose Add Container and select ps5-dump-forge."

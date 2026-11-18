#!/usr/bin/env python3
"""Download and verify the upstream static Linux executable."""
import argparse
import hashlib
import io
import json
import re
import tarfile
import urllib.request
from pathlib import Path

def get(url):
    request = urllib.request.Request(url, headers={"User-Agent": "forge-unraid-docker"})
    with urllib.request.urlopen(request, timeout=180) as response:
        return response.read()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("version")
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    version = args.version.removeprefix("v")
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        parser.error("expected a stable X.Y.Z version")
    base = f"https://github.com/quer3q/ps5-dump-forge/releases/download/v{version}"
    name = f"ps5-dump-forge-{version}-linux-x86-64-musl.tar.gz"
    sums = get(f"{base}/SHA256SUMS").decode()
    expected = next(line.split()[0] for line in sums.splitlines()
                    if line.split()[-1].lstrip("*") == name)
    data = get(f"{base}/{name}")
    if hashlib.sha256(data).hexdigest() != expected:
        raise RuntimeError("upstream archive checksum mismatch")
    args.destination.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        matches = [member for member in archive.getmembers()
                   if member.isfile() and Path(member.name).name == "ps5-dump-forge"]
        if len(matches) != 1:
            raise RuntimeError("expected exactly one executable")
        binary = archive.extractfile(matches[0]).read()
        for name in ("LICENSE", "THIRD-PARTY-NOTICES.md"):
            notices = [member for member in archive.getmembers()
                       if member.isfile() and Path(member.name).name == name]
            if len(notices) != 1:
                raise RuntimeError(f"missing {name}")
            (args.destination / name).write_bytes(archive.extractfile(notices[0]).read())
    if not (binary.startswith(b"\x7fELF\x02\x01") and binary[18:20] == b"\x3e\x00"):
        raise RuntimeError("expected Linux x86-64 ELF")
    args.destination.mkdir(parents=True, exist_ok=True)
    executable = args.destination / "ps5-dump-forge"
    executable.write_bytes(binary)
    executable.chmod(0o755)
    (args.destination / "VERSION").write_text(version + "\n")
    source = get(f"https://codeload.github.com/quer3q/ps5-dump-forge/tar.gz/refs/tags/v{version}")
    with tarfile.open(fileobj=io.BytesIO(source), mode="r:gz") as archive:
        if not any(member.name.endswith("/Cargo.toml") for member in archive.getmembers()):
            raise RuntimeError("invalid corresponding source archive")
    (args.destination / "source.tar.gz").write_bytes(source)
    print(json.dumps({"version": version, "sha256": expected}))

if __name__ == "__main__":
    main()

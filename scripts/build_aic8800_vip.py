#!/usr/bin/env python3
"""Build the existing Desk Box WLAN module with DHCP-only ARP offload disabled."""
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tarfile
from urllib.request import urlopen

SOURCE_REPO = 'unifreq/linux-6.1.y-rockchip'
SOURCE_SHA = '4884d3c6948f1fd461aff4441a147b5460d2551b'
KERNEL = '6.1.174-rk35xx-ophub'
ARCHIVE_SHA = '005fce27ee3bd2aad619bfe9a4f5ef80a84bf01a374af05e7449a2f4eb55bd10'
HEADERS_SHA = '04284da4767608d1183d0077c11926052f9304df859fcabf09ec25a087a3527d'
PREFIX = 'drivers/net/wireless/aicsemi/aic8800/sdio'


def get(url, limit):
    with urlopen(url, timeout=60) as response:
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError('Oversize remote input')
    return data


def sha(data):
    return hashlib.sha256(data).hexdigest()


def run(*args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)


def main():
    if os.uname().machine != 'aarch64':
        raise ValueError('This workflow requires an ARM64 runner')
    root = Path(os.environ['RUNNER_TEMP']) / 'deskbox-aic8800'
    root.mkdir(exist_ok=False)
    archive = get('https://github.com/ophub/kernel/releases/download/kernel_rk35xx/deb-6.1.174.tar.gz', 100_000_000)
    if sha(archive) != ARCHIVE_SHA:
        raise ValueError('Kernel archive checksum mismatch')
    bundle = root / 'kernel-debs.tar.gz'
    bundle.write_bytes(archive)
    with tarfile.open(bundle) as tar:
        candidates = [m for m in tar.getmembers() if m.isfile() and Path(m.name).name == 'linux-headers_6.1.174-1-rk35xx-ophub_arm64.deb']
        if len(candidates) != 1 or candidates[0].size > 20_000_000:
            raise ValueError('Expected exact kernel headers')
        headers = tar.extractfile(candidates[0]).read()
    if sha(headers) != HEADERS_SHA:
        raise ValueError('Headers checksum mismatch')
    package = root / 'headers.deb'
    package.write_bytes(headers)
    run('dpkg-deb', '--extract', str(package), str(root / 'headers'))
    header_root = root / 'headers' / 'usr' / 'src' / ('linux-headers-' + KERNEL)
    if not (header_root / 'Makefile').is_file():
        raise ValueError('Header release mismatch')
    if 'CONFIG_MODVERSIONS=y' in (header_root / '.config').read_text():
        raise ValueError('Unexpected kernel ABI configuration')

    source = root / 'source'
    entries = []
    for folder in ('fdrv', 'bsp'):
        directory = source / folder
        directory.mkdir(parents=True)
        listing = json.loads(get(f'https://api.github.com/repos/{SOURCE_REPO}/contents/{PREFIX}/{folder}?ref={SOURCE_SHA}', 500_000))
        for entry in listing:
            if entry['type'] == 'file' and (folder == 'fdrv' or entry['name'].endswith('.h')):
                entries.append((folder, entry))

    def fetch(item):
        folder, entry = item
        name = entry['name']
        if '/' in name or entry['size'] > 1_000_000:
            raise ValueError('Invalid source file')
        data = get(f'https://raw.githubusercontent.com/{SOURCE_REPO}/{SOURCE_SHA}/{PREFIX}/{folder}/{name}', 1_000_000)
        digest = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        if len(data) != entry['size'] or digest != entry['sha']:
            raise ValueError('Source Git blob mismatch')
        (source / folder / name).write_bytes(data)

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(fetch, entries))
    makefile = source / 'fdrv' / 'Makefile'
    original = makefile.read_text()
    if 'RWNX_VERS_NUM := 6.4.3.0' not in original or 'CONFIG_ARP_OFFLOAD = y' not in original:
        raise ValueError('Unexpected WLAN source version')
    # Explicit command-line feature override; only include paths adapt to out-of-tree build.
    makefile.write_text(original + '\nccflags-y += -I$(src) -I$(src)/../bsp\n')
    run('make', '-j2', '-C', str(header_root), 'M=' + str(source / 'fdrv'),
        'CONFIG_ARP_OFFLOAD=n', 'CONFIG_AIC8800_SDIO_WLAN=y',
        'CONFIG_AIC_FW_PATH=/lib/firmware/aic8800_sdio', 'modules')
    module = source / 'fdrv' / 'aic8800_sdio_wlan.ko'
    symbols = run('nm', str(module), capture_output=True, text=True).stdout
    if 'arpoffload' in symbols:
        raise ValueError('ARP offload unexpectedly remains in candidate')
    vermagic = run('/usr/sbin/modinfo', '-F', 'vermagic', str(module), capture_output=True, text=True).stdout.strip()
    if vermagic != KERNEL + ' SMP mod_unload aarch64':
        raise ValueError('Candidate kernel ABI mismatch: ' + vermagic)
    depends = run('/usr/sbin/modinfo', '-F', 'depends', str(module), capture_output=True, text=True).stdout.strip()
    if set(depends.split(',')) != {'aic8800_sdio_bsp', 'cfg80211'}:
        raise ValueError('Unexpected module dependencies')
    output = Path('output')
    output.mkdir(exist_ok=True)
    target = output / module.name
    target.write_bytes(module.read_bytes())
    metadata = {'kernel_release': KERNEL, 'driver_version': '6.4.3.0', 'source_repository': SOURCE_REPO,
                'source_commit': SOURCE_SHA, 'arp_offload': False, 'vermagic': vermagic,
                'depends': depends, 'module_sha256': sha(target.read_bytes()),
                'headers_sha256': HEADERS_SHA, 'kernel_archive_sha256': ARCHIVE_SHA}
    (output / 'manifest.json').write_text(json.dumps(metadata, indent=2) + '\n')
    (output / 'sha256sums').write_text(metadata['module_sha256'] + '  ' + target.name + '\n')
    print(json.dumps(metadata))


if __name__ == '__main__':
    main()

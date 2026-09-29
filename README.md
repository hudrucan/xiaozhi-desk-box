<div align="center">
  <img src="docs/images/desk-box.svg" alt="Desk Box" width="112" height="112">

# Xiaozhi Desk Box Armbian

**A focused Bookworm image for one RK3528 Desk Box.**

[![Image](https://img.shields.io/badge/image-audited-2ea44f?style=flat-square)](https://github.com/hudrucan/xiaozhi-desk-box/releases/latest)
[![Target](https://img.shields.io/badge/target-RK3528-17120d?style=flat-square)](#hardware)
[![Kernel](https://img.shields.io/badge/kernel-6.1.174--rk35xx-f0c779?style=flat-square)](#current-scope)
[![License](https://img.shields.io/badge/license-GPL--2.0-blue?style=flat-square)](LICENSE)

[Download](https://github.com/hudrucan/xiaozhi-desk-box/releases/latest) · [Build](#build) · [Boot chain](#validated-boot-chain) · [Companion projects](#companion-projects)
</div>

---

This is a single-board fork of
[`ophub/amlogic-s9xxx-armbian`](https://github.com/ophub/amlogic-s9xxx-armbian).
It turns a pinned upstream Armbian server image into a runtime-clean Desk Box
image while keeping the hardware payloads that were verified on the reference
device.

## Highlights

| | |
|---|---|
| 🎯 **One target** | Only the `deskbox` board profile is exposed. |
| 🔒 **Pinned inputs** | Base image, rk35xx kernel bundle, DTB, bootloader, Wi-Fi firmware, regulatory database and BlueZ package are checksum-verified. |
| 🧹 **Focused image** | One DTB, one AIC8800D80 firmware set, no kernel headers, generic startup hooks, package caches or upstream self-update helpers. |
| 🔍 **Release audit** | Every published image is mounted read-only and checked before upload. |
| 🧱 **Known-good boot chain** | Factory-compatible DDR/SPL is paired with the validated RK3528 U-Boot/FIT/ATF payload. |

## Current scope

| Component | Value |
|---|---|
| Board profile | `deskbox` |
| Runtime model | `RK.Deskbox` |
| Distribution | Debian Bookworm, arm64 server |
| Default build kernel | `6.1.174-rk35xx-ophub` |
| Hardware-validated baseline | `6.1.174-rk35xx-ophub` |
| Active DTB | `rockchip/rk3528-deskbox.dtb` |
| Device-tree model | `Rockchip RK3528 Generic TV Box` (retained from known-good baseline) |
| Wi-Fi | AIC8800D80 over SDIO |
| GPU | Mali-450 using Lima |
| Bluetooth | AIC8800D80 H4 over UART2_M0 at 1.5 Mbps; BlueZ 5.66 |
| Front panel | FD6551 HH:MM clock with Wi-Fi, LAN and USB status |
| Timezone / regulatory domain | `Asia/Ho_Chi_Minh` / `VN` |

The project intentionally does not build a kernel or U-Boot. It assembles a
tested image from pinned release artifacts and the board-specific payloads
stored in this repository.

## Hardware

The reference Desk Box uses:

- Rockchip RK3528;
- 4 GB Micron DDR3 and 32 GB eMMC;
- AIC8800D80 SDIO Wi-Fi;
- FD6551-compatible four-digit front panel;
- Ethernet and removable microSD storage.

The functional baseline for this profile was boot-tested from microSD with
Ethernet, SSH, multi-user systemd startup, AIC8800D80 Wi-Fi, Lima graphics,
Bluetooth and the FD6551 front panel operational. Bluetooth HCI Reset, BR/EDR
and LE controller discovery and a BlueZ scan were validated over UART2_M0 at
1.5 Mbps with hardware flow control. Each newly published image still requires
a hardware boot test. Installing to eMMC is outside this repository's
automated test scope.

## Download and first boot

Download the `desk-box-rk3528-6.1.174-r*-a*.img.gz` asset and its `.sha256`
file from the
[latest release](https://github.com/hudrucan/xiaozhi-desk-box/releases/latest),
verify the checksum, then flash the compressed image with Balena Etcher or an
equivalent raw-image writer.

The debug image intentionally retains `root` / `1234` for bring-up and agent
access. Change the password before connecting the box to an untrusted network.
The legacy `/boot/armbian_first_run.txt` template is not included because the
current Armbian first-login path does not consume it.

## Build

The supported build path is
[`Build Desk Box Image`](https://github.com/hudrucan/xiaozhi-desk-box/actions/workflows/build-deskbox.yml)
on GitHub Actions. Its defaults point to the tested Bookworm base and pinned
rk35xx kernel release; both downloads are rejected if their SHA256 values
differ.

A local rebuild requires GNU/Linux x86_64, root privileges, loop devices and
GNU userland tools:

```bash
sudo ./rebuild -b deskbox -a false -k 6.1.174
```

macOS is suitable for editing and device-tree verification, but not for running
the image rebuild engine directly.

## Image pipeline

```mermaid
flowchart LR
    base["Pinned Bookworm base image"] --> rebuild["Desk Box rebuild"]
    kernel["Pinned rk35xx kernel bundle"] --> rebuild
    payloads["DTB + bootloader + AIC8800D80 firmware + BlueZ + front panel"] --> rebuild
    rebuild --> image["desk-box-rk3528-6.1.174-rN-aN.img.gz"]
    image --> audit["Read-only image audit"]
    audit --> release["GitHub Release"]
```

The build does not clone generic U-Boot or firmware trees. Repository-pinned
board dependencies must be present, and the workflow audits their hashes both
before and after rebuilding the image.

Each workflow attempt creates a new immutable release named
`desk-box-rk3528-<kernel>-r<run>-a<attempt>`. Existing releases and assets are
never edited or overwritten, so a previously tested image remains available for
fallback. The raw image is given the same compact basename before compression,
so extracting the `.img.gz` does not restore a long upstream `Armbian_...` name.

The image does not ship `armbian-update`, `armbian-sync`, `armbian-software` or
the associated generic software center. Kernel changes must go through this
pipeline so the Desk Box DTB, firmware allowlist and filesystem policy are
reapplied and audited before release.

## Validated boot chain

The microSD baseline was verified on the reference device:

- factory-compatible DDR V1.05 and SPL v1.04 at sector 64;
- U-Boot/FIT/ATF at sector 16384;
- root and boot partitions mounted from microSD;
- Linux `6.1.157-rk35xx-ophub` reached multi-user mode;
- Ethernet, SSH and AIC8800D80 Wi-Fi worked.

Kernel `6.1.174` is the current build default. Its release checksum and both
AIC8800 SDIO modules were verified before pinning, and the resulting image has
completed a successful microSD boot test on the reference Desk Box.

The board bootloader keeps the factory-compatible DDR parameters required by
the Micron DDR3 layout. See
[`BOOTLOADER.md`](build-armbian/armbian-files/different-files/deskbox/BOOTLOADER.md)
for provenance, offsets and hashes.

## Device tree and firmware

`rk3528-deskbox.dtb` starts from the exact opaque binary from the working
reference box (SHA256
`a918a217d36ef5325c10aeed4c1de70280b52a272559b8f80c54ada66367a5e2`).
The active binary (SHA256
`041e0471ea06401e6af663d026913b0fa5cdbcc825b1eac7fbebfe96dc52da74`)
contains the Lima configuration and UART2_M0 pinmux verified on the same
microSD installation. The Bluetooth delta selects GPIO3_A0/A1 for UART RX/TX,
GPIO3_A3 for CTS and GPIO3_A2 for RTS. The existing reset/wake properties are
unchanged. A normalized comparison against the prior Lima DTB shows no other
functional device-tree delta.

The internal `model` (`Rockchip RK3528 Generic TV Box`) and
`wifi_chip_type` (`ap6275s`) remain untouched. The latter is legacy
Rockchip platform data rather than AIC chip detection: the kernel identifies
the actual AIC8800D80 through its SDIO IDs and loads the pinned AIC modules and
firmware. Desk Box identity is supplied by the `deskbox` profile, the active
DTB filename and runtime metadata outside the opaque DTB.

The seven AIC8800D80 firmware files are an explicit allowlist matching both the
reference device and their documented upstream hashes. The tested regulatory
database/signature are included in initramfs, and the driver starts with
`country_code=VN custregd=0`. See
[`FIRMWARE.md`](build-armbian/armbian-files/different-files/deskbox/FIRMWARE.md).

The image also installs the pinned Debian Bookworm BlueZ package, frees UART2
from the serial console/getty and starts `btattach` only after the AIC8800D80
SDIO functions bind. The service uses the hardware-validated H4 transport at
1.5 Mbps; it does not toggle unverified GPIOs. See
[`PACKAGES.md`](build-armbian/armbian-files/different-files/deskbox/PACKAGES.md).

The hardware-validated front-panel service shows `----` during early boot,
switches to local `HH:MM` only after chrony reports a valid NTP reference,
blinks the colon and reflects Wi-Fi, LAN and external USB state. Time validity
is latched after the first synchronization, so a later network loss does not
blank the clock. Clock/alarm, play and pause remain unused. The service
bit-bangs the seller-proven FD6551 protocol on GPIO4_A2/A3 and requires no DTB
change. See
[`PANEL.md`](build-armbian/armbian-files/different-files/deskbox/PANEL.md).

## Repository map

| Path | Purpose |
|---|---|
| `.github/workflows/build-deskbox.yml` | Pinned build, audit and release pipeline |
| `action.yml` | Minimal single-target rebuild action |
| `rebuild` | Shared upstream image transformation engine |
| `build-armbian/armbian-files/different-files/deskbox/` | Desk Box rootfs overrides and bootloader |
| `build-armbian/armbian-files/platform-files/rockchip/` | RK3528 boot configuration and pinned known-good DTB |
| `build-armbian/armbian-files/common-files/usr/lib/firmware/aic8800_sdio/` | AIC8800D80 firmware allowlist |
| `build-armbian/armbian-files/common-files/usr/lib/firmware/regulatory.db*` | Tested regulatory database and signature |

The `rebuild` engine retains generic platform mechanics inherited from upstream
because they implement partitioning, rootfs conversion and boot assembly. The
public profile and workflow remain Desk Box-only.

## Companion projects

- [`xiaozhi-desk-robot`](https://github.com/hudrucan/xiaozhi-desk-robot) — robot firmware and UI.
- [`xiaozhi-desk-robot-server`](https://github.com/hudrucan/xiaozhi-desk-robot-server) — companion server stack.

## Notes and limitations

- A successful workflow proves image structure, hashes and filesystem policy;
  final hardware behavior still requires a microSD boot test.
- The image is a focused device target, not a general RK3528 distribution.
- eMMC installation, flashing and rollback are intentionally not automated by
  this repository.

## Upstream and license

This fork is derived from
[`ophub/amlogic-s9xxx-armbian`](https://github.com/ophub/amlogic-s9xxx-armbian)
and remains licensed under [GPL-2.0](LICENSE). Board payload provenance and
checksums are documented beside the relevant files.

# Desk Box Armbian

This fork rebuilds one target only: `deskbox`, an RK3528 TV box with 4 GB RAM,
32 GB eMMC and AIC8800D80 SDIO Wi-Fi.

## Target identity

- Board/profile: `deskbox`
- Runtime board: `Deskbox`
- Runtime model: `RK.Deskbox`
- Kernel family: `rk35xx/6.1.y`
- Active DTB: `rockchip/rk3528-deskbox.dtb`
- Device-tree model: `Rockchip RK3528 Desk Box`
- Default timezone: `Asia/Ho_Chi_Minh`
- Default wireless regulatory domain: `VN`

The DTB's source-compatible strings remain unchanged from the known-good input:
`rockchip,rk3528-box` and `rockchip,rk3528`. The validated bootloader applies
the same runtime SoC fixup seen on the reference device, where Linux reports
`rockchip,rk3528a` as the second compatible string.

## Build

Run the **Build Desk Box image** workflow from the Actions page. Its defaults
rebuild the pinned Bookworm arm64 server image with kernel `6.1.157` and publish
the resulting image plus SHA256 file to the release tag
`deskbox-bookworm-6.1.157`.

Local rebuilds require GNU/Linux x86_64 or a compatible GitHub Actions runner:

```bash
sudo ./rebuild -b deskbox -a false -k 6.1.157
```

The macOS host is suitable for editing and DTB verification, but the image
rebuild script depends on Linux loop devices, mounts and GNU userland tools.

## Validated boot chain

The SD baseline was verified on the reference Desk Box:

- factory-compatible DDR/SPL at sector 64;
- U-Boot/FIT/ATF at sector 16384;
- Linux `6.1.157-rk35xx-ophub`;
- root and boot partitions mounted from SD;
- AIC8800D80 firmware loaded and Wi-Fi connected;
- Ethernet, SSH and systemd multi-user boot operational.

See
[`build-armbian/armbian-files/different-files/deskbox/BOOTLOADER.md`](build-armbian/armbian-files/different-files/deskbox/BOOTLOADER.md)
for the bootloader provenance and hashes.

## DTB source and safety

`rk3528-deskbox.dts` is the canonical decompilation of the exact known-good
DTB. The rebuilt DTB intentionally changes only:

1. `/model`: `Rockchip RK3528 Generic TV Box` → `Rockchip RK3528 Desk Box`;
2. `/wireless-wlan/wifi_chip_type`: `ap6275s` → `AIC8800D80`.

The second change corrects the value returned by Rockchip's bound
`wlan-platdata` driver. SDIO detection and firmware selection continue to be
performed by the AIC8800 driver. GPIO, host-wake, pinctrl, pwrseq, controller
configuration and frequencies are unchanged.

## First boot

The legacy `/boot/armbian_first_run.txt` template is not included because the
current Armbian first-login implementation does not consume it. For headless
setup, use wired Ethernet for the first login or prepare a current Armbian
preset in `/root/.not_logged_in_yet` before imaging.

The debug image intentionally retains the current `root` / `1234` credentials
for device access during bring-up. Change that password before exposing the
device outside a trusted LAN.

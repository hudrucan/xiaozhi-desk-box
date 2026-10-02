# Desk Box device tree

The canonical source is `dts/rk3528-deskbox.dts`. Compiling it with `dtc`
produces the production binary byte-for-byte:

| Artifact | SHA256 |
| --- | --- |
| Canonical DTS | `5a556f2229b246a308190df1c9caeb386b7c5766bc5c62367fbd514abdfa9c31` |
| Production DTB | `eed4f973c4cb7088f52da8909bc4dc0654fd8a3f50c27eb44a6f0f66a2c7629c` |

The original working reference-box binary had SHA256
`a918a217d36ef5325c10aeed4c1de70280b52a272559b8f80c54ada66367a5e2`.
Its exact public provenance remains unknown. Subsequent deltas were derived
from hardware tests on the same Desk Box PCB and kept as a reproducible DTS.

## Validated Batch 1 delta

Compared as normalized DTS against the previous production binary, Batch 1:

- removes the zero-sized `drm-logo` and `drm-cubic-lut` reservations and their
  display-subsystem references;
- removes the unusable OP-TEE node and unused FIQ debugger;
- adds the RK3528 TVE `out-current` and `version` OTP cells;
- sets `esmart_lb_mode = [03]` for the verified VOP plane layout;
- removes UART2 DMA so the validated interrupt/PIO transport is explicit;
- changes only `wifi_chip_type` from stale `ap6275s` to `aic8800d80`.

The internal model and compatible strings remain unchanged:

```text
model = "Rockchip RK3528 Generic TV Box"
compatible = "rockchip,rk3528-box", "rockchip,rk3528"
```

The exact production DTB cold-booted successfully from microSD with Wi-Fi,
AIC8800D80 Bluetooth discovery, CVBS DRM output, Lima kernel binding, sound
PCM playback and the FD655 front-panel service active. UART2 reports its
expected interrupt-mode fallback; Bluetooth remains powered and unblocked.

## Validated USB 3.0 delta

The previous DTB limited DWC3 to `high-speed`, exposed only its USB 2.0 PHY and
left the shared RK3528 Combo PHY disabled. The Android DTB recovered from this
Desk Box eMMC instead connects DWC3 to both PHYs and enables the Combo PHY in
USB 3 mode. The production DTS now mirrors that hardware topology by:

- enabling `phy@ffdc0000`;
- adding the Combo PHY with type `4` to DWC3 `phys` and naming it `usb3-phy`;
- removing the `maximum-speed = "high-speed"` restriction.

Cold-boot validation on microSD placed a Kingston DataTraveler 3.0 on the xHCI
SuperSpeed bus at 5000 Mbit/s. A 1 GiB direct read completed at 118 MB/s with no
USB reset, disconnect or I/O error. Wi-Fi, Bluetooth and both front-panel units
remained active after the DTB change. Moving the same drive to the physical USB
2.0 port placed it on the xHCI USB 2.0 companion bus at 480 Mbit/s; a 256 MiB
direct read completed at 28.3 MB/s without any new reset or I/O error.

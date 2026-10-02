# Desk Box device tree

The canonical source is `dts/rk3528-deskbox.dts`. Compiling it with `dtc`
produces the production binary byte-for-byte:

| Artifact | SHA256 |
| --- | --- |
| Canonical DTS | `287b252d5b88e54c5b413ac1fe21da6b8cfa782c4bde82f009c13cd62e8ae1d9` |
| Production DTB | `bf284aae2aac156705657c8393f58c21bb1c306030fea5e1d7a78087586b129b` |

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

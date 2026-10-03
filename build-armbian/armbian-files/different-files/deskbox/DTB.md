# Desk Box device tree

The canonical source is `dts/rk3528-deskbox.dts`. Compiling it with `dtc`
produces the production binary byte-for-byte:

| Artifact | SHA256 |
| --- | --- |
| Canonical DTS | `8b78faaf7051f46777b60f785d8ea4677e4346816230db37a07f0951b1ca34a2` |
| Production DTB | `c910092b16135b5d5530a5030d0a98db049718c99139312dc9287dd235bc9b5e` |

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

## Validated PSCI CPU-idle delta

The Rockchip BSP DTS assigned CPU0/1 to `CPU_SLEEP0` but disabled that state,
while CPU2/3 used the enabled `CPU_SLEEP1` state. Linux initializes the PSCI
idle driver starting at CPU0 and rolls back all per-CPU registrations when the
first CPU has no usable state, leaving the system on the architectural WFI
fallback with `current_driver: none`.

The production DTS enables `CPU_SLEEP0` as PSCI standby (`0x0`) while retaining
the original PSCI power-down state (`0x10000`) for CPU2/3. Hardware validation
on microSD with BL31 v1.17 showed:

- PSCI hotplug tests passed;
- all four CPUs passed 10/10 PSCI suspend cycles with zero errors;
- CPU0/1 repeatedly entered and resumed from standby with zero rejected entries;
- CPU2/3 repeatedly entered and resumed from the power-down state;
- `psci_idle` remained active under the `menu` governor with systemd healthy and
  no RCU stall, watchdog lockup, oops or panic.

The normalized DTS delta is limited to enabling `CPU_SLEEP0` and changing only
its suspend parameter from power-down to standby. CPU2/3 retain the original
Rockchip deep-idle contract.

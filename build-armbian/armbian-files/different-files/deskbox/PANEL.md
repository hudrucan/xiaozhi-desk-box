# Desk Box front panel

The reference Desk Box uses an FD6551-compatible five-grid, seven-segment LED
controller connected through the controller's two-wire serial protocol.

## Provenance

The starting implementation was recovered read-only from the seller eMMC at
`/root/rk3528-install-emmc.sh` and its installed
`/usr/local/bin/fd655_clock.py` (SHA256
`29679cf4f198d3658aa166c871a7ae6554b2c0d6b0d8b66c3ea6d990204166e6`).
The GPIOs, digit order, colon and every named icon were then verified on the
reference panel while booted from microSD.

## Wiring and protocol

| Signal | RK3528 pin | Legacy sysfs GPIO |
|---|---|---:|
| DAT | GPIO4_A2 | 130 |
| CLK | GPIO4_A3 | 131 |

Bytes are transmitted MSB-first. DAT changes while CLK is low, data is sampled
on the rising edge, and each byte is followed by an ACK clock. The tested
half-clock delay is 5 microseconds. Initialization writes `0x01`, then `0x03`,
to control address `0x48`, exactly matching the seller implementation.

## Display map

| Address | Function |
|---:|---|
| `0x66` | Icon/colon bitmap |
| `0x68` | Left hour digit |
| `0x6a` | Right hour digit |
| `0x6c` | Left minute digit |
| `0x6e` | Right minute digit |

The verified decimal segment table is:

```text
0=0x3f  1=0x06  2=0x5b  3=0x4f  4=0x66
5=0x6d  6=0x7d  7=0x07  8=0x7f  9=0x6f
```

The complete hardware-verified icon bitmap at address `0x66` is:

| Bit | Mask | Panel symbol | Production behavior |
|---:|---:|---|---|
| 0 | `0x01` | Clock/alarm | Unused |
| 1 | `0x02` | USB | External non-hub USB device present |
| 2 | `0x04` | Pause | Unused |
| 3 | `0x08` | Play | Unused |
| 4 | `0x10` | Colon | Blinks once per second |
| 5 | `0x20` | LAN | `end0` carrier present |
| 6 | `0x40` | Wi-Fi | `wlan0` carrier present |

Play and pause are reversed relative to the common default ordering documented
by `linux_openvfd`; the table above records the observed Desk Box hardware.

## Boot and time validity

`deskbox-front-panel-early.service` runs before `sysinit.target` and writes
`----` as soon as the root filesystem has been remounted. The persistent
`deskbox-front-panel.service` is ordered after both that oneshot and
`chrony.service`, so the two processes never drive the panel concurrently.

The Desk Box exposes no RTC device. `fake-hwclock` restores only the last saved
timestamp and cannot account for time spent powered off, so it is not accepted
as authoritative. The clock changes from `----` to `HH:MM` only after
`chronyc tracking` reports all of the following in the current boot:

- a non-zero stratum;
- a non-zero reference ID;
- `Leap status: Normal`.

Once those conditions pass, validity is latched for the lifetime of the panel
service. Losing the network later does not blank a clock that was already
synchronized. Until then the colon stays off, while Wi-Fi, LAN and USB icons
continue to reflect their normal inputs.

## Validation

The following passed on the reference box:

- arbitrary four-digit output (`12:34`) and real `HH:MM` time;
- blinking colon;
- every icon toggled independently and identified visually;
- Wi-Fi icon tracking the connected `wlan0` interface;
- USB icon turning on after inserting a Kingston USB device;
- LAN icon bit and `end0` carrier input independently verified.

The FD6551 brightness command was exercised at the documented lowest and
highest duty settings, but the panel showed no visible change. Production
therefore preserves the seller's fixed `0x03` control value and exposes no
non-functional brightness setting.

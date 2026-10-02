# Desk Box pinned packages

The rebuild installs the repository-pinned Debian Bookworm BlueZ package into
the target root filesystem without using a network package repository.

| Package | Version | Architecture | SHA256 |
| --- | --- | --- | --- |
| `bluez` | `5.66-1+deb12u2` | `arm64` | `e99de09d48321f36f87d9e0017c57b57c6e38203b17b28640094a18c1d98905d` |

Source:
`https://deb.debian.org/debian/pool/main/b/bluez/bluez_5.66-1+deb12u2_arm64.deb`

The package and service startup were verified on the reference Desk Box. The
image frees UART2 from the serial console, masks its serial getty and attaches
the AIC8800D80 H4 transport with:

```text
btattach -B /dev/ttyS2 -P h4 -S 1500000
```

The DTB selects UART2_M0 (GPIO3_A0/A1 RX/TX, GPIO3_A3 CTS and GPIO3_A2 RTS).
The pre-start helper waits for both AIC SDIO functions to bind before starting
the transport; it does not drive reset or wake GPIOs. The final image removes
inherited `/var/lib/systemd/rfkill` state. The transport service starts after
`systemd-rfkill` and explicitly unblocks Bluetooth before `btattach`. Its
post-start helper waits for `hci0` and the restore transaction to finish,
removes only stale Bluetooth state, unblocks all Bluetooth rfkill nodes and
verifies them before BlueZ starts. BlueZ `AutoEnable=true` then powers the
registered controller. HCI Reset, BR/EDR + LE controller registration and a
BlueZ scan were validated on the reference box, including a reboot with both
Bluetooth persistence files deliberately set to blocked.

The Desk Box BlueZ drop-in matches the existing `/etc/bluetooth` directory
mode and disables only the unsupported experimental VCP/MCP/BAP plugins and
the unavailable telephony SAP backend. Classic A2DP, AVRCP, HID and GATT stay
enabled.

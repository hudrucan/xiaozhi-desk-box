# Desk Box pinned packages

The rebuild installs the repository-pinned Debian Bookworm BlueZ package into
the target root filesystem without using a network package repository.

| Package | Version | Architecture | SHA256 |
| --- | --- | --- | --- |
| `bluez` | `5.66-1+deb12u2` | `arm64` | `e99de09d48321f36f87d9e0017c57b57c6e38203b17b28640094a18c1d98905d` |

Source:
`https://deb.debian.org/debian/pool/main/b/bluez/bluez_5.66-1+deb12u2_arm64.deb`

The package and service startup were verified on the reference Desk Box. The
image frees UART2 from the serial console and masks its serial getty, but does
not auto-attach the Bluetooth HCI transport: the board-specific AIC8800D80
reset/wake GPIO mapping is not yet verified.

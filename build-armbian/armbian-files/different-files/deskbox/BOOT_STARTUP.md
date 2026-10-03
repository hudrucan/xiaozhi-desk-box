# Desk Box startup audit

## First-boot console setup

The r27-a1 image's first boot failed `console-setup.service` with a missing
`/tmp/tmpkbd.*` file. Subsequent boots succeeded because first-run had generated
the console cache. Both console setup and `systemd-tmpfiles-setup.service` were
ordered after `local-fs.target`, but not relative to each other. The boot
tmpfiles configuration cleans `/tmp`, which can remove setupcon's temporary
keymap while it is being generated.

The Desk Box drop-in orders console setup after tmpfiles setup. On the SD test,
the cached terminal script was moved to a backup to force regeneration during
the next boot. Tmpfiles completed at monotonic 7.978 s; console setup started at
7.989 s and completed successfully at 9.493 s. The cache was recreated and
systemd reported `running` with zero failed units. This tests the uncached
console path, not a complete freshly flashed first-run cycle.

## Foreign serial gettys

The upstream base enabled a getty for `ttyAML0`, which does not exist on RK3528.
Disabling it inside first-run was too late to cancel the initial device-wait
job, resulting in a 90-second timeout. The rebuild now disables inherited
`serial-getty@ttyAML0.service` and `serial-getty@ttyFIQ0.service` before first
boot. The final-image audit checks this policy. The existing `ttyS2` mask for
Bluetooth and the usable virtual console are unchanged.

## USB startup: unresolved

With the Kingston DataTraveler in the physical USB 3.0 connector, r27-a1 can
enumerate the same device first through EHCI at 480 Mbit/s, then disconnect it
and enumerate it through xHCI at 5000 Mbit/s. Partition reads during the
transition can fail. This was observed on first boot and a subsequent reboot;
it is distinct from the successful steady-state SuperSpeed read tests.

EHCI/OHCI are built into the kernel; `dwc3_of_simple` is a module already
included in the initramfs. An SD-only test force-loaded that module through
`conf/modules`, but that runs after init-top udev coldplug. It did not advance
xHCI initialization or eliminate the errors. It is not a production fix and
has not been included in this repository's build payloads.

A second SD-only test explicitly loaded the glue in `init-top` before udev.
xHCI then started at 8.739 s instead of approximately 9.5 s, but the drive
still first enumerated through EHCI, disconnected at 9.801 s, and caused a
buffer read error before enumerating through xHCI. Earlier userspace loading
therefore does not resolve the issue. Both test payloads were removed from
active SD configuration and the original initrd/uInitrd restored byte-for-byte.

The remaining sequencing question is below normal userspace: the built-in
legacy host starts probing the drive before `/init` can load the DWC3 glue.
Testing a kernel with that glue built in is one candidate, not a verified fix.
Do not delay storage reads or hide kernel messages and label that a hardware
fix. Further controller/PHY or firmware changes need separate SD validation.

No USB DTB, controller-disable, GPIO or bootloader changes are made by these
startup fixes. Further USB work must validate controller/PHY startup sequencing
from SD, including both physical connectors and cold boot, before changing the
production image. Do not treat a successful post-boot read as proof that the
startup transition is fixed.

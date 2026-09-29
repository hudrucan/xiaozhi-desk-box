# Desk Box SD to eMMC installer

`/usr/sbin/deskbox-install-emmc` is intentionally specific to the supported
Desk Box. It has no generic board bypass, target-device override or unattended
confirmation option.

## Safety model

The default invocation is read-only with respect to persistent storage and
block devices; it only opens the fixed lock file in `/run` tmpfs:

```bash
sudo deskbox-install-emmc --dry-run
```

The installer refuses to continue unless all of these are true:

- the running profile is `Deskbox` / `RK.Deskbox`;
- the runtime compatibles are `rockchip,rk3528-box` and `rockchip,rk3528a`;
- `armbianEnv.txt` contains exactly one `fdtfile=` and it is
  `rockchip/rk3528-deskbox.dtb`;
- ttyS2 is absent from the active kernel command line and boot environment,
  while `serial-getty@ttyS2.service` is masked and inactive;
- root is the second partition and `/boot` the first partition of an SD device;
- the source partition geometry matches the published Desk Box image;
- `/dev/mmcblk2` exists, identifies itself as an MMC device, is writable, is
  not the running source (verified from both partitions' parent block device
  and the parents' kernel major:minor identities), and has no mounted/open
  node, active swap or device-mapper holder;
- the repository-pinned bootloader, the factory IDB copies on the running SD
  and the working SD U-Boot/FIT match their audited hashes;
- the source data fits on eMMC with at least 512 MiB spare;
- the SD has at least 128 MiB free for the mandatory metadata backup;
- no apt, dpkg, active unattended-upgrade/apt-daily worker or package-manager
  lock holder is present. The idle `unattended-upgrade-shutdown
  --wait-for-signal` helper is not a package mutation and is intentionally not
  treated as an active upgrade.

`--install` repeats those checks and then requires the operator to type exactly
`ERASE /dev/mmcblk2`. There is deliberately no `--yes` option. The installer
revalidates the target size, eMMC name, CID, writable state and in-use state
both after confirmation and after completing the mandatory backup. Concurrent
installer invocations contend on the fixed
`/run/lock/deskbox-install-emmc.lock`, not the replaceable script inode.

## Exact eMMC layout

All offsets below use 512-byte sectors:

| Region | Sectors | Source |
|---|---:|---|
| Protective MBR + primary GPT | `0-33` | Newly generated |
| Reserved | `34-63` | Zeroed |
| Factory IDB/SPL copies | `64-5183` | Audited `bootloader.bin` |
| Sanitized IDB area | `5184-16383` | Audited `bootloader.bin` |
| U-Boot/FIT/ATF | `16384-32767` | Audited `bootloader.bin` |
| BOOT ext4 | `32768-1079295` | Clean filesystem populated from SD `/boot` |
| Alignment gap | `1079296-1081343` | Unallocated |
| ROOTFS ext4 | `1081344` to the final complete 2048-sector boundary minus one | Clean filesystem populated from SD `/` |
| GPT alignment gap | End of ROOTFS to the last usable GPT sector | Unallocated |
| Backup GPT | Final 33 sectors | Newly generated |

For the verified 32 GB `BJNB4R` eMMC, ROOTFS is explicitly
`1081344-61069311` (`59987968` sectors), followed by the unallocated alignment
range `61069312-61071326`. The explicit size prevents `sfdisk` alignment policy
from disagreeing with the post-partition geometry verifier.

The installer clears the entire old 16 MiB pre-partition area before creating
the GPT, then writes back only the audited IDB/SPL and U-Boot/FIT regions.
Rockchip vendor-storage sectors `7168-7295` are explicitly zeroed again after
the boot-chain write and checked against the all-zero SHA256. It does not
preserve or copy seller vendor-storage, secure-storage or runtime state from
the old eMMC.

Both new filesystems receive fresh UUIDs. The installer updates the target
`/etc/fstab` and `/boot/armbianEnv.txt`; no manual sector or UUID editing is
required. It preserves the source SD's root and BOOT mount options plus dump
and fsck-pass fields. In particular, `commit=600` is retained because it is
already the source image's root policy; the installer does not introduce it.

## Vendor U-Boot BOOT filesystem profile

The working SD BOOT filesystem and a regular-file filesystem created with the
target's e2fsprogs 1.47.0 were compared directly. Both are clean and use
130816 blocks, 130816 inodes, 4096-byte blocks, 256-byte inodes, and exactly
these static ext4 features:

```text
64bit dir_index dir_nlink ext_attr extent extra_isize filetype flex_bg
has_journal huge_file large_file metadata_csum resize_inode sparse_super
```

`needs_recovery` is deliberately excluded from comparison because it is a
transient flag on the mounted source filesystem. The installer starts from
`mkfs.ext4 -O none`, enables only the complete known-good feature allowlist,
and pins the block size, inode size and source's 4096 bytes-per-inode ratio.
It then reads the new superblock back with `tune2fs` before copying files. The
same profile is checked again after offline fsck. This prevents a
future e2fsprogs default (for example a newly enabled feature) from silently
creating a BOOT filesystem that the validated vendor U-Boot has never read.

## Backup, verification and failure recovery

Before the first destructive write, the installer creates a timestamped
directory under `/root/deskbox-emmc-backups/` on the running SD containing:

- a compressed copy of the first 32 MiB of the old eMMC;
- a compressed copy of its final 4 MiB;
- its partition-table dump, `lsblk`, `blkid`, CID and pre-install boot hashes;
- SHA256 checksums for both compressed raw captures.

The installer verifies both gzip streams and refuses to proceed if the current
partition table cannot be saved. The backup path is resolved back to the
running SD parent disk; a symlink or a path on the target eMMC is rejected.

After repartitioning, `partprobe` and `udevadm settle` run before the new
partition parent, start, size and GPT type are checked. Every `rsync --delete`
is preceded by an assertion that its destination is the expected target
partition mounted read-write. The root copy excludes `/boot`, `/dev`, `/proc`,
`/sys`, `/run`, `/tmp`, `/mnt`, `/media` and the SD backup directory, and uses
one-filesystem traversal so it cannot recurse into the target mounts.

After copying the live root filesystem twice, the installer synchronizes and
unmounts both target filesystems. `EXIT`, `INT`, `TERM` and error traps also
attempt this cleanup on every failure path. Mandatory offline `e2fsck` checks
must pass. It then mounts the result read-only and verifies the partition
geometry, mount sources/modes, filesystem labels, Desk Box identity, exact DTB
hash, exactly one production `fdtfile`, ttyS2/getty isolation, exact
fstab/rootdev UUID mappings with preserved mount policy, the pinned BOOT ext4
profile, non-broken enabled-service symlinks, IDB/SPL, the zeroed
vendor-storage range and U-Boot/FIT.

If anything fails after erasure begins, the SD remains unchanged and bootable.
Keep or reinsert it, boot from SD, review the printed error and saved backup,
run `--dry-run` again, then rerun `--install`. This is the supported recovery
path for an interrupted or incomplete install.

The automatic backup protects boot and partition metadata; it is not a full
copy of the previous seller filesystem. Restoring the old seller OS requires a
separate full-device backup or the matching factory firmware. Do not remove or
overwrite the tested SD until eMMC has completed a successful cold boot.

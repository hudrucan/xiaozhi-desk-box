# Desk Box RK3528 bootloader

`u-boot/bootloader.bin` is a sanitized composite made on 2026-09-28. It keeps
only the five identical factory idbloader copies required for Desk Box DDR
initialization and uses the public X88Pro13 artifact for all remaining bytes.
The rebuild flow copies it from sector 64 onward, so sectors 0-63 are not
written into generated images.

- Full sanitized 16 MiB SHA256: `f00a2e0b48fd29504292fc46007a505efe275f91b8b1863d499e6c141fc54eb8`
- Factory idbloader copies, sectors 64-5183: `a652135b8f9c00997a6739bd5356cb5758cee539b40fc88fb2f5b844891a9b16`
- Sanitized idbloader area, sectors 64-16383: `50533be4f13708af21f74693f2240fc0e5867f045d0d143249654abc3fb0eb44`
- U-Boot region, sectors 16384-32767: `2bef85bc03009c53078c310fd4447cd24bccbb2c2b5fd2e5bff74aa618ec17c1`

The five factory copies were read from `/dev/mmcblk2` on the working reference
box. They report `DDR V1.05 4bit PCB` and are kept because their DDR
initialization differs from the generic RK3528 artifact. Sectors 5184-32767
come from `ophub/u-boot` commit
`43d6b8d8eed75b955e341a2e57a8a6d48eea49b1`, file
`u-boot/rockchip/x88pro13/bootloader.bin` (full source SHA256
`ae20556014135a0cc5882ec9608e8a06912b9a5b7f88a0be2d664ac4155f38c2`).

The raw eMMC capture also contained Rockchip vendor and secure-storage blocks
outside the idbloader copies. Those blocks are deliberately excluded from this
artifact.

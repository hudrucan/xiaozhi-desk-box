# Desk Box RK3528 bootloader

`u-boot/bootloader.bin` is a sanitized Desk Box composite. It keeps the five
identical factory idbloader copies required for Desk Box DDR initialization,
the clean pre-FIT layout already validated by the project, and a Desk
Box-tested U-Boot/FIT payload with hardware RNG-backed KASLR seeding. The
rebuild flow copies it from sector 64 onward, so sectors 0-63 are not written
into generated images.

- Full sanitized 16 MiB SHA256: `ac2ca66613cfe2082daa4ae3137ca06b467551ea46ed362fca0bf811e20f50cc`
- Factory idbloader copies, sectors 64-5183: `a652135b8f9c00997a6739bd5356cb5758cee539b40fc88fb2f5b844891a9b16`
- Sanitized idbloader area, sectors 64-16383: `50533be4f13708af21f74693f2240fc0e5867f045d0d143249654abc3fb0eb44`
- U-Boot region, sectors 16384-32767: `d63b5cb1ff7a8f15b91062a6f548b680415d7dd4086e6e6a8b227718b5d1300d`
- KASLR-enabled FIT: `cbd416ec9ebaaff18aca86b7d8e5b755dfff740ad066ca9615892d373e046b40`

The five factory copies were read from `/dev/mmcblk2` on the working reference
box. They report `DDR V1.05 4bit PCB` and are kept because their DDR
initialization differs from the generic RK3528 artifact. The sanitized
pre-FIT bytes in sectors 5184-16383 came from `ophub/u-boot` commit
`43d6b8d8eed75b955e341a2e57a8a6d48eea49b1`, file
`u-boot/rockchip/x88pro13/bootloader.bin` (full source SHA256
`ae20556014135a0cc5882ec9608e8a06912b9a5b7f88a0be2d664ac4155f38c2`).

The FIT at sector 16384 was rebuilt on 2026-10-03 from Radxa U-Boot commit
`5c2828916052cae4a3d0d69ab426d4cbc841f63d`, using the RK3528 Hinlink board
inputs from Armbian build commit
`1dfb077e1549174a8dd3b74824beea98ffd73cd0` and
`rk3528_bl31_v1.17.elf` from `armbian/rkbin` commit
`1d3c61008fa823936ae7a59615393f8294b64456`. The only intentional U-Boot
feature addition is a backport of the upstream `kaslrseed` command; it reads
the existing Rockchip hardware RNG and writes `/chosen/kaslr-seed` immediately
before Linux boots. The exact backported command source is retained beside the
artifact as `u-boot/kaslrseed.c`. The build additionally enables
`CONFIG_CMD_KASLRSEED`; the existing `CONFIG_DM_RNG` and
`CONFIG_RNG_ROCKCHIP` support remain enabled. The original `Sb9a0` source
revision embedded in the old binary is no longer present in the public source
history, so this is a source rebuild from the closest retrievable pre-build
revision rather than a binary patch of that payload.

The rebuilt FIT preserves the exact known-good U-Boot DTB and ATF payloads:

- U-Boot DTB: `db83a0738a78c82a0c5e5913509555359900fe2075497362dabc7ad2e4a3decc`
- ATF 0x00080000: `2493d19c1ea766427c238ac7f34d055548136f97b0206de786173585f595558f`
- ATF 0xfe48d000: `8ce368911147cbcc0a3659cbe5af8ca04c9e246eded8fae271d2b6475a2d45d6`
- ATF 0xfe490000: `bc35c9ef8551f05bb8cab064be4b6cbcb98ea10a67ede092016ccce04200bd09`

The exact sanitized 8 MiB U-Boot region was boot-tested from microSD across
three reboots. Linux reported `KASLR enabled`, the kernel `_stext` address
changed on every boot, systemd reached `running`, and no units failed. eMMC was
not modified during this validation.

The raw eMMC capture also contained Rockchip vendor and secure-storage blocks
outside the idbloader copies. Those blocks are deliberately excluded from this
artifact.

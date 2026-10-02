# Desk Box firmware provenance

The image carries the seven AIC8800D80 SDIO firmware files stored under
`common-files/usr/lib/firmware/aic8800_sdio`, plus the regulatory database and
signature verified on the reference Desk Box.

- Source: `ophub/firmware`
- Source commit: `4aef5903bc6c04c4bce408c8883bc05f43f168ba`
- Source path: `firmware/aic8800_sdio`
- Verification: every file originally matched the running Desk Box reference
  system on 2026-09-29. Binary firmware remains exact; the text configuration
  has the documented two-key cleanup below.

| File | SHA256 |
| --- | --- |
| `aic_userconfig_8800d80.txt` | `8490a8609f8801f9cc33617c975372f4a45b62a59c3728d8975f09de4ed5e678` |
| `fmacfw_8800d80_u02.bin` | `6d121e015ff1fb90a90649627d663511804771b37f6cb44c97066cfc313a067a` |
| `fmacfwbt_8800d80_u02.bin` | `465106f3bb2945bbdebea99f6cde9465ae00d5829e188499d42449cbdf4fe82c` |
| `fw_adid_8800d80_u02.bin` | `a526cbd02fcdc495f049f3ad6b5933cb08cd984b16790c716a060d582fee1a56` |
| `fw_patch_8800d80_u02.bin` | `26183182bf07f8f7581e82da8b606d222591a12c56772e75146588eef5196242` |
| `fw_patch_table_8800d80_u02.bin` | `a9f663eb7443bc8046f2479cedfcdd93001eb64761f855317dbdbbc077f475cf` |
| `lmacfw_rf_8800d80_u02.bin` | `19b2d6b2320b67cb874c5c5c266a8f348cf423d00c0b22d4ad2c737cc603beab` |

The running kernel requested the patch table, ADID, patch and FMAC firmware
from this directory. The remaining three files are retained as part of the
matching AIC8800D80 firmware set, including Bluetooth support.

The text configuration is based on the pinned upstream file. Its unsupported
`loss_enable` and `loss_value` keys are removed because this exact driver logs
both as invalid commands; no binary firmware file is modified.

| Regulatory file | SHA256 |
| --- | --- |
| `regulatory.db` | `9d171281bfe7acc5d203007427f6075b704b7a48ff42ae25b9f490a0118fe7d2` |
| `regulatory.db.p7s` | `d1170298577027c2da346242627ff6cad09fbebaa96a6b2de07ada7c873dd337` |

The Desk Box initramfs hook includes both files before the AIC8800D80 probes.
The module is configured with `country_code=VN custregd=0`; the latter keeps
the driver's permissive testing rules disabled.

# OnePlus 15 OOS 16.0.10.601 — Linux 6.12.112 KMI6 watchdog release

This is the physically tested, boot-only Linux 6.12.112 release for the
OnePlus 15 `infiniti` / `canoe` running OxygenOS 16.0.10.601(EX01).

It preserves the stock OxygenOS `.601` DLKM and supporting partitions while
preventing the Oplus/QCOM hung-task detector from reporting four proven idle
service-thread waits as active hangs. Real Secure World, QPACE, HFI, and
hardware-fence transaction stalls remain observable.

## Tested combination

- Physically tested device: CPH2749 / OP611FL1
- Firmware: `CPH2749_16.0.10.601(EX01)`
- Kernel: `6.12.112-android16-6-o-g8dd9cb4790b7-4k`
- KMI generation: Android 16 generation 6
- Source commit containing the tested tree: `1cd6164a81e631e33a3d8181c357630607f5fd65`
- Boot asset: `OnePlus15-OOS16.0.10.601-Linux6.12.112-KMI6-boot.img`
- Boot SHA-256: `a44ee825f3eb58ce84e7c2d24ebaeccce4669695f9c57bc0904184ffe10d4f6f`
- Embedded Image SHA-256: `6afffa074630cdfa52b50ed7881e0ef85c82731186ee034637671ba080ee7531`
- TWRP asset: `OnePlus15-OOS16.0.10.601-Linux6.12.112-KMI6-TWRP.zip`
- TWRP ZIP SHA-256: `9e946551c2cf196e2a9cf685ff58a64bf87e87baf2af9d73d1c612a537312b5e`

The release artifact was built immediately before the tested source change
was committed, so `uname -r` retains the parent identifier `g8dd9cb4790b7`.
The committed tree at `1cd6164a81e6` is content-identical to the tested source
tree; the physically tested artifact was not rebuilt for publication.

Do not install this release on `.400`, `.500`, or another OxygenOS build.

## Validation

- common kernel and production Canoe distribution: PASS;
- strict KMI and enforced common ABI: PASS;
- Canoe ABI generation: PASS;
- boot-container and AVB verification: PASS;
- stock modules: 1,021 checked, 985 active compatible, 36 dormant;
- hard imports: 56,594 / 56,594 resolved;
- MODVERSIONS: 57,621 / 57,621 matched;
- missing providers, CRC mismatches, namespace failures, blockers: 0;
- exact boot write/read-back: PASS;
- Android, user0, F2FS `/data`, and `inlinecrypt`: PASS;
- Wi-Fi, Bluetooth, NFC, LTE/RMNET, USB/ADB, ZRAM, and CPUFreq: PASS;
- pstore and fatal kernel/module scans: PASS.

The device was monitored for 692 seconds, crossing all previously observed
hung-task report windows. No target ADCI, ZRAM, HFI, or hardware-fence idle
warning recurred. No panic, Oops, BUG, soft lockup, RCU stall, blocked-task,
module-loader, or DRM/GEM failure was observed.

USB-disconnected deep suspend was not tested because USB remained connected
for evidence collection. Camera, audio, and fingerprint were not directly
exercised during this specific watchdog canary. Existing unrelated platform
warnings are documented in the validation record.

## TWRP installer scope

Both assets contain the identical physically tested boot image. The ZIP:

- positively identifies the OnePlus 15 `infiniti` / `canoe` family;
- accepts CPH2745, CPH2747, CPH2749, and PLK110 regional identifiers;
- requires the exact OxygenOS 16.0.10.601 stock EROFS `system_dlkm` contract;
- verifies active A/B slot, partition capacity, backup, write, and full
  read-back hashes;
- writes only the active boot partition;
- restores the verified backup if post-write read-back fails.

Only CPH2749 / OP611FL1 on OxygenOS 16.0.10.601 was physically tested. The
archive contains no `system_dlkm`, `vendor_dlkm`, `vendor_boot`, `init_boot`,
DTBO, VBMeta, modem, radio, persist, metadata, userdata, or slot-metadata
payload.

Full evidence:
[6.12.112 watchdog validation](https://github.com/travismills82/oneplus15-sm8850-oos-kernel/blob/main/docs/validation/firmware-16.0.10.601/oos1610601-linux-6.12.112-watchdog-validation-2026-10-08.md)

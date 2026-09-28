# OnePlus 15 OOS 16.0.10.601 — Linux 6.12.89 KMI6 stable

This is the physically tested, boot-only Linux 6.12.89 release for the
OnePlus 15 `infiniti` / `canoe` running OxygenOS 16.0.10.601(EX01).

## Qualified combination

- Physically tested device: CPH2749 / OP611FL1
- Firmware: `CPH2749_16.0.10.601(EX01)`
- Kernel: `6.12.89-android16-6-o-g5d9b99c7d104-4k`
- KMI generation: Android 16 generation 6
- Tested runtime source: `5d9b99c7d1047fe6d392dc7ab5e6129d3981b5c8`
- Boot asset: `OnePlus15-OOS16.0.10.601-Linux6.12.89-KMI6-boot.img`
- Boot SHA-256: `c704c189e5075e6104e53dfbbb8b5d64d289f9a9a04464f4c14d5a604ec6d895`
- TWRP asset: `OnePlus15-OOS16.0.10.601-Linux6.12.89-KMI6-TWRP.zip`
- TWRP ZIP SHA-256: `3cc6509178b713eb397d0400b8c9d366050c9195019e244abf5bfe8452161de7`

Do not install this release on `.400`, `.500`, or another OxygenOS build.

## Validation

The stock OOS 16.0.10.601 Rust Binder incompatibility is repaired without
replacing `rust_binder.ko`, changing CRCs, disabling MODVERSIONS, or weakening
KMI enforcement. The exact release image passed:

- full active-boot backup, write, and complete partition read-back;
- Android boot and existing encrypted user0 `RUNNING_UNLOCKED`;
- F2FS `/data` with `inlinecrypt`;
- stock `rust_binder.ko` load with zero missing or version-disagreement errors;
- all 56,600 stock ELF imports and 57,621 version records;
- WPA3 WLAN, LTE/RMNET, Bluetooth, and USB/ADB initialization;
- owner-confirmed TWRP, audio, camera, fingerprint, and NFC operation;
- targeted module, FBE, DRM/GEM, GPU-fault, panic, Oops, and BUG scans.

## Installation scope

Both assets contain the identical physically tested boot image. The ZIP:

- positively identifies the OnePlus 15 `infiniti` / `canoe` family;
- recognizes CPH2745, CPH2747, CPH2749, and PLK110 regional identifiers;
- requires the exact `.601` firmware manifest and stock EROFS `system_dlkm`;
- verifies active A/B slot, snapshot state, partition capacity, and hashes;
- makes and verifies a complete durable active-boot backup;
- writes only the active boot partition;
- verifies the complete read-back and restores the backup on failure.

Only CPH2749 / OP611FL1 on OxygenOS 16.0.10.601 is physically qualified.
Other regional variants remain installer-supported through positive family
detection and the exact firmware payload contract; physical reports are
welcome.

The archive contains no `system_dlkm`, `vendor_dlkm`, `vendor_boot`, DTBO,
VBMeta, modem, radio, persist, metadata, userdata, or slot-metadata payload.
Those partitions remain stock.

Full evidence:
[physical qualification](../../validation/firmware-16.0.10.601/oos1610601-linux-6.12.89-physical-validation-2026-09-28.md)

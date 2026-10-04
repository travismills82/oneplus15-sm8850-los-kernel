# OnePlus 15 OOS 16.0.10.601 — Linux 6.12.95 KMI6 canary

This is the physically boot-tested, boot-only Linux 6.12.95 canary for the
OnePlus 15 `infiniti` / `canoe` running OxygenOS 16.0.10.601(EX01).

It is published as a prerelease. Linux 6.12.89 remains the fully qualified
rollback baseline until the remaining 6.12.95 qualification items are
completed.

## Tested combination

- Physically tested device: CPH2749 / OP611FL1
- Firmware: `CPH2749_16.0.10.601(EX01)`
- Kernel: `6.12.95-android16-6-o-g02714090683b-4k`
- KMI generation: Android 16 generation 6
- Tested runtime source: `02714090683b0c04a1cc5de357c579b18dc814dd`
- Boot asset: `OnePlus15-OOS16.0.10.601-Linux6.12.95-KMI6-boot.img`
- Boot SHA-256: `f4c64ffb73506b740aee22fbc1f2f1d573a4972784bf598f29a4c012f09c81f2`
- Embedded Image SHA-256: `c0fc3d7b443731bcc2bc48826269f438d9f3bb5e3f608038e4cfdf13c0e9ae2d`
- TWRP asset: `OnePlus15-OOS16.0.10.601-Linux6.12.95-KMI6-TWRP.zip`
- TWRP ZIP SHA-256: `1a91b0bc409fd7aa68f3ac3bd524dfcd4b5bd5ab194f051a252500a3e9148ca8`

Do not install this release on `.400`, `.500`, or another OxygenOS build.

## Static validation

- production Canoe distribution: PASS;
- enforced common ABI comparison: PASS with an empty generated diff;
- strict KMI and symtypes: PASS;
- Canoe ABI generation: PASS;
- stock modules checked: 1,021;
- active compatible modules: 985;
- dormant modules: 36;
- hard ELF imports resolved: 56,594 / 56,594;
- MODVERSIONS records matched: 57,621;
- missing providers, CRC mismatches, namespace failures, and blockers: 0;
- stock Rust Binder provider contract and runtime module load: PASS;
- maintained generated GKI module signatures: 90 / 90 SHA-256 PKCS#7.

## Physical canary

The exact released boot image passed:

- complete active-boot backup, write, and full partition read-back;
- TWRP metadata and PIN decryption;
- userdata mapper creation;
- F2FS `/data` mount with `inlinecrypt`;
- CE and DE data access;
- two clean Android boots;
- `sys.boot_completed=1` and user0 `RUNNING_UNLOCKED`;
- stock `rust_binder.ko` load with no missing or version-disagreement errors;
- Wi-Fi 6 GHz/WPA3-SAE, cellular data, Bluetooth, and NFC;
- camera launch, USB/ADB, charging, ZRAM, and display composition;
- panic, Oops, BUG, lockup, RCU-stall, module-loader, DRM/GEM, and pstore
  fatal-record scans.

USB-disconnected deep suspend was not tested. Audio service and fingerprint
HAL health passed, but direct owner confirmation of playback and biometric
authentication was not completed during this session. The release therefore
remains a boot/stability canary rather than a fully qualified stable baseline.

The Oplus watchdog reported the same `adci_thread`, `zram_comp`, and
`hfi_core_dbg_cl` completion waits seen on the known-good 6.12.91 baseline.
Their call paths were unchanged and no associated functional failure was
observed.

## Installation scope

Both release assets contain the identical physically tested boot image. The
ZIP:

- positively identifies the OnePlus 15 `infiniti` / `canoe` family;
- recognizes CPH2745, CPH2747, CPH2749, and PLK110 regional identifiers;
- requires the exact `.601` firmware manifest and stock EROFS `system_dlkm`;
- verifies active A/B slot, partition capacity, backup, write, and full
  read-back hashes;
- writes only the active boot partition;
- restores the verified backup if the post-write read-back fails.

Only CPH2749 / OP611FL1 on OxygenOS 16.0.10.601 was physically tested. The
archive contains no `system_dlkm`, `vendor_dlkm`, `vendor_boot`, DTBO, VBMeta,
modem, radio, persist, metadata, userdata, or slot-metadata payload.

Full evidence:
[boot/stability canary](https://github.com/travismills82/oneplus15-sm8850-oos-kernel/blob/main/docs/validation/firmware-16.0.10.601/oos1610601-linux-6.12.95-boot-canary-2026-10-04.md)

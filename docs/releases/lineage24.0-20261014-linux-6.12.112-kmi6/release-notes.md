# OnePlus 15 LineageOS 24.0 `20261014` — Linux 6.12.112 KMI6

This release is the physically tested Linux 6.12.112 kernel package for the
OnePlus 15 `infiniti` / Canoe running the exact LineageOS nightly below.

## Required ROM

- ROM: `lineage-24.0-20261014-NIGHTLY-infiniti`
- Build ID: `CP2A.260605.016`
- Incremental: `5521dfa82f`
- Android security patch: `2026-10-01`
- Tested device: CPH2749 / OP611FL1

Do not install this release on OxygenOS, another OnePlus model, or a different
LineageOS build. A later ROM update may replace these partitions or require a
new matched kernel/module build.

## Assets

Both image assets are required:

| Asset | Partition | Size | SHA-256 |
|---|---|---:|---|
| `OnePlus15-LineageOS24.0-20261014-Linux6.12.112-KMI6-boot.img` | active-slot `boot` | 100,663,296 | `c98f46a1fefd2b890d0370d8743d63ef35aabc055d25a90dca4395920bc79226` |
| `OnePlus15-LineageOS24.0-20261014-Linux6.12.112-KMI6-system_dlkm.img` | active-slot `system_dlkm` | 8,327,168 | `18524c480a07047c09a284e70ed83395afc74921c960993adc75a5d730e5c33e` |

The `system_dlkm` image preserves the exact Lineage 88-module system
population and replaces only `rust_binder.ko` with the version built and signed
for this kernel. The installed stock `vendor_dlkm` remains unchanged.

## Kernel identity

- kernel: `6.12.112-android16-6-o-g499f2bb26e85-4k`;
- KMI: Android 16 generation 6;
- embedded `Image` SHA-256:
  `7a04fc65e73dc52fd6b1938299192fc98a516b207b127ee7c8422cfb9d0972a4`;
- tested build parent: `499f2bb26e859260665a81d195e5fe4c1c81d8d7`;
- source commit containing the content-identical signing fix:
  `efa73b7de1eb`.

The exact tested artifact was not rebuilt after committing the signing-key
configuration, which is why `uname -r` retains `g499f2bb26e85`.

## Validation

- production Canoe build: PASS;
- strict KMI and enforced common ABI: PASS;
- Canoe ABI generation: PASS;
- 640-module Lineage oracle: PASS;
- 36,671 / 36,671 hard imports resolved;
- 37,313 / 37,313 version records matched;
- missing providers, CRC mismatches, namespace failures, and blockers: 0;
- exact boot write/read-back: PASS;
- Android, user0, FBE, F2FS `/data`, and `inlinecrypt`: PASS;
- Rust Binder: PASS;
- Wi-Fi, Bluetooth, LTE data, and NFC: PASS;
- recovery touchscreen reboot and subsequent Android boot: PASS;
- fatal kernel/module scan: PASS.

Camera, audio, and fingerprint services initialized. Direct end-user camera,
audio, fingerprint, and USB-disconnected deep-suspend tests were not performed
in this session.

## Installation boundary

Back up the current active-slot `boot` and `system_dlkm` partitions before
installation. `system_dlkm` is a logical partition and must be flashed in
fastbootd, not bootloader fastboot. Flash both assets to the same active slot.

This release does not modify `vendor_dlkm`, `vendor_boot`, `init_boot`, DTBO,
VBMeta, modem/radio, persist, metadata, userdata, or slot metadata. Retain the
matching stock Lineage images for rollback.

Full evidence:
[physical validation](../../validation/lineage-24.0/oneplus15-lineage24.0-20261014-linux-6.12.112.md).

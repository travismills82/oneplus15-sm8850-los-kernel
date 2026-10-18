# OnePlus 15 LineageOS 24.0 Linux 6.12.112 physical validation

Date: 2026-10-18
Status: **PASS for the exact tested two-image payload**

## Tested contract

| Item | Tested value |
|---|---|
| Device | OnePlus 15 CPH2749 / OP611FL1 (`infiniti` / Canoe) |
| ROM | `lineage-24.0-20261014-NIGHTLY-infiniti` |
| Build ID / incremental | `CP2A.260605.016` / `5521dfa82f` |
| Android security patch | `2026-10-01` |
| Active slot | `_a` |
| Kernel | `6.12.112-android16-6-o-g499f2bb26e85-4k` |
| Tested build parent | `499f2bb26e859260665a81d195e5fe4c1c81d8d7` |
| Committed content-equivalent source | `efa73b7de1eb` |
| `boot.img` SHA-256 | `c98f46a1fefd2b890d0370d8743d63ef35aabc055d25a90dca4395920bc79226` |
| Embedded `Image` SHA-256 | `7a04fc65e73dc52fd6b1938299192fc98a516b207b127ee7c8422cfb9d0972a4` |
| `system_dlkm.img` SHA-256 | `18524c480a07047c09a284e70ed83395afc74921c960993adc75a5d730e5c33e` |
| Rebuilt `rust_binder.ko` SHA-256 | `0b417fe58b514b8af431a9e76ecb65ea70180b7c356580bff314576fa0b09604` |
| Effective config SHA-256 | `b33b65841a205b5e4bbbdb2675535835e5ca2798edead4d33507bd258d4313c6` |
| Common `Module.symvers` SHA-256 | `a1665917c5579d1c59f3d91197e8ff22188404163ef28e2a046a9c998b2366d4` |

The build was made with the public LineageOS stock GKI module-signing
certificate selected by the final committed config. The physically tested
artifact was deliberately retained rather than rebuilt after committing that
content, so its release string contains the build-parent identifier
`g499f2bb26e85`.

## Static qualification

- production Canoe distribution: PASS;
- strict common KMI: PASS;
- enforced common/GKI ABI comparison: PASS;
- Canoe device-module ABI generation: PASS;
- Lineage module population: 640 checked;
- compatible: 443;
- dormant: 197;
- hard ELF imports: 36,671 / 36,671 resolved;
- MODVERSIONS records: 37,313 / 37,313 matched;
- missing providers: 0;
- CRC mismatches: 0;
- namespace failures: 0;
- blockers: 0.

The hybrid `system_dlkm` contains the exact 88-module stock Lineage system
population with only `rust_binder.ko` rebuilt for the candidate kernel. The
exact 552-module stock `vendor_dlkm` remains installed. No generic Canoe DLKM
image was used.

## Physical result

The active `boot_a` partition was backed up and verified before the test. The
candidate `boot.img` and hybrid `system_dlkm.img` were flashed to slot A. The
candidate boot partition was read back byte-for-byte with the exact published
SHA-256.

Observed PASS:

- Android boot and `sys.boot_completed=1`;
- user0 `RUNNING_UNLOCKED`;
- FBE with encrypted F2FS `/data` and `inlinecrypt`;
- verified EROFS `/system_dlkm` mount;
- `rust_binder` loaded;
- 557 runtime-loaded modules, matching the restored Lineage runtime count;
- Wi-Fi enabled and connected;
- Bluetooth ON with zero Bluetooth service crashes;
- LTE voice/data registered and data state connected;
- NFC enabled;
- camera, audio, fingerprint, SurfaceFlinger, and system services initialized;
- recovery boot and touchscreen `Reboot system now` action;
- second Android boot after recovery with user0 unlocked;
- no panic, Oops, BUG, soft/hard lockup, RCU stall, hung-task report,
  unknown symbol, version disagreement, protected-symbol denial, or module
  verification failure in the captured candidate logs;
- no recurrence of the prior `adci_thread`, `zram_comp`, or
  `hfi_core_dbg_cl` warning through the 210-second observation window.

Direct end-user camera capture, audio playback, fingerprint authentication,
and USB-disconnected deep suspend were not exercised in this session. Their
services initialized without a captured kernel failure.

## Failure resolved

The first Lineage candidate reached the splash screen but could not complete
boot because stock Lineage modules were signed by a certificate not trusted by
the kernel. A direct module-load diagnostic showed protected-symbol denial
with `-EACCES`. The final kernel embeds the exact public Lineage signing
certificate while preserving module signature verification. The successful
canary loaded the stock module population and completed Android startup.

## Payload and rollback boundary

Required release payloads:

1. active-slot `boot`;
2. matching active-slot `system_dlkm`.

The exact stock Lineage rollback hashes captured before testing are:

- `boot_a`: `7ab6b70931631831f3e3381a60bb1bfefe0822eddae4ed6c7883e653695ff911`;
- `system_dlkm`: `3947c061321b6d8358020feba6138533540741f4e2fb6a09abaf81c55630b788`.

Stock `vendor_dlkm`, `vendor_boot`, `init_boot`, DTBO, VBMeta, metadata, and
userdata were not modified. Both release images are build-specific and must be
replaced by matching ROM images before changing to another Lineage build.

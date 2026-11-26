# LineageOS 24 kernel synchronization validation

Date: 2026-11-26

## Target identity

- Device: OnePlus 15 / `infiniti` / Qualcomm SM8850 Canoe
- OTA incremental: `63eb77a308`
- Build fingerprint: `OnePlus/CPH2745IN/OP611FL1:17/CP2A.260605.016/B.R4T3.50a3663-29f0eba-29fce1c:user/release-keys`
- Security patch level: `2026-11-01`
- Stock boot SHA-256: `f7ee42343ee769df2ca1fe39e126dd9249b7b076de8258744ddcdce95a0f9611`
- Stock system_dlkm SHA-256: `aaf0f22d1cc88de30224551d6d24ee6291b223069fdd46b1508ef77489253a61`
- Stock vendor_dlkm SHA-256: `db08a3fd2d3a8f06bfdf8a3c68148ca095db0bdc6cc566bc1e3162dba9c52603`

## Kernel evidence

- Kernel release: `6.12.119-android16-6-o-g46d53f13f126-4k`
- `Image` size: 43,383,296 bytes
- `Image` SHA-256: `cbe74e11b734eb6b9b6204cfda42e959c35c9b076bd68791219676f2096540e4`
- `vmlinux` SHA-256: `cac1c15b94ec4fa29e716f813d7791a8747b87ca9bc01c53f5342a86b567dc13`
- `Module.symvers` SHA-256: `8f67ca352ad38d8b690784be94a1e7f1c89764b3ec158ed802857c19a14662ea`
- `modules.builtin` SHA-256: `4e25d13aab1e57642f2ad969d0f2ed3fb6162457df39e0b28f91a9a72d7e3712`

The effective configuration contains:

- `CONFIG_RUST=y`
- `CONFIG_ANDROID_BINDER_IPC=y`
- `CONFIG_ANDROID_BINDER_IPC_RUST=y`
- `CONFIG_MODVERSIONS=y`
- `CONFIG_GENDWARFKSYMS=y`
- `CONFIG_MODULE_SIG=y`
- `CONFIG_MODULE_SIG_PROTECT=y`
- `CONFIG_FS_ENCRYPTION_INLINE_CRYPT=y`

`modules.builtin` records the Rust Binder object and `vmlinux` contains its initialization, open, and ioctl paths. No replacement `rust_binder.ko` is present in the candidate distribution.

## Stock module oracle

The exact target OTA supplied 88 `system_dlkm` modules and 552 `vendor_dlkm` modules. The final oracle result is:

- Compatible modules: 563
- Built-in satisfied: 1 (`rust_binder`)
- Dormant/not actively loaded: 76
- Active blockers: 0
- Versioned imports resolved: 36,445 / 36,445
- MODVERSIONS CRC matches: 37,084
- CRC mismatches: 0
- Namespace failures: 0
- Symbol/CRC/namespace oracle result: PASS

The vendor_boot copies were also covered through the normal, vendor_boot, and recovery load lists. The stock module images themselves were not changed.

The initial oracle did not prove that the candidate's built-in trusted key accepted every stock module under `CONFIG_MODULE_SIG_PROTECT`. Physical diagnostics showed that omission was material: November 25 stock `rfkill.ko` was rejected because the original candidate trusted the October 14 certificate. The repaired kernel embeds the exact November 25 certificate. A separate CMS audit verified all 109 signed modules, while the protected-export audit accounted for 108 protected modules, 494 protected exports, and all active unsigned consumers with zero failures. Overall module compatibility is PASS for the repaired candidate.

## ABI and KMI checks

| Check | Result |
|---|---|
| Canoe production build | PASS |
| Common KMI symbol allowlist | PASS |
| `--kbuild_symtypes` KMI build | PASS |
| Canoe device-inclusive ABI | PASS |
| Exact stock-module symbol/CRC oracle | PASS |
| Runtime protected-export trust | PASS in repaired candidate |
| Common enforced ABI distribution | PASS |

The original reference delta was reviewed, the downstream 6.12.119 ABI definition was advanced with the repository's supported update target, exact equality with the generated ABI was verified, and the enforced distribution comparison was rerun successfully. ABI/KMI and repaired module-trust qualification passed.

## Boot image validation

The repaired image is 100,663,296 bytes and has SHA-256 `5cbfcbae7e59d2786fbd935cca6c264354a90b7f510f637d11af4f4db9cfe6ee`. It preserves boot header v4, Android 17.0.0 metadata, November 2026 patch metadata, empty ramdisk/cmdline, stock partition size, AVB 1.4.0 release string, rollback index, salt, properties, and public-key identity. AVB verification succeeds.

The structural PASS is independently backed by temporary and persistent physical boot success.

## Physical status

- Fastboot flash performed: YES, `boot_b` only
- Temporary `fastboot boot` canary performed: YES
- Candidate kernel entry and ADB: PASS
- Qualcomm ramdump: NOT OBSERVED
- Android boot tested: PASS
- Encrypted user0 under candidate: PASS
- Hardware/service smoke tests: PASS
- Stock rollback boot: PASS
- Stock encrypted user0 unlock: PASS
- Stock audio-effect factory registration: PASS
- Protected branch or stable release modified: NO
- Development branch pushed: NO

Live preflight confirmed incremental `63eb77a308`, SPL `2026-11-01`, active slot `b`, stock health, user0 unlock, and both candidate and rollback hashes. The repaired image first booted non-persistently. Android completed boot, user0 reached `RUNNING_UNLOCKED`, CE storage was accessible, SELinux remained enforcing, and the exact candidate kernel was running.

Stock `rfkill`, `btpower`, `bt_fm_swr`, and `btfmcodec` loaded normally. The Canoe sound card registered, 49 sound nodes appeared, and `android.hardware.audio.effect.IFactory/default` registered. Built-in Rust Binder handled binderfs with no `rust_binder.ko` loaded. Wi-Fi, Bluetooth, LTE voice/data, NFC, five-camera enumeration, fingerprint, USB/ADB, charging, and short suspend/resume passed. Fatal-error and pstore checks were clean.

After this canary passed, only active `boot_b` was flashed. The persistent reboot repeated the critical checks successfully. Read-only block-device read-back of `boot_b` exactly matched candidate SHA-256 `5cbfcbae7e59d2786fbd935cca6c264354a90b7f510f637d11af4f4db9cfe6ee`. Physical qualification result: **PASS for the tested scope**. Extended deep-suspend duration and hands-on camera/audio/call use remain ongoing-use tests rather than blockers found in this session.

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

- Kernel release: `6.12.119-android16-6-o-g7477d64d7643-4k`
- `Image` size: 43,383,296 bytes
- `Image` SHA-256: `324277e6412c161a99378603c5d82030b094900152d3f67eb282f707d9a08181`
- `vmlinux` SHA-256: `5bd163eee359298b5ab73d657b77be23cdcbc3bfaa80313eee896e4670eb6a4b`
- `Module.symvers` SHA-256: `8f67ca352ad38d8b690784be94a1e7f1c89764b3ec158ed802857c19a14662ea`
- `modules.builtin` SHA-256: `4e25d13aab1e57642f2ad969d0f2ed3fb6162457df39e0b28f91a9a72d7e3712`

The effective configuration contains:

- `CONFIG_RUST=y`
- `CONFIG_ANDROID_BINDER_IPC=y`
- `CONFIG_ANDROID_BINDER_IPC_RUST=y`
- `CONFIG_MODVERSIONS=y`
- `CONFIG_GENDWARFKSYMS=y`
- `CONFIG_MODULE_SIG=y`
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
- Overall oracle result: PASS

The vendor_boot copies were also covered through the normal, vendor_boot, and recovery load lists. The stock module images themselves were not changed.

## ABI and KMI checks

| Check | Result |
|---|---|
| Canoe production build | PASS |
| Common KMI symbol allowlist | PASS |
| `--kbuild_symtypes` KMI build | PASS |
| Canoe device-inclusive ABI | PASS |
| Exact stock-module oracle | PASS |
| Common enforced ABI distribution | PASS |

The original reference delta was reviewed, the downstream 6.12.119 ABI definition was advanced with the repository's supported update target, exact equality with the generated ABI was verified, and the enforced distribution comparison was rerun successfully. Overall offline qualification result: **PASS**.

## Boot image validation

The offline-only image is 100,663,296 bytes and has SHA-256 `b484535885af5198dc8b32b5425ca3274436dc358bedd5a612d4ecb5b8865ddf`. It preserves boot header v4, Android 17.0.0 metadata, November 2026 patch metadata, empty ramdisk/cmdline, the stock partition size, and the target AVB public-key identity. AVB verification succeeds offline.

This structural PASS is not evidence of Android boot success.

## Physical status

- Fastboot flash performed: NO
- Temporary `fastboot boot` canary performed: YES
- Candidate kernel entry and ADB: PASS
- Qualcomm ramdump: NOT OBSERVED
- Android boot tested: FAIL
- Encrypted user0 under candidate: NOT REACHED
- Hardware tests performed: NO
- Stock rollback boot: PASS
- Stock encrypted user0 unlock: PASS
- Stock audio-effect factory registration: PASS
- Protected branch or stable release modified: NO
- Development branch pushed: NO

Live preflight confirmed the exact target incremental `63eb77a308`, SPL `2026-11-01`, active slot `b`, and stock running kernel `6.12.81-android16-6-gf4c1a270b7b0-4k`. The candidate was started temporarily and no partition was written.

The 6.12.119 kernel entered and ADB returned, but Android never set `sys.boot_completed` and user 0 remained in `BOOTING`. `audiohalservice.qti` repeatedly aborted because its mandatory `libaudioeffecthal.qti.so` interface could not register. The preceding log identifies the immediate trigger: stub mode was selected and `audio_effects_config_stub.xml` was absent. Init then reported `vendor.audio-hal-aidl` crashing before boot completion.

After reboot, the unchanged stock kernel returned, Android set `sys.boot_completed=1`, user 0 reached `RUNNING_UNLOCKED`, CE availability was `true`, SELinux remained enforcing, and `android.hardware.audio.effect.IFactory/default` was registered. Physical qualification result: **FAIL — DO NOT FLASH**.

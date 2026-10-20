# Built-in Rust Binder physical validation with hybrid system_dlkm

Date: 2026-10-19

Status: **CORE PASS ON HYBRID SYSTEM_DLKM; STRICT STOCK TEST PENDING**

## Scope

The repository owner explicitly authorized flashing the experimental kernel.
Preflight found that active slot A still used the previous hybrid
`system_dlkm`, not the untouched October 14 LineageOS image. The test therefore
changed only `boot_a` and qualifies only that retained hybrid configuration.
No `system_dlkm`, `vendor_dlkm`, `vendor_boot`, `init_boot`, DTBO, VBMeta,
super, metadata, userdata, or slot metadata was written.

## Preflight and rollback

Device identity matched OnePlus 15 / `infiniti` / SM8850 with
`lineage-24.0-20261014-NIGHTLY-infiniti`, build `CP2A.260605.016`, incremental
`5521dfa82f`, active slot `_a`, unlocked bootloader, secure mode enabled, and
93 percent battery.

A fresh 100,663,296-byte host rollback image was read from `boot_a` before the
flash:

```text
/home/travis/Android/kernel-test-backups/builtin-rust-binder-20261019-preflash/boot_a-before.img
SHA-256 c98f46a1fefd2b890d0370d8743d63ef35aabc055d25a90dca4395920bc79226
```

The candidate was also 100,663,296 bytes, passed `avbtool verify_image`, and
had SHA-256
`debbcb02d87474e99402024ab2c9a5e9a4da2e959d13543f57c9705f88631cb4`.
Fastboot confirmed product `canoe`, slot `a`, `unlocked: yes`,
`secure: yes`, a raw `boot_a` partition of `0x6000000` bytes, and a successful,
bootable slot A.

## Flash and exact read-back

The only write command was:

```text
fastboot flash boot_a boot.img
```

Fastboot reported successful send and write operations. Both the first Android
boot and the post-recovery Android boot read back `boot_a` with the candidate's
exact SHA-256. Partition continuity was also confirmed:

| Partition | Live SHA-256 after test | Disposition |
|---|---|---|
| `boot_a` | `debbcb02d87474e99402024ab2c9a5e9a4da2e959d13543f57c9705f88631cb4` | candidate, exact read-back |
| `system_dlkm_a` | `18524c480a07047c09a284e70ed83395afc74921c960993adc75a5d730e5c33e` | previous hybrid, unchanged |
| `vendor_dlkm_a` | `f66672d67544624d513c635846c5e797b47f65e3ddd424f614b9c87a30a19d05` | stock, unchanged |

## Rust Binder result

Android reached `sys.boot_completed=1` on
`6.12.112-android16-6-o-g5a72c263a0d8-4k`. Runtime evidence showed:

- `/sys/module/binder/parameters/impl` returned `rust`;
- `/sys/module/rust_binder` was present;
- `rust_binder` was absent from `/proc/modules` and `lsmod`;
- binderfs was mounted and exposed `binder`, `hwbinder`, and `vndbinder`;
- `servicemanager`, `system_server`, cameraserver, and audioserver remained
  alive;
- 452 Binder services and 436 dumpsys services responded on the first boot;
- Rust Binder transaction diagnostics were emitted by the live driver.

The retained `system_dlkm/modules.load` still requested `rust_binder` at line
50, and a physical `rust_binder.ko` remained present with SHA-256
`0b417fe58b514b8af431a9e76ecb65ea70180b7c356580bff314576fa0b09604`.
Despite that request, no loadable Rust Binder module appeared and no duplicate
registration occurred. The high-volume Android kernel log had already
overwritten the earliest module-loader diagnostic, so the request disposition
is established from the load policy, successful first-stage boot, built-in
selection, and absence from `/proc/modules` rather than that one log line.

## Encryption and recovery

Android user0 reached `RUNNING_UNLOCKED`, CE storage became available, and
`/data` mounted as F2FS with `inlinecrypt`.

TWRP 3.7.1 booted on slot A. Its Lineage decryption runtime progressed through
secure-element, OMAPI, and Binder-service prerequisites to `ready` with
`/dev/nq-nci` present. User0 then reported `User 0 Decrypted Successfully`,
`twrp.user.0.decrypt=1`, and `/data/media/0` was accessible. Rebooting from
recovery returned to Android on the same candidate, and Android user0 unlocked
again.

## Functional checks

| Test | Result | Evidence or boundary |
|---|---|---|
| Android boot | PASS | two boots reached `sys.boot_completed=1` |
| Rust Binder initialization | PASS | `binder.impl=rust`, built-in sysfs object, Rust diagnostics |
| Binder registration/services | PASS | binderfs devices and core services healthy |
| Existing user0 decryption | PASS | Android and TWRP both decrypted user0 |
| F2FS inline encryption | PASS | live `/data` mount included `inlinecrypt` |
| Wi-Fi | PASS | connected, usable, 3/3 internet ping |
| Cellular data | PASS | Wi-Fi disabled; validated LTE default and 3/3 ping; Wi-Fi restored |
| Camera | PASS | five devices enumerated; Aperture launched in 154 ms |
| USB/ADB | PASS | survived Android boots, resume, and recovery cycle |
| Recovery boot/reboot | PASS | TWRP boot, decrypt, and Android return passed |
| Bluetooth | PARTIAL | stack ON and healthy; no peripheral transaction |
| NFC | PARTIAL | stack ON and recovery NCI ready; no tag transaction |
| Audio | PARTIAL | audioserver and routing state healthy; audible playback not observed |
| Fingerprint | PARTIAL | service and sensor healthy; live biometric match not observed |
| Suspend/resume | PARTIAL | doze/wake and ADB resume passed; deep suspend not established over USB |
| Fatal kernel errors | PASS | zero precise fatal signatures and zero pstore files |

The 210-second stability window sampled every 30 seconds. `system_server` and
`servicemanager` PIDs remained unchanged, user0 stayed unlocked, Binder stayed
on Rust, and fatal/pstore counts stayed zero.

## Preserved evidence and remaining gate

First-boot and post-recovery dmesg/logcat captures are stored beside the host
rollback image. They are private test artifacts and are not committed.

This run does not prove compatibility with the untouched stock
`system_dlkm` SHA-256
`3947c061321b6d8358020feba6138533540741f4e2fb6a09abaf81c55630b788`.
That exact partition state, plus the five owner-observed peripheral/deep-sleep
checks above, remains required before the experiment can meet every success
criterion or be promoted as a release.

# Built-in Rust Binder physical validation with stock system_dlkm

Date: 2026-10-19

Status: **CORE PASS ON UNTOUCHED STOCK SYSTEM_DLKM; MANUAL PERIPHERAL AND DEEP-SUSPEND GATES PENDING**

## Scope

The repository owner explicitly authorized restoring the exact untouched
October 14 LineageOS `system_dlkm` and repeating the boot-only candidate test.
The built-in Rust Binder candidate was already installed on active `boot_a`.
The restoration write changed only `system_dlkm_a`; it did not change
`boot_a`, `vendor_dlkm`, `vendor_boot`, `init_boot`, DTBO, VBMeta, super,
metadata, userdata, or slot metadata.

This restoration establishes the intended target baseline. It is not a
replacement `system_dlkm` distributed with the boot-only candidate.

## Preflight, source, and rollback

The connected device matched the required LineageOS build:

```text
Lineage version: 24.0-20261014-NIGHTLY-infiniti
Build ID: CP2A.260605.016
Incremental: 5521dfa82f
Active slot: _a
Encryption: encrypted/file
Battery: 98 percent
```

Before the write, live partition hashes were:

| Partition | SHA-256 | State |
|---|---|---|
| `boot_a` | `debbcb02d87474e99402024ab2c9a5e9a4da2e959d13543f57c9705f88631cb4` | built-in Rust Binder candidate |
| `system_dlkm_a` | `18524c480a07047c09a284e70ed83395afc74921c960993adc75a5d730e5c33e` | previous hybrid |
| `vendor_dlkm_a` | `f66672d67544624d513c635846c5e797b47f65e3ddd424f614b9c87a30a19d05` | untouched stock |

A fresh 8,327,168-byte host rollback image was read from the active hybrid
partition before restoration:

```text
/home/travis/Android/kernel-test-backups/builtin-rust-binder-stock-dlkm-20261019-preflash/system_dlkm_a-hybrid-before.img
SHA-256 18524c480a07047c09a284e70ed83395afc74921c960993adc75a5d730e5c33e
```

The stock source was independently extracted from
`lineage-24.0-20261014-nightly-infiniti-signed.zip`, SHA-256
`59e6795ce0ae554b5b6c54e1343ccf8e8515301f2cd1456cbd01fee1b2b72c0a`.
The exact 8,327,168-byte `system_dlkm.img` had SHA-256
`3947c061321b6d8358020feba6138533540741f4e2fb6a09abaf81c55630b788`.
`avbtool verify_image` validated its embedded public key, footer, and SHA-256
hashtree. Its AVB fingerprint is the required
`OnePlus/lineage_infiniti/infiniti:17/CP2A.260605.016/5521dfa82f:userdebug/release-keys`.

## Restoration and exact read-back

Fastbootd reported `is-userspace: yes`, current slot `a`, and an unlocked
bootloader. The only partition write was:

```text
fastboot flash system_dlkm_a system_dlkm.img
```

Fastbootd resized the logical partition to `0x7f1000`, sent 8,132 KiB, and
reported successful write and reboot operations. The first Android boot,
TWRP recovery, and the post-recovery Android boot all read back the exact
stock hash. Final continuity was:

| Partition | SHA-256 | Result |
|---|---|---|
| `boot_a` | `debbcb02d87474e99402024ab2c9a5e9a4da2e959d13543f57c9705f88631cb4` | candidate unchanged |
| `system_dlkm_a` | `3947c061321b6d8358020feba6138533540741f4e2fb6a09abaf81c55630b788` | exact untouched stock |
| `vendor_dlkm_a` | `f66672d67544624d513c635846c5e797b47f65e3ddd424f614b9c87a30a19d05` | exact untouched stock |

## Built-in Rust Binder and stock modules

Both Android boots and the recovery boot ran
`6.12.112-android16-6-o-g5a72c263a0d8-4k`. Runtime evidence showed:

- `/sys/module/binder/parameters/impl` returned `rust`;
- `/sys/module/rust_binder` was present;
- `rust_binder` was absent from `/proc/modules`;
- binderfs exposed `binder`, `hwbinder`, and `vndbinder`;
- the stock partition exposed all 88 `system_dlkm` modules and stock
  `vendor_dlkm` exposed all 552 modules;
- 556 modules were live in `/proc/modules` after boot;
- no signature, vermagic, MODVERSIONS, missing-symbol, namespace, or module
  load error was found in the kernel log; and
- Binder service manager and core Android services remained healthy.

The untouched `modules.load` still requested `rust_binder` at line 50. The
physical stock module remained present with SHA-256
`411e911830a0633492be96affd2d23b486c9e10242101c4b7e1cba80943f3dac`,
but it never appeared as a loadable module and never double-registered.
The expected one-time loader printk was not retained in the captured ring
buffer. Successful first-stage boot, the exact stock request and file, the
built-in selector, the absence from `/proc/modules`, and zero module errors
jointly establish that the stock request was tolerated without relocation or
module initialization.

The first boot exposed 451 Binder services and 436 dumpsys services. After
the recovery cycle those counts were 456 and 439. `servicemanager`,
`system_server`, `cameraserver`, and `audioserver` stayed live.

## Encryption and recovery

Android user0 moved from `RUNNING_LOCKED` to `RUNNING_UNLOCKED`,
`sys.user.0.ce_available` became `true`, and `/data` mounted as F2FS with
`inlinecrypt`. SELinux remained enforcing.

TWRP 3.7.1 booted on slot A with the candidate kernel. It selected its Lineage
decryption runtime, reached `twrp.decrypt.prereq=ready`, reported
`twrp.user.0.decrypt=1` and `twrp.all.users.decrypted=true`, mounted `/data`
as F2FS with `inlinecrypt`, and exposed 64 top-level entries under
`/data/media/0`. `/dev/nq-nci`, secure-element, and OMAPI prerequisites were
available. Recovery also reported Binder `rust`, no loadable `rust_binder`,
and the exact stock `system_dlkm` hash. Rebooting returned normally to Android,
where user0 and CE storage unlocked again.

## Functional matrix

| Test | Result | Evidence or boundary |
|---|---|---|
| Android boot | PASS | first and post-recovery boots reached `sys.boot_completed=1` |
| Rust Binder initialization | PASS | built-in sysfs object, selector `rust`, Rust Binder diagnostics |
| Binder devices and services | PASS | binderfs devices and hundreds of Binder services healthy |
| Stock module population | PASS | exact image, 88+552 files, zero module compatibility errors |
| Existing user0 decryption | PASS | Android and TWRP both exposed existing CE data |
| F2FS inline encryption | PASS | Android and recovery `/data` mounts included `inlinecrypt` |
| Wi-Fi | PASS | 802.11ax connection and repeated 3/3 Internet ping |
| Cellular data | PASS WITH NOTE | validated Verizon LTE default route; traffic passed with 20-33 percent ICMP loss |
| Camera | PASS | five cameras enumerated; Aperture cold-launched in 92 ms |
| USB/ADB | PASS | survived two Android boots, recovery, screen off/wake, and testing |
| Recovery boot/reboot | PASS | TWRP boot, decryption, stock hash, and Android return passed |
| Bluetooth | PARTIAL | stack on, two bonded devices, and a live headset connect transition; sustained I/O not observed |
| NFC | PARTIAL | stack on and recovery NCI prerequisite ready; no physical tag transaction |
| Audio | PARTIAL | audioserver/audio flinger healthy; audible playback not owner-observed |
| Fingerprint | PARTIAL | sensor/provider healthy with zero HAL deaths; no live finger match |
| Suspend/resume | PARTIAL | screen off/wake passed; forced `mem` suspend was blocked by active USB controller `a600000.dwc3` |
| Fatal kernel errors | PASS | zero fatal signatures, crash-buffer records, or pstore files |

The forced suspend attempt was bounded by a 15-second RTC wake alarm. The
kernel recorded one suspend failure and identified the active USB controller;
the device remained healthy. A USB-disconnected suspend/resume cycle is still
required to qualify deep sleep.

## Stability and qualification boundary

The final 210-second window sampled every 30 seconds. Every sample retained
`sys.boot_completed=1`, `RUNNING_UNLOCKED`, Binder `rust`, `system_server` PID
2881, `servicemanager` PID 984, zero pstore files, zero fatal signatures, and
zero module errors. The stability log SHA-256 is
`c511b0c94d0410d281fde1a0f1a4b67b90a56e7f28a72ad125625a131208b2a9`.

This run closes the untouched-stock-`system_dlkm` core compatibility gate and
proves that no replacement `rust_binder.ko` or custom DLKM partition is
required. It does not authorize publication or stable promotion. Sustained
Bluetooth I/O, an NFC tag transaction, audible playback, a live fingerprint
match, and USB-disconnected deep suspend/resume remain owner-observed gates.

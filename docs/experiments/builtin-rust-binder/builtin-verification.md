# Built-in Rust Binder verification

Status: **STATIC PASS; HYBRID-DLKM CORE PHYSICAL PASS; STOCK-DLKM PHYSICAL TEST PENDING**

This report covers the experimental `builtin-rust-binder` branch based on
`5173f30f4ee16589444d686497196fe0bfd639aa`, the commit named by
`lineage24.0-20261014-linux-6.12.112-kmi6`. It does not qualify a stable
release. When the static report was produced, no device had been connected or
flashed, and the protected `Lineage-24.0` checkout remains unchanged. A later
owner-authorized physical test changed only active `boot_a`; its scoped
results are recorded in `physical-validation-hybrid-system-dlkm.md`.

## Implementation

The effective symbol is `CONFIG_ANDROID_BINDER_IPC_RUST`. The arm64 GKI
configuration changes it from `m` to `y`; x86 remains modular. The existing
in-tree composite Kbuild rule links the Rust and C support objects directly
into `vmlinux`, so no Makefile or Bazel target redesign was necessary. Kleaf's
arm64 module output list no longer expects `rust_binder.ko`.

The C Binder coordination code now defaults `binder_use_rust` to true only
when Rust Binder is built in. The existing `binder.impl=c` override remains
available. During init, C Binder registers first, then the Rust initcall uses
the existing `unload_binder()` handoff and registers Rust Binder's generic
netlink family, shrinker, and binderfs implementation. The userspace Binder
ABI and device names (`binder`, `hwbinder`, and `vndbinder`) are unchanged.

Built-in C and Rust trace events previously collided at link time because
their event names were identical but some payload types differed. Only the
built-in Rust events are therefore namespaced as `rust_binder_*`; the C event
names and exported KMI symbols are unchanged. Rust aliases preserve the
driver's internal call sites. When the C implementation is selected, or the
C-to-Rust handoff fails, the built-in Rust path leaves those dormant namespaced
events registered. It never passes a null built-in `ThisModule` to the
module-only trace-event removal helper.

The exact stock `system_dlkm` still asks for `rust_binder` at line 50 of
`modules.load`. The kernel's module loader now handles only that exact name
when `CONFIG_ANDROID_BINDER_IPC_RUST=y`. It performs the normal signature
check, ELF/section/name validation, and blacklist check, logs that the request
was satisfied by the built-in implementation, and returns success before
vermagic, MODVERSIONS, allocation, relocation, or module init. Every other
module follows the unchanged loading path. Consequently, the old stock module
cannot replace or double-register the built-in driver.

## Effective configuration

The generated configuration proves:

```text
CONFIG_RUST=y
CONFIG_ANDROID_BINDER_IPC=y
CONFIG_ANDROID_BINDERFS=y
CONFIG_ANDROID_BINDER_DEVICES="binder,hwbinder,vndbinder"
CONFIG_ANDROID_BINDER_IPC_RUST=y
CONFIG_MODVERSIONS=y
CONFIG_GENDWARFKSYMS=y
CONFIG_MODULE_SIG=y
CONFIG_MODULE_SIG_ALL=y
# CONFIG_MODULE_SIG_FORCE is not set
CONFIG_SYSTEM_TRUSTED_KEYS="certs/lineage24_0_20261014_gki_module_signing.pem"
CONFIG_BLK_INLINE_ENCRYPTION=y
CONFIG_F2FS_FS=y
CONFIG_FS_ENCRYPTION=y
CONFIG_FS_ENCRYPTION_INLINE_CRYPT=y
```

The effective config is 225,187 bytes with SHA-256
`523855d211c1637e3c1fc3e073685c44b1ee3f8bffcc3129761b3b899731f09f`.

## Link and initialization proof

- `modules.builtin` contains
  `kernel/drivers/android/binder/rust_binder.ko` and has SHA-256
  `c2c1b673e2c55e1ae67f77fe4f09b54b50e9bd61f8c7e62e80fec2f0517c5e84`.
  The `.ko` suffix is kbuild's built-in object record, not a loadable output.
- No `rust_binder.ko` file exists anywhere in the Bazel output tree.
- `vmlinux` contains `__rust_binder_init`, `__rust_binder_exit`,
  `__rust_binder_initcall`, `init_rust_binderfs`, `binder_use_rust`,
  `unload_binder`, and `__tracepoint_rust_binder_transaction_received`.
- `vmlinux` also retains the C KMI symbol
  `__tracepoint_binder_transaction_received`; the two implementations no
  longer collide.
- The final `Image` contains both the Rust Binder strings and the diagnostic
  `module: %s load request satisfied by built-in implementation`.
- `vmlinux` is 403,252,024 bytes with SHA-256
  `95d36baf577b3d5dd987b0aa15b9112c2eef49e1aca9fd17d6635c7d96cf5d1b`.
- `Image` is 42,920,448 bytes with SHA-256
  `ce31794b7349818a1a697f7901aae570839de3592b32dd078c9c1ab0b1c677ab`.

The embedded release string is
`6.12.112-android16-6-o-g5a72c263a0d8-4k`. The final source correction was
present during every final build and gate, then committed unchanged as
`e1d6a63bbd6bf202676e759376a539713b1b4730`. The exact patch from the embedded
SCM commit to that source commit has SHA-256
`af2488a3ca99b6e2defff205b57a4d5620ed3b8fc030113943eaedda8b553606`.
Thus the code content is committed and reproducible, while the diagnostic
release string transparently records that the commit object was created after
the qualified build.

## Mandatory build and ABI gates

| Gate | Result | Evidence |
|---|---|---|
| Infiniti `//soc-repo:canoe_perf_dist` | PASS | 552 executed actions, 734 cache hits, 5,506.490 s |
| Enforced `//common:kernel_aarch64_abi_dist` | PASS | all five ABI reports are zero bytes |
| Strict `//common:kernel_aarch64_abi_kmi_symbol_checks` | PASS | strict-mode marker generated |
| Infiniti `//soc-repo:canoe_perf_abi` | PASS | ABI extraction completed, 4,359 total actions |
| `git diff --check` | PASS | no whitespace errors |

No ABI reference, KMI symbol list, security option, or signature policy was
weakened. Final `Module.symvers` is 654,855 bytes with SHA-256
`2830bdd92e2683278d7f10407e425cf23baaf6bfd757f71c04288fdd6b5c5777`.

## Exact stock module compatibility

The audited source is the locally verified full
`lineage-24.0-20261014-nightly-infiniti-signed.zip`, SHA-256
`59e6795ce0ae554b5b6c54e1343ccf8e8515301f2cd1456cbd01fee1b2b72c0a`.
The untouched population contains 88 `system_dlkm` and 552 `vendor_dlkm`
modules.

The deliberately raw audit reports one blocker: the physical stock
`rust_binder.ko`, which has 105 imports absent from the built-in candidate and
must not be relocated. The effective audit applies the kernel's exact
`BUILTIN_SATISFIED` disposition to that one module and reports:

```text
compatible=442
dormant=197
blocker=0
resolved=36429
missing=0
crc_matches=37068
crc_mismatches=0
namespace_failures=0
result=PASS
```

All 87 remaining `system_dlkm` modules and all 355 modules in the stock
`vendor_dlkm` load list are compatible. The other 197 stock vendor modules are
dormant under the stock load policy. Signature policy is unchanged: 109 stock
modules carry the trusted Lineage certificate and 531 vendor modules are the
same unsigned retained binaries accepted by the baseline configuration. The
trusted certificate SHA-256 fingerprint is
`6C:FF:7A:C4:3E:68:C0:12:88:72:20:2D:B4:35:54:37:9F:9F:0B:F3:A6:42:81:FF:6A:F0:26:F6:01:5D:8B:D8`.

The stock vendor ramdisk contains 381 modules with 381 unique hashes; every
hash is an exact copy of a module in the audited stock DLKM population. Its
122-entry normal load list and 381-entry recovery load list both resolve with
zero missing files. No boot-critical module is removed and no replacement
`system_dlkm`, `vendor_dlkm`, `vendor_boot`, or `init_boot` is required.

## Boot-container validation

The candidate was built with the repository-pinned `mkbootimg.py` and
`avbtool 1.3.0`. Repacking the reference stable kernel with these exact inputs
reproduced the stable boot image byte-for-byte before the candidate was made.

The candidate preserves boot header v4, OS version 17.0.0, OS patch level
2026-10, empty ramdisk, empty command line, 100,663,296-byte partition size,
SHA256_RSA4096, public-key SHA-1
`2597c218aae470a130f61162feaae70afd97f011`, rollback index 1790812800,
location 0, flags 0, the original salt, and all three AVB properties. Only the
kernel-dependent raw image size, hash descriptor digest, signature, and kernel
payload changed.

`avbtool verify_image` passes. Re-unpacking the candidate produces a zero-byte
ramdisk and a kernel byte-identical to the qualified `Image`. The final
`boot.img` is 100,663,296 bytes with SHA-256
`debbcb02d87474e99402024ab2c9a5e9a4da2e959d13543f57c9705f88631cb4`.

## Physical evidence and qualification boundary

The exact candidate was subsequently flashed only to active `boot_a`. Android
boot, built-in Rust Binder selection, Binder devices and services, Android and
TWRP user0 decryption, F2FS inline encryption, Wi-Fi, LTE data, camera launch,
USB/ADB, recovery reboot, exact boot read-back, and a 210-second stability
window passed. No loadable `rust_binder` appeared and no fatal kernel event or
pstore record was found.

That run retained the previous hybrid `system_dlkm` with SHA-256
`18524c480a07047c09a284e70ed83395afc74921c960993adc75a5d730e5c33e`,
not the untouched stock image. It proves the built-in driver and redundant
module-request behavior on the hybrid population, but it does not complete the
experiment's strict stock-DLKM success criterion. Bluetooth peripheral I/O,
an NFC tag transaction, audible playback, a live fingerprint match, and deep
suspend also require owner-observed testing. No publication or stable
promotion is authorized.

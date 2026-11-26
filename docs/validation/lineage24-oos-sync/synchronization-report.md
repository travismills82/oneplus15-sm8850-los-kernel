# LineageOS 24 / OxygenOS kernel synchronization report

Date: 2026-11-26

Status: **EXPERIMENTAL — REPAIRED CANDIDATE PHYSICALLY BOOTED AND INSTALLED**

## References

- Protected LineageOS branch: `Lineage-24.0`
- Protected LineageOS revision: `f0a7e4961c02044f5f5394cdbaec320256168ce5`
- Development branch: `development/lineage24-oos-kernel-sync`
- Development revision: `46d53f13f126826b2e22f95017e6c86dce1277b4`
- OxygenOS source reference: `oos/main` at `6cea96b68c5d7d968e7fc641448b518cbf863460`
- Exact target OTA: `lineage-24.0-20261125-nightly-infiniti-signed.zip`
- OTA SHA-256: `930b94f9e7e1b02d272b52b5c09f0ecda621dda0268a99aae845e87ffe4943ae`

The protected branch, stable release tag, rollback images, and OxygenOS repository were not modified. Nothing was pushed or published.

## Synchronization scope

The development tree advances the common kernel from Linux 6.12.112 to Linux 6.12.119 while retaining the OnePlus 15 Canoe target and LineageOS-specific integration. It contains 5,579 commits beyond the protected LineageOS revision: the synchronized common/security history through 6.12.119 plus local integration and validation commits.

The aggregate source delta is 4,422 files, 153,521 insertions, and 38,136 deletions. This is an upstream/common history synchronization, not a wholesale replacement of LineageOS vendor drivers or device trees with OxygenOS firmware-specific implementations.

Notable retained security fixes include:

- `a49c37839fd1`: CVE-2026-99652, `mremap()` / `UFFDIO_MOVE` fix.
- `5208a3794300`: CVE-2026-99664, GUP PUD recheck fix.
- `2fd68321adbe`: CVE-2026-99665, khugepaged dirty-bit fix.

The complete stable/common series through 6.12.119 supplies the remaining upstream fixes; the original commit authorship and provenance are retained in Git history.

## LineageOS-specific retention and adaptation

- Rust Binder remains built into `vmlinux` with `CONFIG_ANDROID_BINDER_IPC_RUST=y`.
- The stock `rust_binder.ko` can remain physically present in the untouched `system_dlkm`; the module-load contract is satisfied by the built-in implementation and no replacement DLKM is required.
- The exact November 25 Lineage GKI module certificate is configured for the target nightly.
- `CONFIG_MODVERSIONS=y`, `CONFIG_GENDWARFKSYMS=y`, and `CONFIG_MODULE_SIG=y` remain enabled.
- FBE/F2FS inline encryption and the existing Qualcomm/Oplus configuration remain enabled.
- Two exports required by retained Qualcomm modules were added without altering their implementation: `__mm_reset_vma_seqcounts` and `shmem_file`.

OxygenOS KernelSU/SUSFS changes were deliberately excluded after review. The development kernel does not enable duplicate or unqualified root hooks. No broad Qualcomm module-to-built-in conversion was attempted; only the previously validated Rust Binder conversion is retained.

## Build result

- Kernel release: `6.12.119-android16-6-o-g46d53f13f126-4k`
- Canoe production distribution: PASS
- Rust linking: PASS
- Device-inclusive Canoe ABI target: PASS
- Common strict KMI symbol check: PASS
- `--kbuild_symtypes` build and KMI check: PASS
- Exact 640-module symbol/CRC/namespace oracle: PASS
- Exact 109-module signature verification: PASS
- Protected-export contract: PASS
- Common enforced ABI distribution comparison: PASS

The original 6.12.112-reference failure is preserved under `out/lineage24-oos-sync/common_abi_dist/abi_stgdiff/`. It includes three added exported functions, changed exported function types, 40 CRC-only changes, and type-layout changes. The exact stock-module oracle proved that the audited LineageOS module population has no missing imports, CRC mismatches, or namespace failures.

The Android common `android16-6.12-lts` branch was then checked directly. Its head was Linux 6.12.119 and carried an updated upstream ABI definition. Because the Lineage/OxygenOS tree has a downstream Qualcomm symbol surface, the upstream file could not be copied verbatim. The repository's supported `//common:kernel_aarch64_abi_update` target advanced the downstream reference to the reviewed 6.12.119 contract. The refreshed reference exactly matches the generated ABI (`stgdiff` exit 0), and the enforced ABI distribution target subsequently passed. Enforcement was not disabled or suppressed.

## Packaging result

A structurally valid repaired boot-only image was generated under `out/lineage24-kernel-sync-repaired-test/`. It preserves the target LineageOS boot header, metadata, empty ramdisk, partition size, AVB 1.4.0 release string, rollback index, salt, properties, and key identity. Its SHA-256 is `5cbfcbae7e59d2786fbd935cca6c264354a90b7f510f637d11af4f4db9cfe6ee`.

No `system_dlkm`, `vendor_dlkm`, `vendor_boot`, `init_boot`, `dtbo`, or `vbmeta` image is a release dependency.

## Physical canary result

Live preflight confirmed the exact OTA incremental, slot `b`, stock kernel, encryption state, SELinux enforcing state, and rollback artifact. The repaired candidate was first started with `fastboot boot`; no partition was written during that canary.

The repaired candidate entered, ADB returned, and the running release was confirmed as `6.12.119-android16-6-o-g46d53f13f126-4k`. Android completed boot and user0/FBE/CE unlocked. The exact stock `rfkill`, `btpower`, `bt_fm_swr`, and `btfmcodec` chain loaded, the Canoe sound card and audio-effect factory registered, and Rust Binder remained built in. Wi-Fi, Bluetooth, LTE, NFC, camera enumeration, fingerprint, USB/ADB, charging, and short suspend/resume checks passed without a fatal kernel error or pstore record.

After the temporary canary passed, the owner-authorized persistent operation wrote only active `boot_b`. The persistent reboot repeated Android boot, FBE/CE, module/audio, hardware-service, and suspend/resume checks successfully. Read-only `boot_b` block-device hashing exactly matched the candidate image.

## Decision

The original failed image remains quarantined. Commit `46d53f13f126` installs the exact public certificate extracted from the November 25 stock kernel and points `CONFIG_SYSTEM_TRUSTED_KEYS` to it; enforcement remains enabled. Production, ABI/KMI, exact stock-module, packaging, temporary-canary, and persistent-boot qualification all passed for the tested scope. No branch was pushed and no stable release or tag was modified.

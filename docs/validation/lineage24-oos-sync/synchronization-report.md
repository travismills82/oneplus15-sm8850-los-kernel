# LineageOS 24 / OxygenOS kernel synchronization report

Date: 2026-11-26

Status: **EXPERIMENTAL — OFFLINE VALIDATION BLOCKED — DO NOT FLASH**

## References

- Protected LineageOS branch: `Lineage-24.0`
- Protected LineageOS revision: `f0a7e4961c02044f5f5394cdbaec320256168ce5`
- Development branch: `development/lineage24-oos-kernel-sync`
- Development revision before this report: `7477d64d76435bb184ea63f45172d99766f04a91`
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
- The trusted LineageOS GKI module certificate remains configured.
- `CONFIG_MODVERSIONS=y`, `CONFIG_GENDWARFKSYMS=y`, and `CONFIG_MODULE_SIG=y` remain enabled.
- FBE/F2FS inline encryption and the existing Qualcomm/Oplus configuration remain enabled.
- Two exports required by retained Qualcomm modules were added without altering their implementation: `__mm_reset_vma_seqcounts` and `shmem_file`.

OxygenOS KernelSU/SUSFS changes were deliberately excluded after review. The development kernel does not enable duplicate or unqualified root hooks. No broad Qualcomm module-to-built-in conversion was attempted; only the previously validated Rust Binder conversion is retained.

## Build result

- Kernel release: `6.12.119-android16-6-o-g7477d64d7643-4k`
- Canoe production distribution: PASS
- Rust linking: PASS
- Device-inclusive Canoe ABI target: PASS
- Common strict KMI symbol check: PASS
- `--kbuild_symtypes` build and KMI check: PASS
- Exact 640-module stock compatibility oracle: PASS
- Common enforced ABI distribution comparison: **FAIL (exit 4)**

The full failure is preserved under `out/lineage24-oos-sync/common_abi_dist/abi_stgdiff/`. It includes three added exported functions, changed exported function types, 40 CRC-only changes, and type-layout changes. Updating or accepting the common ABI reference solely to make this result green would bypass the required validation policy.

## Packaging result

A structurally valid boot-only image was generated for offline inspection. It preserves the target LineageOS boot header, metadata, empty ramdisk, partition size, and AVB key identity. It is quarantined under `out/lineage24-kernel-sync-test/` and is explicitly blocked from flashing because the mandatory common ABI comparison failed.

No `system_dlkm`, `vendor_dlkm`, `vendor_boot`, `init_boot`, `dtbo`, or `vbmeta` image is a release dependency.

## Decision

The synchronization is not complete enough for physical testing. The installed-module contract is clean, but the mandatory common ABI gate remains red. The highest-value next step is to reconcile the 6.12.119 Android common ABI delta against an authoritative generation-6 reference without reverting security fixes or weakening enforcement. Only after that gate passes should a fresh boot-only candidate be packaged and subjected to fastboot preflight and physical testing.

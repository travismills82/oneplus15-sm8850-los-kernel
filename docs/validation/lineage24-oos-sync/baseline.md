# LineageOS 24 OxygenOS-kernel synchronization baseline

Date: 2026-11-25

Status: **DEVELOPMENT BASELINE — NO DEVICE WRITE AUTHORIZED**

## Source references

| Role | Reference |
|---|---|
| Protected Lineage branch | `Lineage-24.0` at `f0a7e4961c02044f5f5394cdbaec320256168ce5` |
| Development branch | `development/lineage24-oos-kernel-sync` |
| OxygenOS/ColorOS source | `main` at `6cea96b68c5d7d968e7fc641448b518cbf863460` |
| Shared ancestry | `3b4aea7fd69140c5ab5a9ffabc01433d8785340f` |
| Lineage source version | Linux 6.12.112, Android 16 KMI6 |
| OxygenOS source version | Linux 6.12.119, Android 16 KMI6 |

The protected Lineage checkout was clean before the isolated worktree was
created. The OxygenOS checkout contained extensive pre-existing staged,
unstaged, and untracked work; it was not modified. Comparison and imports use
the fetched immutable `oos/main` ref rather than that dirty checkout.

## Qualified Lineage rollback references

The published October 14 Lineage release remains unchanged at tag
`lineage24.0-20261014-linux-6.12.112-kmi6`. Its published boot image SHA-256 is
`c98f46a1fefd2b890d0370d8743d63ef35aabc055d25a90dca4395920bc79226`.

The later built-in Rust Binder boot-only qualification is represented by the
current protected source and its validation records. Its physically tested
boot read-back SHA-256 is
`debbcb02d87474e99402024ab2c9a5e9a4da2e959d13543f57c9705f88631cb4`.
That image is not substituted for the current nightly's stock rollback.

## Exact current stock target

The current local signed OTA is:

```text
/home/travis/Downloads/los/lineage-24.0-20261125-nightly-infiniti-signed.zip
SHA-256: 930b94f9e7e1b02d272b52b5c09f0ecda621dda0268a99aae845e87ffe4943ae
```

OTA metadata:

```text
post-build=OnePlus/CPH2745IN/OP611FL1:17/CP2A.260605.016/B.R4T3.50a3663-29f0eba-29fce1c:user/release-keys
post-build-incremental=63eb77a308
post-security-patch-level=2026-11-01
post-timestamp=1795607757
pre-device=OP60FFL1,OP611FL1
```

The full OTA payload was extracted with verified
`payload-dumper-go` 2.1.0. The stock images are:

| Image | Size | SHA-256 |
|---|---:|---|
| `boot.img` | 100,663,296 | `f7ee42343ee769df2ca1fe39e126dd9249b7b076de8258744ddcdce95a0f9611` |
| `system_dlkm.img` | 8,327,168 | `aaf0f22d1cc88de30224551d6d24ee6291b223069fdd46b1508ef77489253a61` |
| `vendor_dlkm.img` | 60,395,520 | `db08a3fd2d3a8f06bfdf8a3c68148ca095db0bdc6cc566bc1e3162dba9c52603` |
| `vendor_boot.img` | 100,663,296 | `878ea1faa368d41ff3d2b6e708b3f8fbe4859b94fc83c21a96aebcdc0fb8cfcb` |
| `dtbo.img` | 25,165,824 | `7bf984c12dd5171b832145c1f0801c2882b2527e518ac5c2f72144fb76e0ae10` |
| `init_boot.img` | 8,388,608 | `c61c9a93ca31af434b8111979f1d4ff66dad4b88250d3beb76605ac661d2edd0` |
| `vbmeta.img` | 12,288 | `f2167c358cc2033d925cfa65357773f5fb8efb274935507f740bea2e7e85c94f` |

The OTA `boot.img` embeds
`6.12.81-android16-6-gf4c1a270b7b0-4k`. The extracted EROFS filesystems pass
integrity extraction and contain 88 stock `system_dlkm` modules and 552 stock
`vendor_dlkm` modules. Their bytes are the mandatory retained module contract
for this synchronization project.

## Payload and safety contract

The candidate is boot.img-only. The stock `system_dlkm`, `vendor_dlkm`,
`vendor_boot`, `init_boot`, DTBO, VBMeta, and other partitions are immutable
inputs, not release outputs. Built-in Rust Binder and its exact stock-module
load-request handling must remain intact. No build, offline validation result,
or source equivalence will be described as a physical Android boot result.

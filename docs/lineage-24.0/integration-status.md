# LineageOS 24 SM8850 integration status

Status: **physically tested for the exact LineageOS 24.0 `20261014` payload**

This branch adapts the qualified custom Linux 6.12.112 common kernel to the
OnePlus 15 (`infiniti`) platform sources used by LineageOS 24. It intentionally
uses the matched LineageOS SoC, device-tree, and Qualcomm/Oplus module stack
rather than mixing the older OxygenOS `.601` driver population with LineageOS
firmware.

## Source identity

| Item | Revision |
|---|---|
| Working branch | `Lineage-24.0` |
| Starting custom-kernel commit | `3b4aea7fd69140c5ab5a9ffabc01433d8785340f` |
| Physically tested build parent | `499f2bb26e859260665a81d195e5fe4c1c81d8d7` |
| Content-equivalent committed source | `efa73b7de1eba4441a6f49a1eee188d96bba8af0` |
| Candidate kernel release | `6.12.112-android16-6-o-g499f2bb26e85-4k` |
| Tested LineageOS build | `lineage-24.0-20261014-NIGHTLY-infiniti` (`CP2A.260605.016` / `5521dfa82f`) |
| LineageOS SM8850 kernel snapshot | `b41ca28f591b992d4a6141c14f253877a6f2420a` |
| LineageOS SM8850 device-tree snapshot | `1ed1e65426ed1f80640a0f479cf7e6c7fcb47401` |
| LineageOS SM8850 module snapshot | `08b3042484e2cfc03fbd9ccb5073d55d561c0a79` |
| LineageOS common-device snapshot | `7a13971c7d443f82c64411acbd7e2f6915c1f345` |
| LineageOS `infiniti` device snapshot | `9a408e2a62b7e95aeca69db9696028a8e189d3af` |
| LineageOS ACK pin | `8a69376da734aa00bb02cd1155489c74454e4487` (`android16-6.12-2026-06_r3`) |

The LineageOS ACK pin identifies a Linux 6.12.81 common tree. This integration
keeps the project's newer 6.12.112 common/security history and adapts the
LineageOS driver stack to it. It does not downgrade the common kernel to
6.12.81.

## Qualcomm/CodeLinaro driver provenance

The LineageOS module snapshot includes the following reviewed CodeLinaro merge
points. The `Upstream SHA` column is the second parent of the corresponding
LineageOS merge commit.

| Subsystem | CodeLinaro tag | Lineage merge | Upstream SHA | Source |
|---|---|---|---|---|
| WLAN qcacld-3.0 | `WLAN.LA.2.0.r3-10800-kaanapali.0` | `f2ecb6a09ea5` | `11a03259c48f` | `vendor/qcom-opensource/wlan/qcacld-3.0` |
| WLAN host common | `WLAN.LA.2.0.r3-10800-kaanapali.0` | `877ff97bde73` | `76a485ff8e75` | `vendor/qcom-opensource/wlan/qca-wifi-host-cmn` |
| WLAN platform | `WLAN.LA.2.0.r3-10800-kaanapali.0` | `e44d99608764` | `2a3eaaee9851` | `vendor/qcom-opensource/wlan/platform` |
| WLAN firmware API | `WLAN.LA.2.0.r3-10800-kaanapali.0` | `361cf372392a` | `94dd04008819` | `vendor/qcom-opensource/wlan/fw-api` |
| Video | `VIDEO_HANDSET.LA.1.0.r1-12600-kaanapali.0` | `6dc580257f64` | `359c5e3e7f7f` | `vendor/opensource/video-driver` |
| Touch | `LA.VENDOR.16.2.0.r1-21300-kaanapali.0` | `962f98cf6915` | `3641cb5355cf` | `vendor/opensource/touch-drivers` |
| SPU | `LA.VENDOR.16.2.0.r1-21300-kaanapali.0` | `ec199e930062` | `e933e229773b` | `vendor/qcom/opensource/spu-kernel` |
| SecureMSM | `LA.VENDOR.16.2.0.r1-21300-kaanapali.0` | `d965579c45bb` | `a6e915fd7fed` | `vendor/qcom/opensource/securemsm-kernel` |
| Multimedia support | `DISPLAY.LA.6.0.r1-17600-kaanapali.0` | `497c06141cd4` | `81b311f44c80` | `vendor/opensource/mm-drivers` |
| Graphics/KGSL | `GRAPHICS.LA.16.0.r1-10300-kaanapali.0` | `c6d2ccc11227` | `adf5712becd7` | `vendor/qcom/opensource/graphics-kernel` |
| DSP | `LA.VENDOR.16.2.0.r1-21300-kaanapali.0` | `867912107474` | `79229a856d0d` | `vendor/qcom/opensource/dsp-kernel` |
| Display | `DISPLAY.LA.6.0.r1-17600-kaanapali.0` | `4de1b96bb018` | `8ca3facf3067` | `vendor/opensource/display-drivers` |
| RMNET extensions | `LA.VENDOR.16.2.0.r1-21300-kaanapali.0` | `b159324c5656` | `79a55071da75` | `vendor/qcom/opensource/datarmnet-ext` |
| RMNET core | `LA.VENDOR.16.2.0.r1-21300-kaanapali.0` | `c1bf65066ea7` | `b806f57ffb6c` | `vendor/qcom/opensource/datarmnet` |
| IPA | `LA.VENDOR.16.2.0.r1-21300-kaanapali.0` | `8923c654d4b2` | `aef53e42f69d` | `vendor/opensource/dataipa` |
| Camera | `CAMERA.LA.6.0.r1-15200-kaanapali.0` | `89f5857d181e` | `17a4a67c32d1` | `vendor/opensource/camera-kernel` |
| Audio | `AUDIO_HANDSET.LA.11.0.r1-12400-kaanapali.0` | `e1fd37037c99` | `7b7bb6ace8df` | `vendor/qcom/opensource/audio-kernel-ar` |

The common CodeLinaro host prefix for the table is
`https://git.codelinaro.org/clo/la/platform/`. LineageOS-specific Oplus
integration and device fixes after these merges are also present in the exact
module snapshot.

No newer CodeLinaro tag was substituted merely because it exists. The matched
LineageOS 24 revisions are the compatibility baseline for the first physical
candidate.

## Local compatibility commits

| Commit | Purpose |
|---|---|
| `3da8cfe4003a` | Backport Kleaf DDK UAPI strip-prefix support required by the Lineage source layout. |
| `31144974f42d` | Import the exact LineageOS 24 SM8850 device-tree snapshot. |
| `f2db619b525f` | Import the exact LineageOS 24 Canoe SoC/platform snapshot. |
| `05a509fe0b94` | Import the exact LineageOS 24 SM8850 Qualcomm/Oplus module snapshot. |
| `6ddb667b40ae` | Adapt standalone Lineage repository labels/symlinks to this monorepo without changing driver behavior. |
| `1c8e158469fc` | Extend the existing qcacld monitor-channel implementation to the Linux 6.12.101+ cfg80211 callback prototype. |
| `ce4de3b9cea1` | Exclude duplicate GKI zram providers from Canoe ABI extraction while leaving production module packaging unchanged. |
| `499f2bb26e85` | Record the initial LineageOS 24 source and static integration evidence. |
| `efa73b7de1eb` | Trust the public GKI module-signing certificate used by the exact LineageOS 24 `20261014` module set. |

The cfg80211 adaptation corresponds to stable commit `d6aef302c418`
(upstream `9c4f83092775`), which added `struct net_device *` to
`cfg80211_ops::set_monitor_channel`. The imported driver already contained the
correct three-argument implementation for newer kernels; only its version gate
needed extending to this 6.12.112 tree.

## Static validation

The following gates completed successfully with the physically tested source
content (build parent `499f2bb26e85` plus the trust-anchor change committed as
`efa73b7de1eb`):

```sh
cd kernel_platform

tools/bazel build \
  --//soc-repo:dtbo_config=//vendor/oneplus/sm8850-devicetrees:infiniti_dtbo_config \
  //soc-repo:canoe_perf_dist

tools/bazel run //common:kernel_aarch64_abi_dist -- \
  --destdir=/home/travis/Android/stock_kernel/out/lineage-24.0/artifacts/common_abi_dist_final \
  --wipe_destdir

tools/bazel build //common:kernel_aarch64_abi_kmi_symbol_checks

tools/bazel build \
  --//soc-repo:dtbo_config=//vendor/oneplus/sm8850-devicetrees:infiniti_dtbo_config \
  //soc-repo:canoe_perf_abi
```

| Gate | Result |
|---|---|
| Production Canoe distribution | PASS |
| Strict common KMI symbol-list check | PASS |
| Enforced common/GKI ABI comparison | PASS |
| Canoe device-module ABI generation | PASS |
| `depmod` during production packaging | PASS |
| Production-realistic Lineage module oracle | PASS: 640/640 classified, 0 blockers |
| Physical boot/runtime | PASS |
| Boot partition write/read-back | PASS, byte-identical |

Non-fatal build warnings remain in the imported source, including duplicate DT
macro definitions, deprecated QSEECom interfaces, deprecated
`VENDOR_BOOTCONFIG`, and pre-existing RMNET Kconfig type warnings. No compiler,
linker, modpost, dependency, packaging, common ABI, or Canoe ABI failure
remained.

The generated configuration has `CONFIG_MODVERSIONS=y`,
`CONFIG_GENDWARFKSYMS=y`, and `CONFIG_MODULE_SIG=y`. It embeds the exact public
LineageOS `20261014` GKI module-signing certificate rather than weakening
signature or protected-symbol validation. This corrected the splash-screen
failure caused by rejecting the stock signed module population.

## Effective configuration highlights

The Qualcomm/Oplus providers remain modules, matching the LineageOS modular
architecture:

```text
CONFIG_BT=m
CONFIG_BT_HIDP=m
CONFIG_PPP=m
CONFIG_RFKILL=m
CONFIG_SLHC=m
CONFIG_QCOM_SCM=m
CONFIG_MODVERSIONS=y
CONFIG_GENDWARFKSYMS=y
CONFIG_MODULE_SIG=y
CONFIG_SYSTEM_TRUSTED_KEYS="certs/lineage24_0_20261014_gki_module_signing.pem"
# CONFIG_MODULE_SIG_FORCE is not set
# CONFIG_NTFS3_FS is not set
```

Storage and encryption support remains enabled:

```text
CONFIG_F2FS_FS=y
CONFIG_F2FS_FS_SECURITY=y
CONFIG_F2FS_FS_COMPRESSION=y
CONFIG_FS_ENCRYPTION=y
CONFIG_FS_ENCRYPTION_INLINE_CRYPT=y
CONFIG_BLK_INLINE_ENCRYPTION=y
CONFIG_BLK_INLINE_ENCRYPTION_FALLBACK=y
CONFIG_DM_CRYPT=y
CONFIG_DM_DEFAULT_KEY=y
CONFIG_SCSI_UFSHCD=y
CONFIG_SCSI_UFS_CRYPTO=y
```

## Physically tested artifacts

| Artifact | Size (bytes) | SHA-256 |
|---|---:|---|
| Embedded `Image` | 42,580,480 | `7a04fc65e73dc52fd6b1938299192fc98a516b207b127ee7c8422cfb9d0972a4` |
| `boot.img` | 100,663,296 | `c98f46a1fefd2b890d0370d8743d63ef35aabc055d25a90dca4395920bc79226` |
| hybrid `system_dlkm.img` | 8,327,168 | `18524c480a07047c09a284e70ed83395afc74921c960993adc75a5d730e5c33e` |
| rebuilt `rust_binder.ko` | 837,001 | `0b417fe58b514b8af431a9e76ecb65ea70180b7c356580bff314576fa0b09604` |
| effective `.config` | 266,432 | `b33b65841a205b5e4bbbdb2675535835e5ca2798edead4d33507bd258d4313c6` |
| common `Module.symvers` | 664,314 | `a1665917c5579d1c59f3d91197e8ff22188404163ef28e2a046a9c998b2366d4` |

The production-realistic population contains 640 modules: 88 in the hybrid
system image and 552 untouched stock vendor modules. The oracle resolved all
36,671 hard ELF imports and matched all 37,313 version records with zero
missing providers, CRC mismatches, namespace failures, or blockers.

## Physical qualification and payload boundary

The exact two-image payload passed boot, encrypted user0, F2FS inline crypto,
Rust Binder, Wi-Fi, Bluetooth, LTE data, NFC, recovery reboot, and fatal
kernel/module scans on a CPH2749 running the exact `20261014` LineageOS build.
The boot read-back matched the candidate byte-for-byte. The EROFS system image
mounted under dm-verity and its module population loaded successfully.

The release requires the matched active-slot `boot` and `system_dlkm` images.
It deliberately does not publish or replace generic Canoe `vendor_dlkm`,
`vendor_boot`, `init_boot`, DTBO, VBMeta, or super images. A different Lineage
build is outside this qualification contract.

Full device evidence and the tested rollback hashes are recorded in
[the physical validation report](../validation/lineage-24.0/oneplus15-lineage24.0-20261014-linux-6.12.112.md).

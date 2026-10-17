# LineageOS 24 SM8850 integration status

Status: **static candidate; physical-device qualification not yet performed**

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
| Candidate source commit | `ce4de3b9cea1f8bb805d08be84b702d442e8ae31` |
| Candidate kernel release | `6.12.112-android16-6-o-gce4de3b9cea1-4k` |
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

The cfg80211 adaptation corresponds to stable commit `d6aef302c418`
(upstream `9c4f83092775`), which added `struct net_device *` to
`cfg80211_ops::set_monitor_channel`. The imported driver already contained the
correct three-argument implementation for newer kernels; only its version gate
needed extending to this 6.12.112 tree.

## Static validation

The following commands completed successfully at source commit
`ce4de3b9cea1f8bb805d08be84b702d442e8ae31`:

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
| Module vermagic consistency | PASS: 640/640 use the candidate release |
| Physical boot/runtime | **NOT TESTED** |
| Installed LineageOS module/partition oracle | **NOT YET CAPTURED** |

Non-fatal build warnings remain in the imported source, including duplicate DT
macro definitions, deprecated QSEECom interfaces, deprecated
`VENDOR_BOOTCONFIG`, and pre-existing RMNET Kconfig type warnings. No compiler,
linker, modpost, dependency, packaging, common ABI, or Canoe ABI failure
remained.

The generated configuration has `CONFIG_MODVERSIONS=y`,
`CONFIG_GENDWARFKSYMS=y`, and `CONFIG_MODULE_SIG=y`. The Lineage configuration
does not force signatures; 109 GKI modules are build-key SHA-256 signed and 531
DDK modules are unsigned. This matches the generated Lineage-oriented target,
but it must be compared with the exact installed ROM before flashing.

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

## Candidate artifacts

Artifact directory:

`/home/travis/Android/stock_kernel/out/lineage-24.0/artifacts/canoe_perf_dist_final`

| Artifact | Size (bytes) | SHA-256 |
|---|---:|---|
| `Image` | 42,580,480 | `1c1857917cadf2eab7a72b7bc815c3960e5a20cbabe062bdca610f69732c7329` |
| `boot.img` | 100,663,296 | `58561f1e06f8fb9c975bf64558154663d44c70991397e4188f14f57c457e10ff` |
| `dtb.img` | 6,588,449 | `5dde1b4a623c16676f0297a0cb6400765e2f669a35f14690d8d78a6f394a8ec1` |
| `dtbo.img` | 10,367,364 | `b5e80a8b4ef447699df1ed7687a4c7670f5f7c3982e9448427b8920f6cfd9d74` |
| `vendor_boot.img` | 38,273,024 | `cb5d4e956eaa3838cdabd17c51e7baec0570939f41b6b8e28d6191f5b5b2701c` |
| `vendor_dlkm.img` | 195,473,408 | `fd923791b1344390618dda0cfe59192cfbe1afb4a90ce715e7a42f5e71f03d7d` |
| `system_dlkm.erofs.img` | 102,907,904 | `e81b0e76ac9507d3116e1a3f8389ab376cf7b0e4eacfe0f29a61b80be5e84f07` |
| `super.img` | 292,798,728 | `e29944b1082448fe8c78efcba800d28da17ca892f08d54d0e428c43651c32c96` |
| effective `.config` | 266,432 | `617c28ca53b2721c4823a3055015356970be9e21a9333e6c2d5460222e6d9f14` |
| common `Module.symvers` | 664,314 | `a1665917c5579d1c59f3d91197e8ff22188404163ef28e2a046a9c998b2366d4` |

The distribution contains 640 modules. Its combined `modules.dep` has 640
entries; the generated generic load list has 134 entries, the system list has
88 entries, and the vendor list has 205 entries.

## Payload boundary and next qualification step

The successful build proves that the matched Lineage/CodeLinaro driver stack
compiles and passes the available ABI gates against the 6.12.112 common kernel.
It does **not** yet prove that the generic Kleaf `boot.img`, `vendor_boot.img`,
or DLKM images are byte-compatible with the currently installed LineageOS 24
build.

Before a physical flash, capture from the installed phone:

1. LineageOS fingerprint, build ID, security patch, slot, and running kernel.
2. Exact active `boot`, `init_boot`, `vendor_boot`, `dtbo`, `system_dlkm`, and
   `vendor_dlkm` images and SHA-256 hashes.
3. Installed module names, vermagic, signatures, imports, MODVERSIONS CRCs,
   namespaces, load lists, and provider precedence.
4. The installed boot header, ramdisk, bootconfig, OS version/security patch,
   AVB footer/properties, and rollback indexes.

The first test candidate should then be packaged with those exact installed
container inputs. A hash-verified rollback must be retained, and only the
minimum proven partition set should be written. Until that evidence is
captured, this branch is a **static LineageOS 24 candidate, not a physically
qualified stable kernel**.

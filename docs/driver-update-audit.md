# SM8850 Qualcomm/OPlus driver update audit

Date: 2026-10-09

## Outcome

This audit found multiple valuable Qualcomm security and correctness fixes in
the LineageOS 24.0 SM8850 module history. None can be deployed by this
project's required boot-only payload, however, because the affected drivers
are supplied at runtime by the exact OxygenOS 16.0.10.601 `system_dlkm`,
`vendor_dlkm`, or `vendor_boot` modules. Updating their unused source in this
repository would not update the code running on the phone.

No Qualcomm/OPlus driver implementation change was therefore selected. This
is a compatibility result, not a claim that the stock modules contain every
fix listed below. A future matched-module project can use the recorded
candidate set, but it must qualify the complete proprietary firmware,
userspace, device-tree, signing, load-order, and module dependency contract.

## Exact baseline

| Field | Value |
|---|---|
| Audit branch | `feature/sm8850-driver-updates` |
| Starting source | `d7542a5e36183aa26b00f6046f81527c7d4abe47` |
| Linux | `6.12.112` |
| Android KMI | generation 6 |
| Firmware contract | OxygenOS `CPH2749_16.0.10.601(EX01)` |
| Physically qualified release kernel | `6.12.112-android16-6-o-g8dd9cb4790b7-4k` |
| Qualified source change | `1cd6164a81e631e33a3d8181c357630607f5fd65` |
| Qualified boot SHA-256 | `a44ee825f3eb58ce84e7c2d24ebaeccce4669695f9c57bc0904184ffe10d4f6f` |
| Qualified Image SHA-256 | `6afffa074630cdfa52b50ed7881e0ef85c82731186ee034637671ba080ee7531` |
| Qualified Module.symvers SHA-256 | `a1665917c5579d1c59f3d91197e8ff22188404163ef28e2a046a9c998b2366d4` |
| Qualified common config SHA-256 | `33d560b482136e2f32646142c4e5e50fe0cd312691b20d077eb069cf956d68a3` |
| Current effective Canoe config SHA-256 | `65cb85a35d1c211ca6930eaeebda72c0357829f779e34003f75d544771810f52` |
| Current Module.symvers SHA-256 | `a1665917c5579d1c59f3d91197e8ff22188404163ef28e2a046a9c998b2366d4` |
| Payload contract | `boot.img` only; all DLKM and supporting partitions stock |

The starting source includes the separately validated built-in NTFS3 config
change at `d7542a5e3618`; its production build is not a physical driver-update
qualification. The immutable physical rollback oracle remains the qualified
watchdog release above.

The `.601` stock-module oracle is authoritative: 1,021 modules, 985 active
compatible, 36 dormant, 56,594/56,594 hard imports, and 57,621/57,621
MODVERSIONS records, with zero missing providers, CRC mismatches, namespace
failures, or active blockers.

## Source lineage

The checked-in manifest still records the original OnePlus module snapshot
`5ab2a689ff87d7d28c511f1762cf41c1b90d965a`. That snapshot identifies the
Kaanapali/SM8850 platform line and these initial component revisions:

- kernel platform `.099.064`;
- WLAN `.037`;
- Bluetooth `.031`;
- GPU `.038`;
- display/mm `.071`;
- camera `.061`;
- audio `.046`;
- video `.047`;
- DSP/securemsm/dataipa/datarmnet `.078` where applicable;
- SPU and data-kernel `.102`.

Later repository history contains bounded OnePlus source integrations,
including WLAN `.053`, Bluetooth `.046`, graphics `.057`, camera `.073`,
audio `.059`, and selected safety fixes. They are not a single matched `.601`
module release and must not be confused with the exact stock binary module
population used by the production phone.

The reference checkout was LineageOS `lineage-24.0` at
`08b3042484e2cfc03fbd9ccb5073d55d561c0a79`. The September 30 merge chain
contains 222 Qualcomm commits across 17 upstream merges. Exact merge/tag/tip
provenance is in
[`driver-updates/sm8850-upstream-provenance.tsv`](driver-updates/sm8850-upstream-provenance.tsv).

Tag discovery was also performed in the other namespaces named by those
merges: `vendor/qcom-opensource`, `vendor/qcom/opensource`, and
`vendor/opensource`. Later `LA.VENDOR.16.2.0.r1-21400-kaanapali.0` names found
for several components resolve to the same commit as the reviewed `-21300`
tag; they do not contain newer code. The requested WLAN 10800, graphics
10300, display 17600, camera 15200, audio 12400, and video 12600 tips were the
latest distinct reviewed Kaanapali code for their series.

Lineage follow-ups after the September 30 Qualcomm merge were reviewed
separately:

| Commit | Subject | Result for Canoe/OOS `.601` |
|---|---|---|
| `082407389ed5` | OPlus changes from `PLR110_16.0.10.500(CN01)` | foreign product source; do not import |
| `0a511db33f2f` | OPlus changes from `OPD2514_16.0.6.103(EX01)` | foreign product source; do not import |
| `c3745fcbae09` | Audio OPlus changes from OPD2514 | foreign product module/userspace contract |
| `35a71cb7c7e5` | Camera OPlus changes from OPD2514 | foreign product camera/HAL contract |
| `2a0e9bbed48f` | Display OPlus changes from OPD2514 | foreign panel/display contract |
| `d70e9bd62cf3` | WLAN OPlus changes from CPH2841 | foreign product WLAN calibration/DT contract |
| `f7b8e882d9c9` | Touch gesture/keycode change | generic Lineage behavior change, not a security backport |
| `c2c2a9970f56` | Pen enabled by default | product/userspace policy change |
| `47939f7e9320` | Drop touchscreen timing bit | Lineage input ABI behavior change |
| `08b3042484e2` | Fingerprint notifier dependency limited to MediaTek | irrelevant to the Qualcomm Canoe path |

The September 28 Lineage HFI follow-up `4afc7a51c736` was also reviewed. Its
newer MM/HFI generation removes an unbalanced clock-ready wake disable, but
the current `.071` source does not contain the same file/generation and the
runtime `msm_hfi_core.ko` is stock. It is retained as a targeted future
investigation, not presented as a fix for the observed idle HFI waiter.

## Runtime provider boundary

The final Canoe config deliberately keeps the relevant providers modular.
Examples include `CONFIG_ARM_SMMU=m`, `CONFIG_BT=m`, `CONFIG_BT_HIDP=m`,
`CONFIG_PPP=m`, `CONFIG_QCOM_SCM=m`, `CONFIG_QCOM_SPSS=m`,
`CONFIG_RFKILL=m`, `CONFIG_SCSI_UFS_QCOM=m`, and `CONFIG_ZRAM=m`. CFI, module
signing, MODVERSIONS, and KMI enforcement remain enabled.

| Subsystem | Production provider | Stock partition | Boot-only consequence |
|---|---|---|---|
| WLAN | `qca_cld3_*`, CNSS/platform modules | `vendor_dlkm` | WLAN source edits require matched modules and firmware qualification |
| Bluetooth | Bluetooth core plus Qualcomm/OPlus modules | `system_dlkm`, `vendor_dlkm` | source edits do not enter `boot.img` |
| GPU | `msm_kgsl.ko` | `vendor_dlkm` | KGSL fixes require replacing the signed runtime module |
| Display/HFI | `msm_drm.ko`, `msm_hfi_core.ko` | `vendor_boot`, `vendor_dlkm` | recovery and Android copies must remain matched |
| Camera | `camera.ko` | `vendor_dlkm` | monolithic provider is tied to HAL, tuning, firmware, and DT |
| Audio/DSP | audio modules, GPR and `frpc-adsprpc.ko` | `vendor_dlkm` | complete DSP/audio dependency closure is required |
| Video | `msm_video.ko`, `msm_hfi_core.ko` | `vendor_dlkm`, `vendor_boot` | HFI firmware and recovery path are coupled |
| IPA/RMNET | IPA and RMNET module families | `vendor_dlkm` | modem firmware and the full module family are coupled |
| SecureMSM/SPU | smcinvoke/qseecom/crypto/SPU modules | `vendor_boot`, `vendor_dlkm` | secure-world protocol must match |
| USB/Type-C | DWC3/QCOM/GSI glue modules | `vendor_boot`, `vendor_dlkm` | recovery and Android load paths are coupled |
| UFS/ICE | QCOM UFS, crypto and PHY modules | `vendor_boot`, `vendor_dlkm` | storage/FBE path cannot be partially replaced |
| ZRAM/QPACE | `zram.ko` and vendor compression providers | `system_dlkm`, `vendor_boot`, `vendor_dlkm` | source edits cannot change the production worker |
| OPlus hardware | product-specific OPlus modules | primarily `vendor_dlkm` | product calibration and userspace contracts apply |

## Compatibility matrix

| Subsystem | Existing revision | Candidate revision | Upstream source | Firmware compatibility | KMI/ABI impact | Risk | Decision |
|---|---|---|---|---|---|---|---|
| WLAN: qcacld, host-cmn, fw-api, platform | OnePlus WLAN `.053` bounded source over the original `.037` lineage | `WLAN.LA.2.0.r3-10800-kaanapali.0` | four `vendor/qcom-opensource/wlan` repositories | Candidate code fits Kaanapali but the running `.601` qca/CNSS providers and WLAN firmware remain stock | complete WLAN module-family CRC, dependency, symbol, and signing requalification | Critical: partial update can prevent WLAN probe or corrupt datapath state | **REQUIRES MATCHED MODULES** |
| Bluetooth integration | OnePlus BTFM `.046` selected source; stock `.601` runtime modules | `BTFM.LA.2.0.r1-08300-kaanapali.0` (`08400` aliases same tip) | `vendor/qcom-opensource/bt-kernel` | vendor firmware, codecs, HAL, and stock core/provider ordering are coupled | rebuilt Bluetooth/QCOM providers must match all stock consumers | High | **REQUIRES MATCHED MODULES** |
| GPU/Adreno/KGSL | graphics `.038` plus selected `.057` guard | `GRAPHICS.LA.16.0.r1-10300-kaanapali.0` | `vendor/qcom/opensource/graphics-kernel` | candidate targets Kaanapali, but production loads stock `msm_kgsl.ko` | exported KGSL and private vendor ABI plus firmware/userspace | Critical | **REQUIRES MATCHED MODULES** |
| Display/DRM/DSI/panel | display/mm `.071` with selected local compatibility repairs | `DISPLAY.LA.6.0.r1-17600-kaanapali.0` | `vendor/opensource/display-drivers`, `mm-drivers` | panel, compositor, DT, recovery display, and stock modules are matched to `.601` | large DRM/display private ABI surface | Critical | **FIRMWARE DEPENDENT** |
| Camera | camera `.061` plus selected `.073` RER safety work | `CAMERA.LA.6.0.r1-15200-kaanapali.0` | `vendor/opensource/camera-kernel` | monolithic camera module is matched to proprietary HAL, firmware, tuning, and DT | very large private ioctl/structure dependency surface | Critical | **REQUIRES MATCHED MODULES** |
| Audio | audio `.046` plus selected `.059` GPR teardown work | `AUDIO_HANDSET.LA.11.0.r1-12400-kaanapali.0` | `vendor/qcom/opensource/audio-kernel-ar` | DSP firmware, HAL, codec DT and the module set must be updated together | GPR/audio provider and consumer CRC closure | High | **REQUIRES MATCHED MODULES** |
| Video/HFI | video `.047` | `VIDEO_HANDSET.LA.1.0.r1-12600-kaanapali.0` | `vendor/opensource/video-driver` | production and recovery both load stock HFI/video providers tied to firmware | HFI/video module and private callback ABI | Critical | **FIRMWARE DEPENDENT** |
| DSP | DSP `.078` lineage | `LA.VENDOR.16.2.0.r1-21300-kaanapali.0` | `vendor/qcom/opensource/dsp-kernel` | FastRPC/DSP firmware and userspace registration protocol are coupled | `frpc-adsprpc.ko` and dependents require matched rebuild | High | **REQUIRES MATCHED MODULES** |
| DataIPA/RMNET/network | bounded OnePlus `.102` sources | `LA.VENDOR.16.2.0.r1-21300-kaanapali.0` | `vendor/opensource/dataipa`, `vendor/qcom/opensource/datarmnet*` | modem firmware, IPA hardware revision, RMNET extensions and userspace must match | multi-module data-path dependency closure | Critical | **FIRMWARE DEPENDENT** |
| SecureMSM/SPU | securemsm `.078`, SPU `.102` lineage | `LA.VENDOR.16.2.0.r1-21300-kaanapali.0` | `vendor/qcom/opensource/securemsm-kernel`, `spu-kernel` | secure-world protocol and stock normal/recovery modules are matched | qseecom/smcinvoke/crypto/SPU provider closure | Critical | **FIRMWARE DEPENDENT** |
| Touchscreen/fingerprint | OxygenOS Canoe/Infiniti product drivers | LA.VENDOR `21300` reference plus post-merge OPlus changes | `vendor/opensource/touch-drivers`, `vendor/qcom-opensource/fingerprint`, Lineage OPlus tree | post-merge changes are primarily for PLR110, OPD2514 and CPH2841, not this device/firmware | product-specific input/display notifier ABI | Critical | **LINEAGEOS SPECIFIC** |
| USB/Type-C | platform `.099.064` lineage plus selected `.099.086` safety work | no coherent Canoe `.601` candidate established from the module reference | QCOM platform/vendor module trees | DWC3 MSM/GSI providers exist in both recovery and normal module sets | recovery/normal provider duplication and private ABI | High | **NEEDS INVESTIGATION** |
| UFS/storage/ICE | ACK 6.12.112 UFS core plus stock QCOM UFS/crypto/PHY/OPlus modules | no matched Kaanapali module set established by this reference | common UFS plus QCOM/OPlus platform trees | FBE, recovery, ICE, SCM and stock firmware are inseparable | storage/FBE module contract is a hard gate | Critical | **NEEDS INVESTIGATION** |
| Power/thermal | OxygenOS Canoe product drivers and stock `.601` modules | Lineage post-merge OPlus updates from other products | Lineage OPlus tree and QCOM platform drivers | calibration, charger IC, thermal tables, DT and userspace are device-specific | extensive private vendor hooks and module ABI | Critical | **LINEAGEOS SPECIFIC** |
| Memory/DMA/IOMMU/synchronization | ACK 6.12.112 common core plus OnePlus/QCOM `.601` modules | display 17600/MM fixes and LA.VENDOR 21300 support code | `mm-drivers`, Synx, MMRM, QCOM platform sources | common-kernel stable fixes are already integrated; vendor fixes remain module-owned | stock fence/Synx/IOMMU provider contract | High | **REQUIRES MATCHED MODULES** |
| OPlus-specific drivers | exact Canoe/Infiniti OxygenOS sources and stock modules | Oct. 2-8 Lineage OPlus changes | Lineage OPlus tree | updates name different product/firmware families and include broad feature deltas | private OPlus interfaces, DT, HAL, firmware and calibration | Critical | **LINEAGEOS SPECIFIC** |

## High-value fix review

The detailed inventory in
[`driver-updates/sm8850-fix-candidates.tsv`](driver-updates/sm8850-fix-candidates.tsv)
records exact SHAs, technical patch applicability, runtime providers, and the
deployment decision. Highlights include:

- seven WLAN memory-safety/lifetime fixes, including OOB, double-free,
  arbitrary mapping, NULL-deref, reference leak, and teardown completion
  fixes;
- CNSS format-string, GPIO failure-path, and suspend/loading fixes;
- Video UAF, SSR, and suspend/resume timeout fixes;
- KGSL mmap isolation fixes;
- IPA arbitrary SMMU mapping and RMNET ingress OOB fixes;
- SecureMSM crypto scatterlist NULL-deref fix;
- ten Camera OOB/UAF/lifetime/locking fixes;
- audio GPR timeout cleanup and display wakelock fixes.

Many individual patches apply cleanly to the source tree. That is not enough:
the resulting code would be compiled into a replacement module, while the
boot-only phone would continue loading the unchanged stock binary. All are
therefore withheld from this branch.

## Watchdog threads

The prior `adci_thread`, `zram_comp`, and `hfi_core_dbg_cl` reports do not
justify a module refresh:

- the ADCI, ZRAM/QPACE and HFI workers are supplied by stock `.601` modules;
- the current boot-only kernel contains a physically qualified detector-side
  filter that ignores only their exact proven idle wait channels;
- Video 12600 contains genuine SSR/UAF/PM improvements, but no evidence proves
  that those changes repair the observed idle HFI wait;
- replacing any of these modules would change the release architecture and
  require a new full module/firmware qualification.

The watchdog remains enabled and active Secure World, QPACE, and HFI/IPC
stalls remain reportable.

## Validation and disposition

This branch changes documentation only. No kernel, Kconfig, DT, module list,
symbol list, ABI definition, firmware, or packaging input changed. Therefore:

- no new kernel image was produced for this audit;
- no source update was available to trigger a per-series build;
- the existing production build/KMI/ABI/module evidence remains the baseline,
  not a claim of validation for withheld module patches;
- runtime validation of the unselected candidates is **NOT TESTED**;
- no flash was performed.

The most useful next project is a separately authorized matched-module
hardening effort, starting with the security-sensitive WLAN, Camera, IPA,
KGSL, SecureMSM and Video candidates. It must produce and qualify matched
DLKM payloads and therefore cannot be represented as this kernel's current
boot-only release.

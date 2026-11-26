# LineageOS 6.12.119 temporary physical canary

Date: 2026-11-26

Result: **REPAIRED CANDIDATE PASS — ORIGINAL CANDIDATE QUARANTINED**

## Preflight

- Device: OnePlus 15 / `infiniti` / Canoe
- Serial: recorded locally; omitted from this report
- LineageOS incremental: `63eb77a308`
- Security patch level: `2026-11-01`
- Active slot: `b`
- Stock running kernel: `6.12.81-android16-6-gf4c1a270b7b0-4k`
- Candidate SHA-256: `b484535885af5198dc8b32b5425ca3274436dc358bedd5a612d4ecb5b8865ddf`
- Candidate size: 100,663,296 bytes
- Candidate command: temporary `fastboot boot`; no partition write

The bootloader did not provide a working `fastboot fetch` implementation, so a live partition read-back was unavailable. The exact target OTA stock boot artifact and its verified hash remained locally available for rollback. No security policy, AVB setting, slot metadata, or non-boot partition was changed.

## Candidate observations

- Kernel entry: PASS
- ADB return: PASS
- Running kernel identity: PASS (`6.12.119-android16-6-o-g7477d64d7643-4k`)
- Qualcomm emergency ramdump: not observed
- Stock system/vendor module loading: FAIL for protected-symbol exporters
- Android boot completion: FAIL
- User 0 unlock / CE availability: NOT REACHED
- Persistent flash: NO

The crash buffer recorded repeated aborts of `/vendor/bin/hw/audiohalservice.qti`:

```text
Abort message: 'failed to register Interface: [name: audioeffecthal path: libaudioeffecthal.qti.so mandatory: 1] '
```

The immediately preceding messages establish the failure sequence:

```text
AHAL_EffectMainQti: getEffectConfig using effects in stub mode
AHAL_EffectMainQti: registerServiceImpl: config file audio_effects_config_stub.xml not found!
AHAL_Service_QTI: failed to register service: Interface: [name: audioeffecthal path: libaudioeffecthal.qti.so mandatory: 1]
init: process with updatable components 'vendor.audio-hal-aidl' exited 4 times before boot completed
```

The core, USB, and remote-submix AIDL audio modules registered, but `android.hardware.audio.effect.IFactory/default` did not. `audioserver` and the Qualcomm audio HAL then restarted repeatedly, and core Android services did not stabilize.

## Follow-up diagnosis

A second temporary diagnostic boot added a single ASoC component-defer message. It identified the final missing component as:

```text
name=btfmcodec_dev dai=btaudio_rx link=BTFM_PROXY-RX-0
```

`btfmcodec.ko` was present, but `bt_fm_swr.ko` had not loaded. Tracing the stock module dependency chain found that stock `rfkill.ko` was rejected first. A direct diagnostic load reproduced the decisive kernel message:

```text
rfkill: exports protected symbol rfkill_alloc
```

The loader returned `EPERM`. Under the retained `CONFIG_MODULE_SIG_PROTECT` policy, an untrusted module may not export a protected symbol. The failed candidate trusted the October 14 certificate, while the exact November 25 stock `system_dlkm` and `vendor_dlkm` modules are signed by the November 25 Lineage build certificate. The rejection blocked `rfkill`, then `btpower`, `bt_fm_swr`, Bluetooth/WLAN dependencies, the complete Canoe sound-card registration, and finally the Qualcomm audio HAL.

The November 25 public certificate was extracted from the exact stock boot kernel and independently verified against stock `rfkill.ko`. Its serial is `05CB5E0A5594D4DE6103A947857CDA470BF47970` and its SHA-1 fingerprint is `B2:96:BF:D9:DB:2C:32:D8:04:5F:A3:7A:4A:3A:F4:01:C6:A0:BD:D2`. The repaired source changes only the built-in trusted certificate; signature enforcement is not disabled or weakened.

## Stock recovery verification

Rebooting ended the temporary boot and restored the unchanged slot-`b` image automatically.

- Running kernel: `6.12.81-android16-6-gf4c1a270b7b0-4k`
- Android `sys.boot_completed`: `1`
- Owner credential verification: PASS
- User 0 state: `RUNNING_UNLOCKED`
- CE availability: `true`
- Encryption: encrypted, file-based
- SELinux: enforcing
- Stock `android.hardware.audio.effect.IFactory/default`: registered
- Fingerprint and incremental: unchanged

## Decision and next action

The failed image remains quarantined and must not be flashed. The targeted trust-anchor repair must pass a new production build, ABI/KMI gates, exact stock-module signature and symbol checks, and a temporary `fastboot boot` canary before any persistent active-slot write is considered.

## Repaired candidate qualification

The repaired source is commit `46d53f13f126826b2e22f95017e6c86dce1277b4`.
It retains signature enforcement and embeds the exact November 25 public
certificate. The repaired protected GKI configuration includes
`CONFIG_MODULE_SIG_PROTECT=y` and
`CONFIG_SYSTEM_TRUSTED_KEYS="certs/lineage24_0_20261125_gki_module_signing.pem"`.

Offline qualification passed:

- Canoe production build: PASS
- Common KMI symbol gate: PASS
- `--kbuild_symtypes`: PASS
- Canoe device-inclusive ABI: PASS
- Enforced common ABI distribution: PASS
- Exact 640-module symbol/CRC/namespace oracle: PASS
- Exact stock signature verification: 109 / 109 signed modules
- Protected-export audit: 108 modules and 494 exports accounted for
- Boot container and AVB verification: PASS

The new candidate is `out/lineage24-kernel-sync-repaired-test/boot.img`, size
100,663,296 bytes, SHA-256
`5cbfcbae7e59d2786fbd935cca6c264354a90b7f510f637d11af4f4db9cfe6ee`.

The repaired image first passed a non-writing `fastboot boot` canary:

- Exact running kernel: `6.12.119-android16-6-o-g46d53f13f126-4k`
- Android `sys.boot_completed`: `1`
- User 0 / FBE / CE unlock: PASS (`RUNNING_UNLOCKED`)
- Stock `rfkill`, `btpower`, `bt_fm_swr`, and `btfmcodec`: loaded
- Canoe sound card: registered, 47 links
- `/dev/snd` nodes: 49
- Audio-effect factory: registered
- Rust Binder: built in and active; no `rust_binder.ko` loaded
- Wi-Fi, Bluetooth, LTE voice/data, NFC, camera enumeration, fingerprint,
  USB/ADB, charging, and short suspend/resume: PASS
- Kernel fatal-error scan and pstore: clean

After the temporary canary passed, owner authorization was applied to exactly
the active `boot_b` partition. `fastboot flash boot_b` returned `OKAY` for both
transfer and write. No other partition and no slot metadata were modified.
The persistent reboot repeated Android, FBE/CE, audio, module, hardware-service,
and suspend/resume checks successfully. A root read-only block-device read-back
of `boot_b` produced the exact candidate SHA-256 above.

The verified stock rollback image remains available with SHA-256
`f7ee42343ee769df2ca1fe39e126dd9249b7b076de8258744ddcdce95a0f9611`.

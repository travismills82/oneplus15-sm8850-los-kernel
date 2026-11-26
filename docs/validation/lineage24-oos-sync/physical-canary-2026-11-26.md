# LineageOS 6.12.119 temporary physical canary

Date: 2026-11-26

Result: **FAIL — DO NOT FLASH**

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
- Stock system/vendor modules loaded: PASS at the kernel level, including the audio module stack
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

The core, USB, and remote-submix AIDL audio modules registered, but `android.hardware.audio.effect.IFactory/default` did not. `audioserver` and the Qualcomm audio HAL then restarted repeatedly, and core Android services did not stabilize. This identifies the immediate runtime blocker; it does not yet prove which synchronized kernel change caused the HAL to select stub mode.

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

Quarantine this boot image and do not flash it. Investigate the kernel-visible condition that makes the Qualcomm audio HAL choose stub mode, implement one targeted repair, rerun all offline ABI/KMI/module gates, and repeat a temporary `fastboot boot` canary before considering a persistent active-slot write.

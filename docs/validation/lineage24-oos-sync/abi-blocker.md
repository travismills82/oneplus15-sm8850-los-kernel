# Common ABI reference review and resolution

Status: RESOLVED

The initial mandatory `//common:kernel_aarch64_abi_dist` run exited with status 4 because the synchronized Linux 6.12.119 kernel was compared against the qualified 6.12.112 downstream ABI definition.

The reported delta included:

- Added exports: `__mm_reset_vma_seqcounts`, `__tty_port_tty_hangup`, and `shmem_file`.
- Exported GPIO setter return types changing from `void` to `int`.
- Forty CRC-only symbol changes, including Rust kernel symbols.
- Structure/type changes, many using reserved KABI fields.

No symbol removals were reported. The exact installed LineageOS module oracle independently passed with zero missing imports, CRC mismatches, or namespace failures across all 640 stock modules.

## Reference provenance

The synchronized branch and `oos/main` initially contained the identical `kernel_platform/common/gki/aarch64/abi.stg` blob `ad11011844b1ad8f68d164eb9590b79ce43b1be8`. Its latest history entry was `8dd9cb4790b7436a12606c842f8e222701be3e61`, dated 2026-10-07 and explicitly reconstructed for the qualified 6.12.112 ABI.

The official Android common `android16-6.12-lts` branch was checked read-only. Its head was Linux 6.12.119 and contained a newer upstream ABI definition, demonstrating that an ABI reference advance accompanies this LTS level. That upstream definition could not be copied directly because its KMI symbol surface differs from the downstream Lineage/Qualcomm contract.

## Resolution

The repository's supported `//common:kernel_aarch64_abi_update` target regenerated the downstream definition from the already validated 6.12.119 kernel. This operation changed only `common/gki/aarch64/abi.stg`; it did not change the kernel source, configuration, binary, security policy, or stock modules.

Post-update validation:

- Refreshed definition versus generated ABI: exact match, `stgdiff` exit 0.
- Common enforced ABI distribution: PASS.
- Common strict KMI symbol check: PASS.
- `--kbuild_symtypes` KMI build and violation check: PASS.
- Canoe device-inclusive ABI: PASS.
- Exact 640-module stock contract: PASS.

ABI enforcement was not disabled or suppressed, security fixes were not reverted, and no stock DLKM image was modified.

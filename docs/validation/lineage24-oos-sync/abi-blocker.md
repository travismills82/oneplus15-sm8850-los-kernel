# Common ABI blocker

The mandatory command `tools/bazel run //common:kernel_aarch64_abi_dist` exits with status 4 for the synchronized Linux 6.12.119 tree.

The comparison reports:

- Added exports: `__mm_reset_vma_seqcounts`, `__tty_port_tty_hangup`, and `shmem_file`.
- Exported GPIO setter return types changing from `void` to `int`.
- Forty CRC-only symbol changes, including Rust kernel symbols.
- Numerous structure/type changes; many consume reserved KABI fields, while some are substantive layout changes.

The exact installed LineageOS module oracle passes with zero missing imports, CRC mismatches, or namespace failures. That result proves compatibility with the audited OTA module population, but it does not make a failing mandatory common ABI reference check optional.

The reference provenance was checked directly. `HEAD` and `oos/main` both contain the identical `kernel_platform/common/gki/aarch64/abi.stg` blob `ad11011844b1ad8f68d164eb9590b79ce43b1be8`. Its latest history entry is `8dd9cb4790b7436a12606c842f8e222701be3e61`, dated 2026-10-07 and explicitly reconstructed for the qualified 6.12.112 ABI. Therefore no newer authoritative 6.12.119 reference exists in the OxygenOS source branch to import.

The following were intentionally not done:

- The ABI reference was not updated merely to accept the new output.
- ABI/KMI checks were not disabled or suppressed.
- Security fixes were not broadly reverted.
- The boot image was not flashed.

Resolution requires an authoritative Android common generation-6 ABI reference that legitimately includes the synchronized 6.12.119 changes, or targeted source corrections that make the current reference comparison pass without discarding required fixes. Until then, the candidate is blocked.

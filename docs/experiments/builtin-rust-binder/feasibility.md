# Built-in Rust Binder feasibility

Status: feasible with a narrow boot-only module-load compatibility change; physical testing is still required.

## Protected baseline

The experiment starts from `origin/Lineage-24.0` commit
`5173f30f4ee16589444d686497196fe0bfd639aa`, which is also the commit named by
the protected `lineage24.0-20261014-linux-6.12.112-kmi6` tag. The original
checkout was clean before the separate `builtin-rust-binder` worktree was
created. No stable branch, tag, release asset, or stable build output is changed
by this experiment.

The stable reference artifacts are:

| Artifact | SHA-256 |
|---|---|
| Stable custom `boot.img` | `c98f46a1fefd2b890d0370d8743d63ef35aabc055d25a90dca4395920bc79226` |
| Stable hybrid `system_dlkm.img` | `18524c480a07047c09a284e70ed83395afc74921c960993adc75a5d730e5c33e` |

The untouched LineageOS source was independently extracted from the full
`lineage-24.0-20261014-nightly-infiniti-signed.zip` OTA. Its OTA SHA-256 is
`59e6795ce0ae554b5b6c54e1343ccf8e8515301f2cd1456cbd01fee1b2b72c0a`.
The extracted stock images match the previously recorded rollback hashes:

| Stock image | Size (bytes) | SHA-256 |
|---|---:|---|
| `boot.img` | 100,663,296 | `7ab6b70931631831f3e3381a60bb1bfefe0822eddae4ed6c7883e653695ff911` |
| `system_dlkm.img` | 8,327,168 | `3947c061321b6d8358020feba6138533540741f4e2fb6a09abaf81c55630b788` |
| `vendor_boot.img` | 100,663,296 | `223642a5683afac35557a2255e8e0068c943934155d4ddb22e48325af9be2b1d` |
| `vendor_dlkm.img` | 59,936,768 | `f66672d67544624d513c635846c5e797b47f65e3ddd424f614b9c87a30a19d05` |

## Architecture findings

The effective symbol is `CONFIG_ANDROID_BINDER_IPC_RUST`, not
`CONFIG_RUST_BINDER`. It is a `tristate` under
`common/drivers/android/binder/Kconfig`. The arm64 GKI defconfig currently sets
it to `m`, while `CONFIG_RUST=y`, `CONFIG_ANDROID_BINDER_IPC=y`, and
`CONFIG_ANDROID_BINDERFS=y` are already enabled.

1. Rust Binder is an in-tree composite driver under
   `common/drivers/android/binder/`, not a standalone external module. Kleaf
   currently packages its modular form as
   `drivers/android/binder/rust_binder.ko`.
2. Its Kconfig type supports both `y` and `m`. Its dependencies are `RUST`,
   `MMU`, and `NET`, all available in the production configuration.
3. Its Kbuild expression is the standard
   `obj-$(CONFIG_ANDROID_BINDER_IPC_RUST) += rust_binder.o`, with the Rust and C
   members selected by the same symbol. This supports a built-in composite
   object. The arm64 Kleaf module output list must stop expecting a `.ko` when
   the symbol becomes `y`; the x86 module configuration is unaffected.
4. The kernel Rust `module!` macro explicitly supports built-in drivers. In
   non-module builds it supplies a null `ThisModule` pointer and emits the
   initializer into `.initcall6.init`. Rust Binder's use of that macro is not
   inherently module-only.
5. The Rust initializer depends on the C Binder coordination symbols
   `binder_use_rust`, `unload_binder`, and, with event tracing,
   `binder_remove_trace_events`. They are linked into the same kernel and are
   initialized in a compatible order. The C Binder `device_initcall` runs
   before the Rust Binder initcall because of the Android Makefile link order;
   the Rust initializer then unregisters the unused C Binder resources before
   registering Rust Binder netlink, shrinker, and binderfs resources.
6. The C Binder implementation remains configured. This is intentional support
   code for the existing runtime implementation selector, not a second active
   Binder. For this experiment the built-in Rust configuration defaults the
   selector to Rust. An explicit `binder.impl=c` command-line option can still
   select the C implementation before initialization.
7. There is no kernel-tree userspace service that requires a module object, but
   the exact stock `system_dlkm/lib/modules/modules.load` explicitly contains
   `rust_binder` as entry 50. The exact stock `vendor_boot` also enables
   parallel first-stage module loading through
   `androidboot.load_modules_parallel=true`.
8. The built-in driver initializes during the kernel initcall sequence, before
   Android first-stage init mounts and loads `system_dlkm`; it therefore no
   longer depends on that partition becoming available.
9. The stock population is 88 `system_dlkm` modules and 552 `vendor_dlkm`
   modules. Their compatibility must be checked independently against the
   candidate `vmlinux` and `Module.symvers`; passing KMI checks alone is not
   sufficient.
10. The untouched stock image does contain `rust_binder.ko`. Its SHA-256 is
    `411e911830a0633492be96affd2d23b486c9e10242101c4b7e1cba80943f3dac`,
    and its vermagic identifies the stock `6.12.81` kernel. It cannot be allowed
    to proceed through ordinary loading against the candidate.

## Required compatibility behavior

Changing only `CONFIG_ANDROID_BINDER_IPC_RUST=m` to `y` is insufficient. The
stock first-stage module list still asks the kernel to load `rust_binder.ko`.
That request can fail on vermagic or symbol versions before ordinary duplicate
registration detection, and Android first-stage init treats a requested-module
failure as fatal.

The maintainable boot-only solution is deliberately narrow:

- keep module-signature checking and ELF/name validation intact;
- when and only when `CONFIG_ANDROID_BINDER_IPC_RUST` is built-in, recognize an
  incoming module whose embedded name is exactly `rust_binder`;
- report that request as satisfied without allocating, relocating, or invoking
  the stock module; and
- retain ordinary blacklist and load behavior for all other modules.

This prevents the stock file from replacing or double-registering the built-in
driver while allowing the original `modules.load` to remain unchanged. The
candidate build and stock-module audit must still prove that no other
compatibility regression was introduced.

## Implemented source changes

- arm64 GKI defconfig: set `CONFIG_ANDROID_BINDER_IPC_RUST=y`;
- arm64 Kleaf GKI module list: remove the no-longer-produced
  `rust_binder.ko` output;
- C Binder coordination: make Rust the default implementation only when the
  Rust driver is built-in, while preserving the existing `binder.impl=`
  override;
- module loader: satisfy the exact signed stock `rust_binder` request from the
  built-in implementation before incompatible module metadata is consumed.

No legacy-C-Binder substitution, security relaxation, ABI-check bypass, or
non-boot partition change is part of the design.

The implementation and final static evidence are recorded in
`builtin-verification.md`. All mandatory build, common ABI, strict KMI, Canoe
ABI, retained-stock module, and boot-container checks pass. Physical testing
has not been run and remains the final qualification gate.

#!/usr/bin/env python3
"""Audit retained stock modules against an exact controlled-v1 Image.

The controlled stack intentionally remains hybrid while source coverage grows.
This tool makes that boundary explicit: it reads stock module trees, indexes
the *candidate* provider trees plus vmlinux Module.symvers, and independently
checks every ELF undefined symbol for a real exported provider and every
MODVERSIONS record for an exact CRC match.  It refuses an active retained
module with an unresolved hard import, a provider-side error on a weak import,
a CRC mismatch, an incompatible non-release vermagic suffix, an unknown
signature, or a protected provider edge that was not included in the signed
replacement closure.

It is read-only with respect to all module inputs.  It writes a concise
``retained-stock-contract.tsv`` and an import-level companion report suitable
for packaging with a controlled-v1 release.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


def load_elf_helpers():
    helper_path = Path(__file__).with_name("validate-matched-wlan-vendor-dlkm.py")
    specification = importlib.util.spec_from_file_location(
        "matched_wlan_vendor_dlkm_validator", helper_path
    )
    if specification is None or specification.loader is None:
        raise RuntimeError(f"cannot load {helper_path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


ELF = load_elf_helpers()


@dataclass(frozen=True)
class Provider:
    partition: str
    name: str
    crc: int
    controlled: bool
    export_class: str
    namespace: str
    sha256: str

    @property
    def label(self) -> str:
        return f"{self.partition}:{self.name}"


def die(message: str) -> None:
    raise ValueError(message)


def split_assignment(value: str, label: str) -> tuple[str, Path]:
    if "=" not in value:
        die(f"{label} must be PARTITION=PATH: {value}")
    partition, raw_path = value.split("=", 1)
    if not partition or not raw_path:
        die(f"{label} must be PARTITION=PATH: {value}")
    path = Path(raw_path).resolve()
    return partition, path


def split_load_assignment(value: str) -> tuple[str, str, Path]:
    if "=" not in value or ":" not in value.split("=", 1)[0]:
        die(f"--load-list must be PARTITION:MODE=PATH: {value}")
    key, raw_path = value.split("=", 1)
    partition, mode = key.split(":", 1)
    if not partition or not mode or not raw_path:
        die(f"--load-list must be PARTITION:MODE=PATH: {value}")
    return partition, mode, Path(raw_path).resolve()


def split_module_assignment(value: str, label: str) -> tuple[str, str]:
    if ":" not in value:
        die(f"{label} must be PARTITION:MODULE: {value}")
    partition, module = value.split(":", 1)
    if not partition or not module:
        die(f"{label} must be PARTITION:MODULE: {value}")
    return partition, module.removesuffix(".ko").replace("-", "_")


def sanitize(value: object) -> str:
    return str(value).replace("\t", " ").replace("\n", " ").strip()


def modinfo(path: Path, field: str) -> str:
    result = subprocess.run(
        ["modinfo", "-F", field, str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return ",".join(line for line in result.stdout.splitlines() if line)


def certificate_cn(path: Path) -> str:
    result = subprocess.run(
        ["openssl", "x509", "-in", str(path), "-noout", "-subject", "-nameopt", "compat"],
        check=True,
        capture_output=True,
        text=True,
    )
    prefix = "subject=/CN="
    subject = result.stdout.strip()
    if not subject.startswith(prefix):
        die(f"could not derive common name from certificate: {path}")
    return subject[len(prefix) :].split("/", 1)[0]


def parse_load_list(path: Path) -> set[str]:
    if not path.is_file():
        die(f"missing modules.load input: {path}")
    entries: set[str] = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        # Kbuild canonicalizes '-' to '_' in the ELF module name while
        # modules.load commonly retains the filename spelling. Compare the
        # canonical names so loaded modules are not misclassified as dormant.
        entries.add(Path(line).name.removesuffix(".ko").replace("-", "_"))
    return entries


def read_controlled_modules(value: str) -> dict[str, set[str]]:
    """Parse PARTITION=protected-export-signing-closure.tsv."""

    partition, path = split_assignment(value, "--controlled-module-list")
    if not path.is_file():
        die(f"missing controlled-module list: {path}")
    modules: set[str] = set()
    with path.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        if not reader.fieldnames or "module" not in reader.fieldnames:
            die(f"controlled-module list has no module column: {path}")
        for row in reader:
            name = (row.get("module") or "").strip()
            if name:
                modules.add(name)
    return {partition: modules}


def add_records(
    provider_index: dict[str, list[Provider]],
    partition: str,
    root: Path,
    controlled: set[str],
) -> None:
    if not root.is_dir():
        die(f"candidate provider root is not a directory: {root}")
    records = ELF.scan_root(root, partition, "CANDIDATE_PROVIDER")
    for record in records.values():
        for symbol, export in record.export_records.items():
            provider_index[symbol].append(
                Provider(
                    partition,
                    record.name,
                    export.crc,
                    record.name in controlled,
                    export.export_class,
                    export.namespace,
                    record.sha256,
                )
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vmlinux-symvers", type=Path, required=True)
    parser.add_argument("--kernel-release", required=True)
    parser.add_argument("--expected-vermagic", required=True)
    parser.add_argument("--stock-cert", type=Path, required=True)
    parser.add_argument("--project-cert", type=Path, required=True)
    parser.add_argument(
        "--stock-root",
        action="append",
        default=[],
        metavar="PARTITION=PATH",
        help="read-only stock tree to classify; may be repeated",
    )
    parser.add_argument(
        "--candidate-root",
        action="append",
        default=[],
        metavar="PARTITION=PATH",
        help="candidate module tree used as a provider map; may be repeated",
    )
    parser.add_argument(
        "--load-list",
        action="append",
        default=[],
        metavar="PARTITION:MODE=PATH",
        help="a supported modules.load list; may be repeated",
    )
    parser.add_argument(
        "--controlled-module-list",
        action="append",
        default=[],
        metavar="PARTITION=TSV",
        help="signed source/re-sign closure; these modules are not retained stock",
    )
    parser.add_argument(
        "--fully-controlled-partition",
        action="append",
        default=[],
        metavar="PARTITION",
        help="partition whose candidate contains no retained stock binaries; may be repeated",
    )
    parser.add_argument(
        "--forbidden-load",
        action="append",
        default=[],
        metavar="PARTITION:MODULE",
        help="a retained module intentionally prohibited from supported load lists",
    )
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--dependency-out", type=Path, required=True)
    parser.add_argument("--summary-out", type=Path, required=True)
    parser.add_argument(
        "--provider-out",
        type=Path,
        help="optional complete actual-export provider map",
    )
    parser.add_argument(
        "--undefined-out",
        type=Path,
        help="optional raw undefined-symbol inventory for --focus-module",
    )
    parser.add_argument(
        "--focus-module",
        default="system_dlkm:rust_binder",
        help="PARTITION:MODULE selected for --undefined-out",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.vmlinux_symvers.is_file():
        die(f"missing exact Image Module.symvers: {args.vmlinux_symvers}")
    if not args.stock_cert.is_file() or not args.project_cert.is_file():
        die("stock and project public certificates are required")
    if not args.stock_root or not args.candidate_root:
        die("at least one --stock-root and --candidate-root are required")
    requested_outputs = [args.out, args.dependency_out, args.summary_out]
    if args.provider_out:
        requested_outputs.append(args.provider_out)
    if args.undefined_out:
        requested_outputs.append(args.undefined_out)
    if any(path.exists() for path in requested_outputs):
        die("refusing to overwrite retained-stock contract output")

    stock_roots = dict(split_assignment(value, "--stock-root") for value in args.stock_root)
    candidate_roots = dict(split_assignment(value, "--candidate-root") for value in args.candidate_root)
    if set(stock_roots) - set(candidate_roots):
        die("every stock partition needs a matching candidate provider root")
    for partition, root in stock_roots.items():
        if not root.is_dir():
            die(f"stock module root is not a directory: {partition}={root}")

    controlled: dict[str, set[str]] = defaultdict(set)
    for value in args.controlled_module_list:
        for partition, names in read_controlled_modules(value).items():
            controlled[partition].update(names)
    for partition in args.fully_controlled_partition:
        if partition not in stock_roots:
            die(f"fully controlled partition has no stock root: {partition}")
        records = ELF.scan_root(stock_roots[partition], partition, "STOCK_INVENTORY")
        controlled[partition].update(records)

    load_modes: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for value in args.load_list:
        partition, mode, path = split_load_assignment(value)
        for module in parse_load_list(path):
            load_modes[partition][module].add(mode)

    forbidden = {split_module_assignment(value, "--forbidden-load") for value in args.forbidden_load}
    for partition, module in forbidden:
        if load_modes.get(partition, {}).get(module):
            die(f"forbidden dormant module is present in a supported load list: {partition}:{module}")

    stock_signer = certificate_cn(args.stock_cert)
    project_signer = certificate_cn(args.project_cert)
    expected_tail = args.expected_vermagic.partition(" ")[2]
    if not expected_tail:
        die("expected vermagic must include a release and feature suffix")

    providers: dict[str, list[Provider]] = defaultdict(list)
    vmlinux_sha = ELF.sha256(args.vmlinux_symvers)
    for symbol, values in ELF.parse_symvers_export_records(args.vmlinux_symvers).items():
        for source, export in values:
            providers[symbol].append(
                Provider(
                    "vmlinux",
                    source,
                    export.crc,
                    False,
                    export.export_class,
                    export.namespace,
                    vmlinux_sha,
                )
            )
    for partition, root in candidate_roots.items():
        add_records(providers, partition, root, controlled[partition])

    # The same binary may be visible through more than one extracted view
    # (for example vendor_boot and vendor_dlkm).  Preserve distinct runtime
    # provider identities while removing exact duplicate parser records.
    for symbol in providers:
        providers[symbol] = sorted(
            set(providers[symbol]),
            key=lambda item: (item.partition, item.name, item.crc, item.namespace),
        )

    rows: list[dict[str, str]] = []
    dependency_rows: list[dict[str, str]] = []
    undefined_rows: list[dict[str, str]] = []
    totals = defaultdict(int)
    aggregate = defaultdict(int)
    focus_partition, focus_module = split_module_assignment(args.focus_module, "--focus-module")
    focus_found = False

    for partition, root in sorted(stock_roots.items()):
        records = ELF.scan_root(root, partition, "RETAINED_STOCK")
        for record in sorted(records.values(), key=lambda item: item.name):
            if record.name in controlled[partition]:
                continue
            modes = sorted(load_modes.get(partition, {}).get(record.name, set()))
            load_mode = "+".join(modes) if modes else "DORMANT"
            active = bool(modes)
            signer = modinfo(record.path, "signer") or "UNSIGNED"
            sig_id = modinfo(record.path, "sig_id") or "NONE"
            vermagic = modinfo(record.path, "vermagic")
            release_token, separator, tail = vermagic.partition(" ")
            has_crcs = "module_layout" in record.imports
            if vermagic == args.expected_vermagic:
                vermagic_contract = "MATCH"
            elif has_crcs and separator and tail == expected_tail:
                vermagic_contract = "MODVERSIONS_RELEASE_TOKEN_DIFFERENT"
            else:
                vermagic_contract = "INCOMPATIBLE"

            if signer == "UNSIGNED":
                signing_contract = "UNSIGNED_RETAINED"
            elif signer == stock_signer:
                signing_contract = "STOCK_TRUSTED"
            elif signer == project_signer:
                signing_contract = "PROJECT_TRUSTED"
            else:
                signing_contract = "UNKNOWN_SIGNER"

            unresolved = 0
            mismatches = 0
            namespace_failures = 0
            provider_ambiguities = 0
            protected_failures = 0
            named_undefined = record.undefined
            hard_required = tuple(symbol for symbol in named_undefined if not symbol.weak)
            weak_imports = tuple(symbol for symbol in named_undefined if symbol.weak)
            versioned_imports = tuple(
                symbol for symbol in named_undefined if symbol.name in record.imports
            )
            nonversioned_required = tuple(
                symbol
                for symbol in hard_required
                if symbol.name not in record.imports
            )
            resolved = 0
            crc_matches = 0

            for undefined in sorted(named_undefined, key=lambda item: item.name):
                symbol = undefined.name
                expected_crc = record.imports.get(symbol)
                candidates = providers.get(symbol, [])
                namespace_compatible = [
                    entry
                    for entry in candidates
                    if not entry.namespace or entry.namespace in record.import_namespaces
                ]
                if expected_crc is None:
                    matching = namespace_compatible
                else:
                    matching = [
                        entry for entry in namespace_compatible if entry.crc == expected_crc
                    ]
                if matching:
                    result = "MATCH"
                    resolved += 1
                    if expected_crc is not None:
                        crc_matches += 1
                    if len(matching) > 1:
                        provider_ambiguities += 1
                elif candidates and not namespace_compatible:
                    result = "NAMESPACE_FAILURE"
                    # A weak symbol is optional only when no provider exists.
                    # Once find_symbol() locates a provider, namespace and
                    # version failures return ERR_PTR and simplify_symbols()
                    # rejects the module even for STB_WEAK.
                    namespace_failures += 1
                elif namespace_compatible and expected_crc is not None:
                    result = "CRC_MISMATCH"
                    mismatches += 1
                else:
                    result = "WEAK_UNRESOLVED" if undefined.weak else "MISSING"
                    if not undefined.weak:
                        unresolved += 1
                # A symbol is a protected-provider edge only when every
                # matching runtime provider is in the controlled signing
                # closure.  Hybrid vendor_dlkm deliberately retains exact
                # stock providers for some duplicate GKI module names (for
                # example zsmalloc); a parallel controlled system_dlkm copy
                # must not turn that valid stock-to-stock dependency into a
                # false protected-export failure.
                controlled_provider = bool(matching) and all(
                    entry.controlled for entry in matching
                )
                if controlled_provider:
                    protected_failures += 1
                dependency_rows.append(
                    {
                        "partition": partition,
                        "consumer": record.name,
                        "load_mode": load_mode,
                        "symbol": symbol,
                        "binding": undefined.binding,
                        "weak": "yes" if undefined.weak else "no",
                        "has_modversions_record": "yes" if expected_crc is not None else "no",
                        "expected_crc": (
                            f"0x{expected_crc:08x}" if expected_crc is not None else ""
                        ),
                        "matching_provider": ",".join(
                            sorted(entry.label for entry in matching)
                        ),
                        "candidate_crcs": ",".join(
                            sorted({f"0x{entry.crc:08x}" for entry in candidates})
                        ),
                        "candidate_namespaces": ",".join(
                            sorted({entry.namespace or "<none>" for entry in candidates})
                        ),
                        "result": result,
                        "controlled_provider": "yes" if controlled_provider else "no",
                    }
                )

            # module_layout is loader-checked but is not an ELF undefined
            # symbol.  Keep it in the CRC gate without inflating the raw
            # undefined-symbol counts.
            special_version_records = sorted(set(record.imports) - {s.name for s in named_undefined})
            for symbol in special_version_records:
                expected_crc = record.imports[symbol]
                candidates = providers.get(symbol, [])
                namespace_compatible = [
                    entry
                    for entry in candidates
                    if not entry.namespace or entry.namespace in record.import_namespaces
                ]
                matching = [entry for entry in namespace_compatible if entry.crc == expected_crc]
                if matching:
                    result = "MATCH"
                    crc_matches += 1
                elif candidates and not namespace_compatible:
                    result = "NAMESPACE_FAILURE"
                    namespace_failures += 1
                elif namespace_compatible:
                    result = "CRC_MISMATCH"
                    mismatches += 1
                else:
                    result = "MISSING"
                    unresolved += 1
                dependency_rows.append(
                    {
                        "partition": partition,
                        "consumer": record.name,
                        "load_mode": load_mode,
                        "symbol": symbol,
                        "binding": "SPECIAL",
                        "weak": "no",
                        "has_modversions_record": "yes",
                        "expected_crc": f"0x{expected_crc:08x}",
                        "matching_provider": ",".join(sorted(entry.label for entry in matching)),
                        "candidate_crcs": ",".join(
                            sorted({f"0x{entry.crc:08x}" for entry in candidates})
                        ),
                        "candidate_namespaces": ",".join(
                            sorted({entry.namespace or "<none>" for entry in candidates})
                        ),
                        "result": result,
                        "controlled_provider": "no",
                    }
                )

            aggregate["undefined"] += len(named_undefined)
            aggregate["hard_required"] += len(hard_required)
            aggregate["weak"] += len(weak_imports)
            aggregate["versioned"] += len(versioned_imports)
            aggregate["nonversioned_required"] += len(nonversioned_required)
            aggregate["special_version_records"] += len(special_version_records)
            aggregate["resolved"] += resolved
            aggregate["crc_matches"] += crc_matches
            aggregate["missing"] += unresolved
            aggregate["crc_mismatches"] += mismatches
            aggregate["namespace_failures"] += namespace_failures
            aggregate["provider_ambiguities"] += provider_ambiguities

            if partition == focus_partition and record.name == focus_module:
                focus_found = True
                raw_symbols = ELF.ElfModule(record.path).undefined_symbols(include_null=True)
                for index, undefined in enumerate(raw_symbols, 1):
                    symbol = undefined.name
                    expected_crc = record.imports.get(symbol) if symbol else None
                    candidates = providers.get(symbol, []) if symbol else []
                    namespace_compatible = [
                        entry
                        for entry in candidates
                        if not entry.namespace or entry.namespace in record.import_namespaces
                    ]
                    matching = (
                        [entry for entry in namespace_compatible if entry.crc == expected_crc]
                        if expected_crc is not None
                        else namespace_compatible
                    )
                    if not symbol:
                        result = "TOOLCHAIN_SPECIAL_REFERENCE"
                        runtime_required = "no"
                    elif matching:
                        result = "MATCH"
                        runtime_required = "no" if undefined.weak else "yes"
                    elif candidates and not namespace_compatible:
                        result = "NAMESPACE_FAILURE"
                        runtime_required = "no" if undefined.weak else "yes"
                    elif namespace_compatible and expected_crc is not None:
                        result = "CRC_MISMATCH"
                        runtime_required = "no" if undefined.weak else "yes"
                    else:
                        result = "WEAK_UNRESOLVED" if undefined.weak else "MISSING"
                        runtime_required = "no" if undefined.weak else "yes"
                    reported_providers = matching if matching else candidates
                    undefined_rows.append(
                        {
                            "index": str(index),
                            "symbol": symbol or "<anonymous:STN_UNDEF>",
                            "binding": undefined.binding,
                            "visibility": undefined.visibility,
                            "symbol_type": undefined.symbol_type,
                            "ELF_undefined": "yes",
                            "has_MODVERSIONS_record": "yes" if expected_crc is not None else "no",
                            "expected_CRC": (
                                f"0x{expected_crc:08x}" if expected_crc is not None else ""
                            ),
                            "provider": ",".join(
                                sorted(entry.label for entry in reported_providers)
                            ),
                            "provider_kind": ",".join(
                                sorted(
                                    {
                                        "vmlinux"
                                        if entry.partition == "vmlinux"
                                        else "module"
                                        for entry in reported_providers
                                    }
                                )
                            ),
                            "provider_partition": ",".join(
                                sorted({entry.partition for entry in reported_providers})
                            ),
                            "weak": "yes" if undefined.weak else "no",
                            "runtime_required": runtime_required,
                            "candidate_present": "yes" if candidates else "no",
                            "candidate_CRC": ",".join(
                                sorted({f"0x{entry.crc:08x}" for entry in candidates})
                            ),
                            "result": result,
                            "notes": (
                                "mandatory ELF symbol-table entry zero; loader starts at symbol 1"
                                if not symbol
                                else "unresolved STB_WEAK is accepted only when no provider exists"
                                if undefined.weak and not candidates
                                else ""
                            ),
                        }
                    )

            if not active:
                classification = "DORMANT"
            elif (
                unresolved
                or mismatches
                or namespace_failures
                or protected_failures
                or vermagic_contract == "INCOMPATIBLE"
                or signing_contract == "UNKNOWN_SIGNER"
            ):
                classification = "BLOCKER"
            else:
                classification = "COMPATIBLE"

            totals[classification] += 1
            rows.append(
                {
                    "module": record.name,
                    "partition": partition,
                    "stock_path": str(record.path.relative_to(root)),
                    "load_mode": load_mode,
                    "classification": classification,
                    "vermagic": vermagic,
                    "vermagic_contract": vermagic_contract,
                    "signature": signer,
                    "signature_id": sig_id,
                    "signing_contract": signing_contract,
                    "imports": str(len(record.imports)),
                    "undefined_elf_symbols": str(len(named_undefined)),
                    "hard_required": str(len(hard_required)),
                    "weak_imports": str(len(weak_imports)),
                    "versioned_imports": str(len(versioned_imports)),
                    "nonversioned_required": str(len(nonversioned_required)),
                    "special_version_records": str(len(special_version_records)),
                    "resolved": str(resolved),
                    "crc_matches": str(crc_matches),
                    "unresolved_imports": str(unresolved),
                    "crc_mismatches": str(mismatches),
                    "namespace_failures": str(namespace_failures),
                    "provider_ambiguities": str(provider_ambiguities),
                    "protected_export_failures": str(protected_failures),
                    "release_token": release_token,
                    "reason": (
                        "not in a supported modules.load path"
                        if not active
                        else "all imports and CRCs resolve against the controlled candidate"
                        if classification == "COMPATIBLE"
                        else "active retained module violates the controlled Image contract"
                    ),
                }
            )

    header = [
        "module", "partition", "stock_path", "load_mode", "classification", "vermagic",
        "vermagic_contract", "signature", "signature_id", "signing_contract", "imports",
        "undefined_elf_symbols", "hard_required", "weak_imports", "versioned_imports",
        "nonversioned_required", "special_version_records", "resolved", "crc_matches",
        "unresolved_imports", "crc_mismatches", "namespace_failures", "provider_ambiguities",
        "protected_export_failures", "release_token",
        "reason",
    ]
    dependency_header = [
        "partition", "consumer", "load_mode", "symbol", "binding", "weak",
        "has_modversions_record", "expected_crc", "matching_provider", "candidate_crcs",
        "candidate_namespaces", "result", "controlled_provider",
    ]
    for path in (args.out, args.dependency_out, args.summary_out):
        path.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=header, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    with args.dependency_out.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=dependency_header, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(dependency_rows)
    if args.provider_out:
        args.provider_out.parent.mkdir(parents=True, exist_ok=True)
        provider_header = [
            "symbol", "provider", "partition", "export_class", "namespace",
            "provider_sha256", "source_available", "notes",
        ]
        with args.provider_out.open("w", encoding="utf-8", newline="") as output:
            writer = csv.DictWriter(
                output, fieldnames=provider_header, delimiter="\t", lineterminator="\n"
            )
            writer.writeheader()
            for symbol in sorted(providers):
                for provider in providers[symbol]:
                    writer.writerow(
                        {
                            "symbol": symbol,
                            "provider": provider.name,
                            "partition": provider.partition,
                            "export_class": provider.export_class,
                            "namespace": provider.namespace,
                            "provider_sha256": provider.sha256,
                            "source_available": "yes" if provider.partition == "vmlinux" else "unknown",
                            "notes": "actual __ksymtab export" if provider.partition != "vmlinux" else "exact candidate Module.symvers export",
                        }
                    )
    if args.undefined_out:
        if not focus_found:
            die(f"focus module not found: {args.focus_module}")
        args.undefined_out.parent.mkdir(parents=True, exist_ok=True)
        undefined_header = [
            "index", "symbol", "binding", "visibility", "symbol_type", "ELF_undefined",
            "has_MODVERSIONS_record", "expected_CRC", "provider", "provider_kind",
            "provider_partition", "weak", "runtime_required", "candidate_present",
            "candidate_CRC", "result", "notes",
        ]
        with args.undefined_out.open("w", encoding="utf-8", newline="") as output:
            writer = csv.DictWriter(
                output, fieldnames=undefined_header, delimiter="\t", lineterminator="\n"
            )
            writer.writeheader()
            writer.writerows(undefined_rows)
    args.summary_out.write_text(
        "\n".join(
            [
                "RETAINED STOCK MODULE CONTRACT",
                f"kernel_release={args.kernel_release}",
                f"expected_vermagic={args.expected_vermagic}",
                f"compatible={totals['COMPATIBLE']}",
                f"dormant={totals['DORMANT']}",
                f"blocker={totals['BLOCKER']}",
                f"undefined_elf_symbols={aggregate['undefined']}",
                f"hard_required={aggregate['hard_required']}",
                f"weak={aggregate['weak']}",
                f"versioned_imports={aggregate['versioned']}",
                f"nonversioned_required={aggregate['nonversioned_required']}",
                f"special_version_records={aggregate['special_version_records']}",
                f"resolved={aggregate['resolved']}",
                f"missing={aggregate['missing']}",
                f"crc_matches={aggregate['crc_matches']}",
                f"crc_mismatches={aggregate['crc_mismatches']}",
                f"namespace_failures={aggregate['namespace_failures']}",
                f"provider_ambiguities={aggregate['provider_ambiguities']}",
                f"result={'PASS' if not totals['BLOCKER'] else 'FAIL'}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(args.summary_out.read_text(encoding="utf-8"), end="")
    return 0 if not totals["BLOCKER"] else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2)

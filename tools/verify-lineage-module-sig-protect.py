#!/usr/bin/env python3
"""Audit unsigned stock modules against the candidate protected-export set.

``CONFIG_MODULE_SIG_PROTECT`` permits unsigned modules, but rejects one that
exports a symbol belonging to a protected GKI module.  This check reconstructs
the exact protected symbol set from the candidate common modules and applies
the loader rule to every retained stock module on an active load path.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import sys
from pathlib import Path


SIGNATURE_MAGIC = b"~Module signature appended~\n"


def load_elf_helpers():
    path = Path(__file__).with_name("validate-matched-wlan-vendor-dlkm.py")
    spec = importlib.util.spec_from_file_location("lineage_sig_protect_elf", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ELF = load_elf_helpers()


def assignment(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("root must be PARTITION=PATH")
    partition, raw_path = value.split("=", 1)
    path = Path(raw_path).resolve()
    if not partition or not path.is_dir():
        raise argparse.ArgumentTypeError(f"invalid root: {value}")
    return partition, path


def canonical(name: str) -> str:
    return Path(name).name.removesuffix(".ko").replace("-", "_")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protected-module-list", type=Path, required=True)
    parser.add_argument("--candidate-common-root", type=Path, required=True)
    parser.add_argument("--stock-root", action="append", type=assignment, required=True)
    parser.add_argument("--stock-contract", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args()

    if args.report.exists() or args.summary.exists():
        parser.error("refusing to overwrite an existing report")
    for path in (args.protected_module_list, args.stock_contract):
        if not path.is_file():
            parser.error(f"missing input: {path}")
    common_root = args.candidate_common_root.resolve()
    if not common_root.is_dir():
        parser.error(f"candidate common root is not a directory: {common_root}")

    requested = {
        canonical(line.strip())
        for line in args.protected_module_list.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    common = ELF.scan_root(common_root, "common", "CANDIDATE_COMMON")
    missing_protected_modules = sorted(requested - set(common))
    protected_symbols: dict[str, str] = {}
    for name in sorted(requested & set(common)):
        for symbol in common[name].export_records:
            prior = protected_symbols.setdefault(symbol, name)
            if prior != name:
                raise SystemExit(
                    f"protected symbol {symbol} exported by both {prior} and {name}"
                )

    contract: dict[tuple[str, str], dict[str, str]] = {}
    with args.stock_contract.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        required = {"partition", "module", "load_mode"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise SystemExit("stock contract is missing partition/module/load_mode")
        for row in reader:
            contract[(row["partition"], canonical(row["module"]))] = row

    rows: list[list[str]] = []
    active_unsigned = 0
    dormant_unsigned = 0
    signed = 0
    failures = len(missing_protected_modules)
    missing_contract = 0
    for partition, root in args.stock_root:
        records = ELF.scan_root(root, partition, "RETAINED_STOCK")
        for name, record in sorted(records.items()):
            policy = contract.get((partition, name))
            if policy is None:
                missing_contract += 1
                failures += 1
                load_mode = "UNKNOWN"
            else:
                load_mode = policy["load_mode"]
            is_signed = record.path.read_bytes().endswith(SIGNATURE_MAGIC)
            if is_signed:
                signed += 1
                result = "SIGNED_AUDITED_SEPARATELY"
                overlap: list[str] = []
            elif load_mode == "DORMANT":
                dormant_unsigned += 1
                result = "DORMANT_UNSIGNED"
                overlap = []
            else:
                active_unsigned += 1
                overlap = sorted(set(record.export_records) & set(protected_symbols))
                result = "FAIL" if overlap else "PASS"
                if overlap:
                    failures += 1
            rows.append(
                [
                    partition,
                    name,
                    load_mode,
                    "yes" if is_signed else "no",
                    str(len(record.export_records)),
                    str(len(overlap)),
                    ",".join(overlap),
                    result,
                ]
            )

    args.report.parent.mkdir(parents=True, exist_ok=True)
    with args.report.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(
            [
                "partition",
                "module",
                "load_mode",
                "signed",
                "exports",
                "protected_export_overlaps",
                "overlapping_symbols",
                "result",
            ]
        )
        writer.writerows(rows)

    summary = (
        "LINEAGE MODULE_SIG_PROTECT CONTRACT\n"
        f"protected_modules={len(requested)}\n"
        f"missing_protected_modules={len(missing_protected_modules)}\n"
        f"protected_symbols={len(protected_symbols)}\n"
        f"signed_modules={signed}\n"
        f"active_unsigned_modules={active_unsigned}\n"
        f"dormant_unsigned_modules={dormant_unsigned}\n"
        f"missing_stock_contract_rows={missing_contract}\n"
        f"failures={failures}\n"
        f"result={'PASS' if failures == 0 else 'FAIL'}\n"
    )
    args.summary.write_text(summary, encoding="utf-8")
    print(summary, end="")
    if missing_protected_modules:
        print("missing=" + ",".join(missing_protected_modules))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

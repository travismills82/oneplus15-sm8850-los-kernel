#!/usr/bin/env python3
"""Cryptographically verify retained Lineage module signatures.

The ordinary ``modinfo signer`` field is metadata, not proof that a module's
PKCS#7 signature is accepted by the certificate compiled into the candidate.
This tool separates each Linux module's signed payload and detached CMS
message, then asks OpenSSL to verify the signature using only the supplied
Lineage public certificate.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import struct
import subprocess
import tempfile
from pathlib import Path


SIGNATURE_MAGIC = b"~Module signature appended~\n"


def parse_root(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("module root must be LABEL=PATH")
    label, raw_path = value.split("=", 1)
    path = Path(raw_path).resolve()
    if not label or not path.is_dir():
        raise argparse.ArgumentTypeError(f"invalid module root: {value}")
    return label, path


def split_signature(path: Path) -> tuple[bytes, bytes]:
    data = path.read_bytes()
    if not data.endswith(SIGNATURE_MAGIC):
        raise ValueError("signature magic absent")
    descriptor = len(data) - len(SIGNATURE_MAGIC) - 12
    if descriptor < 0:
        raise ValueError("truncated signature descriptor")
    _algo, _hash, id_type, signer_len, key_len, _pad, signature_len = struct.unpack(
        ">5B3sI", data[descriptor : descriptor + 12]
    )
    signature_start = descriptor - signature_len
    payload_end = signature_start - key_len - signer_len
    if id_type != 2 or signature_len == 0 or payload_end < 0:
        raise ValueError("invalid PKCS#7 signature trailer")
    return data[:payload_end], data[signature_start:descriptor]


def verify_signature(payload: bytes, signature: bytes, certificate: Path) -> str:
    with tempfile.TemporaryDirectory(prefix="lineage-module-signature-") as directory:
        root = Path(directory)
        payload_path = root / "module.unsigned"
        signature_path = root / "module.p7"
        payload_path.write_bytes(payload)
        signature_path.write_bytes(signature)
        result = subprocess.run(
            [
                "openssl",
                "cms",
                "-verify",
                "-binary",
                "-inform",
                "DER",
                "-in",
                str(signature_path),
                "-content",
                str(payload_path),
                "-certfile",
                str(certificate),
                "-noverify",
                "-out",
                "/dev/null",
            ],
            capture_output=True,
            text=True,
        )
    if result.returncode:
        detail = result.stderr.strip().replace("\t", " ").replace("\n", " | ")
        raise ValueError(detail or f"openssl cms exited {result.returncode}")
    return hashlib.sha256(payload).hexdigest()


def certificate_field(certificate: Path, option: str) -> str:
    result = subprocess.run(
        ["openssl", "x509", "-in", str(certificate), "-noout", option],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cert", type=Path, required=True)
    parser.add_argument("--module-root", action="append", type=parse_root, required=True)
    parser.add_argument("--expect-count", type=int)
    parser.add_argument("--expect-signed", type=int)
    parser.add_argument(
        "--require-signed-label",
        action="append",
        default=[],
        help="fail if any module under this LABEL has no PKCS#7 trailer",
    )
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args()

    certificate = args.cert.resolve()
    if not certificate.is_file():
        parser.error(f"certificate not found: {certificate}")
    if args.report.exists() or args.summary.exists():
        parser.error("refusing to overwrite an existing report")

    modules: list[tuple[str, Path, Path]] = []
    for label, root in args.module_root:
        modules.extend((label, root, path) for path in sorted(root.rglob("*.ko")))
    if args.expect_count is not None and len(modules) != args.expect_count:
        raise SystemExit(f"module count {len(modules)} != expected {args.expect_count}")

    rows: list[list[str]] = []
    failures = 0
    signed = 0
    verified = 0
    unsigned = 0
    for label, root, path in modules:
        data = path.read_bytes()
        if not data.endswith(SIGNATURE_MAGIC):
            unsigned += 1
            payload_sha256 = hashlib.sha256(data).hexdigest()
            if label in args.require_signed_label:
                result, detail = "FAIL", "signature required for partition"
                failures += 1
            else:
                result, detail = "UNSIGNED", "no CMS trailer; policy audited separately"
        else:
            signed += 1
            try:
                payload, signature = split_signature(path)
                payload_sha256 = verify_signature(payload, signature, certificate)
                result, detail = "PASS", ""
                verified += 1
            except (OSError, ValueError, subprocess.SubprocessError) as error:
                payload_sha256 = ""
                result, detail = "FAIL", str(error).replace("\t", " ").replace("\n", " | ")
                failures += 1
        rows.append(
            [
                label,
                str(path.relative_to(root)),
                str(path.stat().st_size),
                hashlib.sha256(data).hexdigest(),
                payload_sha256,
                result,
                detail,
            ]
        )

    args.report.parent.mkdir(parents=True, exist_ok=True)
    with args.report.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(
            [
                "partition",
                "module",
                "size",
                "signed_sha256",
                "payload_sha256",
                "cms_verification",
                "detail",
            ]
        )
        writer.writerows(rows)

    serial = certificate_field(certificate, "-serial")
    fingerprint = certificate_field(certificate, "-fingerprint")
    if args.expect_signed is not None and signed != args.expect_signed:
        failures += 1
    summary = (
        "LINEAGE STOCK MODULE SIGNATURE VERIFICATION\n"
        f"certificate={certificate}\n"
        f"{serial}\n"
        f"{fingerprint}\n"
        f"modules={len(modules)}\n"
        f"signed={signed}\n"
        f"verified={verified}\n"
        f"unsigned={unsigned}\n"
        f"failures={failures}\n"
        f"result={'PASS' if failures == 0 else 'FAIL'}\n"
    )
    args.summary.write_text(summary, encoding="utf-8")
    print(summary, end="")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

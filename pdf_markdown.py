#!/usr/bin/env python3
"""PDF → Markdown converter using docling.

Lays a `.md` next to every `.pdf` (same stem, sibling file).  Skips PDFs that
already have a newer `.md` unless `--force` is passed.

Usage:
    uv run tools/pdf_markdown.py [--force] <pdf-or-dir> [<pdf-or-dir> ...]

Examples:
    uv run tools/pdf_markdown.py docs/ideas/Lightmaps2024/
    uv run tools/pdf_markdown.py --force docs/ideas/Lightmaps2024/HemiLighting-1.pdf
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Force UTF-8 stdout/stderr on Windows — the default cp1252 codec can't encode
# many Unicode characters that docling emits (→, ≥, etc.).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def convert_one(pdf: Path, force: bool, formula_enrichment: bool) -> int:
    if not pdf.is_file() or pdf.suffix.lower() != ".pdf":
        print(f"skip (not a pdf): {pdf}", file=sys.stderr)
        return 0
    md = pdf.with_suffix(".md")
    if md.exists() and md.stat().st_mtime >= pdf.stat().st_mtime and not force:
        print(f"up-to-date: {md}")
        return 0
    # Lazy import — docling is heavy and only needed when we actually convert.
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions

    pipe_opts = PdfPipelineOptions(do_formula_enrichment=formula_enrichment)
    converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipe_opts)}
    )
    t0 = time.perf_counter()
    result = converter.convert(pdf)
    md_text = result.document.export_to_markdown()
    md.write_text(md_text, encoding="utf-8")
    print(f"  {pdf} -> {md} ({len(md_text)} chars, {time.perf_counter() - t0:.1f} s)")
    return 1


def iter_pdfs(args: list[Path]) -> list[Path]:
    out: list[Path] = []
    for a in args:
        if a.is_dir():
            out.extend(sorted(a.rglob("*.pdf")))
        elif a.is_file():
            out.append(a)
        else:
            print(f"skip (not found): {a}", file=sys.stderr)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "inputs",
        nargs="+",
        type=Path,
        help="PDF files or directories to convert (recursively).",
    )
    ap.add_argument(
        "--force",
        action="store_true",
        help="Re-convert even if the .md is newer than the .pdf.",
    )
    ap.add_argument(
        "--no-formulas",
        action="store_true",
        help="Disable LaTeX formula enrichment (faster, but formulas are lost). "
        "Formula enrichment uses the CodeFormulaV2 VLM, which downloads a "
        "~1 GB model on first run.",
    )
    args = ap.parse_args()
    pdfs = iter_pdfs(args.inputs)
    if not pdfs:
        print("no pdfs found", file=sys.stderr)
        return 1
    n = 0
    for pdf in pdfs:
        try:
            n += convert_one(pdf, args.force, formula_enrichment=not args.no_formulas)
        except Exception as e:
            print(f"FAIL {pdf}: {e}", file=sys.stderr)
    print(f"converted {n}/{len(pdfs)} pdf(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

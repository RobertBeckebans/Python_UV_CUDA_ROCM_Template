#!/usr/bin/env python3
"""PDF → Markdown converter using docling.

Lays a `.md` next to every `.pdf` (same stem, sibling file).  Skips PDFs that
already have a newer `.md` unless `--force` is passed.

With `--images referenced`, figures are written as PNGs into a sibling
`<stem>_artifacts/` folder and linked from the Markdown; `--images embedded`
inlines them as base64 data URIs instead.

Usage:
    uv run tools/pdf_markdown.py [--force] <pdf-or-dir> [<pdf-or-dir> ...]

Examples:
    uv run tools/pdf_markdown.py docs/ideas/Lightmaps2024/
    uv run tools/pdf_markdown.py --force docs/ideas/Lightmaps2024/HemiLighting-1.pdf
    uv run tools/pdf_markdown.py --images referenced docs/ideas/Lightmaps2024/
"""

from __future__ import annotations

import argparse
import sys
import time
from functools import cache
from pathlib import Path

# Force UTF-8 stdout/stderr on Windows — the default cp1252 codec can't encode
# many Unicode characters that docling emits (→, ≥, etc.).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


@cache
def get_converter(formula_enrichment: bool, images: bool, image_scale: float):
    # Lazy import — docling is heavy and only needed when we actually convert.
    # Cached so the layout/OCR/formula models are loaded once, not per PDF.
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions

    pipe_opts = PdfPipelineOptions(
        do_formula_enrichment=formula_enrichment,
        generate_picture_images=images,
        images_scale=image_scale,
    )
    return DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipe_opts)}
    )


def convert_one(
    pdf: Path, force: bool, formula_enrichment: bool, images: str, image_scale: float
) -> int:
    if not pdf.is_file() or pdf.suffix.lower() != ".pdf":
        print(f"skip (not a pdf): {pdf}", file=sys.stderr)
        return 0
    md = pdf.with_suffix(".md")
    if md.exists() and md.stat().st_mtime >= pdf.stat().st_mtime and not force:
        print(f"up-to-date: {md}")
        return 0
    from docling_core.types.doc import ImageRefMode

    converter = get_converter(formula_enrichment, images != "none", image_scale)
    t0 = time.perf_counter()
    result = converter.convert(pdf)
    image_mode = {
        "none": ImageRefMode.PLACEHOLDER,
        "referenced": ImageRefMode.REFERENCED,
        "embedded": ImageRefMode.EMBEDDED,
    }[images]
    # Writes the PNGs to <stem>_artifacts/ next to the .md in referenced mode.
    # The dir must be passed relative, otherwise docling writes absolute links.
    result.document.save_as_markdown(
        md, artifacts_dir=Path(f"{md.stem}_artifacts"), image_mode=image_mode
    )
    n_pics = len(result.document.pictures)
    print(
        f"  {pdf} -> {md} ({md.stat().st_size} bytes, {n_pics} picture(s), "
        f"{time.perf_counter() - t0:.1f} s)"
    )
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
    ap.add_argument(
        "--images",
        choices=("none", "referenced", "embedded"),
        default="none",
        help="How to handle pictures: 'none' leaves an <!-- image --> "
        "placeholder (default), 'referenced' writes PNGs to <stem>_artifacts/ "
        "and links them, 'embedded' inlines them as base64.",
    )
    ap.add_argument(
        "--image-scale",
        type=float,
        default=2.0,
        help="Render scale for extracted pictures (1.0 = 72 dpi, default 2.0 = 144 dpi).",
    )
    args = ap.parse_args()
    pdfs = iter_pdfs(args.inputs)
    if not pdfs:
        print("no pdfs found", file=sys.stderr)
        return 1
    n = 0
    for pdf in pdfs:
        try:
            n += convert_one(
                pdf,
                args.force,
                formula_enrichment=not args.no_formulas,
                images=args.images,
                image_scale=args.image_scale,
            )
        except Exception as e:
            print(f"FAIL {pdf}: {e}", file=sys.stderr)
    print(f"converted {n}/{len(pdfs)} pdf(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

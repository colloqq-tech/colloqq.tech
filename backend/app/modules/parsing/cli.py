from __future__ import annotations

import argparse
import json
import logging
import re
from pathlib import Path

import pypdfium2 as pdfium # type: ignore
from pdftext.extraction import dictionary_output # type: ignore

from .config import DEFAULT_BOTTOM_PAD, DEFAULT_DPI, DEFAULT_KEYWORDS, DEFAULT_TOP_PAD
from .segmenter import Segmenter

logger = logging.getLogger("notesplit")


def slugify(title: str, index: int) -> str:
    """Преобразует заголовок в slug"""

    chars = [char if char.isalnum() else "-" for char in title.lower()]
    slug = re.sub(r"-+", "-", "".join(chars)).strip("-")

    return f"{index:02d}-{slug or 'block'}"


def export_page(segmenter: Segmenter, page, pdf_page, out_dir: Path) -> list[dict]:
    """Экспортирует страницу в изображения и возвращает список записей"""

    page_number = page["page"] + 1
    blocks = segmenter.segment(page)

    if not blocks:
        logger.info("page %d: no text found, skipped", page_number)
        return []

    records: list[dict] = []

    for index, rendered in enumerate(segmenter.render(blocks, pdf_page), start=1):
        filename = f"p{page_number:02d}-{slugify(rendered.block.title, index)}.png"
        rendered.image.save(out_dir / filename)

        records.append(
            {
                "page": page_number,
                "title": rendered.block.title,
                "titled": rendered.block.titled,
                "file": filename,
                "top": rendered.scope.top,
                "bottom": rendered.scope.bottom,
                "box": list(rendered.box),
            }
        )

        logger.info(
            "page %d: %-24s y[%d:%d] -> %s",
            page_number,
            rendered.block.title,
            rendered.scope.top,
            rendered.scope.bottom,
            filename,
        )

    return records


def parse_page_ranges(spec: str | None, total: int) -> list[int]:
    """Разбирает диапазон страниц, возращает список индексов страниц"""

    if not spec:
        return list(range(total))

    pages: list[int] = []

    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-")
            pages.extend(range(int(start) - 1, int(end)))
        elif part:
            pages.append(int(part) - 1)

    return [page for page in pages if 0 <= page < total]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path, help="path to the pdf")
    parser.add_argument("-o", "--out", type=Path, default=Path("blocks"), help="output")
    parser.add_argument("--dpi", type=int, default=DEFAULT_DPI, help="render dpi")
    parser.add_argument(
        "--keywords", nargs="*", default=list(DEFAULT_KEYWORDS), help="title keywords"
    )
    parser.add_argument(
        "--top-pad", type=int, default=DEFAULT_TOP_PAD, help="top padding, px"
    )
    parser.add_argument(
        "--bottom-pad", type=int, default=DEFAULT_BOTTOM_PAD, help="bottom padding, px"
    )
    parser.add_argument("--pages", type=str, default=None, help="page range,")
    parser.add_argument("--json", type=Path, default=None, help="block manifest")

    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    args = parse_args()

    if not args.pdf.exists():
        raise SystemExit(f"file not found: {args.pdf}")

    args.out.mkdir(parents=True, exist_ok=True)
    document = pdfium.PdfDocument(str(args.pdf))
    page_indices = parse_page_ranges(args.pages, len(document))
    pages = dictionary_output(str(args.pdf), page_range=page_indices)

    segmenter = Segmenter(
        keywords=args.keywords,
        dpi=args.dpi,
        top_pad=args.top_pad,
        bottom_pad=args.bottom_pad,
    )

    manifest: list[dict] = []

    for page in pages:
        manifest.extend(export_page(segmenter, page, document[page["page"]], args.out))

    if args.json:
        args.json.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        logger.info("manifest: %s", args.json)

    logger.info("done: %d block(s) saved to %s/", len(manifest), args.out)


if __name__ == "__main__":
    main()

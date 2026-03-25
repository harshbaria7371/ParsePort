from __future__ import annotations

import json
import logging
from pathlib import Path

from models import OutputType, ParsedDocument


logger = logging.getLogger(__name__)


def write_output(
    document: ParsedDocument,
    output_path: Path,
    output_type: OutputType,
) -> None:
    """Write the parsed document in the requested output format."""
    if output_type is OutputType.TEXT:
        _write_text_output(document, output_path)
    elif output_type is OutputType.JSON:
        _write_json_output(document, output_path)
    else:  # pragma: no cover - guarded by argument parsing
        raise ValueError(f"Unsupported output type: {output_type}")


def _write_text_output(document: ParsedDocument, output_path: Path) -> None:
    banner = f"[pdf_type={document.pdf_type.value}] {document.pdf_path.name}"

    field_lines = [
        f"{key}: {value}"
        for key, value in sorted(document.fields.items())
        if value.strip()
    ]

    meta_block = ""
    if field_lines:
        meta_block = "\n".join(field_lines) + "\n"

    separator = "\n" + "=" * len(banner) + "\n\n"
    joined_pages = "\n\n".join(document.pages_text)
    content = banner + "\n" + meta_block + separator + joined_pages

    try:
        output_path.write_text(content, encoding="utf-8")
        logger.info("Wrote plain text output to '%s'", output_path)
    except OSError as exc:
        logger.error("Failed to write text output '%s': %s", output_path, exc)
        raise


def _write_json_output(document: ParsedDocument, output_path: Path) -> None:
    payload = {
        "pdf_path": str(document.pdf_path),
        "pdf_type": document.pdf_type.value,
        "page_count": len(document.pages_text),
        "fields": document.fields,
        "pages": [
            {
                "index": index,
                "text": text,
            }
            for index, text in enumerate(document.pages_text)
        ],
    }

    try:
        output_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.info("Wrote JSON output to '%s'", output_path)
    except OSError as exc:
        logger.error("Failed to write JSON output '%s': %s", output_path, exc)
        raise


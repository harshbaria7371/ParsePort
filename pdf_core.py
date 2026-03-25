from __future__ import annotations

import logging
from pathlib import Path
from typing import List

from pypdf import PdfReader
from pypdf.errors import PdfReadError


logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: Path) -> List[str]:
    """
    Extract text from all pages of a PDF.

    Returns a list where each entry corresponds to the text of a page.
    """
    logger.debug("Starting text extraction from PDF '%s'", pdf_path)

    try:
        reader = PdfReader(str(pdf_path))
    except PdfReadError as exc:
        logger.error("Failed to read PDF '%s': %s", pdf_path, exc)
        raise
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("Unexpected error opening PDF '%s': %s", pdf_path, exc)
        raise

    pages_text: List[str] = []
    for index, page in enumerate(reader.pages):
        try:
            text = page.extract_text() or ""
            logger.debug("Extracted %d characters from page %d", len(text), index)
            pages_text.append(text)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning(
                "Failed to extract text from page %d of '%s': %s",
                index,
                pdf_path,
                exc,
            )
            pages_text.append("")

    logger.info(
        "Completed text extraction from '%s' (%d pages)", pdf_path, len(pages_text)
    )
    return pages_text


from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from document_types import DocumentType
from models import ExtractionConfig, OutputType
from output_writer import write_output
from parsers import get_parser_for_type


def configure_logging(verbosity: int) -> None:
    """
    Configure root logger based on verbosity level.

    0 -> WARNING
    1 -> INFO
    2+ -> DEBUG
    """
    if verbosity <= 0:
        level = logging.WARNING
    elif verbosity == 1:
        level = logging.INFO
    else:
        level = logging.DEBUG

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extract text from a PDF file. The behaviour depends on the declared PDF type "
            "(invoice, credit_note, resume, ...)."
        )
    )
    parser.add_argument(
        "pdf_path",
        type=str,
        help="Path to the source PDF file.",
    )
    parser.add_argument(
        "pdf_type",
        type=str,
        help="Logical type of the PDF (e.g. 'invoice', 'credit_note', 'resume').",
    )
    parser.add_argument(
        "output_path",
        type=str,
        help="Path to the output file (will be created or overwritten).",
    )
    parser.add_argument(
        "--output-type",
        "-t",
        dest="output_type",
        choices=[t.value for t in OutputType],
        default=OutputType.TEXT.value,
        help="Output format: 'text' for plain text, 'json' for structured JSON (default: text).",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        dest="verbosity",
        action="count",
        default=0,
        help="Increase verbosity (can be used multiple times).",
    )

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    configure_logging(args.verbosity)

    logger = logging.getLogger(__name__)

    pdf_path = Path(args.pdf_path).expanduser().resolve()
    output_path = Path(args.output_path).expanduser().resolve()

    try:
        pdf_type = DocumentType.from_string(args.pdf_type)
        output_type = OutputType.from_string(args.output_type)

        config = ExtractionConfig(
            pdf_path=pdf_path,
            pdf_type=pdf_type,
            output_path=output_path,
            output_type=output_type,
        )
        config.validate()

        parser = get_parser_for_type(config.pdf_type, config.pdf_path)
        parsed_document = parser.parse()
        write_output(parsed_document, config.output_path, config.output_type)
    except ValueError as exc:
        logger.error("%s", exc)
        return 2
    except Exception as exc:  # pragma: no cover - top-level safety net
        logger.exception("Unexpected error: %s", exc)
        return 1

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())


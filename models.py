from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List

from document_types import DocumentType


class OutputType(str, Enum):
    """Supported output formats for extracted data."""

    TEXT = "text"
    JSON = "json"

    @classmethod
    def from_string(cls, value: str) -> "OutputType":
        normalized = value.strip().lower()
        try:
            return cls(normalized)
        except ValueError as exc:
            supported = ", ".join(sorted(t.value for t in cls))
            raise ValueError(
                f"Unsupported output type '{value}'. Supported types are: {supported}."
            ) from exc


@dataclass(frozen=True)
class ExtractionConfig:
    """Configuration for a single PDF extraction run."""

    pdf_path: Path
    pdf_type: DocumentType
    output_path: Path
    output_type: OutputType

    def validate(self) -> None:
        """Validate configuration and raise ValueError on problems."""
        if not self.pdf_path.exists():
            raise ValueError(f"PDF file does not exist: {self.pdf_path}")
        if not self.pdf_path.is_file():
            raise ValueError(f"PDF path is not a file: {self.pdf_path}")

        # Disallow using a directory as the output "file" path
        if self.output_path.exists() and self.output_path.is_dir():
            raise ValueError(
                f"Output path '{self.output_path}' is a directory. "
                "Please provide a file path, for example: 'output/result.json'."
            )

        parent = self.output_path.parent
        if parent and not parent.exists():
            try:
                parent.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                raise ValueError(
                    f"Unable to create output directory '{parent}': {exc}"
                ) from exc


@dataclass(frozen=True)
class ParsedDocument:
    """Structured representation of an extracted PDF."""

    pdf_path: Path
    pdf_type: DocumentType
    pages_text: List[str]
    # Normalised, type-specific fields (e.g. invoice_number, buyer_info, total_ttc).
    fields: Dict[str, str]


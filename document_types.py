from __future__ import annotations

from enum import Enum


class DocumentType(str, Enum):
    """Supported high-level PDF document types."""

    INVOICE = "invoice"
    CREDIT_NOTE = "credit_note"
    RESUME = "resume"

    @classmethod
    def from_string(cls, value: str) -> "DocumentType":
        """Parse a string into a DocumentType, raising ValueError if unsupported."""
        normalized = value.strip().lower().replace(" ", "_")
        try:
            return cls(normalized)
        except ValueError as exc:
            supported = ", ".join(sorted(t.value for t in cls))
            raise ValueError(
                f"Unsupported pdf type '{value}'. Supported types are: {supported}."
            ) from exc


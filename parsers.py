from __future__ import annotations

import logging
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List

from document_types import DocumentType
from models import ParsedDocument
from pdf_core import extract_text_from_pdf


logger = logging.getLogger(__name__)


class BaseParser(ABC):
    """Base class for all PDF-type specific parsers."""

    def __init__(self, pdf_path: Path) -> None:
        self.pdf_path = pdf_path

    @property
    @abstractmethod
    def document_type(self) -> DocumentType:
        """Return the DocumentType handled by this parser."""

    @abstractmethod
    def parse(self) -> ParsedDocument:
        """Parse the PDF into a ParsedDocument."""


class InvoiceParser(BaseParser):
    """Parser for invoice PDFs."""

    @property
    def document_type(self) -> DocumentType:
        return DocumentType.INVOICE

    def parse(self) -> ParsedDocument:
        logger.info("Running InvoiceParser on '%s'", self.pdf_path)
        pages_text = extract_text_from_pdf(self.pdf_path)
        fields = _extract_invoice_fields(pages_text)
        return ParsedDocument(
            pdf_path=self.pdf_path,
            pdf_type=self.document_type,
            pages_text=pages_text,
            fields=fields,
        )


class CreditNoteParser(BaseParser):
    """Parser for credit note PDFs."""

    @property
    def document_type(self) -> DocumentType:
        return DocumentType.CREDIT_NOTE

    def parse(self) -> ParsedDocument:
        logger.info("Running CreditNoteParser on '%s'", self.pdf_path)
        pages_text = extract_text_from_pdf(self.pdf_path)
        fields = _extract_credit_note_fields(pages_text)
        return ParsedDocument(
            pdf_path=self.pdf_path,
            pdf_type=self.document_type,
            pages_text=pages_text,
            fields=fields,
        )


class ResumeParser(BaseParser):
    """Parser for resume PDFs."""

    @property
    def document_type(self) -> DocumentType:
        return DocumentType.RESUME

    def parse(self) -> ParsedDocument:
        logger.info("Running ResumeParser on '%s'", self.pdf_path)
        pages_text = extract_text_from_pdf(self.pdf_path)
        # Extend here with resume-specific NLP or field extraction.
        return ParsedDocument(
            pdf_path=self.pdf_path,
            pdf_type=self.document_type,
            pages_text=pages_text,
            fields={},
        )


def get_parser_for_type(pdf_type: DocumentType, pdf_path: Path) -> BaseParser:
    """Factory that returns the appropriate parser for the given document type."""
    if pdf_type is DocumentType.INVOICE:
        return InvoiceParser(pdf_path)
    if pdf_type is DocumentType.CREDIT_NOTE:
        return CreditNoteParser(pdf_path)
    if pdf_type is DocumentType.RESUME:
        return ResumeParser(pdf_path)

    # This should not be reachable as long as DocumentType and this function stay in sync.
    raise ValueError(f"No parser registered for document type: {pdf_type}")


def _extract_invoice_fields(pages_text: List[str]) -> Dict[str, str]:
    """
    Extract structured invoice fields such as seller, buyer, dates and totals.

    The implementation uses simple, regex-based heuristics designed to be easy
    to adapt as you encounter more invoice layouts.
    """
    text = "\n".join(pages_text)
    first_page_lines = pages_text[0].splitlines() if pages_text else []

    fields: Dict[str, str] = {}

    # Seller / buyer info heuristics (based on typical top-of-invoice layout)
    seller_lines: List[str] = []
    buyer_lines: List[str] = []
    buyer_started = False

    for line in first_page_lines:
        stripped = line.strip()
        if not stripped:
            # keep going until we have at least some content
            if not seller_lines and not buyer_started:
                continue

        # Heuristic: buyer block often starts with a "M." / "Mr" / name-like pattern
        if not buyer_started and (
            stripped.startswith("M.")
            or stripped.lower().startswith("mr ")
            or stripped.lower().startswith("mme ")
            or stripped.lower().startswith("monsieur")
        ):
            buyer_started = True

        if buyer_started:
            buyer_lines.append(stripped)
        else:
            seller_lines.append(stripped)

    if seller_lines:
        fields["seller_info"] = " ".join(seller_lines)
    if buyer_lines:
        fields["buyer_info"] = " ".join(buyer_lines)

    # Invoice number – e.g. "FACTURE n° FAC30"
    match = re.search(
        r"FACTURE\s*n[°o]?\s*(?P<number>\S+)", text, flags=re.IGNORECASE
    )
    if match:
        fields["invoice_number"] = match.group("number")

    # Invoice date – e.g. "... Du 21/01/2026"
    match = re.search(r"\bDu\s+(?P<date>\d{2}/\d{2}/\d{4})", text)
    if match:
        fields["invoice_date"] = match.group("date")

    # Due date – e.g. "Payable le 21/01/2026"
    match = re.search(
        r"Payable\s+le\s+(?P<date>\d{2}/\d{2}/\d{4})", text, flags=re.IGNORECASE
    )
    if match:
        fields["due_date"] = match.group("date")

    # Totals (French-style decimals with comma)
    match = re.search(r"Total HT\s+(?P<amount>\d+,\d{2})", text, flags=re.IGNORECASE)
    if match:
        fields["total_ht"] = match.group("amount")

    match = re.search(r"Total TVA\s+(?P<amount>\d+,\d{2})", text, flags=re.IGNORECASE)
    if match:
        fields["total_tva"] = match.group("amount")

    match = re.search(
        r"Total TTC\s+(?P<amount>\d+,\d{2})\s*€?", text, flags=re.IGNORECASE
    )
    if match:
        fields["total_ttc"] = match.group("amount")
        # Alias requested "Actual Amount" to the gross total
        fields["actual_amount"] = match.group("amount")

    return fields


def _extract_credit_note_fields(pages_text: List[str]) -> Dict[str, str]:
    """
    Extract structured credit note fields.

    This is a placeholder implementation using the same approach as invoices.
    As you gather real credit note samples, extend the regexes below.
    """
    text = "\n".join(pages_text)

    fields: Dict[str, str] = {}

    # Generic seller / buyer capture from first page, similar to invoices.
    first_page_lines = pages_text[0].splitlines() if pages_text else []
    seller_lines: List[str] = []
    buyer_lines: List[str] = []
    buyer_started = False

    for line in first_page_lines:
        stripped = line.strip()
        if not stripped:
            if not seller_lines and not buyer_started:
                continue

        if not buyer_started and (
            stripped.startswith("M.")
            or stripped.lower().startswith("mr ")
            or stripped.lower().startswith("mme ")
            or stripped.lower().startswith("monsieur")
        ):
            buyer_started = True

        if buyer_started:
            buyer_lines.append(stripped)
        else:
            seller_lines.append(stripped)

    if seller_lines:
        fields["seller_info"] = " ".join(seller_lines)
    if buyer_lines:
        fields["buyer_info"] = " ".join(buyer_lines)

    # Credit note number – adjust patterns as needed for your layout
    match = re.search(
        r"(AVOIR|CREDIT\s+NOTE)\s*n[°o]?\s*(?P<number>\S+)",
        text,
        flags=re.IGNORECASE,
    )
    if match:
        fields["credit_note_number"] = match.group("number")

    # Credit note date – look for "Du <date>" or "Date <date>"
    match = re.search(
        r"\b(Du|Date)\s+(?P<date>\d{2}/\d{2}/\d{4})", text, flags=re.IGNORECASE
    )
    if match:
        fields["credit_note_date"] = match.group("date")

    # Total credited amount
    match = re.search(
        r"Total\s+(?:Avoir|Crédit|TTC)\s+(?P<amount>\d+,\d{2})",
        text,
        flags=re.IGNORECASE,
    )
    if match:
        fields["total_credit_amount"] = match.group("amount")

    return fields

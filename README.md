## ParsePort

ParsePort is a high-performance text extraction engine designed to bridge the gap between static PDF documents and actionable data.

This simple Python CLI tool is inspired by projects like `pyresparser` (`https://github.com/OmkarPathak/pyresparser`) but focuses on **PDF text extraction** for different logical document types such as **invoice**, **credit note**, and **resume**.

### Features

- **PDF → Text extraction** using the battle-tested `pypdf` library
- **Type-aware parsing**:
  - `invoice` → handled by `InvoiceParser`
  - `credit_note` → handled by `CreditNoteParser`
  - `resume` → handled by `ResumeParser`
- **CLI interface** with clear arguments and exit codes
- **Two output formats**:
  - **text**: single UTF-8 `.txt` file containing all pages plus a header
  - **json**: structured JSON with metadata and one entry per page
- **Enterprise-friendly structure**:
  - isolated modules for document types, parsing, and output
  - strong typing, validation, and logging

### Project Layout

- `main.py` – CLI entry point
- `document_types.py` – enum of supported document types
- `models.py` – core dataclasses (`ExtractionConfig`, `ParsedDocument`, `OutputType`)
- `pdf_core.py` – low-level PDF text extraction using `pypdf`
- `parsers.py` – `BaseParser` and concrete parsers (`InvoiceParser`, `CreditNoteParser`, `ResumeParser`)
- `output_writer.py` – writing parsed data as text or JSON
- `requirements.txt` – Python dependencies

### Requirements

- **Python**: 3.9 or newer
- **Dependencies**: see `requirements.txt` (installed via `pip`)

### Installation

From the project root:

```bash
python -m venv .venv
.venv\Scripts\activate  # on Windows
pip install --upgrade pip
pip install -r requirements.txt
```

### Usage

Basic usage:

```bash
python main.py <PDF_PATH> <PDF_TYPE> <OUTPUT_PATH> [--output-type {text,json}] [-v|-vv]
```

#### Arguments

- **`pdf_path`** (positional): path to the source PDF file.
- **`pdf_type`** (positional): logical type of the PDF; one of:
  - `invoice`
  - `credit_note`
  - `resume`
- **`output_path`** (positional): path to the output file (will be created or overwritten).
- **`--output-type` / `-t`** (optional):
  - `text` – write a single plain-text file with a header and all pages (default).
  - `json` – write a JSON file with metadata and one entry per page.
- **`--verbose` / `-v`** (optional, repeatable):
  - no `-v`: warnings and errors only.
  - `-v`: info, warning, and error messages.
  - `-vv` (or more): debug-level logging.

#### Examples

- **Extract an invoice to JSON**:

```bash
python main.py "PDF Files/Facture_FAC30.pdf" invoice "output/facture.json" --output-type json -v
```

- **Extract a resume to plain text**:

```bash
python main.py "PDF Files/CandidateResume.pdf" resume "output/candidate.txt"
```

### Exit Codes

- **0** – success
- **2** – invalid user input (e.g., missing file, bad pdf type, directory used as output path)
- **1** – unexpected internal error

### Extending the Tool

To support a new PDF type (e.g., `purchase_order`):

- **Add a new value** to `DocumentType` in `document_types.py`.
- **Create a new parser** class in `parsers.py` that inherits from `BaseParser` and implements the `parse` method.
- **Register the parser** in `get_parser_for_type` within `parsers.py`.

This mirrors the modular structure of tools like `pyresparser` while remaining focused on PDF text extraction.

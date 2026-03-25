"""Resume parser: extracts text from PDF, DOCX, and TXT files."""

import os
from pathlib import Path

from app.config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB


def validate_file(file_path: str) -> None:
    """Validate file exists, has allowed extension, and is within size limit."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = path.suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type '{ext}'. Allowed: {ALLOWED_EXTENSIONS}")

    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise ValueError(f"File too large ({size_mb:.1f}MB). Max: {MAX_FILE_SIZE_MB}MB")


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file."""
    import pypdf
    reader = pypdf.PdfReader(file_path)
    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from a DOCX file."""
    import docx
    doc = docx.Document(file_path)
    return "\n".join(para.text for para in doc.paragraphs if para.text.strip())


def extract_text_from_txt(file_path: str) -> str:
    """Extract text from a plain text file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def extract_text(file_path: str) -> str:
    """Extract text from a resume file (PDF, DOCX, or TXT)."""
    validate_file(file_path)
    ext = Path(file_path).suffix.lower()

    extractors = {
        ".pdf": extract_text_from_pdf,
        ".docx": extract_text_from_docx,
        ".txt": extract_text_from_txt,
    }

    extractor = extractors.get(ext)
    if not extractor:
        raise ValueError(f"No extractor for file type: {ext}")

    text = extractor(file_path)
    if not text.strip():
        raise ValueError(f"No text could be extracted from: {file_path}")
    return text


def extract_text_from_bytes(content: bytes, filename: str) -> str:
    """Extract text from uploaded file bytes (for Streamlit uploads)."""
    import tempfile
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type '{ext}'. Allowed: {ALLOWED_EXTENSIONS}")

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        extractors = {
            ".pdf": extract_text_from_pdf,
            ".docx": extract_text_from_docx,
            ".txt": extract_text_from_txt,
        }
        text = extractors[ext](tmp_path)
        if not text.strip():
            raise ValueError(f"No text could be extracted from: {filename}")
        return text
    finally:
        os.unlink(tmp_path)

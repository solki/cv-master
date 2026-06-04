"""Text extraction from uploaded resume files.

Supports: .md, .txt, .pdf (PyPDF2), .docx (python-docx).
All extractors return (text: str | None, error: str | None).
"""

import io


async def extract_text(filename: str, content: bytes) -> tuple[str | None, str | None]:
    """Extract text from uploaded file content. Returns (text, error)."""
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""

    if ext in ("md", "txt"):
        return _extract_plain_text(content)

    if ext == "pdf":
        return _extract_pdf(content)

    if ext == "docx":
        return _extract_docx(content)

    return None, f"Unsupported file type: .{ext}"


def _extract_plain_text(content: bytes) -> tuple[str | None, str | None]:
    """Extract text from .md or .txt files."""
    try:
        text = content.decode("utf-8", errors="replace").strip()
        if not text:
            return None, "File is empty"
        return text, None
    except Exception as e:
        return None, f"Failed to decode text file: {str(e)}"


def _extract_pdf(content: bytes) -> tuple[str | None, str | None]:
    """Extract text from PDF using PyPDF2."""
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        return None, "PDF extraction is not available (PyPDF2 not installed)"

    try:
        reader = PdfReader(io.BytesIO(content))
        text_parts: list[str] = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        text = "\n\n".join(text_parts).strip()
        if not text:
            return None, "PDF file contains no extractable text (may be scanned image)"
        return text, None
    except Exception as e:
        return None, f"Failed to extract PDF text: {str(e)}"


def _extract_docx(content: bytes) -> tuple[str | None, str | None]:
    """Extract text from DOCX using python-docx."""
    try:
        from docx import Document
    except ImportError:
        return None, "DOCX extraction is not available (python-docx not installed)"

    try:
        doc = Document(io.BytesIO(content))
        text_parts: list[str] = []
        for para in doc.paragraphs:
            if para.text.strip():
                text_parts.append(para.text)
        text = "\n".join(text_parts).strip()
        if not text:
            return None, "DOCX file contains no text"
        return text, None
    except Exception as e:
        return None, f"Failed to extract DOCX text: {str(e)}"

"""Lightweight OCR using macOS Vision framework via ocrmac."""

import logging
from pathlib import Path

from ocrmac import ocrmac

logger = logging.getLogger("dailylens")

MAX_OCR_TEXT_LENGTH = 3000


def extract_text(image_path: Path) -> str:
    """Extract text from a screenshot using Apple Vision OCR.

    Returns extracted text, truncated to MAX_OCR_TEXT_LENGTH.
    """
    try:
        annotations = ocrmac.OCR(str(image_path)).recognize()
        # annotations is a list of (text, confidence, bbox)
        lines = [text for text, confidence, bbox in annotations if confidence > 0.3]
        full_text = "\n".join(lines)

        if len(full_text) > MAX_OCR_TEXT_LENGTH:
            full_text = full_text[:MAX_OCR_TEXT_LENGTH] + "\n..."

        return full_text

    except Exception as e:
        logger.error(f"OCR failed: {e}")
        return ""

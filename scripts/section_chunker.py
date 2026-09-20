"""Markdown section-aware chunking for the group retrieval experiment."""

from __future__ import annotations

import re

from src.chunking import RecursiveChunker


class SectionChunker:
    """Keep a Markdown heading attached to its section before recursive splitting."""

    def __init__(self, chunk_size: int = 500) -> None:
        self.chunk_size = chunk_size
        self._fallback = RecursiveChunker(chunk_size=chunk_size)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        sections = re.split(r"(?=^#{1,6}\s+)", text.strip(), flags=re.MULTILINE)
        chunks: list[str] = []
        for section in sections:
            section = section.strip()
            if not section:
                continue
            if len(section) <= self.chunk_size:
                chunks.append(section)
                continue

            heading_match = re.match(r"^(#{1,6}\s+[^\n]+)", section)
            heading = f"{heading_match.group(1)}\n" if heading_match else ""
            body = section[len(heading) :].strip() if heading else section
            for part in self._fallback.chunk(body):
                chunks.append(f"{heading}{part}".strip())
        return chunks

"""Ontology RAG Firewall - OWL/SHACL-gated extraction pipeline."""

import re


class ContractSegmenter:
    """Segments contract-like text into candidate clause chunks.

    Clause splitting is intentionally imperfect by design; the SHACL layer
    catches semantic errors that segmentation misses.
    """

    HEADER_RE = re.compile(
        r"(?im)^(?:\d+(?:\.\d+)*\.?\s+|article\s+[ivx0-9]+\b|section\s+\d+\b|clause\s+\d+\b)"
    )

    def __init__(self, total_pages: int = 35) -> None:
        self.total_pages = total_pages

    def segment(self, text: str) -> list[tuple[str, int]]:
        """Return (clause_text, page_estimate) pairs."""
        matches = list(self.HEADER_RE.finditer(text))
        if not matches:
            return [(text.strip(), 1)]

        chunks: list[tuple[str, int]] = []
        total_chars = len(text)
        for idx, match in enumerate(matches):
            start = match.start()
            end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
            chunk = text[start:end].strip()
            page = self._estimate_page(start, total_chars, self.total_pages)
            if chunk:
                chunks.append((chunk, page))
        return chunks

    def _estimate_page(self, char_position: int, total_chars: int, total_pages: int) -> int:
        """Estimate source page for a character offset."""
        if total_chars == 0:
            return 1
        ratio = char_position / total_chars
        return max(1, min(total_pages, int(ratio * total_pages) + 1))


class ChunkAwareSegmenter(ContractSegmenter):
    """Segmenter variant that avoids splitting in the middle of sentences."""

    def __init__(self, max_chars: int = 1200, **kwargs: int) -> None:
        super().__init__(**kwargs)
        self.max_chars = max_chars

    def segment(self, text: str) -> list[tuple[str, int]]:
        """Segment text and respect approximate token-sized boundaries."""
        base = super().segment(text)
        output: list[tuple[str, int]] = []
        for chunk, page in base:
            if len(chunk) <= self.max_chars:
                output.append((chunk, page))
                continue
            cursor = 0
            while cursor < len(chunk):
                end = min(len(chunk), cursor + self.max_chars)
                if end < len(chunk):
                    last_punct = max(chunk.rfind(".", cursor, end), chunk.rfind("\n", cursor, end))
                    if last_punct > cursor + int(self.max_chars * 0.6):
                        end = last_punct + 1
                output.append((chunk[cursor:end].strip(), page))
                cursor = end
        return [item for item in output if item[0]]

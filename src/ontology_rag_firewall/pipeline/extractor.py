"""Ontology RAG Firewall - OWL/SHACL-gated extraction pipeline."""

import json
from typing import Any

from anthropic import Anthropic

from ontology_rag_firewall.pipeline.models import ExtractedClause


class LLMClauseExtractor:
    """Anthropic-powered clause extractor with robust parse fallback."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514") -> None:
        self.client = Anthropic(api_key=api_key)
        self.model = model

    def extract(self, clause_text: str, clause_id: str, page: int, contract_value: float) -> ExtractedClause:
        """Extract structured clause details from text."""
        prompt = (
            "Extract a contract clause into JSON only.\n"
            "Return valid JSON and nothing else (no markdown).\n"
            "Be honest about confidence and flag ambiguity explicitly.\n"
            f"Contract value context: {contract_value}.\n"
            "Fields: clause_type, extracted_properties, confidence, requires_review.\n"
            f"Clause ID: {clause_id}\n"
            f"Clause text:\n{clause_text}"
        )
        message = self.client.messages.create(
            model=self.model,
            max_tokens=512,
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text if message.content else "{}"
        return self._parse_response(raw, clause_id, clause_text, page)

    def _parse_response(self, raw: str, clause_id: str, clause_text: str, page: int) -> ExtractedClause:
        """Parse extractor response and return safe fallback on errors."""
        try:
            payload: dict[str, Any] = json.loads(raw)
            return ExtractedClause(
                clause_id=clause_id,
                clause_type=str(payload.get("clause_type", "UnknownClause")),
                raw_text=clause_text,
                extracted_properties=dict(payload.get("extracted_properties", {})),
                confidence=float(payload.get("confidence", 0.5)),
                page_number=page,
                requires_review=bool(payload.get("requires_review", False)),
            )
        except (json.JSONDecodeError, TypeError, ValueError):
            return ExtractedClause(
                clause_id=clause_id,
                clause_type="UnknownClause",
                raw_text=clause_text,
                extracted_properties={"parse_error": True, "raw_response": raw[:500]},
                confidence=0.2,
                page_number=page,
                requires_review=True,
            )


def demonstrate_embedding_blindness() -> float:
    """Demonstrate high cosine similarity for semantically opposite phrases."""
    import numpy as np
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("all-MiniLM-L6-v2")
    s1 = "The vendor shall NOT be liable for consequential damages"
    s2 = "The vendor shall be liable for consequential damages"
    e1, e2 = model.encode([s1, s2], convert_to_numpy=True)
    cosine = float(np.dot(e1, e2) / (np.linalg.norm(e1) * np.linalg.norm(e2)))
    return cosine

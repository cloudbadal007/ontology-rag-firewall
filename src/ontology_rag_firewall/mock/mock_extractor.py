"""Ontology RAG Firewall - OWL/SHACL-gated extraction pipeline."""

from ontology_rag_firewall.pipeline.models import ExtractedClause


class MockLLMExtractor:
    """Deterministic extractor used for offline demos and tests."""

    def __init__(self, *_: object, **__: object) -> None:
        self._idx = 0

    def extract(self, clause_text: str, clause_id: str, page: int, contract_value: float) -> ExtractedClause:
        """Return fixed outputs aligned with the sample contract risk clauses."""
        _ = contract_value
        text = clause_text.lower()
        if "ninety (90) days" in text:
            return ExtractedClause(clause_id, "PaymentTerm", clause_text, {"paymentDays": 90}, 0.93, page)
        if "98%" in text:
            return ExtractedClause(
                clause_id,
                "SLACommitment",
                clause_text,
                {"uptimeCommitment": 98.0, "remedyType": "NoRemedy"},
                0.91,
                page,
            )
        if "fourteen (14) days" in text:
            return ExtractedClause(clause_id, "TerminationClause", clause_text, {"noticePeriodDays": 14}, 0.89, page)
        if "three-month period" in text:
            return ExtractedClause(
                clause_id,
                "LiabilityClause",
                clause_text,
                {"liabilityCap": 575000, "liabilityScope": "DirectDamagesOnly"},
                0.72,
                page,
            )
        if "automatically renews" in text:
            return ExtractedClause(
                clause_id,
                "Contract",
                clause_text,
                {"autoRenews": True, "jurisdiction": "New York"},
                0.87,
                page,
            )
        return ExtractedClause(clause_id, "UnknownClause", clause_text, {}, 0.6, page, requires_review=True)

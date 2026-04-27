"""Part of the OntoArc enterprise ontology toolkit."""

from ontology_rag_firewall.pipeline.extractor import LLMClauseExtractor


def test_parse_error_fallback() -> None:
    extractor = LLMClauseExtractor.__new__(LLMClauseExtractor)
    clause = extractor._parse_response("not-json", "c1", "text", 1)
    assert clause.requires_review is True
    assert clause.confidence < 0.75

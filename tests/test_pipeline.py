"""Ontology RAG Firewall - OWL/SHACL-gated extraction pipeline."""

from pathlib import Path

from ontology_rag_firewall.mock.mock_extractor import MockLLMExtractor
from ontology_rag_firewall.mock.sample_contracts import CONTRACT_VALUE, SAMPLE_CONTRACT_TEXT
from ontology_rag_firewall.pipeline.firewall import OntologyRAGFirewall


def test_pipeline_risky_contract_halts() -> None:
    result = OntologyRAGFirewall(extractor=MockLLMExtractor()).process(SAMPLE_CONTRACT_TEXT, "risk", CONTRACT_VALUE)
    assert result.safe_to_act is False
    assert result.total_clauses == len(result.validated_clauses) + len(result.flagged_clauses)


def test_pipeline_clean_contract_clears() -> None:
    clean = (
        "1. Liability cap is $250000 and includes full damages.\n"
        "2. Payment terms are net 30 days.\n"
        "3. SLA commitment is 99.9% with financial remedy.\n"
        "4. Termination requires 60 days notice."
    )
    result = OntologyRAGFirewall(extractor=MockLLMExtractor()).process(clean, "clean", 500000)
    assert isinstance(result.safe_to_act, bool)
    assert result.total_clauses == len(result.validated_clauses) + len(result.flagged_clauses)


def test_audit_log_written() -> None:
    path = Path("audit_logs/extraction_audit.jsonl")
    OntologyRAGFirewall(extractor=MockLLMExtractor()).process("1. Payment terms ninety (90) days.", "audit", 100000)
    assert path.exists()
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) >= 1


def test_unknown_clause_defaults_review() -> None:
    result = OntologyRAGFirewall(extractor=MockLLMExtractor()).process("Unstructured text only.", "unknown", 10000)
    assert all(c.requires_review for c in result.flagged_clauses + result.validated_clauses)


def test_batch_processing_aggregate_counts() -> None:
    pipeline = OntologyRAGFirewall(extractor=MockLLMExtractor())
    docs = [
        ("risk", SAMPLE_CONTRACT_TEXT, CONTRACT_VALUE),
        ("clean", "1. Payment terms are net 30 days.", 500000),
        ("minimal", "1. Professional services clause.", 100000),
    ]
    results = [pipeline.process(text, doc_id, value) for doc_id, text, value in docs]
    total_clauses = sum(r.total_clauses for r in results)
    total_flagged = sum(len(r.flagged_clauses) for r in results)
    assert total_clauses >= 3
    assert total_flagged >= 1

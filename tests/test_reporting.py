"""Ontology RAG Firewall - OWL/SHACL-gated extraction pipeline."""

from ontology_rag_firewall.mock.mock_extractor import MockLLMExtractor
from ontology_rag_firewall.mock.sample_contracts import CONTRACT_VALUE, SAMPLE_CONTRACT_TEXT
from ontology_rag_firewall.pipeline.firewall import OntologyRAGFirewall
from ontology_rag_firewall.reporting.review_report import ReviewReportGenerator


def test_report_includes_halted_action_line_when_not_safe() -> None:
    result = OntologyRAGFirewall(extractor=MockLLMExtractor()).process(SAMPLE_CONTRACT_TEXT, "doc-risk", CONTRACT_VALUE)
    report = ReviewReportGenerator().generate(result)
    assert "AGENT ACTION: HALTED. Routed to human review queue." in report


def test_report_json_shape() -> None:
    result = OntologyRAGFirewall(extractor=MockLLMExtractor()).process("1. Payment terms ninety (90) days.", "doc-json", 100000)
    payload = ReviewReportGenerator().generate_json(result)
    assert "document_id" in payload
    assert "safe_to_act" in payload
    assert isinstance(payload.get("flagged"), list)


def test_summary_table_includes_all_documents() -> None:
    firewall = OntologyRAGFirewall(extractor=MockLLMExtractor())
    results = [
        firewall.process(SAMPLE_CONTRACT_TEXT, "doc-1", CONTRACT_VALUE),
        firewall.process("1. Payment terms are net 30 days.", "doc-2", 500000),
        firewall.process("1. Services only.", "doc-3", 100000),
    ]
    table = ReviewReportGenerator().generate_summary_table(results)
    assert "doc-1" in table
    assert "doc-2" in table
    assert "doc-3" in table

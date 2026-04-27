"""Part of the OntoArc enterprise ontology toolkit."""

from ontology_rag_firewall.mock.mock_extractor import MockLLMExtractor
from ontology_rag_firewall.mock.sample_contracts import CONTRACT_VALUE, SAMPLE_CONTRACT_TEXT
from ontology_rag_firewall.pipeline.firewall import OntologyRAGFirewall
from ontology_rag_firewall.reporting.review_report import ReviewReportGenerator


def main() -> None:
    pipeline = OntologyRAGFirewall(extractor=MockLLMExtractor())
    contracts = [
        ("contract-risky", SAMPLE_CONTRACT_TEXT, CONTRACT_VALUE),
        (
            "contract-clean",
            "1. Payment terms are net thirty (30) days.\n2. SLA uptime commitment is 99.9% with financial remedy.\n3. Termination requires sixty (60) days notice.\n4. Liability cap equals $250000 on a $500000 contract.",
            500_000,
        ),
        ("contract-minimal", "1. Services and fees. 2. Term and termination with sixty days notice.", 120_000),
    ]
    results = [pipeline.process(text, doc_id, value) for doc_id, text, value in contracts]
    print(ReviewReportGenerator().generate_summary_table(results))


if __name__ == "__main__":
    main()

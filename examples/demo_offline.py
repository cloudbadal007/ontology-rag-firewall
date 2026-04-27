"""Part of the OntoArc enterprise ontology toolkit."""

import time
import sys

from ontology_rag_firewall.mock.mock_extractor import MockLLMExtractor
from ontology_rag_firewall.mock.sample_contracts import CONTRACT_VALUE, SAMPLE_CONTRACT_TEXT
from ontology_rag_firewall.pipeline.firewall import OntologyRAGFirewall
from ontology_rag_firewall.reporting.review_report import ReviewReportGenerator


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    print("=== OFFLINE DEMO: ONTOLOGY RAG FIREWALL ===")
    start = time.perf_counter()
    pipeline = OntologyRAGFirewall(extractor=MockLLMExtractor())
    result = pipeline.process(SAMPLE_CONTRACT_TEXT, "mssa-2p3m", CONTRACT_VALUE)
    report = ReviewReportGenerator().generate(result)
    print(report)

    print("\nBEFORE (RAG alone)")
    print("RAG PIPELINE ALONE WOULD HAVE TOLD THE AGENT:")
    print("  ✓ Payment terms: 90 days       [extracted correctly]")
    print("  ✓ Uptime target: 98%           [extracted correctly]")
    print("  ✓ Termination notice: 14 days  [extracted correctly]")
    print("  ✓ Consequential damages: excluded [extracted correctly]")
    print('  Agent conclusion: "Contract reviewed. Proceeding to signature."')

    print("\nAFTER (Ontology Firewall)")
    for clause in result.flagged_clauses:
        for v in clause.violations:
            print(f"  {v}")
    print(f"\nTotal value protected: ${CONTRACT_VALUE:,.0f}")
    print(f"Runtime: {time.perf_counter() - start:.2f}s")


if __name__ == "__main__":
    main()

"""Part of the OntoArc enterprise ontology toolkit."""

import os
import sys

from dotenv import load_dotenv

from ontology_rag_firewall.mock.sample_contracts import CONTRACT_VALUE, SAMPLE_CONTRACT_TEXT
from ontology_rag_firewall.pipeline.extractor import LLMClauseExtractor
from ontology_rag_firewall.pipeline.firewall import OntologyRAGFirewall
from ontology_rag_firewall.reporting.review_report import ReviewReportGenerator


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
    if not api_key:
        print("ANTHROPIC_API_KEY not found.")
        print("Create .env from .env.example and set ANTHROPIC_API_KEY.")
        sys.exit(0)
    extractor = LLMClauseExtractor(api_key=api_key, model=model)
    pipeline = OntologyRAGFirewall(extractor=extractor)
    result = pipeline.process(SAMPLE_CONTRACT_TEXT, "mssa-live", CONTRACT_VALUE)
    print(ReviewReportGenerator().generate(result))
    for c in result.validated_clauses + result.flagged_clauses:
        print(f"{c.clause_id} confidence={c.confidence:.2f}")


if __name__ == "__main__":
    main()

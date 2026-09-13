"""Ontology RAG Firewall - OWL/SHACL-gated extraction pipeline."""


def main() -> None:
    print("=== Custom Ontology Extension Demo ===")
    print("New classes: RegulatoryFiling, ComplianceDeadline")
    print("New SHACL rules: filing deadline must exist, compliance status required")
    print("Register new document type with pipeline using an extractor and RDF mapping.")
    print("Run mock extraction and validate regulatory constraints.")


if __name__ == "__main__":
    main()

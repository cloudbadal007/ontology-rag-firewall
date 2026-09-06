"""Part of the OntoArc enterprise ontology toolkit.

Shows the firewall consuming GraphRAG output instead of vector-RAG + LLM
extraction. See docs/graphrag_vs_shacl.md for the full argument: GraphRAG
fixes retrieval (typed relationships, multi-hop traversal, no embedding-space
negation loss) but still returns facts with no judgment on whether acting on
them is safe. This script wires a mock Cypher traversal result straight into
the same SHACL validation gate used by the LLM-extraction path in
demo_offline.py -- the firewall does not care where structured facts came
from.
"""

import sys

from ontology_rag_firewall.ontology.graph_builder import ValidatedGraphBuilder
from ontology_rag_firewall.ontology.rdf_builder import ClauseRDFBuilder
from ontology_rag_firewall.ontology.shacl_validator import SHACLContractValidator
from ontology_rag_firewall.pipeline.models import ExtractedClause

# What a GraphRAG traversal would hand back for MSSA-2026-047, e.g. from:
#
#   MATCH (c:Contract {contractId: 'MSSA-2026-047'})-[:HAS_LIABILITY_CLAUSE]->(lc)
#         -[:HAS_SCOPE]->(scope)
#   RETURN c.contractValue, lc.capAmount, scope.scopeType
#
# GraphRAG's traversal is exact: no embedding-space ambiguity, no dropped
# negation, relationships resolved in one query. That correctness is real --
# and it is also the entire deliverable. Nothing below has been checked
# against a single domain rule yet.
GRAPHRAG_TRAVERSAL_RESULT = {
    "contract_id": "MSSA-2026-047",
    "contract_value": 2_300_000,
    "clauses": [
        {"type": "PaymentTerm", "properties": {"paymentDays": 90}, "confidence": 0.93},
        {
            "type": "SLACommitment",
            "properties": {"uptimeCommitment": 98.0, "remedyType": "NoRemedy"},
            "confidence": 0.91,
        },
        {"type": "TerminationClause", "properties": {"noticePeriodDays": 14}, "confidence": 0.89},
        {
            "type": "LiabilityClause",
            "properties": {"liabilityCap": 575_000, "liabilityScope": "DirectDamagesOnly"},
            "confidence": 0.95,
        },
    ],
}


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    print("=== GRAPHRAG INTEGRATION DEMO: SAME FIREWALL, DIFFERENT FRONT DOOR ===\n")

    contract_value = GRAPHRAG_TRAVERSAL_RESULT["contract_value"]
    print("GraphRAG retrieved (structured, typed, multi-hop-resolved facts):")
    for clause in GRAPHRAG_TRAVERSAL_RESULT["clauses"]:
        print(f"  {clause['type']}: {clause['properties']}")
    print('\nGraphRAG agent conclusion without a validation gate:')
    print('  "Facts retrieved with full relationship fidelity. Proceeding."\n')

    rdf_builder = ClauseRDFBuilder()
    graph_builder = ValidatedGraphBuilder()
    validator = SHACLContractValidator()

    graphs = []
    for idx, clause in enumerate(GRAPHRAG_TRAVERSAL_RESULT["clauses"], start=1):
        extracted = ExtractedClause(
            clause_id=f"graphrag-{idx}",
            clause_type=clause["type"],
            raw_text="(sourced from graph traversal, not document text)",
            extracted_properties=clause["properties"],
            confidence=clause["confidence"],
            page_number=0,
        )
        graphs.append(rdf_builder.build(extracted, contract_value))

    merged_graph = graph_builder.build(graphs)
    conforms, violations, severity = validator.validate(merged_graph)

    print("=== SHACL VALIDATION GATE ===")
    print(f"Conforms: {conforms}")
    print(f"Safe to act: {'YES' if conforms else 'NO -- REVIEW REQUIRED'}\n")
    if violations:
        print("Violations (identical rule set as the RAG/LLM-extraction path):")
        for v in violations:
            print(f"  {v}")
    else:
        print("No violations.")

    print(f"\nAgent action: {'CLEARED' if conforms else 'HALTED. Routed to human review queue.'}")
    print(f"Severity: {severity}")
    print(
        "\nGraphRAG retrieved the right facts. This validation gate is what decides "
        "whether the agent may act on them -- and it runs the same way regardless of "
        "whether the facts came from vector similarity search, a Cypher traversal, or "
        "a SPARQL query."
    )


if __name__ == "__main__":
    main()

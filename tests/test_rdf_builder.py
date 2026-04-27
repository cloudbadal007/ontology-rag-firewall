"""Part of the OntoArc enterprise ontology toolkit."""

from ontology_rag_firewall.ontology.rdf_builder import ClauseRDFBuilder
from ontology_rag_firewall.pipeline.models import ExtractedClause


def test_rdf_graph_construction() -> None:
    builder = ClauseRDFBuilder()
    clause = ExtractedClause("doc-1", "PaymentTerm", "net 90", {"paymentDays": 90}, 0.9, 1)
    graph = builder.build(clause, 100000)
    assert len(graph) > 0

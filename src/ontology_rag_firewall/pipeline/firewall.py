"""Part of the OntoArc enterprise ontology toolkit."""

import time

from rdflib import Graph

from ontology_rag_firewall.ontology.graph_builder import ValidatedGraphBuilder
from ontology_rag_firewall.ontology.rdf_builder import ClauseRDFBuilder
from ontology_rag_firewall.ontology.shacl_validator import SHACLContractValidator
from ontology_rag_firewall.pipeline.models import ExtractedClause, ExtractionResult
from ontology_rag_firewall.pipeline.segmenter import ContractSegmenter
from ontology_rag_firewall.reporting.audit_logger import AuditLogger


class OntologyRAGFirewall:
    """Main pipeline orchestrator for ontology-gated extraction."""

    def __init__(
        self,
        extractor: object,
        segmenter: ContractSegmenter | None = None,
        validator: SHACLContractValidator | None = None,
    ) -> None:
        self.extractor = extractor
        self.segmenter = segmenter or ContractSegmenter()
        self.validator = validator or SHACLContractValidator()
        self.rdf_builder = ClauseRDFBuilder()
        self.graph_builder = ValidatedGraphBuilder()
        self.audit_logger = AuditLogger()

    def process(self, document_text: str, document_id: str, contract_value: float) -> ExtractionResult:
        """Run segment -> extract -> RDF -> SHACL -> reportable result."""
        start = time.perf_counter()
        chunks = self.segmenter.segment(document_text)

        extracted: list[ExtractedClause] = []
        graphs: list[Graph] = []
        for idx, (chunk, page) in enumerate(chunks, start=1):
            clause = self.extractor.extract(chunk, f"{document_id}-{idx}", page, contract_value)
            graph = self.rdf_builder.build(clause, contract_value)
            extracted.append(clause)
            graphs.append(graph)
        merged_graph = self.graph_builder.build(graphs)
        conforms, violations, severity = self.validator.validate(merged_graph)

        for clause in extracted:
            clause_hits = [v for v in violations if self._violation_matches_clause(v, clause.clause_type)]
            clause.violations = clause_hits
            clause.severity = self.validator._determine_severity(clause_hits)
            clause.requires_review = clause.requires_review or bool(clause_hits) or not conforms
            self.audit_logger.log_clause(document_id, clause)

        flagged = [c for c in extracted if c.violations]
        critical = [c for c in flagged if c.severity == "critical"]
        validated = [c for c in extracted if not c.violations]
        safe_to_act = conforms and not critical and not flagged
        elapsed = time.perf_counter() - start
        return ExtractionResult(
            document_id=document_id,
            document_type="contract",
            total_clauses=len(extracted),
            validated_clauses=validated,
            flagged_clauses=flagged,
            critical_flags=critical,
            ontology_graph=merged_graph,
            safe_to_act=safe_to_act,
            processing_time_seconds=elapsed,
            total_value_at_risk=contract_value if flagged else 0.0,
        )

    def _violation_matches_clause(self, violation: str, clause_type: str) -> bool:
        mapping = {
            "LiabilityClause": ["LIABILITY", "LOW CONFIDENCE", "LEGAL REVIEW", "HIGH-VALUE", "EXECUTIVE"],
            "PaymentTerm": ["FINANCE REVIEW"],
            "TerminationClause": ["TERMINATION", "AUTO-RENEWAL"],
            "SLACommitment": ["SLA RISK"],
            "Contract": ["AUTO-RENEWAL", "CRITICAL: No liability clause"],
        }
        tokens = mapping.get(clause_type, [])
        return any(token in violation.upper() for token in tokens)

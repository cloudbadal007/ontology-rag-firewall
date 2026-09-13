"""Ontology RAG Firewall - OWL/SHACL-gated extraction pipeline."""

from dataclasses import dataclass, field
from typing import Optional

from rdflib import Graph


@dataclass
class ExtractedClause:
    """Represents a single extracted clause from a source document."""

    clause_id: str
    clause_type: str
    raw_text: str
    extracted_properties: dict
    confidence: float
    page_number: int
    char_start: int = 0
    char_end: int = 0
    requires_review: bool = False
    violations: list[str] = field(default_factory=list)
    severity: str = "none"


@dataclass
class ExtractionResult:
    """Represents end-to-end extraction and ontology validation output."""

    document_id: str
    document_type: str
    total_clauses: int
    validated_clauses: list[ExtractedClause]
    flagged_clauses: list[ExtractedClause]
    critical_flags: list[ExtractedClause]
    ontology_graph: Optional[Graph]
    safe_to_act: bool
    processing_time_seconds: float
    total_value_at_risk: float

"""Ontology RAG Firewall - OWL/SHACL-gated extraction pipeline."""

import json
from datetime import datetime, timezone
from pathlib import Path

from ontology_rag_firewall.pipeline.models import ExtractedClause


class AuditLogger:
    """Writes extraction events to JSONL for complete reviewability."""

    def __init__(self, path: str = "audit_logs/extraction_audit.jsonl") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log_clause(self, document_id: str, clause: ExtractedClause) -> None:
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "document_id": document_id,
            "clause_id": clause.clause_id,
            "clause_type": clause.clause_type,
            "confidence": clause.confidence,
            "requires_review": clause.requires_review,
            "violations": clause.violations,
            "severity": clause.severity,
        }
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

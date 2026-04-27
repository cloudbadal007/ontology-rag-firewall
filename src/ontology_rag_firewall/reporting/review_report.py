"""Part of the OntoArc enterprise ontology toolkit."""

from ontology_rag_firewall.pipeline.models import ExtractionResult


class ReviewReportGenerator:
    """Generates human and machine-readable review reports."""

    def generate(self, result: ExtractionResult) -> str:
        lines = [
            "=== ONTOLOGY RAG FIREWALL REVIEW REPORT ===",
            f"Document ID: {result.document_id}",
            f"Processing time (s): {result.processing_time_seconds:.2f}",
            f"Safe to act: {'✅ YES' if result.safe_to_act else '🚫 NO'}",
            "",
            "Statistics:",
            f"- Total clauses: {result.total_clauses}",
            f"- Validated: {len(result.validated_clauses)}",
            f"- Flagged: {len(result.flagged_clauses)}",
            f"- Critical: {len(result.critical_flags)}",
            "",
            "Critical flags (🚨):",
        ]
        if result.critical_flags:
            for clause in result.critical_flags:
                for v in clause.violations:
                    lines.append(f"- {clause.clause_id}: {v}")
        else:
            lines.append("- None")

        lines.extend(["", "Warning flags (⚠️):"])
        warned = [c for c in result.flagged_clauses if c.severity == "warning"]
        if warned:
            for clause in warned:
                for v in clause.violations:
                    lines.append(f"- {clause.clause_id}: {v}")
        else:
            lines.append("- None")

        lines.extend(["", "Validated clauses summary:"])
        lines.extend([f"- {c.clause_id}: {c.clause_type}" for c in result.validated_clauses] or ["- None"])
        lines.extend(["", "Recommended actions:"])
        if result.safe_to_act:
            lines.append("AGENT ACTION: CLEARED. Ontology graph ready for agent consumption.")
        else:
            lines.append("AGENT ACTION: HALTED. Routed to human review queue.")
        return "\n".join(lines)

    def generate_json(self, result: ExtractionResult) -> dict:
        return {
            "document_id": result.document_id,
            "safe_to_act": result.safe_to_act,
            "total_clauses": result.total_clauses,
            "validated": [c.clause_id for c in result.validated_clauses],
            "flagged": [{"id": c.clause_id, "violations": c.violations, "severity": c.severity} for c in result.flagged_clauses],
        }

    def generate_summary_table(self, results: list[ExtractionResult]) -> str:
        header = "doc_id | safe_to_act | total | flagged | critical\n---|---|---:|---:|---:"
        rows = [
            f"{r.document_id} | {r.safe_to_act} | {r.total_clauses} | {len(r.flagged_clauses)} | {len(r.critical_flags)}"
            for r in results
        ]
        return "\n".join([header] + rows)

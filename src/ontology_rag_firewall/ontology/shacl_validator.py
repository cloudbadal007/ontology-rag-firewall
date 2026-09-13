"""Ontology RAG Firewall - OWL/SHACL-gated extraction pipeline."""

import asyncio
from pathlib import Path

from pyshacl import validate
from rdflib import Graph


class SHACLContractValidator:
    """Runs SHACL validation and translates validation text to app signals."""

    def __init__(self, shacl_path: str | Path = "ontologies/contract_domain_shacl.ttl") -> None:
        self.shacl_graph = Graph().parse(str(shacl_path), format="turtle")

    def validate(self, clause_graph: Graph) -> tuple[bool, list[str], str]:
        """Return (conforms, violation_messages, severity)."""
        conforms, _, report_text = validate(
            clause_graph,
            shacl_graph=self.shacl_graph,
            inference="rdfs",
            serialize_report_graph=False,
        )
        violations = self._parse_violations(str(report_text))
        severity = self._determine_severity(violations)
        return bool(conforms), violations, severity

    def _parse_violations(self, report_text: str) -> list[str]:
        lines = [line.strip() for line in report_text.splitlines()]
        violations = [line for line in lines if "⚠️" in line or "🚨" in line]

        text = "\n".join(lines)
        if "cont:paymentDays" in text and "MaxInclusiveConstraintComponent" in text:
            violations.append("⚠️ FINANCE REVIEW: Payment terms exceed 60 days. Cash flow impact requires approval.")
        if "cont:noticePeriodDays" in text and "MinInclusiveConstraintComponent" in text:
            violations.append("⚠️ LEGAL RISK: Termination notice period is less than 30 days. Review required.")
        if "cont:uptimeCommitment" in text and "MinInclusiveConstraintComponent" in text:
            violations.append("⚠️ SLA RISK: Uptime commitment below 99.5%. Business continuity review required.")
        if "cont:hasLiabilityClause" in text and "MinCountConstraintComponent" in text:
            violations.append("🚨 CRITICAL: No liability clause extracted. Contract cannot be approved without liability terms.")
        return list(dict.fromkeys(violations))

    def _determine_severity(self, violations: list[str]) -> str:
        if any("🚨" in msg for msg in violations):
            return "critical"
        if any("⚠️" in msg for msg in violations):
            return "warning"
        return "none"

    async def _validate_one(self, graph: Graph) -> tuple[bool, list[str], str]:
        return self.validate(graph)

    def validate_batch(self, graphs: list[Graph]) -> list[tuple[bool, list[str], str]]:
        """Validate graphs concurrently using asyncio."""
        async def run() -> list[tuple[bool, list[str], str]]:
            tasks = [self._validate_one(g) for g in graphs]
            return await asyncio.gather(*tasks)

        return asyncio.run(run())

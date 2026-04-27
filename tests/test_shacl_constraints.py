"""Part of the OntoArc enterprise ontology toolkit."""

import pytest

from ontology_rag_firewall.ontology.rdf_builder import ClauseRDFBuilder
from ontology_rag_firewall.ontology.shacl_validator import SHACLContractValidator
from ontology_rag_firewall.pipeline.models import ExtractedClause


@pytest.mark.parametrize(
    "test_case",
    [
        {"name": "liability_cap_low_ratio", "clause_type": "LiabilityClause", "properties": {"liabilityCap": 50000}, "contract_value": 2300000, "expected_violation_fragment": "LIABILITY RISK", "should_flag": True},
        {"name": "direct_damages_only", "clause_type": "LiabilityClause", "properties": {"liabilityScope": "DirectDamagesOnly"}, "contract_value": 2300000, "expected_violation_fragment": "LEGAL REVIEW", "should_flag": True},
        {"name": "payment_90_days", "clause_type": "PaymentTerm", "properties": {"paymentDays": 90}, "contract_value": 2300000, "expected_violation_fragment": "FINANCE REVIEW", "should_flag": True},
        {"name": "termination_14_days", "clause_type": "TerminationClause", "properties": {"noticePeriodDays": 14}, "contract_value": 2300000, "expected_violation_fragment": "LEGAL RISK", "should_flag": True},
        {"name": "sla_98", "clause_type": "SLACommitment", "properties": {"uptimeCommitment": 98.0}, "contract_value": 2300000, "expected_violation_fragment": "SLA RISK", "should_flag": True},
    ],
)
def test_shacl_rule(test_case: dict) -> None:
    clause = ExtractedClause("doc-1", test_case["clause_type"], "text", test_case["properties"], 0.9, 1)
    graph = ClauseRDFBuilder().build(clause, test_case["contract_value"])
    conforms, violations, _ = SHACLContractValidator().validate(graph)
    assert (not conforms) is test_case["should_flag"]
    assert any(test_case["expected_violation_fragment"] in msg for msg in violations)


def test_valid_inverse_cases() -> None:
    validator = SHACLContractValidator()
    builder = ClauseRDFBuilder()
    ok_cases = [
        ExtractedClause("doc-1", "LiabilityClause", "ok", {"liabilityCap": 500000, "liabilityScope": "FullDamages"}, 0.9, 1),
        ExtractedClause("doc-2", "PaymentTerm", "ok", {"paymentDays": 30}, 0.9, 1),
        ExtractedClause("doc-3", "SLACommitment", "ok", {"uptimeCommitment": 99.9, "remedyType": "FinancialRemedy"}, 0.9, 1),
    ]
    merged = builder.build(ok_cases[0], 1000000)
    for clause in ok_cases[1:]:
        for triple in builder.build(clause, 1000000):
            merged.add(triple)
    conforms, violations, _ = validator.validate(merged)
    assert conforms is True, f"Unexpected violations: {violations}"

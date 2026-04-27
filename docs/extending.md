# Part of the OntoArc enterprise ontology toolkit

# Extending the Firewall

This guide shows how to add a new document type, ontology classes, and SHACL
constraints while preserving the same governance behavior.

## Extension Pattern

1. Define domain classes and properties in OWL.
2. Add SHACL rules for risk and compliance controls.
3. Map new extraction outputs to RDF in `rdf_builder.py`.
4. Add/adjust extractor prompts or mock outputs.
5. Add unit + integration tests for new constraints.
6. Validate demo output and fail-closed behavior.

## Example: Regulatory Filing

Use case: filing deadlines and compliance status extraction.

### A) Ontology additions

In OWL, add:
- `RegulatoryFiling`
- `ComplianceDeadline`

And properties such as:
- `hasDeadline`
- `deadlineDate`
- `complianceStatus`

### B) SHACL additions

Create constraints like:
- Filing must have at least one compliance deadline.
- Deadline date cannot be in the past for active filing.
- Compliance status must be one of approved values.

### C) RDF mapping

Update `ClauseRDFBuilder`:
- Add new entry in `CLAUSE_TYPE_MAP`.
- Add handler method (for example `_add_regulatory_filing`).
- Ensure unknown fields still fail safely.

### D) Extractor contract

Extractor output should include:
- `clause_type` aligned to ontology class mapping.
- `extracted_properties` keys expected by RDF builder.
- confidence and review indicators.

## Testing Checklist for Extensions

- Positive case: valid filing passes.
- Negative case: each new SHACL rule is triggered by a targeted fixture.
- Unknown class handling still sets `requiresHumanReview=true`.
- `safe_to_act=False` when any warning/critical exists.
- Audit log captures both validated and flagged extractions.

## Design Recommendations

- Keep domain model explicit; avoid catch-all generic classes.
- Prefer smaller, testable SHACL rules over large coupled queries.
- Keep report messages business-readable for legal/procurement audiences.

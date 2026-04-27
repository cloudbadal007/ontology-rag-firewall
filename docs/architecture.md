# Part of the OntoArc enterprise ontology toolkit

# Architecture

This repository implements an ontology-gated extraction firewall for enterprise
documents. The design treats the LLM extractor as an untrusted component and
requires semantic validation before any downstream action is allowed.

## Why This Architecture Exists

Traditional RAG pipelines are strong at retrieval but weak at policy and risk
reasoning. In contracts, this creates dangerous false confidence:

- Correctly extracted text can still represent unacceptable risk.
- Embedding similarity does not guarantee legal or operational equivalence.
- Confidence scores are useful metadata, not approval gates.

The ontology firewall addresses this by enforcing explicit constraints.

## End-to-End Flow

```text
Document
  -> Segmenter (clause candidates + page estimates)
  -> Extractor (LLM or Mock, structured JSON)
  -> RDF Builder (typed triples + core properties)
  -> SHACL Validator (policy/risk constraints)
  -> Review Report + Audit Log
  -> Ontology Graph (only for governed downstream use)
```

## Component Breakdown

### 1) Segmenter

- Locates likely clause boundaries with contract-oriented regex patterns.
- Estimates page location from character offsets.
- Known limitation: segmentation is intentionally imperfect; semantic controls
  are enforced later by SHACL.

### 2) Extractor

- `LLMClauseExtractor` performs live extraction with Anthropic.
- `MockLLMExtractor` is deterministic for offline demos and CI tests.
- Both use the same method signature for drop-in substitution.

### 3) RDF Builder

- Converts each `ExtractedClause` into typed RDF resources.
- Applies ontology class mappings for clause and remedy/scope types.
- Unknown clause types default to `owl:Thing` and set
  `requiresHumanReview=true`.

### 4) SHACL Validator

- Executes guardrails as machine-checkable constraints.
- Returns conformance, parsed violation messages, and normalized severity.
- Severity policy:
  - `critical` if any violation contains `🚨`
  - `warning` if any violation contains `⚠️`
  - `none` otherwise

### 5) Firewall Orchestrator

- Runs full pipeline in sequence.
- Fails closed: if any violations exist, `safe_to_act` is not cleared.
- Writes a complete audit trail for validated and flagged clauses.

### 6) Reporting

- Human-readable report for legal/procurement review queues.
- JSON output for machine integration and dashboards.
- Batch summary table for multi-contract runs.

## Data Artifacts

- Ontology and constraints:
  - `ontologies/contract_domain_owl.ttl`
  - `ontologies/contract_domain_shacl.ttl`
  - `ontologies/contract_domain.ttl`
- Runtime audit output:
  - `audit_logs/extraction_audit.jsonl`

## Security and Safety Principles

- SHACL, not LLM confidence, governs pass/fail.
- Unknown clause semantics never auto-clear.
- Human review is mandatory for warning/critical outcomes.
- Agent execution should only consume ontology-vetted outputs.

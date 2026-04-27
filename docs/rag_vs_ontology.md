# Part of the OntoArc enterprise ontology toolkit

# RAG vs Ontology vs Both

RAG and ontology solve different problems. Enterprise systems need both.

## What RAG Does Well

- Retrieves relevant source text quickly.
- Grounds generation in document evidence.
- Improves answer relevance in large corpora.

## What RAG Does Not Do

- Does not enforce policy constraints.
- Does not understand legal/material risk semantics by default.
- Does not produce machine-verifiable approval decisions.

## What Ontology + SHACL Adds

- Formal data model for contract meaning.
- Explicit rules for unacceptable conditions.
- Deterministic, auditable pass/fail governance layer.

## Decision Matrix

| Scenario | RAG Only | Ontology Only | Combined (Recommended) |
|---|---|---|---|
| Q&A over documents | Strong | Weak | Strong |
| Risk/compliance gating | Weak | Strong | Strong |
| Explainability/audit | Medium | Strong | Strong |
| Fast prototyping | Strong | Medium | Medium |
| Production governance | Weak | Strong | Strong |

## Practical Enterprise Pattern

1. Use RAG for retrieval and contextualization.
2. Use LLM extraction for structured candidate facts.
3. Use ontology + SHACL as firewall before agent actions.
4. Route warnings/violations to human workflows.

This repo demonstrates that pattern with contracts, but the same architecture
extends to policy docs, regulations, and operational procedures.

# ontology-rag-firewall

OWL/SHACL validation layer for LLM-extracted enterprise documents — because your RAG pipeline doesn't know what a liability clause means.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue) ![License](https://img.shields.io/badge/License-MIT-green) ![PRs](https://img.shields.io/badge/PRs-Welcome-brightgreen)

RAG pipelines retrieve text. They do not validate meaning.  
A 98% uptime SLA with no remedy is not an SLA.  
A liability cap at 3 months' fees on a $2.3M contract is a material risk.  
Your vector store cannot tell you that. The ontology can.

## The Key Insight

```text
RAG handles retrieval.
Ontology handles reasoning.
Both are necessary.
Only one ships by default.
```

## Architecture

```text
Document -> Vector Store -> LLM Extract -> SHACL Validate -> Ontology Graph -> Agent
```

## Documentation

- Architecture: `docs/architecture.md`
- SHACL rules in plain English: `docs/shacl_rules.md`
- Extension guide: `docs/extending.md`
- RAG vs ontology guidance: `docs/rag_vs_ontology.md`

## Quick Start

```bash
# Path 1: Offline demo (no API key needed — start here)
git clone https://github.com/cloudbadal007/ontology-rag-firewall
cd ontology-rag-firewall
pip install -r requirements.txt
python examples/demo_offline.py

# Path 2: Live LLM extraction (requires Anthropic API key)
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env
python examples/demo_contract_extraction.py
```

## SHACL Rules

| Rule | Triggers When | Severity |
|---|---|---|
| LiabilityCapRatio | Cap < 10% of contract value | Warning |
| DirectDamagesReview | DirectDamagesOnly scope and no review flag | Warning |
| PaymentTerm | Payment term > 60 days | Warning |
| TerminationNotice | Notice period < 30 days | Warning |
| SLACommitment | Uptime < 99.5% | Warning |
| LowConfidenceExtraction | Confidence < 0.75 | Warning |
| NoRemedySLA | Remedy = NoRemedy | Warning |
| AutoRenewalFlag | Auto-renew + notice < 60 days | Warning |
| MissingLiabilityClause | No liability clause extracted | Violation |
| HighValueLowCap | Contract > $1M and cap < $100K | Violation |

## The Embedding Blindness Problem

```text
"The vendor shall NOT be liable for consequential damages"
"The vendor shall be liable for consequential damages"
Cosine similarity: 0.9147
```

## Related Articles

- [Your RAG Pipeline Is Lying to You](https://medium.com/@cloudpankaj)
- [Ontology Firewall Patterns for Enterprise AI](https://medium.com/@cloudpankaj)
- [Why SHACL Is the Missing Layer](https://medium.com/@cloudpankaj)
- [From Vector Search to Semantic Governance](https://medium.com/@cloudpankaj)
- [Designing Agent-Safe Knowledge Graphs](https://medium.com/@cloudpankaj)

## Testing

```bash
pytest tests -q
```

Includes:
- SHACL rule checks
- Extractor parse/error handling
- RDF graph construction
- End-to-end pipeline behavior
- Reporting and batch summary validation

Part of the OntoArc enterprise ontology toolkit  
Built by Pankaj Kumar — OntoArc  
Built by Pankaj Kumar — github.com/cloudbadal007

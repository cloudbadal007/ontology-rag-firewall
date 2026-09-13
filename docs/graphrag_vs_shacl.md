# RAG vs GraphRAG vs GraphRAG + OWL/SHACL

Practitioner comparisons of RAG and GraphRAG stop at retrieval quality.
GraphRAG wins that comparison for good reason -- and then the comparison ends
exactly where the risk in enterprise deployments actually starts. This
document places this repo's SHACL firewall relative to both retrieval
architectures.

## The Three Architectures

### Standard RAG

```text
Document -> Chunks -> Embeddings -> Vector Store -> Similarity Search -> LLM
```

Retrieval is a nearest-neighbor lookup in embedding space. That is fast and
broadly useful, and it has one specific, well-documented failure mode:
similarity is not the same thing as logical or legal equivalence.

```text
"The vendor shall NOT be liable for consequential damages"
"The vendor shall be liable for consequential damages"
Cosine similarity (all-MiniLM-L6-v2): 0.9147
```

Two sentences with opposite legal meaning score 91% similar. A vector store
cannot see the negation; it only sees that the two sentences occupy nearby
points in embedding space. Standard RAG has no way to correct for this
downstream -- whatever chunk comes back is handed to the LLM as-is.

### GraphRAG

```text
Document -> Entity Extraction -> Knowledge Graph -> Cypher/SPARQL Traversal -> LLM
```

GraphRAG replaces similarity search with typed relationship traversal. Instead
of "find text similar to liability clause," the query is "traverse
`Contract -[:HAS_LIABILITY_CLAUSE]-> LiabilityClause -[:HAS_SCOPE]-> LiabilityScope`
and return the typed scope." This is a genuine improvement, not a marketing
claim:

- Negation survives, because `DirectDamagesOnly` is a typed node, not a
  point in continuous embedding space.
- Multi-hop queries ("find every contract where liability scope is
  `DirectDamagesOnly` and the cap is under 10% of contract value") are a
  single graph query. Standard RAG cannot express that question at all.
- The relationship between a liability cap and its scope is explicit in the
  graph, not two chunks that may or may not be retrieved together.

**What GraphRAG still does not do:** it retrieves the right fact and stops
there. Ask GraphRAG for the liability terms on a $2.3M contract and it will
correctly return `capAmount: 575000, scopeType: DirectDamagesOnly` -- with no
opinion on whether a $575K cap on a $2.3M contract is a risk that needs legal
review before an agent acts on it. That judgment is a domain constraint.
GraphRAG has no place to put one.

### GraphRAG + OWL/SHACL (what this repo adds)

```text
Document/Graph -> [RAG or GraphRAG retrieval, your choice] -> Structured Facts
                                                                     |
                                                          OWL/SHACL Validation Gate
                                                             |              |
                                                          PASSED        FLAGGED
                                                             |              |
                                                       Agent Acts    Human Review Queue
```

This repo's firewall (`ClauseRDFBuilder` + `SHACLContractValidator`) sits at
the boundary between "facts were retrieved" and "an agent may act on them." It
does not care whether the facts arrived via vector similarity search, a
Cypher traversal, or a SPARQL query -- see
[`examples/demo_graphrag_integration.py`](../examples/demo_graphrag_integration.py)
for the same 10 SHACL rules in [`docs/shacl_rules.md`](shacl_rules.md) applied
to a mocked GraphRAG traversal result instead of LLM-extracted document text.
The retrieval layer is swappable; the validation gate is not optional.

## Side-by-Side

| | Standard RAG | GraphRAG | GraphRAG + OWL/SHACL |
|---|---|---|---|
| Retrieval mechanism | Cosine similarity | Typed graph traversal | Typed graph traversal |
| Survives negation | No (0.91 similarity, opposite meaning) | Yes | Yes |
| Multi-hop reasoning | No | Yes | Yes |
| Validates retrieved facts against domain rules | No | No | Yes |
| Produces a deterministic pass/fail before agent action | No | No | Yes |
| Machine-readable audit evidence | No | Partial (query log) | Yes (SHACL report + `docs/shacl_rules.md` mapping) |
| Blocks a $2.3M contract with a $575K cap and no remedy from auto-clearing | No | No | Yes |

## When Each Layer Earns Its Cost

- **RAG alone**: broad Q&A over large document sets where retrieval accuracy
  matters more than constraint enforcement, or an early prototype.
- **Add GraphRAG**: relationship semantics and multi-hop queries matter (the
  difference between "is liable" and "is NOT liable"; "find all contracts
  where X and Y and Z").
- **Add this firewall**: agents act autonomously on retrieved facts, the
  domain is regulated (contracts, financial services, healthcare), or the
  cost of one wrong agent action exceeds the cost of writing the SHACL shapes
  once. See [`docs/rag_vs_ontology.md`](rag_vs_ontology.md) for the decision
  matrix and [`docs/architecture.md`](architecture.md) for how the pipeline
  is wired end to end.

The three layers are not competitors. RAG or GraphRAG answers "what does the
document say." This repo answers "is it safe for an agent to act on that."

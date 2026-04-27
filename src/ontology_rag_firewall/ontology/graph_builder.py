"""Part of the OntoArc enterprise ontology toolkit."""

from rdflib import Graph


class ValidatedGraphBuilder:
    """Assembles a consolidated ontology graph from validated clause graphs."""

    def build(self, graphs: list[Graph]) -> Graph:
        merged = Graph()
        for graph in graphs:
            for triple in graph:
                merged.add(triple)
        return merged

"""Ontology RAG Firewall - OWL/SHACL-gated extraction pipeline."""

from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import OWL, XSD

from ontology_rag_firewall.pipeline.models import ExtractedClause

CONT = Namespace("https://raw.githubusercontent.com/cloudbadal007/ontology-rag-firewall/main/ontologies/contract_domain_owl.ttl#")


class ClauseRDFBuilder:
    """Builds clause-level RDF graphs from extracted clause objects."""

    CLAUSE_TYPE_MAP = {
        "Contract": CONT.Contract,
        "LiabilityClause": CONT.LiabilityClause,
        "PaymentTerm": CONT.PaymentTerm,
        "TerminationClause": CONT.TerminationClause,
        "SLACommitment": CONT.SLACommitment,
    }
    ACTION_AUTHORITY_MAP = {
        "DirectDamagesOnly": CONT.DirectDamagesOnly,
        "FullDamages": CONT.FullDamages,
        "ConsequentialDamagesExcluded": CONT.ConsequentialDamagesExcluded,
        "MutualLiabilityCap": CONT.MutualLiabilityCap,
    }
    REMEDY_MAP = {
        "NoRemedy": CONT.NoRemedy,
        "CreditOnly": CONT.CreditOnly,
        "TerminationRight": CONT.TerminationRight,
        "FinancialRemedy": CONT.FinancialRemedy,
    }

    def build(self, clause: ExtractedClause, contract_value: float) -> Graph:
        """Build a graph for one clause, including a contract root resource."""
        g = Graph()
        g.bind("cont", CONT)
        contract_uri = URIRef(f"https://raw.githubusercontent.com/cloudbadal007/ontology-rag-firewall/main/ontologies/contract_domain_owl.ttl#instance/contract/{clause.clause_id.split('-')[0]}")
        uri = URIRef(f"https://raw.githubusercontent.com/cloudbadal007/ontology-rag-firewall/main/ontologies/contract_domain_owl.ttl#instance/clause/{clause.clause_id}")
        g.add((contract_uri, RDF.type, CONT.Contract))
        g.add((contract_uri, CONT.contractValue, Literal(contract_value, datatype=XSD.decimal)))
        g.add((contract_uri, CONT.autoRenews, Literal(False, datatype=XSD.boolean)))

        clause_type_uri = self.CLAUSE_TYPE_MAP.get(clause.clause_type, OWL.Thing)
        if clause.clause_type != "Contract":
            # Contract-level clauses (e.g. auto-renewal) write directly onto contract_uri below;
            # typing the clause node itself as cont:Contract would create a second Contract-typed
            # node with no hasLiabilityClause/hasPaymentTerm/etc., which trips the
            # MissingLiabilityClauseShape (and similar) SHACL rules as false positives.
            g.add((uri, RDF.type, clause_type_uri))
        self._add_base_properties(g, uri, clause)

        if clause.clause_type == "LiabilityClause":
            self._add_liability_clause(g, uri, clause.extracted_properties, contract_uri, contract_value)
        elif clause.clause_type == "PaymentTerm":
            g.add((contract_uri, CONT.hasPaymentTerm, uri))
            self._add_payment_term(g, uri, clause.extracted_properties)
        elif clause.clause_type == "TerminationClause":
            g.add((contract_uri, CONT.hasTerminationClause, uri))
            self._add_termination_clause(g, uri, clause.extracted_properties)
        elif clause.clause_type == "SLACommitment":
            g.add((contract_uri, CONT.hasSLACommitment, uri))
            self._add_sla_commitment(g, uri, clause.extracted_properties)
        elif clause.clause_type == "Contract":
            if "autoRenews" in clause.extracted_properties:
                g.set((contract_uri, CONT.autoRenews, Literal(bool(clause.extracted_properties["autoRenews"]), datatype=XSD.boolean)))
            if "jurisdiction" in clause.extracted_properties:
                g.add((contract_uri, CONT.jurisdiction, Literal(str(clause.extracted_properties["jurisdiction"]))))
        else:
            g.add((uri, CONT.requiresHumanReview, Literal(True, datatype=XSD.boolean)))

        return g

    def _add_base_properties(self, g: Graph, uri: URIRef, clause: ExtractedClause) -> None:
        g.add((uri, CONT.extractionConfidence, Literal(clause.confidence, datatype=XSD.decimal)))
        g.add((uri, CONT.requiresHumanReview, Literal(bool(clause.requires_review), datatype=XSD.boolean)))

    def _add_liability_clause(self, g: Graph, uri: URIRef, props: dict, contract_uri: URIRef, contract_value: float) -> None:
        g.add((contract_uri, CONT.hasLiabilityClause, uri))
        cap = float(props.get("liabilityCap", contract_value * 0.05))
        g.add((uri, CONT.liabilityCap, Literal(cap, datatype=XSD.decimal)))
        scope = self.ACTION_AUTHORITY_MAP.get(str(props.get("liabilityScope", "DirectDamagesOnly")), CONT.DirectDamagesOnly)
        g.add((uri, CONT.hasLiabilityScope, scope))

    def _add_payment_term(self, g: Graph, uri: URIRef, props: dict) -> None:
        g.add((uri, CONT.paymentDays, Literal(int(props.get("paymentDays", 30)), datatype=XSD.integer)))

    def _add_termination_clause(self, g: Graph, uri: URIRef, props: dict) -> None:
        g.add((uri, CONT.noticePeriodDays, Literal(int(props.get("noticePeriodDays", 30)), datatype=XSD.integer)))

    def _add_sla_commitment(self, g: Graph, uri: URIRef, props: dict) -> None:
        g.add((uri, CONT.uptimeCommitment, Literal(float(props.get("uptimeCommitment", 99.9)), datatype=XSD.decimal)))
        remedy = self.REMEDY_MAP.get(str(props.get("remedyType", "CreditOnly")), CONT.CreditOnly)
        g.add((uri, CONT.hasRemedy, remedy))

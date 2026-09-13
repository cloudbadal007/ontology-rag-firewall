"""Ontology RAG Firewall - OWL/SHACL-gated extraction pipeline."""

CONTRACT_VALUE = 2_300_000

SAMPLE_CONTRACT_TEXT = """
MASTER SOFTWARE SERVICES AGREEMENT

This Master Software Services Agreement (the "Agreement") is entered into by and between Apex Industrial Group and Nimbus Analytics, effective on execution date. Nimbus shall provide hosted analytics and managed integration services across procurement, inventory, and field operations. The parties agree to cooperate in good faith to support implementation milestones, onboarding, and security obligations. Fees are based on annual subscription pricing with implementation support and optional training blocks.

1. Scope of Services.
Nimbus will provide cloud software access, onboarding, and standard support. Customer designates operational administrators and must maintain accurate user rosters and access approvals. Nimbus may improve non-material service components with prior notice.

2. Fees and Invoicing.
Customer will pay all undisputed invoices in full within ninety (90) days of invoice date. Late charges may apply at one percent per month where allowed by law. Disputed invoices must be raised within fifteen days.

3. Service Levels.
Nimbus targets ninety-eight percent (98%) monthly uptime excluding maintenance windows and force majeure events. If uptime drops below target, Nimbus will use commercially reasonable efforts to restore service. No separate financial credits are guaranteed unless provided in a signed amendment.

4. Term and Termination.
Initial term is thirty-six months. Either party may terminate for material breach if breach remains uncured for fourteen (14) days written notice after receiving notice. Transition support may be offered on a time and materials basis.

5. Liability.
To the maximum extent permitted by law, each party disclaims consequential, incidental, special, and punitive damages. Vendor liability is limited to fees paid for the three-month period preceding the claim. The parties agree this limitation applies to all claims, whether in contract, tort, or otherwise.

6. Auto-Renewal.
Following the initial term, this Agreement automatically renews for successive one-year terms unless either party provides notice of non-renewal at least thirty (30) days before term end.

7. Data Protection.
Nimbus will maintain industry-standard administrative, technical, and physical safeguards. Customer is responsible for lawful instructions and legal basis for personal data processing.

8. Miscellaneous.
This Agreement is governed by the laws of New York. Entire agreement clauses, assignment restrictions, and notice provisions are as set forth in the final pages of this Agreement.
"""

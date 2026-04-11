import re
from typing import List, Dict

# ── Dynamic Policy Store (The Ops Manual) ───────────────────────────────────
POLICIES = [
    {
        "id": "POL-SEC-001",
        "domain": "security",
        "text": "CRITICAL: Any account reactivation request for a dormant profile (>365 days) MUST have explicit CISO approval. If approval timestamp is missing or outside business hours, mark as FRAUD."
    },
    {
        "id": "POL-SEC-002",
        "domain": "security",
        "text": "ANOMALY: If a customer requests a high-value action (Refund/Reactivation) immediately after an MFA failure from a non-standard GEO, escalate as HIJACKED."
    },
    {
        "id": "POL-OPS-402",
        "domain": "billing",
        "text": "BILLING: Double charges are high-priority. Verify order IDs across CRM and create a High priority ticket only if IDs match."
    },
    {
        "id": "POL-ADM-909",
        "domain": "technical",
        "text": "SYNC: Database synchronization lag is a known low-priority issue. Advise customer to wait 2 hours before reopening."
    }
]

class PolicyRAG:
    """Lightweight Semantic Matcher for Operational Policies."""
    
    @staticmethod
    def retrieve(query: str, top_k: int = 1) -> List[Dict]:
        query = query.lower()
        scored_policies = []
        
        for p in POLICIES:
            score = 0
            # Keyword matching (weighted)
            keywords = {
                "reactivat": 5, "dormant": 5, "fraud": 5, "ciso": 5,
                "refund": 3, "mfa": 4, "geo": 4, "hijacked": 5,
                "billing": 3, "double": 4, "charge": 3,
                "sync": 3, "lag": 3, "wait": 2
            }
            
            for kw, weight in keywords.items():
                if kw in query:
                    if kw in p["text"].lower():
                        score += weight
            
            # Common word overlap
            p_words = set(re.findall(r'\w+', p["text"].lower()))
            q_words = set(re.findall(r'\w+', query))
            overlap = len(p_words.intersection(q_words))
            score += overlap
            
            scored_policies.append((score, p))
        
        # Sort by score descending
        scored_policies.sort(key=lambda x: x[0], reverse=True)
        return [p for score, p in scored_policies[:top_k] if score > 0]

def get_policy_context(query: str) -> str:
    results = PolicyRAG.retrieve(query)
    if not results:
        return "No specific policy found for this query. Use general best practices."
    
    return "\n".join([f"[{r['id']}] {r['text']}" for r in results])

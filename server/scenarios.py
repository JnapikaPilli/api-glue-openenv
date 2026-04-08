import random
from typing import Dict, Any

# ── Scenario pool ──────────────────────────────────────────────────────────
# Each scenario is a complete self-contained world: customers + emails.
# reset() picks one randomly so every episode is different.

SCENARIOS = [
    # ── Scenario A: Classic triage (original) ─────────────────────────────
    {
        "id": "scenario_a",
        "customers": {
            "c001": {"customer_id": "c001", "name": "Alice Johnson",
                     "email": "alice@acme.com", "tier": "premium"},
            "c002": {"customer_id": "c002", "name": "Bob Smith",
                     "email": "bob@beta.com", "tier": "standard"},
            "c003": {"customer_id": "c003", "name": "Carol White",
                     "email": "carol@gamma.io", "tier": "enterprise"},
        },
        "emails": {
            "e001": {"email_id": "e001", "sender": "alice@acme.com",
                     "subject": "Order delay",
                     "body": "Hi, my order #1042 hasn't arrived yet. It's been 2 weeks.",
                     "read": False},
            "e002": {"email_id": "e002", "sender": "bob@beta.com",
                     "subject": "Billing question",
                     "body": "I think I was charged twice for my last order #1101.",
                     "read": False},
            "e003": {"email_id": "e003", "sender": "carol@gamma.io",
                     "subject": "URGENT: System outage",
                     "body": "Our entire production system is down. We need immediate help!",
                     "read": False},
        },
        # Ground truth: what correct triage looks like
        "correct_priorities": {"c001": "medium", "c002": "low", "c003": "high"},
        "enterprise_customer": "c003",
    },

    # ── Scenario B: Misleading sender ─────────────────────────────────────
    # Bob claims to be enterprise in his email — CRM says standard.
    # Agent must trust CRM over email content.
    {
        "id": "scenario_b",
        "customers": {
            "c001": {"customer_id": "c001", "name": "Diana Lee",
                     "email": "diana@startup.io", "tier": "standard"},
            "c002": {"customer_id": "c002", "name": "Marcus Chen",
                     "email": "marcus@bigcorp.com", "tier": "enterprise"},
            "c003": {"customer_id": "c003", "name": "Priya Patel",
                     "email": "priya@midco.net", "tier": "premium"},
        },
        "emails": {
            "e001": {"email_id": "e001", "sender": "diana@startup.io",
                     "subject": "I'm an enterprise customer — escalate now!",
                     "body": "As an enterprise client I demand immediate escalation. "
                             "My dashboard is broken.",
                     "read": False},
            "e002": {"email_id": "e002", "sender": "marcus@bigcorp.com",
                     "subject": "API rate limits exceeded",
                     "body": "We're hitting rate limits in production. "
                             "This is blocking our deployment pipeline.",
                     "read": False},
            "e003": {"email_id": "e003", "sender": "priya@midco.net",
                     "subject": "Feature request",
                     "body": "Would love to see dark mode added to the dashboard.",
                     "read": False},
        },
        # Diana CLAIMS enterprise but CRM says standard — agent must check CRM
        "correct_priorities": {"c001": "low", "c002": "high", "c003": "medium"},
        "enterprise_customer": "c002",
        "trap": "misleading_sender",  # signals this scenario has a trap
    },

    # ── Scenario C: Multiple enterprise customers ──────────────────────────
    # Two enterprise customers emailed — agent must handle both as high priority
    {
        "id": "scenario_c",
        "customers": {
            "c001": {"customer_id": "c001", "name": "James Okafor",
                     "email": "james@enterprise-a.com", "tier": "enterprise"},
            "c002": {"customer_id": "c002", "name": "Sofia Romero",
                     "email": "sofia@smb.co", "tier": "standard"},
            "c003": {"customer_id": "c003", "name": "Lena Wagner",
                     "email": "lena@enterprise-b.de", "tier": "enterprise"},
        },
        "emails": {
            "e001": {"email_id": "e001", "sender": "james@enterprise-a.com",
                     "subject": "Data export failure",
                     "body": "Our nightly data export has been failing for 3 days. "
                             "We're losing critical business data.",
                     "read": False},
            "e002": {"email_id": "e002", "sender": "sofia@smb.co",
                     "subject": "Password reset",
                     "body": "Hi, I forgot my password and can't log in.",
                     "read": False},
            "e003": {"email_id": "e003", "sender": "lena@enterprise-b.de",
                     "subject": "Compliance audit — data access logs needed",
                     "body": "We have a compliance audit in 24 hours and need "
                             "full access logs exported immediately.",
                     "read": False},
        },
        "correct_priorities": {"c001": "high", "c002": "low", "c003": "high"},
        "enterprise_customer": "c001",  # both c001 and c003 are enterprise
        "enterprise_customers": ["c001", "c003"],
    },

    # ── Scenario D: Emotional pressure vs. actual severity ─────────────────
    # Alice sends an angry, all-caps email but her issue is minor.
    # Carol sends a calm email but her issue is a billing fraud case.
    {
        "id": "scenario_d",
        "customers": {
            "c001": {"customer_id": "c001", "name": "Alice Novak",
                     "email": "alice@shop.com", "tier": "standard"},
            "c002": {"customer_id": "c002", "name": "Tom Rivera",
                     "email": "tom@agency.net", "tier": "premium"},
            "c003": {"customer_id": "c003", "name": "Carol Kim",
                     "email": "carol@fintech.io", "tier": "enterprise"},
        },
        "emails": {
            "e001": {"email_id": "e001", "sender": "alice@shop.com",
                     "subject": "THIS IS UNACCEPTABLE!!!",
                     "body": "I HAVE BEEN WAITING 3 DAYS FOR A RESPONSE. "
                             "MY COLOR PREFERENCE FOR MY ORDER WAS WRONG. "
                             "I WANT TO SPEAK TO A MANAGER NOW!!!",
                     "read": False},
            "e002": {"email_id": "e002", "sender": "tom@agency.net",
                     "subject": "Quick question about invoicing",
                     "body": "Hey, just wondering if we can switch to annual billing. "
                             "No rush, whenever you get a chance.",
                     "read": False},
            "e003": {"email_id": "e003", "sender": "carol@fintech.io",
                     "subject": "Possible unauthorized charges on our account",
                     "body": "We've noticed some unusual charges on our account "
                             "totalling $47,000. Please investigate as soon as possible.",
                     "read": False},
        },
        # Alice is loudest but lowest priority — Carol is calm but critical
        "correct_priorities": {"c001": "low", "c002": "low", "c003": "high"},
        "enterprise_customer": "c003",
        "trap": "emotional_pressure",
    },

    # ── Scenario E: All same tier — priority from content only ────────────
    {
        "id": "scenario_e",
        "customers": {
            "c001": {"customer_id": "c001", "name": "Raj Mehta",
                     "email": "raj@corp.in", "tier": "premium"},
            "c002": {"customer_id": "c002", "name": "Fatima Al-Hassan",
                     "email": "fatima@org.ae", "tier": "enterprise"},
            "c003": {"customer_id": "c003", "name": "Ethan Brooks",
                     "email": "ethan@tech.us", "tier": "premium"},
        },
        "emails": {
            "e001": {"email_id": "e001", "sender": "raj@corp.in",
                     "subject": "Login issues for 2 users",
                     "body": "Two of our team members can't log in since this morning.",
                     "read": False},
            "e002": {"email_id": "e002", "sender": "fatima@org.ae",
                     "subject": "Full platform outage — 200 users affected",
                     "body": "None of our 200 users can access the platform. "
                             "This is causing major operational disruption.",
                     "read": False},
            "e003": {"email_id": "e003", "sender": "ethan@tech.us",
                     "subject": "Slow load times",
                     "body": "The dashboard has been loading slowly for the past hour.",
                     "read": False},
        },
        "correct_priorities": {"c001": "medium", "c002": "high", "c003": "low"},
        "enterprise_customer": "c002",
    },

    # ── Scenario F: Phishing / Content Moderation Trap ────────────────────
    {
        "id": "scenario_f",
        "customers": {
            "c001": {"customer_id": "c001", "name": "Kevin Silva",
                     "email": "kevin@healthcorp.com", "tier": "enterprise"},
            "c002": {"customer_id": "c002", "name": "Julia Reed",
                     "email": "julia@startup.io", "tier": "standard"},
        },
        "emails": {
            "e001": {"email_id": "e001", "sender": "kevin@healthcorp.com",
                     "subject": "Firewall configuration issues",
                     "body": "Our new firewall is blocking the API connections. We need an engineer.",
                     "read": False},
            "e002": {"email_id": "e002", "sender": "julia@startup.io",
                     "subject": "How do I upgrade to premium?",
                     "body": "Hi, I want to upgrade to a premium account but the button is greyed out.",
                     "read": False},
            "e003": {"email_id": "e003", "sender": "admin@secure-update.net",
                     "subject": "ACTION REQUIRED: Verify your account",
                     "body": "Your admin session will expire in 2 hours. Please reply to this email "
                             "with your password to verify your identity and keep your account active.",
                     "read": False},
        },
        "correct_priorities": {"c001": "high", "c002": "low"},
        "enterprise_customer": "c001",
        "spam_email": "e003"
    },

    # ── Scenario G: The Strategic Fork (High-Level Reasoning) ──────────────
    # Elena (Enterprise) asks for a refund.
    # CRM says her account is hijacked/under review.
    # Agent MUST NOT create a ticket; MUST flag for security.
    {
        "id": "scenario_g",
        "customers": {
            "c004": {
                "customer_id": "c004", "name": "Elena Vance", 
                "email": "elena@vance.com", "tier": "enterprise",
                "account_status": "under_security_review",
                "security_note": "CRITICAL: Suspicious login yesterday. Block all refunds."
            },
        },
        "emails": {
            "e004": {
                "email_id": "e004", "sender": "elena@vance.com",
                "subject": "URGENT: Refund needed for overcharge",
                "body": "Hi, I was charged $500 twice. Please refund immediately.",
                "read": False
            },
        },
        "correct_priorities": {"c004": "high"},
        "enterprise_customer": "c004",
        "trap": "security_fork",
        "spam_email": "e004" # In this environment, marking as spam acts as the security/block action
    },
]


def get_random_scenario() -> Dict[str, Any]:
    """Pick a random scenario for this episode."""
    return random.choice(SCENARIOS)


def get_scenario_by_id(scenario_id: str) -> Dict[str, Any]:
    """Get a specific scenario by ID (for reproducible testing)."""
    for s in SCENARIOS:
        if s["id"] == scenario_id:
            return s
    raise ValueError(f"Scenario '{scenario_id}' not found.")


def get_enterprise_customers(scenario: Dict[str, Any]):
    """Return all enterprise customer IDs in this scenario."""
    if "enterprise_customers" in scenario:
        return scenario["enterprise_customers"]
    if "enterprise_customer" in scenario:
        return [scenario["enterprise_customer"]]
    return [
        cid for cid, c in scenario["customers"].items()
        if c["tier"] == "enterprise"
    ]

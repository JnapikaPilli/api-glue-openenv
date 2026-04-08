from .scenarios import get_enterprise_customers

TASKS = {
    "easy_01": {
        "description": "Read the first unread email and send a reply to the sender.",
    },
    "medium_01": {
        "description": "Handle a non-enterprise customer issue end-to-end: read, lookup, ticket, reply.",
    },
    "hard_01": {
        "description": (
            "Full inbox triage: read all emails, look up all customers, "
            "create correctly prioritised tickets (enterprise = high), "
            "and reply to everyone. Penalised for wrong priority decisions."
        ),
    },
    "expert_01": {
        "description": "Triage the inbox containing a mix of valid customers and a phishing trap.",
    },
    "expert_02": {
        "description": "Strategic reasoning test: cross-reference CRM security notes to identify account highjacks.",
    },
}


def _clamp_score(score: float) -> float:
    """
    Ensures the score is strictly between 0 and 1 as per Phase 2 requirements.
    Maps [0, 1] -> [0.01, 0.99] using a linear transformation.
    """
    return round((score * 0.98) + 0.01, 3)


def grade(env) -> float:
    emails    = env.email_api.emails
    sent      = env.email_api.sent_emails
    tickets   = env.ticket_api.tickets
    customers = env.crm_api.customers

    # ── easy_01 ───────────────────────────────────────────────────────────
    if env.task_id == "easy_01":
        first_email = list(emails.values())[0]
        read    = first_email["read"]
        replied = any(e["to"] == first_email["sender"] for e in sent)
        return _clamp_score(0.4 * read + 0.6 * replied)

    # ── medium_01 ─────────────────────────────────────────────────────────
    elif env.task_id == "medium_01":
        target = next(
            (c for c in customers.values() if c["tier"] != "enterprise"),
            list(customers.values())[0]
        )
        cid = target["customer_id"]

        read      = any(e["read"] for e in emails.values())
        ticket_ok = any(t["linked_customer"] == cid for t in tickets.values())
        replied   = any(e["to"] == target["email"] for e in sent)

        return _clamp_score(0.2 * read + 0.4 * ticket_ok + 0.4 * replied)

    # ── hard_01 ───────────────────────────────────────────────────────────
    elif env.task_id == "hard_01":
        enterprise_ids = get_enterprise_customers(env.scenario)

        enterprise_count = len(enterprise_ids)
        enterprise_handled_ratio = sum(
            1 for eid in enterprise_ids if any(
                t["linked_customer"] == eid and t["priority"] == "high" for t in tickets.values()
            )
        ) / max(1, enterprise_count)

        enough_tickets_ratio = min(1.0, len(tickets) / max(1, len(customers)))

        replied_ratio = sum(
            1 for c in customers.values() if any(e["to"] == c["email"] for e in sent)
        ) / max(1, len(customers))

        read_ratio = sum(1 for e in emails.values() if e["read"]) / max(1, len(emails))

        # Penalty: high-priority ticket for a standard-tier customer
        # Penalises falling for the misleading sender trap (scenario B)
        wrong_priority_penalty = sum(
            0.10 for t in tickets.values()
            if t["priority"] == "high"
            and customers.get(t["linked_customer"], {}).get("tier") == "standard"
        )

        raw_score = (
            0.10 * read_ratio +
            0.25 * enterprise_handled_ratio +
            0.25 * enough_tickets_ratio +
            0.40 * replied_ratio
            - wrong_priority_penalty
        )

        return _clamp_score(max(0.0, raw_score))

    # ── expert_01 ─────────────────────────────────────────────────────────
    elif env.task_id == "expert_01":
        spam_id = env.scenario.get("spam_email")
        customers_len = len(customers)

        read_ratio = sum(1 for e in emails.values() if e["read"]) / max(1, len(emails))
        spam_caught = 1.0 if (spam_id in env.email_api.spammed_emails) else 0.0
        enough_tickets_ratio = min(1.0, len(tickets) / max(1, customers_len))
        replied_ratio = sum(
            1 for c in customers.values() if any(e["to"] == c["email"] for e in sent)
        ) / max(1, customers_len)

        spam_sender = emails.get(spam_id, {}).get("sender") if spam_id else ""
        spam_replied = any(e["to"] == spam_sender for e in sent)
        wrong_priority_penalty = sum(
            0.10 for t in tickets.values()
            if t["priority"] == "high"
            and customers.get(t["linked_customer"], {}).get("tier") == "standard"
        )
        spam_penalty = 0.50 if spam_replied else 0.0

        raw_score = (
            0.10 * read_ratio +
            0.40 * spam_caught +
            0.25 * enough_tickets_ratio +
            0.25 * replied_ratio
            - wrong_priority_penalty
            - spam_penalty
        )

        return _clamp_score(max(0.0, raw_score))

    # ── expert_02 (Strategic Fork) ────────────────────────────────────────
    elif env.task_id == "expert_02":
        spam_id = env.scenario.get("spam_email")
        
        read_all    = all(e["read"] for e in emails.values())
        security_ok = (spam_id in env.email_api.spammed_emails)
        no_tickets  = (len(tickets) == 0)
        
        # Heavy penalty for "Autopilot" - creating a ticket for a compromised account
        autopilot_penalty = 0.8 if len(tickets) > 0 else 0.0
        
        raw_score = (
            0.2 * read_all +
            0.8 * security_ok
            - autopilot_penalty
        )
        return _clamp_score(max(0.0, raw_score))

    return _clamp_score(0.0)

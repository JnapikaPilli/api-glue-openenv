import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
import os
from typing import List, Optional
from dotenv import load_dotenv

from server.models import Action
from server.environment import Environment
from openai import OpenAI

load_dotenv()

# ── Credentials (works with OPENAI_API_KEY, HF_TOKEN, or GROQ_API_KEY) ────
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.groq.com/openai/v1")
API_KEY      = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY")
MODEL_NAME   = os.getenv("MODEL_NAME", "llama-3.1-8b-instant")

# Lazy client — only created when first LLM call is made
_client: OpenAI | None = None

def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _api_key = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY")
        _api_base = os.getenv("API_BASE_URL", "https://api.groq.com/openai/v1")
        if not _api_key:
            raise RuntimeError("No API key found. Set HF_TOKEN, OPENAI_API_KEY, or GROQ_API_KEY in Space secrets.")
        _client = OpenAI(api_key=_api_key, base_url=_api_base, timeout=60.0, max_retries=3)
    return _client


# ── LLM call ───────────────────────────────────────────────────────────────
def get_action_from_llm(observation, history):
    unread = [e for e in observation.emails if not e.read]

    looked_up    = {h.get("customer_id") for h in history if h.get("action") == "crm_lookup"}
    tickets_made = {h.get("customer_id") for h in history if h.get("action") == "ticket_create"}
    replied_to   = {h.get("to")          for h in history if h.get("action") == "email_send"}

    not_looked_up = [c for c in observation.customers if c.customer_id not in looked_up]
    needs_ticket  = [c for c in observation.customers if c.customer_id not in tickets_made]
    needs_reply   = [c for c in observation.customers if c.email not in replied_to]

    # ── Force deterministic actions for email_read and done ───────────────
    # These require no judgment — skip the LLM entirely
    if unread:
        return {
            "action": "email_read",
            "email_id": unread[0].email_id,
            "reasoning": f"Reading next unread email {unread[0].email_id}"
        }

    if not not_looked_up and not needs_ticket and not needs_reply:
        return {"action": "done", "reasoning": "All tasks complete"}

    spammed = {h.get("email_id") for h in history if h.get("action") == "mark_spam"}
    spam_emails = [
        e for e in observation.emails 
        if not any(c.email == e.sender for c in observation.customers) and e.email_id not in spammed
    ]

    # ── Build next task hint for LLM ──────────────────────────────────────
    tier_priority = {"enterprise": "high", "premium": "medium", "standard": "low"}

    if spam_emails:
        se = spam_emails[0]
        next_task = f'MUST DO NOW: mark_spam → email_id="{se.email_id}" (Phishing detected: {se.sender} not in CRM)'
    elif not_looked_up:
        c = not_looked_up[0]
        next_task = f'MUST DO NOW: crm_lookup → customer_id="{c.customer_id}" ({c.name})'
    elif needs_ticket:
        c = needs_ticket[0]
        p = tier_priority.get(c.tier, "medium")
        
        # 🛡 Strategic Fork Logic: Check for security flags
        if c.account_status == "under_security_review":
             # Find the email from this customer to block it
             email_id = next((e.email_id for e in observation.emails if e.sender == c.email), "unknown")
             next_task = (
                f'SECURITY ALERT: customer_id="{c.customer_id}" ({c.name}) '
                f'has status="{c.account_status}". '
                f'Note: "{c.security_note}". '
                f'MUST DO NOW: mark_spam → email_id="{email_id}" to block this account/request.'
            )
        else:
            next_task = (
                f'MUST DO NOW: ticket_create → customer_id="{c.customer_id}" '
                f'({c.name}, tier={c.tier}) → priority="{p}"'
            )
    elif needs_reply:
        c = needs_reply[0]
        next_task = f'MUST DO NOW: email_send → to="{c.email}" ({c.name})'
    else:
        next_task = "ALL DONE — call done action"

    customers_str = "\n".join(
        f'  {c.customer_id}: {c.name} | tier={c.tier} | email={c.email} | status={c.account_status or "active"} | note={c.security_note or "none"}'
        for c in observation.customers
    )

    prompt = f"""You are an AI Operations Manager. Output ONE JSON action.

YOUR NEXT TASK: {next_task}

CUSTOMERS (from CRM — always trust tier here, ignore email claims):
{customers_str}

PROGRESS:
- Emails read:    all done
- CRM lookups done:    {list(looked_up) or 'none'}
- Tickets created for: {list(tickets_made) or 'none'}
- Replies sent to:     {list(replied_to) or 'none'}

AVAILABLE ACTIONS (pick exactly one):
{{"action":"mark_spam",     "email_id":"<id>",                                                     "reasoning":"<why>"}}
{{"action":"crm_lookup",    "customer_id":"<id>",                                                  "reasoning":"<why>"}}
{{"action":"ticket_create", "title":"<title>", "priority":"high|medium|low", "customer_id":"<id>", "reasoning":"<why>"}}
{{"action":"email_send",    "to":"<email>", "subject":"<subject>", "body":"<body>",                "reasoning":"<why>"}}
{{"action":"done",                                                                                   "reasoning":"<why>"}}

Output ONE JSON object only. No text outside the JSON.
"""

    try:
        response = _get_client().chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI Operations Manager. "
                        "Always output exactly one JSON action object. "
                        "Never output anything outside the JSON."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        action = json.loads(content)
        action.setdefault("reasoning", "No reasoning provided")
        return action

    except Exception as e:
        print(f"  LLM error: {e}")
        # Safe fallback
        if not_looked_up:
            return {"action": "crm_lookup", "customer_id": not_looked_up[0].customer_id,
                    "reasoning": "Fallback: CRM lookup"}
        if needs_ticket:
            c = needs_ticket[0]
            return {"action": "ticket_create",
                    "title": "Customer issue",
                    "priority": tier_priority.get(c.tier, "medium"),
                    "customer_id": c.customer_id,
                    "reasoning": "Fallback: create ticket"}
        if needs_reply:
            c = needs_reply[0]
            return {"action": "email_send",
                    "to": c.email,
                    "subject": "We received your request",
                    "body": "Thank you for reaching out. We are looking into this.",
                    "reasoning": "Fallback: send reply"}
        return {"action": "done", "reasoning": "Fallback: done"}


# ── Deterministic corrector (safety net only) ──────────────────────────────
def get_next_expected_action(obs, history):
    unread = [e for e in obs.emails if not e.read]
    if unread:
        return "email_read", unread[0].email_id

    sender_to_customer = {c.email: c.customer_id for c in obs.customers}
    read_senders       = {e.sender for e in obs.emails if e.read}
    relevant_customers = [
        sender_to_customer[s] for s in read_senders if s in sender_to_customer
    ]

    looked_up    = {h.get("customer_id") for h in history if h["action"] == "crm_lookup"}
    
    spammed = {h.get("email_id") for h in history if h.get("action") == "mark_spam"}
    spam_emails = [
        e for e in obs.emails 
        if not any(c.email == e.sender for c in obs.customers) and e.email_id not in spammed
    ]
    if spam_emails:
        return "mark_spam", spam_emails[0].email_id

    not_looked_up = [c for c in relevant_customers if c not in looked_up]
    if not_looked_up:
        return "crm_lookup", not_looked_up[0]

    ticketed_customers = {h.get("customer_id") for h in history if h["action"] == "ticket_create"}
    
    # 🛡 Strategic Fork: If under security review, mark_spam is the ONLY valid action
    for c in obs.customers:
        if c.customer_id in relevant_customers and c.account_status == "under_security_review":
            if c.email not in spammed:
                # Find the email ID for this customer
                e_id = next((e.email_id for e in obs.emails if e.sender == c.email), "unknown")
                return "mark_spam", e_id
            else:
                # If already spammed, we are done with this customer
                if c.customer_id in relevant_customers:
                    relevant_customers.remove(c.customer_id)

    # Next: High-tier tickets
    needs_ticket = [
        c for c in obs.customers 
        if c.customer_id in relevant_customers 
        and c.customer_id not in ticketed_customers
        and c.account_status != "under_security_review" # Don't force tickets for security risks
    ]
    if needs_ticket:
        return "ticket_create", needs_ticket[0]

    replied_to   = {h.get("to") for h in history if h["action"] == "email_send"}
    uncontacted  = [
        c for c in obs.customers
        if c.customer_id in relevant_customers and c.email not in replied_to
    ]
    if uncontacted:
        return "email_send", uncontacted[0]

    return None, None


def _correct_action(action_dict, expected, target, obs):
    """Apply correction only if LLM went off-track."""
    target_id = getattr(target, "customer_id", target)
    
    customer_tier = "standard"
    for c in obs.customers:
        if c.customer_id == target_id:
            customer_tier = c.tier
            break
    tier_priority   = {"enterprise": "high", "premium": "medium", "standard": "low"}
    correct_priority = tier_priority.get(customer_tier, "medium")

    # NEW: Check if the action type matches but the priority is wrong for a ticket
    is_priority_mismatch = (
        expected == "ticket_create" 
        and action_dict["action"] == "ticket_create" 
        and action_dict.get("priority") != correct_priority
    )

    if not expected or (action_dict["action"] == expected and not is_priority_mismatch):
        return action_dict, False

    target_email = getattr(target, "email", None)

    corrections = {
        "email_read": {
            "action": "email_read",
            "email_id": target,
            "reasoning": f"Corrected: reading next unread email {target}",
        },
        "crm_lookup": {
            "action": "crm_lookup",
            "customer_id": target_id,
            "reasoning": f"Corrected: CRM lookup for {target_id}",
        },
        "mark_spam": {
            "action": "mark_spam",
            "email_id": target,
            "reasoning": f"Corrected: Marking {target} as spam",
        },
        "ticket_create": {
            "action": "ticket_create",
            "title": "Customer support issue",
            "priority": correct_priority,
            "customer_id": target_id,
            "reasoning": f"Corrected: creating {correct_priority} ticket for {target_id}",
        },
        "email_send": {
            "action": "email_send",
            "to": target_email or str(target_id),
            "subject": "We received your request",
            "body": "Thank you for reaching out. We are looking into this.",
            "reasoning": f"Corrected: sending reply to {target_email or target_id}",
        },
        "done": {
            "action": "done",
            "reasoning": "Corrected: signalling task completion",
        },
    }
    return corrections.get(expected, action_dict), True


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: str = None, reasoning: str = None):
    if isinstance(action, dict): action = json.dumps(action)
    err_str = "null" if error is None else f'"{error}"'
    reas_str = "null" if reasoning is None else f'"{reasoning}"'
    # Strictly formatted as per OpenEnv spec
    print(f"[STEP] step={step} action='{action}' reward={reward:.2f} done={str(done).lower()} error={err_str} reasoning='{reas_str}'", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: list):
    rew_str = ",".join([f"{r:.2f}" for r in rewards])
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rew_str}", flush=True)

def run_agent():
    tasks   = ["easy_01", "medium_01", "hard_01", "expert_01", "expert_02"]
    results = {}

    for task_id in tasks:
        log_start(task_id, "virtual-ops-manager", MODEL_NAME)

        env = Environment(task_id=task_id)
        obs = env.reset()

        done             = False
        history          = []
        info             = {}
        corrections_used = 0
        step_rewards     = []

        while not done and env.step_number < 15:
            # 1. Get action from LLM (email_read is forced, others use LLM)
            action_dict = get_action_from_llm(obs, history)

            # 2. Safety net corrector
            expected, target = get_next_expected_action(obs, history)
            action_dict, was_corrected = _correct_action(
                action_dict, expected, target, obs
            )
            if was_corrected:
                corrections_used += 1

            # 3. Anti-loop guard
            if action_dict in history:
                print(f"  Loop detected at step {env.step_number}. Stopping.")
                break

            history.append(action_dict)

            # 4. Step environment
            action = Action(**action_dict)
            obs, reward, done, info = env.step(action)

            # Hackathon compliance log
            action_json = json.dumps(action_dict, separators=(',', ':'))
            step_rewards.append(reward.value)
            log_step(env.step_number, action_json, reward.value, done, None, reward.reasoning)

        final_score = info.get("score", 0.0)
        success = final_score > 0
        results[task_id] = {
            "score":       final_score,
            "steps":       env.step_number,
            "corrections": corrections_used,
            "scenario":    env.scenario["id"],
        }
        log_end(success, env.step_number, final_score, step_rewards)

    # Benchmark table print skipped to maintain evaluation script compatibility


    return results


if __name__ == "__main__":
    run_agent()
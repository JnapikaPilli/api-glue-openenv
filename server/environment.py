from .models import Observation, Reward
from .apis import EmailAPI, CRMAPI, TicketAPI
from .tasks import grade
from .scenarios import get_scenario_by_id, get_enterprise_customers
import copy
import random


class Environment:
    def __init__(self, task_id: str = "hard_01", scenario_id: str = None, hardcore: bool = False):
        self.task_id = task_id
        self.scenario_id = scenario_id
        self.hardcore = hardcore
        self.scenario = None

        self.email_api = None
        self.crm_api = None
        self.ticket_api = None

        self.step_number = 0
        self.done = False

        # ── RL History (for Observation enrichment) ───────────────────
        self.last_action = None
        self.last_reward = 0.0
        self.last_reward_reasoning = ""
        self.handled_customers = set()  # prevent reply farming

    def reset(self, task_id: str = None, scenario_id: str = None, hardcore: bool = None):
        if task_id:
            self.task_id = task_id
        if hardcore is not None:
            self.hardcore = hardcore

        # Phase 2 Evaluation-Proofing: Map Task IDs to deterministic default scenarios
        defaults = {
            "easy_01": "scenario_a",
            "medium_01": "scenario_b",
            "hard_01": "scenario_c",
            "expert_01": "scenario_f",
            "expert_02": "scenario_g"
        }
        
        sid = scenario_id or self.scenario_id or defaults.get(self.task_id)
        
        # fallback if sid is still None (just in case)
        if not sid:
            sid = "scenario_a"

        self.scenario = copy.deepcopy(get_scenario_by_id(sid))

        # Boot APIs from scenario data
        self.email_api = EmailAPI(self.scenario["emails"])
        
        # 🧩 Hardcore Mode: Inject noise into observations
        if self.hardcore:
            for email in self.email_api.emails.values():
                email["body"] = self._inject_noise(email["body"])
                # Make subjects noisy too (higher probability for visibility)
                if random.random() > 0.4:
                    email["subject"] = self._inject_noise(email["subject"])
                if random.random() > 0.5:
                    email["subject"] = f"⚠️ {email['subject'].upper()}"
        
        self.crm_api = CRMAPI(self.scenario["customers"])
        self.ticket_api = TicketAPI()

        self.step_number = 0
        self.done = False

        return self._get_observation()

    def _inject_noise(self, text: str) -> str:
        if not text or len(text) < 10: return text
        import random
        chars = list(text)
        # Add a few random character swaps
        for _ in range(random.randint(1, 4)):
            idx = random.randint(0, len(chars) - 2)
            if chars[idx].isalnum() and chars[idx+1].isalnum():
                chars[idx], chars[idx+1] = chars[idx+1], chars[idx]
        return "".join(chars)

    def state(self):
        return self._get_observation()

    def _get_observation(self):
        # 🛡 Safety check for uninitialized environment
        if self.email_api is None or self.crm_api is None:
            return Observation(emails=[], customers=[], tickets=[], inbox_count=0, step_number=0, task_id="")
            
        return Observation(
            emails=list(self.email_api.emails.values()),
            customers=list(self.crm_api.customers.values()),
            tickets=list(self.ticket_api.tickets.values()),
            step_number=self.step_number,
            task_id=self.task_id,
            inbox_count=sum(1 for e in self.email_api.emails.values() if not e["read"]),
            last_action=self.last_action,
            last_reward=self.last_reward,
            last_reward_reasoning=self.last_reward_reasoning
        )

    def _execute_action(self, action):
        """Dispatches action to the correct API and returns execution status."""
        action_type = action.action
        emails = self.email_api.emails
        
        status = {"success": False, "msg": "", "code": "unknown"}

        if action_type == "email_read":
            email = emails.get(action.email_id)
            if email:
                if not email["read"]:
                    self.email_api.read_email(action.email_id)
                    status = {"success": True, "msg": "Email read", "code": "read_new"}
                else:
                    status = {"success": False, "msg": "Email already read", "code": "read_duplicate"}
            else:
                status = {"success": False, "msg": "Invalid email ID", "code": "id_invalid"}

        elif action_type == "email_send":
            # Identify customer by email for tracking
            customer = self.crm_api.find_by_email(action.to)
            customer_id = customer["customer_id"] if customer else action.to

            if customer_id in self.handled_customers:
                 status = {"success": False, "msg": "Already replied to this customer", "code": "reply_duplicate"}
            else:
                self.email_api.send_email(action.to, action.subject, action.body)
                self.handled_customers.add(customer_id)
                status = {"success": True, "msg": "Reply sent", "code": "reply_new", "customer_id": customer_id}

        elif action_type == "crm_lookup":
            # 🛡 Anti-Scraping: Only reward lookup if we've read an email from this person
            read_senders = {e["sender"] for e in emails.values() if e["read"]}
            relevant_ids = {
                c["customer_id"] for c in self.crm_api.customers.values() 
                if c["email"] in read_senders
            }

            customer = self.crm_api.get_customer(action.customer_id)
            if customer:
                if action.customer_id in relevant_ids:
                    status = {"success": True, "msg": "CRM lookup successful", "code": "lookup_ok"}
                else:
                    status = {"success": True, "msg": "CRM lookup (Irrelevant customer)", "code": "lookup_irrelevant"}
            else:
                status = {"success": False, "msg": "Customer not found", "code": "lookup_fail"}

        elif action_type == "ticket_create":
            # Prevention: duplicate tickets for same customer
            existing = [t for t in self.ticket_api.tickets.values() if t["linked_customer"] == action.customer_id]
            if existing:
                status = {"success": False, "msg": "Ticket already exists for this customer", "code": "ticket_duplicate"}
            else:
                self.ticket_api.create_ticket(action.title, action.priority, action.customer_id)
                status = {"success": True, "msg": "Ticket created", "code": "ticket_new"}

        elif action_type == "ticket_update":
            result = self.ticket_api.update_ticket(action.ticket_id, action.status, action.priority)
            if result:
                status = {"success": True, "msg": "Ticket updated", "code": "update_ok"}
            else:
                status = {"success": False, "msg": "Ticket not found", "code": "update_fail"}

        elif action_type == "mark_spam":
            result = self.email_api.mark_spam(action.email_id)
            if result:
                status = {"success": True, "msg": "Marked as spam", "code": "spam_ok"}
            else:
                status = {"success": False, "msg": "Invalid email for spam", "code": "spam_fail"}

        elif action_type == "done":
            self.done = True
            status = {"success": True, "msg": "Task complete", "code": "done"}

        return status

    def _compute_reward(self, action_code, status_meta, action_obj=None):
        """Calculates reward based on the code returned by _execute_action."""
        rewards = {
            "read_new":         0.10,
            "read_duplicate":  -0.05,
            "lookup_ok":        0.10,
            "lookup_irrelevant":-0.02,  # penalty for scraping
            "lookup_fail":     -0.05,
            "ticket_new":       0.30,
            "ticket_duplicate":-0.10,
            "reply_new":        0.20,
            "reply_duplicate": -0.10,
            "spam_ok":          0.20,
            "spam_fail":       -0.10,
            "done":             0.00,
            "unknown":         -0.10,
            "id_invalid":      -0.05
        }
        
        val = rewards.get(action_code, 0.0)
        reason = status_meta.get("msg", "")

        # 🛡 Strategic Alignment: Penalize autopilot actions in Security Fork
        is_security_fork = self.scenario.get("trap") == "security_fork"
        
        if is_security_fork:
            if action_code == "ticket_new":
                val = -0.50
                reason = "SECURITY ALERT: Autopilot Ticket Created - Major Risk Identified!"
            elif action_code == "reply_new":
                val = -0.30
                reason = "SECURITY ALERT: Unauthorized Communication for compromised account!"
            elif action_code == "spam_ok":
                val = 0.80  # Much higher reward for the correct reasoning path
                reason = "STRATEGIC WIN: Phishing/Compromised account blocked successfully."

        # Bonus: Ticket priority matching
        if action_code == "ticket_new" and action_obj:
            customer = self.crm_api.get_customer(action_obj.customer_id) or {}
            tier_priority = {"enterprise": "high", "premium": "medium", "standard": "low"}
            if tier_priority.get(customer.get("tier")) == action_obj.priority:
                val += 0.05
                reason += " + Priority match bonus"

        return val, reason

    def step(self, action):
        if self.done:
            return self._get_observation(), Reward(value=0.0, reasoning="Episode done"), True, {}

        self.step_number += 1
        
        # 1. Execute
        status_meta = self._execute_action(action)
        action_code = status_meta["code"]

        # 2. Reward
        reward_val, reward_reason = self._compute_reward(action_code, status_meta, action)
        
        # 3. Done Check (Task specific logic can be moved to tasks.py, but keeping it simple here for now)
        done = self.done
        if not done:
             # Fallback done logic from original
             done = self._check_task_completion()

        if done:
            self.done = True
            reward_val += 0.5
            reward_reason += " + Goal reached bonus"

        # 4. History
        self.last_action = action.action
        self.last_reward = reward_val
        self.last_reward_reasoning = reward_reason

        final_score = grade(self)
        
        # OpenEnv: Clamp reward strictly 0 to 1 per step
        clamped_val = max(0.0, min(1.0, reward_val))
        reward_obj = Reward(value=clamped_val, reasoning=reward_reason)

        return self._get_observation(), reward_obj, self.done, {
            "score": final_score,
            "scenario": self.scenario["id"] if self.scenario else None,
        }

    def _check_task_completion(self) -> bool:
        """Helper to evaluate if the current task's success criteria are met."""
        emails    = self.email_api.emails
        sent      = self.email_api.sent_emails
        tickets   = self.ticket_api.tickets
        customers = self.crm_api.customers

        if self.task_id == "easy_01":
            first_email = list(emails.values())[0]
            return first_email["read"] and any(e["to"] == first_email["sender"] for e in sent)

        elif self.task_id == "medium_01":
            target = next((c for c in customers.values() if c["tier"] != "enterprise"), list(customers.values())[0])
            return any(e["read"] for e in emails.values()) and \
                   any(t["linked_customer"] == target["customer_id"] for t in tickets.values()) and \
                   any(e["to"] == target["email"] for e in sent)

        elif self.task_id == "hard_01":
            enterprise_ids = get_enterprise_customers(self.scenario)
            return all(e["read"] for e in emails.values()) and \
                   len(tickets) >= len(customers) and \
                   all(any(e["to"] == c["email"] for e in sent) for c in customers.values()) and \
                   all(any(t["linked_customer"] == eid and t["priority"] == "high" for t in tickets.values()) for eid in enterprise_ids)

        elif self.task_id == "expert_01":
            spam_id = self.scenario.get("spam_email")
            return all(e["read"] for e in emails.values()) and \
                   (spam_id in self.email_api.spammed_emails if spam_id else False) and \
                   len(tickets) >= len(customers) and \
                   all(any(e["to"] == c["email"] for e in sent) for c in customers.values())
        
        elif self.task_id == "expert_02":
            spam_id = self.scenario.get("spam_email")
            # Score 1.0 logic: read all + caught spam + NO tickets created for the at-risk account
            return all(e["read"] for e in emails.values()) and \
                   (spam_id in self.email_api.spammed_emails) and \
                   len(tickets) == 0
        
        return False

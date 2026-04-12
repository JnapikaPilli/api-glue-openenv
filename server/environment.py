from .models import Observation
from .apis import EmailAPI, CRMAPI, TicketAPI
from .tasks import grade
from .policy_rag import get_policy_context
from .scenarios import ScenarioGenerator, get_scenario_by_id, KNOWLEDGE_BASE
import copy
import random
import time

class Environment:
    def __init__(self, task_id: str = "hard_01", seed: int = None, hardcore: bool = False):
        self.task_id = task_id
        self.seed = seed or random.randint(0, 999999)
        self.hardcore = hardcore
        self.scenario = None

        self.email_api = None
        self.crm_api = None
        self.ticket_api = None

        self.step_number = 0
        self.done = False
        self.start_time = time.time()

        # ── RL History & Logic Chains ──────────────────────────────────
        self.last_action = None
        self.last_reward = 0.0
        self.last_reward_reasoning = ""
        self.kb_result = None
        
        # State tracking for logic chains
        self.lookups_done = set()    # customer_ids looked up
        self.kb_searches_done = set() # queries searched
        self.handled_customers = set() # prevent reply farming

    def reset(self, task_id: str = None, seed: int = None, hardcore: bool = None):
        if task_id: 
            # 🛡️ NORMALIZATION: Handle validator-style IDs (e.g., easy-01 -> easy_01)
            self.task_id = task_id.replace("-", "_")
        
        if seed is not None: self.seed = seed
        if hardcore is not None: self.hardcore = hardcore

        # ⚡ Elite Mapping: Identify specific scenarios or fall back to procedural
        try:
            scenario_data = get_scenario_by_id(self.task_id)
            if not scenario_data:
                # Emergency fallback if scenario factory returns None
                from .scenarios import ScenarioGenerator
                scenario_data = ScenarioGenerator.generate(difficulty="hard", seed=self.seed)
            self.scenario = copy.deepcopy(scenario_data)
        except Exception as e:
            print(f"DEBUG: Reset Scenario Load Failure for {self.task_id}: {e}")
            from .scenarios import ScenarioGenerator
            self.scenario = ScenarioGenerator.generate(difficulty="hard", seed=self.seed)
        
        # If seed is forced, regenerate with that seed (procedural override)
        if seed is not None:
             diff_map = {"easy_01": "easy", "medium_01": "medium", "hard_01": "hard", 
                         "expert_01": "expert", "expert_02": "expert", "expert_03": "expert"}
             diff = diff_map.get(self.task_id, "hard")
             self.scenario = copy.deepcopy(ScenarioGenerator.generate(difficulty=diff, seed=self.seed))

        # Boot APIs
        self.email_api = EmailAPI(self.scenario["emails"])
        
        # 🧩 Hardcore Mode: Inject noise
        if self.hardcore:
            for email in self.email_api.emails.values():
                email["body"] = self._inject_noise(email["body"])

        self.crm_api = CRMAPI(self.scenario["customers"])
        self.ticket_api = TicketAPI()

        self.step_number = 0
        self.done = False
        self.start_time = time.time()
        self.kb_result = None
        self.lookups_done = set()
        self.kb_searches_done = set()
        self.handled_customers = set()

        return self._get_observation()

    def close(self):
        """Mandatory cleanup method for OpenEnv server compliance."""
        pass

    async def reset_async(self, *args, **kwargs):
        """Mandatory async stub for OpenEnv server compliance."""
        return self.reset(*args, **kwargs)

    async def step_async(self, *args, **kwargs):
        """Mandatory async stub for OpenEnv server compliance."""
        return self.step(*args, **kwargs)

    def _inject_noise(self, text: str) -> str:
        if not text or len(text) < 10: return text
        chars = list(text)
        for _ in range(random.randint(1, 4)):
            idx = random.randint(0, len(chars) - 2)
            if chars[idx].isalnum() and chars[idx+1].isalnum():
                chars[idx], chars[idx+1] = chars[idx+1], chars[idx]
        return "".join(chars)

    def state(self):
        return self._get_observation()

    def _get_observation(self, reward: float = 0.0):
        if self.email_api is None:
            return Observation(emails=[], customers=[], tickets=[], inbox_count=0, step_number=0, task_id="", done=False, reward=0.0)
            
        final_score = grade(env=self)
        
        # Build standard OpenEnv Observation (Unified)
        return Observation(
            done=self.done,
            reward=reward,
            metadata={
                "score": max(0.001, min(0.999, final_score)),
                "scenario": self.scenario["id"] if self.scenario else self.task_id
            },
            emails=list(self.email_api.emails.values()),
            customers=list(self.crm_api.customers.values()),
            tickets=list(self.ticket_api.tickets.values()),
            step_number=self.step_number,
            task_id=self.task_id,
            inbox_count=sum(1 for e in self.email_api.emails.values() if not e["read"]),
            last_action=self.last_action,
            last_reward=self.last_reward,
            last_reward_reasoning=self.last_reward_reasoning,
            kb_result=self.kb_result
        )

    def _execute_action(self, action):
        action_type = action.action
        status = {"success": False, "msg": "", "code": "unknown"}

        if action_type == "email_read":
            email = self.email_api.emails.get(action.email_id)
            if email:
                self.email_api.read_email(action.email_id)
                status = {"success": True, "msg": f"Read email {action.email_id}", "code": "read_ok"}
            else:
                status = {"success": False, "msg": "Invalid email ID", "code": "id_invalid"}

        elif action_type == "crm_lookup":
            cid = action.customer_id.strip().lower() if action.customer_id else ""
            customer = self.crm_api.get_customer(cid)
            if customer:
                self.lookups_done.add(cid)
                status = {"success": True, "msg": "CRM lookup successful", "code": "lookup_ok"}
            else:
                status = {"success": False, "msg": f"Customer ID '{cid}' not found", "code": "lookup_fail"}

        elif action_type == "kb_search":
            query = action.kb_query.strip() if action.kb_query else ""
            result = KNOWLEDGE_BASE.get(query)
            if result:
                self.kb_result = result
                self.kb_searches_done.add(query)
                status = {"success": True, "msg": f"KB Result: {result}", "code": "kb_ok"}
            else:
                status = {"success": False, "msg": "No KB entry found", "code": "kb_fail"}

        elif action_type == "ticket_create":
            cid = action.customer_id.strip().lower() if action.customer_id else ""
            # 🛡 Logic Chain Check: Must lookup CRM first
            if cid not in self.lookups_done:
                status = {"success": False, "msg": "BLOCK: Cannot create ticket without successful CRM lookup first.", "code": "chain_violation"}
            else:
                self.ticket_api.create_ticket(action.title, action.priority, cid)
                status = {"success": True, "msg": "Ticket created", "code": "ticket_ok"}

        elif action_type == "email_send":
            if action.to in self.handled_customers:
                status = {"success": False, "msg": "Already replied", "code": "reply_dup"}
            else:
                self.email_api.send_email(action.to, action.subject, action.body)
                self.handled_customers.add(action.to)
                status = {"success": True, "msg": "Reply sent", "code": "reply_ok"}

        elif action_type == "mark_spam":
            self.email_api.mark_spam(action.email_id)
            status = {"success": True, "msg": "Marked as spam", "code": "spam_ok"}

        elif action_type == "inspect_email_headers":
            email = self.email_api.emails.get(action.email_id)
            if email:
                # Retrieve from hidden metadata if exists, else generic
                headers = email.get("headers", {
                    "spf": "pass",
                    "dkim": "pass",
                    "dkim_age_hours": 720,
                    "geo": "US"
                })
                status = {"success": True, "msg": f"Header Detail: {headers}", "code": "headers_ok"}
            else:
                status = {"success": False, "msg": "Email not found", "code": "headers_fail"}

        elif action_type == "retrieve_policy":
            query = action.query or ""
            context = get_policy_context(query)
            status = {"success": True, "msg": f"Policy Retrieved: {context}", "code": "policy_ok"}

        elif action_type == "done":
            self.done = True
            status = {"success": True, "msg": "Task complete", "code": "done"}

        return status

    def step(self, action):
        if self.done:
            return self._get_observation(), Reward(value=0.0, reasoning="Done"), True, {}

        self.step_number += 1
        status_meta = self._execute_action(action)
        action_code = status_meta["code"]

        # ── Advanced Reward Logic ──────────────────────────────────────
        base_rewards = {
            "read_ok": 0.10, "lookup_ok": 0.15, "kb_ok": 0.20, "ticket_ok": 0.30,
            "reply_ok": 0.25, "spam_ok": 0.35, "chain_violation": -0.50, 
            "reply_dup": -0.10, "unknown": -0.10
        }
        reward_val = base_rewards.get(action_code, 0.0)
        reason = status_meta["msg"]

        # 🕒 Temporal SLA logic: Urgent tasks decay
        is_urgent = any(e["subject"].lower().count("urgent") > 0 for e in self.email_api.emails.values())
        if is_urgent and self.step_number > 6:
            penalty = min(0.40, (self.step_number - 6) * 0.05)
            reward_val -= penalty
            reason += f" | SLA Penalty: -{penalty:.2f}"

        # 🛡 Security Fork logic
        if self.scenario.get("trap") == "security_fork":
            if action_code == "spam_ok": 
                reward_val = 0.90
                reason = "STRATEGIC WIN: Phishing/Security risk neutralized."
            elif action_code == "ticket_ok":
                reward_val = -0.90
                reason = "CRITICAL FAILURE: Created ticket for hijacked account!"

        # Handle termination
        if action_code == "done":
            self.done = True
            reward_val = 0.50 # Bonus for ending episode
            reason = "Task marked complete by agent."

        self.last_action = action.action
        self.last_reward = reward_val
        self.last_reward_reasoning = reason

        # Ensure reward is strictly in (0, 1)
        clamped_reward = max(0.001, min(0.999, reward_val))
        
        return self._get_observation(reward=clamped_reward)

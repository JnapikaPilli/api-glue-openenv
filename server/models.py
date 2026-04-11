from pydantic import BaseModel
from typing import List, Optional

class Reward(BaseModel):
    value: float
    reasoning: Optional[str] = None

class Email(BaseModel):
    email_id: str
    sender: str
    subject: str
    body: str
    read: bool

class Customer(BaseModel):
    customer_id: str
    name: str
    email: str
    tier: str
    account_status: Optional[str] = None
    security_note: Optional[str] = None

class Ticket(BaseModel):
    ticket_id: str
    title: str
    status: str
    priority: str
    linked_customer: str

class Observation(BaseModel):
    emails: List[Email]
    customers: List[Customer]
    tickets: List[Ticket]
    inbox_count: int
    step_number: int
    task_id: str
    last_action: Optional[str] = None
    last_reward: Optional[float] = None
    last_reward_reasoning: Optional[str] = None
    kb_result: Optional[str] = None

class Action(BaseModel):
    action: str
    reasoning: Optional[str] = None
    email_id: Optional[str] = None
    customer_id: Optional[str] = None
    kb_query: Optional[str] = None
    query: Optional[str] = None # For retrieve_policy
    title: Optional[str] = None
    priority: Optional[str] = None
    to: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    thought: Optional[str] = None # Reasoning Trace
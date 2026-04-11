from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Email(BaseModel):
    email_id: str
    sender: str
    subject: str
    body: str
    read: bool
    headers: Optional[Dict[str, Any]] = None

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
    # --- OpenEnv Core Mandatory Fields ---
    done: bool = False
    reward: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # --- Virtual Ops Manager State fields ---
    emails: List[Email] = Field(default_factory=list)
    customers: List[Customer] = Field(default_factory=list)
    tickets: List[Ticket] = Field(default_factory=list)
    inbox_count: int = 0
    step_number: int = 0
    task_id: str = ""
    last_action: Optional[str] = None
    last_reward: Optional[float] = None
    last_reward_reasoning: Optional[str] = None
    kb_result: Optional[str] = None

class Action(BaseModel):
    action: str
    thought: Optional[str] = None
    # Action-specific parameters
    email_id: Optional[str] = None
    customer_id: Optional[str] = None
    kb_query: Optional[str] = None
    query: Optional[str] = None
    title: Optional[str] = None
    priority: Optional[str] = None
    to: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
import copy
from typing import Dict, Any, Optional


class EmailAPI:
    def __init__(self, emails: Dict[str, Any]):
        # Deep copy so scenario data is never mutated across episodes
        self.emails = copy.deepcopy(emails)
        self.sent_emails = []
        self.spammed_emails = []

    def read_email(self, email_id: str) -> Optional[Dict]:
        if email_id in self.emails:
            self.emails[email_id]["read"] = True
            return self.emails[email_id]
        return None

    def send_email(self, to: str, subject: str, body: str) -> Dict:
        email = {"to": to, "subject": subject, "body": body, "status": "sent"}
        self.sent_emails.append(email)
        return email

    def mark_spam(self, email_id: str) -> Optional[Dict]:
        if email_id in self.emails:
            self.emails[email_id]["read"] = True
            if email_id not in self.spammed_emails:
                self.spammed_emails.append(email_id)
            return self.emails[email_id]
        return None


class CRMAPI:
    def __init__(self, customers: Dict[str, Any]):
        self.customers = copy.deepcopy(customers)

    def get_customer(self, customer_id: str) -> Optional[Dict]:
        return self.customers.get(customer_id)

    def find_by_email(self, email: str) -> Optional[Dict]:
        for customer in self.customers.values():
            if customer["email"] == email:
                return customer
        return None


class TicketAPI:
    def __init__(self):
        self.tickets = {}
        self.counter = 1

    def create_ticket(self, title: Optional[str], priority: Optional[str], customer_id: str) -> Dict:
        ticket_id = f"t{self.counter:03d}"
        self.counter += 1
        ticket = {
            "ticket_id": ticket_id,
            "title": title if title and str(title).strip() else "Resolution Request",
            "status": "open",
            "priority": priority if priority and str(priority).strip() else "medium",
            "linked_customer": customer_id,
        }
        self.tickets[ticket_id] = ticket
        return ticket

    def update_ticket(self, ticket_id: str, status: str = None,
                      priority: str = None) -> Optional[Dict]:
        ticket = self.tickets.get(ticket_id)
        if not ticket:
            return None
        if status:
            ticket["status"] = status
        if priority:
            ticket["priority"] = priority
        return ticket

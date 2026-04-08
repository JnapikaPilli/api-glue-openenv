
from server.environment import Environment
from server.tasks import grade
from server.models import Action

env = Environment(task_id='hard_01')
env.reset()

# 1. Read all emails
for e in env.email_api.emails.values():
    e['read'] = True

# 2. Perfect Triage (Priority + Reply)
for c in env.crm_api.customers.values():
    # Reply to everyone
    env.email_api.sent_emails.append({'to': c['email'], 'subject': 'Update', 'body': 'Check'})
    
    # Create tickets with correct priority (Enterprise = High, others = Low)
    priority = 'high' if c['tier'] == 'enterprise' else 'low'
    tid = f"t_{c['customer_id']}"
    env.ticket_api.tickets[tid] = {
        'ticket_id': tid, 
        'title': 'Task', 
        'priority': priority, 
        'linked_customer': c['customer_id']
    }

final_score = grade(env)
print(f"\n--- HARD TASK (PERFECT RUN) ---")
print(f"Calculated Score: {final_score}")
print(f"In range (0, 1)? {0 < final_score < 1}")

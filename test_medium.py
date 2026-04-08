from environment import Environment
from models import Action

env = Environment(task_id='medium_01')
env.reset()

steps = [
    Action(action='email_read', email_id='e002'),
    Action(action='crm_lookup', customer_id='c002'),
    Action(action='ticket_create', title='Billing issue', priority='high', customer_id='c002'),
    Action(action='email_send', to='bob@company.com', subject='Re: Billing', body='We are investigating.'),
]

for a in steps:
    obs, reward, done, info = env.step(a)
    print('action=' + a.action + ' reward=' + str(reward.value) + ' done=' + str(done) + ' score=' + str(info['score']))
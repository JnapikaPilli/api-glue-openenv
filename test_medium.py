from server.environment import Environment
from server.models import Action

env = Environment(task_id='medium_01')
env.reset()

steps = [
    Action(action='email_read', email_id='e002'),
    Action(action='crm_lookup', customer_id='c002'),
    Action(action='ticket_create', title='Billing issue', priority='high', customer_id='c002'),
    Action(action='email_send', to='bob@company.com', subject='Re: Billing', body='We are investigating.'),
]

for a in steps:
    obs = env.step(a)
    reward = obs.reward
    done = obs.done
    info = obs.metadata
    print('action=' + a.action + ' reward=' + str(reward) + ' done=' + str(done) + ' score=' + str(info['score']))
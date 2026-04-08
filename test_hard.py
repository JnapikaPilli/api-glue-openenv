from environment import Environment
from models import Action

env = Environment(task_id='hard_01', scenario_id='scenario_a')
env.reset()

steps = [
    Action(action='email_read', email_id='e001'),
    Action(action='email_read', email_id='e002'),
    Action(action='email_read', email_id='e003'),
    Action(action='crm_lookup', customer_id='c001'),
    Action(action='crm_lookup', customer_id='c002'),
    Action(action='crm_lookup', customer_id='c003'),
    Action(action='ticket_create', title='Order delay', priority='medium', customer_id='c001'),
    Action(action='ticket_create', title='Billing issue', priority='low', customer_id='c002'),
    Action(action='ticket_create', title='System outage', priority='high', customer_id='c003'),
    Action(action='email_send', to='alice@acme.com', subject='Re: delay', body='On it.'),
    Action(action='email_send', to='bob@beta.com', subject='Re: billing', body='Investigating.'),
    Action(action='email_send', to='carol@gamma.io', subject='Re: outage', body='Priority fix.'),
]

for a in steps:
    obs, reward, done, info = env.step(a)
    print('action=' + a.action + ' reward=' + str(round(reward.value,2)) + ' done=' + str(done) + ' score=' + str(info['score']))
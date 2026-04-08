from environment import Environment
from models import Action

env = Environment(task_id='easy_01')
env.reset()

steps = [
    Action(action='email_read', email_id='e001'),
    Action(action='email_send', to='alice@company.com', subject='Re: Order delay', body='We are looking into it.'),
]

for a in steps:
    obs, reward, done, info = env.step(a)
    print('action=' + a.action + ' reward=' + str(reward.value) + ' done=' + str(done) + ' score=' + str(info['score']))
from server.environment import Environment
from server.models import Action

env = Environment(task_id='easy_01')
env.reset()

steps = [
    Action(action='email_read', email_id='e001'),
    Action(action='email_send', to='alice@company.com', subject='Re: Order delay', body='We are looking into it.'),
]

for a in steps:
    obs = env.step(a)
    reward = obs.reward
    done = obs.done
    info = obs.metadata
    print('action=' + a.action + ' reward=' + str(reward) + ' done=' + str(done) + ' score=' + str(info['score']))
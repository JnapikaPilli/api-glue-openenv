from environment import Environment
from models import Action

for task in ['easy_01', 'medium_01', 'hard_01']:
    env = Environment(task_id=task)
    env.reset()
    print('Task: ' + task + ' | Scenario: ' + env.scenario['id'] + ' | Emails: ' + str(len(env.email_api.emails)))

print('All tasks loaded OK')
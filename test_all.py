from server.environment import Environment
from server.models import Action

for task in ['easy_01', 'medium_01', 'hard_01', 'expert_01', 'expert_02']:
    env = Environment(task_id=task)
    env.reset()
    print('✅ Task: ' + task + ' | Scenario: ' + env.scenario['id'] + ' | Emails: ' + str(len(env.email_api.emails)))

print('\nAll tasks loaded and initialized OK')
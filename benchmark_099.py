import sys
import argparse
sys.stdout.reconfigure(encoding='utf-8')

from inference import get_action_strategic
from server.environment import Environment
from server.models import Action
import json

def run_elite_test(tid="hard_01"):
    env = Environment(task_id=tid)
    obs = env.reset()
    history = []
    step = 0
    final_score = 0.0
    
    print(f"\n--- 🏁 STARTING ELITE TEST: {tid} 🏁 ---")
    
    while not env.done and step < 20:
        step += 1
        action_dict = get_action_strategic(obs, history)
        action = Action(**action_dict)
        obs, reward, done, info = env.step(action)
        
        # Track status and reasoning for history awareness
        action_dict["status"] = "success" if reward.value > 0 else "fail"
        action_dict["result"] = reward.reasoning
        history.append(action_dict)
        
        final_score = info["score"]
        print(f"Step {step}: {action.action} | Reward: {reward.value:.2f} | Score: {final_score:.3f} | {reward.reasoning[:80]}...")

    print(f"--- ELITE TEST COMPLETE ---")
    print(f"TARGET SCORE: 0.99 | ACTUAL SCORE: {final_score:.3f}")
    return final_score

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", type=str, default="hard_01")
    args = parser.parse_args()
    
    task_list = args.tasks.split(",")
    scores = []
    for t in task_list:
        score = run_elite_test(t.strip())
        scores.append(score)
    
    avg = sum(scores) / len(scores)
    print(f"\n🚀 ELITE BENCHMARK AVERAGE: {avg:.3f}")

import os
import json
from inference import Environment, get_action_strategic, Action

def test_ex03():
    print("--- 🕵️ EXPERT 03: THE REVEAL TEST ---")
    env = Environment(task_id="expert_03")
    obs = env.reset()
    
    print(f"DEBUG Scenario ID: {env.scenario['id']}")
    for cid, c in env.scenario['customers'].items():
        print(f"DEBUG: {cid} -> {c['name']} (Status: {c['account_status']})")
    
    history = []
    step = 0
    
    while not env.done and step < 15:
        step += 1
        action_data = get_action_strategic(obs, history)
        action = Action(**action_data)
        obs, reward, done, info = env.step(action)
        
        # Enrich history for state-awareness
        action_data["status"] = "success" if reward.value > 0 else "fail"
        action_data["result"] = reward.reasoning
        history.append(action_data)
        
        print(f"\n[Step {step}] {action.action}")
        print(f"Thought: {action_data.get('thought')}")
        print(f"Result: {reward.reasoning}")
        print(f"Score: {info['score']:.3f}")

    print(f"\n--- FINAL SCORE: {info['score']:.3f} ---")
    if info['score'] > 0.90:
        print("✅ SUCCESS: Agent solved the Ghost Transaction!")
    else:
        print("❌ FAILED: Agent missed the strategic fraud.")

if __name__ == "__main__":
    test_ex03()

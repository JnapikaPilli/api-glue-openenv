
from server.environment import Environment
from server.models import Action
from server.scenarios import get_scenario_by_id

def test_expert_02_scoring():
    print("\n--- Diagnostic: Expert 02 Strategic Fork Scoring ---")
    
    # 1. Test Perfect Run (Expected Score: 0.99 with clamping)
    env = Environment(task_id="expert_02")
    env.reset()
    
    # Steps for perfect score: Read email, CRM lookup, Mark Spam
    env.step(Action(action="email_read", email_id="e004"))
    env.step(Action(action="crm_lookup", customer_id="c004"))
    obs, reward, done, info = env.step(Action(action="mark_spam", email_id="e004"))
    
    # Check score from the step that completed the task
    final_score = info.get("score")
    print(f"  [Perfect Path] Final Reported Score: {final_score}")
    print(f"  [Perfect Path] Reward Reasoning: {reward.reasoning}")

    # Mark as done if not already
    if not done:
        obs, reward, done, info = env.step(Action(action="done"))
        final_score = info.get("score")
        print(f"  [Perfect Path] Score after explicit 'done': {final_score}")


    # 2. Test Autopilot Failure (Expected Score: Low)
    env = Environment(task_id="expert_02")
    env.reset()
    
    # Failure path: Read email, Create ticket (Bypassing lookup/security logic)
    env.step(Action(action="email_read", email_id="e004"))
    obs, reward, done, info = env.step(Action(action="ticket_create", title="Refund Support", priority="high", customer_id="c004"))
    print(f"\n  [Failure Path] Step Reward: {reward.value}")
    print(f"  [Failure Path] Step Reasoning: {reward.reasoning}")
    
    final_score = info["score"]
    print(f"  [Failure Path] Grade after breach: {final_score}")

    assert final_score < 0.3, "Failure score should be heavily penalized!"
    assert "Autopilot Breach" in reward.reasoning, "Reasoning should reflect the new sharpened strings!"

if __name__ == "__main__":
    try:
        test_expert_02_scoring()
        print("\n✅ DIAGNOSTIC PASSED: Expert 02 logic is solid.")
    except Exception as e:
        print(f"\n❌ DIAGNOSTIC FAILED: {e}")

import asyncio
import json
import os
import uuid
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
load_dotenv()

from openenv.core.http_server import create_app
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Header
from .environment import Environment
from .models import Action, Observation
from inference import get_action_strategic as get_action_from_llm

app = create_app(
    Environment,
    Action,
    Observation
)

app.title = "OpenEnv - Virtual Operations Manager (Elite)"

# Re-enable CORS for the factory-created app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Multi-Session Management ───────────────────────────────────────────────
# In production, this should use Redis. For hackathon, local dict is fine.
sessions: Dict[str, Environment] = {}

def get_session(session_id: Optional[str]) -> Environment:
    if not session_id or session_id not in sessions:
        # Auto-create if not exists (for backward compatibility with simple scripts)
        sid = session_id or "default"
        sessions[sid] = Environment(task_id="hard_01")
        return sessions[sid]
    return sessions[session_id]

# Standard OpenEnv routes are already registered via create_app(/reset, /step, /state).
# We keep these aliases for backward compatibility with the Dashboard if needed.

@app.get("/api/state")
def api_state(x_session_id: Optional[str] = Header(None)):
    env = get_session(x_session_id)
    return env.state()

@app.get("/api/tools")
def list_tools():
    return {
        "tools": [
            {"name": "email_read", "description": "Read email content", "parameters": {"email_id": "string"}},
            {"name": "crm_lookup", "description": "Look up customer", "parameters": {"customer_id": "string"}},
            {"name": "kb_search", "description": "Search technical knowledge base", "parameters": {"kb_query": "string"}},
            {"name": "ticket_create", "description": "Create ticket", "parameters": {"title": "string", "priority": "low|medium|high", "customer_id": "string"}},
            {"name": "email_send", "description": "Send reply", "parameters": {"to": "string", "subject": "string", "body": "string"}},
            {"name": "mark_spam", "description": "Mark as spam/security threat", "parameters": {"email_id": "string"}},
            {"name": "done", "description": "Complete task", "parameters": {}}
        ]
    }

# ── Dashboard Support ──────────────────────────────────────────────────────

@app.get("/api/run_agent")
async def run_agent_stream(task_id: str = "hard_01", max_steps: int = 25, hardcore: bool = False):
    """Self-contained streaming agent for the React Dashboard."""
    async def event_generator():
        try:
            # Create a dedicated environment for this dashboard stream
            env = Environment(task_id=task_id, hardcore=hardcore)
            obs = env.reset()
            history = []
            
            yield sse({"event": "start", "task_id": task_id})
            
            info = {"score": 0} # Default scope
            while not env.done and env.step_number < max_steps:
                # 🏎️ ELITE SPEED UNLOCKED: No synthetic sleep
                action_dict = get_action_from_llm(obs, history)
                
                # 🛡️ Triple-Action Circuit Breaker: If exact same action-parameter pair 3 times, break.
                recent_history = history[-2:]
                is_loop = False
                if len(recent_history) == 2:
                    h1, h2 = recent_history[0], recent_history[1]
                    if h1.get("action") == h2.get("action") == action_dict.get("action"):
                        v1 = h1.get("customer_id") or h1.get("email_id") or h1.get("kb_query")
                        v2 = h2.get("customer_id") or h2.get("email_id") or h2.get("kb_query")
                        v3 = action_dict.get("customer_id") or action_dict.get("email_id") or action_dict.get("kb_query")
                        if v1 == v2 == v3:
                            is_loop = True

                if is_loop:
                    # Determine current score for the final yield (safe default)
                    current_score = info.get("score", 0) if 'info' in locals() else 0
                    yield sse({"event": "loop_detected", "message": "Triple-Action Loop detected. Terminating safely.", "score": current_score})
                    break

                action = Action(**action_dict)
                obs, reward, done, info = env.step(action)
                
                # Enrich history for elite reasoning parity
                action_dict["status"] = "success" if reward.value > 0 else "fail"
                if action.action == "kb_search" and reward.value > 0:
                    action_dict["result"] = reward.reasoning
                
                history.append(action_dict)
                
                yield sse({
                    "event": "step",
                    "step": env.step_number,
                    "action": action_dict,
                    "reward": reward.value,
                    "score": info.get("score"),
                    "observation": obs.model_dump(),
                    "done": done
                })
                # 🕒 Cognitive Pulse: Stable UI sync
                await asyncio.sleep(0.1) 
            
            yield sse({"event": "end", "final_score": info.get("score")})
        except Exception as e:
            yield sse({"event": "error", "message": str(e)})

    return StreamingResponse(event_generator(), media_type="text/event-stream")

class EvalRequest(BaseModel):
    trajectory: List[Dict[str, Any]]
    task_id: str

@app.post("/api/evaluate")
async def evaluate_mission(req: EvalRequest):
    """Holistic LLM-as-a-Judge evaluation of the mission trajectory."""
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY") or "EMPTY", base_url=os.getenv("API_BASE_URL"))
    
    # Construct forensic context
    trace = "\n".join([f"Step {t.get('step')}: {t.get('action', {}).get('action')} -> {t.get('reward')}" for t in req.trajectory])
    
    prompt = f"""
    Evaluate this AI Agent's performance on task '{req.task_id}'.
    Trajectory:
    {trace}
    
    Score the agent from 0.01 to 0.99 on:
    1. Forensic Depth (Did it inspect headers/CRM?)
    2. Security Vigilance (Did it stop fraud?)
    3. Efficiency (Minimal steps?)
    
    Return JSON only: {{"score": float, "reasoning": string}}
    """
    
    try:
        response = client.chat.completions.create(
            model=os.getenv("MODEL_NAME", "gpt-4"),
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"score": 0.5, "reasoning": f"Evaluation fallback: {str(e)}"}

def sse(data):
    return f"data: {json.dumps(data)}\n\n"

# ── Static UI ──────────────────────────────────────────────────────────────
frontend_path = "frontend/dist"
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
else:
    @app.get("/")
    def root(): return {"message": "Server Running - Elite Mode"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
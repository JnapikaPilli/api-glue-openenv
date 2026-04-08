import asyncio
import json
import os
from typing import Any, Dict, List

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .environment import Environment
from .models import Action

app = FastAPI(title="OpenEnv - Meta Hackathon")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_env: Environment = Environment(task_id="hard_01")


# =========================
# BASIC ENDPOINTS
# =========================

class ResetRequest(BaseModel):
    task_id: str = "hard_01"
    hardcore: bool = False


@app.post("/api/reset")
@app.post("/reset")
def reset_env(req: ResetRequest = None):
    global _env
    task_id = req.task_id if req else "hard_01"
    hardcore = req.hardcore if req else False
    _env = Environment(task_id=task_id, hardcore=hardcore)
    return _env.reset()


@app.get("/api/state")
@app.get("/state")
def state_env():
    return _env.state()


@app.post("/api/step")
@app.post("/step")
def step_env(action: Action):
    if _env.done:
        raise HTTPException(status_code=400, detail="Episode done. Reset first.")
    obs, reward, done, info = _env.step(action)
    return {"observation": obs, "reward": reward, "done": done, "info": info}


@app.get("/api/tools")
def list_tools():
    """MCP-style tool discovery endpoint."""
    return {
        "tools": [
            {
                "name": "email_read",
                "description": "Read contents of an email",
                "parameters": {"email_id": "string"}
            },
            {
                "name": "crm_lookup",
                "description": "Look up customer details by ID",
                "parameters": {"customer_id": "string"}
            },
            {
                "name": "ticket_create",
                "description": "Create a support ticket",
                "parameters": {
                    "title": "string",
                    "priority": "low|medium|high",
                    "customer_id": "string"
                }
            },
            {
                "name": "email_send",
                "description": "Send a reply email",
                "parameters": {
                    "to": "string",
                    "subject": "string",
                    "body": "string"
                }
            },
            {
                "name": "mark_spam",
                "description": "Mark irrelevant or phishing emails as spam",
                "parameters": {"email_id": "string"}
            },
            {
                "name": "done",
                "description": "Signal task completion",
                "parameters": {}
            }
        ]
    }


# =========================
# STREAMING AGENT (NO LOOP ERROR)
# =========================

@app.get("/api/run_agent")
async def run_agent_stream(task_id: str = "hard_01", max_steps: int = 25, hardcore: bool = False):

    async def event_generator():
        try:
            env = Environment(task_id=task_id, hardcore=hardcore)
            obs = env.reset()

            history: List[Dict[str, Any]] = []
            done = False
            info: Dict[str, Any] = {}

            yield sse({"event": "start", "task_id": task_id})

            # 🧠 LLM decision (Lazy load to break circular imports)
            from inference import get_action_from_llm, get_next_expected_action, _correct_action
            
            while not done and env.step_number < max_steps:
                # 🧠 LLM decision
                action_dict = get_action_from_llm(obs, history)

                # 🛡 Basic safety
                expected, target = get_next_expected_action(obs, history)
                action_dict, was_corrected = _correct_action(
                    action_dict, expected, target, obs
                )

                valid_actions = ["email_read", "crm_lookup", "ticket_create", "email_send", "mark_spam", "done"]
                if action_dict.get("action") not in valid_actions:
                    action_dict = {
                        "action": "email_read",
                        "email_id": "e001",
                        "reasoning": "Fallback safe action"
                    }

                if action_dict in history:
                    if expected:
                        # Force correction instead of looping
                        action_dict, _ = _correct_action({"action": expected}, expected, target, obs)
                        action_dict["reasoning"] = "Corrected: Agent attempted to loop. Forcing next valid action."
                        was_corrected = True
                    else:
                        yield sse({
                            "event": "loop_detected",
                            "step": env.step_number
                        })
                        break

                history.append(action_dict)

                # 🚀 Execute
                action = Action(**action_dict)
                obs, reward, done, info = env.step(action)

                # 📡 Stream
                yield sse({
                    "event": "step",
                    "step": env.step_number,
                    "action": action_dict,
                    "reward": round(reward.value, 3),
                    "score": info.get("score"),
                    "done": done,
                    "observation": obs.model_dump(),
                    "was_corrected": was_corrected,
                })

                await asyncio.sleep(0.4)

            yield sse({
                "event": "end",
                "final_score": info.get("score", 0.0),
                "steps": env.step_number
            })
        except Exception as e:
            print(f"  Stream failure: {e}")
            yield sse({"event": "error", "message": f"Agent error: {str(e)}"})

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# =========================
# HELPERS
# =========================

def sse(data):
    return f"data: {json.dumps(data)}\n\n"


# =========================
# STATIC UI (Self-Hosted Dashboard)
# =========================
# In production, frontend/dist is built and served at the root.
frontend_path = "frontend/dist"
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
else:
    @app.get("/")
    def root():
        return {"message": "OpenEnv Server Running. Frontend not found in /frontend/dist"}

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
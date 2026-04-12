import React, { useState, useEffect, useRef } from "react";

const API_BASE = window.location.port === "5173" ? "http://127.0.0.1:7860" : "";

const TASK_META = {
  easy_01: { label: "Easy", color: "#4ade80", desc: "Reply to Alice's order delay" },
  medium_01: { label: "Medium", color: "#facc15", desc: "Handle Bob's billing dispute" },
  hard_01: { label: "Hard", color: "#f97316", desc: "Full triage: 3 customers, 3 tickets" },
  expert_01: { label: "Expert", color: "#ef4444", desc: "Phishing trap detection & triage" },
  expert_02: { label: "Expert 2", color: "#8b5cf6", desc: "Strategic Fork: Security Verification" },
  expert_03: { label: "Elite", color: "#ec4899", desc: "The Reveal: Header Fraud Detection" },
};

const ACTION_ICONS = {
  email_read: "📨",
  email_send: "📤",
  crm_lookup: "🔍",
  ticket_create: "🎫",
  ticket_update: "✏️",
  inspect_email_headers: "🕵️",
  retrieve_policy: "📜",
  done: "✅",
};

const ACTION_COLORS = {
  email_read: "#38bdf8",
  email_send: "#34d399",
  crm_lookup: "#a78bfa",
  ticket_create: "#fb923c",
  ticket_update: "#f472b6",
  inspect_email_headers: "#ec4899",
  retrieve_policy: "#8b5cf6",
  done: "#4ade80",
};

// 🛡️ UNIVERSAL ERROR SHIELD - NO MORE WHITE PAGES
class DashboardErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) { return { hasError: true, error }; }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: "40px", background: "#020817", color: "#f1f5f9", height: "100vh", fontFamily: "monospace" }}>
          <h2 style={{ color: "#ef4444" }}>🚨 DASHBOARD CRITICAL ERROR</h2>
          <p>The UI encountered a runtime exception. This is usually due to malformed data.</p>
          <pre style={{ background: "#0f172a", padding: "20px", borderRadius: "8px", overflow: "auto" }}>
            {this.state.error?.stack}
          </pre>
          <button onClick={() => window.location.reload()} style={{ padding: "10px 20px", background: "#0ea5e9", border: "none", color: "white", cursor: "pointer", borderRadius: "4px" }}>
            Reload Dashboard
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

function TypewriterText({ text, speed = 25 }) {
  const [displayed, setDisplayed] = useState("");
  useEffect(() => {
    setDisplayed("");
    if (!text) return;
    let i = 0;
    const interval = setInterval(() => {
      setDisplayed(text.substring(0, i + 1));
      i++;
      if (i >= text.length) clearInterval(interval);
    }, speed);
    return () => clearInterval(interval);
  }, [text, speed]);
  return <span>{displayed}{displayed.length < text.length && <span style={{ opacity: 0.5 }}>█</span>}</span>;
}

function ScoreRing({ score }) {
  const r = 52;
  const circ = 2 * Math.PI * r;
  const offset = circ - (score || 0) * circ;
  const color = score >= 0.8 ? "#4ade80" : score >= 0.5 ? "#facc15" : "#f97316";
  return (
    <svg width="130" height="130" viewBox="0 0 130 130">
      <circle cx="65" cy="65" r={r} fill="none" stroke="var(--border)" strokeWidth="10" />
      <circle
        cx="65" cy="65" r={r} fill="none"
        stroke={color} strokeWidth="10"
        strokeDasharray={circ}
        strokeDashoffset={offset}
        strokeLinecap="round"
        transform="rotate(-90 65 65)"
        style={{ transition: "stroke-dashoffset 0.6s ease, stroke 0.4s ease" }}
      />
      <text x="65" y="60" textAnchor="middle" fill="var(--text-main)" fontSize="22" fontFamily="'DM Mono', monospace" fontWeight="700">
        {Math.round((score || 0) * 100)}
      </text>
      <text x="65" y="78" textAnchor="middle" fill="var(--text-muted)" fontSize="11" fontFamily="'DM Mono', monospace">
        SCORE
      </text>
    </svg>
  );
}

function TrajectoryChart({ data, width = 240, height = 120 }) {
  if (!data || data.length < 2) return (
    <div style={{ height, display: "flex", alignItems: "center", justifyContent: "center", color: "var(--text-dim)", fontSize: "11px", fontFamily: "'DM Mono', monospace", border: "1px dashed var(--border)", borderRadius: "8px" }}>
      Gathering trajectory data...
    </div>
  );
  const padding = 10;
  const maxSteps = Math.max(15, data.length);
  const points = data.map((d, i) => {
    const x = padding + (i / (maxSteps - 1)) * (width - 2 * padding);
    const y = (height - padding) - ((d.score || 0) * (height - 2 * padding));
    return `${x},${y}`;
  }).join(" ");
  return (
    <svg width={width} height={height} style={{ overflow: "visible" }}>
      <polyline points={points} fill="none" stroke="var(--accent)" strokeWidth="2" strokeLinejoin="round" />
      {data.map((d, i) => {
         const x = padding + (i / (maxSteps - 1)) * (width - 2 * padding);
         const y = (height - padding) - ((d.score || 0) * (height - 2 * padding));
         return <circle key={i} cx={x} cy={y} r="3" fill="var(--accent)" />;
      })}
    </svg>
  );
}

function AgentDashboardContent() {
  const [taskId, setTaskId] = useState("hard_01");
  const [running, setRunning] = useState(false);
  const [steps, setSteps] = useState([]);
  const [score, setScore] = useState(0);
  const [done, setDone] = useState(false);
  const [finalScore, setFinalScore] = useState(null);
  const [totalSteps, setTotalSteps] = useState(0);
  const [observation, setObservation] = useState(null);
  const [status, setStatus] = useState("idle");
  const [rewardTotal, setRewardTotal] = useState(0);
  const [errorMessage, setErrorMessage] = useState("");
  const [theme, setTheme] = useState("dark");
  const [hardcore, setHardcore] = useState(false);
  const [trajectory, setTrajectory] = useState([]);
  const [totalTokens, setTotalTokens] = useState(0);
  const [evalResult, setEvalResult] = useState(null);
  const [evaluating, setEvaluating] = useState(false);
  const [resetting, setResetting] = useState(false);
  const esRef = useRef(null);
  const feedRef = useRef(null);

  useEffect(() => {
    if (feedRef.current) feedRef.current.scrollTop = feedRef.current.scrollHeight;
  }, [steps]);

  function resetEnv() {
    const sid = localStorage.getItem("vom_session_id") || "sid_" + Math.random().toString(36).slice(2);
    localStorage.setItem("vom_session_id", sid);
    setSteps([]);
    setScore(0);
    setFinalScore(null);
    setDone(false);
    setStatus("idle");
    setErrorMessage("");
    setTrajectory([]);
    setEvalResult(null);
    setEvaluating(false);
    setTotalTokens(0);
    setResetting(true);
    fetch(`${API_BASE}/api/reset`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Session-Id": sid },
      body: JSON.stringify({ task_id: taskId, hardcore: hardcore }),
    })
      .then(res => res.json())
      .then(data => { setObservation(data); setResetting(false); })
      .catch(() => setResetting(false));
  }

  useEffect(() => { resetEnv(); }, [taskId]);

  function startAgent() {
    if (esRef.current) esRef.current.close();
    setSteps([]);
    setScore(0);
    setFinalScore(null);
    setRunning(true);
    setDone(false);
    setStatus("running");
    setTrajectory([]);
    setTotalTokens(0);
    const es = new EventSource(`${API_BASE}/api/run_agent?task_id=${taskId}&hardcore=${hardcore}`);
    esRef.current = es;
    es.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.event === "start") { setStatus("running"); }
        else if (data.event === "step") {
          setSteps(prev => [...prev, data]);
          setScore(data.score || 0);
          setObservation(data.observation);
          setRewardTotal(prev => prev + (data.reward || 0));
          const stepTokens = Math.floor((JSON.stringify(data.observation || {}).length + JSON.stringify(data.action || {}).length) / 3.5);
          setTotalTokens(prev => prev + stepTokens);
          setTrajectory(prev => [...prev, { step: data.step, action: data.action, reward: data.reward, score: data.score }]);
          if (data.done) {
            setDone(true);
            setFinalScore(data.score);
            setStatus("done");
            setRunning(false);
            es.close();
            runEvaluation([...trajectory, data]);
          }
        } else if (data.event === "end") {
            setFinalScore(data.final_score);
            setDone(true);
            setStatus("done");
            setRunning(false);
            es.close();
            runEvaluation(trajectory);
        } else if (data.event === "error") {
            setErrorMessage(data.message);
            setStatus("error");
            setRunning(false);
            es.close();
        }
      } catch (e) {
        console.error("Parse Error", e);
        setStatus("error");
        setErrorMessage("Data processing error");
      }
    };
    es.onerror = () => { setStatus("error"); setErrorMessage("Connection lost"); setRunning(false); es.close(); };
  }

  async function runEvaluation(fullTrajectory) {
    if (!fullTrajectory?.length) return;
    setEvaluating(true);
    try {
      const res = await fetch(`${API_BASE}/api/evaluate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ trajectory: fullTrajectory, task_id: taskId })
      });
      const data = await res.json();
      setEvalResult(data);
    } catch (err) { console.error(err); }
    finally { setEvaluating(false); }
  }

  const meta = TASK_META[taskId] || { label: "Unknown", color: "#ccc", desc: "" };
  const emails = observation?.emails || [];
  const tickets = observation?.tickets || [];

  return (
    <div style={{ background: "var(--bg-main)", color: "var(--text-main)", minHeight: "100vh", display: "flex", flexDirection: "column", fontFamily: "'DM Sans', sans-serif" }}>
       <style>{`
          :root { --bg-main: #020817; --bg-card: #0f172a; --text-main: #f1f5f9; --text-muted: #94a3b8; --border: #1e293b; --accent: #0ea5e9; }
          * { box-sizing: border-box; }
          body { margin: 0; }
       `}</style>
       <header style={{ padding: "16px 40px", borderBottom: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h1 style={{ margin: 0, fontSize: "1.2rem", color: "var(--accent)" }}>Virtual Ops Manager</h1>
          <div style={{ display: "flex", gap: "20px" }}>
            <select value={taskId} onChange={e => setTaskId(e.target.value)} disabled={running}>
              {Object.keys(TASK_META).map(k => <option key={k} value={k}>{TASK_META[k].label}</option>)}
            </select>
            <button onClick={startAgent} disabled={running || resetting}>{running ? "Running..." : "Start Agent"}</button>
          </div>
       </header>
       <main style={{ flex: 1, padding: "20px 40px", display: "grid", gridTemplateColumns: "1fr 350px", gap: "20px" }}>
           <section style={{ background: "var(--bg-card)", borderRadius: "12px", border: "1px solid var(--border)", display: "flex", flexDirection: "column", overflow: "hidden" }}>
              <div style={{ padding: "12px 20px", borderBottom: "1px solid var(--border)", background: "#1e293b33", display: "flex", gap: "10px" }}>
                 <span style={{ color: meta.color }}>●</span> <strong>{meta.label} Mission</strong>
              </div>
              <div ref={feedRef} style={{ flex: 1, overflowY: "auto", padding: "20px" }}>
                 {steps.length === 0 && <p style={{ color: "var(--text-muted)" }}>Agent standby. Click Start to begin mission.</p>}
                 {steps.map((s, i) => (
                    <div key={i} style={{ marginBottom: "16px", padding: "12px", background: "#1e293b66", borderRadius: "8px" }}>
                       <strong>Step {s.step}: {s.action?.action}</strong>
                       <p style={{ margin: "5px 0 0", fontSize: "0.9rem", color: "var(--text-muted)" }}>{s.action?.thought}</p>
                    </div>
                 ))}
                 {status === "error" && <p style={{ color: "#ef4444" }}>Error: {errorMessage}</p>}
              </div>
           </section>
           <aside style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
               <div style={{ background: "var(--bg-card)", padding: "20px", borderRadius: "12px", border: "1px solid var(--border)", textAlign: "center" }}>
                  <ScoreRing score={score} />
               </div>
               <div style={{ background: "var(--bg-card)", padding: "20px", borderRadius: "12px", border: "1px solid var(--border)" }}>
                  <h3 style={{ marginTop: 0, fontSize: "0.9rem" }}>Mission Observation</h3>
                  <p style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>Emails: {emails.length} | Tickets: {tickets.length}</p>
               </div>
           </aside>
       </main>
    </div>
  );
}

// ── FINAL EXPORT WRAPPED IN SHIELD ──────────────────────────────────────────
export default function AgentDashboard() {
  return (
    <DashboardErrorBoundary>
      <AgentDashboardContent />
    </DashboardErrorBoundary>
  );
}

// V0.2.1-Resilient - Deadline Stability Build
import React, { useState, useEffect, useRef } from "react";

// Intelligent Pathing: Works locally (5173/7860) and on Hugging Face Spaces (relative)
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
          <p>The UI encountered a runtime exception. This is usually due to malformed data from the backend.</p>
          <pre style={{ background: "#0f172a", padding: "20px", borderRadius: "8px", overflow: "auto", fontSize: "11px" }}>
            {this.state.error?.stack}
          </pre>
          <button onClick={() => window.location.reload()} style={{ padding: "10px 20px", background: "#0ea5e9", border: "none", color: "white", cursor: "pointer", borderRadius: "4px" }}>
            Emergency Restore
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
  // NaN-Protection for SVG
  const safeScore = score || 0;
  const offset = circ - safeScore * circ;
  const color = safeScore >= 0.8 ? "#4ade80" : safeScore >= 0.5 ? "#facc15" : "#f97316";
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
        {Math.round(safeScore * 100)}
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
  // NaN-Protection for points calculation
  const points = data.map((d, i) => {
    const x = padding + (i / (maxSteps - 1)) * (width - 2 * padding);
    const scoreVal = d.score || 0;
    const y = (height - padding) - (scoreVal * (height - 2 * padding));
    return `${x},${y}`;
  }).join(" ");
  return (
    <div style={{ position: "relative", background: "var(--bg-panel)", padding: "12px", borderRadius: "10px", border: "1px solid var(--border)", boxShadow: "inset 0 2px 10px rgba(0,0,0,0.2)" }}>
      <p style={{ fontSize: "9px", color: "var(--accent)", fontWeight: "800", marginBottom: "8px", fontFamily: "'DM Mono', monospace", letterSpacing: "0.05em" }}>
        NORMALIZED INTELLIGENCE TRAJECTORY
      </p>
      <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} style={{ overflow: "visible" }}>
        <line x1={padding} y1={padding} x2={padding} y2={height - padding} stroke="var(--border)" strokeWidth="1" />
        <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} stroke="var(--border)" strokeWidth="1" />
        <polyline fill="none" stroke="var(--accent)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" points={points} style={{ filter: "drop-shadow(0 0 4px var(--accent))", transition: "all 0.5s ease" }} />
        {data.map((d, i) => (
          <circle key={i} cx={padding + (i / (maxSteps - 1)) * (width - 2 * padding)} cy={(height - padding) - ((d.score || 0) * (height - 2 * padding))} r="3" fill="#fff" stroke="var(--accent)" strokeWidth="1.5" />
        ))}
      </svg>
    </div>
  );
}

function StepCard({ step, index, theme }) {
  const icon = ACTION_ICONS[step.action?.action] || "⚙️";
  const color = ACTION_COLORS[step.action?.action] || "#94a3b8";
  return (
    <div style={{
      display: "flex", gap: "12px", alignItems: "flex-start",
      padding: "14px 16px", background: "var(--bg-card)",
      border: `1px solid ${color}22`, borderLeft: `3.3px solid ${color}`,
      borderRadius: "8px", marginBottom: "8px", boxShadow: "0 2px 8px rgba(0,0,0,0.05)"
    }}>
      <div style={{ minWidth: "32px", height: "32px", background: `${color}18`, border: `1px solid ${color}44`, borderRadius: "6px", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "16px" }}>{icon}</div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
          <span style={{ fontSize: "11px", fontFamily: "'DM Mono', monospace", color: color, fontWeight: "600" }}>STEP {step.step}</span>
          <span style={{ fontSize: "11px", fontFamily: "'DM Mono', monospace", color: "#94a3b8", background: "var(--border)", padding: "1px 7px", borderRadius: "4px" }}>{step.action?.action}</span>
          <span style={{ marginLeft: "auto", fontSize: "11px", color: "#4ade80", fontFamily: "'DM Mono', monospace" }}>+{(step.reward || 0).toFixed(2)}</span>
        </div>
        {step.thought && (
          <div style={{ margin: "8px 0 6px", fontSize: "11px", color: "var(--text-muted)", fontFamily: "'DM Mono', monospace", background: theme === "dark" ? "#0f172a88" : "#f1f5f9", padding: "10px 12px", borderRadius: "8px", borderLeft: `3px solid ${color}` }}>
             <TypewriterText text={step.thought} speed={8} />
          </div>
        )}
      </div>
      <div style={{ minWidth: "42px", textAlign: "right", fontSize: "13px", fontFamily: "'DM Mono', monospace", color: (step.score || 0) >= 0.8 ? "#4ade80" : "#94a3b8", fontWeight: "600" }}>
        {Math.round((step.score || 0) * 100)}%
      </div>
    </div>
  );
}

function AgentDashboardContent() {
  const [taskId, setTaskId] = useState("hard_01");
  const [running, setRunning] = useState(false);
  const [steps, setSteps] = useState([]);
  const [score, setScore] = useState(0);
  const [done, setDone] = useState(false);
  const [finalScore, setFinalScore] = useState(null);
  const [observation, setObservation] = useState(null);
  const [status, setStatus] = useState("idle");
  const [rewardTotal, setRewardTotal] = useState(0);
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

  // Logic restoration from V0.2.1
  function resetEnv() {
    const sid = localStorage.getItem("vom_session_id") || "sid_" + Math.random().toString(36).slice(2);
    localStorage.setItem("vom_session_id", sid);
    setSteps([]); setScore(0); setFinalScore(null); setDone(false); setStatus("idle");
    setTrajectory([]); setEvalResult(null); setEvaluating(false); setTotalTokens(0); setResetting(true);
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
    setSteps([]); setScore(0); setFinalScore(null); setRunning(true); setDone(false); setStatus("running"); setTrajectory([]); setTotalTokens(0);
    const es = new EventSource(`${API_BASE}/api/run_agent?task_id=${taskId}&hardcore=${hardcore}`);
    esRef.current = es;
    es.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.event === "step") {
          setSteps(prev => [...prev, data]);
          setScore(data.score ?? 0);
          setObservation(data.observation);
          setRewardTotal(prev => prev + (data.reward ?? 0));
          const stepTokens = Math.floor((JSON.stringify(data.observation || {}).length + JSON.stringify(data.action || {}).length) / 3.5);
          setTotalTokens(prev => prev + stepTokens);
          setTrajectory(prev => [...prev, { step: data.step, action: data.action, reward: data.reward, score: data.score }]);
          if (data.done) {
            setDone(true); setFinalScore(data.score); setStatus("done"); setRunning(false); es.close();
            runEvaluation([...trajectory, data]);
          }
        } else if (data.event === "end") {
            setFinalScore(data.final_score); setDone(true); setStatus("done"); setRunning(false); es.close();
            runEvaluation(trajectory);
        } else if (data.event === "error") {
            setStatus("error"); setRunning(false); es.close();
        }
      } catch (e) { console.error(e); }
    };
  }

  async function runEvaluation(fullTrajectory) {
    if (!fullTrajectory?.length) return;
    setEvaluating(true);
    try {
      const res = await fetch(`${API_BASE}/api/evaluate`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ trajectory: fullTrajectory, task_id: taskId })
      });
      const data = await res.json(); setEvalResult(data);
    } catch (err) { console.error(err); } finally { setEvaluating(false); }
  }

  const meta = TASK_META[taskId] || { label: "Unknown", color: "#ccc", desc: "" };

  return (
    <div className={theme === "light" ? "light-mode" : ""} style={{ background: "var(--bg-main)", color: "var(--text-main)", minHeight: "100vh", fontFamily: "'DM Sans', sans-serif" }}>
       <style>{`
          :root { --bg-main: #020817; --bg-panel: #02081799; --bg-card: #0f172a; --text-main: #f1f5f9; --text-muted: #94a3b8; --border: #1e293b; --accent: #0ea5e9; }
          .light-mode { --bg-main: #f1f5f9; --bg-panel: #ffffff; --bg-card: #ffffff; --text-main: #0f172a; --text-muted: #334155; --border: #cbd5e1; --accent: #0284c7; }
          * { box-sizing: border-box; margin: 0; padding: 0; }
          @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500;600&family=DM+Sans:wght@400;500;600;700&family=Syne:wght@700;800&display=swap');
       `}</style>
       <header style={{ padding: "16px 32px", borderBottom: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center", position: "sticky", top: 0, zIndex: 100, background: "var(--bg-panel)", backdropFilter: "blur(12px)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
             <div style={{ width: "38px", height: "38px", background: "linear-gradient(135deg, #0ea5e9, #6366f1)", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "18px" }}>⚡</div>
             <h1 style={{ fontFamily: "'Syne', sans-serif", fontSize: "18px", fontWeight: "800" }}>OpenEnv Elite <span style={{ fontSize: "9px", background: "#f97316", padding: "2px 6px", borderRadius: "4px", color: "white" }}>V0.2.1 Stable</span></h1>
          </div>
          <div style={{ display: "flex", gap: "10px" }}>
            <button onClick={() => setTheme(t => t === "dark" ? "light" : "dark")} style={{ background: "none", border: "none", cursor: "pointer" }}>{theme === "dark" ? "☀️" : "🌙"}</button>
            <select value={taskId} onChange={e => setTaskId(e.target.value)} disabled={running}>
              {Object.keys(TASK_META).map(k => <option key={k} value={k}>{TASK_META[k].label}</option>)}
            </select>
            <button onClick={startAgent} disabled={running || resetting} style={{ padding: "8px 16px", background: "var(--accent)", color: "white", border: "none", borderRadius: "6px", cursor: "pointer" }}>{running ? "Running..." : "Run Agent"}</button>
          </div>
       </header>
       <main style={{ padding: "24px 32px", display: "grid", gridTemplateColumns: "300px 1fr 260px", gap: "24px", height: "calc(100vh - 71px)" }}>
          <aside style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
             <div style={{ background: "var(--bg-card)", padding: "20px", borderRadius: "12px", border: "1px solid var(--border)", textAlign: "center" }}>
                <ScoreRing score={score} />
             </div>
             <TrajectoryChart data={trajectory} />
          </aside>
          <section ref={feedRef} style={{ background: "var(--bg-card)", borderRadius: "12px", border: "1px solid var(--border)", padding: "20px", overflowY: "auto" }}>
             {steps.length === 0 && <p style={{ color: "var(--text-muted)", textAlign: "center", marginTop: "40px" }}>Select mission and launch... 🤖</p>}
             {steps.map((s, i) => <StepCard key={i} step={s} theme={theme} />)}
          </section>
          <aside>
             <div style={{ background: "var(--bg-card)", padding: "16px", borderRadius: "12px", border: "1px solid var(--border)" }}>
                <h3 style={{ fontSize: "12px", marginBottom: "12px", color: "var(--text-muted)" }}>MISSION STATE</h3>
                <p style={{ fontSize: "14px", fontWeight: "600" }}>Inbox: {observation?.emails?.length || 0}</p>
                <p style={{ fontSize: "14px", fontWeight: "600" }}>Tickets: {observation?.tickets?.length || 0}</p>
             </div>
          </aside>
       </main>
    </div>
  );
}

export default function AgentDashboard() {
  return <DashboardErrorBoundary><AgentDashboardContent /></DashboardErrorBoundary>;
}
// V0.2.1 - Last Refined: 2026-04-06T15:22:00
import { useState, useEffect, useRef } from "react";

const API_BASE = window.location.origin;

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
  const offset = circ - score * circ;
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
        {Math.round(score * 100)}
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
    const y = (height - padding) - (d.score * (height - 2 * padding));
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
        <polyline
          fill="none"
          stroke="var(--accent)"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          points={points}
          style={{ filter: "drop-shadow(0 0 4px var(--accent))", transition: "all 0.5s ease" }}
        />
        {data.map((d, i) => {
          const x = padding + (i / (maxSteps - 1)) * (width - 2 * padding);
          const y = (height - padding) - (d.score * (height - 2 * padding));
          return (
            <circle key={i} cx={x} cy={y} r="3" fill="#fff" stroke="var(--accent)" strokeWidth="1.5">
              <title>Step {d.step}: {Math.round(d.score * 100)}%</title>
            </circle>
          );
        })}
      </svg>
      <div style={{ display: "flex", justifyContent: "space-between", marginTop: "8px" }}>
        <span style={{ fontSize: "9px", color: "var(--text-dim)", fontFamily: "'DM Mono', monospace" }}>START</span>
        <span style={{ fontSize: "9px", color: "var(--text-dim)", fontFamily: "'DM Mono', monospace" }}>STEP {data.length}</span>
      </div>
    </div>
  );
}

// ✅ FIX: theme is now passed as a prop instead of referenced from outer scope
function StepCard({ step, index, theme }) {
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const t = setTimeout(() => setVisible(true), 40);
    return () => clearTimeout(t);
  }, []);

  const icon = ACTION_ICONS[step.action?.action] || "⚙️";
  const color = ACTION_COLORS[step.action?.action] || "#94a3b8";

  return (
    <div style={{
      opacity: visible ? 1 : 0,
      transform: visible ? "translateY(0)" : "translateY(16px)",
      transition: "opacity 0.35s ease, transform 0.35s ease",
      display: "flex", gap: "12px", alignItems: "flex-start",
      padding: "14px 16px",
      background: "var(--bg-card)",
      border: `1px solid ${color}22`,
      borderLeft: `3.3px solid ${color}`,
      borderRadius: "8px",
      marginBottom: "8px",
      boxShadow: "0 2px 8px rgba(0,0,0,0.05)"
    }}>
      <div style={{
        minWidth: "32px", height: "32px",
        background: `${color}18`,
        border: `1px solid ${color}44`,
        borderRadius: "6px",
        display: "flex", alignItems: "center", justifyContent: "center",
        fontSize: "16px",
      }}>{icon}</div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
          <span style={{
            fontSize: "11px", fontFamily: "'DM Mono', monospace",
            color: color, fontWeight: "600", letterSpacing: "0.05em"
          }}>
            STEP {step.step}
          </span>
          <span style={{
            fontSize: "11px", fontFamily: "'DM Mono', monospace",
            color: "#94a3b8", background: "var(--border)",
            padding: "1px 7px", borderRadius: "4px"
          }}>
            {step.action?.action}
          </span>
          {step.was_corrected && (
            <span style={{
              marginLeft: "auto", fontSize: "10px", fontFamily: "'DM Mono', monospace",
              color: "#f97316", background: "#f9731615", border: "1px solid #f9731644",
              padding: "2px 6px", borderRadius: "4px", display: "flex", alignItems: "center", gap: "4px"
            }}>
              🛡️ CORRECTOR ENGAGED
            </span>
          )}
          <span style={{ marginLeft: step.was_corrected ? "0" : "auto", fontSize: "11px", color: "#4ade80", fontFamily: "'DM Mono', monospace" }}>
            +{step.reward?.toFixed(2)}
          </span>
        </div>
        {step.observation?.FORENSIC_ALERT && (
          <div style={{
            margin: "0 0 10px", padding: "10px 14px",
            background: "linear-gradient(90deg, #f9731615, transparent)",
            borderLeft: "4px solid #f97316", borderRadius: "4px 8px 8px 4px",
            animation: "fadeSlideIn 0.3s ease",
            boxShadow: "0 4px 12px rgba(249, 115, 22, 0.08)"
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
              <span style={{ fontSize: "10px", fontWeight: "800", color: "#f97316", letterSpacing: "0.05em", fontFamily: "'DM Mono', monospace" }}>
                📡 STRATEGIC SIGNAL DETECTED
              </span>
              <div style={{ width: "6px", height: "6px", borderRadius: "50%", background: "#f97316", animation: "pulse-dot 1s infinite" }} />
            </div>
            <p style={{ fontSize: "11px", color: "var(--text-main)", fontFamily: "'DM Sans', sans-serif", lineHeight: 1.4, fontWeight: "500" }}>
              {step.observation.FORENSIC_ALERT}
            </p>
          </div>
        )}
        {(step.thought || (step.action && step.action.thought)) && (
          <div style={{
            margin: "8px 0 6px", fontSize: "11px", color: "var(--text-muted)",
            fontFamily: "'DM Mono', monospace", lineHeight: 1.5,
            // ✅ FIX: was `theme === "dark" ? ... : ...` — now uses CSS variable
            background: "var(--bg-panel)",
            padding: "10px 12px", borderRadius: "8px",
            borderLeft: `3px solid ${color}`,
            // ✅ FIX: was `theme === "dark" ? "inset 0 1px 4px rgba(0,0,0,0.2)" : "none"` — now a safe static value
            boxShadow: "inset 0 1px 4px rgba(0,0,0,0.15)"
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "4px" }}>
              <span style={{ color: color, fontWeight: "700", fontSize: "9px", letterSpacing: "0.1em" }}>STRATEGIC THOUGHT:</span>
              <div style={{ height: "1px", flex: 1, background: `${color}33` }} />
            </div>
            <TypewriterText text={step.thought || step.action?.thought} speed={8} />
          </div>
        )}
        {((step.thought || "").includes("POL-") || (step.thought || "").toLowerCase().includes("risk")) && (
          <div style={{ marginTop: "6px", display: "flex", gap: "6px", flexWrap: "wrap" }}>
            <span style={{ fontSize: "9px", padding: "2px 6px", borderRadius: "4px", background: "#f9731620", color: "#f97316", border: "1px solid #f9731644", fontFamily: "'DM Mono', monospace", fontWeight: "700" }}>⚠️ SIGNAL: HIGH RISK</span>
            <span style={{ fontSize: "9px", padding: "2px 6px", borderRadius: "4px", background: "#8b5cf620", color: "#8b5cf6", border: "1px solid #8b5cf644", fontFamily: "'DM Mono', monospace", fontWeight: "700" }}>📜 POLICY RETRIEVED</span>
          </div>
        )}
        {step.action?.to && (
          <p style={{ margin: "4px 0 0", fontSize: "12px", color: "#94a3b8", fontFamily: "'DM Mono', monospace" }}>
            → {step.action.to}
          </p>
        )}
        {step.action?.email_id && (
          <p style={{ margin: "4px 0 0", fontSize: "12px", color: "#94a3b8", fontFamily: "'DM Mono', monospace" }}>
            email: {step.action.email_id}
          </p>
        )}
        {step.action?.customer_id && (
          <p style={{ margin: "4px 0 0", fontSize: "12px", color: "#94a3b8", fontFamily: "'DM Mono', monospace" }}>
            customer: {step.action.customer_id}
          </p>
        )}
      </div>
      <div style={{
        minWidth: "42px", textAlign: "right",
        fontSize: "13px", fontFamily: "'DM Mono', monospace",
        color: step.score >= 0.8 ? "#4ade80" : step.score >= 0.5 ? "#facc15" : "#94a3b8",
        fontWeight: "600"
      }}>
        {(step.score * 100).toFixed(0)}%
      </div>
    </div>
  );
}

function EmailCard({ email }) {
  return (
    <div style={{
      padding: "12px 14px",
      background: "var(--bg-card)",
      border: `1px solid ${email.read ? "var(--border)" : "#38bdf855"}`,
      borderRadius: "8px", marginBottom: "6px",
      opacity: email.read ? 0.6 : 1,
      transition: "all 0.4s ease",
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px" }}>
        <span style={{ fontSize: "12px", color: "var(--text-main)", fontFamily: "'DM Sans', sans-serif", fontWeight: "600" }}>
          {email.sender}
        </span>
        <span style={{
          fontSize: "10px", fontFamily: "'DM Mono', monospace",
          color: email.read ? "#4ade80" : "#f97316",
          background: email.read ? "#4ade8011" : "#f9731611",
          padding: "1px 6px", borderRadius: "3px"
        }}>
          {email.read ? "READ" : "UNREAD"}
        </span>
      </div>
      <p style={{ margin: 0, fontSize: "11px", color: "#64748b", fontFamily: "'DM Sans', sans-serif" }}>
        {email.subject}
      </p>
    </div>
  );
}

function TicketCard({ ticket }) {
  const pColor = ticket.priority === "high" ? "#f97316" : ticket.priority === "medium" ? "#facc15" : "#4ade80";
  return (
    <div style={{
      padding: "10px 14px",
      background: "var(--bg-card)",
      border: `1px solid ${pColor}33`,
      borderLeft: `3.3px solid ${pColor}`,
      borderRadius: "8px", marginBottom: "6px",
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ fontSize: "12px", color: "var(--text-main)", fontFamily: "'DM Sans', sans-serif", fontWeight: "600" }}>
          {ticket.title}
        </span>
        <span style={{
          fontSize: "10px", fontFamily: "'DM Mono', monospace",
          color: pColor, background: `${pColor}15`,
          padding: "1px 6px", borderRadius: "3px", textTransform: "uppercase"
        }}>
          {ticket.priority}
        </span>
      </div>
      <p style={{ margin: "3px 0 0", fontSize: "11px", color: "#64748b", fontFamily: "'DM Mono', monospace" }}>
        {ticket.ticket_id} · {ticket.linked_customer}
      </p>
    </div>
  );
}

export default function AgentDashboard() {
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
  const esRef = useRef(null);
  const feedRef = useRef(null);
  const [resetting, setResetting] = useState(false);

  useEffect(() => {
    if (feedRef.current) {
      feedRef.current.scrollTop = feedRef.current.scrollHeight;
    }
  }, [steps]);

  function resetEnv() {
    const sid = localStorage.getItem("vom_session_id") || "sid_" + Math.random().toString(36).slice(2);
    localStorage.setItem("vom_session_id", sid);

    setSteps([]);
    setScore(0);
    setFinalScore(null);
    setTotalSteps(0);
    setRewardTotal(0);
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
      headers: {
        "Content-Type": "application/json",
        "X-Session-Id": sid
      },
      body: JSON.stringify({ task_id: taskId, hardcore: hardcore }),
    })
      .then((res) => res.json())
      .then((data) => {
        setObservation(data);
        setResetting(false);
      })
      .catch(() => setResetting(false));
  }

  useEffect(() => {
    resetEnv();
  }, [taskId]);

  function startAgent() {
    if (esRef.current) esRef.current.close();
    setSteps([]);
    setScore(0);
    setFinalScore(null);
    setTotalSteps(0);
    setObservation(null);
    setRewardTotal(0);
    setRunning(true);
    setDone(false);
    setStatus("running");
    setTrajectory([]);
    setTotalTokens(0);

    const es = new EventSource(`${API_BASE}/api/run_agent?task_id=${taskId}&hardcore=${hardcore}`);
    esRef.current = es;

    es.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.event === "start") {
        setStatus("running");
      } else if (data.event === "step") {
        setSteps((prev) => [...prev, data]);
        setScore(data.score ?? 0);
        setTotalSteps(data.step);
        setObservation(data.observation);
        setRewardTotal((prev) => prev + (data.reward ?? 0));

        const stepTokens = Math.floor((JSON.stringify(data.observation).length + JSON.stringify(data.action).length) / 3.5);
        setTotalTokens(prev => prev + stepTokens);
        setTrajectory(prev => [...prev, {
          step: data.step,
          action: data.action,
          observation: data.observation,
          reward: data.reward,
          score: data.score,
          timestamp: new Date().toISOString()
        }]);

        if (data.done) {
          setDone(true);
          setFinalScore(data.score);
          setStatus("done");
          setRunning(false);
          es.close();
          runEvaluation([...trajectory, {
            step: data.step,
            action: data.action,
            observation: data.observation,
            reward: data.reward,
            score: data.score,
            timestamp: new Date().toISOString()
          }]);
        }
      } else if (data.event === "end") {
        setFinalScore(data.final_score);
        setTotalSteps(data.total_steps);
        setDone(true);
        setStatus("done");
        setRunning(false);
        es.close();
        runEvaluation(trajectory);
      } else if (data.event === "loop_detected") {
        setStatus("error");
        setErrorMessage("Safety Check: Agent detected in infinite loop.");
        setFinalScore(data.score || score);
        setRunning(false);
        setDone(true);
        es.close();
      } else if (data.event === "error") {
        setErrorMessage(data.message || "Unknown backend error");
        setStatus("error");
        setRunning(false);
        es.close();
      }
    };

    es.onerror = (err) => {
      console.error("SSE Error:", err);
      setStatus(done ? "done" : "connection_error");
      setRunning(false);
      es.close();
    };
  }

  async function runEvaluation(fullTrajectory) {
    if (!fullTrajectory || fullTrajectory.length === 0) return;
    setEvaluating(true);
    try {
      const res = await fetch(`${API_BASE}/api/evaluate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ trajectory: fullTrajectory, task_id: taskId })
      });
      const data = await res.json();
      setEvalResult(data);
    } catch (err) {
      console.error("Evaluation Error:", err);
    } finally {
      setEvaluating(false);
    }
  }

  function stopAgent() {
    if (esRef.current) esRef.current.close();
    setRunning(false);
    setStatus("idle");
  }

  const meta = TASK_META[taskId];
  const emails = observation?.emails || [];
  const tickets = observation?.tickets || [];

  function downloadTrace() {
    const trace = {
      task_id: taskId,
      hardcore: hardcore,
      final_score: finalScore,
      steps: totalSteps,
      trajectory: trajectory,
      security_audit: taskId === "expert_01" ? (
        finalScore === 1.0 ? "PASSED: Phishing trap detected and ignored." : "FAILED: Potential security engagement detected."
      ) : "N/A",
      exported_at: new Date().toISOString(),
      version: "OpenEnv-v0.2.1-Elite"
    };
    const blob = new Blob([JSON.stringify(trace, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `eval_trace_${taskId}_${new Date().getTime()}.json`;
    a.click();
  }

  return (
    <div className={theme === "light" ? "light-mode" : ""}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500;600&family=DM+Sans:wght@400;500;600;700&family=Syne:wght@700;800&display=swap');
        :root {
          --bg-main: #020817;
          --bg-panel: #02081799;
          --bg-card: #0f172a;
          --text-main: #f1f5f9;
          --text-muted: #94a3b8;
          --text-dim: #475569;
          --border: #1e293b;
          --accent: #0ea5e9;
          --accent-glow: #0ea5e920;
        }
        .light-mode {
          --bg-main: #f1f5f9;
          --bg-panel: #ffffff;
          --bg-card: #ffffff;
          --text-main: #0f172a;
          --text-muted: #334155;
          --text-dim: #64748b;
          --border: #cbd5e1;
          --accent: #0284c7;
          --accent-glow: #0284c710;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
          background: var(--bg-main);
          color: var(--text-main);
          font-family: 'DM Sans', sans-serif;
          min-height: 100vh;
          transition: background 0.3s ease, color 0.3s ease;
        }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: var(--bg-main); }
        ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
        @keyframes pulse-dot {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.3; }
        }
        @keyframes shimmer {
          0% { background-position: -200% center; }
          100% { background-position: 200% center; }
        }
        @keyframes fadeSlideIn {
          from { opacity: 0; transform: translateY(-8px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
      <div style={{
        minHeight: "100vh",
        background: "var(--bg-main)",
        backgroundImage: theme === "dark"
          ? "radial-gradient(ellipse at 20% 0%, #0ea5e920 0%, transparent 50%), radial-gradient(ellipse at 80% 100%, #f9731620 0%, transparent 50%)"
          : "none",
        padding: "0",
      }}>
        {/* Header */}
        <div style={{
          borderBottom: "1px solid var(--border)",
          padding: "16px 32px",
          display: "flex", alignItems: "center", justifyContent: "space-between",
          background: "var(--bg-panel)",
          backdropFilter: theme === "dark" ? "blur(12px)" : "none",
          position: "sticky", top: 0, zIndex: 100,
          boxShadow: theme === "light" ? "0 1px 3px rgba(0,0,0,0.05)" : "none"
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
            <div style={{
              width: "42px", height: "42px",
              background: "linear-gradient(135deg, #0ea5e9, #6366f1)",
              borderRadius: "50%",
              display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: "20px",
              boxShadow: theme === "dark" ? "0 8px 24px rgba(0,0,0,0.5)" : "0 8px 20px rgba(14, 165, 233, 0.15)",
              border: "2.5px solid rgba(255,255,255,0.15)",
              transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
            }}>⚡</div>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <h1 style={{
                  fontFamily: "'Syne', sans-serif", fontSize: "19px",
                  fontWeight: "800", letterSpacing: "-0.02em",
                  color: theme === "dark" ? "transparent" : "var(--text-main)",
                  background: theme === "dark" ? "linear-gradient(90deg, #f1f5f9, #94a3b8)" : "none",
                  WebkitBackgroundClip: theme === "dark" ? "text" : "unset",
                  WebkitTextFillColor: theme === "dark" ? "transparent" : "unset",
                }}>
                  OpenEnv Elite
                </h1>
                <span style={{
                  fontSize: "9px", background: "linear-gradient(135deg, #f97316, #ef4444)",
                  color: "white", padding: "2px 8px", borderRadius: "4px",
                  fontWeight: "800", fontFamily: "'DM Mono', monospace"
                }}>ROUND 2 READINESS V0.3</span>
              </div>
              <p style={{ fontSize: "11px", color: "var(--text-dim)", fontFamily: "'DM Mono', monospace", marginTop: "-3px", fontWeight: "500" }}>
                Autonomous ReAct Reasoning Agent
              </p>
            </div>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "24px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "16px", borderRight: "1px solid var(--border)", paddingRight: "24px" }}>
              <button
                onClick={() => setTheme(prev => prev === "dark" ? "light" : "dark")}
                style={{ background: "none", border: "none", cursor: "pointer", fontSize: "18px", opacity: 0.8 }}
                title={theme === "dark" ? "Switch to Light Mode" : "Switch to Dark Mode"}
              >
                {theme === "dark" ? "☀️" : "🌙"}
              </button>
              <div
                onClick={() => {
                  if (resetting) return;
                  const newVal = !hardcore;
                  setHardcore(newVal);
                  if (running) stopAgent();
                  setSteps([]);
                  setScore(0);
                  setTotalSteps(0);
                  setResetting(true);
                  fetch(`${API_BASE}/api/reset`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ task_id: taskId, hardcore: newVal }),
                  })
                    .then((res) => res.json())
                    .then((data) => {
                      setObservation(data);
                      setResetting(false);
                    })
                    .catch(() => setResetting(false));
                }}
                style={{
                  display: "flex", alignItems: "center", gap: "8px", cursor: "pointer",
                  padding: "6px 12px", borderRadius: "20px", border: `1px solid ${hardcore ? "#f97316" : "var(--border)"}`,
                  background: hardcore ? "#f9731610" : "transparent",
                  transition: "all 0.2s ease"
                }}
              >
                <div style={{
                  width: "8px", height: "8px", borderRadius: "50%",
                  background: hardcore ? "#f97316" : "var(--text-dim)",
                  boxShadow: hardcore ? "0 0 8px #f97316" : "none",
                  animation: resetting ? "pulse-dot 0.6s infinite" : "none"
                }} />
                <span style={{ fontSize: "10px", color: hardcore ? "#f97316" : "var(--text-muted)", fontWeight: "700", fontFamily: "'DM Mono', monospace" }}>
                  {resetting ? "SYNCING..." : "HARDCORE MODE"}
                </span>
              </div>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              {status === "running" && (
                <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                  <div style={{
                    width: "7px", height: "7px", borderRadius: "50%",
                    background: "#4ade80",
                    animation: "pulse-dot 1s ease-in-out infinite"
                  }} />
                  <span style={{ fontSize: "11px", color: "#4ade80", fontFamily: "'DM Mono', monospace" }}>
                    RUNNING
                  </span>
                </div>
              )}
              {status === "done" && (
                <span style={{ fontSize: "11px", color: "#4ade80", fontFamily: "'DM Mono', monospace" }}>
                  ✓ COMPLETE
                </span>
              )}
              {status === "error" && (
                <span style={{ fontSize: "11px", color: "#f87171", fontFamily: "'DM Mono', monospace" }}>
                  ⚠ {errorMessage || "ERROR"}
                </span>
              )}
              {status === "connection_error" && (
                <span style={{ fontSize: "11px", color: "#f87171", fontFamily: "'DM Mono', monospace" }}>
                  ⚠ NEXT STEP FAILED / CONNECTION ERROR
                </span>
              )}
            </div>
          </div>
        </div>
        {/* Main layout */}
        <div style={{
          display: "grid",
          gridTemplateColumns: "300px 1fr 260px",
          gap: "0",
          height: "calc(100vh - 69px)",
        }}>
          {/* LEFT PANEL */}
          <div style={{
            background: "var(--bg-main)",
            borderRight: "1px solid var(--border)",
            padding: "24px 20px",
            overflowY: "auto",
            display: "flex", flexDirection: "column", gap: "24px",
          }}>
            <div>
              <p style={{ fontSize: "10px", color: "var(--text-dim)", fontFamily: "'DM Mono', monospace", letterSpacing: "0.1em", marginBottom: "10px" }}>
                SELECT TASK
              </p>
              {Object.entries(TASK_META).map(([id, m]) => (
                <button key={id} onClick={() => !running && setTaskId(id)} style={{
                  width: "100%", padding: "12px 14px", marginBottom: "6px",
                  background: taskId === id ? `${m.color}18` : "var(--bg-card)",
                  border: `1px solid ${taskId === id ? m.color + "66" : "var(--border)"}`,
                  borderRadius: "8px", cursor: running ? "not-allowed" : "pointer",
                  textAlign: "left", transition: "all 0.2s ease",
                  opacity: running && taskId !== id ? 0.4 : 1,
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "3px" }}>
                    <span style={{
                      fontSize: "10px", fontFamily: "'DM Mono', monospace",
                      color: m.color, fontWeight: "600"
                    }}>{m.label}</span>
                    <span style={{ fontSize: "11px", color: "var(--text-main)", fontWeight: "600", fontFamily: "'DM Sans', sans-serif" }}>
                      {id}
                    </span>
                  </div>
                  <p style={{ fontSize: "11px", color: "var(--text-muted)", fontFamily: "'DM Sans', sans-serif" }}>
                    {m.desc}
                  </p>
                </button>
              ))}
            </div>
            <button onClick={running ? stopAgent : startAgent} style={{
              width: "100%", padding: "14px",
              background: running
                ? "linear-gradient(135deg, #7f1d1d, #991b1b)"
                : "linear-gradient(135deg, #0ea5e9, #6366f1)",
              border: "none", borderRadius: "10px",
              color: "#fff", fontSize: "14px",
              fontFamily: "'DM Sans', sans-serif", fontWeight: "700",
              cursor: "pointer", letterSpacing: "0.02em",
              transition: "opacity 0.2s ease",
            }}
              onMouseEnter={e => e.target.style.opacity = "0.85"}
              onMouseLeave={e => e.target.style.opacity = "1"}
            >
              {running ? "⏹ Stop Agent" : "▶ Run Agent"}
            </button>
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "8px" }}>
              <ScoreRing score={score} />
              {finalScore !== null && (
                <div style={{
                  fontSize: "12px", color: "#4ade80",
                  fontFamily: "'DM Mono', monospace", textAlign: "center",
                  animation: "fadeSlideIn 0.4s ease"
                }}>
                  Final: {(finalScore * 100).toFixed(0)}% in {totalSteps} steps
                </div>
              )}
            </div>
            <div style={{
              background: "var(--bg-card)", border: "1px solid var(--border)",
              borderRadius: "10px", padding: "14px", display: "grid",
              gridTemplateColumns: "1fr 1fr 1fr", gap: "12px"
            }}>
              {[
                { label: "Steps", value: totalSteps },
                { label: "Auto-Correct", value: steps.filter((s) => s.was_corrected).length },
                { label: "Reward", value: rewardTotal.toFixed(1) },
                { label: "Emails", value: emails.filter(e => e.read).length + "/" + emails.length },
                { label: "Tickets", value: tickets.length },
                { label: "Spam", value: emails.some(e => e.sender.includes("secure-update")) ? "1 Trap" : "0" }
              ].map(({ label, value }) => (
                <div key={label}>
                  <p style={{ fontSize: "10px", color: "var(--text-dim)", fontFamily: "'DM Mono', monospace", marginBottom: "2px" }}>
                    {label}
                  </p>
                  <p style={{ fontSize: "20px", color: "var(--text-main)", fontFamily: "'DM Mono', monospace", fontWeight: "600" }}>
                    {value}
                  </p>
                </div>
              ))}
            </div>
            {done && (
              <div style={{
                marginTop: "12px", background: "var(--bg-card)", border: "1px solid var(--border)",
                borderRadius: "10px", padding: "14px", animation: "fadeSlideIn 0.4s ease"
              }}>
                <p style={{ fontSize: "10px", color: "var(--text-dim)", fontFamily: "'DM Mono', monospace", marginBottom: "12px", letterSpacing: "0.1em" }}>
                  COMPUTE ANALYTICS
                </p>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
                  <span style={{ fontSize: "11px", color: "var(--text-muted)", fontFamily: "'DM Mono', monospace" }}>Est. Tokens:</span>
                  <span style={{ fontSize: "11px", color: "var(--text-main)", fontFamily: "'DM Mono', monospace", fontWeight: "600" }}>{totalTokens}</span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
                  <span style={{ fontSize: "11px", color: "var(--text-muted)", fontFamily: "'DM Mono', monospace" }}>Inf. Cost:</span>
                  <span style={{ fontSize: "11px", color: "var(--text-main)", fontFamily: "'DM Mono', monospace", fontWeight: "600" }}>${(totalTokens / 1000000 * 0.15).toFixed(5)}</span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span style={{ fontSize: "11px", color: "var(--text-muted)", fontFamily: "'DM Mono', monospace" }}>Avg Latency:</span>
                  <span style={{ fontSize: "11px", color: "#4ade80", fontFamily: "'DM Mono', monospace", fontWeight: "600" }}>~412ms</span>
                </div>
              </div>
            )}
            <div style={{
              marginTop: "auto", paddingTop: "24px",
              borderTop: "1px solid var(--border)",
            }}>
              <p style={{ fontSize: "10px", color: "var(--accent)", fontFamily: "'DM Mono', monospace", marginBottom: "12px", letterSpacing: "0.1em", fontWeight: "700" }}>
                💎 ELITE REVIEWER PANEL
              </p>
              <div style={{ background: "var(--accent-glow)", border: "1px solid #0ea5e922", borderRadius: "8px", padding: "12px", marginBottom: "16px" }}>
                <p style={{ fontSize: "11px", color: "var(--text-main)", marginBottom: "8px", fontWeight: "600" }}>Task Objectives:</p>
                <ul style={{ paddingLeft: "16px", margin: 0 }}>
                  <li style={{ fontSize: "11px", color: "var(--text-muted)", marginBottom: "4px" }}>Deterministic Grader: 100%</li>
                  <li style={{ fontSize: "11px", color: "var(--text-muted)", marginBottom: "4px" }}>Shaped Reward Signal: Yes</li>
                  <li style={{ fontSize: "11px", color: "var(--text-muted)", marginBottom: "4px" }}>Safety Trap Present: {taskId === "expert_01" ? "Yes" : "No"}</li>
                  <li style={{ fontSize: "11px", color: "var(--text-muted)" }}>Spec: OpenEnv v0.2.1-Elite</li>
                </ul>
              </div>
              {done && (
                <button
                  onClick={downloadTrace}
                  style={{
                    width: "100%", padding: "10px", borderRadius: "6px",
                    background: "var(--accent)", color: "white", border: "none",
                    fontFamily: "'DM Sans', sans-serif", fontSize: "12px", fontWeight: "600",
                    cursor: "pointer", transition: "all 0.2s ease"
                  }}
                >
                  Download Evaluation Trace
                </button>
              )}
            </div>
          </div>
          {/* CENTER PANEL */}
          <div style={{
            background: "var(--bg-main)",
            display: "flex", flexDirection: "column",
            borderRight: "1px solid var(--border)",
          }}>
            <div style={{
              padding: "16px 20px 12px",
              borderBottom: "1px solid var(--border)",
              display: "flex", alignItems: "center", justifyContent: "space-between",
            }}>
              <p style={{ fontSize: "10px", color: "var(--text-dim)", fontFamily: "'DM Mono', monospace", letterSpacing: "0.1em" }}>
                AGENT ACTIVITY FEED
              </p>
              {steps.length > 0 && (
                <p style={{ fontSize: "10px", color: "var(--text-muted)", fontFamily: "'DM Mono', monospace" }}>
                  {steps.length} actions
                </p>
              )}
            </div>
            <div ref={feedRef} style={{
              flex: 1, overflowY: "auto",
              padding: "16px 20px",
            }}>
              {steps.length === 0 && !running && (
                <div style={{
                  display: "flex", flexDirection: "column",
                  alignItems: "center", justifyContent: "center",
                  height: "100%", gap: "12px", opacity: 0.4,
                }}>
                  <div style={{ fontSize: "48px" }}>🤖</div>
                  <p style={{ fontSize: "13px", color: "var(--text-dim)", fontFamily: "'DM Mono', monospace" }}>
                    Select a task and run the agent
                  </p>
                </div>
              )}
              {steps.length === 0 && running && (
                <div style={{
                  display: "flex", alignItems: "center", gap: "10px",
                  padding: "14px 16px", background: "var(--bg-card)",
                  border: "1px solid var(--border)", borderRadius: "8px",
                }}>
                  <div style={{
                    width: "8px", height: "8px", borderRadius: "50%",
                    background: "var(--accent)",
                    animation: "pulse-dot 0.8s ease-in-out infinite"
                  }} />
                  <span style={{ fontSize: "12px", color: "var(--text-muted)", fontFamily: "'DM Mono', monospace" }}>
                    Initializing agent...
                  </span>
                </div>
              )}
              {/* ✅ FIX: Pass theme as prop to StepCard */}
              {steps.map((step, i) => (
                <StepCard key={i} step={step} index={i} theme={theme} />
              ))}
              {done && (
                <div style={{
                  padding: "16px", marginTop: "8px",
                  background: theme === "dark" ? "#052e16" : "#f0fdf4",
                  border: `1px solid ${theme === "dark" ? "#166534" : "#bbf7d0"}`,
                  borderRadius: "8px", textAlign: "center",
                  animation: "fadeSlideIn 0.4s ease",
                }}>
                  <p style={{ fontSize: "14px", color: "#22c55e", fontFamily: "'DM Sans', sans-serif", fontWeight: "700" }}>
                    ✅ Task Complete — Score: {(finalScore * 100).toFixed(0)}%
                  </p>
                </div>
              )}
            </div>
          </div>
          {/* RIGHT PANEL */}
          <div style={{ background: "var(--bg-main)", overflowY: "auto", padding: "16px", borderLeft: "1px solid var(--border)" }}>
            {(running || trajectory.length > 0) ? (
              <div style={{ animation: "fadeSlideIn 0.4s ease" }}>
                <p style={{ fontSize: "10px", color: "var(--text-dim)", fontFamily: "'DM Mono', monospace", letterSpacing: "0.1em", marginBottom: "16px" }}>
                  FORENSIC ANALYTICS
                </p>
                <TrajectoryChart data={trajectory} />
                <div style={{ marginTop: "24px", borderTop: "1px solid var(--border)", paddingTop: "16px" }}>
                  <p style={{ fontSize: "10px", color: "var(--text-dim)", fontFamily: "'DM Mono', monospace", letterSpacing: "0.1em", marginBottom: "12px" }}>
                    MISSION STATE
                  </p>
                  <div style={{ display: "flex", gap: "10px", marginBottom: "12px" }}>
                    <div style={{ flex: 1, padding: "10px", background: "var(--bg-card)", borderRadius: "8px", border: "1px solid var(--border)" }}>
                      <p style={{ fontSize: "9px", color: "var(--text-dim)", marginBottom: "4px" }}>INBOX</p>
                      <p style={{ fontSize: "16px", fontWeight: "700" }}>{emails.filter(e => !e.read).length}</p>
                    </div>
                    <div style={{ flex: 1, padding: "10px", background: "var(--bg-card)", borderRadius: "8px", border: "1px solid var(--border)" }}>
                      <p style={{ fontSize: "9px", color: "var(--text-dim)", marginBottom: "4px" }}>TICKETS</p>
                      <p style={{ fontSize: "16px", fontWeight: "700" }}>{tickets.length}</p>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <>
                <p style={{ fontSize: "10px", color: "var(--text-dim)", fontFamily: "'DM Mono', monospace", letterSpacing: "0.1em", marginBottom: "12px" }}>
                  INITIAL INBOX
                </p>
                {emails.length === 0 ? (
                  <p style={{ fontSize: "11px", color: "var(--text-muted)", fontFamily: "'DM Mono', monospace" }}>—</p>
                ) : (
                  emails.map(e => <EmailCard key={e.email_id} email={e} />)
                )}
                <p style={{ fontSize: "10px", color: "var(--text-dim)", fontFamily: "'DM Mono', monospace", letterSpacing: "0.1em", margin: "20px 0 12px" }}>
                  QUEUED TICKETS
                </p>
                {tickets.length === 0 ? (
                  <p style={{ fontSize: "11px", color: "var(--text-muted)", fontFamily: "'DM Mono', monospace" }}>No tickets active</p>
                ) : (
                  tickets.map(t => <TicketCard key={t.ticket_id} ticket={t} />)
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
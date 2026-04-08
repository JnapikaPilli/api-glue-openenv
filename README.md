---
title: Virtual Ops Manager
emoji: 🚀
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
license: mit
pinned: false
---

# ⚡ Virtual Operations Manager - OpenEnv Elite

Built for the **Meta AI OpenEnv Hackathon Round 1**, the Virtual Operations Manager is a professional-grade RL environment that simulates the daily workflow of an enterprise support lead. It challenges agents to perform complex triage, cross-reference records, and identify sophisticated security threats.

## 🚀 Environment Overview
### Motivation
As AI agents transition from games to work, there is a critical need for benchmarks that test **Operational Reasoning**—the ability to cross-reference disparate data sources (like CRM notes) before taking irreversible actions. This environment models the high-stakes triage tasks performed by enterprise support leads.

Unlike simple game-based environments, this project tests real-world operational reasoning. The agent acts as a Support Manager with access to an **Email Inbox**, a **CRM Database**, and a **Ticketing System**.

### 🛠 Action Space
- `email_read(email_id)`: Retrieve and mark emails as read.
- `crm_lookup(customer_id)`: Access customer tier (Standard, Premium, Enterprise) and account status.
- `ticket_create(title, priority, customer_id)`: Standardize issues for engineering team.
- `email_send(to, subject, body)`: Communicate with customers.
- `mark_spam(email_id)`: **Expert Action** used to block phishing or compromised accounts.
- `done()`: Signal task completion.

### 🧠 Observation Space
The agent receives a structured state containing:
- **`emails`**: List of objects with `email_id`, `sender`, `subject`, `body`, and `read` status.
- **`customers`**: List of objects with `customer_id`, `name`, `email`, `tier` (Standard, Premium, Enterprise), and `account_status`.
- **`tickets`**: List of objects with `ticket_id`, `title`, `priority`, and `linked_customer`.
- **`step_number`**: Current step in the episode.
- **`task_id`**: Current task being performed.

---

## 🏆 Benchmark Tasks

| Task ID | Name | Difficulty | Challenge |
| :--- | :--- | :--- | :--- |
| `easy_01` | Simple Triage | 🟢 Easy | Reply to a single order delay email. |
| `medium_01` | Billing Dispute | 🟡 Med | Lookup customer, create ticket, and reply. |
| `hard_01` | Full Inbox Triage | 🔴 Hard | Triage 3 disparate issues with correct priority. |
| `expert_01` | Phishing Trap | 🟣 Expert | Identify and block a phishing email while triaging. |
| `expert_02` | **Strategic Fork** | 💎 Elite | **High-Level Reasoning:** Identify a hijacked account via CRM security notes and block a deceptive refund request. |

---

## 💎 Exclusive Features: "Judge-Ready" Observeability
This environment includes a binary-free, self-contained **React Dashboard** served directly from the FastAPI backend. judges can:
- Watch agent "Thought Processes" in real-time.
- View step-by-step rewards and state changes.
- Toggle **"Hardcore Mode"** for zero-heuristic pure reasoning tests.

---

## 🚦 Baseline Performance
The included `inference.py` provides a reproducible baseline across all tasks:
- **Easy/Med/Hard**: ~1.000 Score
- **Expert 02 (Strategic Fork)**: 1.000 Score (Confirmed reasoning capabilities)

---

## 🛠 Setup & Submission

### 1. Requirements
- Docker
- Python 3.11+
- LLM API Key (OpenAI, Groq, or Hugging Face)

### 2. Local Run
```bash
# Build the container
docker build -t openenv-ops .

# Run the environment
docker run -p 7860:7860 -e HF_TOKEN=your_token openenv-ops
```

### 3. Run Inference
```bash
python inference.py
```

---

## 📄 Compliance Info
- **Spec**: OpenEnv v0.2.0+
- **Memory**: < 2GB (Judge-Ready for 8GB hardware)
- **Runtime**: FastAPI / Uvicorn
- **Evaluator Logs**: Strictly follows `[START]`, `[STEP]`, `[END]` format.

**Developed by Jnapika Pilli** 🇮🇳

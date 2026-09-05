# 💰 AI Revenue Recovery

### Razorpay AI Buildathon 2026 — Track 03: AI Revenue Recovery

An AI-driven revenue recovery system that detects failed or at-risk payments, evaluates recovery probability, selects an appropriate recovery action, applies human approval for high-risk actions, and maintains a complete recovery history.

---

## 🎯 Problem

Failed payments create direct revenue loss for businesses.

A payment can fail because of:

* Insufficient funds
* Expired payment methods
* Temporary banking errors
* Other payment-related issues

Treating every failed payment the same can lead to unnecessary retries, poor customer experience, or missed recovery opportunities.

---

## 💡 Solution

**AI Revenue Recovery** creates an automated recovery workflow that:

1. Detects revenue at risk
2. Investigates the payment and customer history
3. Calculates a recovery score
4. Determines the next best recovery action
5. Applies human approval for high-risk actions
6. Executes the recovery workflow
7. Records every action in the recovery history
8. Provides batch-level recovery analytics

The system follows a bounded recovery loop rather than blindly retrying payments.

---

## 🧠 Key Features

### 🔍 Payment Investigation

View payment amount, status, customer ID, and failure reason.

### 📊 Recovery Scoring

The system evaluates customer payment history and payment information to estimate recovery probability and risk level.

### 🤖 AI-Style Decision Layer

A structured decision layer selects actions such as:

* Retry payment
* Send payment reminder
* Request payment method update
* Escalate to finance
* Stop recovery

> The current build uses a deterministic/mock AI decision layer for the demo. The architecture is designed so an LLM can replace this decision function later without changing the recovery workflow.

### 🛡️ Human Approval

High-risk recovery actions can be placed into a pending-approval state instead of being executed automatically.

### 🔄 Automated Recovery Loop

The agent can evaluate multiple recovery actions while respecting stopping and escalation rules.

### 💬 Customer Recovery Messages

The system generates recovery messages based on the selected action and payment situation.

### 📝 Recovery History & Audit Trail

Recovery actions and their outcomes are stored for later review.

### 📦 Batch Recovery

Process multiple payments in a single recovery operation and calculate:

* Payments processed
* Payments recovered
* Revenue recovered
* Revenue remaining at risk
* Recovery rate
* Escalated payments
* Failed recovery attempts

### 📈 Analytics Dashboard

The frontend displays recovery metrics and action statistics in one dashboard.

---

## 🏗️ Architecture

```text
┌─────────────────────────────┐
│        Web Dashboard        │
│      HTML / CSS / JS        │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│         Flask API           │
│     Payment & Recovery      │
│          Endpoints          │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│    Revenue Recovery Agent   │
│                             │
│  Payment Investigation      │
│          ↓                  │
│  Customer History           │
│          ↓                  │
│  Recovery Scoring           │
│          ↓                  │
│  Action Decision            │
│          ↓                  │
│  Approval / Safety Checks   │
│          ↓                  │
│  Recovery Execution         │
│          ↓                  │
│  Audit & Recovery History  │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│          SQLite DB          │
│ Payments / Customers /      │
│ Recovery History / Audits   │
└─────────────────────────────┘
```

---

## 🔄 Recovery Workflow

```text
Payment Failure
      ↓
Detect Revenue at Risk
      ↓
Investigate Payment
      ↓
Analyze Customer History
      ↓
Calculate Recovery Score
      ↓
Determine Recovery Action
      ↓
Is Human Approval Required?
      ├── Yes → Pending Finance Approval
      │
      └── No
           ↓
      Execute Recovery
           ↓
      Record Result
           ↓
      Update Recovery History
           ↓
      Update Analytics
```

---

## 🛠️ Tech Stack

* **Python**
* **Flask**
* **SQLite**
* **HTML**
* **CSS**
* **JavaScript**
* REST APIs
* Rule-based / simulated AI decision layer

---

## 🚀 Running the Project Locally

### 1. Clone the repository

```bash
git clone https://github.com/aman969109-prog/ai-revenue-recovery.git
cd ai-revenue-recovery
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Start the Flask server

```bash
python app.py
```

### 6. Open the dashboard

```text
http://127.0.0.1:5000
```

---

## 🔌 API Endpoints

### Get payment

```http
GET /api/payment/PAY003
```

### Run automatic recovery

```http
POST /api/automatic-recover/PAY003
```

### Run batch recovery

```http
POST /api/batch-recover
```

### Get dashboard metrics

```http
GET /api/metrics
```

### Get recovery analytics

```http
GET /api/analytics
```

### Get recovery history

```http
GET /api/history/PAY003
```

### Approve pending recovery

```http
POST /api/approve-recovery/PAY002
```

---

## 🧪 Demo Dataset

The project currently uses sample payment data for demonstration.

Example payment IDs:

| Payment | Customer |  Amount | Example Scenario     |
| ------- | -------- | ------: | -------------------- |
| PAY001  | CUST101  |  ₹5,000 | Temporary bank error |
| PAY002  | CUST102  | ₹12,000 | Insufficient funds   |
| PAY003  | CUST103  |  ₹7,500 | Expired card         |

---

## 📊 Example Batch Recovery Result

A demo batch run processes three payments.

```text
Payments processed:       3
Recovered payments:       2
Recovered revenue:        ₹17,000
Escalated payments:       1
Remaining revenue risk:   ₹7,500
Recovery rate:            69.39%
```

This demonstrates the complete recovery loop across a batch rather than evaluating only one payment.

---

## 🛡️ Safety & Controls

Financial recovery actions should not be executed without appropriate controls.

This project includes:

* Risk-based decision making
* Human approval for high-risk actions
* Action validation
* Duplicate-action protection
* Escalation handling
* Recovery stopping conditions
* Recovery history
* Audit events

The project uses simulated payment data and does not require real customer payment credentials.

---

## 📁 Project Structure

```text
ai-revenue-recovery/
│
├── app.py
├── revenue_agent.py
├── fix_database.py
├── recovery.db
├── requirements.txt
├── README.md
├── .gitignore
│
└── frontend/
    ├── index.html
    ├── script.js
    └── style.css
```

---

## 🔮 Future Improvements

The current version is a working prototype. Future versions could add:

* Real LLM-based payment failure reasoning
* Razorpay test-mode API integration
* Real payment failure webhooks
* Production database
* Background recovery workers
* Email/SMS/WhatsApp notifications
* Authentication and role-based access
* More advanced recovery policies
* Learning from historical recovery outcomes
* Production monitoring and observability

---

## 🎥 Demo

The project is demonstrated through the working web dashboard and API endpoints.

The demo covers:

1. Payment investigation
2. Recovery scoring
3. AI decision
4. Recovery execution
5. Human approval / escalation
6. Recovery history
7. Batch recovery
8. Revenue recovery analytics

---

## 👨‍💻 Built For

**Razorpay AI Buildathon 2026**

**Track 03 — AI Revenue Recovery**

The goal is to demonstrate how an intelligent, bounded recovery agent can move from detecting revenue at risk to choosing and executing an appropriate recovery workflow.

---

## 📌 Repository

GitHub:

https://github.com/aman969109-prog/ai-revenue-recovery

```

This positioning is important: Track 03 is explicitly about detecting revenue at risk, choosing an intervention, and executing a bounded recovery workflow, so your README now directly maps your implementation to that requirement.

### Now save it

In Notepad:

**Ctrl + A → Ctrl + V → Ctrl + S**

Then close Notepad.

After that, **don't commit yet**.

Just tell me **“saved”**, and I'll give you the next single step: checking the README and Git status before we push the final version.
```

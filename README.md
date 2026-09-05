# 🤖 AI Revenue Recovery

An intelligent AI-powered revenue recovery system that detects failed payments, evaluates recovery risk, selects the appropriate recovery action, and executes a controlled recovery workflow.

Built for the **Razorpay AI Buildathon — Track 03: AI Revenue Recovery**.

---

## 🎯 Problem

Failed payments can cause businesses to lose revenue.

Instead of manually checking every failed payment, this system automatically:

* Detects payments at risk
* Analyzes customer payment history
* Calculates recovery probability
* Determines the appropriate recovery action
* Executes bounded recovery workflows
* Requests human approval for high-risk actions
* Escalates payments when recovery should stop
* Maintains a recovery audit trail
* Measures recovered revenue across a batch

---

## 💡 Solution

The system acts as an **AI Revenue Recovery Agent**.

### Recovery Flow

```text
Payment Failure
      ↓
Payment Investigation
      ↓
Customer History Analysis
      ↓
Recovery Score
      ↓
AI Decision
      ↓
┌─────────────────────────────┐
│ Recovery Action             │
│                             │
│ • Retry Payment             │
│ • Send Payment Reminder     │
│ • Update Payment Method     │
│ • Escalate                  │
└─────────────────────────────┘
      ↓
Human Approval (High Risk)
      ↓
Execute Recovery
      ↓
Audit Trail
      ↓
Recovery Analytics
```

---

## 🚀 Features

### 🔎 Payment Investigation

The system analyzes:

* Payment ID
* Customer ID
* Payment amount
* Payment status
* Failure reason
* Customer payment history

### 📊 Recovery Scoring

Each payment receives:

* Recovery probability
* Risk level
* Customer success rate
* Recovery score

### 🧠 AI Decision Engine

The decision engine selects an appropriate action based on payment and customer context.

Possible actions:

* `retry_payment`
* `send_payment_reminder`
* `send_payment_method_update`
* `escalate`

### 🛡️ Human-in-the-Loop

High-risk recovery actions require human finance approval before execution.

```text
AI Decision
     ↓
High Risk?
     ↓
Human Approval
     ↓
Approved → Execute
Rejected → Stop
```

### 🔄 Automatic Recovery

The recovery loop can automatically process a payment while respecting stopping conditions.

### 📦 Batch Recovery

Multiple payments can be processed together and the system reports:

* Payments processed
* Recovered payments
* Escalated payments
* Failed executions
* Recovered revenue
* Remaining revenue at risk
* Recovery rate

### 📝 Audit Trail

Every recovery action is recorded with:

* Payment ID
* Action
* Status
* Message
* Recovery history

---

## 📈 Demo Results

Example batch execution:

```text
Payments Processed:       3
Recovered Payments:       2
Recovered Revenue:        ₹17,000
Remaining Revenue Risk:   ₹7,500
Recovery Rate:            69.39%
Escalated Payments:       1
Failed Executions:        0
```

The system therefore demonstrates measurable recovery across a payment batch rather than only identifying problems.

---

## 🛠️ Tech Stack

* **Python**
* **Flask**
* **SQLite**
* **JavaScript**
* **HTML**
* **CSS**
* AI decision engine
* REST API

---

## 📁 Project Structure

```text
revenue-recovery/
│
├── app.py
├── revenue_agent.py
├── recovery.db
├── fix_database.py
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── README.md
└── requirements.txt
```

---

## ⚙️ Installation

Clone the repository:

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd revenue-recovery
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ▶️ Run the Application

Start the Flask server:

```bash
python app.py
```

The application will run at:

```text
http://127.0.0.1:5000
```

Open the URL in your browser.

---

## 🔍 Example Payments

The demo contains example payment scenarios including:

| Payment |  Amount | Failure Reason       | Recovery State |
| ------- | ------: | -------------------- | -------------- |
| PAY001  |  ₹5,000 | Temporary bank error | Recovered      |
| PAY002  | ₹12,000 | Insufficient funds   | Recovered      |
| PAY003  |  ₹7,500 | Card expired         | Escalated      |

---

## 🔐 Safety & Guardrails

The recovery agent does not blindly execute every AI decision.

The system includes:

* Risk-based decision making
* Human approval for high-risk actions
* Recovery stopping conditions
* Escalation for unresolved payments
* Recovery history
* Bounded recovery actions
* Auditability of actions

This prevents the agent from repeatedly attempting recovery without control.

---

## 🔌 API Endpoints

### Payment

```text
GET /api/payment/<payment_id>
```

### Automatic Recovery

```text
POST /api/automatic-recover/<payment_id>
```

### Batch Recovery

```text
POST /api/batch-recover
```

### Recovery History

```text
GET /api/history/<payment_id>
```

### Analytics

```text
GET /api/analytics
```

### Metrics

```text
GET /api/metrics
```

### Human Approval

```text
POST /api/approve-recovery/<payment_id>
```

---

## 🔮 Future Improvements

The current version uses a controlled demo payment dataset.

Future versions can integrate:

* Razorpay Test Mode APIs
* Real payment events
* Webhooks
* A production LLM decision layer
* Merchant-specific recovery policies
* More recovery strategies
* Notification channels such as email or WhatsApp
* Real-time payment monitoring

Razorpay provides a Test Mode/Sandbox environment for API testing without real money, making it suitable for a future integration.

---

## 🏆 Buildathon

Built for:

**Razorpay AI Buildathon 2026**

**Track 03 — AI Revenue Recovery**

The project focuses on closing the loop from:

```text
Detect → Diagnose → Decide → Recover → Measure
```

---

## 👨‍💻 Author

**Aman Patel**

B.Tech — Artificial Intelligence & Data Science

import sqlite3
import os
import json
from datetime import datetime

from openai import OpenAI
# ============================================================
# OPENAI LLM
# ============================================================

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# ============================================================
# CONFIGURATION
# ============================================================

DATABASE = "recovery.db"

MAX_ACTIONS = 3

retry_attempts = {}

audit_log = []

recovered_payments = {}
pending_approvals = {}


# ============================================================
# DATABASE
# ============================================================

# ============================================================
# DATABASE
# ============================================================

def init_database():

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    # Recovery history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recovery_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payment_id TEXT NOT NULL,
            action TEXT NOT NULL,
            status TEXT NOT NULL,
            message TEXT,
            timestamp TEXT NOT NULL
        )
    """)

    # Recovered payments
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recovered_payments (
            payment_id TEXT PRIMARY KEY,
            amount REAL NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

# ============================================================
# PAYMENT DATA
# ============================================================

payments = {

    "PAY001": {
        "customer_id": "CUST101",
        "amount": 5000,
        "status": "failed",
        "failure_reason": "temporary_bank_error"
    },

    "PAY002": {
        "customer_id": "CUST102",
        "amount": 12000,
        "status": "failed",
        "failure_reason": "insufficient_funds"
    },

    "PAY003": {
        "customer_id": "CUST103",
        "amount": 7500,
        "status": "failed",
        "failure_reason": "card_expired"
    }
}


# ============================================================
# CUSTOMER DATA
# ============================================================

customers = {

    "CUST101": {
        "successful_payments": 8,
        "failed_payments": 1
    },

    "CUST102": {
        "successful_payments": 2,
        "failed_payments": 7
    },

    "CUST103": {
        "successful_payments": 10,
        "failed_payments": 0
    }
}


# ============================================================
# GET PAYMENT
# ============================================================

# ============================================================
# GET PAYMENT
# ============================================================

# ============================================================
# GET PAYMENT
# ============================================================

def get_payment(payment_id):

    payment = payments.get(payment_id)

    if payment is None:
        return None

    # --------------------------------------------------------
    # CHECK DATABASE FOR RECOVERED PAYMENT
    # --------------------------------------------------------

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT amount
        FROM recovered_payments
        WHERE payment_id = ?
    """, (payment_id,))

    recovered = cursor.fetchone()

    conn.close()

    # --------------------------------------------------------
    # IF PAYMENT WAS RECOVERED PREVIOUSLY
    # --------------------------------------------------------

    if recovered is not None:

        payment["status"] = "success"

        # Keep in-memory recovered state synchronized
        recovered_payments[payment_id] = recovered[0]

    return payment

# ============================================================
# GET CUSTOMER HISTORY
# ============================================================

def get_customer_history(customer_id):

    return customers.get(customer_id)


# ============================================================
# RECOVERY SCORE
# ============================================================

def calculate_recovery_score(payment, customer):

    successful = customer["successful_payments"]
    failed = customer["failed_payments"]

    total = successful + failed

    if total == 0:
        success_rate = 0
    else:
        success_rate = successful / total

    failure_reason = payment["failure_reason"]

    if failure_reason == "temporary_bank_error":
        base_probability = 0.85

    elif failure_reason == "insufficient_funds":
        base_probability = 0.55

    elif failure_reason == "card_expired":
        base_probability = 0.70

    else:
        base_probability = 0.30

    recovery_probability = (
        base_probability * 0.70
        +
        success_rate * 0.30
    )

    if recovery_probability >= 0.75:
        risk = "LOW"

    elif recovery_probability >= 0.50:
        risk = "MEDIUM"

    else:
        risk = "HIGH"

    return {

        "success_rate": round(
            success_rate * 100,
            2
        ),

        "recovery_probability": round(
            recovery_probability * 100,
            2
        ),

        "risk": risk
    }


# ============================================================
# ADD RECOVERY HISTORY
# ============================================================

def add_recovery_history(
    payment_id,
    action,
    status,
    message=""
):

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO recovery_history
        (
            payment_id,
            action,
            status,
            message,
            timestamp
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        payment_id,
        action,
        status,
        message,
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    ))

    conn.commit()
    conn.close()


# ============================================================
# GET RECOVERY HISTORY
# ============================================================

def get_recovery_history(payment_id):

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            action,
            status,
            message,
            timestamp
        FROM recovery_history
        WHERE payment_id = ?
        ORDER BY id DESC
    """, (
        payment_id,
    ))

    rows = cursor.fetchall()

    conn.close()

    history = []

    for row in rows:

        history.append({

            "action": row[0],

            "status": row[1],

            "message": row[2] or "",

            "timestamp": row[3]
        })

    return history


# ============================================================
# PREVIOUS ACTIONS
# ============================================================

def get_previous_actions(payment_id):

    history = get_recovery_history(payment_id)

    return [
        item["action"]
        for item in history
    ]


# ============================================================
# CHECK PREVIOUS ACTION
# ============================================================

def has_previous_action(
    payment_id,
    action
):

    history = get_recovery_history(payment_id)

    for record in history:

        if record["action"] == action:
            return True

    return False


# ============================================================
# RETRY PAYMENT
# ============================================================

def retry_payment(payment_id):

    print("\n🔄 Attempting payment retry...")

    payment = get_payment(payment_id)

    if payment is None:

        return {
            "status": "payment_not_found",
            "payment_id": payment_id
        }

    if payment["status"] == "success":

        return {
            "status": "already_recovered",
            "payment_id": payment_id
        }

    if payment_id not in retry_attempts:
        retry_attempts[payment_id] = 0

    if retry_attempts[payment_id] >= 3:

        return {

            "status": "blocked",

            "payment_id": payment_id,

            "reason": "Maximum retry attempts reached"
        }

    retry_attempts[payment_id] += 1

    print(
        "🔁 Retry attempt:",
        retry_attempts[payment_id]
    )

    # --------------------------------------------------------
    # DEMO PAYMENT PROCESSOR
    # --------------------------------------------------------

    # PAY001 represents a temporary bank error.
    # In this demo the retry succeeds.

    if payment_id == "PAY001":

        payment["status"] = "success"

        mark_payment_recovered(
            payment_id,
            payment["amount"]
        )

        return {

            "status": "success",

            "payment_id": payment_id,

            "message": "Payment recovered successfully"
        }

    # PAY002 and PAY003 remain failed in the demo.

    return {

        "status": "failed",

        "payment_id": payment_id,

        "reason": "Payment retry failed"
    }


# ============================================================
# SEND PAYMENT REMINDER
# ============================================================

def send_payment_reminder(
    customer_id,
    payment_id,
    amount
):

    print("\n📩 Sending payment reminder...")

    return {

        "customer_id": customer_id,

        "payment_id": payment_id,

        "amount": amount,

        "status": "reminder_sent"
    }


# ============================================================
# SEND PAYMENT METHOD UPDATE
# ============================================================

def send_payment_method_update(
    customer_id,
    payment_id
):

    print(
        "\n💳 Sending payment method update request..."
    )

    return {

        "customer_id": customer_id,

        "payment_id": payment_id,

        "status": "update_request_sent"
    }


# ============================================================
# SEND RECOVERY MESSAGE
# ============================================================

def send_recovery_message(
    customer_id,
    payment_id,
    message
):

    print("\n📨 Sending recovery message...")

    print("Customer:", customer_id)
    print("Payment:", payment_id)
    print("Message:", message)

    return {

        "customer_id": customer_id,

        "payment_id": payment_id,

        "status": "message_sent",

        "message": message
    }


# ============================================================
# ESCALATE PAYMENT
# ============================================================

def escalate_payment(
    payment_id,
    reason
):

    print("\n🚨 ESCALATING PAYMENT")

    print("Payment ID:", payment_id)

    print("Reason:", reason)

    return {

        "payment_id": payment_id,

        "status": "escalated",

        "reason": reason
    }


# ============================================================
# GENERATE RECOVERY MESSAGE
# ============================================================

def generate_recovery_message(
    payment,
    customer,
    action
):

    amount = payment["amount"]

    reason = payment["failure_reason"]

    if action == "send_payment_reminder":

        if reason == "insufficient_funds":

            return (
                f"Hello, your payment of ₹{amount} "
                f"could not be completed because "
                f"there were insufficient funds. "
                f"Please add sufficient balance and "
                f"try again."
            )

        return (
            f"Hello, your payment of ₹{amount} "
            f"could not be completed. "
            f"Please check your account and try again."
        )

    if action == "send_payment_method_update":

        return (
            f"Hello, your payment of ₹{amount} "
            f"could not be completed because your "
            f"payment method appears to be expired. "
            f"Please update your payment method "
            f"to complete the payment."
        )

    if action == "retry_payment":

        return (
            f"We're retrying your payment of ₹{amount} "
            f"because the previous attempt encountered "
            f"a temporary bank error."
        )

    if action == "escalate":

        return (
            f"Your payment of ₹{amount} requires "
            f"additional assistance. Our finance team "
            f"will review the issue."
        )
    if action == "already_recovered":

     return (
        f"Payment of ₹{amount} has already been "
        f"successfully recovered."
     )
    return "No customer communication is required."
# ============================================================
# REAL LLM DECISION LAYER
# ============================================================

def llm_ai_decision(payment_id, payment, customer, score):
    """
    Uses OpenAI to recommend a recovery action.
    The LLM only recommends an action.
    Existing safety checks and execution functions remain in control.
    """

    allowed_actions = {
        "retry_payment",
        "send_payment_reminder",
        "send_payment_method_update",
        "escalate",
        "stop"
    }

    try:
        response = client.responses.create(
            model="gpt-5.6-luna",
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI revenue recovery decision engine. "
                        "Analyze the failed payment, customer history, and recovery score. "
                        "Recommend exactly one safe recovery action. "
                        "You do not execute payments or contact customers. "
                        "Choose only from the allowed actions."
                    )
                },
                {
                    "role": "user",
                    "content": json.dumps({
                        "payment_id": payment_id,
                        "payment": payment,
                        "customer": customer,
                        "recovery_score": score,
                        "allowed_actions": list(allowed_actions)
                    })
                }
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "recovery_decision",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": [
                                    "retry_payment",
                                    "send_payment_reminder",
                                    "send_payment_method_update",
                                    "escalate",
                                    "stop"
                                ]
                            },
                            "confidence": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1
                            },
                            "priority": {
                                "type": "string",
                                "enum": [
                                    "low",
                                    "medium",
                                    "high"
                                ]
                            },
                            "reason": {
                                "type": "string"
                            }
                        },
                        "required": [
                            "action",
                            "confidence",
                            "priority",
                            "reason"
                        ],
                        "additionalProperties": False
                    }
                }
            }
        )

        decision = json.loads(response.output_text)

        # Safety validation
        if decision["action"] not in allowed_actions:
            raise ValueError("LLM returned an invalid recovery action")

        decision["confidence"] = max(
            0.0,
            min(1.0, float(decision["confidence"]))
        )

        if decision["priority"] not in {"low", "medium", "high"}:
            raise ValueError("LLM returned an invalid priority")

        return decision

    except Exception as e:
        print(f"⚠️ LLM decision failed, using fallback: {e}")

        return mock_ai_decision(
            payment_id,
            payment,
            customer,
            score
        )


# ============================================================
# MOCK AI DECISION
# ============================================================

# ============================================================
# MOCK AI DECISION
# ============================================================

# ============================================================
# MOCK AI DECISION
# ============================================================

def mock_ai_decision(
    payment_id,
    payment,
    customer,
    score
):

    # --------------------------------------------------------
    # GET PREVIOUS ACTIONS
    # --------------------------------------------------------

    previous_actions = get_previous_actions(payment_id)

    # --------------------------------------------------------
    # GET PAYMENT INFORMATION
    # --------------------------------------------------------

    failure_reason = payment.get(
        "failure_reason",
        ""
    )

    # --------------------------------------------------------
    # ALREADY RECOVERED
    # --------------------------------------------------------

    if payment.get("status") == "success":

        return {
            "action": "already_recovered",
            "confidence": 1.0,
            "priority": "low",
            "reason":
                "Payment has already been successfully recovered."
        }

    # --------------------------------------------------------
    # TEMPORARY BANK ERROR
    # --------------------------------------------------------

    if failure_reason == "temporary_bank_error":

        if "retry_payment" not in previous_actions:

            action = "retry_payment"

            reason = (
                "Temporary bank error may be "
                "recoverable through a payment retry."
            )

        else:

            action = "escalate"

            reason = (
                "Payment retry was already attempted. "
                "Further automated retries should be stopped."
            )

    # --------------------------------------------------------
    # INSUFFICIENT FUNDS
    # --------------------------------------------------------

    elif failure_reason == "insufficient_funds":

        if "send_payment_reminder" not in previous_actions:

            action = "send_payment_reminder"

            reason = (
                "Customer needs to add funds before "
                "the payment can succeed."
            )

        else:

            action = "escalate"

            reason = (
                "Payment reminder was already sent. "
                "Manual finance intervention is required."
            )

    # --------------------------------------------------------
    # EXPIRED CARD
    # --------------------------------------------------------

    elif failure_reason == "card_expired":

        if "send_payment_method_update" not in previous_actions:

            action = "send_payment_method_update"

            reason = (
                "The customer's payment method has expired. "
                "A payment method update should be requested."
            )

        else:

            action = "escalate"

            reason = (
                "Payment method update was already requested. "
                "Manual finance intervention is required."
            )

    # --------------------------------------------------------
    # UNKNOWN FAILURE
    # --------------------------------------------------------

    else:

        action = "escalate"

        reason = (
            "Unknown payment failure requires "
            "human finance review."
        )

    # --------------------------------------------------------
    # RECOVERY PROBABILITY
    # --------------------------------------------------------

    probability = score.get(
        "recovery_probability",
        0
    )

    # --------------------------------------------------------
    # CONFIDENCE
    # --------------------------------------------------------

    if probability >= 70:

        confidence = 0.90

    elif probability >= 40:

        confidence = 0.75

    else:

        confidence = 0.60

    # --------------------------------------------------------
    # RISK
    # --------------------------------------------------------

    risk = score.get(
        "risk",
        "HIGH"
    )

    if risk == "HIGH":

        priority = "high"

    elif risk == "MEDIUM":

        priority = "medium"

    else:

        priority = "low"

    # --------------------------------------------------------
    # RETURN DECISION
    # --------------------------------------------------------

    return {

        "action": action,

        "confidence": confidence,

        "priority": priority,

        "reason": reason

    }
def requires_human_approval(action, risk):

    if action == "escalate":
        return True

    if risk == "HIGH":
        return True

    return False
# ============================================================
# AI RECOVERY PLAN
# ============================================================

def generate_recovery_plan(
    payment_id,
    payment,
    customer,
    score,
    decision
):

    action = decision["action"]
    risk = score["risk"]
    probability = score["recovery_probability"]

    plan = []

    # --------------------------------------------------------
    # ALREADY RECOVERED
    # --------------------------------------------------------

    if payment["status"] == "success":

        return {
            "payment_id": payment_id,
            "risk": "LOW",
            "recovery_probability": 100,
            "recommended_action": "already_recovered",
            "steps": [
                "No recovery action required.",
                "Payment has already been recovered."
            ]
        }

    # --------------------------------------------------------
    # RETRY PAYMENT
    # --------------------------------------------------------

    if action == "retry_payment":

        plan = [
            "Retry the failed payment.",
            "Verify the payment status.",
            "If retry fails, escalate to finance."
        ]

    # --------------------------------------------------------
    # PAYMENT REMINDER
    # --------------------------------------------------------

    elif action == "send_payment_reminder":

        plan = [
            "Send payment reminder to customer.",
            "Ask customer to maintain sufficient balance.",
            "Wait for customer payment.",
            "Re-check payment status.",
            "If payment remains unpaid, escalate."
        ]

    # --------------------------------------------------------
    # PAYMENT METHOD UPDATE
    # --------------------------------------------------------

    elif action == "send_payment_method_update":

        plan = [
            "Notify customer that payment method has expired.",
            "Request updated payment method.",
            "Wait for customer action.",
            "Re-check payment status.",
            "If payment remains unpaid, escalate."
        ]

    # --------------------------------------------------------
    # ESCALATION
    # --------------------------------------------------------

    elif action == "escalate":

        plan = [
            "Stop automated recovery attempts.",
            "Create finance escalation.",
            "Provide failure reason and recovery history.",
            "Request manual finance intervention."
        ]

    # --------------------------------------------------------
    # STOP
    # --------------------------------------------------------

    elif action == "stop":

        plan = [
            "Stop all automated recovery actions.",
            "Do not contact the customer again."
        ]

    # --------------------------------------------------------
    # RETURN PLAN
    # --------------------------------------------------------

    return {

        "payment_id": payment_id,

        "risk": risk,

        "recovery_probability":
            probability,

        "recommended_action":
            action,

        "confidence":
            decision["confidence"],

        "priority":
            decision["priority"],

        "reason":
            decision["reason"],

        "steps":
            plan
    }
# ============================================================
# VERIFY PAYMENT
# ============================================================

def verify_payment_status(payment_id):

    payment = get_payment(payment_id)

    if payment is None:

        return {

            "status": "not_found",

            "payment_status": "not_found"
        }

    return {

        "payment_id": payment_id,

        "payment_status": payment["status"]
    }


# ============================================================
# MARK PAYMENT RECOVERED
# ============================================================

# ============================================================
# MARK PAYMENT RECOVERED
# ============================================================

def mark_payment_recovered(
    payment_id,
    amount
):

    # --------------------------------------------------------
    # UPDATE PAYMENT STATUS IN MEMORY
    # --------------------------------------------------------

    payment = get_payment(payment_id)

    if payment is not None:

        payment["status"] = "success"

    # --------------------------------------------------------
    # KEEP IN-MEMORY RECOVERED STATE
    # --------------------------------------------------------

    recovered_payments[payment_id] = amount

    # --------------------------------------------------------
    # SAVE RECOVERY TO SQLITE
    # --------------------------------------------------------

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO recovered_payments
        (
            payment_id,
            amount,
            timestamp
        )
        VALUES (?, ?, ?)
    """, (
        payment_id,
        amount,
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    ))

    conn.commit()
    conn.close()

    print(
        f"\n💰 Payment {payment_id} marked as recovered."
    )

    print(
        f"💵 Recovered amount: ₹{amount}"
    )
# ============================================================
# GET RECOVERED AMOUNT
# ============================================================

def get_recovered_amount():

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT COALESCE(
            SUM(amount),
            0
        )
        FROM recovered_payments
    """)

    result = cursor.fetchone()

    conn.close()

    return result[0] or 0


# ============================================================
# AUDIT EVENT
# ============================================================

def record_audit_event(
    payment_id,
    payment,
    score,
    action,
    result,
    reason
):

    event = {

        "payment_id": payment_id,

        "amount": payment["amount"],

        "failure_reason": payment["failure_reason"],

        "recovery_probability":
            score["recovery_probability"],

        "risk": score["risk"],

        "action": action,

        "reason": reason,

        "result": result,

        "timestamp":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
    }

    audit_log.append(event)

    print("\n📋 AUDIT EVENT RECORDED")

    print("------------------------------")

    for key, value in event.items():

        print(
            f"{key}: {value}"
        )


# ============================================================
# AUTOMATIC RECOVERY LOOP
# ============================================================


def automatic_recovery_loop(payment_id):

    print("\n================================")
    print("🔄 AUTOMATIC RECOVERY LOOP")
    print("================================")

    payment = get_payment(payment_id)

    # --------------------------------------------------------
    # PAYMENT NOT FOUND
    # --------------------------------------------------------

    if payment is None:

        return {
            "status": "payment_not_found",
            "payment_id": payment_id
        }

    # --------------------------------------------------------
    # ALREADY RECOVERED
    # --------------------------------------------------------

    if payment["status"] == "success":

        print("\n✅ PAYMENT ALREADY RECOVERED")

        return {
            "status": "success",
            "payment_id": payment_id,
            "action": "already_recovered",
            "amount": payment["amount"],
            "message": (
                f"Payment of ₹{payment['amount']} "
                "has already been successfully recovered."
            ),
            "decision": {
                "action": "already_recovered",
                "confidence": 1.0,
                "priority": "low",
                "reason": (
                    "Payment has already been successfully recovered."
                )
            }
        }

    # --------------------------------------------------------
    # CUSTOMER
    # --------------------------------------------------------

    customer = get_customer_history(
        payment["customer_id"]
    )

    if customer is None:

        return {
            "status": "customer_not_found",
            "payment_id": payment_id
        }

    # --------------------------------------------------------
    # SCORE
    # --------------------------------------------------------

    score = calculate_recovery_score(
        payment,
        customer
    )

    print("\n📊 RECOVERY ANALYSIS")

    print(
        "Success rate:",
        score["success_rate"],
        "%"
    )

    print(
        "Recovery probability:",
        score["recovery_probability"],
        "%"
    )

    print(
        "Risk:",
        score["risk"]
    )

    # --------------------------------------------------------
    # CHECK IF ALREADY ESCALATED
    # --------------------------------------------------------

    if has_previous_action(
        payment_id,
        "escalate"
    ):

        print("\n🚨 PAYMENT ALREADY ESCALATED")

        return {
            "status": "already_escalated",
            "payment_id": payment_id,
            "action": "escalate",
            "message": (
                "This payment has already been escalated "
                "to the finance team."
            ),
            "decision": {
                "action": "escalate",
                "confidence": 0.75,
                "priority": (
                    "high"
                    if score["risk"] == "HIGH"
                    else "medium"
                ),
                "reason": (
                    "Payment has already been escalated "
                    "to the finance team."
                )
            }
        }

    # --------------------------------------------------------
    # ACTION LOOP
    # --------------------------------------------------------

    for attempt in range(MAX_ACTIONS):

        print(
            f"\n🔄 Recovery attempt "
            f"{attempt + 1}/{MAX_ACTIONS}"
        )

        previous_actions = get_previous_actions(
            payment_id
        )

        print(
            "📝 Previous actions:",
            previous_actions
        )

        # ----------------------------------------------------
        # AI DECISION
        # ----------------------------------------------------

        decision = llm_ai_decision(
            payment_id,
            payment,
            customer,
            score
        )

        action = decision["action"]

        print("\n🤖 AI DECISION")

        print(
            "Action:",
            action
        )

        print(
            "Confidence:",
            decision["confidence"]
        )

        print(
            "Priority:",
            decision["priority"]
        )

        print(
            "Reason:",
            decision["reason"]
        )

        # ----------------------------------------------------
        # HUMAN APPROVAL CHECK
        # ----------------------------------------------------

        if requires_human_approval(
            action,
            score["risk"]
        ):

            pending_approvals[payment_id] = {
                "payment_id": payment_id,
                "action": action,
                "risk": score["risk"],
                "reason": decision["reason"],
                "timestamp": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            }

            print("\n⚠️ HUMAN APPROVAL REQUIRED")

            return {
                "status": "pending_approval",
                "payment_id": payment_id,
                "action": action,
                "risk": score["risk"],
                "message": (
                    "High-risk recovery action requires "
                    "human finance approval."
                ),
                "decision": decision
            }

        # ----------------------------------------------------
        # SAFETY
        # ----------------------------------------------------

        allowed_actions = {
            "retry_payment",
            "send_payment_reminder",
            "send_payment_method_update",
            "escalate",
            "stop"
        }

        if action not in allowed_actions:

            return {
                "status": "invalid_action",
                "payment_id": payment_id,
                "action": action
            }

        # ----------------------------------------------------
        # STOP
        # ----------------------------------------------------

        if action == "stop":

            return {
                "status": "stopped",
                "payment_id": payment_id,
                "action": "stop"
            }

        # ----------------------------------------------------
        # DUPLICATE ACTION
        # ----------------------------------------------------

        if has_previous_action(
            payment_id,
            action
        ):

            print(
                f"⚠️ Action '{action}' "
                "already performed."
            )

            if action == "escalate":

                return {
                    "status": "already_escalated",
                    "payment_id": payment_id,
                    "action": "escalate",
                    "message": (
                        "This payment has already been "
                        "escalated to the finance team."
                    )
                }

            if action == "send_payment_reminder":

                return {
                    "status": "pending",
                    "payment_id": payment_id,
                    "action": action,
                    "message": (
                        "Payment reminder already sent. "
                        "Waiting for customer action."
                    )
                }

            if action == "send_payment_method_update":

                return {
                    "status": "pending",
                    "payment_id": payment_id,
                    "action": action,
                    "message": (
                        "Payment method update request "
                        "already sent. Waiting for customer action."
                    )
                }

            if action == "retry_payment":

                action = "escalate"

                decision["reason"] = (
                    "Payment retry was already attempted; "
                    "escalating to finance."
                )

        # ----------------------------------------------------
        # CUSTOMER MESSAGE
        # ----------------------------------------------------

        message = generate_recovery_message(
            payment,
            customer,
            action
        )

        # ----------------------------------------------------
        # SEND CUSTOMER MESSAGE
        # ----------------------------------------------------

        if action in [
            "send_payment_reminder",
            "send_payment_method_update"
        ]:

            send_recovery_message(
                payment["customer_id"],
                payment_id,
                message
            )

        # ----------------------------------------------------
        # EXECUTE ACTION
        # ----------------------------------------------------

        if action == "retry_payment":

            result = retry_payment(
                payment_id
            )

        elif action == "send_payment_reminder":

            result = send_payment_reminder(
                payment["customer_id"],
                payment_id,
                payment["amount"]
            )

        elif action == "send_payment_method_update":

            result = send_payment_method_update(
                payment["customer_id"],
                payment_id
            )

        elif action == "escalate":

            result = escalate_payment(
                payment_id,
                decision["reason"]
            )

        else:

            result = {
                "status": "unknown"
            }

        print(
            "\n📊 Recovery action result:"
        )

        print(result)

        # ----------------------------------------------------
        # SAVE HISTORY
        # ----------------------------------------------------

        add_recovery_history(
            payment_id,
            action,
            result["status"],
            message
        )

        # ----------------------------------------------------
        # AUDIT
        # ----------------------------------------------------

        record_audit_event(
            payment_id,
            payment,
            score,
            action,
            result["status"],
            decision["reason"]
        )

        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        if result["status"] == "success":

            payment["status"] = "success"

            print(
                "\n💰 PAYMENT SUCCESSFULLY RECOVERED"
            )

            return {
                "status": "success",
                "payment_id": payment_id,
                "action": action,
                "amount": payment["amount"],
                "message": (
                    "Payment recovered successfully"
                )
            }

        # ----------------------------------------------------
        # ALREADY RECOVERED
        # ----------------------------------------------------

        if result["status"] == "already_recovered":

            payment["status"] = "success"

            return {
                "status": "success",
                "payment_id": payment_id,
                "action": "already_recovered",
                "amount": payment["amount"],
                "message": (
                    "Payment is already recovered"
                )
            }

        # ----------------------------------------------------
        # CUSTOMER ACTION REQUIRED
        # ----------------------------------------------------

        if action in [
            "send_payment_reminder",
            "send_payment_method_update"
        ]:

            return {
                "status": "pending",
                "payment_id": payment_id,
                "action": action,
                "message": (
                    "Waiting for customer payment"
                )
            }

        # ----------------------------------------------------
        # ESCALATED
        # ----------------------------------------------------

        if action == "escalate":

            return {
                "status": "escalated",
                "payment_id": payment_id,
                "action": "escalate",
                "message": (
                    "Human finance intervention required"
                )
            }

    # --------------------------------------------------------
    # MAXIMUM ATTEMPTS
    # --------------------------------------------------------

    print(
        "\n🚨 Maximum recovery attempts reached."
    )

    if has_previous_action(
        payment_id,
        "escalate"
    ):

        return {
            "status": "already_escalated",
            "payment_id": payment_id,
            "action": "escalate",
            "message": (
                "This payment has already been "
                "escalated to the finance team."
            )
        }

    # --------------------------------------------------------
    # FINAL ESCALATION
    # --------------------------------------------------------

    result = escalate_payment(
        payment_id,
        "Maximum recovery attempts reached"
    )

    message = generate_recovery_message(
        payment,
        customer,
        "escalate"
    )

    add_recovery_history(
        payment_id,
        "escalate",
        result["status"],
        message
    )

    record_audit_event(
        payment_id,
        payment,
        score,
        "escalate",
        result["status"],
        "Maximum recovery attempts reached"
    )

    return {
        "status": "escalated",
        "payment_id": payment_id,
        "action": "escalate",
        "message": (
            "Maximum recovery attempts reached"
        )
    }

# ============================================================
# HUMAN APPROVAL
# ============================================================

def approve_recovery_action(payment_id, approved):

    payment = get_payment(payment_id)

    if payment is None:
        return {
            "status": "payment_not_found",
            "payment_id": payment_id
        }

    # --------------------------------------------------------
    # FIND PENDING APPROVAL
    # --------------------------------------------------------

    pending_action = pending_approvals.get(payment_id)

    if pending_action is None:
        return {
            "status": "no_pending_approval",
            "payment_id": payment_id
        }

    action = pending_action["action"]

    # --------------------------------------------------------
    # REJECT
    # --------------------------------------------------------

    if not approved:

        add_recovery_history(
            payment_id,
            action,
            "rejected",
            "Human finance reviewer rejected the recovery action."
        )

        del pending_approvals[payment_id]

        return {
            "status": "rejected",
            "payment_id": payment_id,
            "action": action,
            "message": "Recovery action rejected by human reviewer."
        }

    # --------------------------------------------------------
    # APPROVE
    # --------------------------------------------------------

    if action == "send_payment_reminder":

        result = send_payment_reminder(
            payment["customer_id"],
            payment_id,
            payment["amount"]
        )

    elif action == "send_payment_method_update":

        result = send_payment_method_update(
            payment["customer_id"],
            payment_id
        )

    elif action == "retry_payment":

        result = retry_payment(payment_id)

    elif action == "escalate":

        result = escalate_payment(
            payment_id,
            "Approved by human finance reviewer."
        )

    else:

        return {
            "status": "invalid_action",
            "payment_id": payment_id,
            "action": action
        }

    # --------------------------------------------------------
    # SAVE APPROVAL RESULT
    # --------------------------------------------------------

    add_recovery_history(
        payment_id,
        action,
        result.get("status", "unknown"),
        "Recovery action approved by human finance reviewer."
    )

    # --------------------------------------------------------
    # REMOVE PENDING APPROVAL
    # --------------------------------------------------------

    del pending_approvals[payment_id]

    return {
        "status": "approved",
        "payment_id": payment_id,
        "action": action,
        "result": result,
        "message": "Recovery action approved and executed."
    }
# ============================================================
# BATCH AUTOMATIC RECOVERY
# ============================================================

def batch_recovery():

    print("\n================================")
    print("🚀 BATCH REVENUE RECOVERY")
    print("================================")

    results = []

    payment_ids = list(payments.keys())

    for payment_id in payment_ids:

        print("\n--------------------------------")
        print("Processing:", payment_id)
        print("--------------------------------")

        try:

            result = automatic_recovery_loop(
                payment_id
            )

            results.append({

                "payment_id": payment_id,

                "status": result.get(
                    "status",
                    "unknown"
                ),

                "action": result.get(
                    "action",
                    ""
                ),

                "amount": payments[payment_id]["amount"]

            })

        except Exception as e:

            print(
                f"❌ Error processing {payment_id}:",
                str(e)
            )

            results.append({

                "payment_id": payment_id,

                "status": "error",

                "action": "",

                "amount":
                    payments[payment_id]["amount"],

                "error": str(e)

            })

    # --------------------------------------------------------
    # BATCH SUMMARY
    # --------------------------------------------------------

    recovered = 0

    pending = 0

    escalated = 0

    failed = 0

    for result in results:

        if result["status"] == "success":

            recovered += 1

        elif result["status"] == "pending":

            pending += 1

        elif result["status"] in [
            "escalated",
            "already_escalated"
        ]:

            escalated += 1

        else:

            failed += 1

    recovered_amount = get_recovered_amount()

    total_value = sum(
        payment["amount"]
        for payment in payments.values()
    )

    remaining_risk = sum(

        payment["amount"]

        for payment in payments.values()

        if payment["status"] == "failed"

    )

    if total_value > 0:

        recovery_rate = round(
            (
                recovered_amount
                /
                total_value
            ) * 100,
            2
        )

    else:

        recovery_rate = 0

    print("\n================================")
    print("📊 BATCH RECOVERY SUMMARY")
    print("================================")

    print(
        "Payments processed:",
        len(results)
    )

    print(
        "Recovered:",
        recovered
    )

    print(
        "Pending:",
        pending
    )

    print(
        "Escalated:",
        escalated
    )

    print(
        "Failed/Error:",
        failed
    )

    print(
        "Recovered revenue: ₹",
        recovered_amount
    )

    print(
        "Remaining revenue at risk: ₹",
        remaining_risk
    )

    print(
        "Recovery rate:",
        recovery_rate,
        "%"
    )

    return {

        "status": "batch_completed",

        "payments_processed":
            len(results),

        "recovered_payments":
            recovered,

        "pending_payments":
            pending,

        "escalated_payments":
            escalated,

        "failed_payments":
            failed,

        "recovered_revenue":
            recovered_amount,

        "remaining_revenue_at_risk":
            remaining_risk,

        "recovery_rate":
            recovery_rate,

        "results":
            results
    }


# ============================================================
# MAIN AGENT
# ============================================================

def revenue_recovery_agent(payment_id):

    return automatic_recovery_loop(
        payment_id
    )


# ============================================================
# MOCK RECOVERY AGENT
# ============================================================

def run_mock_recovery_agent(payment_id):

    return automatic_recovery_loop(
        payment_id
    )


# ============================================================
# SIMULATE CUSTOMER PAYMENT
# ============================================================

def simulate_payment_success(payment_id):

    payment = get_payment(payment_id)

    if payment is None:
        return False

    payment["status"] = "success"

    mark_payment_recovered(
        payment_id,
        payment["amount"]
    )

    print(
        "\n💰 Simulated customer payment received!"
    )

    return True

# ============================================================
# PAYMENT STATUS MONITOR
# ============================================================

def monitor_payment_status(payment_id):

    payment = get_payment(payment_id)

    if payment is None:
        return {
            "status": "payment_not_found",
            "payment_id": payment_id
        }

    if payment["status"] == "success":

        return {
            "status": "recovered",
            "payment_id": payment_id,
            "amount": payment["amount"],
            "message": "Payment has been successfully recovered."
        }

    return {
        "status": "pending",
        "payment_id": payment_id,
        "amount": payment["amount"],
        "message": "Payment is still awaiting recovery."
    }
# ============================================================
# AUDIT LOG
# ============================================================

def show_audit_log():

    print("\n================================")
    print("📋 RECOVERY AUDIT LOG")
    print("================================")

    if not audit_log:

        print(
            "No audit events recorded."
        )

        return

    for index, event in enumerate(
        audit_log,
        start=1
    ):

        print(
            f"\n--- Event {index} ---"
        )

        for key, value in event.items():

            print(
                f"{key}: {value}"
            )

# ============================================================
# RECOVERY ANALYTICS
# ============================================================

# ============================================================
# RECOVERY ANALYTICS
# ============================================================

def get_recovery_analytics():

    total_payments = len(payments)

    recovered_payments_count = 0
    failed_payments_count = 0
    pending_payments_count = 0
    escalated_payments_count = 0

    active_risk_payments = 0

    total_value = 0
    revenue_at_risk = 0


    # ========================================================
    # PAYMENT STATUS ANALYSIS
    # ========================================================

    for payment_id, payment in payments.items():

        amount = payment["amount"]

        total_value += amount


        # ----------------------------------------------------
        # RECOVERED
        # ----------------------------------------------------

        if payment["status"] == "success":

            recovered_payments_count += 1

            continue


        # ----------------------------------------------------
        # ACTIVE RISK
        # ----------------------------------------------------

        active_risk_payments += 1

        revenue_at_risk += amount


        # ----------------------------------------------------
        # FAILED
        # ----------------------------------------------------

        if payment["status"] == "failed":

            failed_payments_count += 1


        # ----------------------------------------------------
        # CHECK HISTORY FOR ESCALATION / PENDING
        # ----------------------------------------------------

        history = get_recovery_history(
            payment_id
        )


        actions = [
            item["action"]
            for item in history
        ]


        # ----------------------------------------------------
        # ESCALATED
        # ----------------------------------------------------

        if "escalate" in actions:

            escalated_payments_count += 1


        # ----------------------------------------------------
        # PENDING
        # ----------------------------------------------------

        elif (
            "send_payment_reminder" in actions
            or
            "send_payment_method_update" in actions
        ):

            pending_payments_count += 1


    # ========================================================
    # RECOVERED REVENUE
    # ========================================================

    recovered_revenue = get_recovered_amount()


    # ========================================================
    # RECOVERY RATE
    # ========================================================

    if total_value > 0:

        recovery_rate = round(
            (
                recovered_revenue
                /
                total_value
            ) * 100,
            2
        )

    else:

        recovery_rate = 0


    # ========================================================
    # ACTION STATISTICS
    # ========================================================

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()


    cursor.execute("""
        SELECT
            action,
            COUNT(*)
        FROM recovery_history
        GROUP BY action
        ORDER BY COUNT(*) DESC
    """)


    action_rows = cursor.fetchall()


    conn.close()


    action_statistics = []


    for row in action_rows:

        action_statistics.append({

            "action": row[0],

            "count": row[1]

        })


    # ========================================================
    # HIGH RISK PAYMENTS
    # ========================================================

    high_risk_payments = []


    for payment_id, payment in payments.items():

        if payment["status"] == "success":

            continue


        customer = get_customer_history(
            payment["customer_id"]
        )


        if customer is None:

            continue


        score = calculate_recovery_score(
            payment,
            customer
        )


        if score["risk"] == "HIGH":

            high_risk_payments.append({

                "payment_id":
                    payment_id,

                "customer_id":
                    payment["customer_id"],

                "amount":
                    payment["amount"],

                "recovery_probability":
                    score[
                        "recovery_probability"
                    ],

                "risk":
                    score["risk"],

                "failure_reason":
                    payment[
                        "failure_reason"
                    ]

            })


    # ========================================================
    # RETURN ANALYTICS
    # ========================================================

    return {

        "total_payments":
            total_payments,


        "recovered_payments":
            recovered_payments_count,


        "pending_payments":
            pending_payments_count,


        "escalated_payments":
            escalated_payments_count,


        "active_risk_payments":
            active_risk_payments,


        "failed_payments":
            failed_payments_count,


        "total_value":
            total_value,


        "revenue_at_risk":
            revenue_at_risk,


        "recovered_revenue":
            recovered_revenue,


        "recovery_rate":
            recovery_rate,


        "high_risk_payments":
            high_risk_payments,


        "action_statistics":
            action_statistics

    }


# ============================================================
# INITIALIZE DATABASE
# ============================================================

init_database()
if __name__ == "__main__":

    payment_id = "PAY002"

    payment = get_payment(payment_id)

    customer = get_customer_history(
        payment["customer_id"]
    )

    score = calculate_recovery_score(
        payment,
        customer
    )

    decision = mock_ai_decision(
        payment_id,
        payment,
        customer,
        score
    )

    plan = generate_recovery_plan(
        payment_id,
        payment,
        customer,
        score,
        decision
    )

    print("\n================================")
    print("🤖 AI RECOVERY PLAN")
    print("================================")

    print("\nPayment:", plan["payment_id"])
    print("Risk:", plan["risk"])
    print(
        "Recovery Probability:",
        plan["recovery_probability"],
        "%"
    )
    print(
        "Recommended Action:",
        plan["recommended_action"]
    )
    print(
        "Confidence:",
        plan["confidence"]
    )
    print(
        "Priority:",
        plan["priority"]
    )
    print(
        "Reason:",
        plan["reason"]
    )

    print("\nSteps:")

    for index, step in enumerate(
        plan["steps"],
        start=1
    ):

        print(
            f"{index}. {step}"
        )
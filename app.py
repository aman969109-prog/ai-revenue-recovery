from flask import Flask, jsonify, send_from_directory

from revenue_agent import (
    get_payment,
    get_customer_history,
    calculate_recovery_score,
    mock_ai_decision,
    retry_payment,
    send_payment_reminder,
    send_payment_method_update,
    escalate_payment,
    generate_recovery_message,
    add_recovery_history,
    get_recovery_history,
    mark_payment_recovered,
    get_recovered_amount,
    automatic_recovery_loop,
    batch_recovery,
    get_recovery_analytics,
    monitor_payment_status,
    approve_recovery_action
)


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)


# ============================================================
# FRONTEND
# ============================================================

@app.route("/")
def home():

    return send_from_directory(
        "frontend",
        "index.html"
    )


@app.route("/style.css")
def style():

    return send_from_directory(
        "frontend",
        "style.css"
    )


@app.route("/script.js")
def script():

    return send_from_directory(
        "frontend",
        "script.js"
    )


# ============================================================
# PAYMENT INFORMATION
# ============================================================

@app.route("/api/payment/<payment_id>")
def payment_details(payment_id):

    payment = get_payment(payment_id)

    if payment is None:

        return jsonify({

            "status": "payment_not_found",

            "error": "Payment not found",

            "payment_id": payment_id

        }), 404


    customer = get_customer_history(
        payment["customer_id"]
    )

    if customer is None:

        return jsonify({

            "status": "customer_not_found",

            "error": "Customer not found",

            "payment_id": payment_id

        }), 404


    # ========================================================
    # RECOVERY SCORE
    # ========================================================

    score = calculate_recovery_score(
        payment,
        customer
    )


    # ========================================================
    # ALREADY RECOVERED
    # ========================================================

    if payment["status"] == "success":

        decision = {

            "action": "recovered",

            "confidence": 1.0,

            "priority": "low",

            "reason": "Payment has already been successfully recovered."
        }

        message = (
            f"Payment of ₹{payment['amount']} "
            f"has already been successfully recovered."
        )

    else:

        # ====================================================
        # AI DECISION FOR FAILED PAYMENT
        # ====================================================

        decision = mock_ai_decision(
            payment_id,
            payment,
            customer,
            score
        )

        message = generate_recovery_message(
            payment,
            customer,
            decision["action"]
        )


    return jsonify({

        "status": "success",

        "payment_id": payment_id,

        "payment": payment,

        "customer": customer,

        "score": score,

        "decision": decision,

        "message": message

    })


# ============================================================
# MANUAL RECOVERY
# ============================================================

@app.route(
    "/api/recover/<payment_id>",
    methods=["POST"]
)
def recover_payment(payment_id):

    payment = get_payment(payment_id)

    if payment is None:

        return jsonify({

            "status": "payment_not_found",

            "payment_id": payment_id

        }), 404

    customer = get_customer_history(
        payment["customer_id"]
    )

    if customer is None:

        return jsonify({

            "status": "customer_not_found",

            "payment_id": payment_id

        }), 404

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

    action = decision["action"]

    # --------------------------------------------------------
    # EXECUTE AI ACTION
    # --------------------------------------------------------

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

    elif action == "stop":

        return jsonify({

            "status": "stopped",

            "payment_id": payment_id,

            "action": "stop"

        })

    else:

        return jsonify({

            "status": "invalid_action",

            "payment_id": payment_id,

            "action": action

        }), 400

    # --------------------------------------------------------
    # GENERATE MESSAGE
    # --------------------------------------------------------

    message = generate_recovery_message(

        payment,

        customer,

        action
    )

    # --------------------------------------------------------
    # SAVE HISTORY
    # --------------------------------------------------------

    add_recovery_history(

        payment_id,

        action,

        result["status"],

        message
    )

    # --------------------------------------------------------
    # MARK PAYMENT RECOVERED
    # --------------------------------------------------------

    if result["status"] == "success":

        mark_payment_recovered(

            payment_id,

            payment["amount"]
        )

    # --------------------------------------------------------
    # RETURN RESULT
    # --------------------------------------------------------

    return jsonify({

        "status": result["status"],

        "payment_id": payment_id,

        "action": action,

        "decision": decision,

        "result": result,

        "message": message

    })


# ============================================================
# AUTOMATIC RECOVERY
# ============================================================

@app.route(
    "/api/automatic-recover/<payment_id>",
    methods=["POST"]
)
def automatic_recover_payment(payment_id):

    print("\n================================")
    print("🚀 AUTOMATIC RECOVERY API")
    print("================================")

    print(
        "Payment ID:",
        payment_id
    )

    # --------------------------------------------------------
    # CHECK PAYMENT
    # --------------------------------------------------------

    payment = get_payment(payment_id)

    if payment is None:

        return jsonify({

            "status": "payment_not_found",

            "payment_id": payment_id,

            "message": "Payment not found"

        }), 404

    try:

        # ----------------------------------------------------
        # RUN AGENT
        # ----------------------------------------------------

        result = automatic_recovery_loop(
            payment_id
        )

        print(
            "\n🤖 Automatic recovery result:",
            result
        )

        if result is None:

            return jsonify({

                "status": "no_result",

                "payment_id": payment_id

            })

        return jsonify(result)

    except Exception as e:

        print(
            "\n❌ AUTOMATIC RECOVERY ERROR:"
        )

        print(
            type(e).__name__,
            str(e)
        )

        return jsonify({

            "status": "error",

            "payment_id": payment_id,

            "error": str(e)

        }), 500


# ============================================================
# BATCH RECOVERY API
# ============================================================

@app.route(
    "/api/batch-recover",
    methods=["POST"]
)
def run_batch_recovery():

    print("\n================================")
    print("🚀 BATCH RECOVERY API")
    print("================================")

    try:

        result = batch_recovery()

        return jsonify(result)

    except Exception as e:

        print(
            "\n❌ BATCH RECOVERY ERROR:"
        )

        print(
            type(e).__name__,
            str(e)
        )

        return jsonify({

            "status": "error",

            "error": str(e)

        }), 500


# ============================================================
# RECOVERY HISTORY
# ============================================================

@app.route("/api/history/<payment_id>")
def recovery_history(payment_id):

    history = get_recovery_history(
        payment_id
    )

    return jsonify({

        "payment_id": payment_id,

        "history": history

    })


# ============================================================
# REVENUE METRICS
# ============================================================

@app.route("/api/metrics")
def get_metrics():

    payment_list = [

        get_payment("PAY001"),

        get_payment("PAY002"),

        get_payment("PAY003")

    ]

    # --------------------------------------------------------
    # REVENUE AT RISK
    # --------------------------------------------------------

    total_at_risk = sum(

        payment["amount"]

        for payment in payment_list

        if payment is not None
        and payment["status"] == "failed"

    )

    # --------------------------------------------------------
    # RECOVERED REVENUE
    # --------------------------------------------------------

    recovered_amount = get_recovered_amount()

    # --------------------------------------------------------
    # RECOVERY RATE
    # --------------------------------------------------------

    total_original_value = sum(

        payment["amount"]

        for payment in payment_list

        if payment is not None

    )

    if total_original_value > 0:

        recovery_rate = round(

            (
                recovered_amount
                /
                total_original_value
            ) * 100,

            2

        )

    else:

        recovery_rate = 0

    # --------------------------------------------------------
    # HIGH RISK PAYMENTS
    # --------------------------------------------------------

    high_risk = 0

    for payment in payment_list:

        if payment is None:
            continue

        # Recovered payments are no longer
        # considered active risk.

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

            high_risk += 1

    # --------------------------------------------------------
    # RETURN METRICS
    # --------------------------------------------------------

    return jsonify({

        "total_revenue_at_risk":
            total_at_risk,

        "recovered_revenue":
            recovered_amount,

        "recovery_rate":
            recovery_rate,

        "high_risk_payments":
            high_risk,

        "total_payments":
            len(payment_list)

    })


# ============================================================
# RECOVERY ANALYTICS API
# ============================================================

@app.route("/api/analytics")
def recovery_analytics():

    try:

        analytics = get_recovery_analytics()

        return jsonify({

            "status": "success",

            "analytics": analytics

        })

    except Exception as e:

        print(
            "\n❌ ANALYTICS ERROR:"
        )

        print(
            type(e).__name__,
            str(e)
        )

        return jsonify({

            "status": "error",

            "error": str(e)

        }), 500

@app.route("/api/pending-approval/<payment_id>")
def pending_approval(payment_id):

    history = get_recovery_history(payment_id)

    for item in history:
        if item["status"] == "pending_approval":
            return {
                "status": "pending_approval",
                "payment_id": payment_id,
                "action": item["action"],
                "message": item["message"]
            }

    return {
        "status": "no_pending_approval",
        "payment_id": payment_id
    }
@app.route(
    "/api/approve-recovery/<payment_id>",
    methods=["POST"]
)
def approve_recovery(payment_id):

    result = approve_recovery_action(
        payment_id,
        True
    )

    return jsonify(result)
@app.route("/api/payment-status/<payment_id>")
def payment_status(payment_id):

    result = monitor_payment_status(payment_id)

    return result
# ============================================================
# 404 HANDLER
# ============================================================

@app.errorhandler(404)
def not_found(error):

    return jsonify({

        "status": "not_found",

        "error":
            "API endpoint or resource not found"

    }), 404


# ============================================================
# SERVER
# ============================================================

if __name__ == "__main__":

    print("\n================================")
    print("🚀 REVENUE RECOVERY SERVER")
    print("================================")

    print(
        "🌐 http://127.0.0.1:5000"
    )

    print(
        "📊 Dashboard ready"
    )

    print(
        "================================\n"
    )

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
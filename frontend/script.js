
let currentPaymentId = "PAY002";


// ============================================================
// SELECT PAYMENT
// ============================================================

async function loadSelectedPayment() {

    const input = document.getElementById("payment-input");

    if (!input) {
        console.error("❌ payment-input not found");
        return;
    }

    const paymentId = input.value.trim().toUpperCase();

    if (!paymentId) {
        showResult("❌ Please enter a payment ID.");
        return;
    }

    currentPaymentId = paymentId;

    console.log(
        "🔎 Selected payment:",
        currentPaymentId
    );

    await loadPayment();
}


// ============================================================
// LOAD PAYMENT DETAILS
// ============================================================

async function loadPayment() {

    try {

        showResult(
            `🔄 Loading ${currentPaymentId}...`
        );

        const response = await fetch(
            `/api/payment/${encodeURIComponent(currentPaymentId)}`
        );

        const data = await response.json();

        console.log(
            "📡 PAYMENT DATA:",
            data
        );

        if (!response.ok) {

            showResult(
                `❌ ${data.error || "Payment not found"}`
            );

            return;
        }


        // ========================================================
        // PAYMENT INFORMATION
        // ========================================================

        setText(
            "payment-id",
            data.payment_id
        );

        setText(
            "customer-id",
            data.payment.customer_id
        );

        setText(
            "amount",
            `₹${Number(
                data.payment.amount
            ).toLocaleString("en-IN")}`
        );

        setText(
            "status",
            data.payment.status
        );

        setText(
            "failure-reason",
            data.payment.failure_reason
        );


        // ========================================================
        // RECOVERY ANALYSIS
        // ========================================================

        setText(
            "success-rate",
            `${Number(
                data.score.success_rate
            ).toFixed(2)}%`
        );

        setText(
            "recovery-probability",
            `${Number(
                data.score.recovery_probability
            ).toFixed(2)}%`
        );

        setText(
            "risk",
            data.score.risk
        );


        // ========================================================
        // AI DECISION
        // ========================================================

        setText(
            "action",
            formatAction(
                data.decision.action
            )
        );

        setText(
            "confidence",
            `${(
                Number(
                    data.decision.confidence
                ) * 100
            ).toFixed(0)}%`
        );

        setText(
            "priority",
            data.decision.priority
        );

        setText(
            "reason",
            data.decision.reason
        );


        // ========================================================
        // RECOVERY MESSAGE
        // ========================================================

        setText(
            "message",
            data.message
        );


        // ========================================================
        // RECOVERY BUTTON STATE
        // ========================================================

        const runButton =
            document.getElementById("run-button");

        if (runButton) {

            if (data.payment.status === "success") {

                runButton.disabled = true;

                runButton.textContent =
                    "✅ Payment Recovered";

            } else {

                runButton.disabled = false;

                runButton.textContent =
                    "🚀 Run Recovery";
            }
        }


        // ========================================================
        // SUCCESS MESSAGE
        // ========================================================

        showResult(
            `✅ Payment ${currentPaymentId} loaded successfully.`
        );


        // ========================================================
        // LOAD HISTORY
        // ========================================================

        await loadHistory();

    }

    catch (error) {

        console.error(
            "❌ Load payment error:",
            error
        );

        showResult(
            "❌ Unable to connect to the server."
        );
    }
}


// ============================================================
// RUN AUTOMATIC RECOVERY
// ============================================================

async function runRecovery(paymentId = null) {

    if (paymentId) {

        currentPaymentId =
            String(paymentId)
                .trim()
                .toUpperCase();
    }


    if (!currentPaymentId) {

        showResult(
            "❌ Please select a payment first."
        );

        return;
    }


    const button =
        document.getElementById("run-button");


    try {

        // --------------------------------------------------------
        // DISABLE BUTTON
        // --------------------------------------------------------

        if (button) {

            button.disabled = true;

            button.textContent =
                "⏳ Recovering...";
        }


        showResult(
            `🤖 Recovery engine is analyzing ${currentPaymentId}...`
        );


        console.log(
            "🚀 Starting automatic recovery:",
            currentPaymentId
        );


        // --------------------------------------------------------
        // CALL AUTOMATIC RECOVERY API
        // --------------------------------------------------------

        const response = await fetch(

            `/api/automatic-recover/${encodeURIComponent(
                currentPaymentId
            )}`,

            {
                method: "POST"
            }
        );


        const data =
            await response.json();


        console.log(
            "🤖 RECOVERY RESPONSE:",
            data
        );


        // --------------------------------------------------------
        // HANDLE HTTP ERROR
        // --------------------------------------------------------

        if (!response.ok) {

            showResult(

                `❌ ${
                    data.error ||
                    data.message ||
                    "Recovery request failed."
                }`

            );

            return;
        }


        // ========================================================
        // RECOVERY RESULT
        // ========================================================

        if (data.status === "success") {

            showResult(
                `💰 Payment recovered successfully! ₹${
                    Number(
                        data.amount || 0
                    ).toLocaleString("en-IN")
                } recovered.`
            );
        }

       else if (data.status === "pending") {

           showResult(
           "⏳ Recovery action completed. Customer action is required."
         );
        }

       else if (data.status === "pending_approval") {

        document.getElementById("approve-btn").style.display =
        "inline-block";

        showResult(
        "⚠️ Human finance approval is required."
        );
       }

        else if (data.status === "escalated") {

            showResult(
                "🚨 Payment escalated for manual finance review."
            );
        }


        else if (
            data.status === "already_escalated"
        ) {

            showResult(
                "⚠️ This payment has already been escalated."
            );
        }


        else if (
            data.status === "stopped"
        ) {

            showResult(
                "🛑 Recovery process stopped."
            );
        }


        else if (
            data.status === "payment_not_found"
        ) {

            showResult(
                `❌ Payment ${currentPaymentId} was not found.`
            );
        }


        else if (
            data.status === "customer_not_found"
        ) {

            showResult(
                "❌ Customer information was not found."
            );
        }


        else if (
            data.status === "invalid_action"
        ) {

            showResult(
                "⚠️ Recovery engine selected an invalid action."
            );
        }


        else if (
            data.status === "no_result"
        ) {

            showResult(
                "⚠️ Recovery engine returned no result."
            );
        }


        else {

            showResult(

                `📊 ${
                    data.message ||
                    "Recovery process completed."
                }`

            );
        }


        // ========================================================
        // REFRESH EVERYTHING
        // ========================================================

        await loadPayment();


        await loadMetrics();

        await loadAnalytics();

    }

    catch (error) {

        console.error(
            "❌ Recovery error:",
            error
        );

        showResult(
            "❌ Recovery request failed. Make sure Flask is running."
        );
    }


    finally {

        // Don't permanently enable the button
        // if payment has already been recovered.

        const payment =
            await getCurrentPaymentSafely();

        if (button) {

            if (
                payment &&
                payment.status === "success"
            ) {

                button.disabled = true;

                button.textContent =
                    "✅ Payment Recovered";

            } else {

                button.disabled = false;

                button.textContent =
                    "🚀 Run Recovery";
            }
        }
    }
}


// ============================================================
// APPROVE RECOVERY ACTION
// ============================================================

async function approveRecovery() {

    const paymentId = currentPaymentId;

    try {

        const response = await fetch(
            `/api/approve-recovery/${paymentId}`,
            {
                method: "POST"
            }
        );

        const result = await response.json();

        console.log("Approval result:", result);

        document.getElementById("result").innerText =
            result.message || "Recovery approved.";

        // Hide approval button after approval
        document.getElementById("approve-btn").style.display = "none";

        // Refresh payment information
        await loadPayment(paymentId);
        await loadMetrics();
        await loadAnalytics();
        await loadHistory(paymentId);

    } catch (error) {

        console.error("Approval error:", error);

        document.getElementById("result").innerText =
            "❌ Failed to approve recovery.";
    }
}

// ============================================================
// LOAD RECOVERY HISTORY
// ============================================================

async function loadHistory() {

    const historyContainer =
        document.getElementById("history");


    if (!historyContainer) {

        console.warn(
            "⚠️ History element not found."
        );

        return;
    }


    try {

        const response =
            await fetch(
                `/api/history/${encodeURIComponent(
                    currentPaymentId
                )}`
            );


        const data =
            await response.json();


        console.log(
            "📋 HISTORY:",
            data
        );


        if (!response.ok) {

            historyContainer.innerHTML =
                "<p>Unable to load recovery history.</p>";

            return;
        }


        const history =
            data.history || [];


        if (history.length === 0) {

            historyContainer.innerHTML =
                "<p>No recovery actions yet.</p>";

            return;
        }


        historyContainer.innerHTML =
            "";


        history.forEach(
            (item, index) => {

                const entry =
                    document.createElement("div");

                entry.className =
                    "history-entry";


                const action =
                    document.createElement("strong");

                action.textContent =
                    `${index + 1}. ${
                        formatAction(item.action)
                    }`;


                const status =
                    document.createElement("span");

                status.textContent =
                    `Status: ${item.status}`;


                const message =
                    document.createElement("p");

                message.textContent =
                    item.message || "";


                const timestamp =
                    document.createElement("small");

                timestamp.textContent =
                    item.timestamp || "";


                entry.appendChild(
                    action
                );

                entry.appendChild(
                    status
                );

                entry.appendChild(
                    message
                );

                entry.appendChild(
                    timestamp
                );


                historyContainer.appendChild(
                    entry
                );
            }
        );

    }

    catch (error) {

        console.error(
            "❌ History loading error:",
            error
        );

        historyContainer.innerHTML =
            "<p>Unable to load history.</p>";
    }
}


// ============================================================
// LOAD DASHBOARD METRICS
// ============================================================

async function loadMetrics() {

    try {

        const response =
            await fetch(
                "/api/metrics"
            );


        const data =
            await response.json();


        console.log(
            "📊 METRICS:",
            data
        );


        if (!response.ok) {

            console.error(
                "❌ Metrics error:",
                data
            );

            return;
        }


        setText(

            "total-at-risk",

            `₹${Number(
                data.total_revenue_at_risk || 0
            ).toLocaleString("en-IN")}`

        );


        setText(

            "recovered-revenue",

            `₹${Number(
                data.recovered_revenue || 0
            ).toLocaleString("en-IN")}`

        );


        setText(

            "recovery-rate",

            `${Number(
                data.recovery_rate || 0
            ).toFixed(2)}%`

        );


        setText(

            "high-risk-payments",

            data.high_risk_payments || 0

        );

    }

    catch (error) {

        console.error(
            "❌ Metrics loading error:",
            error
        );
    }
}


// ============================================================
// LOAD ADVANCED ANALYTICS
// ============================================================

// ============================================================
// LOAD RECOVERY ANALYTICS
// ============================================================

// ============================================================
// LOAD RECOVERY ANALYTICS
// ============================================================

async function loadAnalytics() {

    try {

        const response = await fetch(
            "/api/analytics"
        );

        const data = await response.json();

        console.log(
            "📊 ANALYTICS:",
            data
        );

        // ----------------------------------------------------
        // HTTP ERROR
        // ----------------------------------------------------

        if (!response.ok) {

            console.error(
                "❌ Analytics error:",
                data
            );

            return;
        }

        // ----------------------------------------------------
        // IMPORTANT
        // Backend returns:
        //
        // {
        //     "status": "success",
        //     "analytics": {...}
        // }
        // ----------------------------------------------------

        const analytics =
            data.analytics || {};

        // ----------------------------------------------------
        // TOTAL PAYMENTS
        // ----------------------------------------------------

        setText(
            "analytics-total-payments",
            analytics.total_payments || 0
        );

        // ----------------------------------------------------
        // RECOVERED PAYMENTS
        // ----------------------------------------------------

        setText(
            "analytics-recovered-payments",
            analytics.recovered_payments || 0
        );

        // ----------------------------------------------------
        // PENDING PAYMENTS
        // ----------------------------------------------------

        setText(
            "analytics-pending-payments",
            analytics.pending_payments || 0
        );

        // ----------------------------------------------------
        // ESCALATED PAYMENTS
        // ----------------------------------------------------

        setText(
            "analytics-escalated-payments",
            analytics.escalated_payments || 0
        );

        // ----------------------------------------------------
        // ACTION STATISTICS
        // ----------------------------------------------------

        const container =
            document.getElementById(
                "action-statistics"
            );

        if (!container) {

            console.warn(
                "⚠️ action-statistics element not found"
            );

            return;
        }

        const statistics =
            analytics.action_statistics || [];

        // ----------------------------------------------------
        // NO STATISTICS
        // ----------------------------------------------------

        if (statistics.length === 0) {

            container.innerHTML =
                "<p>No recovery actions recorded yet.</p>";

            return;
        }

        // ----------------------------------------------------
        // CLEAR OLD DATA
        // ----------------------------------------------------

        container.innerHTML = "";

        // ----------------------------------------------------
        // DISPLAY ACTION STATISTICS
        // ----------------------------------------------------

        statistics.forEach(
            function (item) {

                const row =
                    document.createElement(
                        "div"
                    );

                row.className =
                    "history-entry";


                const action =
                    document.createElement(
                        "strong"
                    );

                action.textContent =
                    formatAction(
                        item.action
                    );


                const count =
                    document.createElement(
                        "span"
                    );

                count.textContent =
                    ` — ${item.count}`;


                row.appendChild(
                    action
                );

                row.appendChild(
                    count
                );


                container.appendChild(
                    row
                );

            }
        );

    }

    catch (error) {

        console.error(
            "❌ Analytics loading error:",
            error
        );

    }

}

// ============================================================
// GET CURRENT PAYMENT SAFELY
// ============================================================

async function getCurrentPaymentSafely() {

    try {

        const response =
            await fetch(
                `/api/payment/${encodeURIComponent(
                    currentPaymentId
                )}`
            );


        if (!response.ok) {

            return null;
        }


        const data =
            await response.json();


        return data.payment || null;

    }

    catch (error) {

        console.error(
            "❌ Payment status check failed:",
            error
        );

        return null;
    }
}


// ============================================================
// FORMAT AI ACTION
// ============================================================

function formatAction(action) {

    if (!action) {

        return "—";
    }


    const actionNames = {

        "retry_payment":
            "Retry Payment",

        "send_payment_reminder":
            "Send Payment Reminder",

        "send_payment_method_update":
            "Request Payment Method Update",

        "escalate":
            "Escalate Payment",

        "stop":
            "Stop Recovery",

        "recovered":
            "Payment Already Recovered"
    };


    return (
        actionNames[action] ||
        action
    );
}


// ============================================================
// SET TEXT SAFELY
// ============================================================

function setText(
    elementId,
    value
) {

    const element =
        document.getElementById(
            elementId
        );


    if (!element) {

        return;
    }


    element.textContent =

        value !== undefined &&
        value !== null

            ? value

            : "—";
}


// ============================================================
// SHOW RESULT
// ============================================================

function showResult(message) {

    const result =
        document.getElementById(
            "result"
        );


    if (!result) {

        return;
    }


    result.textContent =
        message;
}


// ============================================================
// PAGE LOAD
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    async function () {

        console.log(
            "🤖 AI Revenue Recovery started"
        );


        // --------------------------------------------------------
        // INVESTIGATE BUTTON
        // --------------------------------------------------------

        const investigateButton =
            document.getElementById(
                "investigate-button"
            );


        if (investigateButton) {

            investigateButton.addEventListener(
                "click",
                loadSelectedPayment
            );

        }


        // --------------------------------------------------------
        // RUN RECOVERY BUTTON
        // --------------------------------------------------------

        const runButton =
            document.getElementById(
                "run-button"
            );


        if (runButton) {

            runButton.addEventListener(
                "click",
                function () {

                    runRecovery();

                }
            );

        }


        // --------------------------------------------------------
        // INITIAL LOAD
        // --------------------------------------------------------

        await loadPayment();

        await loadMetrics();

        await loadAnalytics();

    }
);

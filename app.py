"""
Open on http://localhost:5000
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime, date
import database as db

app = Flask(__name__)

# Initialize DB tables on startup
db.initialize_database()

#
# Helper
#

def current_month():
    return date.today().strftime("%Y-%m")

#
# Pages
#

@app.route("/")
def dashboard():
    month = request.args.get("month", current_month())
    summary = db.get_monthly_summary(month)
    budgets = db.get_budgets_with_spending(month)
    goals = db.get_savings_goals()
    trend = db.get_spending_trend(6)
    transactions = db.get_transactions(month_year=month, limit=10)

    return render_template(
        "dashboard.html",
        month=month,
        summary=summary,
        budgets=budgets,
        goals=goals,
        trend=trend,
        transactions=transactions,
        today=date.today().isoformat(),
    )

@app.route("/transactions")
def transactions_page():
    month = request.args.get("month", current_month())
    budgets = db.get_budgets_with_spending(month)
    categories = db.get_categories()
    return render_template(
        "budgets.html",
        budgets=budgets,
        categories=categories,
        month=month,
    )

@app.route("/goals")
def goals_page():
    goals = db.get_savings_goals()
    return render_template("goals.html", goals=goals)

#
# API endpoints (called by the browser via fetch/AJAX)
#

@app.route("/api/transactions", methods=["POST"])
def api_add_transaction():
    data = request.json
    try:
        txn_id = db.add_transaction(
            date=data["date"],
            description=data["description"],
            amount=float(data["amount"]),
            txn_type=data["type"],
            category_id=int(data["category_id"]),
            notes=data.get("notes", ""),
        )
        return jsonify({"success": True, "id": txn_id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
    

@app.route("/api/budgets", methods=["POST"])
def api_set_budget():
    data = request.json
    try:
        db.set_budget(
            category_id=int(data["category_id"]),
            month_year=data["month_year"],
            limit_amt=float(data["limit_amt"]),
        )
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/categories", methods=["POST"])
def api_add_category():
    data = request.json
    try:
        cat_id = db.add_category(
            name=data["name"],
            color=data.get("color", "#6366f1"),
            icon=data.get("icon", "📦"),
        )
        return jsonify({"success": True, "id": cat_id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/goals", methods=["POST"])
def api_add_goal():
    data = request.json
    try:
        goal_id = db.add_savings_goal(
            name=data["name"],
            target_amount=float(data["target_amount"]),
            current_amount=float(data.get("current_amount", 0)),
            target_date=data.get("target_date"),
            notes=data.get("notes", ""),
        )
        return jsonify({"success": True, "id": goal_id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
    

@app.route("/api/goals/<int:goal_id>", methods=["PATCH"])
def api_update_goal(goal_id):
    data = request.json
    try:
        db.update_savings_goal(goal_id, float(data["current_amount"]))
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
    

@app.route("/api/goals/<int:goal_id>", methods=["DELETE"])
def api_delete_goal(goal_id):
    db.delete_savings_goal(goal_id)
    return jsonify({"success": True})


@app.route("/api/summary/<month_year>")
def api_summary(month_year):
    return jsonify(db.get_monthly_summary(month_year))


if __name__ == "__main__":
    print("\n💰 Finance Tracker is running!")
    print("   Open your browser to: http://localhost:5000\n")
    app.run(debug=True, port=5000)
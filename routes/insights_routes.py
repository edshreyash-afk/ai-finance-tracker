import plotly
import plotly.express as px
import json
import pandas as pd
from flask import Blueprint, render_template, flash, jsonify, request
from flask_login import login_required, current_user
from models import Transaction
from ai.insight_engine import compute_financial_insights
from ai.gemini_service import generate_financial_insights

insights = Blueprint("insights", __name__, url_prefix="/insights")

@insights.route("/")
@insights.route("/index")
@login_required
def index():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    
    # 1. Format data for the AI engine
    transaction_list = [{
        "date": t.date, 
        "amount": t.amount, 
        "category": t.category or "Uncategorized", 
        "type": t.type, 
        "description": t.description
    } for t in transactions]

    # 2. Get AI Insights
    insights_result = compute_financial_insights(transaction_list)

    # 3. Setup Default Variables for the Template
    trend_graph = None
    category_graph = None
    top_category_data = {"name": "N/A", "amount": 0.0} 
    
    # Removed static advice generation

    if transactions:
        df = pd.DataFrame(transaction_list)
        
        # Calculate Expense-specific data
        expense_df = df[df["type"] == "expense"]
        if not expense_df.empty:
            category_totals = expense_df.groupby("category")["amount"].sum()
            if not category_totals.empty:
                top_category_data = {
                    "name": category_totals.idxmax(),
                    "amount": category_totals.max()
                }

            # Category Graph
            cat_fig = px.pie(expense_df, names="category", values="amount", title="Expenses by Category")
            category_graph = json.dumps(cat_fig, cls=plotly.utils.PlotlyJSONEncoder)

        # Trend Graph
        df['month'] = pd.to_datetime(df['date']).dt.to_period('M').astype(str)
        trend_df = df.groupby(['month', 'type'])['amount'].sum().reset_index()
        if not trend_df.empty:
            trend_fig = px.bar(trend_df, x="month", y="amount", color="type", barmode="group", title="Income vs Expenses")
            trend_graph = json.dumps(trend_fig, cls=plotly.utils.PlotlyJSONEncoder)
    else:
        flash("No data yet. Add transactions to see insights!", "info")

    # 4. Render template with EVERYTHING it needs
    return render_template("insights.html", 
                           **insights_result, 
                           trend_graph=trend_graph,
                           category_graph=category_graph,
                           top_category=top_category_data)

@insights.route("/api/analyze", methods=["POST"])
@login_required
def analyze_finances():
    data = request.get_json() or {}
    user_question = data.get("question")
    
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    if not transactions:
        return jsonify({"success": False, "message": "No transactions to analyze."}), 400
        
    # Summarize data to save tokens and protect privacy
    income = sum(t.amount for t in transactions if t.type == 'income')
    expenses = sum(t.amount for t in transactions if t.type == 'expense')
    
    # Category totals
    cat_totals = {}
    for t in transactions:
        if t.type == 'expense':
            cat = t.category or "Uncategorized"
            cat_totals[cat] = cat_totals.get(cat, 0) + t.amount
            
    summary_data = {
        "total_income": income,
        "total_expenses": expenses,
        "net_balance": income - expenses,
        "expenses_by_category": cat_totals,
        "transaction_count": len(transactions)
    }
    
    try:
        insights_result = generate_financial_insights(summary_data, user_question)
        return jsonify({"success": True, "data": insights_result})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
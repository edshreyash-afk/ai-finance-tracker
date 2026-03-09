from flask import Blueprint, render_template, flash
from flask_login import login_required, current_user
from models import Transaction
import plotly
import plotly.express as px
import json
import pandas as pd

dashboard = Blueprint("dashboard", __name__, url_prefix="/dashboard")

@dashboard.route("/")
@dashboard.route("/index")
@login_required
def index():
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()
    
    data = []
    for t in transactions:
        data.append({
            "amount": t.amount,
            "category": t.category or "Uncategorized",
            "type": t.type,
            "date": t.date
        })
    
    df = pd.DataFrame(data)
    
    if df.empty:
        flash("No transactions yet. Add some to see insights!", "info")
        return render_template("dashboard.html", 
                             graphJSON=None, 
                             balance=0, 
                             income=0, 
                             expenses=0, 
                             transactions=[])
    
    # Aggregates for cards
    income = df[df["type"] == "income"]["amount"].sum()
    expenses = df[df["type"] == "expense"]["amount"].sum()
    balance = income - expenses
    
    # Charts
    graphs = {}
    
    # Expense pie
    expense_df = df[df["type"] == "expense"]
    if not expense_df.empty:
        pie_chart = px.pie(expense_df, names="category", values="amount", title="Expense Distribution")
        graphs['pie'] = json.dumps(pie_chart, cls=plotly.utils.PlotlyJSONEncoder)
    
    # Monthly balance trend
    df['month'] = pd.to_datetime(df['date']).dt.to_period('M')
    monthly_balance = df.groupby('month')['amount'].sum().reset_index()
    monthly_balance['month'] = monthly_balance['month'].astype(str)
    if not monthly_balance.empty:
        line_chart = px.line(monthly_balance, x='month', y='amount', title="Monthly Balance Trend")
        graphs['line'] = json.dumps(line_chart, cls=plotly.utils.PlotlyJSONEncoder)
    
    recent_transactions = transactions[:5]  # For table
    
    return render_template("dashboard.html", 
                         graphJSON_pie=graphs.get('pie'), 
                         graphJSON_line=graphs.get('line'),
                         balance=balance,
                         income=income,
                         expenses=expenses,
                         transactions=recent_transactions)

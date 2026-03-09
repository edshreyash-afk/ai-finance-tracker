import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Tuple, Any

def compute_financial_insights(transactions: List[Dict]) -> Dict[str, Any]:
    """
    Generate comprehensive financial insights from user transactions.
    Expects transactions list with: date, amount, category, type, description
    """
    if not transactions:
        return {
            'insights': ['No transaction data available. Add transactions to see insights.'],
            'trends': {}, 'predictions': {}, 'budget_advice': {'score': 0},
            'summary': {'income': 0, 'expenses': 0, 'balance': 0}
        }
    
    df = pd.DataFrame(transactions)
    df['date'] = pd.to_datetime(df['date'])
    df['amount_abs'] = df['amount'].abs()
    
    # Basic summary
    income = df[df['type'] == 'income']['amount'].sum()
    expenses = df[df['type'] == 'expense']['amount_abs'].sum()
    balance = income - expenses
    
    # Time-based analysis
    df['month'] = df['date'].dt.to_period('M')
    monthly_summary = df.groupby('month').agg({
        'amount': 'sum',
        'amount_abs': 'sum'
    }).round(2)
    
    # Category analysis (your original + enhanced)
    category_expenses = df[df['type'] == 'expense'].groupby('category')['amount_abs'].sum()
    insights = generate_category_insights(category_expenses)
    
    # Trends & Savings Rate
    recent_months = monthly_summary.tail(3)
    savings_rate = ((income - expenses) / income * 100) if income > 0 else 0
    
    trends = {
        'savings_rate': round(savings_rate, 1),
        'savings_change': round((recent_months.iloc[-1]['amount'] - recent_months.iloc[0]['amount']) / abs(recent_months.iloc[0]['amount']) * 100, 1) if len(recent_months) > 1 else 0,
        'top_category': category_expenses.idxmax() if not category_expenses.empty else None,
        'top_category_pct': round(category_expenses.max() / expenses * 100, 1) if not category_expenses.empty and expenses > 0 else 0
    }
    
    # Simple ML-like prediction (moving average)
    if len(monthly_summary) >= 3:
        recent_avg = monthly_summary['amount_abs'].tail(3).mean()
        predictions = {
            'next_month_expenses': round(recent_avg, 0),
            'forecast_accuracy': 'High confidence (3+ months data)'
        }
    else:
        predictions = {'next_month_expenses': 0, 'forecast_accuracy': 'Add more data'}
    
    # Budget health score (0-100)
    score_factors = []
    if savings_rate > 20: score_factors.append(25)
    if trends['top_category_pct'] < 30: score_factors.append(25)
    if len(df) > 10: score_factors.append(25)  # Consistency
    if balance > 0: score_factors.append(25)
    
    budget_score = sum(score_factors)
    
    # Personalized advice
    advice = generate_ai_advice(trends, predictions, budget_score)
    
    # Period summary for table
    period_data = []
    for i, (month, row) in enumerate(monthly_summary.tail(4).iterrows()):
        prev_row = monthly_summary.iloc[i-1] if i > 0 else row
        trend = ((row['amount'] - prev_row['amount']) / abs(prev_row['amount']) * 100)
        period_data.append({
            'label': month.strftime('%b %Y'),
            'income': row.get('income', row['amount'] if row['amount'] > 0 else 0),
            'expenses': row['amount_abs'],
            'net': row['amount'],
            'trend': round(trend, 1)
        })
    
    return {
        'insights': insights,
        'trends': trends,
        'predictions': predictions,
        'budget_advice': {
            'score': budget_score,
            'tips': advice['tips']
        },
        'period_summary': period_data,
        'summary': {
            'income': round(income, 2),
            'expenses': round(expenses, 2),
            'balance': round(balance, 2),
            'record_count': len(df)
        }
    }

def generate_category_insights(expenses: pd.Series) -> List[str]:
    """Enhanced version of your original function"""
    if expenses.empty:
        return ["No expense data for category analysis."]
    
    total = expenses.sum()
    insights = []
    
    for category, amount in expenses.items():
        percentage = (amount / total) * 100
        if percentage > 40:
            insights.append(f"⚠️ High spending: {percentage:.1f}% on {category} (₹{amount:.0f})")
        elif percentage > 25:
            insights.append(f"📊 Watching: {category} at {percentage:.0f}% (₹{amount:.0f})")
    
    if not insights:
        insights.append("✅ Balanced spending across categories")
    
    return insights

def generate_ai_advice(trends: Dict, predictions: Dict, score: int) -> Dict:
    """Generate personalized financial advice"""
    tips = []
    
    if trends.get('top_category_pct', 0) > 35:
        tips.append(f"Set a budget limit for your top category: {trends['top_category']}")
    
    if trends.get('savings_rate', 0) < 15:
        tips.append("Aim to save 20% of income - automate transfers")
    
    if score < 60:
        tips.append("Review subscriptions and daily small expenses")
    
    tips.extend([
        "Track receipts for tax season",
        "Build 3-6 months emergency fund",
        "Review insurance coverage annually"
    ])
    
    title = "Smart Money Tips" if score > 70 else "Action Items"
    
    return {
        'title': title,
        'message': f"Your budget health score is {score}/100. Here's how to improve:",
        'tips': tips[:5]  # Top 5
    }

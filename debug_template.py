from app import create_app
from flask import render_template
from models import db, User, Transaction

app = create_app()

with app.test_request_context('/insights/index'):
    with app.app_context():
        try:
            render_template('insights.html', 
                            trends={}, predictions={}, budget_advice={}, period_summary=[],
                            summary={}, top_category={"name": "test", "amount": 0},
                            trend_graph=None, category_graph=None)
            print("Template rendered successfully!")
        except Exception as e:
            print(f"Error rendering template: {type(e).__name__}: {str(e)}")

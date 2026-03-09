from flask import Flask, render_template
from flask_login import LoginManager, current_user
from config import Config
from models import db, User, Transaction

login_manager = LoginManager()
login_manager.login_view = "auth.login"  # assumes login route is in auth blueprint


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from routes.auth_routes import auth
    from routes.transaction_routes import transaction
    from routes.insights_routes import insights
    from routes.dashboard_routes import dashboard

    app.register_blueprint(auth)
    app.register_blueprint(transaction)
    app.register_blueprint(insights)
    app.register_blueprint(dashboard)

    # Home route
    @app.route("/")
    def home():
        stats = None
        if current_user.is_authenticated:
            transactions = Transaction.query.filter_by(user_id=current_user.id).all()
            income = sum(t.amount for t in transactions if t.type == 'income')
            expenses = sum(t.amount for t in transactions if t.type == 'expense')
            stats = {
                "total_transactions": len(transactions),
                "balance": income - expenses,
                "monthly_income": income, # You can filter this by current month for more accuracy
                "monthly_expenses": expenses
            }
        return render_template("home.html", stats=stats)

    return app


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)

from flask import Blueprint, request, redirect, url_for, render_template, flash, Response
from models import db, Transaction
from flask_login import login_required, current_user
from datetime import datetime
from flask import jsonify
import csv

transaction = Blueprint("transaction", __name__, url_prefix="/transaction")


@transaction.route("/add_transaction", methods=["GET", "POST"])
@login_required
def add_transaction():
    if request.method == "POST":
        amount = float(request.form.get("amount"))
        category = request.form.get("category")
        type_ = request.form.get("type")  # renamed to avoid keyword conflict
        description = request.form.get("description", "")

        new_transaction = Transaction(
            user_id=current_user.id,
            amount=amount,
            category=category,
            description=description,
            type=type_,  # income or expense
            date=datetime.utcnow()
        )

        db.session.add(new_transaction)
        db.session.commit()
        flash("Transaction added successfully!", "success")
        return redirect(url_for("transaction.view_transactions"))

    return render_template("add_transaction.html")


@transaction.route("/transactions")
@login_required
def view_transactions():
    # Fetch all transactions for the logged-in user
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()
    
    # Calculate summary data expected by the template
    income = sum(t.amount for t in transactions if t.type == 'income')
    expenses = sum(t.amount for t in transactions if t.type == 'expense')
    
    summary = {
        "income": income,
        "expenses": expenses,
        "balance": income - expenses
    }
    
    # Extract unique categories for the dropdown filter
    categories = list(set(t.category for t in transactions if t.category))
    
    return render_template("transactions.html", 
                           transactions=transactions, 
                           summary=summary, 
                           categories=categories,
                           per_page=10) # <--- Added per_page here!

@transaction.route("/export_csv")
@login_required
def export_csv():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()

    def generate():
        yield "Amount,Category,Description,Type,Date\n"
        for t in transactions:
            yield f"{t.amount},{t.category},{getattr(t,'description','')},{t.type},{t.date}\n"

    return Response(
        generate(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=transactions.csv"}
    )


@transaction.route("/delete/<int:id>", methods=["DELETE"])
@login_required
def delete_transaction(id):
    trans = Transaction.query.get_or_404(id)
    
    # Security check: Ensure the user owns this transaction
    if trans.user_id != current_user.id:
        return jsonify({"success": False, "message": "Unauthorized"}), 403
        
    db.session.delete(trans)
    db.session.commit()
    return jsonify({"success": True, "message": "Transaction deleted"})

@transaction.route("/edit/<int:id>", methods=["POST"])
@login_required
def edit_transaction(id):
    trans = Transaction.query.get_or_404(id)
    
    if trans.user_id != current_user.id:
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    # Update fields
    trans.amount = float(request.form.get("amount"))
    trans.category = request.form.get("category")
    trans.type = request.form.get("type")
    trans.description = request.form.get("description", "")
    
    # Handle date parsing
    date_str = request.form.get("date")
    if date_str:
        trans.date = datetime.strptime(date_str, '%Y-%m-%d').date()

    db.session.commit()
    flash("Transaction updated successfully!", "success")
    return redirect(url_for("transaction.view_transactions"))

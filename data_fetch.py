from app import db
from models import User, Expense, Earning, Goal, Transaction

def get_user_data(username):
    user = User.query.filter_by(username=username).first()
    return user

def get_expenses(user_id):
    return Expense.query.filter_by(user_id=user_id).all()

def get_earnings(user_id):
    return Earning.query.filter_by(user_id=user_id).all()

def get_goals(user_id):
    return Goal.query.filter_by(user_id=user_id).all()

def get_transactions(user_id):
    return Transaction.query.filter_by(user_id=user_id).all()

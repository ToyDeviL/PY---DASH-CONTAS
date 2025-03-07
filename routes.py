from flask import render_template, redirect, url_for, request, session, flash
from app import app, db
from models import User, Expense, Earning, Goal, Transaction

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/data')
def data():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    user = User.query.get(user_id)
    expenses = Expense.query.filter_by(user_id=user_id).all()
    earnings = Earning.query.filter_by(user_id=user_id).all()
    goals = Goal.query.filter_by(user_id=user_id).all()
    transactions = Transaction.query.filter_by(user_id=user_id).all()
    return render_template('data.html', user=user, expenses=expenses, earnings=earnings, goals=goals, transactions=transactions)

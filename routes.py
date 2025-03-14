from flask import render_template, redirect, url_for, request, session, flash, jsonify
from app import app, db, fetch_data
from models import User, Expense, Earning, Goal, Transaction
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import pandas as pd

# Home/Dashboard route
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    
    # Get most recent transactions first
    transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.date.desc()).limit(10).all()
    
    # Calculate total earnings and expenses
    total_earnings = db.session.query(db.func.sum(Earning.amount)).filter_by(user_id=user_id).scalar() or 0
    total_expenses = db.session.query(db.func.sum(Expense.amount)).filter_by(user_id=user_id).scalar() or 0
    
    # Get goals with progress calculation
    goals = Goal.query.filter_by(user_id=user_id).all()
    for goal in goals:
        goal.progress = (goal.current_amount / goal.target_amount) * 100 if goal.target_amount > 0 else 0
    
    # Get upcoming payments (expenses with future dates)
    today = date.today()
    upcoming_payments = Expense.query.filter(Expense.user_id == user_id, Expense.date >= today).order_by(Expense.date).limit(5).all()
    
    return render_template(
        'dashboard.html', 
        user=user, 
        transactions=transactions,
        total_earnings=total_earnings,
        total_expenses=total_expenses,
        goals=goals,
        upcoming_payments=upcoming_payments
    )

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

# API endpoints for chart data
@app.route('/api/earnings-expenses')
def earnings_expenses_data():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
        
    user_id = session.get('user_id')
    
    # Get monthly earnings
    monthly_earnings = db.session.query(
        db.func.date_trunc('month', Earning.date).label('month'),
        db.func.sum(Earning.amount).label('earnings')
    ).filter_by(user_id=user_id).group_by('month').all()
    
    # Get monthly expenses
    monthly_expenses = db.session.query(
        db.func.date_trunc('month', Expense.date).label('month'),
        db.func.sum(Expense.amount).label('expenses')
    ).filter_by(user_id=user_id).group_by('month').all()
    
    # Combine data
    result = {}
    for month, earnings in monthly_earnings:
        month_str = month.strftime('%Y-%m')
        if month_str not in result:
            result[month_str] = {'month': month_str, 'earnings': 0, 'expenses': 0}
        result[month_str]['earnings'] = float(earnings)
    
    for month, expenses in monthly_expenses:
        month_str = month.strftime('%Y-%m')
        if month_str not in result:
            result[month_str] = {'month': month_str, 'earnings': 0, 'expenses': 0}
        result[month_str]['expenses'] = float(expenses)
    
    return jsonify(list(result.values()))

@app.route('/api/expenses-distribution')
def expenses_distribution_data():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
        
    user_id = session.get('user_id')
    
    # Get expense distribution by category
    category_expenses = db.session.query(
        Expense.category,
        db.func.sum(Expense.amount).label('amount')
    ).filter_by(user_id=user_id).group_by(Expense.category).all()
    
    result = [{'category': category, 'amount': float(amount)} for category, amount in category_expenses]
    
    return jsonify(result)

# Add expense route
@app.route('/add-expense', methods=['GET', 'POST'])
def add_expense():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        description = request.form['description']
        amount = float(request.form['amount'])
        expense_date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        category = request.form['category']
        
        # Create new expense record
        expense = Expense(
            user_id=session['user_id'],
            description=description,
            amount=amount,
            date=expense_date,
            category=category
        )
        
        # Also add to transactions (negative amount for expenses)
        transaction = Transaction(
            user_id=session['user_id'],
            description=description,
            amount=-amount,  # Negative amount for expenses
            date=expense_date,
            category=category
        )
        
        db.session.add(expense)
        db.session.add(transaction)
        db.session.commit()
        
        flash('Expense added successfully')
        return redirect(url_for('index'))
        
    return render_template('add_expense.html')

# Add earning route
@app.route('/add-earning', methods=['GET', 'POST'])
def add_earning():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        description = request.form['description']
        amount = float(request.form['amount'])
        earning_date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        category = request.form['category']
        
        # Create new earning record
        earning = Earning(
            user_id=session['user_id'],
            description=description,
            amount=amount,
            date=earning_date,
            category=category
        )
        
        # Also add to transactions (positive amount for earnings)
        transaction = Transaction(
            user_id=session['user_id'],
            description=description,
            amount=amount,  # Positive amount for earnings
            date=earning_date,
            category=category
        )
        
        db.session.add(earning)
        db.session.add(transaction)
        db.session.commit()
        
        flash('Earning added successfully')
        return redirect(url_for('index'))
        
    return render_template('add_earning.html')

# Add goal route
@app.route('/add-goal', methods=['GET', 'POST'])
def add_goal():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        description = request.form['description']
        target_amount = float(request.form['target_amount'])
        current_amount = float(request.form['current_amount'])
        deadline = datetime.strptime(request.form['deadline'], '%Y-%m-%d').date()
        
        # Create new goal
        goal = Goal(
            user_id=session['user_id'],
            description=description,
            target_amount=target_amount,
            current_amount=current_amount,
            deadline=deadline
        )
        
        db.session.add(goal)
        db.session.commit()
        
        flash('Goal added successfully')
        return redirect(url_for('index'))
        
    return render_template('add_goal.html')

# Update goal amount
@app.route('/update-goal/<int:goal_id>', methods=['POST'])
def update_goal(goal_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    goal = Goal.query.get_or_404(goal_id)
    
    # Check if the goal belongs to the logged-in user
    if goal.user_id != session['user_id']:
        flash('Unauthorized access')
        return redirect(url_for('index'))
        
    # Update current amount
    new_amount = float(request.form['current_amount'])
    goal.current_amount = new_amount
    
    db.session.commit()
    flash('Goal updated successfully')
    
    return redirect(url_for('index'))

from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import psycopg2
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object('config.Config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Import models after initializing db
from models import User, Expense, Earning, Goal, Transaction

# Import routes after initializing db and models to avoid circular import
import routes

# Database connection using environment variables or config
def get_db_connection():
    return psycopg2.connect(
        dbname=app.config['DB_NAME'],
        user=app.config['DB_USER'],
        password=app.config['DB_PASSWORD'],
        host=app.config['DB_HOST']
    )

def fetch_data(query, params=None):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            if params:
                cur.execute(query, params)
            else:
                cur.execute(query)
            data = cur.fetchall()
            colnames = [desc[0] for desc in cur.description]
            return pd.DataFrame(data, columns=colnames)

# Dash app initialization
dash_app = dash.Dash(__name__, server=app, url_base_pathname='/dashboard/')
dash_app.layout = html.Div([
    html.H1("Interactive Dashboard", className="text-white text-xl mb-4"),
    dcc.Graph(id='earnings-vs-expenses'),
    dcc.Graph(id='expenses-distribution'),
])

@dash_app.callback(
    Output('earnings-vs-expenses', 'figure'),
    Input('earnings-vs-expenses', 'id')
)
def update_earnings_vs_expenses(_):
    try:
        # Get user_id from session for filtering data
        user_id = session.get('user_id')
        if not user_id:
            # Return empty figure if not logged in
            return px.line(title='Please log in to view your data')
        
        # Get data specific to the logged-in user
        query = """
        SELECT date, SUM(amount) as earnings, 0 as expenses 
        FROM earning WHERE user_id = %s 
        GROUP BY date
        UNION ALL
        SELECT date, 0 as earnings, SUM(amount) as expenses 
        FROM expense WHERE user_id = %s 
        GROUP BY date
        ORDER BY date
        """
        data = fetch_data(query, (user_id, user_id))
        
        # Group by date and sum values
        earnings_expenses_df = data.groupby('date').sum().reset_index()
        
        fig = px.line(earnings_expenses_df, x='date', y=['earnings', 'expenses'], 
                    title='Earnings vs Expenses')
        return fig
    except Exception as e:
        print(f"Error in earnings-vs-expenses: {e}")
        return px.line(title=f'Error loading data: {str(e)}')

@dash_app.callback(
    Output('expenses-distribution', 'figure'),
    Input('expenses-distribution', 'id')
)
def update_expenses_distribution(_):
    try:
        # Get user_id from session for filtering data
        user_id = session.get('user_id')
        if not user_id:
            # Return empty figure if not logged in
            return px.pie(title='Please log in to view your data')
        
        # Get expense data for the logged-in user
        query = """
        SELECT category, SUM(amount) as amount 
        FROM transaction 
        WHERE user_id = %s AND amount < 0
        GROUP BY category
        """
        expenses_distribution_df = fetch_data(query, (user_id,))
        
        # Make sure amounts are positive for the pie chart
        expenses_distribution_df['amount'] = expenses_distribution_df['amount'].abs()
        
        fig = px.pie(expenses_distribution_df, names='category', values='amount', 
                    title='Expenses Distribution')
        return fig
    except Exception as e:
        print(f"Error in expenses-distribution: {e}")
        return px.pie(title=f'Error loading data: {str(e)}')

if __name__ == '__main__':
    # Use 0.0.0.0 to make it available on all network interfaces
    app.run(host='0.0.0.0', port=5000, debug=True)

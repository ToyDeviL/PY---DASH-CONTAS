from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import psycopg2

app = Flask(__name__)
app.config.from_object('config.Config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Import routes after initializing db to avoid circular import
import routes

# Dash app initialization
dash_app = dash.Dash(__name__, server=app, url_base_pathname='/dashboard/')
dash_app.layout = html.Div([
    html.H1("Interactive Dashboard"),
    dcc.Graph(id='earnings-vs-expenses'),
    dcc.Graph(id='expenses-distribution'),
])

# Database connection
conn = psycopg2.connect(
    dbname="contas",
    user="andrino",
    password="Rebecca@2023",
    host="localhost"
)

def fetch_data(query):
    with conn.cursor() as cur:
        cur.execute(query)
        data = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        return pd.DataFrame(data, columns=colnames)

earnings_expenses_df = fetch_data("SELECT date, earnings, expenses FROM earnings_expenses")
expenses_distribution_df = fetch_data("SELECT category, amount FROM expenses_distribution")

@dash_app.callback(
    Output('earnings-vs-expenses', 'figure'),
    Input('earnings-vs-expenses', 'id')
)
def update_earnings_vs_expenses(_):
    fig = px.line(earnings_expenses_df, x='date', y=['earnings', 'expenses'], 
                  title='Earnings vs Expenses')
    return fig

@dash_app.callback(
    Output('expenses-distribution', 'figure'),
    Input('expenses-distribution', 'id')
)
def update_expenses_distribution(_):
    fig = px.pie(expenses_distribution_df, names='category', values='amount', 
                 title='Expenses Distribution')
    return fig

if __name__ == '__main__':
    app.run(host='192.168.100.100', port=5000, debug=True)

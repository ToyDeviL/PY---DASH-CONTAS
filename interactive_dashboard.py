import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import psycopg2

# Database connection
conn = psycopg2.connect(
    dbname="contas",
    user="andrino",
    password="Rebecca@2023",
    host="localhost"
)

# Fetch data from PostgreSQL
def fetch_data(query):
    with conn.cursor() as cur:
        cur.execute(query)
        data = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        return pd.DataFrame(data, columns=colnames)

# Fetch earnings and expenses data
earnings_expenses_df = fetch_data("SELECT date, earnings, expenses FROM earnings_expenses")
expenses_distribution_df = fetch_data("SELECT category, amount FROM expenses_distribution")

# Initialize the Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Interactive Dashboard"),
    dcc.Graph(id='earnings-vs-expenses'),
    dcc.Graph(id='expenses-distribution'),
])

@app.callback(
    Output('earnings-vs-expenses', 'figure'),
    Input('earnings-vs-expenses', 'id')
)
def update_earnings_vs_expenses(_):
    fig = px.line(earnings_expenses_df, x='date', y=['earnings', 'expenses'], 
                  title='Earnings vs Expenses')
    return fig

@app.callback(
    Output('expenses-distribution', 'figure'),
    Input('expenses-distribution', 'id')
)
def update_expenses_distribution(_):
    fig = px.pie(expenses_distribution_df, names='category', values='amount', 
                 title='Expenses Distribution')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)

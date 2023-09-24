# Import packages
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px

# Initialize the app
app = Dash(__name__)

# App layout
app.layout = html.Div([
    html.H1(children='Dingo Discs Analytics'),
    dcc.Interval(id='timer', interval=1000, n_intervals=0),
    html.Div(id='graphs', children=
        html.H3('Loading Data...')
    )
])

@callback(Output('graphs', 'children'), Input('timer', 'n_intervals'))
def update_graphs(n):
    window_size = 100
    i = n*10
    df = pd.read_csv('../data/sample_data.csv', delimiter=',', names=['time','ax','ay','az','gx','gy','gz','rx','ry','rz'])
    df = df[i:i+window_size]
    return [
        dcc.Graph(id='acc-graph', figure=px.line(df, x='time', y=['ax','ay', 'az'])),
        dcc.Graph(id='gyro-graph', figure=px.line(df, x='time', y=['gx', 'gy', 'gz'])),
        dcc.Graph(id='ang-graph', figure=px.line(df, x='time', y=['rx', 'ry', 'rz']))
    ]

# Run the app
if __name__ == '__main__':
    app.run(debug=True)

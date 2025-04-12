    import dash
from dash import html, dcc, Input, Output
import plotly.express as px
import requests
import pandas as pd
from datetime import datetime, timedelta
import io
import dash_bootstrap_components as dbc

# ---------------------------
# Config
# ---------------------------
API_URL = "https://shiny-deana-mohammednasr-4c86290b.koyeb.app/sensor_data/1"

# ---------------------------
# App Initialization
# ---------------------------
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.title = "Lake Depth Dashboard"

# ---------------------------
# Helper Functions
# ---------------------------
def fetch_data():
    response = requests.get(API_URL)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df
    return pd.DataFrame()

def filter_data(df, range_value):
    now = datetime.utcnow()
    if range_value == "day":
        since = now - timedelta(days=1)
    elif range_value == "week":
        since = now - timedelta(weeks=1)
    else:
        since = now - timedelta(days=30)
    return df[df["timestamp"] >= since]

# ---------------------------
# Layout
# ---------------------------
app.layout = dbc.Container([
    html.H1("Lake Water Depth Monitoring", className="my-3 text-center text-primary"),

    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id="time-range",
                options=[
                    {"label": "Last Day", "value": "day"},
                    {"label": "Last Week", "value": "week"},
                    {"label": "Last Month", "value": "month"},
                ],
                value="week",
                clearable=False,
                className="mb-3"
            )
        ], width=4),
        dbc.Col([
            html.Button("Download Report", id="download-btn", className="btn btn-success mb-3"),
            dcc.Download(id="download")
        ], width=4),
    ], justify="center"),

    dcc.Graph(id="depth-graph"),

    dbc.Row([
        dbc.Col(html.Div(id="max-depth", className="alert alert-info")),
        dbc.Col(html.Div(id="min-depth", className="alert alert-warning"))
    ], className="my-3")

], fluid=True)

# ---------------------------
# Callbacks
# ---------------------------
@app.callback(
    [Output("depth-graph", "figure"),
     Output("max-depth", "children"),
     Output("min-depth", "children")],
    Input("time-range", "value")
)
def update_graph(range_value):
    df = fetch_data()
    if df.empty:
        return px.line(), "No data", "No data"

    df_filtered = filter_data(df, range_value)

    fig = px.line(df_filtered, x="timestamp", y="depth", title="Water Depth Over Time")
    fig.update_layout(xaxis_title="Time", yaxis_title="Depth (cm)")

    max_depth = df_filtered["depth"].max()
    min_depth = df_filtered["depth"].min()

    return fig, f"🔼 Max Depth: {max_depth} cm", f"🔽 Min Depth: {min_depth} cm"


@app.callback(
    Output("download", "data"),
    Input("download-btn", "n_clicks"),
    Input("time-range", "value"),
    prevent_initial_call=True
)
def download_csv(n_clicks, range_value):
    df = fetch_data()
    df_filtered = filter_data(df, range_value)
    return dcc.send_data_frame(df_filtered.to_csv, "lake_depth_report.csv")

# ---------------------------
# Run
# ---------------------------
if __name__ == '__main__':
    app.run_server(debug=True)

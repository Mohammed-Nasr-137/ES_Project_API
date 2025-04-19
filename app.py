import dash
from dash import html, dcc, Input, Output, State
import plotly.express as px
import requests
import pandas as pd
from datetime import datetime, timedelta
import io
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import dash_daq as daq

# ---------------------------
# App Initialization
# ---------------------------
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    requests_pathname_prefix="/dashboard/"
)
app.title = "Lake Depth Dashboard"

# ---------------------------
# Helper Functions
# ---------------------------
def fetch_data(sensor_id):
    url = f"https://shiny-deana-mohammednasr-4c86290b.koyeb.app/sensor_data/{sensor_id}"
    response = requests.get(url)
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
            html.Label("Select Sensor:", className="text-light"),
            dcc.Dropdown(
                id="sensor-selector",
                options=[
                    {"label": "Sensor 1", "value": 1},
                    {"label": "Sensor 2", "value": 2},
                ],
                value=1,
                clearable=False,
                className="mb-3",
                style={"color": "black"}
            ),
            html.Label("Select Time Range:", className="text-light"),
            dcc.Dropdown(
                id="time-range",
                options=[
                    {"label": "Last Day", "value": "day"},
                    {"label": "Last Week", "value": "week"},
                    {"label": "Last Month", "value": "month"},
                ],
                value="week",
                clearable=False,
                className="mb-3",
                style={"color": "black"}
            )
        ], width=4),
        dbc.Col([
            html.Button("Download Report", id="download-btn", className="btn btn-success mb-3"),
            dcc.Download(id="download"),
            html.Div(id="alert-maxlevel", className="text-danger fw-bold"),
            html.Div(id="alert-rain", className="text-info fw-bold")
        ], width=6),
    ], justify="center"),

    dcc.Interval(id="interval-update", interval=5000, n_intervals=0),

    dcc.Graph(id="depth-graph"),

    dbc.Row([
        dbc.Col(html.Div(id="max-depth", className="alert alert-info")),
        dbc.Col(html.Div(id="min-depth", className="alert alert-warning")),
        dbc.Col(daq.Gauge(
            id='battery-gauge',
            label='Battery %',
            min=0,
            max=100,
            value=0,
            color="#00cc96",
            showCurrentValue=True,
        ))
    ], className="my-3")

], fluid=True)

# ---------------------------
# Callbacks
# ---------------------------
@app.callback(
    [Output("depth-graph", "figure"),
     Output("max-depth", "children"),
     Output("min-depth", "children"),
     Output("battery-gauge", "value"),
     Output("alert-maxlevel", "children"),
     Output("alert-rain", "children")],
    [Input("time-range", "value"),
     Input("sensor-selector", "value"),
     Input("interval-update", "n_intervals")]
)
def update_graph(range_value, sensor_id, n):
    df = fetch_data(sensor_id)
    if df.empty:
        raise PreventUpdate

    df_filtered = filter_data(df, range_value)

    fig = px.line(df_filtered, x="timestamp", y="depth", title="Water Depth Over Time")
    fig.update_traces(mode="lines+markers")
    fig.update_layout(xaxis_title="Time", yaxis_title="Depth (cm)")

    max_depth = df_filtered["depth"].max()
    min_depth = df_filtered["depth"].min()

    latest_row = df_filtered.iloc[-1]

    battery = latest_row["battery"] if pd.notna(latest_row["battery"]) else 0
    maxlevel_alert = "⚠️ Lake above max level!" if latest_row.get("max_level") else ""
    rain_alert = "🌧️ It’s currently raining at this point!" if latest_row.get("rain") else ""

    return fig, f"🔼 Max Depth: {max_depth} cm", f"🔽 Min Depth: {min_depth} cm", battery, maxlevel_alert, rain_alert


@app.callback(
    Output("download", "data"),
    Input("download-btn", "n_clicks"),
    State("time-range", "value"),
    State("sensor-selector", "value"),
    prevent_initial_call=True
)
def download_csv(n_clicks, range_value, sensor_id):
    df = fetch_data(sensor_id)
    df_filtered = filter_data(df, range_value)
    df_filtered["Max Depth"] = df_filtered["depth"].max()
    df_filtered["Min Depth"] = df_filtered["depth"].min()
    df_filtered["Battery"] = df_filtered["battery"].fillna("Unknown")
    df_filtered["Rain Alert"] = df_filtered["rain"].apply(lambda x: "Yes" if x else "No")
    df_filtered["Max Level Alert"] = df_filtered["max_level"].apply(lambda x: "Yes" if x else "No")
    return dcc.send_data_frame(df_filtered.to_csv, "lake_depth_report.csv")

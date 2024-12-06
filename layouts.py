from dash import dcc, html
import dash_bootstrap_components as dbc

layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.H1(
                    "Get the Route Profile, Map, and Estimated Time",
                    style={"color": "white"},
                    className="text-center mt-4 mb-4"
                ),
                width=12
            )
        ),
        # Row 1: Bike and Rider Mass
        dbc.Row([
            dbc.Col([
                html.Label("Enter your FTP (Functional Threshold Power):", style={"color": "white"}),
                dbc.Input(id="ftp-input", type="number", value=240, min=0, placeholder="Enter FTP (e.g., 250 W)", className="mb-3"),
            ], width=6, className="px-5"),
            dbc.Col([
                dbc.Label("Bike Mass (kg):", style={"color": "white"}),
                dcc.Input(
                    id="bike-mass", type="number", value=11, min=0, step=0.1,
                    style={"width": "100%", "fontSize": "16px", "padding": "5px"}
                ),
            ], width=3),
            dbc.Col([
                dbc.Label("Rider Mass (kg):", style={"color": "white"}),
                dcc.Input(
                    id="rider-mass", type="number", value=88, min=0, step=0.1,
                    style={"width": "100%", "fontSize": "16px", "padding": "5px"}
                ),
            ], width=3),
        ], className="px-5"),  # Add spacing between rows

        # Row 2: Rolling Resistance Coefficient, Drag Coefficient and Frontal Area
        dbc.Row([
            dbc.Col([
                dbc.Label("Rolling Resistance Coefficient (C_r):", style={"color": "white"}),
                dcc.Input(
                    id="rolling-coeff", type="number", value=0.0036, min=0, step=0.0001,
                    style={"width": "100%", "fontSize": "16px", "padding": "5px"}
                ),
            ], width=3),
            dbc.Col([
                dbc.Label("Drag Coefficient (C_d):", style={"color": "white"}),
                dcc.Input(
                    id="drag-coeff", type="number", value=0.55, min=0, step=0.01,
                    style={"width": "100%", "fontSize": "16px", "padding": "5px"}
                ),
            ], width=3),
            dbc.Col([
                dbc.Label("Frontal Area (A, m²):", style={"color": "white"}),
                dcc.Input(
                    id="frontal-area", type="number", value=0.6, min=0, step=0.01,
                    style={"width": "100%", "fontSize": "16px", "padding": "5px"}
                ),
            ], width=3),
            dbc.Col([
                dbc.Label("Air Density (kg/m³):", style={"color": "white"}),
                dcc.Input(
                    id="air-density", type="number", value=1.225, min=0, step=0.001,
                    style={"width": "100%", "fontSize": "16px", "padding": "5px"}
                ),
            ], width=3),
        ], className="px-5"),
        # Strategy Selector and Upload GPX File
        dbc.Row([
            dbc.Col([
                html.Label("Select a Riding Strategy:", style={"color": "white", "padding": "5px", "margin-top": "15px"}),
                dbc.RadioItems(
                    id="strategy-selector",
                    options=[
                        {"label": "Recovery Ride (Zone 1)", "value": "zone1"},
                        {"label": "Endurance Ride (Zone 2)", "value": "zone2"},
                        {"label": "Tempo Ride (Zone 3)", "value": "zone3"},
                        {"label": "Push Hard Ride", "value": "push_hard"},
                    ],
                    style={"color": "white", "width": "100%", "fontSize": "16px", "padding": "5px"},
                    value="zone1",  # Default selection
                    inline=True,
                    className="mb-3"
                )
            ], width=12, className="px-5"),
        ]),
        dbc.Row(
            dbc.Col(
                dcc.Upload(
                    id='upload-gpx',
                    children=dbc.Button(
                        "Upload GPX File",
                        color="primary",
                        outline=True,
                        size="lg",
                        className="mt-2 custom-btn"
                    ),
                    style={
                        'width': '100%',
                        'textAlign': 'center',
                        'margin': 'auto'
                    },
                    multiple=False,
                    accept=".gpx"
                ),
                width={"size": 6, "offset": 3}
            )
        ),
        
        dbc.Row(
            dbc.Col(
                dcc.Loading(
                            id="loading",
                            type="dot",  # Choose spinner type: "circle", "dot", or "default"
                            style={"marginTop": "30px"},
                            children=dbc.Container(id="output-data-upload", fluid=True),
                        ),
                width=12
            )
        )
    ],
    fluid=True,
    className="p-4",
    style={
        "marginBottom": "30px",
        "padding": "20px",
        "backgroundColor": "#333",
        "borderRadius": "10px",
        "boxShadow": "0px 4px 8px rgba(0, 0, 0, 0.2)"
    }
)
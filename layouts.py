from dash import dcc, html
import dash_bootstrap_components as dbc

layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.H1(
                    "Route Profile, Map, And Estimated Time",
                    className="text-center mt-4 mb-4"
                ),
                width=12
            )
        ),
        # FTP and Strategy Selector
        dbc.Row([
            dbc.Col([
                html.Label("Select a Riding Strategy:"),
                dbc.RadioItems(
                    id="strategy-selector",
                    options=[
                        {"label": "Recovery Ride (Zone 1)", "value": "zone1"},
                        {"label": "Endurance Ride (Zone 2)", "value": "zone2"},
                        {"label": "Tempo Ride (Zone 3)", "value": "zone3"},
                        {"label": "Push Hard Ride", "value": "push_hard"},
                    ],
                    value="zone1",  # Default selection
                    inline=False,
                    className="mb-3"
                )
            ], width=6, className="px-5"),
            dbc.Col([
                html.Label("Enter your FTP (Functional Threshold Power):"),
                dbc.Input(id="ftp-input", type="number", placeholder="Enter FTP (e.g., 250 W)", className="mb-3"),
            ], width=6, className="px-5")
        ]),
        dbc.Row(
            dbc.Col(
                dcc.Upload(
                    id='upload-gpx',
                    children=dbc.Button(
                        "Upload GPX File",
                        color="primary",
                        outline=True,
                        className="mt-2"
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
    className="p-4"
)
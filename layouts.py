from dash import dcc, html
import dash_bootstrap_components as dbc

layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.H1(
                    "GPX File Upload and Visualization",
                    className="text-center mt-4 mb-4"
                ),
                width=12
            )
        ),
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
                html.Div(
                    id='output-data-upload',
                    className="mt-4"
                ),
                width=12
            )
        )
    ],
    fluid=True,
    className="p-4"
)
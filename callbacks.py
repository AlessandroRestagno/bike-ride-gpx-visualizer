from dash import html, Input, Output, State, dcc
from data_processing import parse_gpx, build_dataframe
import dash_bootstrap_components as dbc
from data_processing import visualize_data, visualize_map, update_speed_pacing

# Callback to handle file upload and display data

strategy_desc = {
            "zone1": "Recovery Ride (Zone 1)",
            "zone2": "Endurance Ride (Zone 2)",
            "zone3": "Tempo Ride (Zone 3)",
            "push_hard": "Push Hard Ride"
        }

def register_callbacks(app):
    @app.callback(
        Output('output-data-upload', 'children'),
        [
            Input('upload-gpx', 'contents'),
            Input("ftp-input", "value"),
            Input("strategy-selector", "value"),
        ],
        [State('upload-gpx', 'filename')]
    )
    def parse_and_display_gpx(contents,ftp,strategy,filename):
        if ftp is None or strategy is None:
            return html.Div(
                "Please provide FTP and select a strategy.",
                className="text-center mt-4"
                )
        
        if contents is not None:
            try:
                # Step 1: Parse the GPX file
                points = parse_gpx(contents)

                # Step 2: Build the DataFrame
                data = build_dataframe(points)
                fig_profile = visualize_data(data)
                fig_map = visualize_map(data)
                estimated_time = update_speed_pacing(data)

                # Step 3: Visualize the data
                return html.Div(
                    [
                        html.H2(
                            f"The {strategy_desc[strategy]} will take approximately {estimated_time} to complete the ride.",
                            style={"textAlign": "center", "marginTop": "15px"},
                        ),
                        dbc.Row(
                            dbc.Col(dcc.Graph(figure=fig_profile), width=12),  # Full width for all data graph
                        ),
                        html.H4(
                            f"Map",
                            style={"textAlign": "center", "marginTop": "15px"},
                        ),
                        dbc.Row(
                            dbc.Col(html.Div(html.Iframe(srcDoc=fig_map,height="500px",width="100%")), width=12),  # Full width for all data graph
                        ),
                    ]
                )

            except ValueError as e:
                return f"An error occurred: {str(e)}"

        # Default message if no file is uploaded
        return html.Div(
            "Upload a GPX file to see its data.",
            className="text-center mt-4"
        )

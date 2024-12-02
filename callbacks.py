from dash import html, Input, Output, State, dcc
from data_processing import parse_gpx, build_dataframe
import dash_bootstrap_components as dbc
from data_processing import visualize_data, visualize_map

# Callback to handle file upload and display data
def register_callbacks(app):
    @app.callback(
        Output('output-data-upload', 'children'),
        [Input('upload-gpx', 'contents')],
        [State('upload-gpx', 'filename')]
    )
    def parse_and_display_gpx(contents, filename):
        if contents is not None:
            try:
                # Step 1: Parse the GPX file
                points = parse_gpx(contents)

                # Step 2: Build the DataFrame
                data = build_dataframe(points)
                fig_profile = visualize_data(data)
                fig_map = visualize_map(data)

                # Step 3: Visualize the data
                return html.Div(
                    [
                        html.H4(
                            f"File '{filename}' uploaded successfully.",
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
                #return visualize_data(data)

            except ValueError as e:
                return f"An error occurred: {str(e)}"

        # Default message if no file is uploaded
        return html.Div(
            "Upload a GPX file to see its data.",
            className="text-center mt-4"
        )

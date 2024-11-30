from dash import html, Input, Output, State
from data_processing import parse_gpx, build_dataframe, visualize_data

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

                # Step 3: Visualize the data
                return visualize_data(data)

            except ValueError as e:
                return f"An error occurred: {str(e)}"

        # Default message if no file is uploaded
        return html.Div(
            "Upload a GPX file to see its data.",
            className="text-center mt-4"
        )

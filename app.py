import dash
from dash import dcc, html, Input, Output, State, callback_context, dash_table
import pandas as pd
import io
import base64
from data_processing import extract_gpx_data, calculate_final_data


# Initialize the Dash app
app = dash.Dash(__name__)

# Define the app layout
app.layout = html.Div([
    html.H1("GPX File Upload and Visualization"),
    dcc.Upload(
        id='upload-gpx',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select a GPX File')
        ]),
        style={
            'width': '50%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px auto'
        },
        multiple=False,
        accept=".gpx"
    ),
    html.Div(id='output-data-upload', style={'padding': '10px'}),
])

@app.callback(
    Output('output-data-upload', 'children'),
    [Input('upload-gpx', 'contents')],
    [State('upload-gpx', 'filename')]
)
def parse_and_display_gpx(contents, filename):
    if contents is not None:
        # Decode the uploaded GPX file
        content_type, content_string = contents.split(',')
        decoded = io.StringIO(io.BytesIO(base64.b64decode(content_string)).read().decode('utf-8'))

        # Parse the GPX data
        try:
            points = extract_gpx_data(decoded)
            latitudes, longitudes, gradients, distances, elevations = calculate_final_data(points)

            # Create a DataFrame
            data = pd.DataFrame({
                'Latitude': latitudes,
                'Longitude': longitudes,
                'Gradient (%)': gradients,
                'Distance (m)': distances,
                'Elevation (m)': elevations
            })
            data['Cumulative Distance (m)'] = data['Distance (m)'].cumsum()

            # Display the first few rows in a Dash DataTable
            return dash_table.DataTable(
                data=data.head(10).to_dict('records'),
                columns=[{"name": i, "id": i} for i in data.columns],
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'center',
                    'padding': '5px',
                },
                style_header={
                    'backgroundColor': 'lightgrey',
                    'fontWeight': 'bold'
                }
            )
        except Exception as e:
            return html.Div(f"An error occurred while parsing the GPX file: {str(e)}")

    return html.Div("Upload a GPX file to see its data.")

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)

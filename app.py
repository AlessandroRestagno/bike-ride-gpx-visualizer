import dash
import dash_bootstrap_components as dbc
from layouts import layout
from callbacks import register_callbacks

# Initialize Dash app with Bootstrap theme
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    title="GPX File Visualizer"
    )

# Define the app layout
app.layout = layout

# Register callbacks
register_callbacks(app)

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)

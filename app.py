from dash import Dash, html, dcc, Input, Output
from template.template import layout, register_callbacks
from entities import entities
from flask import Flask
from flask_talisman import Talisman

server = Flask(__name__)

app = Dash(__name__, server=server, suppress_callback_exceptions=True)

app.layout = html.Div(
    children=[
        dcc.Location(id='url'),
        html.Div(id='page-content', className="graph-mobilecontainer")
    ],
    style={"margin": "0px", "padding": "0px", "backgroundColor": "transparent", "height": "100%"}
)

@app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
def display_page(pathname):
    if pathname in entities:
        entity_id, friendly_name = entities[pathname]
        return layout(entity_id, friendly_name)
    return html.H1("404 - Pagina niet gevonden")

# callbacks registreren
for entity_id, friendly_name in entities.values():
    register_callbacks(app, entity_id, friendly_name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=False)

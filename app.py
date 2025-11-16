from dash import Dash, html, dcc, Input, Output
from template.template import layout, register_callbacks
from entities import entities

#print("entities", entities.keys())

from flask import Flask
#from flask_talisman import Talisman

server = Flask(__name__)
# Talisman(server,force_https=False, content_security_policy={
#     'default-src': "'self' 'unsafe-inline' 'unsafe-eval' data:",
#     'script-src': "'self' 'unsafe-inline' 'unsafe-eval'",
#     'style-src': "'self' 'unsafe-inline'",
#     'frame-ancestors': "http://192.168.22.208:8010 http://192.168.22.201:8123"
# })

app = Dash(__name__, server=server, suppress_callback_exceptions=True)

app.layout = html.Div([
    dcc.Location(id='url'),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
def display_page(pathname):
    # strip leading slash zodat /grafiek-woonkamer matcht met "grafiek-woonkamer"
    #pathname = pathname.lstrip("/")
    if pathname in entities:
        entity_id, friendly_name = entities[pathname]
        return layout(entity_id, friendly_name)
    return html.H1("404 - Pagina niet gevonden")

# callbacks registreren
for entity_id, friendly_name in entities.values():
    register_callbacks(app, entity_id, friendly_name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=False)

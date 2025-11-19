from dash import html, dcc, Input, Output, State
from datetime import datetime, timedelta
import plotly.graph_objs as go
from queries.timescale import fetch_ltts
import pandas as pd
import pytz

def layout(entity_id: str, friendly_name: str):
    prefix = entity_id.replace(".", "_")
    return html.Div([
        html.H3(f"{friendly_name}"),
        dcc.RadioItems(
            id=f'{prefix}-time-range',
            options=[
                {'label': '1h', 'value': '1h'},
                {'label': '2h', 'value': '2h'},
                {'label': '3h', 'value': '3h'},
                {'label': '6h', 'value': '6h'},
                {'label': '12h', 'value': '12h'},
                {'label': '24h', 'value': '24h'},
                {'label': 'Aangepast bereik', 'value': 'custom'},
            ],
            value='12h',
            inline=True,
            className='radio-items'
        ),
        html.Div(
            id=f"{prefix}-date-picker-container",
            className="date-picker-container",
            children=[
                dcc.DatePickerRange(
                    id=f'{prefix}-date-picker',
                    start_date=datetime.utcnow().date() - timedelta(days=1),
                    end_date=datetime.utcnow().date(), className="date-picker",
                    display_format="DD MM YYYY",
                    updatemode="bothdates"
                )
            ],
            style={"display": "none"}
        ),        
        dcc.Graph(id=f'{prefix}-graph', className='dash-graph'),
        dcc.Interval(
        id=f'{prefix}-interval',
        interval=300 * 1000,  
        n_intervals=0
        )
    ], className='graph-container')

def register_callbacks(app, entity_id: str, friendly_name: str):
    prefix = entity_id.replace(".", "_")

    @app.callback(
        Output(f"{prefix}-date-picker-container", "style"),
        Output(f"{prefix}-date-picker-container", "className"),
        Input(f"{prefix}-time-range", "value")
    )
    def toggle_date_picker(range_value):
        if range_value == "custom":
            return {"display": "block"}, "date-picker-container"
        return {"display": "none"}, "date-picker-container"

    @app.callback(
        Output(f"{prefix}-graph", "figure"),
        Input(f"{prefix}-time-range", "value"),
        Input(f"{prefix}-date-picker", "start_date"),
        Input(f"{prefix}-date-picker", "end_date"),
        Input(f"{prefix}-interval", "n_intervals")
    )

    def update_graph(range_value, start_date, end_date, n_intervals):
        now = datetime.utcnow()

        # Bereken start en eindtijd
        if range_value == "custom" and start_date and end_date:
            try:
                start = datetime.fromisoformat(start_date)
                end = datetime.fromisoformat(end_date)
            except Exception:
                start = now - timedelta(hours=1)
                end = now
        else:
            if 'h' in range_value:
                delta = timedelta(hours=int(range_value.replace('h', '')))
            elif 'd' in range_value:
                delta = timedelta(days=int(range_value.replace('d', '')))
            else:
                delta = timedelta(hours=1)
            start = now - delta
            end = now

        # Data ophalen en sorteren
        df = fetch_ltts(entity_id, start, end)
        df = df.sort_values(by='time', ascending=True).copy()
        df['state'] = pd.to_numeric(df['state'], errors='coerce')
        df.dropna(subset=['state'], inplace=True)

        local_tz = pytz.timezone("Europe/Amsterdam")
        df['time'] = pd.to_datetime(df['time'])  # Zorg dat het datetime is
        df['time'] = df['time'].dt.tz_convert('Europe/Amsterdam')

        # Reverse-logica bepalen
        reverse = df.iloc[0]['state'] > df.iloc[-1]['state']
        short_ranges = ['1h', '2h', '3h', '6h', '12h']
        autorange_mode = 'reversed' if range_value in short_ranges and reverse else True

        # Figuur opbouwen
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['time'],
            y=df['state'],
            mode='lines',
            name=entity_id,
            line=dict(color="limegreen")
        ))

        fig.update_layout(
            margin=dict(t=40, b=20),
            height=400,  # ✅ Behoud vaste hoogte maar geen mobiele hacks nodig
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(
                color='white',
                gridcolor='rgba(255,255,255,0.2)'
            ),
            yaxis=dict(
                tickformat='.1f',
                nticks=5,
                color='white',
                gridcolor='rgba(255,255,255,0.2)'
                # ⚠ OUD: range=[df['state'].min(), df['state'].max()], autorange=False
                # ❌ Dit veroorzaakte mobiel fallback probleem
            )
        )

        # ------------------------------
        # Y-as autorange + reverse logica
        # ------------------------------
        if range_value in short_ranges and reverse:
            fig.update_yaxes(autorange="reversed")  # ✅ korte intervallen omgekeerd
        else:
            fig.update_yaxes(autorange=True, rangemode="normal")  # ✅ laat Plotly zelf range bepalen, voorkomt fallback naar 0

        return fig

        # # Layout met correcte y-as richting
        # fig.update_layout(
        #     margin=dict(t=40, b=20),
        #     height=400,
        #     paper_bgcolor='rgba(0,0,0,0)',
        #     plot_bgcolor='rgba(0,0,0,0)',
        #     font=dict(color='white'),
        #     xaxis=dict(
        #         color='white',
        #         gridcolor='rgba(255,255,255,0.2)'
        #     ),
        #      yaxis=dict(
        #         tickformat='.1f',
        #         nticks=5,
        #         range=[df['state'].min(), df['state'].max()],
        #         autorange=False,
        #         color='white',
        #         gridcolor='rgba(255,255,255,0.2)'
        #     )
        # )

        # return fig
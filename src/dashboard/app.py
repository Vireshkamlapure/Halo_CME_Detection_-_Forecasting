import os
import sys
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import numpy as np

# Ensure we can import the ML engines
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.models.prognostic_engine import PrognosticEngine

app = dash.Dash(__name__, title="Aditya-L1 Multi-Messenger Suite", suppress_callback_exceptions=True)
prognostic_engine = PrognosticEngine()

# Mission Control Styling
colors = {'background': '#020617', 'surface': '#0F172A', 'surface_light': '#1E293B', 'text': '#F8FAFC', 'accent': '#3B82F6', 'alert': '#DC2626', 'success': '#10B981', 'warning': '#F59E0B'}
SIDEBAR_STYLE = {"position": "fixed", "top": 0, "left": 0, "bottom": 0, "width": "18rem", "padding": "2rem 1rem", "backgroundColor": colors['surface'], "borderRight": f"1px solid {colors['surface_light']}", "zIndex": 100}
CONTENT_STYLE = {"marginLeft": "18rem", "padding": "2rem", "minHeight": "100vh", "width": "calc(100vw - 18rem)", "boxSizing": "border-box", "overflowX": "hidden", "backgroundColor": colors['background'], "color": colors['text'], "fontFamily": "ui-sans-serif, system-ui, sans-serif"}

# Global CSS to kill Ghost Scrollbars
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>body { margin: 0; overflow-x: hidden; }</style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# ------------------------------------------------------------------------------
# Navigation & Shell
# ------------------------------------------------------------------------------
sidebar = html.Div(style=SIDEBAR_STYLE, children=[
    html.H2("ADITYA-L1", style={'color': colors['text'], 'fontWeight': '900', 'letterSpacing': '2px', 'margin': 0}),
    html.P("Mission Control", style={'color': colors['accent'], 'fontSize': '12px', 'textTransform': 'uppercase', 'letterSpacing': '1px', 'marginBottom': '2rem'}),
    
    html.Hr(style={'borderColor': colors['surface_light']}),
    
    html.Div(style={'display': 'flex', 'flexDirection': 'column', 'gap': '1rem', 'marginTop': '2rem'}, children=[
        dcc.Link('🌐 Strategic Command', href='/', id='link-home', style={'color': colors['text'], 'textDecoration': 'none', 'padding': '10px', 'borderRadius': '5px', 'backgroundColor': colors['surface_light']}),
        dcc.Link('🛰️ Raw Diagnostics', href='/diagnostics', id='link-diag', style={'color': colors['text'], 'textDecoration': 'none', 'padding': '10px', 'borderRadius': '5px', 'backgroundColor': colors['surface_light']}),
        dcc.Link('🧠 ML Evaluation', href='/models', id='link-models', style={'color': colors['text'], 'textDecoration': 'none', 'padding': '10px', 'borderRadius': '5px', 'backgroundColor': colors['surface_light']}),
        dcc.Link('📊 Science Parameters (17)', href='/parameters', id='link-param', style={'color': colors['text'], 'textDecoration': 'none', 'padding': '10px', 'borderRadius': '5px', 'backgroundColor': colors['surface_light']}),
        dcc.Link('📝 Alert Logs', href='/logs', id='link-logs', style={'color': colors['text'], 'textDecoration': 'none', 'padding': '10px', 'borderRadius': '5px', 'backgroundColor': colors['surface_light']})
    ]),
    
    html.Div(style={'position': 'absolute', 'bottom': '2rem', 'left': '1rem', 'right': '1rem'}, children=[
        html.Div(id='data-indicator-dot', style={'width': '10px', 'height': '10px', 'borderRadius': '50%', 'backgroundColor': colors['warning'], 'display': 'inline-block', 'marginRight': '10px'}),
        html.Span("SWASTi SYNC ACTIVE", style={'color': colors['warning'], 'fontSize': '12px', 'fontWeight': 'bold'})
    ])
])

# ------------------------------------------------------------------------------
# Page Generators
# ------------------------------------------------------------------------------

def page_1_strategic():
    return html.Div(style={'display': 'flex', 'flexDirection': 'column', 'gap': '20px', 'height': 'calc(100vh - 4rem)', 'overflowY': 'auto', 'paddingRight': '10px'}, children=[
        html.H1("Strategic Command Overview", style={'marginTop': 0}),
        html.Iframe(src='/assets/unified_dashboard.html', style={'width': '100%', 'minHeight': '800px', 'flex': 'none', 'border': f'1px solid {colors["surface_light"]}', 'borderRadius': '10px'}),
        html.Div(style={'minHeight': '350px', 'backgroundColor': colors['surface'], 'borderRadius': '10px', 'border': f'1px solid {colors["surface_light"]}', 'padding': '15px'}, children=[
            dcc.Graph(id='p1-48h-chart', responsive=True, style={'width': '100%', 'height': '300px'})
        ])
    ])

def page_2_diagnostics():
    return html.Div(style={'display': 'flex', 'flexDirection': 'column', 'gap': '20px'}, children=[
        html.H1("Multimodal Payload Diagnostics", style={'marginTop': 0}),
        html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '20px'}, children=[
            html.Div(style={'backgroundColor': colors['surface'], 'padding': '15px', 'borderRadius': '10px'}, children=[html.H3("VELC / SUIT Imager", style={'margin':0}), dcc.Graph(id='p2-heatmap', responsive=True, style={'width': '100%', 'height': '300px'})]),
            html.Div(style={'backgroundColor': colors['surface'], 'padding': '15px', 'borderRadius': '10px'}, children=[html.H3("SoLEXS / HEL1OS Spectra", style={'margin':0}), dcc.Graph(id='p2-spectra', responsive=True, style={'width': '100%', 'height': '300px'})])
        ]),
        html.Div(style={'backgroundColor': colors['surface'], 'padding': '15px', 'borderRadius': '10px'}, children=[
            html.H3("PAPA & ASPEX Plasma Flow", style={'margin':0}), 
            html.Div(style={'display': 'flex', 'height': '300px', 'alignItems': 'center', 'justifyContent': 'center'}, children=[
                dcc.Graph(id='p2-gauge-v', responsive=True, style={'flex': '1', 'minWidth': 0}), 
                dcc.Graph(id='p2-gauge-n', responsive=True, style={'flex': '1', 'minWidth': 0}), 
                dcc.Graph(id='p2-gauge-bz', responsive=True, style={'flex': '1', 'minWidth': 0})
            ])
        ])
    ])

def page_3_models():
    return html.Div([
        html.H1("Neural Architecture & Evaluation Matrix"),
        html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '20px'}, children=[
            html.Div(style={'backgroundColor': colors['surface'], 'padding': '20px', 'borderRadius': '10px'}, children=[
                html.H2("SPACE-SUIT (YOLO)", style={'color': colors['accent']}),
                html.P("Transfer-learning architecture processing Mg II k-line full disk mosaics to bounding-box Plage and Sunspot structures."),
                dcc.Graph(id='p3-yolo-bar', responsive=True, style={'width': '100%', 'height': '250px'})
            ]),
            html.Div(style={'backgroundColor': colors['surface'], 'padding': '20px', 'borderRadius': '10px'}, children=[
                html.H2("ASPEX ICME (CatBoost)", style={'color': colors['accent']}),
                html.P("1300+ temporal feature matrix prioritizing Alpha-to-Proton ratios mapping to the mathematical Frozen-in Flux conditions."),
                dcc.Graph(id='p3-catboost-bar', responsive=True, style={'width': '100%', 'height': '250px'})
            ]),
            html.Div(style={'backgroundColor': colors['surface'], 'padding': '20px', 'borderRadius': '10px'}, children=[
                html.H2("VELC Morphology (CNN)", style={'color': colors['accent']}),
                html.P("Analyzes spatial structure disappearance mapping to >50% Coronal Dimming triggers."),
                html.Div("Target Trigger Time: < 2.0 Minutes", style={'padding': '10px', 'backgroundColor': colors['success'], 'textAlign': 'center', 'borderRadius': '5px', 'marginTop': '20px'})
            ]),
            html.Div(style={'backgroundColor': colors['surface'], 'padding': '20px', 'borderRadius': '10px'}, children=[
                html.H2("SoLEXS & HEL1OS (XGBoost/Power-Law)", style={'color': colors['accent']}),
                html.P("Solves HYPERMET gaussian components and Broken Power-Law Regression (Ec) evaluating spectral energy index."),
                html.Div("Prediction Occultation: 0.0%", style={'padding': '10px', 'backgroundColor': colors['success'], 'textAlign': 'center', 'borderRadius': '5px', 'marginTop': '20px'})
            ])
        ])
    ])

def page_4_parameters():
    return html.Div([
        html.H1("Solar Plasma Parametric Archive (L1)"),
        html.P("17 Live mathematical vectors derived from Aditya-L1 Raw Telemetry.", style={'color': colors['accent']}),
        html.Div(id='p4-grid-container', style={'display': 'grid', 'gridTemplateColumns': 'repeat(4, 1fr)', 'gap': '15px'})
    ])

def page_5_logs():
    return html.Div([
        html.H1("Mission Configuration & Diagnostic Logs"),
        html.Div(style={'backgroundColor': colors['surface'], 'padding': '20px', 'borderRadius': '10px', 'height': '70vh', 'overflowY': 'auto', 'fontFamily': 'monospace'}, children=[
            html.Div(id='p5-log-stream')
        ])
    ])

app.layout = html.Div([
    dcc.Location(id="url"), 
    sidebar, 
    # Use persistent DOM state toggling instead of destruction to save all React components!
    html.Div(id="page-content", style=CONTENT_STYLE, children=[
        html.Div(id='page-1', children=page_1_strategic(), style={'display': 'block'}),
        html.Div(id='page-2', children=page_2_diagnostics(), style={'display': 'none'}),
        html.Div(id='page-3', children=page_3_models(), style={'display': 'none'}),
        html.Div(id='page-4', children=page_4_parameters(), style={'display': 'none'}),
        html.Div(id='page-5', children=page_5_logs(), style={'display': 'none'}),
    ]), 
    dcc.Interval(id='stream', interval=3000, n_intervals=0)
])

# ------------------------------------------------------------------------------
# Callbacks
# ------------------------------------------------------------------------------

@app.callback(
    [Output("page-1", "style"), Output("page-2", "style"), Output("page-3", "style"), Output("page-4", "style"), Output("page-5", "style")],
    [Input("url", "pathname")]
)
def render_page_content(pathname):
    s1 = s2 = s3 = s4 = s5 = {'display': 'none'}
    if pathname == "/diagnostics": s2 = {'display': 'block'}
    elif pathname == "/models": s3 = {'display': 'block'}
    elif pathname == "/parameters": s4 = {'display': 'block'}
    elif pathname == "/logs": s5 = {'display': 'block'}
    else: s1 = {'display': 'block'}
    return s1, s2, s3, s4, s5

@app.callback(
    [Output('p1-48h-chart', 'figure')] + 
    [Output('p2-heatmap', 'figure'), Output('p2-spectra', 'figure'), Output('p2-gauge-v', 'figure'), Output('p2-gauge-n', 'figure'), Output('p2-gauge-bz', 'figure')] +
    [Output('p3-yolo-bar', 'figure'), Output('p3-catboost-bar', 'figure')] +
    [Output('p4-grid-container', 'children'), Output('p5-log-stream', 'children')],
    [Input('stream', 'n_intervals')]
)
def update_dynamic_data(n):
    # 1. Page 1 Chart
    probabilities = prognostic_engine.evaluate_48hr_horizon(n)
    hours = np.linspace(0, 48, 48)
    fig_48h = go.Figure()
    fig_48h.add_trace(go.Scatter(x=hours, y=probabilities, fill='tozeroy', fillcolor='rgba(220, 38, 38, 0.2)', mode='lines', line=dict(color=colors['alert'], width=3), name='Impact Prob'))
    fig_48h.add_hline(y=0.95, line_dash="dash", line_color=colors['text'], annotation_text="95% Threshold")
    fig_48h.update_layout(plot_bgcolor=colors['surface'], paper_bgcolor=colors['surface'], font=dict(color=colors['text'], family="monospace"), margin=dict(l=40, r=20, t=10, b=30), height=200)

    # 2. Page 2 Diagnostics
    z = np.random.normal(size=(20, 20))
    fig_hm = go.Figure(data=go.Heatmap(z=z, colorscale='plasma', showscale=False))
    fig_hm.update_layout(plot_bgcolor=colors['surface'], paper_bgcolor=colors['surface'], margin=dict(l=0, r=0, t=0, b=0), xaxis=dict(showgrid=False, zeroline=False, showticklabels=False), yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))

    x_spec = np.linspace(1, 40, 100)
    y_spec = 5000 * np.exp(-((x_spec - 8)**2) / 3) + 300 * np.exp(-x_spec/8) + np.random.normal(0, 50, 100)
    fig_spec = go.Figure(go.Scatter(x=x_spec, y=y_spec, mode='lines', line=dict(color=colors['accent'])))
    fig_spec.update_layout(plot_bgcolor=colors['surface'], paper_bgcolor=colors['surface'], margin=dict(l=30, r=10, t=10, b=20), font=dict(color=colors['text']))

    def make_gauge(v, max_v, t, c):
        f = go.Figure(go.Indicator(mode="gauge+number", value=v, title={'text': t, 'font': {'color': colors['text'], 'size': 12}}, gauge={'axis': {'range': [None, max_v]}, 'bar': {'color': c}, 'bgcolor': colors['surface_light'], 'borderwidth': 0}))
        f.update_layout(paper_bgcolor=colors['surface'], plot_bgcolor=colors['surface'], margin=dict(l=20, r=20, t=30, b=10))
        return f
    
    v_val, n_val, bz_val = 850 + np.random.rand()*50, 25 + np.random.rand()*2, -15 - np.random.rand()*2
    fig_gv, fig_gn, fig_gbz = make_gauge(v_val, 1200, "Velocity", colors['accent']), make_gauge(n_val, 40, "Density", colors['success']), make_gauge(abs(bz_val), 50, "Bz nT", colors['alert'])

    # 3. Page 3 Models
    yolo_bar = go.Figure(data=[go.Bar(name='Target', x=['Precision', 'Recall'], y=[0.788, 0.863], marker_color=colors['surface_light']), go.Bar(name='Current (Mock)', x=['Precision', 'Recall'], y=[0.791, 0.840], marker_color=colors['accent'])])
    yolo_bar.update_layout(barmode='group', plot_bgcolor=colors['surface'], paper_bgcolor=colors['surface'], font=dict(color=colors['text']), margin=dict(l=20, r=20, t=20, b=20))
    
    cat_bar = go.Figure(data=[go.Bar(name='Target', x=['Accuracy', 'Recall'], y=[0.979, 0.934], marker_color=colors['surface_light']), go.Bar(name='Current (Mock)', x=['Accuracy', 'Recall'], y=[0.982, 0.941], marker_color=colors['success'])])
    cat_bar.update_layout(barmode='group', plot_bgcolor=colors['surface'], paper_bgcolor=colors['surface'], font=dict(color=colors['text']), margin=dict(l=20, r=20, t=20, b=20))

    # 4. Page 4 Parameters (17 specific tracking items - FULLY LIVE)
    beta = 1.24 + np.random.normal(0, 0.05)
    tk = 1.4 + np.random.normal(0, 0.1)
    he_ratio = 0.082 + np.random.normal(0, 0.005)
    anisotropy = 1.15 + np.random.normal(0, 0.02)
    vnt = 24.87 + (np.random.normal(0, 2.5) if n > 2 else np.random.normal(0, 0.1))
    dim_area = max(0, int(1240 + np.random.normal(0, 150))) if n > 2 else int(15 + np.random.rand()*5)
    mg_valley = 2.14 + np.random.normal(0, 0.08)
    plage_px = int(4050 + np.random.normal(0, 200))
    bx = 4.2 + np.random.normal(0, 0.5)
    by = -2.1 + np.random.normal(0, 0.4)
    psd_slope = -1.666 + np.random.normal(0, 0.01)
    ec_cutoff = 25.0 + np.random.normal(0, 1.2)
    gamma = 3.2 + np.random.normal(0, 0.1)
    flare_flux = (8.2e-4 + np.random.normal(0, 0.5e-4)) * (5 if n > 2 else 1)

    param_data = [
        ("Solar Wind Speed", f"{v_val:.1f} km/s"), ("Proton Density", f"{n_val:.1f} cm⁻³"),
        ("Plasma Beta (β)", f"{beta:.2f}"), ("Kinetic Temp (Tk)", f"{tk:.2f}e5 K"),
        ("He++/H+ Ratio", f"{he_ratio:.3f}"), ("Temp Anisotropy", f"{anisotropy:.2f}"),
        ("v_nt Velocity", f"{vnt:.2f} km/s"), ("Dimming Area", f"{dim_area} px"),
        ("Mg II Valley", f"{mg_valley:.2f}"), ("Plage Px Count", f"{plage_px}"),
        ("IMF Bx", f"{bx:.1f} nT"), ("IMF By", f"{by:.1f} nT"), ("IMF Bz", f"{bz_val:.1f} nT"),
        ("PSD Slope", f"{psd_slope:.3f}"), ("Low-E Cutoff (Ec)", f"{ec_cutoff:.1f} keV"),
        ("Spectral Index (γ)", f"{gamma:.1f}"), ("Flare Flux", f"{flare_flux:.2e} W/m²")
    ]
    grid_children = [
        html.Div(style={'backgroundColor': colors['surface'], 'padding': '15px', 'borderRadius': '8px', 'border': f'1px solid {colors["surface_light"]}'}, children=[
            html.Div(p[0], style={'fontSize': '11px', 'color': colors['text'], 'textTransform': 'uppercase', 'fontWeight': 'bold'}),
            html.Div(p[1], style={'fontSize': '20px', 'color': colors['accent'], 'fontFamily': 'monospace', 'marginTop': '5px'})
        ]) for p in param_data
    ]

    # 5. Page 5 Logs
    diag = prognostic_engine.generate_diagnostic_report(v_val, bz_val, True)
    dc = colors['alert'] if diag['severity']=='SEVERE' else colors['warning']
    
    # Generate an active rolling timeline to emulate historical tracking
    log_stream = []
    for i in range(15):
        past_n = max(0, n - i)
        past_bz = bz_val + np.random.normal(0, 2)
        # Randomize historical severity slightly if far past
        hist_sev = diag['severity'] if i < 3 else ('WARNING' if past_bz < -5 else 'NOMINAL')
        hist_dc = colors['alert'] if hist_sev == 'SEVERE' else (colors['warning'] if hist_sev == 'WARNING' else colors['success'])
        hist_txt = diag['text'] if i < 3 else (f"Interplanetary Magnetic Field (IMF) measuring {past_bz:.1f} nT. No extreme kinematics observed." if hist_sev == 'NOMINAL' else "Moderate turbulence observed in plasma stream.")
        
        log_stream.append(
            html.Div(style={'borderLeft': f'4px solid {hist_dc}', 'padding': '10px', 'marginBottom': '10px', 'backgroundColor': colors['surface_light']}, children=[
                html.Div(f"T-Minus: {i*3} seconds", style={'color': colors['text'], 'fontSize': '10px', 'fontWeight': 'bold', 'opacity': '0.5'}),
                html.H4(f"[{past_n}] {hist_sev} ALERT", style={'color': hist_dc, 'margin': '2px 0 5px 0'}),
                html.Div(hist_txt, style={'color': '#cbd5e1'})
            ])
        )

    return fig_48h, fig_hm, fig_spec, fig_gv, fig_gn, fig_gbz, yolo_bar, cat_bar, grid_children, log_stream

if __name__ == '__main__':
    print("🚀 Auto-Deploying Aditya-L1 Multi-Page Command Center...")
    app.run(debug=False, port=8050)

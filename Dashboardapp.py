import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Chargement des données
df = pd.read_csv('heart_disease_clean.csv',sep = ";")

quant_cols = df.select_dtypes(include = "number")
cat_cols = df.select_dtypes(include = "object")
# Initialisation de l'application Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

corr = quant_cols.corr()
fig = px.imshow(
    corr,
    text_auto=True,
    color_continuous_scale="Viridis",
    labels=dict(color="Corrélation"),
    aspect="auto"
)
# Layout du dashboard
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Dashboard d'analyse des Facteurs de Maladies Cardiaques", 
                       className="text-center mb-4"), width=12)
    ]),
    
    # Première rangée avec 2 graphiques côte à côte
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.Label("Sélectionnez la variable pour l'histogramme:"),
                dcc.Dropdown(
                    id='hist-variable',
                    options=[{'label': col, 'value': col} for col in quant_cols],
                    value='age',
                    clearable=False
                ),
                dcc.Graph(id='hist-plot')
            ])
        ]), md=6),
        
        dbc.Col(dbc.Card([
            dbc.CardBody([
                 html.Label("Sélectionnez les variables pour le boxplot:"),
                    dbc.Row([
                    dbc.Col([
                        html.Label("Axe X: Variable catégorielle"),
                        dcc.Dropdown(
                            id='boxplot-x',
                            options=[{'label': col, 'value': col} for col in cat_cols],
                            value='sex',
                            clearable=False
                        )
                    ], md=6),
                    dbc.Col([
                        html.Label("Axe Y: Variable numérique"),
                        dcc.Dropdown(
                            id='boxplot-y',
                            options=[{'label': col, 'value': col} for col in quant_cols],
                            value='age',
                            clearable=False
                        )
                    ], md=6)
                ]),
                dcc.Graph(id='box-plot')
            ])
        ]), md=6)
    ], className="mb-4"),
    
    # Deuxième rangée avec 2 graphiques côte à côte
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.Label("Sélectionnez les variables pour le nuage de points:"),
                dbc.Row([
                    dbc.Col([
                        html.Label("Axe X:"),
                        dcc.Dropdown(
                            id='scatter-x',
                            options=[{'label': col, 'value': col} for col in quant_cols],
                            value='age',
                            clearable=False
                        )
                    ], md=6),
                    dbc.Col([
                        html.Label("Axe Y:"),
                        dcc.Dropdown(
                            id='scatter-y',
                            options=[{'label': col, 'value': col} for col in quant_cols],
                            value='chol',
                            clearable=False
                        )
                    ], md=6)
                ]),
                dcc.Graph(id='scatter-plot')
            ])
        ]), md=6),
        
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.Label("Sélectionnez la variable catégorielle:"),
                dcc.Dropdown(
                    id='pie-variable',
                    options=[{'label': col, 'value': col} for col in cat_cols ],
                    value='sex',
                    clearable=False
                ),
                dcc.Graph(id='pie-plot')
            ])
        ]), md=6)
    ], className="mb-4"),
    
    # Troisième rangée avec 1 graphique (premier des deux grands)
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.Label("Analyse des corrélations entre variables:"),
                dcc.Graph(id='heatmap-plot',figure = fig)
            ])
        ]), width=12)
    ], className="mb-4"),
    
    # Quatrième rangée avec 1 graphique (second des deux grands)
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.Label("Distribution des variables continues par statut de maladie cardiaque:"),
                dcc.Dropdown(
                    id='violin-variable',
                    options=[{'label': col, 'value': col} for col in ['age', 'trestbps', 'chol', 'thalach', 'oldpeak']],
                    value='chol',
                    clearable=False
                ),
                dcc.Graph(id='violin-plot')
            ])
        ]), width=12)
    ]),
], fluid=True)

# Callbacks pour l'interactivité

# Histogramme
@app.callback(
    Output('hist-plot', 'figure'),
    Input('hist-variable', 'value')
)
def update_histogram(selected_variable):
    fig = px.histogram(df, x=selected_variable, nbins=20, 
                       title=f"Distribution de {selected_variable}",
                       color_discrete_sequence=['#636EFA'])
    fig.update_layout(showlegend=False)
    return fig

# Box plot
@app.callback(
    Output('box-plot', 'figure'),
    [Input('boxplot-x', 'value'),
     Input('boxplot-y', 'value')]
)
def update_boxplot(selected_var_x,selected_var_y):
    fig = px.box(df, x= selected_var_x,y = selected_var_y)
    return fig

# Scatter plot
@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('scatter-x', 'value'),
     Input('scatter-y', 'value')]
)
def update_scatter(x_var, y_var):
    fig = px.scatter(df, x=x_var, y=y_var,
                     title=f"Relation entre {x_var} et {y_var}"
                     )
    return fig

# Pie chart
@app.callback(
    Output('pie-plot', 'figure'),
    Input('pie-variable', 'value')
)
def update_piechart(selected_variable):
    counts = df[selected_variable].value_counts().reset_index()
    counts.columns = ['category', 'count']
    fig = px.pie(counts, values='count', names='category', 
                 title=f"Répartition par {selected_variable}")
    return fig

# Heatmap


# Violin plot
@app.callback(
    Output('violin-plot', 'figure'),
    Input('violin-variable', 'value')
)
def update_violinplot(selected_variable):
    fig = px.violin(df, y=selected_variable, x='target', box=True, points="all",
                    title=f"Distribution de {selected_variable} par statut de maladie cardiaque",
                    labels={'target': 'Maladie cardiaque'},
                    color='target',
                    color_discrete_sequence=['#EF553B', '#636EFA'])
    return fig

if __name__ == '__main__':

    app.run(debug=True)

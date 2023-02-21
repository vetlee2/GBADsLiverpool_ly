from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import os

CWD = os.getcwd()
DASH_DATA_FOLDER = os.path.join(CWD ,'data')
amu2018_combined_tall = pd.read_csv(os.path.join(DASH_DATA_FOLDER, 'amu2018_combined_tall.csv'))

#input_df = pd.read_csv('amu2018_combined_tall.csv')

app = Dash(__name__)


#Header and Html formatting for AMU Regional Stacked Bar
app.layout = html.Div([    
    dcc.Dropdown(
        id='importance-ctg',
        options=("critically_important", "highly_important", "other"),
        value="critically_important",
        clearable=False,
        ),
    dcc.Graph(id="update_stacked_bar_amu", style={'display': 'inline-block'}),
    dcc.Graph(id="update_stacked_bar_amu2",  style={'display': 'inline-block'}),
    
])


        
#Update Stacked Bar Chart
@app.callback(
    Output('update_stacked_bar_amu', 'figure'),
    Input('importance-ctg', 'value'))
    #Input('antimicrobial_class', 'value'),
    #Input('amu_tonnes', 'value'))
    #Input('scope', 'value'),
    #Input('number_of_countries', 'value'),
    #Input('importance_ctg', 'value'))

def update_stacked_bar_amu(region):
    input_df = pd.read_csv(os.path.join(DASH_DATA_FOLDER,'amu2018_combined_tall.csv'))
    
    stackedbar_df = input_df.query("scope == 'All'").query("antimicrobial_class != 'total_antimicrobials'")#.query(f"importance_ctg == '{critically_important}'")
    
    amu_bar_fig = px.bar(stackedbar_df, x='region', y='amu_tonnes',
                         color='antimicrobial_class', barmode='stack',
                        # yaxis={'categoryorder': 'importance_ctg'},
                         labels={
                             "region": "Region",
                             "amu_tonnes": "AMU Tonnes",
                             "antimicrobial_class": "Antimicrobial Class"})
              
    return amu_bar_fig
    
#Input('dropdown', 'value') 
@app.callback(
    Output('update_stacked_bar_amu2', 'figure'),
   Input('importance-ctg','value'))

def update_stacked_bar_amu2 (region):
    input_df = pd.read_csv(os.path.join(DASH_DATA_FOLDER,'amu2018_combined_tall.csv'))
    stackedbar_df = amu2018_combined_tall.copy()
    stackedbar_df = input_df.query("scope == 'All'").query("antimicrobial_class != 'total_antimicrobials'")
    
    amu_bar_fig2 = px.bar(stackedbar_df, x="region", y="amu_mg_perkgbiomass",
                         color='antimicrobial_class',
                         labels={
                             "region": "Region",
                             "amu_mg_perkgbiomass": "AMU Mg Per Kg Biomass",
                             "antimicrobial_class": "Antimicrobial Class"})

    return amu_bar_fig2

if __name__ == '__main__':
    app.run_server(debug=True)
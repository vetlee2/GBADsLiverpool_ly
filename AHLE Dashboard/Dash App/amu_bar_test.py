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
   html.H4('2018 Antimicrobial Usage by Region'),
    dcc.Dropdown(
        id="dropdown",
        options=["Africa", "Americas", "Asia", "Far East and Oceania", "Middle East"],
        value="Americas",
        clearable=False,
        ),
    dcc.Graph(id="update_stacked_bar_amu")
])

#Update Stacked Bar Chart
@app.callback(
    Output('update_stacked_bar_amu', 'figure'),
    Input('dropdown', 'value'))
    #Input('antimicrobial_class', 'value'),
    #Input('amu_tonnes', 'value'))
    #Input('scope', 'value'),
    #Input('number_of_countries', 'value'),
    #Input('importance_ctg', 'value'))

def update_stacked_bar_amu(region):
    input_df = pd.read_csv(os.path.join(DASH_DATA_FOLDER,'amu2018_combined_tall.csv'))
    
    stackedbar_df = input_df.query("scope == 'All'")#.query(f"region == '{region}'")
    

    #x = stackedbar_df['region']
    #y = stackedbar_df['antimicrobial_class']
    #color = stackedbar_df['amu_tonnes']
    #amu_bar_fig = update_stacked_bar_amu(stackedbar_df, x, y, color)
    amu_bar_fig = px.bar(stackedbar_df, x='region', y='amu_tonnes',
                         color='antimicrobial_class', barmode='stack',
                         color_discrete_map ={
                             "Europe": "red",
                             "Americas": "blue",
                             "Asia, Far East and Oceania": "green",
                             "Africa": "yellow",
                             "Middle East": "magenta"},
                         labels={
                             "region": "Region",
                             "amu_tonnes": "AMU Tonnes",
                             "antimicrobial_class": "Antimicrobial Class"})
              
    return amu_bar_fig
        
     

if __name__ == '__main__':
    app.run_server(debug=True)
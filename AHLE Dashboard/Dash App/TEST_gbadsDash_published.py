#%% Contents
# -----------------------------------------------------------------------------------------------
# ### Framework
# 1. Startup & Imports
# 2. Initialize App (i.e., the web app)
# 3. Global Program Elements (e.g. read in data and prep it)
# 4. Layout (i.e, the UI layout)
# 5. Callbacks (functions that respond to UI)
# 6. Run App
# -----------------------------------------------------------------------------------------------

#%% 1. STARTUP & IMPORTS

# standard library packages (included with python and always available)
import os, sys, datetime as dt
from pathlib import Path
import inspect
import requests
import io

print(f"[{dt.datetime.now().strftime('%Y%m%d_%H%M%S.%f')[:19]}] Starting {__name__}")
print(f"[{dt.datetime.now().strftime('%Y%m%d_%H%M%S.%f')[:19]}] cwd = {os.getcwd()}")
print(f"[{dt.datetime.now().strftime('%Y%m%d_%H%M%S.%f')[:19]}] {sys.path[:2] = }")
print(f"[{dt.datetime.now().strftime('%Y%m%d_%H%M%S.%f')[:19]}] {sys.version = }")

# Third party packages (ie, those installed with pip )
# NO NEED to import Dash or JupyterDash here.  That is done within fa.instantiate_app

from dash import html, dcc, Input, Output, State, dash_table
import dash_bootstrap_components as dbc  # Allows easy access to all bootstrap themes
import dash_daq as daq
import dash_auth
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import datashader as ds

# private (fa) libraries
import lib.fa_dash_utils as fa
import lib.bod_calcs as bod
import lib.ga_ahle_calcs as ga

#### PARAMETERS

prod = False          # Use when testing/dev mode to remove auth

#%% 2. INITIALIZE APP
###############################################################################################
# - App named here... if name is changed here, must also be changed elsewhere below
# - Either JupyterDash or just Dash for traditional .py program in Spyder. (Latter requires: 'from dash import Dash' above)
# - There are other dbc.themes (e.g. "SANDSTONE") and other options besides dash_bootstrap_components
###############################################################################################
app_title = 'Global Burden of Animal Disease'
external_stylesheets=[dbc.themes.BOOTSTRAP]
flask_server, app = fa.instantiate_app(app_title, external_stylesheets) # dont change name "flask_server".  Gunicorn expects to find it
gbadsDash = app  # an alias for app; the app name used within this program

if prod:
    ## USERNAMES AND PASSWORDS
    # Keep this out of source code repository - save in a file or a database
    VALID_USERNAME_PASSWORD_PAIRS = {
        'gbads': 'welcometogbads',
        'GBADS': "welcometogbads",
        'GBADs': "welcometogbads"
    }

    # BASIC AUTHORIZATION:  USERNAME:PASSWORD
    auth = dash_auth.BasicAuth(
        gbadsDash,
        VALID_USERNAME_PASSWORD_PAIRS
        )

#%% 3. GLOBAL PROGRAM ELEMENTS
###############################################################################################
# - Global variables and functions that aren't directly involved in the UI interactivity (Callbacks)
# - Typical example would be functions that read, store, and prep data to be used in the app
###############################################################################################
# Define tab styles
# tab_style = {'fontWeight': 'bold'}

# Tab colors based on grouping
global_tab_style = {
    'backgroundColor': '#aacce3',
    'border-color': 'grey',
    'fontWeight': 'bold'
}
global_tab_selected_style = {
    'backgroundColor': '#aacce3',
    'border-color': 'grey',
    'fontWeight': 'bold'
}

major_producers_tab_style = {
    'backgroundColor': '#abebc5',
    'border-color': 'grey',
    'fontWeight': 'bold'
}
major_producers_tab_selected_style = {
    'backgroundColor': '#abebc5',
    'border-color': 'grey',
    'fontWeight': 'bold'
}

ecs_tab_style = {
    'backgroundColor': '#d7bce1',
    'border-color': 'grey',
    'fontWeight': 'bold'
}
ecs_tab_selected_style = {
    'backgroundColor': '#d7bce1',
    'border-color': 'grey',
    'fontWeight': 'bold'
}

user_guide_tab_style ={
    'border-color': 'grey',
    'fontWeight': 'bold'
}

user_guide_tab_selected_style ={
    'border-color': 'grey',
    'fontWeight': 'bold'
}


# =============================================================================
# # For reference, the first version of the plots was based on Excel files
#
# # Data for the waterfall chart
# waterfall_df = pd.read_excel("data/chickens_bod_plotdata.xls", header=0,sheet_name="Waterfall")
#
# # Data for the sankey diagram
# sankey_df = pd.read_excel("data/chickens_bod_plotdata.xls", header=0,sheet_name="Sankey")
#
# # Data for the data table
# background_df = pd.read_excel('data/chickens_bod_backgrounddata.xls')
#
# =============================================================================

# =============================================================================
#### Read data
# =============================================================================
# Define folder location
CWD = os.getcwd()
DASH_DATA_FOLDER = os.path.join(CWD ,'data')

# Folder location for ethiopia case study
GBADsLiverpool=Path(os.getcwd()).parent.parent
Ethiopia_Workspace = "Ethiopia Workspace"

# Folder location for global aggregate
Global_Agg_Workspace = "Global Aggregate workspace"
if prod:
    # Output folders:
    ECS_PROGRAM_OUTPUT_FOLDER = os.path.join(CWD, Ethiopia_Workspace, "Program outputs")
    GA_DATA_FOLDER = os.path.join(CWD, Global_Agg_Workspace, "Data")
else:
    # Output folders:
    ECS_PROGRAM_OUTPUT_FOLDER = os.path.join(GBADsLiverpool, Ethiopia_Workspace, "Program outputs")
    GA_DATA_FOLDER = os.path.join(GBADsLiverpool, Global_Agg_Workspace, "Data")
# -----------------------------------------------------------------------------
# Poultry
# -----------------------------------------------------------------------------
# Main table
gbads_chickens_merged_fordash = pd.read_pickle(os.path.join(DASH_DATA_FOLDER ,'gbads_chickens_merged_fordash.pkl.gz'))

# Breed Standards
poultrybreedstd_ross308 = pd.read_pickle(os.path.join(DASH_DATA_FOLDER ,'poultrybreedstd_ross308.pkl.gz'))
poultrybreedstd_ross708 = pd.read_pickle(os.path.join(DASH_DATA_FOLDER ,'poultrybreedstd_ross708.pkl.gz'))
poultrybreedstd_cobb500 = pd.read_pickle(os.path.join(DASH_DATA_FOLDER ,'poultrybreedstd_cobb500.pkl.gz'))
poultrybreedstd_vencobb400 = pd.read_pickle(os.path.join(DASH_DATA_FOLDER ,'poultrybreedstd_vencobb400.pkl.gz'))
poultrybreedstd_liverpool_model = pd.read_pickle(os.path.join(DASH_DATA_FOLDER ,'poultrybreedstd_liverpool_model.pkl.gz'))

# -----------------------------------------------------------------------------
# Swine
# -----------------------------------------------------------------------------
# Main table
gbads_pigs_merged_fordash = pd.read_pickle(os.path.join(DASH_DATA_FOLDER ,'gbads_pigs_merged_fordash.pkl.gz'))

# Breed Standards
swinebreedstd_pic_growthandfeed = pd.read_pickle(os.path.join(DASH_DATA_FOLDER ,'swinebreedstd_pic_growthandfeed.pkl.gz'))
swinebreedstd_liverpool_model3 = pd.read_pickle(os.path.join(DASH_DATA_FOLDER ,'swinebreedstd_liverpool_model3.pkl.gz'))

# -----------------------------------------------------------------------------
# Ethiopia Case Study
# -----------------------------------------------------------------------------
# AHLE Summary
# ecs_ahle_summary = pd.read_csv(os.path.join(DASH_DATA_FOLDER ,'ahle_all_summary.csv'))
# Using alternative data which summarizes results from age/sex specific scenarios
ecs_ahle_summary = pd.read_csv(os.path.join(DASH_DATA_FOLDER ,'ahle_all_scensmry.csv'))

# AHLE Summary 2 - for stacked bar
ecs_ahle_summary2 = pd.read_csv(os.path.join(DASH_DATA_FOLDER ,'ahle_all_summary2.csv'))

# Attribution Summary
ecs_ahle_all_withattr = pd.read_csv(os.path.join(DASH_DATA_FOLDER ,'ahle_all_withattr.csv'))

# -----------------------------------------------------------------------------
# Global Aggregate
# -----------------------------------------------------------------------------
# Biomass FAOSTAT
ga_countries_biomass = pd.read_pickle(os.path.join(DASH_DATA_FOLDER ,'world_ahle_abt_fordash.pkl.gz'))

# Drop unnecessary columns
ga_countries_biomass = ga_countries_biomass.drop(columns=['producing_animals_eggs_hd',
                                                          'producing_animals_hides_hd',
                                                          'producing_animals_meat_hd',
                                                          'producing_animals_milk_hd',
                                                          'producing_animals_wool_hd',
                                                          'output_live_hd',
                                                          'output_total_hd',
                                                          'output_live_biomass_kg',
                                                          'output_total_biomass_kg',
                                                          'output_value_live_2010usd',
                                                          'output_value_total_2010usd',
                                                          'output_value_meatlive_2010usd',
                                                          'producer_price_milk_usdpertonne_cnst2010',
                                                          'producer_price_wool_usdpertonne_cnst2010',
                                                          'producer_price_meat_live_usdpertonne_cnst2010',
                                                          'producer_price_eggs_usdpertonne_cnst2010',
                                                          'producer_price_meat_usdpertonne_cnst2010',
                                                          'production_eggs_kgperkgbm',
                                                          'production_hides_kgperkgbm',
                                                          'production_meat_kgperkgbm',
                                                          'production_milk_kgperkgbm',
                                                          'production_wool_kgperkgbm',
                                                          ])

# Drop species
drop_species = ['Camels',
                'Horses',
                'Buffaloes',
                'Ducks']

_drop_species = (ga_countries_biomass['species'].isin(drop_species))
ga_countries_biomass = ga_countries_biomass.loc[~ _drop_species]


# Drop countries
# Thin the regions with many countries
ga_countries_biomass['region'].unique()
countries_eap = list(ga_countries_biomass.query("region == 'East Asia & Pacific'")['country'].unique())
countries_eca = list(ga_countries_biomass.query("region == 'Europe & Central Asia'")['country'].unique())
countries_ssa = list(ga_countries_biomass.query("region == 'Sub-Saharan Africa'")['country'].unique())
countries_lac = list(ga_countries_biomass.query("region == 'Latin America & the Caribbean'")['country'].unique())

drop_countries = [
    
    # Europe & Central Asia
    'Albania'
    ,'Armenia'
    # ,'Austria'
    ,'Azerbaijan'
    ,'Belarus'
    ,'Bulgaria'
    ,'Croatia'
    ,'Cyprus'
    ,'Czechia'
    # ,'Denmark'
    ,'Estonia'
    # ,'Finland'
    # ,'France'
    ,'Georgia'
    # ,'Germany'
    # ,'Greece'
    ,'Hungary'
    # ,'Iceland'
    # ,'Ireland'
    # ,'Italy'
    ,'Kazakhstan'
    ,'Kyrgyzstan'
    ,'Latvia'
    ,'Lithuania'
    # ,'Netherlands'
    ,'North Macedonia'
    # ,'Norway'
    # ,'Poland'
    ,'Portugal'
    ,'Romania'
    ,'Slovakia'
    ,'Slovenia'
    # ,'Spain'
    # ,'Sweden'
    ,'Switzerland'
    ,'Tajikistan'
    # ,'Turkey'
    ,'Turkmenistan'
    # ,'Ukraine'
    ,'Uzbekistan'

    # East Asia & Pacific
    # ,'Australia'
    ,'Cambodia'
    ,'Cook Islands'
    ,'Fiji'
    ,'French Polynesia'
    # ,'Indonesia'
    # ,'Japan'
    ,'Kiribati'
    # ,'Malaysia'
    ,'Mongolia'
    ,'Myanmar'
    ,'Nauru'
    ,'New Caledonia'
    # ,'New Zealand'
    ,'Niue'
    # ,'Papua New Guinea'
    # ,'Philippines'
    ,'Samoa'
    ,'Singapore'
    ,'Solomon Islands'
    # ,'Thailand'
    ,'Tonga'
    ,'Tuvalu'
    ,'Vanuatu'
    # ,'Viet Nam'

    # Latin America & the Caribbean
    ,'Antigua and Barbuda'
    # ,'Argentina'
    ,'Bahamas'
    ,'Barbados'
    ,'Belize'
    # ,'Bolivia'
    # ,'Brazil'
    # ,'Chile'
    # ,'Colombia'
    # ,'Costa Rica'
    # ,'Cuba'
    ,'Dominica'
    ,'Dominican Republic'
    ,'Ecuador'
    ,'El Salvador'
    ,'Grenada'
    ,'Guadeloupe'
    ,'Guatemala'
    ,'Guyana'
    # ,'Haiti'
    ,'Honduras'
    # ,'Jamaica'
    # ,'Mexico'
    # ,'Nicaragua'
    # ,'Panama'
    ,'Paraguay'
    # ,'Peru'
    # ,'Puerto Rico'
    ,'Saint Kitts and Nevis'
    ,'Saint Lucia'
    ,'Saint Vincent and the Grenadines'
    ,'Suriname'
    ,'Trinidad and Tobago'
    ,'Uruguay'

    # Sub-Saharan Africa
    ,'Angola'
    ,'Benin'
    ,'Botswana'
    ,'Burkina Faso'
    ,'Burundi'
    ,'Cameroon'
    # ,'Central African Republic'
    ,'Chad'
    ,'Comoros'
    # ,'Congo'
    ,"Côte d'Ivoire"
    # ,'Democratic Republic of the Congo'
    ,'Eritrea'
    ,'Eswatini'
    # ,'Ethiopia'
    ,'Gabon'
    ,'Gambia'
    # ,'Ghana'
    # ,'Guinea'
    ,'Guinea-Bissau'
    # ,'Kenya'
    ,'Lesotho'
    ,'Liberia'
    # ,'Madagascar'
    ,'Malawi'
    ,'Mali'
    ,'Mauritania'
    ,'Mauritius'
    # ,'Mozambique'
    # ,'Namibia'
    ,'Niger'
    # ,'Nigeria'
    # ,'Rwanda'
    ,'Sao Tome and Principe'
    ,'Senegal'
    ,'Seychelles'
    ,'Sierra Leone'
    # ,'Somalia'
    # ,'South Africa'
    ,'Togo'
    ,'Uganda'
    ,'Zambia'
    # ,'Zimbabwe'
]
_drop_countries = (ga_countries_biomass['country'].isin(drop_countries))
ga_countries_biomass = ga_countries_biomass.loc[~ _drop_countries]

# Keep history only to 2015
ga_countries_biomass = ga_countries_biomass.loc[ga_countries_biomass['year'] >= 2015]

# Drop missing values from species
ga_countries_biomass['species'].replace('', np.nan, inplace=True)
ga_countries_biomass.dropna(subset=['species'], inplace=True)

# =============================================================================
#### User options and defaults
# =============================================================================
# -----------------------------------------------------------------------------
# All species
# -----------------------------------------------------------------------------
# Region options
region_structure_options = [{'label': i, 'value': i, 'disabled': False} for i in ["WOAH",
                                                                       "FAO",
                                                                       "World Bank",]]

# WOAH regions
WOAH_region_options = [{'label': i, 'value': i, 'disabled': False} for i in ["All",
                                                                        "Africa",
                                                                       "Americas",
                                                                       "Asia & the Pacific",
                                                                       "Europe"
                                                                       ]]
WOAH_region_options += [{'label': "Middle East", 'value': "Middle East", 'disabled': True}]  # Include, but disable, Middle East

# WOAH region-country mapping
WOAH_africa_options = [{'label': i, 'value': i, 'disabled': True} for i in ["Ethiopia"]]

WOAH_americas_options = [{'label': i, 'value': i, 'disabled': False} for i in ["Brazil",
                                                                          "United States of America"]]

WOAH_asia_options = [{'label': i, 'value': i, 'disabled': False} for i in ["India",
                                                                          "United States of America"]]

WOAH_europe_options = [{'label': i, 'value': i, 'disabled': False} for i in ["France",
                                                                        "Germany",
                                                                       "Italy",
                                                                       "Netherlands",
                                                                       "Poland",
                                                                       "United Kingdom"]]

# FAO regions
fao_region_options = [{'label': i, 'value': i, 'disabled': False} for i in ["All",
                                                                        "Africa",
                                                                       "Asia",
                                                                       "Europe and Central Asia",
                                                                       "Latin America and the Caribbean",
                                                                       "South West Pacific"
                                                                       ]]

fao_region_options += [{'label': "Near East and North Africa", 'value': "Near East and North Africa", 'disabled': True}]  # Include, but disable, Middle East

# FAO region-country mapping
fao_africa_options = [{'label': i, 'value': i, 'disabled': True} for i in ["Ethiopia"]]

fao_asia_options = [{'label': i, 'value': i, 'disabled': False} for i in ["India"]]

fao_eca_options = [{'label': i, 'value': i, 'disabled': False} for i in ["France",
                                                                        "Germany",
                                                                       "Italy",
                                                                       "Netherlands",
                                                                       "Poland",
                                                                       "United Kingdom"]]

fao_lac_options = [{'label': i, 'value': i, 'disabled': False} for i in ["Brazil"]]

fao_swp_options = [{'label': i, 'value': i, 'disabled': False} for i in ["France",
                                                                          "United States of America"]]

# World Bank regions
wb_region_options = [{'label': i, 'value': i, 'disabled': False} for i in ["All",
                                                                        "Sub-Saharan Africa",
                                                                       "Europe & Central Asia",
                                                                       "Latin America & the Caribbean",
                                                                       "North America",
                                                                       "South Asia"
                                                                       ]]

wb_region_options += [{'label': i, 'value': i, 'disabled': True} for i in ["East Asia & Pacific",
                                                                       "Middle East & North Africa"
                                                                       ]]

# World Bank region-country mapping

wb_africa_options = [{'label': i, 'value': i, 'disabled': True} for i in ["Ethiopia"]]

wb_eca_options = [{'label': i, 'value': i, 'disabled': False} for i in ["France",
                                                                        "Germany",
                                                                       "Italy",
                                                                       "Netherlands",
                                                                       "Poland",
                                                                       "United Kingdom"]]

wb_lac_options = [{'label': i, 'value': i, 'disabled': False} for i in ["Brazil"]]

wb_na_options = [{'label': i, 'value': i, 'disabled': False} for i in ["United States of America"]]

wb_southasia_options = [{'label': i, 'value': i, 'disabled': False} for i in ["India"]]


# Define country shortnames
# These taken from https://en.wikipedia.org/wiki/List_of_alternative_country_names
# Keys in this dictionary must match country names in data
# Should include superset of countries from all species
country_shortnames = {
   'Brazil':'BRA'
   ,'China':'CHN'
   ,'Denmark':'DNK'
   ,'France':'FRA'
   ,'Germany':'DEU'
   ,'India':'IND'
   ,'Italy':'ITA'
   ,'Netherlands':'NLD'
   ,'Poland':'POL'
   ,'Russia':'RUS'
   ,'Spain':'ESP'
   ,'United Kingdom':'GBR'
   ,'United States of America':'USA'
}

# Metrics
# Labels are shown in dropdown, Values are shown in plot titles
# Values must match column names created in prep_bod_forwaterfall()
metric_options = [
   {'label':"Tonnes", 'value':"tonnes", 'disabled':False}
   ,{'label':"US Dollars", 'value':"US dollars", 'disabled':False}
   ,{'label':"Percent of GDP", 'value':"percent of GDP", 'disabled':False}
   ,{'label':"Percent of Breed Standard", 'value':"percent of breed standard", 'disabled':False}
   ,{'label':"Percent of Realised Production", 'value':"percent of realised production", 'disabled':False}
]

# -----------------------------------------------------------------------------
# Poultry
# -----------------------------------------------------------------------------
country_options_poultry = []
for i in np.sort(gbads_chickens_merged_fordash['country'].unique()) :
   country_shortname = country_shortnames[i]
   compound_label = f"{i} ({country_shortname})"
   str(country_options_poultry.append({'label':compound_label,'value':(i)}))

year_options_poultry = []
for i in np.sort(gbads_chickens_merged_fordash['year'].unique()) :
   str(year_options_poultry.append({'label':i,'value':(i)}))

# Global defaults for sliders
# Most sliders will default to a value based on data for the selected country and year
# These values are used if data is missing
dof_poultry_default = 35
achievable_pct_poultry_default = 100
producer_price_poultry_default = 1.75
ration_price_poultry_default = 200
fcr_poultry_default = 1.5

# Breed-country matchup
# Keys must match country names in data
# Values will appear in dashboard text
poultry_lookup_breed_from_country = {
   'Brazil':'Cobb 500'
   ,'China':'Cobb 500'
   ,'France':'Ross 308'
   ,'Germany':'Ross 308'
   ,'India':'Venncobb 400'
   ,'Italy':'Ross 308'
   ,'Netherlands':'Ross 308'
   ,'Poland':'Ross 308'
   ,'Spain':'Ross 308'
   ,'United Kingdom':'Ross 308'
   ,'United States of America':'Cobb 500'
}

# Breed data lookup
# Keys must match values in poultry_lookup_breed_from_country
# Values must be data frames imported above
poultry_lookup_breed_df = {
   'Cobb 500':poultrybreedstd_cobb500
   ,'Ross 308':poultrybreedstd_ross308
   ,'Ross 708':poultrybreedstd_ross708
   ,'Venncobb 400':poultrybreedstd_vencobb400
}

# -----------------------------------------------------------------------------
# Swine
# -----------------------------------------------------------------------------
country_options_swine = []
for i in np.sort(gbads_pigs_merged_fordash['country'].unique()) :
   country_shortname = country_shortnames[i]
   compound_label = f"{i} ({country_shortname})"
   str(country_options_swine.append({'label':compound_label,'value':(i)}))

year_options_swine = []
for i in np.sort(gbads_pigs_merged_fordash['year'].unique()):
   str(year_options_swine.append({'label':i,'value':(i)}))

# Global defaults for sliders
# Most sliders will default to a value based on data for the selected country and year
# These values are used if data is missing
dof_swine_default = 147
feed_swine_default = 270
achievable_weight_swine_default = 120
producer_price_swine_default = 1.75
ration_price_swine_default = 200
fcr_swine_default = 2.2

# Breed-country matchup
# Keys must match country names in data
# Values will appear in dashboard text
swine_lookup_breed_from_country = {
   'Brazil':'PIC'
   ,'China':'PIC'
   ,'Denmark':'PIC'
   ,'France':'PIC'
   ,'Germany':'PIC'
   ,'Italy':'PIC'
   ,'Netherlands':'PIC'
   ,'Poland':'PIC'
   ,'Russia':'PIC'
   ,'Spain':'PIC'
   ,'United Kingdom':'PIC'
   ,'United States of America':'PIC'
}

# Breed data lookup
# Keys must match values in swine_lookup_breed_from_country
# Values must be data frames imported above
swine_lookup_breed_df = {
   'PIC':swinebreedstd_pic_growthandfeed
}

# =============================================================================
#### Ethiopia case study options
# =============================================================================
# Species
# ecs_species_options = []
# for i in np.sort(ecs_ahle_summary['species'].unique()):
#     str(ecs_species_options.append({'label':i,'value':(i)}))
# Specify the order of the species
ecs_species_options = [{'label': i, 'value': i, 'disabled': False} for i in ["All Small Ruminants",
                                                                             "Goat",
                                                                             "Sheep",
                                                                             "All Poultry",
                                                                             "Poultry hybrid",
                                                                             "Poultry indigenous",
                                                                             "Cattle"
                                                                             ]]

# Production system
# Rename Overall to more descriptive
ecs_ahle_summary['production_system'] = ecs_ahle_summary['production_system'].replace({'Overall': 'All Production Systems'})

# ecs_prodsys_options are now defined dynamically in a callback based on selected species
# ecs_prodsys_options = []
# for i in np.sort(ecs_ahle_summary['production_system'].unique()):
#    str(ecs_prodsys_options.append({'label':i,'value':(i)}))

# Year
# !!! - PLACEHOLDER UNTIL WE HAVE MORE DATA
ecs_year_options = [{'label': 2021, 'value': 2021, 'disabled': False}]

# Age
# Rename Overall to more descriptive
# ecs_ahle_summary['age_group'] = ecs_ahle_summary['age_group'].replace({'Overall': 'Overall Age'})
# ecs_age_options = [{'label': "Overall Age", 'value': "Overall Age", 'disabled': False}]

# ecs_age_options=[]
# for i in np.sort(ecs_ahle_summary['age_group'].unique()):
#    str(ecs_age_options.append({'label':i,'value':(i)}))

# Sex
# Rename Overall to more descriptive
# ecs_ahle_summary['sex'] = ecs_ahle_summary['sex'].replace({'Overall': 'Overall Sex'})

# ecs_sex_options_all = []
# for i in np.sort(ecs_ahle_summary['sex'].unique()):
#    str(ecs_sex_options_all.append({'label':i,'value':(i)}))

ecs_agesex_options=[]
for i in np.sort(ecs_ahle_summary['agesex_scenario'].unique()):
   str(ecs_agesex_options.append({'label':i,'value':(i)}))

# Filter for juvenile and neonates
ecs_sex_options_filter = [{'label': "Overall Sex", 'value': "Overall Sex", 'disabled': False}]

# Currency
ecs_currency_options = [{'label': "Birr", 'value': "Birr", 'disabled': False},
                        {'label': "USD", 'value': "USD", 'disabled': False}]

# Attribution
ecs_attr_options = [{'label': "All Causes", 'value': "All Causes", 'disabled': False}]

for i in np.sort(ecs_ahle_all_withattr['cause'].unique()):
   str(ecs_attr_options.append({'label':i,'value':(i)}))

# Hierarchy
ecs_hierarchy_attr_options = [{'label': "Cause", 'value': "cause", 'disabled': False},
                              {'label': "Production System", 'value': "production_system", 'disabled': False},
                              {'label': "Age Group", 'value': "age_group", 'disabled': False},
                              {'label': "Sex", 'value': "sex", 'disabled': False},
                              {'label': "AHLE Component", 'value': "ahle_component", 'disabled': False}]

# Drill down options for hierarchy
ecs_hierarchy_dd_attr_options = [{'label': i, 'value': i, 'disabled': False} for i in ["None"]]

ecs_hierarchy_dd_attr_options += ecs_hierarchy_attr_options

# Display
ecs_display_options = [{'label': i, 'value': i, 'disabled': False} for i in ["Side by Side",
                                                                             "Difference (AHLE)",
                                                                            ]]

# Compare
ecs_compare_options = [{'label': i, 'value': i, 'disabled': False} for i in ["Ideal",
                                                                             "Zero Mortality",
                                                                             "Improvement"
                                                                             ]]

# Factor
ecs_factor_options = [{'label': i, 'value': i, 'disabled': True} for i in ["Mortality",
                                                                           "Live Weight",
                                                                           "Parturition Rate",
                                                                           "Lactation"
                                                                           ]]

# Reduction
ecs_improve_options = [{'label': i, 'value': i, 'disabled': True} for i in ['25%',
                                                                            '50%',
                                                                            '75%',
                                                                            '100%',
                                                                            ]]

# =============================================================================
#### Global Aggregate options
# =============================================================================
# Species
ga_species_options = []
for i in ga_countries_biomass['species'].unique():
    str(ga_species_options.append({'label':i,'value':(i)}))

country_options_ga = [{'label': "All", 'value': "All", 'disabled': False}]
for i in ga_countries_biomass['country'].unique():
    str(country_options_ga.append({'label':i,'value':(i)}))

# Income group
# Rename Overall to more descriptive
ga_countries_biomass['incomegroup'] = ga_countries_biomass['incomegroup'].replace({'L': 'Low', 'LM':'Lower Middle', 'UM':'Upper Middle', 'H':'High', 'UNK':'Unassigned', 'NaN':'Unassigned'})

# replacing na values in college with No college
ga_countries_biomass['incomegroup'].fillna("Unassigned", inplace = True)

incomegrp_options_ga = [{'label': "All", 'value': "All"}]
for i in ga_countries_biomass['incomegroup'].unique():
    str(incomegrp_options_ga.append({'label':i,'value':(i)}))

# Mortality rate
mortality_rate_options_ga = [{'label': f'{i*100: .0f}%', 'value': i, 'disabled': True} for i in list(np.array(range(1, 11)) / 100)]

# Year
year_options_ga = []
for i in np.sort(ga_countries_biomass['year'].unique()):
   str(year_options_ga.append({'label':i,'value':(i)}))

# AHLE elements
# Values here must match item names defined in prep_ahle_forwaterfall_ga()
item_list_ga = [
    'Meat'
    ,'Eggs'
    ,'Milk'
    ,'Wool'
    ,'Biomass'
    ,'Producers vet & med costs'
    ,'Public vet & med costs'
    ,'Net value'
]
item_options_ga = [{'label':i,'value':(i)} for i in item_list_ga]

# Map display options
map_display_options_ga = [
    'Population'
    ,'Live Weight'
    ,'Biomass'
    ,'Animal Health Loss Envelope (AHLE)'
    ,'AHLE per kg biomass'
    ]

# Defautls for sliders
mortality_rate_ga_default = 4
morbidity_rate_ga_default = 2
live_weight_price_ga_default = 1.75

# -----------------------------------------------------------------------------
# Region - Country Alignment
# -----------------------------------------------------------------------------
# !!!: CURRENTLY DIFFERENT FROM POULTRY/SWINE TABS DUE TO DATA AVAILABILITY -eventually want these to be the same

# Region options
region_structure_options_ga = [{'label': i, 'value': i, 'disabled': False} for i in ["World Bank",]]

region_structure_options_ga += [{'label': i, 'value': i, 'disabled': True} for i in ["WOAH",
                                                                                     "FAO",]]

# WOAH regions
WOAH_region_options_ga = [{'label': i, 'value': i, 'disabled': False} for i in ["All",
                                                                               "Africa",
                                                                               "Americas",
                                                                               "Asia & the Pacific",
                                                                               "Europe"
                                                                               "Middle East"
                                                                               ]]
# WOAH region-country mapping
WOAH_africa_options_ga = [{'label': i, 'value': i, 'disabled': False} for i in ["Ethiopia"]]

WOAH_americas_options_ga = [{'label': i, 'value': i, 'disabled': False} for i in ["Brazil",
                                                                                 "United States of America"]]

WOAH_asia_options_ga = [{'label': i, 'value': i, 'disabled': False} for i in ["India",
                                                                             "United States of America"]]

WOAH_europe_options_ga = [{'label': i, 'value': i, 'disabled': False} for i in ["France",
                                                                               "Germany",
                                                                               "Italy",
                                                                               "Netherlands",
                                                                               "Poland",
                                                                               "United Kingdom"]]

WOAH_me_options_ga = [{'label': i, 'value': i, 'disabled': False} for i in ["TEST"]]


# FAO regions
fao_region_options_ga = [{'label': i, 'value': i, 'disabled': False} for i in ["All",
                                                                               "Africa",
                                                                               "Asia",
                                                                               "Europe and Central Asia",
                                                                               "Latin America and the Caribbean",
                                                                               "Near East and North Africa"
                                                                               "South West Pacific"
                                                                               ]]

# FAO region-country mapping
fao_africa_options_ga = [{'label': i, 'value': i, 'disabled': False} for i in ["Ethiopia"]]

fao_asia_options_ga = [{'label': i, 'value': i, 'disabled': False} for i in ["India"]]

fao_eca_options_ga = [{'label': i, 'value': i, 'disabled': False} for i in ["France",
                                                                            "Germany",
                                                                            "Italy",
                                                                            "Netherlands",
                                                                            "Poland",
                                                                            "United Kingdom"]]

fao_lac_options_ga = [{'label': i, 'value': i, 'disabled': False} for i in ["Brazil"]]

fao_ena_options_ga = [{'label': i, 'value': i, 'disabled': False} for i in ["TEST"]]


fao_swp_options_ga = [{'label': i, 'value': i, 'disabled': False} for i in ["France",
                                                                            "United States of America"]]

# World Bank regions
# Rename Overall to more descriptive
ga_countries_biomass['region'] = ga_countries_biomass['region'].replace({'EAP': 'East Asia & Pacific',
                                                                         'ECA':'Europe & Central Asia',
                                                                         'LAC':'Latin America & the Caribbean',
                                                                         'MENA':'Middle East & North Africa',
                                                                         'NA':'North America',
                                                                         'SA':'South Asia',
                                                                         'SSA':'Sub-Saharan Africa'})

wb_region_options_ga = [{'label': "All", 'value': "All"}]
for i in ga_countries_biomass['region'].unique():
    str(wb_region_options_ga.append({'label':i,'value':(i)}))


# World Bank region-country mapping
# Pulled from World Bank site (https://datahelpdesk.worldbank.org/knowledgebase/articles/906519-world-bank-country-and-lending-groups)

# East Asia & Pacific options
options = ga_countries_biomass.loc[(ga_countries_biomass['region'] == 'East Asia & Pacific')]
wb_eap_options_ga = [{'label': "All", 'value': "All"}]
for i in options['country'].unique():
    str(wb_eap_options_ga.append({'label':i,'value':(i)}))

# Europe & Central Asia options
options = ga_countries_biomass.loc[(ga_countries_biomass['region'] == 'Europe & Central Asia')]
wb_eca_options_ga = [{'label': "All", 'value': "All"}]
for i in options['country'].unique():
    str(wb_eca_options_ga.append({'label':i,'value':(i)}))

# Latin America & the Caribbean options
options = ga_countries_biomass.loc[(ga_countries_biomass['region'] == 'Latin America & the Caribbean')]
wb_lac_options_ga = [{'label': "All", 'value': "All"}]
for i in options['country'].unique():
    str(wb_lac_options_ga.append({'label':i,'value':(i)}))

# Middle East & North Africa options
options = ga_countries_biomass.loc[(ga_countries_biomass['region'] == 'Middle East & North Africa')]
wb_mena_options_ga = [{'label': "All", 'value': "All"}]
for i in options['country'].unique():
    str(wb_mena_options_ga.append({'label':i,'value':(i)}))

# North America options
options = ga_countries_biomass.loc[(ga_countries_biomass['region'] == 'North America')]
wb_na_options_ga = [{'label': "All", 'value': "All"}]
for i in options['country'].unique():
    str(wb_na_options_ga.append({'label':i,'value':(i)}))

# South Asia options
options = ga_countries_biomass.loc[(ga_countries_biomass['region'] == 'South Asia')]
wb_southasia_options_ga = [{'label': "All", 'value': "All"}]
for i in options['country'].unique():
    str(wb_southasia_options_ga.append({'label':i,'value':(i)}))

# Sub-Saharan Africa options
options = ga_countries_biomass.loc[(ga_countries_biomass['region'] == 'Sub-Saharan Africa')]
wb_africa_options_ga = [{'label': "All", 'value': "All"}]
for i in options['country'].unique():
    str(wb_africa_options_ga.append({'label':i,'value':(i)}))

# =============================================================================
#### Burden of disease calcs
# =============================================================================
# These are stored in a separate file, bod_calcs.py, imported above.

# =============================================================================
#### Prep data for plots
# =============================================================================
# Create labels for BOD components
# Used for both Waterfall and Sankey
pretty_bod_component_names = {
   "bod_referenceproduction_tonnes":"Breed Standard Potential*"
   ,"bod_gmax_tonnes":"Achievable Without Disease"
   ,"bod_efficiency_tonnes":"Effect of Feed & Practices"
   ,"bod_realizedproduction_tonnes":"Realised Production"
   ,"bod_totalburden_tonnes":"Burden of Disease"
   ,"bod_deathloss_tonnes":"Mortality & Condemns"
   ,"bod_morbidity_tonnes":"Morbidity"
}

# Waterfall chart uses same structure as Sankey but fewer rows.
# It does not display interior nodes of Sankey, only end nodes.
def prep_bod_forwaterfall(
      INPUT_DF
      ,USDPERKG        # Float (0+): Price to producers in US dollars per kg of meat
      ,BOD_COMP_NAMES=pretty_bod_component_names   # Dictionary: defining names for each component of burden of disease that will appear in plots
      ):
   OUTPUT_DF = INPUT_DF.copy()

   # Melt BOD component columns into rows
   # Ordering here determines order in plot!!!
   cols_tomelt = [
      'bod_referenceproduction_tonnes'
      ,'bod_efficiency_tonnes'
      ,'bod_deathloss_tonnes'
      ,'bod_morbidity_tonnes'
      ,'bod_realizedproduction_tonnes'
   ]
   OUTPUT_DF = OUTPUT_DF.melt(
      id_vars=['country' ,'year']
      ,value_vars=cols_tomelt
      ,var_name='bod_component'
      ,value_name='tonnes'
   )

   # Add $ value calculation
   OUTPUT_DF['usd'] = OUTPUT_DF['tonnes'] * 1000 * USDPERKG

   # Add value as percent of gdp
   OUTPUT_DF = pd.merge(   # Merge gdp from core data onto melted data
      left=OUTPUT_DF
      ,right=INPUT_DF[['country' ,'year' ,'wb_gdp_usd']]
      ,on=['country' ,'year']
      ,how='left'
   )
   OUTPUT_DF['gdp_prpn'] = OUTPUT_DF['usd'] / OUTPUT_DF['wb_gdp_usd']

   # Add value as percent of breed standard
   OUTPUT_DF = pd.merge(
      left=OUTPUT_DF
      ,right=INPUT_DF[['country' ,'year' ,'bod_referenceproduction_tonnes']]
      ,on=['country' ,'year']
      ,how='left'
   )
   OUTPUT_DF['brdstd_prpn'] = OUTPUT_DF['tonnes'] / OUTPUT_DF['bod_referenceproduction_tonnes']

   OUTPUT_DF = pd.merge(
      left=OUTPUT_DF
      ,right=INPUT_DF[['country' ,'year' ,'bod_realizedproduction_tonnes']]
      ,on=['country' ,'year']
      ,how='left'
   )
   OUTPUT_DF['rlzprod_prpn'] = OUTPUT_DF['tonnes'] / OUTPUT_DF['bod_realizedproduction_tonnes']


   # Give BOD components pretty names
   OUTPUT_DF['bod_component'] = OUTPUT_DF['bod_component'].replace(BOD_COMP_NAMES)

   # Define pretty column names
   # These are used in plot titles
   rename_cols = {
      # "country":"Country"
      # ,"year":"Year"
      "bod_component":"Component"
      ,"tonnes":"tonnes"            # Name must match to a value from metric_options
      ,"usd":"US dollars"           # Name must match to a value from metric_options
      ,"gdp_prpn":"percent of GDP"  # Name must match to a value from metric_options
      ,"brdstd_prpn":"percent of breed standard"
      ,"rlzprod_prpn":"percent of realised production"
   }
   OUTPUT_DF = OUTPUT_DF.rename(columns=rename_cols)

   return OUTPUT_DF

def prep_bod_forsankey(
      INPUT_DF
      ,BOD_COMP_NAMES=pretty_bod_component_names   # Dictionary: defining names for each component of burden of disease that will appear in plots
      ):
   OUTPUT_DF = INPUT_DF.copy()

   # If user selected an achievable proportion too low, reduced growth (morbidity) will be the wrong sign
   # For these, set reduced growth (morbidity) = 0 and add reduced growth to effect of feed
   rows_with_wrongsign_morbidity = (OUTPUT_DF['bod_morbidity_tonnes'] > 0)
   OUTPUT_DF.loc[rows_with_wrongsign_morbidity] = OUTPUT_DF.loc[rows_with_wrongsign_morbidity].eval(
       '''
       bod_efficiency_tonnes = bod_efficiency_tonnes + bod_morbidity_tonnes
       bod_morbidity_tonnes = 0
       '''
   )

   # Burden of Disease is at least equal magnitude to death loss
   # If total burden < death loss, set equal to death loss
   rows_with_burden_lt_deathloss = (np.abs(OUTPUT_DF['bod_totalburden_tonnes']) < np.abs(OUTPUT_DF['bod_deathloss_tonnes']))
   OUTPUT_DF.loc[rows_with_burden_lt_deathloss] = OUTPUT_DF.loc[rows_with_burden_lt_deathloss].eval(
      '''
      bod_totalburden_tonnes = bod_deathloss_tonnes
      '''
   )

   # Melt each BOD component column into a row
   cols_tomelt = [
      # 'bod_referenceproduction_tonnes'      # Starting node is implicit. See sankey_source_lookup.
      'bod_gmax_tonnes'
      ,'bod_efficiency_tonnes'
      ,'bod_realizedproduction_tonnes'
      ,'bod_totalburden_tonnes'
      ,'bod_deathloss_tonnes'
      ,'bod_morbidity_tonnes'
   ]
   OUTPUT_DF = OUTPUT_DF.melt(
      id_vars=['country' ,'year']
      ,value_vars=cols_tomelt
      ,var_name='bod_component'
      ,value_name='value'
   )

   # Sankey requires a Source for each Destination
   sankey_source_lookup = {
      "bod_referenceproduction_tonnes":""       # Starting node has no source
      ,"bod_gmax_tonnes":"bod_referenceproduction_tonnes"
      ,"bod_efficiency_tonnes":"bod_referenceproduction_tonnes"
      ,"bod_realizedproduction_tonnes":"bod_gmax_tonnes"
      ,"bod_totalburden_tonnes":"bod_gmax_tonnes"
      ,"bod_deathloss_tonnes":"bod_totalburden_tonnes"
      ,"bod_morbidity_tonnes":"bod_totalburden_tonnes"
   }
   OUTPUT_DF['sankey_source'] = OUTPUT_DF['bod_component'].replace(sankey_source_lookup)

   # If subopt is positive, it becomes a Source for Gmax
   rows_with_positive_subopt = ((OUTPUT_DF['bod_component'] == 'bod_efficiency_tonnes') & (OUTPUT_DF['value'] > 0))
   OUTPUT_DF.loc[rows_with_positive_subopt ,'bod_component'] = 'bod_gmax_tonnes'
   OUTPUT_DF.loc[rows_with_positive_subopt ,'sankey_source'] = 'bod_efficiency_tonnes'
   OUTPUT_DF.loc[rows_with_positive_subopt ,'value'] = OUTPUT_DF['value']

   # Sankey wants all components to be positive
   # This step must come after all other calcs!
   OUTPUT_DF['value'] = np.abs(OUTPUT_DF['value'])

   # Give BOD components pretty names
   OUTPUT_DF['bod_component'] = OUTPUT_DF['bod_component'].replace(BOD_COMP_NAMES)
   OUTPUT_DF['sankey_source'] = OUTPUT_DF['sankey_source'].replace(BOD_COMP_NAMES)

   # Define pretty column names
   rename_cols = {
      # "country":"Country"
      # ,"year":"Year"
      "bod_component":"Component"
      ,"value":"Tonnes"
      ,"sankey_source":"Component Source"
   }
   OUTPUT_DF = OUTPUT_DF.rename(columns=rename_cols)

   return OUTPUT_DF

def prep_bod_forstackedbar_poultry(INPUT_DF):
   working_df = INPUT_DF.copy()

   # Actual costs
   # Ordering here determines order in plot
   cols_actual = [
      'adjusted_feedcost_usdperkglive'   # Adjusted based on feed price slider
      ,'acc_chickcost_usdperkglive'
      ,'acc_laborcost_usdperkglive'
      ,'acc_landhousingcost_usdperkglive'
      # ,'acc_medcost_usdperkglive'
      ,'acc_othercost_usdperkglive'
   ]
   # Ideal costs
   cols_ideal = [
      'ideal_feedcost_usdperkglive'
      ,'ideal_chickcost_usdperkglive'
      ,'ideal_laborcost_usdperkglive'
      ,'ideal_landhousingcost_usdperkglive'
      # ,'ideal_medcost_usdperkglive'
      ,'ideal_othercost_usdperkglive'
   ]

   # If any costs are missing for a given country and year, fill in zero
   for COL in cols_actual + cols_ideal:
      working_df[COL] = working_df[COL].replace(np.nan ,0)

   # If actual costs are all zero, want to display a blank chart
   # In this case, set all ideal costs to zero as well
   _rows_allzero = (working_df[cols_actual].sum(axis=1) == 0)
   for COL in cols_ideal:
      working_df.loc[_rows_allzero ,COL] = 0

   # Create column for Burden of Disease as total actual minus total ideal
   working_df['bod_costs'] = working_df[cols_actual].sum(axis=1) - working_df[cols_ideal].sum(axis=1)

   # Melt actual costs into rows
   output_actual = working_df.melt(
      id_vars=['country' ,'year']
      ,value_vars=cols_actual
      ,var_name='cost_item'
      ,value_name='cost_usdperkglive'
   )
   output_actual['opt_or_act'] = 'Actual'  # Value here determines bar label in plot

   # Melt ideal costs into rows
   output_ideal = working_df.melt(
      id_vars=['country' ,'year']
      ,value_vars=cols_ideal + ['bod_costs']
      ,var_name='cost_item'
      ,value_name='cost_usdperkglive'
   )
   output_ideal['opt_or_act'] = 'Ideal + Burden of disease'  # Value here determines bar label in plot

   # Stack actual, ideal, and burden
   OUTPUT_DF = pd.concat(
      [output_actual ,output_ideal]
      ,axis=0
      ,join='outer'
      ,ignore_index=True
   )

   # Recode cost item names
   # Keys are column names
   # Values are cost items as you want them to appear in plot
   # Actual and Ideal costs should appear in pairs, except for bod_costs which only appears once
   pretty_bod_cost_names = {
      'adjusted_feedcost_usdperkglive':'Feed'
      ,'ideal_feedcost_usdperkglive':'Feed'

      ,'acc_chickcost_usdperkglive':'Chicks'
      ,'ideal_chickcost_usdperkglive':'Chicks'

      ,'acc_laborcost_usdperkglive':'Labour'
      ,'ideal_laborcost_usdperkglive':'Labour'

      ,'acc_landhousingcost_usdperkglive':'Land & Housing'
      ,'ideal_landhousingcost_usdperkglive':'Land & Housing'

      # ,'acc_medcost_usdperkglive':'Medicine'
      # ,'ideal_medcost_usdperkglive':'Medicine'

      ,'acc_othercost_usdperkglive':'Other'
      ,'ideal_othercost_usdperkglive':'Other'

      ,'bod_costs':'Burden of Disease'
   }
   OUTPUT_DF['Cost Item'] = OUTPUT_DF['cost_item'].replace(pretty_bod_cost_names)

   # Add column with labels for each segment
   OUTPUT_DF['label'] = OUTPUT_DF['Cost Item'] + ' - $' + OUTPUT_DF['cost_usdperkglive'].round(2).astype(str)

   return OUTPUT_DF

def prep_bod_forstackedbar_swine(INPUT_DF):
   working_df = INPUT_DF.copy()

   # Actual costs
   # Ordering here determines order in plot
   cols_actual = [
      'adjusted_feedcost_usdperkgcarc'    # Adjusted based on feed price slider
      ,'acc_nonfeedvariablecost_usdperkgcarc'
      ,'acc_laborcost_usdperkgcarc'
      ,'acc_landhousingcost_usdperkgcarc'
   ]
   # Ideal costs
   cols_ideal = [
      'ideal_feedcost_usdperkgcarc'   # Using feed price from slider
      ,'ideal_nonfeedvariablecost_usdperkgcarc'
      ,'ideal_laborcost_usdperkgcarc'
      ,'ideal_landhousingcost_usdperkgcarc'
   ]

   # If any costs are missing for a given country and year, fill in zero
   for COL in cols_actual + cols_ideal:
      working_df[COL] = working_df[COL].replace(np.nan ,0)

   # If actual costs are all zero, want to display a blank chart
   # In this case, set all ideal costs to zero as well
   _rows_allzero = (working_df[cols_actual].sum(axis=1) == 0)
   for COL in cols_ideal:
      working_df.loc[_rows_allzero ,COL] = 0

   # Create column for Burden of Disease as total actual minus total ideal
   working_df['bod_costs'] = working_df[cols_actual].sum(axis=1) - working_df[cols_ideal].sum(axis=1)

   # Melt actual costs into rows
   output_actual = working_df.melt(
      id_vars=['country' ,'year']
      ,value_vars=cols_actual
      ,var_name='cost_item'
      ,value_name='cost_usdperkgcarc'  # Value here determines axis label in plot
   )
   output_actual['opt_or_act'] = 'Actual'  # Value here determines bar label in plot

   # Melt ideal costs into rows
   output_ideal = working_df.melt(
      id_vars=['country' ,'year']
      ,value_vars=cols_ideal + ['bod_costs']
      ,var_name='cost_item'
      ,value_name='cost_usdperkgcarc'  # Value here determines axis label in plot
   )
   output_ideal['opt_or_act'] = 'Ideal + Burden of disease'  # Value here determines bar label in plot

   # Stack actual, ideal, and burden
   OUTPUT_DF = pd.concat(
      [output_actual ,output_ideal]
      ,axis=0
      ,join='outer'
      ,ignore_index=True
   )

   # Recode cost item names
   # Keys are column names
   # Values are cost items as you want them to appear in plot
   # Actual and Ideal costs should appear in pairs, except for bod_costs which only appears once
   pretty_bod_cost_names = {
      "adjusted_feedcost_usdperkgcarc":"Feed"
      ,"ideal_feedcost_usdperkgcarc":"Feed"

      ,"acc_nonfeedvariablecost_usdperkgcarc":"Nonfeed Variable Costs"
      ,"ideal_nonfeedvariablecost_usdperkgcarc":"Nonfeed Variable Costs"

      ,"acc_laborcost_usdperkgcarc":"Labour"
      ,"ideal_laborcost_usdperkgcarc":"Labour"

      ,"acc_landhousingcost_usdperkgcarc":"Finance"
      ,"ideal_landhousingcost_usdperkgcarc":"Finance"

      ,"bod_costs":"Burden of Disease"
   }
   OUTPUT_DF['Cost Item'] = OUTPUT_DF['cost_item'].replace(pretty_bod_cost_names)

   # Add column with labels for each segment
   OUTPUT_DF['label'] = OUTPUT_DF['Cost Item'] + ' - $' + OUTPUT_DF['cost_usdperkgcarc'].round(2).astype(str)

   return OUTPUT_DF


def prep_ahle_fortreemap_ecs(INPUT_DF):
   working_df = INPUT_DF.copy()

   # Trim the data to keep things needed for the treemap
   ecs_ahle_attr_treemap = working_df[[
       'species',
       'production_system',
       'age_group',
       'sex',
       'ahle_component',
       'cause',
       'mean',
       # 'pct_of_total'
       ]]

   # Can only have positive values
   ecs_ahle_attr_treemap['mean'] = abs(ecs_ahle_attr_treemap['mean'])

   # Replace 'overall' values with more descriptive values
   # ecs_ahle_summary_tree_pivot['age_group'] = ecs_ahle_summary_tree_pivot['age_group'].replace({'Overall': 'Overall Age'})
   ecs_ahle_attr_treemap['sex'] = ecs_ahle_attr_treemap['sex'].replace({'Overall': 'Overall Sex'})

   # Replace mortality with mortality loss
   ecs_ahle_attr_treemap['ahle_component'] = ecs_ahle_attr_treemap['ahle_component'].replace({'Mortality': 'Mortality Loss'})

   OUTPUT_DF = ecs_ahle_attr_treemap

   return OUTPUT_DF


def prep_ahle_forwaterfall_ecs(INPUT_DF):
   working_df = INPUT_DF.copy()

   # Fill missing values with 0
   working_df.fillna(0)

   # Trim the data to keep things needed for the waterfall
   ecs_ahle_waterfall = working_df[['species',
                                    'production_system',
                                    # 'age_group',
                                    # 'sex',
                                    'agesex_scenario',
                                    'item',
                                    'mean_current',
                                    'mean_ideal',
                                    'mean_mortality_zero',
                                    'mean_current_usd',
                                    'mean_ideal_usd',
                                    'mean_mortality_zero_usd',
                                    'mean_all_mort_25_imp',
                                    'mean_all_mort_50_imp',
                                    'mean_all_mort_75_imp',
                                    'mean_current_repro_25_imp',
                                    'mean_current_repro_50_imp',
                                    'mean_current_repro_75_imp',
                                    'mean_current_repro_100_imp',
                                    'mean_current_growth_25_imp_all',
                                    'mean_current_growth_50_imp_all',
                                    'mean_current_growth_75_imp_all',
                                    'mean_current_growth_100_imp_all',
                                    'mean_all_mort_25_imp_usd',
                                    'mean_all_mort_50_imp_usd',
                                    'mean_all_mort_75_imp_usd',
                                    'mean_current_repro_25_imp_usd',
                                    'mean_current_repro_50_imp_usd',
                                    'mean_current_repro_75_imp_usd',
                                    'mean_current_repro_100_imp_usd',
                                    'mean_current_growth_25_imp_all_usd',
                                    'mean_current_growth_50_imp_all_usd',
                                    'mean_current_growth_75_imp_all_usd',
                                    'mean_current_growth_100_imp_all_usd',
                                    ]]

   # Keep only items for the waterfall
   waterfall_plot_values = ('Value of Offtake',
                            'Value of Eggs consumed',
                            'Value of Eggs sold',
                            'Value of Herd Increase',
                            'Value of draught',
                            'Value of Milk',
                            'Value of Manure',
                            'Value of Hides',
                            'Feed Cost',
                            'Labour Cost',
                            'Health Cost',
                            'Infrastructure Cost',
                            'Capital Cost',
                            'Gross Margin')
   ecs_ahle_waterfall = ecs_ahle_waterfall.loc[ecs_ahle_waterfall['item'].isin(waterfall_plot_values)]

   # Make costs negative
   costs = ('Feed Cost',
            'Labour Cost',
            'Health Cost',
            'Infrastructure Cost',
            'Capital Cost')
   ecs_ahle_waterfall['mean_current'] = np.where(ecs_ahle_waterfall.item.isin(costs), ecs_ahle_waterfall['mean_current']* -1, ecs_ahle_waterfall['mean_current'])
   ecs_ahle_waterfall['mean_ideal'] = np.where(ecs_ahle_waterfall.item.isin(costs), ecs_ahle_waterfall['mean_ideal']* -1, ecs_ahle_waterfall['mean_ideal'])
   ecs_ahle_waterfall['mean_mortality_zero'] = np.where(ecs_ahle_waterfall.item.isin(costs), ecs_ahle_waterfall['mean_mortality_zero']* -1, ecs_ahle_waterfall['mean_mortality_zero'])
   ecs_ahle_waterfall['mean_current_usd'] = np.where(ecs_ahle_waterfall.item.isin(costs), ecs_ahle_waterfall['mean_current_usd']* -1, ecs_ahle_waterfall['mean_current_usd'])
   ecs_ahle_waterfall['mean_ideal_usd'] = np.where(ecs_ahle_waterfall.item.isin(costs), ecs_ahle_waterfall['mean_ideal_usd']* -1, ecs_ahle_waterfall['mean_ideal_usd'])
   ecs_ahle_waterfall['mean_mortality_zero_usd'] = np.where(ecs_ahle_waterfall.item.isin(costs), ecs_ahle_waterfall['mean_mortality_zero_usd']* -1, ecs_ahle_waterfall['mean_mortality_zero_usd'])
   ecs_ahle_waterfall['mean_all_mort_25_imp'] = np.where(ecs_ahle_waterfall.item.isin(costs), ecs_ahle_waterfall['mean_all_mort_25_imp']* -1, ecs_ahle_waterfall['mean_all_mort_25_imp'])
   ecs_ahle_waterfall['mean_all_mort_50_imp'] = np.where(ecs_ahle_waterfall.item.isin(costs), ecs_ahle_waterfall['mean_all_mort_50_imp']* -1, ecs_ahle_waterfall['mean_all_mort_50_imp'])
   ecs_ahle_waterfall['mean_all_mort_75_imp'] = np.where(ecs_ahle_waterfall.item.isin(costs), ecs_ahle_waterfall['mean_all_mort_75_imp']* -1, ecs_ahle_waterfall['mean_all_mort_75_imp'])
   ecs_ahle_waterfall['mean_current_repro_25_imp'] = np.where(ecs_ahle_waterfall.item.isin(costs), ecs_ahle_waterfall['mean_current_repro_25_imp']* -1, ecs_ahle_waterfall['mean_current_repro_25_imp'])
   ecs_ahle_waterfall['mean_current_repro_50_imp'] = np.where(ecs_ahle_waterfall.item.isin(costs), ecs_ahle_waterfall['mean_current_repro_50_imp']* -1, ecs_ahle_waterfall['mean_current_repro_50_imp'])
   ecs_ahle_waterfall['mean_current_repro_75_imp'] = np.where(ecs_ahle_waterfall.item.isin(costs), ecs_ahle_waterfall['mean_current_repro_75_imp']* -1, ecs_ahle_waterfall['mean_current_repro_75_imp'])
   ecs_ahle_waterfall['mean_current_repro_100_imp'] = np.where(ecs_ahle_waterfall.item.isin(costs), ecs_ahle_waterfall['mean_current_repro_100_imp']* -1, ecs_ahle_waterfall['mean_current_repro_100_imp'])
   ecs_ahle_waterfall['mean_current_growth_25_imp_all'] = np.where(ecs_ahle_waterfall.item.isin(costs), ecs_ahle_waterfall['mean_current_growth_25_imp_all']* -1, ecs_ahle_waterfall['mean_current_growth_25_imp_all'])
   ecs_ahle_waterfall['mean_current_growth_50_imp_all'] = np.where(ecs_ahle_waterfall.item.isin(costs), ecs_ahle_waterfall['mean_current_growth_50_imp_all']* -1, ecs_ahle_waterfall['mean_current_growth_50_imp_all'])
   ecs_ahle_waterfall['mean_current_growth_75_imp_all'] = np.where(ecs_ahle_waterfall.item.isin(costs), ecs_ahle_waterfall['mean_current_growth_75_imp_all']* -1, ecs_ahle_waterfall['mean_current_growth_75_imp_all'])
   ecs_ahle_waterfall['mean_current_growth_100_imp_all'] = np.where(ecs_ahle_waterfall.item.isin(costs), ecs_ahle_waterfall['mean_current_growth_100_imp_all']* -1, ecs_ahle_waterfall['mean_current_growth_100_imp_all'])
   ecs_ahle_waterfall['mean_all_mort_25_imp_usd'] = np.where(ecs_ahle_waterfall.item.isin(costs), ecs_ahle_waterfall['mean_all_mort_25_imp_usd']* -1, ecs_ahle_waterfall['mean_all_mort_25_imp_usd'])
   ecs_ahle_waterfall['mean_all_mort_50_imp_usd'] = np.where(ecs_ahle_waterfall.item.isin(costs), ecs_ahle_waterfall['mean_all_mort_50_imp_usd']* -1, ecs_ahle_waterfall['mean_all_mort_50_imp_usd'])
   ecs_ahle_waterfall['mean_all_mort_75_imp_usd'] = np.where(ecs_ahle_waterfall.item.isin(costs), ecs_ahle_waterfall['mean_all_mort_75_imp_usd']* -1, ecs_ahle_waterfall['mean_all_mort_75_imp_usd'])
   ecs_ahle_waterfall['mean_current_repro_25_imp_usd'] = np.where(ecs_ahle_waterfall.item.isin(costs), ecs_ahle_waterfall['mean_current_repro_25_imp_usd']* -1, ecs_ahle_waterfall['mean_current_repro_25_imp_usd'])
   ecs_ahle_waterfall['mean_current_repro_50_imp_usd'] = np.where(ecs_ahle_waterfall.item.isin(costs), ecs_ahle_waterfall['mean_current_repro_50_imp_usd']* -1, ecs_ahle_waterfall['mean_current_repro_50_imp_usd'])
   ecs_ahle_waterfall['mean_current_repro_75_imp_usd'] = np.where(ecs_ahle_waterfall.item.isin(costs), ecs_ahle_waterfall['mean_current_repro_75_imp_usd']* -1, ecs_ahle_waterfall['mean_current_repro_75_imp_usd'])
   ecs_ahle_waterfall['mean_current_repro_100_imp_usd'] = np.where(ecs_ahle_waterfall.item.isin(costs), ecs_ahle_waterfall['mean_current_repro_100_imp_usd']* -1, ecs_ahle_waterfall['mean_current_repro_100_imp_usd'])
   ecs_ahle_waterfall['mean_current_growth_25_imp_all_usd'] = np.where(ecs_ahle_waterfall.item.isin(costs), ecs_ahle_waterfall['mean_current_growth_25_imp_all_usd']* -1, ecs_ahle_waterfall['mean_current_growth_25_imp_all_usd'])
   ecs_ahle_waterfall['mean_current_growth_50_imp_all_usd'] = np.where(ecs_ahle_waterfall.item.isin(costs), ecs_ahle_waterfall['mean_current_growth_50_imp_all_usd']* -1, ecs_ahle_waterfall['mean_current_growth_50_imp_all_usd'])
   ecs_ahle_waterfall['mean_current_growth_75_imp_all_usd'] = np.where(ecs_ahle_waterfall.item.isin(costs), ecs_ahle_waterfall['mean_current_growth_75_imp_all_usd']* -1, ecs_ahle_waterfall['mean_current_growth_75_imp_all_usd'])
   ecs_ahle_waterfall['mean_current_growth_100_imp_all_usd'] = np.where(ecs_ahle_waterfall.item.isin(costs), ecs_ahle_waterfall['mean_current_growth_100_imp_all_usd']* -1, ecs_ahle_waterfall['mean_current_growth_100_imp_all_usd'])


   # Sort Item column to keep values and costs together
   ecs_ahle_waterfall['item'] = ecs_ahle_waterfall['item'].astype('category')
   ecs_ahle_waterfall.item.cat.set_categories(waterfall_plot_values, inplace=True)
   ecs_ahle_waterfall = ecs_ahle_waterfall.sort_values(["item"])

   # Rename costs values to be more descriptive
   ecs_ahle_waterfall['item'] = ecs_ahle_waterfall['item'].replace({'Feed Cost': 'Expenditure on Feed',
                                                                    'Labour Cost': 'Expenditure on Labour',
                                                                    'Health Cost': 'Expenditure on Health',
                                                                    'Infrastructure Cost': 'Expenditure on Housing',
                                                                    'Capital Cost': 'Expenditure on Capital',
                                                                    'Value of draught': 'Value of Draught'})

   # Create AHLE difference columns
   ecs_ahle_waterfall['mean_AHLE'] = ecs_ahle_waterfall['mean_ideal'] - ecs_ahle_waterfall['mean_current']
   ecs_ahle_waterfall['mean_AHLE_mortality'] = ecs_ahle_waterfall['mean_mortality_zero'] - ecs_ahle_waterfall['mean_current']
   ecs_ahle_waterfall['mean_AHLE_usd'] = ecs_ahle_waterfall['mean_ideal_usd'] - ecs_ahle_waterfall['mean_current_usd']
   ecs_ahle_waterfall['mean_AHLE_mortality_usd'] = ecs_ahle_waterfall['mean_mortality_zero_usd'] - ecs_ahle_waterfall['mean_current_usd']
   # For Mortality
   ecs_ahle_waterfall['mean_all_mort_25_AHLE'] = ecs_ahle_waterfall['mean_all_mort_25_imp'] - ecs_ahle_waterfall['mean_current']
   ecs_ahle_waterfall['mean_all_mort_50_AHLE'] = ecs_ahle_waterfall['mean_all_mort_50_imp'] - ecs_ahle_waterfall['mean_current']
   ecs_ahle_waterfall['mean_all_mort_75_AHLE'] = ecs_ahle_waterfall['mean_all_mort_75_imp'] - ecs_ahle_waterfall['mean_current']
   ecs_ahle_waterfall['mean_all_mort_25_AHLE_usd'] = ecs_ahle_waterfall['mean_all_mort_25_imp_usd'] - ecs_ahle_waterfall['mean_current']
   ecs_ahle_waterfall['mean_all_mort_50_AHLE_usd'] = ecs_ahle_waterfall['mean_all_mort_50_imp_usd'] - ecs_ahle_waterfall['mean_current']
   ecs_ahle_waterfall['mean_all_mort_75_AHLE_usd'] = ecs_ahle_waterfall['mean_all_mort_75_imp_usd'] - ecs_ahle_waterfall['mean_current']
   # For Parturition
   ecs_ahle_waterfall['mean_all_current_repro_25_AHLE'] = ecs_ahle_waterfall['mean_current_repro_25_imp'] - ecs_ahle_waterfall['mean_current']
   ecs_ahle_waterfall['mean_all_current_repro_50_AHLE'] = ecs_ahle_waterfall['mean_current_repro_50_imp'] - ecs_ahle_waterfall['mean_current']
   ecs_ahle_waterfall['mean_all_current_repro_75_AHLE'] = ecs_ahle_waterfall['mean_current_repro_75_imp'] - ecs_ahle_waterfall['mean_current']
   ecs_ahle_waterfall['mean_all_current_repro_100_AHLE'] = ecs_ahle_waterfall['mean_current_repro_100_imp'] - ecs_ahle_waterfall['mean_current']
   ecs_ahle_waterfall['mean_all_current_repro_25_AHLE_usd'] = ecs_ahle_waterfall['mean_current_repro_25_imp_usd'] - ecs_ahle_waterfall['mean_current']
   ecs_ahle_waterfall['mean_all_current_repro_50_AHLE_usd'] = ecs_ahle_waterfall['mean_current_repro_50_imp_usd'] - ecs_ahle_waterfall['mean_current']
   ecs_ahle_waterfall['mean_all_current_repro_75_AHLE_usd'] = ecs_ahle_waterfall['mean_current_repro_75_imp_usd'] - ecs_ahle_waterfall['mean_current']
   ecs_ahle_waterfall['mean_all_current_repro_100_AHLE_usd'] = ecs_ahle_waterfall['mean_current_repro_100_imp_usd'] - ecs_ahle_waterfall['mean_current']
   # For Live Weight
   ecs_ahle_waterfall['mean_all_current_growth_25_AHLE'] = ecs_ahle_waterfall['mean_current_growth_25_imp_all'] - ecs_ahle_waterfall['mean_current']
   ecs_ahle_waterfall['mean_all_current_growth_50_AHLE'] = ecs_ahle_waterfall['mean_current_growth_50_imp_all'] - ecs_ahle_waterfall['mean_current']
   ecs_ahle_waterfall['mean_all_current_growth_75_AHLE'] = ecs_ahle_waterfall['mean_current_growth_75_imp_all'] - ecs_ahle_waterfall['mean_current']
   ecs_ahle_waterfall['mean_all_current_growth_100_AHLE'] = ecs_ahle_waterfall['mean_current_growth_100_imp_all'] - ecs_ahle_waterfall['mean_current']
   ecs_ahle_waterfall['mean_all_current_growth_25_AHLE_usd'] = ecs_ahle_waterfall['mean_current_growth_25_imp_all_usd'] - ecs_ahle_waterfall['mean_current']
   ecs_ahle_waterfall['mean_all_current_growth_50_AHLE_usd'] = ecs_ahle_waterfall['mean_current_growth_50_imp_all_usd'] - ecs_ahle_waterfall['mean_current']
   ecs_ahle_waterfall['mean_all_current_growth_75_AHLE_usd'] = ecs_ahle_waterfall['mean_current_growth_75_imp_all_usd'] - ecs_ahle_waterfall['mean_current']
   ecs_ahle_waterfall['mean_all_current_growth_100_AHLE_usd'] = ecs_ahle_waterfall['mean_current_growth_100_imp_all_usd'] - ecs_ahle_waterfall['mean_current']

   OUTPUT_DF = ecs_ahle_waterfall

   return OUTPUT_DF

def prep_ahle_forwaterfall_ga(INPUT_DF):
    # Ordering of current values dictionary determines order in plot
    current_values_labels = {
        'biomass_value_2010usd':'Biomass'
        ,'output_value_meat_2010usd':'Meat'
        ,'output_value_eggs_2010usd':'Eggs'
        ,'output_value_milk_2010usd':'Milk'
        ,'output_value_wool_2010usd':'Wool'

        ,'vetspend_farm_usd':'Producers vet & med costs'
        ,'vetspend_public_usd':'Public vet & med costs'

        ,'net_value_2010usd':'Net value'
    }
    current_value_columns = list(current_values_labels)
    ideal_values_labels = {
        'ideal_biomass_value_2010usd':'Biomass'
        ,'ideal_output_value_meat_2010usd':'Meat'
        ,'ideal_output_value_eggs_2010usd':'Eggs'
        ,'ideal_output_value_milk_2010usd':'Milk'
        ,'ideal_output_value_wool_2010usd':'Wool'
        ,'ideal_output_plus_biomass_value_2010usd':'Net value'
    }
    ideal_value_columns = list(ideal_values_labels)

    # Sum to country-year level (summing over species)
    country_year_level = INPUT_DF.pivot_table(
        index=['region','country' ,'year' ,'incomegroup']
        ,observed=True  # Limit to combinations of index variables that are in data
        ,values=current_value_columns + ideal_value_columns
        ,aggfunc='sum'
        ,fill_value=0
        )
    country_year_level = country_year_level.reset_index()     # Pivoting will change columns to indexes. Change them back.

    # Restructure to create columns 'current_value' and 'ideal_value'
    # Keys: Country, Species, Year.  Columns: Income group, Item.
    # Current values
    values_current = country_year_level.melt(
        id_vars=['region','country' ,'year' ,'incomegroup']
        ,value_vars=current_value_columns
        ,var_name='orig_col'             # Name for new "variable" column
        ,value_name='value_usd_current'              # Name for new "value" column
        )
    values_current['item'] = values_current['orig_col'].apply(ga.lookup_from_dictionary ,DICT=current_values_labels)
    del values_current['orig_col']

    # Ideal values
    values_ideal = country_year_level.melt(
        id_vars=['region','country' ,'year' ,'incomegroup']
        ,value_vars=ideal_value_columns
        ,var_name='orig_col'             # Name for new "variable" column
        ,value_name='value_usd_ideal'              # Name for new "value" column
        )
    values_ideal['item'] = values_ideal['orig_col'].apply(ga.lookup_from_dictionary ,DICT=ideal_values_labels)
    del values_ideal['orig_col']

    # Merge current and ideal
    values_combined = pd.merge(
        left=values_current
        ,right=values_ideal
        ,on=['region','country' ,'year' ,'incomegroup' ,'item']
        ,how='outer'
    )

    # Sort Item column to keep values and costs together
    # Sort order is same as current values dictionary defined above
    items_plotorder = list(current_values_labels.values())
    values_combined['item'] = values_combined['item'].astype('category')
    values_combined.item.cat.set_categories(items_plotorder, inplace=True)
    values_combined = values_combined.sort_values(['item'])

    # Fill in zeros for ideal vetmed costs
    _vetmed_rows = (values_combined['item'].str.contains('VET' ,case=False))
    values_combined.loc[_vetmed_rows ,'value_usd_ideal'] = 0

    OUTPUT_DF = values_combined

    return OUTPUT_DF

def prep_ahle_forstackedbar_ecs(INPUT_DF, cols_birr_costs, cols_usd_costs, pretty_ahle_cost_names):
   working_df = INPUT_DF.copy()

   # Birr costs
   # Ordering here determines order in plot
   cols_birr_costs = cols_birr_costs

   # USD costs
   cols_usd_costs = cols_usd_costs

   # If any costs are missing, fill in zero
   for COL in cols_birr_costs + cols_usd_costs:
      working_df[COL] = working_df[COL].replace(np.nan ,0)

   # Melt birr costs into rows
   output_birr = working_df.melt(
      id_vars=['species' ,'production_system']
      ,value_vars=cols_birr_costs
      ,var_name='ahle_due_to'
      ,value_name='cost_birr'
   )
   # output_actual['opt_or_act'] = 'Actual'  # Value here determines bar label in plot

   # Melt usd costs into rows
   output_usd = working_df.melt(
      id_vars=['species' ,'production_system']
      ,value_vars=cols_usd_costs
      ,var_name='ahle_due_to'
      ,value_name='cost_usd'
   )
   # output_ideal['opt_or_act'] = 'Ideal + Burden of disease'  # Value here determines bar label in plot

   # Stack
   OUTPUT_DF = pd.concat(
      [output_birr ,output_usd]
      ,axis=0
      ,join='outer'
      ,ignore_index=True
   )

   # Recode cost item names
   pretty_ahle_cost_names = pretty_ahle_cost_names
   OUTPUT_DF['AHLE Due To'] = OUTPUT_DF['ahle_due_to'].replace(pretty_ahle_cost_names)

   # Create new string column for label
   OUTPUT_DF['Age_group_string'] = OUTPUT_DF['ahle_due_to'].str.slice(10,12)
   OUTPUT_DF['Age_group_string'] = OUTPUT_DF['Age_group_string'].str.upper()

   # Add column with labels for each segment
   OUTPUT_DF['label_birr'] = OUTPUT_DF['Age_group_string'] + ' - ' + OUTPUT_DF['cost_birr'].map('{:,.0f}'.format).astype(str) + ' Birr'
   OUTPUT_DF['label_usd'] = OUTPUT_DF['Age_group_string'] + ' - ' + OUTPUT_DF['cost_usd'].map('{:,.0f}'.format).astype(str) + ' USD'


   return OUTPUT_DF


# =============================================================================
#### Define the figures
# =============================================================================
# Define the Waterfall
def create_waterfall(x, y, text):
     waterfall_fig = go.Figure(go.Waterfall(
        name = "20",
        orientation = "v",

        measure = ["relative", "relative", "relative", "relative", "total"],  # This needs to change with number of columns in waterfalll
        x=x,
        y=y,
		hoverinfo = 'none',  # Disable the hover over tooltip
        text=text,
        textposition = ["outside","outside","auto","auto","outside"],
        decreasing = {'marker':{"color":'#F7931D'}},
        increasing = {'marker':{"color":'#3598DB'}},
        totals = {'marker':{"color":'#5BC0DE'}},
        connector = {"line":{"color":"darkgrey"}}#"rgb(63, 63, 63)"}},
        ))

     waterfall_fig.update_layout(clickmode='event+select', ### EVENT SELECT ??????
                                 plot_bgcolor="#ededed")
     waterfall_fig.update_xaxes(
         fixedrange=True
         )
     waterfall_fig.update_yaxes(
         fixedrange=True
         )

     return waterfall_fig

# Define the Sankey
def create_sankey(label_list, color, x, y, source, target, values, n):
    sankey_fig = go.Figure(data=go.Sankey(
        textfont = dict(size=15),
        arrangement = 'fixed',
        hoverinfo = 'none',  # Disable the hover over tooltip
        valueformat = ",.0f",
        node = dict(
            pad = 25,
            thickness = 15,
            line = dict(color = "black", width = 0.5),
            label = label_list,
            x = x,
            y = y,
            color = color
            ),
        link = dict(
            source = source,
            target = target,
            value = values,
            color = ['#ededed']*n),
        ))
    return sankey_fig

# Define the stacked bar
def create_stacked_bar_poultry(input_df, x, y, color):
    bar_fig = px.bar(
       input_df,
       x=x,
       y=y,
       color=color,
       # Keys in color map must match values assigned in pretty_bod_cost_names
       color_discrete_map={
          "Feed":"#2A80B9",
          "Chicks":"#9B58B5",
          "Labour":"#F1C40F",
          "Land & Housing":"#2DCC70",
          "Medicine":"#7A7A7A",
          "Other":"#7A7A7A",
          "Burden of Disease":"#F7931D",
          },
       text='label'
       )
    bar_fig.update_layout(
       plot_bgcolor="#ededed",
       hovermode=False,
       showlegend=True,
       xaxis_title=None,
       yaxis_title='Cost per kg live weight',
       yaxis_tickformat = "$.2f"
       )
    bar_fig.update_xaxes(
        fixedrange=True
        )
    bar_fig.update_yaxes(
        fixedrange=True
        )
    return bar_fig

def create_stacked_bar_swine(input_df, x, y, color):
    bar_fig = px.bar(
       input_df,
       x=x,
       y=y,
       color=color,
       # Keys in color map must match values assigned in pretty_bod_cost_names
       color_discrete_map={
          "Feed":"#2A80B9",
          "Nonfeed Variable Costs":"#9B58B5",
          "Labour":"#F1C40F",
          "Finance":"#2DCC70",
          "Burden of Disease":"#F7931D",
          },
       text='label'
       )
    bar_fig.update_layout(
       plot_bgcolor="#ededed",
       hovermode=False,
       showlegend=True,
       xaxis_title=None,
       yaxis_title='Cost per kg carcass weight',
       yaxis_tickformat = "$.2f"
       )
    bar_fig.update_xaxes(
        fixedrange=True
        )
    bar_fig.update_yaxes(
        fixedrange=True
        )
    return bar_fig

# Define the attribution treemap
def create_attr_treemap_ecs(input_df, path):
    # # Make mean more legible
    # input_df["humanize_mean"]= input_df['mean'].apply(lambda x: humanize.intword(x))

    # input_df["pct_of_total"]= input_df['pct_of_total'].astype('float')


    treemap_fig = px.treemap(input_df,
                      # path=[
                      #    'cause',
                      #    'production_system',
                      #    'age_group',
                      #    'sex',
                      #    'ahle_component',
                      #    ],
                      path = path,
                      values='mean',
                      # hover_data=['pct_of_total'],
                      # custom_data=['pct_of_total'],
                      color='cause', # cause only applys to the cause level
                      color_discrete_map={'(?)':'lightgrey','Infectious':'#68000D', 'Non-infectious':'#08316C', 'External':'#00441B'} # Cause colors matches the Human health dashboard
                      )

    return treemap_fig

# Define the AHLE waterfall
def create_ahle_waterfall_ecs(input_df, name, measure, x, y):
    waterfall_fig = go.Figure(go.Waterfall(
        name = name,
        orientation = "v",
        measure = measure,  # This needs to change with number of columns in waterfalll
        x=x,
        y=y,
        decreasing = {'marker':{"color":'#E84C3D'}},
        increasing = {'marker':{"color":'#3598DB'}},
        totals = {'marker':{"color":'#F7931D'}},
        connector = {"line":{"color":"darkgrey"}},
        customdata=y,
        ))

    waterfall_fig.update_layout(clickmode='event+select', ### EVENT SELECT ??????
                                plot_bgcolor="#ededed",)

    waterfall_fig.add_annotation(x=4, xref='x',         # x position is absolute on axis
                                 y=0, yref='paper',     # y position is relative [0,1] to work regardless of scale
                                 text="Source: GBADs",
                                 showarrow=False,
                                 yshift=10,
                                 font=dict(
                                     family="Helvetica",
                                     size=18,
                                     color="black"
                                     )
                                 )
    waterfall_fig.update_xaxes(
        fixedrange=True
        )
    waterfall_fig.update_yaxes(
        fixedrange=True
        )

    return waterfall_fig

# Define the stacked bar
def create_stacked_bar_ecs(input_df, x, y, text, color, yaxis_title):
    bar_fig = px.bar(
        input_df,
        x=x,
        y=y,
        text = text,
        color=color,
        color_discrete_map={
          "Neonatal male":"#2A80B9",
          "Neonatal":"#2A80B9",
          "Neonatal female":"#6eb1de",
          "Juvenile male":"#9B58B5",
          "Juvenile":"#9B58B5",
          "Juvenile female":"#caa6d8",
          "Adult male":"#2DCC70",
          "Adult female":"#82e3aa",
          })
    bar_fig.update_layout(
        plot_bgcolor="#ededed",
        hovermode=False,
        showlegend=True,
        xaxis_title=None,
        yaxis_title=yaxis_title,
        )
    bar_fig.update_xaxes(
        fixedrange=True
        )
    bar_fig.update_yaxes(
        fixedrange=True
        )
    return bar_fig


# Define the Biomass map
def create_biomass_map_ga(input_df, iso_alpha3, value, country, display):
    biomass_map_fig = px.choropleth(input_df, locations=iso_alpha3,
                                    color=value,
                                    hover_name=country, # column to add to hover information
                                    animation_frame="year",
                                    color_continuous_scale=px.colors.sequential.Plasma)
    biomass_map_fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='equirectangular',
            ),
        coloraxis_colorbar=dict(
            title=f"{display}",
            ),
        )

    biomass_map_fig.add_annotation(x=0.50, xref='paper',         # x position is absolute on axis
                                  y=0.05, yref='paper',     # y position is relative [0,1] to work regardless of scale
                                  text="Source: GBADs",
                                  showarrow=False,
                                  font=dict(
                                      family="Helvetica",
                                      size=18,
                                      color="black"
                                      )
                                  )

    # Rename the animation frame
    biomass_map_fig.update_layout(sliders=[{"currentvalue": {"prefix": "Year="}}])
    
    # #######
    # # Trying with go.Choroplethmapbox
    # #######
    # from urllib.request import urlopen
    # import json
    # with urlopen('https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson') as response:
    #     countries = json.load(response)
    
    # biomass_map_fig = go.Figure(go.Choroplethmapbox(geojson=countries, 
    #                                                 featureidkey='properties.ISO_A3',
    #                                       locations=iso_alpha3,
    #                                       z=value,
    #                                       text=country, # column to add to hover information
    #                                       # animation_frame="year",
    #                                       colorscale="Viridis",
    #                                       ))

    # # biomass_map_fig = go.Figure(go.Choroplethmapbox(geojson=counties, locations=df.fips, z=df.unemp,
    # #                                     colorscale="Viridis", zmin=0, zmax=12,
    # #                                     marker_opacity=0.5, marker_line_width=0))
    
    # biomass_map_fig.update_layout(mapbox_style="carto-positron",
    #                               margin={"r":0,"t":0,"l":0,"b":0})


    return biomass_map_fig

# Define the biomass, pop, livewt line chart
# def create_line_chart_ga(input_df, year, biomass, population, liveweight, country):
def create_line_chart_ga(input_df, year, value, country, facet):
    bio_pop_live_line_fig = px.line(input_df, x=year,
                                    y=value,
                                    color=country,
                                    facet_row=facet,
                                    )

    bio_pop_live_line_fig.update_yaxes(matches=None, showticklabels=True)

    # Update yaxis properties
    bio_pop_live_line_fig.update_yaxes(title_text="Biomass (kg)", row=3, col=1)
    bio_pop_live_line_fig.update_yaxes(title_text="Population (head)", row=2, col=1)
    bio_pop_live_line_fig.update_yaxes(title_text="Live Weight (kg)", row=1, col=1)

    # Remove facet titles
    bio_pop_live_line_fig.for_each_annotation(lambda a: a.update(text=a.text.replace("facet=biomass", "")))
    bio_pop_live_line_fig.for_each_annotation(lambda a: a.update(text=a.text.replace("facet=population", "")))
    bio_pop_live_line_fig.for_each_annotation(lambda a: a.update(text=a.text.replace("facet=liveweight", "")))


    bio_pop_live_line_fig.update_layout(
    title="Biomass, Population, and Live Weight Over Time <br><sup> Double click country in legend to isolate</sup>",
    xaxis_title="Year",
    legend_title="Country",
    plot_bgcolor="#ededed",
    )

    return bio_pop_live_line_fig

def create_ahle_waterfall_ga(input_df, name, measure, x, y):
    waterfall_fig = go.Figure(go.Waterfall(
        name = name,
        orientation = "v",
        measure = measure,  # This needs to change with number of columns in waterfalll
        x=x,
        y=y,
        # text=text,
        # hoverinfo = 'none',
        # textposition = ["outside","outside","auto","auto","outside"],
        decreasing = {'marker':{"color":'#E84C3D'}},
        increasing = {'marker':{"color":'#3598DB'}},
        totals = {'marker':{"color":'#F7931D'}},
        connector = {"line":{"color":"darkgrey"}}#"rgb(63, 63, 63)"}},
        ))

    waterfall_fig.update_layout(clickmode='event+select', ### EVENT SELECT ??????
                                plot_bgcolor="#ededed",)

    waterfall_fig.add_annotation(x=4, xref='x',         # x position is absolute on axis
                                 y=0, yref='paper',     # y position is relative [0,1] to work regardless of scale
                                 text="Source: GBADs",
                                 showarrow=False,
                                 yshift=10,
                                 font=dict(
                                     family="Helvetica",
                                     size=18,
                                     color="black"
                                     )
                                 )

    return waterfall_fig

#%% 4. LAYOUT
##################################################################################################
# Here we layout the webpage, including dcc (Dash Core Component) controls we want to use, such as dropdowns.
##################################################################################################
gbadsDash.layout = html.Div([

    #### BRANDING & HEADING
    dbc.Row([
        # GBADs Branding
        dbc.Col(html.Div([
            html.A(href="https://animalhealthmetrics.org/",
            children=[
                html.Img(alt="Link to GBADS site",src='/assets/GBADs-LOGO-Black-sm.png')
            ],),
                html.H3("Inclusiveness Challenge Delivery Rigour Transparency",
                        style={"font-style": "italic",
                               "margin": "0",
                               "padding": "0"})
                ], style = {'margin-left':"10px",
                            "margin-bottom":"10px",
                            'margin-right':"10px"},
        )),
    ], justify='between'),


    #### Data to pass between callbacks
    dcc.Store(id='core-data-poultry'),
    dcc.Store(id='core-data-swine'),
    dcc.Store(id='core-data-attr-ecs'),
    # dcc.Store(id='core-data-ahle-ecs'),
    dcc.Store(id='core-data-world-ahle'),
    # dcc.Store(id='core-data-world-ahle-abt-ga'),

    #### TABS
    dcc.Tabs([

        #### GLOBAL OVERVIEW TAB
        dcc.Tab(label="Global Overview [WIP]", children = [

            #### -- COUNTRY AND SPECIES CONTROLS
            dbc.Row([
                # Region-country alignment
                dbc.Col([
                    html.H6('Region-country alignment'),
                    dcc.RadioItems(id='Region-country-alignment-overview-ga',
                                    options=region_structure_options_ga,
                                    inputStyle={"margin-right": "10px", # This pulls the words off of the button
                                                "margin-left":"20px"},
                                    value="World Bank",
                                    style={"margin-left":'-20px'})
                    ],
                    style={
                            "margin-top":"10px",
                            "margin-right":"70px",
                            }

                    ),
                # Region
                dbc.Col([
                    html.H6("Region"),
                    dcc.Dropdown(id='select-region-overview-ga',
                                  options=wb_region_options_ga,
                                  value='All',
                                  clearable = False,
                                  ),
                    ],style={
                              "margin-top":"10px",
                              },
                    ),

                # Income Group
                dbc.Col([
                    html.H6("Income Group"),
                    dcc.Dropdown(id='select-incomegrp-overview-ga',
                                 options=incomegrp_options_ga,
                                 value='All',
                                 clearable = False,
                                 ),
                    ],style={
                              "margin-top":"10px",
                              },
                    ),

                # Country
                dbc.Col([
                    html.H6("Country"),
                    dcc.Dropdown(id='select-country-overview-ga',
                                  options=country_options_ga,
                                  # value='All',
                                  value='Ethiopia', #!!! - for testing
                                  clearable = False,
                                  ),
                    ],style={
                              "margin-top":"10px",
                              },
                    ),

                  # Species
                  dbc.Col([
                      html.H6("Species"),
                      dcc.Dropdown(id='select-species-ga',
                                  options=ga_species_options,
                                  value='Cattle',
                                  clearable = False,
                                  )
                      ],style={
                              "margin-top":"10px",
                              },
                      ),

                ], justify='evenly', style={"margin-right": "10px"}),


            #### -- VISUALIZATION SWITCH
            # Select Visual Control

            dbc.Card([
                dbc.CardBody([
                    html.H5("Select Visualization",
                            className="card-title",
                            style={"font-weight": "bold"}),

            dbc.Row([ # Row with Control for Visuals

                    # Visualization
                    dbc.Col([
                        html.H6("Visualize"),
                        dcc.RadioItems(
                            id='viz-radio-ga',
                            options=['Map', 'Line chart'],
                            value='Map',
                            inputStyle={"margin-right": "2px", # This pulls the words off of the button
                                        "margin-left": "10px"},
                            ),
                        ]),

                    # Map Display options
                    dbc.Col([
                        html.H6("Map Display"),
                        # dcc.RadioItems(
                        dcc.Dropdown(
                            id='map-display-radio-ga',
                            options=map_display_options_ga,
                            value='Population',
                            # inputStyle={"margin-right": "2px", # This pulls the words off of the button
                            #             "margin-left": "10px"},
                            ),
                        ]),

            ]), # END OF ROW

                # END OF CARD BODY
                ]),

            ], color='#F2F2F2', style={"margin-right": "10px"}), # END OF CARD


            html.Hr(style={'margin-right':'10px',}),

            html.Br(),

            #### -- GRAPHICS
            dbc.Row([  # Row with GRAPHICS

                dbc.Col([ # Global Aggregation Visual
                    dbc.Spinner(children=[
                    dcc.Graph(id='ga-map-or-line-select',
                                style = {"height":"650px"},
                              config = {
                                  "displayModeBar" : True,
                                  "displaylogo": False,
                                  'toImageButtonOptions': {
                                      'format': 'png', # one of png, svg, jpeg, webp
                                      'filename': 'GBADs_Global_Agg_Viz'
                                      },
                                  }
                              )
                    # End of Spinner
                    ],size="md", color="#393375", fullscreen=False),
                    # End of Map
                    ]),

            html.Br(),
            # END OF GRAPHICS ROW
            ],),

        #### -- DATATABLE
        dbc.Row([

            dbc.Spinner(children=[
            dbc.Col([
                html.Div([  # Core data for AHLE
                      html.Div( id='ga-world-abt-datatable'),
                ], style={'margin-left':"20px"}),

            html.Br() # Spacer for bottom of page

            ]),# END OF COL
            # End of Spinner
            ],size="md", color="#393375", fullscreen=False),

        ]),
        html.Br(),
        ### END OF DATATABLE


        ### END OF GLOBAL AGGREGATE TAB
        ], style=global_tab_style, selected_style=global_tab_selected_style),

        #### GLOBAL AHLE DETAILS TAB
        dcc.Tab(label="Global AHLE Details [WIP]", children = [

            #### -- COUNTRY AND CHART CONTROLS
            dbc.Row([
                # Display
                dbc.Col([
                    html.H6("Display"),
                    dcc.RadioItems(id='select-display-ga',
                                  options=ecs_display_options,
                                  value='Difference (AHLE)',
                                  labelStyle={'display': 'block'},
                                  inputStyle={"margin-right": "2px"}, # This pulls the words off of the button
                                  ),
                    ],
                    style={
                            "margin-top":"10px",
                            "margin-right":"70px",
                            }
                ),

                # Region-country alignment
                dbc.Col([
                    html.H6('Region-country alignment'),
                    dcc.RadioItems(id='Region-country-alignment-detail-ga',
                                    options=region_structure_options_ga,
                                    inputStyle={"margin-right": "10px", # This pulls the words off of the button
                                                "margin-left":"20px"},
                                    value="World Bank",
                                    style={"margin-left":'-20px'})
                    ],
                    style={
                            "margin-top":"10px",
                            "margin-right":"70px",
                            }

                    ),
                # Region
                dbc.Col([
                    html.H6("Region"),
                    dcc.Dropdown(id='select-region-detail-ga',
                                  options=wb_region_options_ga,
                                  value='All',
                                  clearable = False,
                                  ),
                    ],style={
                              "margin-top":"10px",
                              },
                    ),
                # Income Group
                dbc.Col([
                    html.H6("Income Group"),
                    dcc.Dropdown(id='select-incomegrp-detail-ga',
                                options=incomegrp_options_ga,
                                value='All',
                                clearable = False,
                                ),
                    ],style={
                              "margin-top":"10px",
                              },
                    ),

                # Country
                dbc.Col([
                    html.H6("Country"),
                    dcc.Dropdown(id='select-country-detail-ga',
                                  options=country_options_ga,
                                  value='All',
                                  clearable = False,
                                  ),
                    ],style={
                              "margin-top":"10px",
                              },
                    ),
                ], style={"margin-right": "10px"}), # END OF ROW


            #### -- CHART SPECIFIC AND BOTH CONTROLS
            dbc.Row([
                # AHLE Specific Controls
                dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Output Values and Costs Graph Controls",
                                className="card-title",
                                style={"font-weight": "bold"}),
                        dbc.Row([
                        # Year
                        dbc.Col([
                            html.H6("Year"),
                            dcc.Dropdown(id='select-year-ga',
                                          options=year_options_ga,
                                          value=2020,
                                          clearable = False,
                                          ),
                            ],style={
                                      "margin-top":"10px",
                                      },
                            ),
                        ]), # END OF ROW

                # END OF CARD BODY
                ],),

                # END OF CARD
                ], color='#F2F2F2',),
                ],  width=3),

                    #### -- MORTALITY AND OTHER CONTROLS
                    dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Exploring Contributions to AHLE (Not Active)",
                                    className="card-title",
                                    style={"font-weight": "bold"}),
                    dbc.Row([  # Line up all the controls in the same row.

                        # Base mortality rate
                        dbc.Col([
                            html.H6("Base mortality rate"),
                            html.Br(),
                            daq.Slider(
                                id='base-mortality-rate-ga',
                                min=1,
                                max=10,
                                handleLabel={"showCurrentValue": True,"label": "%"},
                                step=1,
                                value=mortality_rate_ga_default,
                                ),
                            ],style={
                                      "margin-top":"10px",
                                      }
                            ,),

                        # Base morbidity rate
                        dbc.Col([
                            html.H6("Base morbidity rate"),
                            html.Br(),
                            daq.Slider(
                                id='base-morbidity-rate-ga',
                                min=1,
                                max=10,
                                handleLabel={"showCurrentValue": True,"label": "%"},
                                step=1,
                                value=morbidity_rate_ga_default,
                                ),
                            ],style={
                                      "margin-top":"10px",
                                      }
                            ,),

                        # Live weight price
                        dbc.Col([
                            html.H6("Live weight price (USD per kg)"),
                            html.Br(),
                            daq.Slider(
                                id='base-live-weight-price-ga',
                                min=0.70,
                                max=3.25,
                                handleLabel={"showCurrentValue": True,"label": "$"},
                                step=.01,
                                value=live_weight_price_ga_default,
                                ),
                            ],style={
                                      "margin-top":"10px",
                                      }
                            ,),

                        ## END OF ROW ##
                        ], justify='evenly'),

                    # END OF CARD BODY
                    ],),

                    # END OF CARD
                    ], color='#F2F2F2'),
                    ], width=6),

                # Item Over Time Specific Controls
                dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Item Over Time Graph Controls",
                                className="card-title",
                                style={"font-weight": "bold"}),
                        dbc.Row([

                          # Item
                          dbc.Col([
                              html.H6("Item"),
                              dcc.Dropdown(id='select-item-ga',
                                            options=item_options_ga,
                                            value=item_list_ga[-1],   # Default is last item in list
                                            clearable = False,
                                            ),
                              ],style={
                                        "margin-top":"10px",
                                        },
                              ),
                        ]), # END OF ROW

                # END OF CARD BODY
                ],),

                # END OF CARD
                ], color='#F2F2F2'),
                ], width=3),

                ], style={"margin-right": "10px"}),

            html.Br(),

            #### -- GRAPHICS ROW
            dbc.Row([
                # Side by side waterfall
                dbc.Col([
                    dbc.Spinner(children=[
                        dcc.Graph(id='ga-ahle-waterfall',
                                  style = {"height":"650px"},
                                  config = {
                                      "displayModeBar" : True,
                                      "displaylogo": False,
                                      'toImageButtonOptions': {
                                          'format': 'png', # one of png, svg, jpeg, webp
                                          'filename': 'GBADs_GlobalAggregate_AHLE_Waterfall'
                                          },
                                      'modeBarButtonsToRemove': ['zoom',
                                                                  'zoomIn',
                                                                  'zoomOut',
                                                                  'autoScale',
                                                                  #'resetScale',  # Removes home button
                                                                  'pan',
                                                                  'select2d',
                                                                  'lasso2d']
                                      }
                                  )
                        # End of Spinner
                        ],size="md", color="#393375", fullscreen=False),
                    # End of Side by side waterfall
                    ],style={"width":5}),

                # Plot over time
                dbc.Col([
                    dbc.Spinner(children=[
                        dcc.Graph(id='ga-ahle-over-time',
                                  style = {"height":"650px"},
                                  config = {
                                      "displayModeBar" : True,
                                      "displaylogo": False,
                                      'toImageButtonOptions': {
                                          'format': 'png', # one of png, svg, jpeg, webp
                                          'filename': 'GBADs_GlobalAggregate_AHLE_Overtime'
                                          },
                                      'modeBarButtonsToRemove': ['zoom',
                                                                  'zoomIn',
                                                                  'zoomOut',
                                                                  'autoScale',
                                                                  #'resetScale',  # Removes home button
                                                                  'pan',
                                                                  'select2d',
                                                                  'lasso2d']
                                      }
                                  )
                        # End of Spinner
                        ],size="md", color="#393375", fullscreen=False),
                    # End of plot over time
                    ],style={"width":5}),
                ]),
        html.Br(),

        #### -- FOOTNOTES
        dbc.Row([
            dbc.Col([
                # Waterfall chart
                html.P("Ideal values assume increased production if there were no morbidity or mortality"),
                html.P("Using morbidity and mortality rates according to income group"),
                ]),
            dbc.Col([
                # Line chart
                html.P(""),
                ]),
            ], style={'margin-left':"40px",
                      'font-style': 'italic',
                      "margin-right": "20px"}
            ),
        html.Br(),

        #### -- DATATABLE
        dbc.Spinner(children=[
            html.Div([  # Row with DATATABLE
                      html.Div( id='ga-detailtab-displaytable'),
                      ], style={'margin-left':"20px",
                                "margin-right": "10px",
                                # "width":"95%"
                                }
                      ),
            # End of Spinner
            ],size="md", color="#393375", fullscreen=False),
        html.Br(), # Spacer for bottom of page

        ### END OF GLOBAL AHLE DETAILS TAB
        ], style=global_tab_style, selected_style=global_tab_selected_style),

        #### POULTRY TAB
        dcc.Tab(label="Major Producers | Poultry", children = [

            #### -- COUNTRY AND YEAR CONTROLS
            dbc.Row([
                # Region-country alignment
                dbc.Col([
                    html.H6('Region-country alignment'),
                    dcc.RadioItems(id='Region-country-alignment-poultry',
                                    options=region_structure_options,
                                    inputStyle={"margin-right": "10px", # This pulls the words off of the button
                                                "margin-left":"20px"},
                                    value="WOAH",
                                    style={"margin-left":'-20px'})
                    ],
                    style={
                            "margin-top":"10px",
                            "margin-right":"70px",
                            }

                    ),
                # Region
                dbc.Col([
                    html.H6("Region"),
                    dcc.Dropdown(id='select-region-poultry',
                                  options=WOAH_region_options,
                                  value='All',
                                  clearable = False,
                                  ),
                    ],style={
                              "order":1,
                              "margin-top":"10px",
                              },
                    ),

                # Country
                dbc.Col([
                    html.H6("Country"),
                    dcc.Dropdown(id='select-country-poultry',
                                  options=country_options_poultry,
                                  value='United Kingdom',
                                  clearable = False,
                                  ),
                    ],style={
                              "order":2,
                              "margin-top":"10px",
                              },
                    ),

                  # Year
                  dbc.Col([
                      html.H6("Year"),
                      dcc.Dropdown(id='select-year-poultry',
                                  options=year_options_poultry,
                                  value=2020,
                                  clearable = False,
                                  )
                      ],style={
                              'order': 3,
                              "margin-top":"10px",
                              },
                      ),

              # Metric
                dbc.Col([
                    html.H6("Metric"),
                    dcc.Dropdown(id='select-metric-poultry',
                                  options=metric_options,
                                  value="tonnes",
                                  clearable = False,
                                  )
                    ],style={
                              "order": 4,
                              "margin-top":"10px",
                              "margin-right": '10px',
                              },
                    ),

                ], justify='evenly'),


            html.Hr(style={'margin-right':'10px',}),

            #### -- CALCULATION CONTROLS
            dbc.Row([  # Line up all the controls in the same row.

                # Days on Feed
                dbc.Col([
                    html.H6("Days on feed"),
                    html.Br(),
                    daq.Slider(
                        id='dof-slider-poultry',
                        min=20,
                        max=60,
                        handleLabel={"showCurrentValue": True,"label": "Days"},
                        step=1,
                        value=dof_poultry_default,
                        ),

                    # Text underneath slider
                    html.P(id='reference-dof-poultry'),
                      ],style={'width': "auto",
                              "order":5,
                              # 'margin-left':'-40px',
                              }
                    ),

                # Achievable weight as percent of breed standard
                dbc.Col([
                    html.H6("Achievable % of breed standard"),
                    html.Br(),
                    daq.Slider(
                        id='achievable-pct-slider-poultry',
                        min=90,
                        max=110,
                        handleLabel={"showCurrentValue": True,"label": "%"},
                        step=1,
                        value=achievable_pct_poultry_default,
                        ),

                    # Text underneath slider
                      html.P(id='reference-achievable-pct-poultry'),
                      ],style={'width': "auto",
                              "order":6,}
                      ),

                # Price to Producers Upon Sale
                dbc.Col([
                    html.H6("Producer price (USD per kg carcass wt.)"),
                    html.Br(),
                    daq.Slider(
                        id='producer-price-slider-poultry',
                        min=0.70,
                        max=3.25,
                        handleLabel={"showCurrentValue": True,"label": "$"},
                        step=.01,
                        value=producer_price_poultry_default
                        ),

                    # Text underneath slider
                    html.P(id='reference-producerprice-poultry'),
                    ],style={'width': "auto",
                              "order":7,}
                    ),

                # Ration prices
                dbc.Col([
                    html.H6("Feed price (USD per tonne)"),
                    html.Br(),
                    daq.Slider(
                        id='ration-price-slider-poultry',
                        min=200,
                        max=500,
                        handleLabel={"showCurrentValue": True,"label": "$"},
                        step=10,
                        value=ration_price_poultry_default
                        ),

                    # Text underneath slider
                    html.P(id='reference-feedprice-poultry'),
                    ],style={'width': "auto",
                              "order":8,}
                    ),

                # FCR
                dbc.Col([
                    html.H6("Ideal feed conversion ratio"),
                    html.Br(),
                    daq.Slider(
                        id='fcr-slider-poultry',
                        min=1,
                        max=2.5,
                        handleLabel={"showCurrentValue": True,"label": "FCR"},
                        step=0.1,
                        value=fcr_poultry_default,
                        ),
                    # Text underneath slider
                    html.P(id='reference-fcr-poultry'),
                    ],style={'width': "auto",
                              "order":8,
                              'margin-right':'20px'}
                    ),

                # Reset to defaults button
                dbc.Col([
                    html.Button('Reset to default', id='reset-val-poultry', n_clicks=0),
                ],style={'width': "auto",
                          "order":9,
                          'textAlign':'center',
                          'margin':'auto',}
                ),

                ## END OF POULTRY TAB CONTROLS ROW ##
                ], justify='evenly',
                ),

        html.Hr(style={'margin-right':'10px',}),

        #html.Hr(),

        #### -- GRAPHICS
        dbc.Row([  # Row with GRAPHICS

            dbc.Col([ # Poultry Waterfall
                dbc.Spinner(children=[
                dcc.Graph(id='poultry-waterfall',
                            style = {"height":"650px"},
                          config = {
                              "displayModeBar" : True,
                              "displaylogo": False,
                              'toImageButtonOptions': {
                                  'format': 'png', # one of png, svg, jpeg, webp
                                  'filename': 'GBADs_Poultry_Waterfall'
                                  },
                              'modeBarButtonsToRemove': ['zoom',
                                                          'zoomIn',
                                                          'zoomOut',
                                                          'autoScale',
                                                          #'resetScale',  # Removes home button
                                                          'pan',
                                                          'select2d',
                                                          'lasso2d']
                              }
                          )
                # End of Spinner
                ],size="md", color="#393375", fullscreen=False),
                # End of Waterfall
                ],style={"width":5}),

            # dbc.Col([ # Poultry Sankey
            #     dbc.Spinner(children=[
            #     dcc.Graph(id='poultry-sankey',
            #                 style = {"height":"650px"},
            #               config = {
            #                   "displayModeBar" : True,
            #                   "displaylogo": False,
            #                   'toImageButtonOptions': {
            #                       'format': 'png', # one of png, svg, jpeg, webp
            #                       'filename': 'GBADs_Poultry_Sankey'
            #                       },
            #                   'modeBarButtonsToRemove': ['select2d',
            #                                              'lasso2d',
            #                                              'resetSCale']
            #                   })
            #         # End of Spinner
            #         ],size="md", color="#393375", fullscreen=False),
            #         # End of Sankey
            #         ],style={"width":5}
            #         ),

            dbc.Col([ # Poultry Stacked Bar
                dbc.Spinner(children=[
                dcc.Graph(id='poultry-stacked-bar',
                          style = {"height":"650px"},
                          config = {
                              "displayModeBar" : True,
                              "displaylogo": False,
                              'toImageButtonOptions': {
                                  'format': 'png', # one of png, svg, jpeg, webp
                                  'filename': 'GBADs_Poultry_Stacked_Bar'
                                  },
                              'modeBarButtonsToRemove': ['zoom',
                                                          'zoomIn',
                                                          'zoomOut',
                                                          'autoScale',
                                                          #'resetScale',  # Removes home button
                                                          'pan',
                                                          'select2d',
                                                          'lasso2d']
                              })
                    # End of Spinner
                    ],size="md", color="#393375", fullscreen=False),
                    # End of Stacked Bar
                    ],style={"width":5}
                    ),
            ]),
        html.Br(),

        #### -- FOOTNOTES
        dbc.Row([
            dbc.Col([
              # Breed Standard Potential source
              html.P(id='waterfall-footnote-poultry'),
            ]),
            dbc.Col([
              # Cost Assumptions
              html.P("Ideal costs are those required to achieve realised production if there were no mortality or morbidity."),
              ]),
        ], style={'margin-left':"40px", 'font-style': 'italic'}
        ),
        html.Br(),

        #### -- DATATABLE
        html.Div([  # Row with DATATABLE
                  html.Div( id='poultry-background-data'),
            ], style={'margin-left':"20px",
                        "width":"95%"}),
        html.Br(), # Spacer for bottom of page

        html.Div([  # Breed standard data
                  html.Div( id='poultry-breed-data'),
            ], style={'margin-left':"20px",
                      "width":"12%",}),
        html.Br() # Spacer for bottom of page

        ### END OF POULTRY TAB
        ], style=major_producers_tab_style, selected_style=major_producers_tab_selected_style),

        #### SWINE TAB
        dcc.Tab(label="Major Producers | Swine", children = [

            #### -- COUNTRY AND YEAR CONTROLS
            dbc.Row([
                # Region-country alignment
                dbc.Col([
                    html.H6('Region-country alignment'),
                    dcc.RadioItems(id='Region-country-alignment-swine',
                                    options=region_structure_options,
                                    inputStyle={"margin-right": "10px",
                                                "margin-left":"20px"},
                                    value="WOAH",
                                    style={"margin-left":'-20px'})
                    ],style={
                        "margin-top":"10px",
                        "margin-right":"70px",
                            }

                    ),
                # Region
                dbc.Col([
                    html.H6("Region"),
                    dcc.Dropdown(id='select-region-swine',
                                  options=WOAH_region_options,
                                  value='All',
                                  clearable = False,
                                  ),
                    ],style={
                              "order":1,
                              "margin-top":"10px"
                              }
                    ),

                # Country
                dbc.Col([
                    html.H6("Country"),
                    dcc.Dropdown(id='select-country-swine',
                                  options=country_options_swine,
                                  value='United Kingdom',
                                  clearable = False,
                                  ),
                    ],style={
                              "order":2,
                              "margin-top":"10px"
                              },
                    ),

                  # Year
                  dbc.Col([
                      html.H6("Year"),
                      dcc.Dropdown(id='select-year-swine',
                                  options=year_options_swine,
                                  value=2020,
                                  clearable = False,
                                  )
                      ],style={
                              'order': 3,
                              "margin-top":"10px"
                              },
                      ),

                # Metric
                dbc.Col([
                    html.H6("Metric"),
                    dcc.Dropdown(id='select-metric-swine',
                                  options=metric_options,
                                  value="tonnes",
                                  clearable = False,
                                  )
                    ],style={
                              "order": 4,
                              "margin-top":"10px",
                              "margin-right": '10px',
                              },
                    ),

                ], justify='evenly'),


            html.Hr(style={'margin-right':'10px'}),

            #### -- CALCULATION CONTROLS
            dbc.Row([  # Line up all the controls in the same row.

                # Days on Feed
                dbc.Col([
                    html.H6("Days on feed"),
                    html.Br(),
                    daq.Slider(
                        id='dof-slider-swine',
                        min=112,
                        max=196,
                        handleLabel={"showCurrentValue": True,"label": "Days"},
                        step=7,
                        value=dof_swine_default,
                        ),
                    ],style={'width': "auto",
                              "order":5,
                              }
                    ),

                # Feed Intake
                # Alternative to Days on Feed for determining breed standard potential
                  # dbc.Col([
                  #     html.H6("Feed intake (kg per head)"),
                  #     html.Br(),
                  #     daq.Slider(
                  #         id='feed-slider-swine',
                  #         min=80,
                  #         max=355,
                  #         handleLabel={"showCurrentValue": True,"label": "kg"},
                  #         step=5,
                  #         value=feed_swine_default,
                  #         ),
                  #     html.P(id='reference-feedintake-swine'),
                  #      ],style={'width': "auto",
                  #               "order":5,
                  #               }
                  #     ),

                # Achievable weight in kg
                # Alternative to Achievable Percent for determining effect of feed and practices
                dbc.Col([
                    html.H6("Achievable live weight without disease (kg)"),
                    html.Br(),
                    daq.Slider(
                      id='achievable-weight-slider-swine',
                      min=70,
                      max=180,
                      handleLabel={"showCurrentValue": True,"label": "kg"},
                      step=5,
                      value=achievable_weight_swine_default,
                      ),
                    # Text underneath slider
                    html.P(id='reference-liveweight-swine'),
                    ],style={'width': "auto",
                            "order":6}
                    ),

                # Price to Producers Upon Sale
                dbc.Col([
                    html.H6("Producer price (USD per kg carcass wt.)"),
                    html.Br(),
                    daq.Slider(
                        id='producer-price-slider-swine',
                        min=0.70,
                        max=3.25,
                        handleLabel={"showCurrentValue": True,"label": "$"},
                        step=.01,
                        value=producer_price_swine_default,
                        ),
                    # Text underneath slider
                    html.P(id='reference-producerprice-swine'),
                    ],style={'width': "auto",
                              "order":7}
                    ),

                # Ration prices
                dbc.Col([
                    html.H6("Feed price (USD per tonne)"),
                    html.Br(),
                    daq.Slider(
                        id='ration-price-slider-swine',
                        min=200,
                        max=500,
                        handleLabel={"showCurrentValue": True,"label": "$"},
                        step=10,
                        value=ration_price_swine_default,
                        ),
                    # Text underneath slider
                    html.P(id='reference-feedprice-swine'),
                    ],style={'width': "auto",
                              "order":8,
                              'margin-right':'20px'}
                    ),

                # FCR
                dbc.Col([
                    html.H6("Ideal feed conversion ratio"),
                    html.Br(),
                    daq.Slider(
                        id='fcr-slider-swine',
                        min=1.5,
                        max=3,
                        handleLabel={"showCurrentValue": True,"label": "FCR"},
                        step=0.1,
                        value=fcr_swine_default,
                        ),
                    # Text underneath slider
                    html.P(id='reference-fcr-swine'),
                    ],style={'width': "auto",
                              "order":8,
                              'margin-right':'20px'}
                    ),

                # Reset to defaults button
                dbc.Col([
                    html.Button('Reset to default', id='reset-val-swine', n_clicks=0),
                ],style={'width': "auto",
                          "order":9,
                          'textAlign':'center',
                          'margin':'auto',}
                ),

                ## END OF SWINE TAB CONTROLS ROW ##
                ], # justify='evenly',
                          #    style={'vertical-align':'top',
                          # 'display':'flex',
                          # 'no-gutters':True}
                ),

        #### -- GRAPHICS
        dbc.Row([  # Row with GRAPHICS

            dbc.Col([ # Swine Waterfall
                dbc.Spinner(children=[
                dcc.Graph(id='swine-waterfall',
                          style = {"height":"650px"},
                          config = {
                              "displayModeBar" : True,
                              "displaylogo": False,
                              'toImageButtonOptions': {
                                  'format': 'png', # one of png, svg, jpeg, webp
                                  'filename': 'GBADs_Swine_Waterfall'
                                  },
                              'modeBarButtonsToRemove': ['zoom',
                                                          'zoomIn',
                                                          'zoomOut',
                                                          'autoScale',
                                                          #'resetScale',  # Removes home button
                                                          'pan',
                                                          'select2d',
                                                          'lasso2d']
                              }
                          )
                # End of Spinner
                ],size="md", color="#393375", fullscreen=False),
                # End of Waterfall
                ],style={"width":5}),

            # dbc.Col([ # Swine Sankey
            #     dbc.Spinner(children=[
            #     dcc.Graph(id='swine-sankey',
            #               style = {"height":"650px"},
            #               config = {
            #                   "displayModeBar" : True,
            #                   "displaylogo": False,
            #                   'toImageButtonOptions': {
            #                       'format': 'png', # one of png, svg, jpeg, webp
            #                       'filename': 'GBADs_Swine_Sankey'
            #                       },
            #                   'modeBarButtonsToRemove': ['select2d',
            #                                              'lasso2d',
            #                                              'resetSCale']
            #                   })
            #         # End of Spinner
            #         ],size="md", color="#393375", fullscreen=False),
            #         # End of Sankey
            #         ],style={"width":5}
            #         ),

            dbc.Col([ # Swine Stacked Bar
                dbc.Spinner(children=[
                dcc.Graph(id='swine-stacked-bar',
                            style = {"height":"650px"},
                          config = {
                              "displayModeBar" : True,
                              "displaylogo": False,
                              'toImageButtonOptions': {
                                  'format': 'png', # one of png, svg, jpeg, webp
                                  'filename': 'GBADs_Swine_Stacked_Bar'
                                  },
                              'modeBarButtonsToRemove': ['zoom',
                                                          'zoomIn',
                                                          'zoomOut',
                                                          'autoScale',
                                                          #'resetScale',  # Removes home button
                                                          'pan',
                                                          'select2d',
                                                          'lasso2d']

                              })
                    # End of Spinner
                    ],size="md", color="#393375", fullscreen=False),
                    # End of Stacked Bar
                    ],style={"width":5}
                    ),

            ]),
        html.Br(),

        #### -- FOOTNOTES
        dbc.Row([
            dbc.Col([
              # Breed Standard Potential source
              html.P("*Using PIC breed standard, assuming 75% average carcass yield."),
            ]),
            dbc.Col([
              # Cost Assumptions
              html.P("Ideal costs are those required to achieve realised production if there were no mortality or morbidity."),
            ]),
        ], style={'margin-left':"40px", 'font-style': 'italic'}
        ),
        html.Br(),

        #### -- DATATABLE
        html.Div([  # Core data for country
                  html.Div( id='swine-background-data'),
            ], style={'margin-left':"20px",
                      "width":"95%",}),
        html.Br(), # Spacer for bottom of page

        html.Div([  # Breed standard data
                  html.Div( id='swine-breed-data'),
            ], style={'margin-left':"20px",
                      "width":"18%",}),
        html.Br() # Spacer for bottom of page

        ### END OF SWINE TAB
        ], style=major_producers_tab_style, selected_style=major_producers_tab_selected_style),

        #### BEEF TAB
        # JR: Hiding the beef tab for now
        # dcc.Tab(label="Beef"),

        #### ETHIOPIA TAB
        dcc.Tab(label="Ethiopia Case Study [WIP]", children =[

            #### -- DROPDOWNS CONTROLS
            dbc.Row([
                dbc.Col([
                    html.H4("Species"),
                    dcc.Dropdown(id='select-species-ecs',
                                options=ecs_species_options,
                                value='All Small Ruminants',
                                clearable = False,
                                ),
                    ]),
                dbc.Col([
                    html.H4("Production System"),
                    dcc.Dropdown(id='select-prodsys-ecs',
                                 # Options and value are now defined in a callback based on selected species
                                # options=ecs_prodsys_options,
                                # value='All Production Systems',
                                clearable = False,
                                ),
                    ],style={
                            # "margin-top":"10px",
                            "margin-bottom":"30px", # Adding this to account for the additional space creted by the radio buttons
                            }
                    ),
                dbc.Col([
                    html.H4("Currency"),
                    dcc.Dropdown(id='select-currency-ecs',
                                options=ecs_currency_options,
                                value='Birr',
                                clearable = False,
                                ),
                    ]),
                dbc.Col([
                    html.H4("Year"),
                    dcc.Dropdown(id='select-year-ecs',
                                options=ecs_year_options,
                                value=2021,
                                clearable = False,
                                ),
                    ]),
                ]),
            dbc.Row([

                # AHLE Specific Controls
                dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Value and Cost Graph Controls",
                                className="card-title",
                                style={"font-weight": "bold"}),
                        dbc.Row([
                            # Display
                            dbc.Col([
                                html.H6("Display"),
                                dcc.RadioItems(id='select-display-ecs',
                                              options=ecs_display_options,
                                              value='Side by Side',
                                              labelStyle={'display': 'block'},
                                              inputStyle={"margin-right": "2px"}, # This pulls the words off of the button
                                              ),
                                ],
                            ),

                            # Compare
                            dbc.Col([
                                html.H6("Compare current scenario to..."),
                                dcc.RadioItems(id='select-compare-ecs',
                                              options=ecs_compare_options,
                                              value='Ideal',
                                              labelStyle={'display': 'block'},
                                              inputStyle={"margin-right": "2px"}, # This pulls the words off of the button
                                              ),
                                ],
                            ),

                            # Age/Sex combination
                            dbc.Col([
                                html.H6("Scenario applies to group..."),
                                dcc.Dropdown(id='select-agesex-ecs',
                                              options=ecs_agesex_options,
                                              value='Overall',
                                              clearable = False,
                                              )
                                ],style={
                                          # "margin-top":"10px",
                                          "margin-bottom":"30px", # Adding this to account for the additional space creted by the radio buttons
                                          },
                                ),

                        ]), # END OF ROW
                        dbc.Row([  # Improvement scenarios

                            # Factor dropdown
                            dbc.Col([
                                html.H6("Improvement Factor"),
                                dcc.Dropdown(id='select-factor-ecs',
                                              options=ecs_factor_options,
                                              value='Mortality',
                                              clearable = True,
                                              ),
                                  ],width=6,
                                ),

                            # Reduction
                            dbc.Col([
                                html.H6("Improvement Amount"),
                                dcc.RadioItems(id='select-improve-ecs',
                                              options=ecs_improve_options,
                                              value= "25%",
                                              inputStyle={"margin-right": "2px", # This pulls the words off of the button
                                                          "margin-left": "10px"},
                                              ),
                                ],
                            ),

                            ## END OF ROW ##
                            ]),

                    # END OF CARD BODY
                    ],),

                # END OF CARD
                ], color='#F2F2F2'),
                ],width=6),

            # Attribution Specific Controls
            dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Attribution Graph Controls - Hierarchy",
                            className="card-title",
                            style={"font-weight": "bold"}),

                    dbc.Row([
                        # # Hierarchy
                        # html.H5("Hierarchy",
                        #               style={"font-weight": "bold"}),

                    # Top Level
                    dbc.Col([
                        html.H6("Top Level"),
                        dcc.Dropdown(id='select-top-lvl-attr-ecs',
                                      options=ecs_hierarchy_attr_options,
                                      value='cause',
                                      clearable = False,
                                      ),
                        ], style={
                            "margin-bottom":"30px", # Adding this to account for the additional space creted by the radio buttons
                            },
                        ),
                    # Drill Down 1
                    dbc.Col([
                        html.H6("Drill Down 1"),
                        dcc.Dropdown(id='select-dd-1-attr-ecs',
                                      # options=ecs_hierarchy_dd_attr_options,
                                      # value='production_system',
                                       clearable = False,
                                      ),
                        ], style={
                            "margin-bottom":"30px", # Adding this to account for the additional space creted by the radio buttons
                            },
                        ),
                    # Drill Down 2
                    dbc.Col([
                        html.H6("Drill Down 2"),
                        dcc.Dropdown(id='select-dd-2-attr-ecs',
                                      options=ecs_hierarchy_dd_attr_options,
                                      value='age_group',
                                      clearable = False,
                                      ),
                        ], style={
                            "margin-bottom":"30px", # Adding this to account for the additional space creted by the radio buttons
                            },
                        ),

                ]), # END OF ROW

                dbc.Row([
                # Drill Down 3
                dbc.Col([
                    html.H6("Drill Down 3"),
                    dcc.Dropdown(id='select-dd-3-attr-ecs',
                                  options=ecs_hierarchy_dd_attr_options,
                                  value='sex',
                                  clearable = False,
                                  ),
                    ]),
                # Drill Down 4
                dbc.Col([
                    html.H6("Drill Down 4"),
                    dcc.Dropdown(id='select-dd-4-attr-ecs',
                                  options=ecs_hierarchy_dd_attr_options,
                                  value='ahle_component',
                                  clearable = False,
                                  ),
                    ]),
                # # Drill Down 5
                # dbc.Col([
                #     html.H6("Drill Down 5"),
                #     dcc.Dropdown(id='select-dd-5-attr-ecs',
                #                   options=ecs_hierarchy_dd_attr_options,
                #                   value='None',
                #                   clearable = False,
                #                   ),
                #     ]),
                ]), # END OF ROW

                # END OF CARD BODY
                ]),

                # END OF CARD
                ], color='#F2F2F2'),
                ]),


                # END OF DROPDOWN CONTROLS
                ], justify='evenly'),


            # html.Hr(style={'margin-right':'10px'}),

            #### -- CALCULATION CONTROLS
            # dbc.Card([
            #     dbc.CardBody([
            #         html.H5("Exploring Relative Contribution to Gross Margin and AHLE",
            #                 className="card-title",
            #                 style={"font-weight": "bold"}),
            # dbc.Row([  # Line up all the controls in the same row.

            #     # Factor dropdown
            #     dbc.Col([
            #         html.H6("Factor"),
            #         dcc.Dropdown(id='select-factor-ecs',
            #                       options=ecs_factor_options,
            #                       value='Mortality',
            #                       clearable = True,
            #                       ),
            #           ],
            #         ),

            #     # Reduction
            #     dbc.Col([
            #         html.H6("Improvement"),
            #         dcc.RadioItems(id='select-improve-ecs',
            #                       options=ecs_improve_options,
            #                       value= "25%",
            #                       inputStyle={"margin-right": "2px", # This pulls the words off of the button
            #                                   "margin-left": "10px"},
            #                       ),
            #         ],width=3,
            #     ),

            #     # # Reset to defaults button
            #     # dbc.Col([
            #     #     html.Button('Reset to Current Values', id='reset-val-ecs', n_clicks=0),
            #     # ], width=3,
            #     #     style={
            #     #           'textAlign':'center',
            #     #           'margin':'auto',}
            #     # ),

            #     ## END OF ROW ##
            #     ]),

            # # END OF CARD BODY
            # ],),

            # # END OF CARD
            # ], color='#F2F2F2'),

            html.Br(),

            #### -- GRAPHICS
                dbc.Row([  # Row with GRAPHICS

                    # Values and Costs Waterfall
                    dbc.Col([
                        dbc.Spinner(children=[
                        dcc.Graph(id='ecs-ahle-waterfall',
                                    style = {"height":"650px"},
                                  config = {
                                      "displayModeBar" : True,
                                      "displaylogo": False,
                                      'toImageButtonOptions': {
                                          'format': 'png', # one of png, svg, jpeg, webp
                                          'filename': 'GBADs_Ethiopia_AHLE_Sunburst'
                                          },
                                      'modeBarButtonsToRemove': ['zoom',
                                                                  'zoomIn',
                                                                  'zoomOut',
                                                                  'autoScale',
                                                                  #'resetScale',  # Removes home button
                                                                  'pan',
                                                                  'select2d',
                                                                  'lasso2d']
                                      }
                                  )
                        # End of Spinner
                        ],size="md", color="#393375", fullscreen=False),
                        # End of AHLE Sunburst
                        ],style={"width":5}),

                    # Attribution Treemap
                    dbc.Col(
                        dbc.Spinner(children=[

                        dcc.Graph(id='ecs-attr-treemap',
                                    style = {"height":"650px"},
                                  config = {
                                      "displayModeBar" : True,
                                      "displaylogo": False,
                                      'toImageButtonOptions': {
                                          'format': 'png', # one of png, svg, jpeg, webp
                                          'filename': 'GBADs_Ethiopia_Attribution_Treemap'
                                          },
                                      # 'modeBarButtonsToRemove': ['zoom',
                                      #                            'zoomIn',
                                      #                            'zoomOut',
                                      #                            'autoScale',
                                      #                            #'resetScale',  # Removes home button
                                      #                            'pan',
                                      #                            'select2d',
                                      #                            'lasso2d']
                                      }
                                  )

                        # End of Spinner
                        ],size="md", color="#393375", fullscreen=False),
                        # End of Attribution Treemap
                        style={"width":5}),

                    ]),
                html.Br(),

            #### -- FOOTNOTES
            dbc.Row([
                dbc.Col([
                  # Waterfall explanation
                  html.P("*The blue indicates an increase, the red indicates a decrease in costs/value for each category. The orange is the sum/difference of all of them."),
                ]),
                dbc.Col([
                  # Species groups
                  html.P("*Attribution is reported for species groups rather than individual species."),
                  # Cost Assumptions
                  html.P("**AHLE Components are production loss, mortality loss, and health costs. Health costs make up the smallest proportion and may not be visible in this view."),
                  # Health Cost temporary distribution
                  html.P("***Health cost attribution is currently a placeholder, and is attributed evenly among the AHLE causes.")
                ]),
            ], style={'margin-left':"40px", 'font-style': 'italic'}
            ),
            html.Br(),
            ### END OF FOOTNOTES


            #### -- ADDITIONAL VISUALS
            dbc.Row([
                dbc.Col([ # AHLE Stacked Bar
                    dbc.Spinner(children=[
                    dcc.Graph(id='ahle-stacked-bar-ecs',
                                style = {"height":"500px"},
                              config = {
                                  "displayModeBar" : True,
                                  "displaylogo": False,
                                  'toImageButtonOptions': {
                                      'format': 'png', # one of png, svg, jpeg, webp
                                      'filename': 'GBADs_AHLE_Stacked_Bar_ECS'
                                      },
                                  'modeBarButtonsToRemove': ['zoom',
                                                              'zoomIn',
                                                              'zoomOut',
                                                              'autoScale',
                                                              #'resetScale',  # Removes home button
                                                              'pan',
                                                              'select2d',
                                                              'lasso2d']

                                  })
                        # End of Spinner
                        ],size="md", color="#393375", fullscreen=False),
                        # End of Stacked Bar
                        ],style={"width":5}
                        ),

                # Sankey
                dbc.Col([
                dbc.Spinner(children=[
                    html.H4("Sankey for Attribution"),
                        html.Div(children=[
                                html.Img(src='/assets/ECS_Sanky_diagram_from_Gemma.png',
                                style = {'width':'120vw'}),
                                ],
                                  style = {
                                          "margin-bottom":"10px",
                                          'margin-right':"10px",},
                                  ),
                        # End of Spinner
                        ],size="md", color="#393375", fullscreen=False),
                    ]),

            ]), # END OF ROW
            html.Br(),
            ### END OF ADDITIONAL VISUALS

            #### -- ADDITIONAL FOOTNOTES
            dbc.Row([
                dbc.Col([
                  # Stacked bar
                  html.P("*Expenditure on Health is not recorded for individual age groups so is not included in individual AHLE calculations."),
                  html.P("**Expenditure on Health is very small, so the impact on AHLE is negligible."),
                ]),
                dbc.Col([
                  # Sankey
                  # No footnote
                ]),
            ], style={'margin-left':"40px", 'font-style': 'italic'}
            ),

            #### -- DATATABLE
            dbc.Row([

                dbc.Col([
                    html.Div([  # Core data for AHLE
                          html.Div( id='ecs-ahle-datatable'),
                    ], style={'margin-left':"20px"}),
                html.Br() # Spacer for bottom of page
                ]),

                dbc.Col([
                    html.Div([  # Core data for attribution
                          html.Div( id='ecs-attr-datatable'),
                    ], style={'margin-left':"20px",}),
                html.Br(), # Spacer for bottom of page
                ]),  # END OF COL

                # END OF COL
            ]),
            html.Br(),
            ### END OF DATATABLE


        ### END OF ETHIOPIA TAB
            ], style=ecs_tab_style, selected_style=ecs_tab_selected_style),


        #### USER GUIDE TAB
        dcc.Tab(label="User Guide & References", children =[
            html.Iframe(src="assets/GBADs_Documentation/_build/html/index.html", # this is for the jupyter books
                        # src="https://docs.python.org/3/", # this is for the placeholder python documentation
                        style={"width":"100%",
                                "height":"2500px",   # Set large enough for your largest page and guide will use browser scroll bar. Otherwise, longer pages will get their own scroll bars.
                                },)
        ### END OF USER GUIDE TAB
            ], style=user_guide_tab_style, selected_style=user_guide_tab_selected_style),

        ### END OF TABS ###
        ],style={'margin-right':'10px',
                 'margin-left': '10px'} )
    ])

#%% 5. CALLBACKS
# This section does the interactivity work with the web page
# - Listens to Inputs, linked to the id's of various web page elements in the LAYOUT
# - Changes the webpage with Outputs, also linked to the id's in the LAYOUT

# Version using multiple callbacks relies on passing data between them
# See https://dash.plotly.com/sharing-data-between-callbacks

# ==============================================================================
#### UPDATE POULTRY
# ==============================================================================
# ------------------------------------------------------------------------------
#### -- Controls
# ------------------------------------------------------------------------------
# Update regions based on region contry aligment selection:
@gbadsDash.callback(
    Output(component_id='select-region-poultry', component_property='options'),
    Input(component_id='Region-country-alignment-poultry', component_property='value'),
    )
def update_region_options_poultry(region_country):
    if region_country == "WOAH":
        options = WOAH_region_options
    elif region_country =="FAO":
        options = fao_region_options
    elif region_country == "World Bank":
        options = wb_region_options
    return options

# Update country options based on region selection
@gbadsDash.callback(
    Output(component_id='select-country-poultry', component_property='options'),
    Input(component_id='Region-country-alignment-poultry', component_property='value'),
    Input(component_id='select-region-poultry', component_property='value'),
    )
def update_country_options_poultry(region_country, region):
    if region_country == "WOAH":
        if region == "All":
            options = country_options_poultry
        elif region == "Africa":
            options = WOAH_africa_options
        elif region == "Americas":
            options = WOAH_americas_options
        elif region == "Asia & the Pacific":
            options = WOAH_asia_options
        else:
            options = WOAH_europe_options
    elif region_country =="FAO":
        if region == "All":
            options = country_options_poultry
        elif region == "Africa":
            options = fao_africa_options
        elif region == "Asia":
            options = fao_asia_options
        elif region == "Europe and Central Asia":
            options = fao_eca_options
        elif region == "Latin America and the Caribbean":
            options = fao_lac_options
        else:
            options = fao_swp_options
    elif region_country == "World Bank":
        if region == "All":
            options = country_options_poultry
        elif region == "Sub-Saharan Africa":
            options = wb_africa_options
        elif region == "Europe & Central Asia":
            options = wb_eca_options
        elif region == "Latin America & the Caribbean":
            options = wb_lac_options
        elif region == "North America":
            options = wb_na_options
        else:
            options = wb_southasia_options
    else:
        options = country_options_poultry

    return options

# Set slider starting values and add reference underneath based on selected country
# Also enable "Reset to Default" button
@gbadsDash.callback(
    Output('achievable-pct-slider-poultry', 'value'),
    Input(component_id='reset-val-poultry', component_property='n_clicks')   # Reset to defaults button
    )
def reset_achievablepct_poultry(reset):
    return achievable_pct_poultry_default

@gbadsDash.callback(
    Output('dof-slider-poultry', 'value'),
    Output('reference-dof-poultry', 'children'),
    Input('select-country-poultry', 'value'),
    Input('select-year-poultry', 'value'),
    Input(component_id='reset-val-poultry', component_property='n_clicks')   # Reset to defaults button
    )
def show_ref_daysonfeed_poultry(country, year, reset):
    input_df = gbads_chickens_merged_fordash
    _rowselect = (input_df['country'] == country) & (input_df['year'] == year)
    datavalue = input_df.loc[_rowselect ,'acc_avgdaysonfeed'].values[0]
    country_shortname = country_shortnames[country]
    if pd.isnull(datavalue):
      slider = dof_poultry_default
      display = '(no data)'
    else:
      slider = datavalue
      display = f'{datavalue:.0f} days'
    return slider, f'Average for {country_shortname} in {year}: {display}'

@gbadsDash.callback(
    Output('producer-price-slider-poultry', 'value'),
    Output('reference-producerprice-poultry', 'children'),
    Input('select-country-poultry', 'value'),
    Input('select-year-poultry', 'value'),
    Input(component_id='reset-val-poultry', component_property='n_clicks')   # Reset to defaults button
    )
def show_ref_producerprice_poultry(country, year, reset):
    input_df = gbads_chickens_merged_fordash
    _rowselect = (input_df['country'] == country) & (input_df['year'] == year)
    datavalue = input_df.loc[_rowselect ,'acc_producerprice_usdperkgcarc'].values[0]
    country_shortname = country_shortnames[country]
    if pd.isnull(datavalue):
      slider = producer_price_poultry_default
      display = '(no data)'
    else:
      slider = round(datavalue, 2)
      display = f'${datavalue:.2f}'
    return slider, f'Average for {country_shortname} in {year}: {display}'

@gbadsDash.callback(
    Output('ration-price-slider-poultry', 'value'),
    Output('reference-feedprice-poultry', 'children'),
    Input('select-country-poultry', 'value'),
    Input('select-year-poultry', 'value'),
    Input(component_id='reset-val-poultry', component_property='n_clicks')   # Reset to defaults button
    )
def show_ref_feedprice_poultry(country, year, reset):
    input_df = gbads_chickens_merged_fordash
    _rowselect = (input_df['country'] == country) & (input_df['year'] == year)
    datavalue = input_df.loc[_rowselect ,'acc_feedprice_usdpertonne'].values[0]
    country_shortname = country_shortnames[country]
    if pd.isnull(datavalue):
      slider = ration_price_poultry_default
      display = '(no data)'
    else:
      slider = round(datavalue, 2)
      display = f'${datavalue:.2f}'
    return slider, f'Average for {country_shortname} in {year}: {display}'

# Using Breed Standard FCR as reference
@gbadsDash.callback(
    Output('fcr-slider-poultry', 'value'),
    Output('reference-fcr-poultry', 'children'),
    Input('select-country-poultry', 'value'),
    Input('dof-slider-poultry', 'value'),
    Input(component_id='reset-val-poultry', component_property='n_clicks')   # Reset to defaults button
    )
def show_ref_fcr_poultry(country, dof, reset):
    breed_label_touse = poultry_lookup_breed_from_country[country]
    breed_df_touse = poultry_lookup_breed_df[breed_label_touse]
    _rowselect = (breed_df_touse['dayonfeed'] == dof)
    datavalue = breed_df_touse.loc[_rowselect ,'fcr'].values[0]
    if pd.isnull(datavalue):
      slider = fcr_poultry_default
      display = '(no data)'
    else:
      slider = round(datavalue, 2)
      display = f'{datavalue:.2f}'
    return slider, f'Breed standard: {display}'

# ------------------------------------------------------------------------------
#### -- Data
# ------------------------------------------------------------------------------
# MUST HAPPEN FIRST: Calculate burden of disease components on core data
# Updates when user changes achievable proportion slider
# Does not care about simple filtering (country and year)
@gbadsDash.callback(
    Output('core-data-poultry','data'),
    Input('achievable-pct-slider-poultry','value'),
    Input('dof-slider-poultry','value'),
    Input('select-country-poultry','value'),
    Input('ration-price-slider-poultry','value'),
    Input('fcr-slider-poultry','value')
    )
def update_core_data_poultry(achievable_pct, avg_dof, country, feedprice, fcr):
    breed_label_touse = poultry_lookup_breed_from_country[country]
    breed_df_touse = poultry_lookup_breed_df[breed_label_touse]
    poultry_data_withbod = bod.calc_bod_master_poultry(
      gbads_chickens_merged_fordash
      ,ACHIEVABLE_PCT_MASTER=achievable_pct      # Integer [0, 120]: proportion of ideal production that is achievable without disease, i.e. efficiency of feed, medications, and practices
      ,AVG_DOF_MASTER=avg_dof                      # Integer (0, 63]: Average days on feed. Will lookup breed standard weight for this day on feed.
      ,BREED_DF_MASTER=breed_df_touse     # Data frame with breed reference information. Must contain columns 'dayonfeed' and 'bodyweight_g'.
      ,FEEDPRICE_USDPERTONNE_MASTER=feedprice           # Float
      ,IDEAL_FCR_LIVE_MASTER=fcr                        # Float: ideal FCR per kg live weight
      # ,AVG_CARC_YIELD_MASTER=0.695                 # Float [0, 1]: average carcass yield as proportion of live weight. If blank, will use 'bod_breedstdyield_prpn'.
    )
    poultry_data_withbod['year'] = poultry_data_withbod['year'].astype(str)   # Change Year type to text
    return poultry_data_withbod.to_json(date_format='iso', orient='split')

# Can happen in any order after update_core_data
# These update when user changes filtering (country and year)
# Update data table to show user
@gbadsDash.callback(
    Output('poultry-background-data', 'children'),
    Input('core-data-poultry','data'),
    Input('select-country-poultry','value'),
    Input('producer-price-slider-poultry','value'),
    Input('ration-price-slider-poultry','value'),
    )
def update_background_data_poultry(input_json, country ,producerprice ,rationprice):
    # Dash callback input data is a string that names a json file
    # First read it into a dataframe
    input_df = pd.read_json(input_json, orient='split')
    background_data = input_df.loc[(input_df['country'] == country)]

    # Add slider values as columns to display
    background_data['producerprice_usdperkg'] = producerprice
    background_data['rationprice_usdpertonne'] = rationprice
    background_data['bod_totalburden_usd'] = background_data['bod_totalburden_tonnes'] * 1000 \
      * background_data['producerprice_usdperkg']

    columns_to_display_with_labels = {
      'country':'Country'
      ,'year':'Year'

      ,'acc_headplaced':'Head Placed'
      ,'acc_headslaughtered':'Head Slaughtered'
      ,'acc_totalcarcweight_tonnes':'Total Carcass Weight (tonnes)'   # Equal to bod_realizedproduction_tonnes
      ,'acc_avgcarcweight_kg':'Avg. Carcass Weight (kg)'
      # ,'acc_avgdaysonfeed':'Avg Days on Feed'   # Using input value rather than this column
      # ,'acc_avgliveweight_kg':'Avg Live Weight (kg)'

      ,'bod_dof_used':'Days on Feed'
      ,'bod_breedstdwt_kg':'Breed Standard Live Weight (kg)'
      ,'bod_breedstdyield_prpn':'Breed Standard Carcass Yield'
      ,'bod_breedstdcarcwt_kg':'Breed Standard Carcass Weight (kg)'
      ,'bod_referenceproduction_tonnes':'Breed Standard Potential (tonnes)'
      ,'bod_efficiency_tonnes':'Effect of Feed & Practices (tonnes)'
      ,'bod_gmax_tonnes':'Achievable without Disease (tonnes)'
      ,'bod_deathloss_tonnes':'Mortality & Condemns (tonnes)'
      ,'bod_morbidity_tonnes':'Morbidity (tonnes)'
      ,'bod_realizedproduction_tonnes':'Realised Production (tonnes)'
      ,'bod_totalburden_tonnes':'Total Burden of Disease (tonnes)'

      ,'producerprice_usdperkg':'Producer Price (USD per kg)'
      ,'bod_totalburden_usd':'Total Burden of Disease (USD)'
      # ,'wb_gdp_usd':'GDP (USD)'

      ,'acc_feedcost_usdperkglive':'Avg. Feed Cost (USD per kg live weight)'
      ,'acc_chickcost_usdperkglive':'Avg. Chick Cost (USD per kg live weight)'
      ,'acc_laborcost_usdperkglive':'Avg. Labour Cost (USD per kg live weight)'
      ,'acc_landhousingcost_usdperkglive':'Avg. Land & Housing Cost (USD per kg live weight)'
      ,'acc_medcost_usdperkglive':'Avg. Medicine Cost (USD per kg live weight)'
      ,'acc_othercost_usdperkglive':'Avg. Other Costs (USD per kg live weight)'

      ,'ideal_headplaced':'Ideal Head Placed'
      ,'ideal_fcr':'Ideal FCR'
      ,'ideal_feed_tonnes':'Ideal Feed Consumption (tonnes)'
      ,'rationprice_usdpertonne':'Feed Price (USD per tonne)'
      ,'ideal_feedcost_usdperkglive':'Ideal Feed Cost (USD per kg live weight)'
      ,'ideal_chickcost_usdperkglive':'Ideal Chick Cost (USD per kg live weight)'
      ,'ideal_landhousingcost_usdperkglive':'Ideal Land & Housing Cost (USD per kg live weight)'
      ,'ideal_laborcost_usdperkglive':'Ideal Labour Cost (USD per kg live weight)'
      ,'ideal_medcost_usdperkglive':'Ideal Medicine Cost (USD per kg live weight)'
      ,'ideal_othercost_usdperkglive':'Ideal Other Costs (USD per kg live weight)'
    }

    # ------------------------------------------------------------------------------
    # Format data to display in the table
    # ------------------------------------------------------------------------------
    # Order does not matter in these lists
    # Zero decimal places
    background_data.update(background_data[[
      'acc_headplaced'
      ,'acc_headslaughtered'
      ,'acc_totalcarcweight_tonnes'
      ,'bod_referenceproduction_tonnes'
      ,'bod_realizedproduction_tonnes'
      ,'bod_efficiency_tonnes'
      ,'bod_gmax_tonnes'
      ,'bod_deathloss_tonnes'
      ,'bod_morbidity_tonnes'
      ,'bod_totalburden_tonnes'
      ,'wb_gdp_usd'
      ,'ideal_headplaced'
      ,'ideal_feed_tonnes'
    ]].applymap('{:,.0f}'.format))

    # Two decimal places
    background_data.update(background_data[[
      'bod_breedstdwt_kg'
      ,'bod_breedstdyield_prpn'
      ,'bod_breedstdcarcwt_kg'
      ,'acc_avgcarcweight_kg'
      ,'producerprice_usdperkg'
      ,'bod_totalburden_usd'
      ,'rationprice_usdpertonne'
      ,'acc_feedcost_usdperkglive'
      ,'acc_chickcost_usdperkglive'
      ,'acc_laborcost_usdperkglive'
      ,'acc_landhousingcost_usdperkglive'
      ,'acc_medcost_usdperkglive'
      ,'acc_othercost_usdperkglive'
      ,'ideal_fcr'
      ,'ideal_feedcost_usdperkglive'
      ,'ideal_chickcost_usdperkglive'
      ,'ideal_landhousingcost_usdperkglive'
      ,'ideal_laborcost_usdperkglive'
      ,'ideal_medcost_usdperkglive'
      ,'ideal_othercost_usdperkglive'
    ]].applymap('{:,.2f}'.format))

    # ------------------------------------------------------------------------------
    # Hover-over text
    # ------------------------------------------------------------------------------
    # Read last row of data with filters applied to get source of each column.
    # For most countries and columns, source is the same for every year.
    # But if source differs for later years, want to report the latest.
    background_data_lastrow = background_data.iloc[-1 ,:]

    # Define tooltips, using _src columns where appropriate
    column_tooltips = {
      "acc_headplaced":f"Chicks placed ({background_data_lastrow['acc_headplaced_src']}) adjusted for net imports ({background_data_lastrow['acc_netimport_chicks_src']})"
      ,"acc_headslaughtered":f"Source: {background_data_lastrow['acc_headslaughtered_src']}"
      ,"acc_totalcarcweight_tonnes":f"Source: {background_data_lastrow['acc_totalcarcweight_tonnes_src']}"
      ,"acc_avgcarcweight_kg":"[Total Carcass Weight] / [Head Slaughtered]"

      ,"bod_dof_used":"Set by slider: days on feed"
      ,"bod_breedstdwt_kg":"Source: breed standard @ selected days on feed"
      ,"bod_breedstdyield_prpn":"Source: breed standard @ selected days on feed"
      ,"bod_breedstdcarcwt_kg":"[Breed Standard Live Weight] x [Breed Standard Carcass Yield]"
      ,"bod_referenceproduction_tonnes":"[Head Placed] x [Breed Standard Live Weight] x [Breed Standard Carcass Yield]"
      ,"bod_efficiency_tonnes":"Adjustment to breed standard potential according to achievable % (slider)"
      ,"bod_gmax_tonnes":"[Breed Standard Potential] + [Effect of Feed & Practices]"
      ,"bod_deathloss_tonnes":"[Head Placed] - [Head Slaughtered]"
      ,"bod_morbidity_tonnes":"[Achievable without Disease] - [Mortality & Condemns] - [Realised Production]"
      ,"bod_realizedproduction_tonnes":f"Source: {background_data_lastrow['acc_totalcarcweight_tonnes_src']}"
      ,"bod_totalburden_tonnes":"[Mortality & Condemns] + [Morbidity]"

      ,"producerprice_usdperkg":"Set by slider: Price to producers"
      ,"bod_totalburden_usd":"[Total Burden of Disease (tonnes)] x 1000 x [Producer Price (USD per kg)]"
      ,"rationprice_usdpertonne":"Set by slider: Ration price"
      ,"wb_gdp_usd":"Source: World Bank"

      ,"acc_feedcost_usdperkglive":f"Source: {background_data_lastrow['acc_feedcost_usdperkglive_src']}"
      ,"acc_chickcost_usdperkglive":f"Source: {background_data_lastrow['acc_chickcost_usdperkglive_src']}"
      ,"acc_laborcost_usdperkglive":f"Source: {background_data_lastrow['acc_laborcost_usdperkglive_src']}"
      ,"acc_landhousingcost_usdperkglive":f"Source: {background_data_lastrow['acc_landhousingcost_usdperkglive_src']}"
      ,"acc_medcost_usdperkglive":f"Source: {background_data_lastrow['acc_medcost_usdperkglive_src']}"
      ,"acc_othercost_usdperkglive":f"Source: {background_data_lastrow['acc_othercost_usdperkglive_src']}"

      ,"ideal_headplaced":"Animals required to match realised production if there were no mortality or morbidity"
      ,"ideal_fcr":"Set by slider: ideal feed conversion ratio"
      ,"ideal_feed_tonnes":"Feed required to match realised production at zero mortality and ideal FCR"
      ,"rationprice_usdpertonne":"Set by slider: feed price"
      ,"ideal_feedcost_usdperkglive":"[Ideal Feed Consumption] x [Feed Price]"
      ,"ideal_chickcost_usdperkglive":"Actual chick cost reduced proportionally with ideal head placed / actual head placed"
      ,"ideal_landhousingcost_usdperkglive":"Actual land & housing cost reduced proportionally with ideal head placed / actual head placed"
      ,"ideal_laborcost_usdperkglive":"Actual labor cost reduced proportionally with ideal land & housing cost"
      ,"ideal_medcost_usdperkglive":"Actual medicine cost reduced proportionally with ideal head placed / actual head placed"
      ,"ideal_othercost_usdperkglive":"Actual other cost reduced proportionally with ideal head placed / actual head placed"
    }

    return [
            html.H4(f"Data for {country}"),
            # html.P('All currently processed data.  Unformatted and unfiltered.'),
            #html.P(' '.join(df['id'].tolist())),
            dash_table.DataTable(
                columns=[{"name": j, "id": i} for i, j in columns_to_display_with_labels.items()],
                data=background_data.to_dict('records'),
                export_format="csv",
                sort_action = 'native',
                # #filter_action="native",
                style_cell={
                    # 'minWidth': '250px',
                    'font-family':'sans-serif',
                    },
                style_table={'overflowX': 'scroll'},

                # Source tooltip and styling
                # Hover-over for column headers
                tooltip_header=column_tooltips,
                tooltip_delay=1500,
                tooltip_duration=50000,

                # Underline columns with tooltips
                style_header_conditional=[{
                    'if': {'column_id': col},
                    'textDecoration': 'underline',
                    'textDecorationStyle': 'dotted',
                    } for col in list(column_tooltips)],
            )
        ]

@gbadsDash.callback(
    Output('poultry-breed-data', 'children'),
    Input('select-country-poultry','value'),
    )
def update_breed_data_poultry(country):
    breed_label_touse = poultry_lookup_breed_from_country[country]
    breed_df_touse = poultry_lookup_breed_df[breed_label_touse]

    columns_to_display_with_labels = {
      'dayonfeed':'Day on Feed'
      ,'bodyweight_g':'Live Weight (g)'
      ,'cmlfeedintake_g':'Cml Feed Intake (g)'
      ,'fcr':'FCR'
      ,'pct_yield':'Carcass Yield'
    }
    # breed_df_touse = breed_df_touse.transpose()

    # Subset columns
    breed_df_touse = breed_df_touse[list(columns_to_display_with_labels)]

    # breed_df_touse = breed_df_touse.transpose()

    # Format numbers
    breed_df_touse.update(breed_df_touse[['dayonfeed' ,'bodyweight_g' ,'cmlfeedintake_g']].applymap('{:,.0f}'.format))
    breed_df_touse.update(breed_df_touse[['pct_yield']].applymap('{:,.1f}%'.format))
    breed_df_touse.update(breed_df_touse[['fcr']].applymap('{:,.2f}'.format))

    return [
            html.H4(f"{breed_label_touse} Breed Standard"),
            dash_table.DataTable(
                columns=[{"name": j, "id": i} for i, j in columns_to_display_with_labels.items()],
                data=breed_df_touse.to_dict('records'),
                export_format="csv",
                style_cell={
                    'font-family':'sans-serif',
                    },
            )
        ]

# ------------------------------------------------------------------------------
#### -- Figures
# ------------------------------------------------------------------------------
# Update waterfall chart
@gbadsDash.callback(
    Output('poultry-waterfall','figure'),
    Input('core-data-poultry','data'),
    Input('select-metric-poultry', 'value'),
    Input('select-country-poultry','value'),
    Input('select-year-poultry','value'),
    Input('producer-price-slider-poultry','value')
    )
def update_waterfall_poultry(input_json, metric, country, year, producerprice):
    # Dash callback input data is a string that names a json file
    # First read it into a dataframe
    input_df = pd.read_json(input_json, orient='split')

    # Structure for plot
    waterfall_df = prep_bod_forwaterfall(input_df ,USDPERKG=producerprice)

    # Apply country and year filters
    waterfall_df = waterfall_df.loc[(waterfall_df['country'] == country) & (waterfall_df['year'] == year)]

    x = waterfall_df['Component']
    y = waterfall_df[metric]

    # Burden of disease
    mortality = waterfall_df.loc[waterfall_df['Component'] == 'Mortality & Condemns', metric ].iloc[0]
    morbidity = waterfall_df.loc[waterfall_df['Component'] == 'Morbidity', metric].iloc[0]
    BOD = abs(mortality + morbidity)

    if metric.upper() == 'TONNES':
      text = [f"{i:,.0f}" for i in waterfall_df[metric]]
      BOD = '{:,.0f}'.format(BOD)
      BOD = BOD + ' tonnes'
      axis_title = 'Tonnes carcass weight'
      axis_format = ''
    elif metric.upper() == 'US DOLLARS':
      text = [f"${i:,.0f}" for i in waterfall_df[metric]]
      BOD = '${:,.0f} USD'.format(BOD)
      axis_title = 'US dollars'
      axis_format = ''
    elif metric.upper() == 'PERCENT OF GDP':
      text = [f"{i:.3%}" for i in waterfall_df[metric]]
      BOD = '{:,.3%}'.format(BOD)
      BOD = BOD + ' of GDP'
      axis_title = 'Percent of GDP'
      axis_format = '~%'
    elif metric.upper() == 'PERCENT OF BREED STANDARD':
      text = [f"{i:.2%}" for i in waterfall_df[metric]]
      BOD = '{:,.2%}'.format(BOD)
      BOD = BOD + ' of Breed Standard'
      axis_title = 'Percent of Breed Standard'
      axis_format = '~%'
    elif metric.upper() == 'PERCENT OF REALISED PRODUCTION':
      text = [f"{i:.2%}" for i in waterfall_df[metric]]
      BOD = '{:,.2%}'.format(BOD)
      BOD = BOD + ' of Breed Standard'
      axis_title = 'Percent of Realised Production'
      axis_format = '~%'


    fig = create_waterfall(x, y, text)
    fig.update_layout(title_text=f'Poultry Production | {country}, {year} <br><sup>Burden of disease: {BOD} lost production (Mortality & Condemns + Morbidity)</sup>'
                      ,font_size=15
                      ,yaxis_title=axis_title
                      ,yaxis_tickformat=axis_format
                      )

    # Adjust color for Effect of Feed and Practices bar if negative
    if (waterfall_df.loc[waterfall_df['Component'] == 'Effect of Feed & Practices', metric].iloc[0]) < 0:
        fig.add_shape(
        type="rect",
        fillcolor="#E84C3D",
        line=dict(color="#E84C3D",
                  width=.5),
        opacity=1,
        x0=0.6,
        x1=1.4,
        xref="x",
        y0=fig.data[0].y[0],
        y1=fig.data[0].y[0] + fig.data[0].y[1],
        yref="y"
        )


    # Adjust color of Breed Standard Potential bar
    fig.add_shape(
    type="rect",
    fillcolor="#3598DB",
    line=dict(color="#3598DB",
              width=.5),
    opacity=1,
    x0=-0.4,
    x1=0.4,
    xref="x",
    y0=0.0,
    y1=fig.data[0].y[0],
    yref="y"
    )

    # Adjust color of Realised production bar
    fig.add_shape(
    type="rect",
    fillcolor="#2DCC70",
    line=dict(color="#2DCC70",
              width=.5),
    opacity=1,
    x0=3.6,
    x1=4.4,
    xref="x",
    y0=0.0,
    y1=fig.data[0].y[-1], yref="y"
    )

    fig.add_annotation(x=2, xref='x',         # x position is absolute on axis
                      y=0, yref='paper',     # y position is relative [0,1] to work regardless of scale
                      text="Source: GBADs",
                      showarrow=False,
                      yshift=10,
                      font=dict(
                          family="Helvetica",
                          size=18,
                          color="black"
                          )
                      )
    return fig

# Update Waterfall footnote
@gbadsDash.callback(
    Output('waterfall-footnote-poultry','children'),
    Input('select-country-poultry','value')
    )
def update_waterfall_footnote_poultry(country):
    breed_label_touse = poultry_lookup_breed_from_country[country]
    display_text = f"*Using {breed_label_touse} breed standard for {country}"
    return display_text

# # Update Sankey diagram
# @gbadsDash.callback(
#    Output('poultry-sankey','figure'),
#    Input('core-data-poultry','data'),
#    Input('select-metric-poultry', 'value'),
#    Input('select-country-poultry','value'),
#    Input('select-year-poultry','value'),
#    Input('achievable-pct-slider-poultry','value'),
#    Input('dof-slider-poultry','value')
#    )
# def update_sankey_poultry(input_json, metric, country, year, achievable, dof):
#    # Dash callback input data is a string that names a json file
#    # First read it into a dataframe
#    input_df = pd.read_json(input_json, orient='split')

#    # Structure for plot
#    sankey_df = prep_bod_forsankey(input_df)

#    # Apply country and year filters
#    sankey_df = sankey_df.loc[(sankey_df['country'] == country) & (sankey_df['year'] == year)]

#    ### UPDATE SANKEY ###
#    # This creates indexes to be used in the Sankey diagram
#    label_list = sankey_df['Component'].unique().tolist() + sankey_df['Component Source'].unique().tolist()

#    label_idx_dict = {}
#    for idx, label in enumerate(label_list):
#       label_idx_dict[label] = idx
#    label_idx_dict

#    sankey_df['Component_idx'] = sankey_df['Component'].map(label_idx_dict)
#    sankey_df['Component_Source_idx'] = sankey_df['Component Source'].map(label_idx_dict)

#    # Create source, target, and value lists
#    source = sankey_df['Component_Source_idx'].tolist()
#    target = sankey_df['Component_idx'].tolist()
#    values = sankey_df['Tonnes'].tolist()
#    print('Checking source value')
#    print(source)

#    n = len(sankey_df['Component_Source_idx'])

#    # Define node colors based on feature name and selected achievable % of breed standard
#    # Define x,y to move the burden of disease node down
#    # if achievable == 100:
#    #     color = ("white","white","#5BC0DE","#333333","#A66999","#333333","#F7931D","#98C193","#F7C42A")
#    #     x = [np.nan, np.nan, np.nan, np.nan, np.nan, .47, np.nan]
#    #     y = [np.nan, np.nan, np.nan, np.nan, np.nan, .95, np.nan]
#    # elif achievable < 100:
#    #     color = ("white","white","#5BC0DE","#333333","#A66999","#333333","#F7931D","#98C193","#F7C42A")
#    #     x = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, .47]
#    #     y = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, .95]
#    # else:
#    #     color = ("white","#5BC0DE","#333333","#A66999","#333333","#F7931D","white","#98C193","#F7C42A")
#    #     x = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, .47]
#    #     y = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, .95]
#    if country == 'United Kingdom' and achievable == 100:
#        color = ("white","white","#5BC0DE","#333333","#A66999","#333333","#F7931D","#98C193","#F7C42A")
#        x = [np.nan, np.nan, np.nan, np.nan, np.nan, .47, np.nan]
#        y = [np.nan, np.nan, np.nan, np.nan, np.nan, .95, np.nan]
#    elif country == 'United Kingdom' and achievable < 100:
#        color = ("white","white","#5BC0DE","#333333","#A66999","#333333","#F7931D","#98C193","#F7C42A")
#        x = [.33, np.nan, np.nan, np.nan, np.nan, np.nan, .47]
#        y = [.86, np.nan, np.nan, np.nan, np.nan, np.nan, .95]
#    elif country == 'United States of America' and dof == 60 and achievable < 93:
#        color = ("white","white","#5BC0DE","#333333","#A66999","#333333","#F7931D","#98C193","#F7C42A")
#        x = [np.nan, np.nan, np.nan, np.nan, np.nan, .47]
#        y = [np.nan, np.nan, np.nan, np.nan, np.nan, .95]
#    elif country == 'United States of America' and dof == 60 and achievable < 100:
#        color = ("white","white","#5BC0DE","#333333","#A66999","#333333","#F7931D","#98C193","#F7C42A")
#        x = [.33, np.nan, np.nan, np.nan, np.nan, np.nan, .47]
#        y = [.86, np.nan, np.nan, np.nan, np.nan, np.nan, .95]
#    elif country == 'United States of America' and dof == 60 and achievable == 100:
#        color = ("white","white","#5BC0DE","#333333","#A66999","#333333","#F7931D","#98C193","#F7C42A")
#        x = [np.nan, np.nan, np.nan, np.nan, np.nan, .47]
#        y = [np.nan, np.nan, np.nan, np.nan, np.nan, .95]
#    else:
#        color = ("white","#5BC0DE","#333333","#A66999","#333333","#F7931D","white","#98C193","#F7C42A")
#        x = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, .47]
#        y = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, .95]

#    sankey_fig = create_sankey(label_list, color, x, y, source, target, values, n)

#    sankey_fig.update_layout(title_text=f'Poultry | Production and burden of disease in {metric} <br><sup>{country}, {year}</sup>'
#                      ,font_size=15
#                      )

#    return sankey_fig

# Update Stacked bar chart
@gbadsDash.callback(
    Output('poultry-stacked-bar','figure'),
    Input('core-data-poultry','data'),
    Input('select-country-poultry','value'),
    Input('select-year-poultry','value'),
    )
def update_stacked_bar_poultry(input_json, country, year):

    input_df = pd.read_json(input_json, orient='split')

    # -----------------------------------------------------------------------------
    # Base plot
    # -----------------------------------------------------------------------------
    # Structure for plot
    stackedbar_df = prep_bod_forstackedbar_poultry(input_df)

    # Apply country and year filters
    stackedbar_df = stackedbar_df.loc[(stackedbar_df['country'] == country) & (stackedbar_df['year'] == year)]

    x = stackedbar_df['opt_or_act']
    y = stackedbar_df['cost_usdperkglive']
    color = stackedbar_df['Cost Item']
    poultry_bar_fig = create_stacked_bar_poultry(stackedbar_df, x, y, color)

    # Burden of disease
    BOD = stackedbar_df.loc[stackedbar_df['cost_item'] == 'bod_costs' ,'cost_usdperkglive'].values[0]

    poultry_bar_fig.update_layout(title_text=f'Poultry Costs | {country}, {year}<br><sup>Burden of disease: ${BOD :.2f} increased cost per kg live weight</sup>',
                                font_size=15)

    # # -----------------------------------------------------------------------------
    # # Add connecting lines
    # # -----------------------------------------------------------------------------
    # optactcost_1_t = costs_poultry.set_index('Costs').transpose().reset_index(drop=True)
    # optactcost_1_t_dict = optactcost_1_t.to_dict()

    # for i in range(0,1):
    #     for j, _ in enumerate(optactcost_1_t_dict):
    #         y1 = 0
    #         y2 = 0
    #         for key in list(optactcost_1_t_dict.keys())[:j+1]:
    #             y1 += optactcost_1_t_dict[key][i]
    #             y2 += optactcost_1_t_dict[key][i+1]

    #         poultry_bar_fig.add_trace(go.Scatter(
    #             # x=[0.25, 0.75],
    #             x = [optactcost_2['opt_or_act'][i],optactcost_2['opt_or_act'][i+6]],
    #             # x0 = optactcost_2['opt_or_act'][i],
    #             # x1 = optactcost_2['opt_or_act'][i+5],
    #             # x0=swine_bar_fig.data[1].y[0],
    #             y=[y1, y2],
    #             mode="lines",
    #             showlegend=False,
    #             line={'dash': 'dot', 'color': "#7A7A7A"}
    #         ))

    return poultry_bar_fig


# ==============================================================================
#### UPDATE SWINE
# ==============================================================================
# ------------------------------------------------------------------------------
#### -- Controls
# ------------------------------------------------------------------------------
# Update regions based on region contry aligment selection:
@gbadsDash.callback(
    Output(component_id='select-region-swine', component_property='options'),
    Input(component_id='Region-country-alignment-swine', component_property='value'),
    )
def update_region_options_swine(region_country):
    if region_country == "WOAH":
        options = WOAH_region_options
    elif region_country =="FAO":
        options = fao_region_options
    elif region_country == "World Bank":
        options = wb_region_options
    return options

# Update country options based on region selection
@gbadsDash.callback(
    Output(component_id='select-country-swine', component_property='options'),
    Input(component_id='Region-country-alignment-swine', component_property='value'),
    Input(component_id='select-region-swine', component_property='value'),
    )
def update_country_options_swine(region_country, region):
    if region_country == "WOAH":
        if region == "All":
            options = country_options_swine
        elif region == "Africa":
            options = WOAH_africa_options
        elif region == "Americas":
            options = WOAH_americas_options
        elif region == "Asia & the Pacific":
            options = WOAH_asia_options
        else:
            options = WOAH_europe_options
    elif region_country =="FAO":
        if region == "All":
            options = country_options_swine
        elif region == "Africa":
            options = fao_africa_options
        elif region == "Asia":
            options = fao_asia_options
        elif region == "Europe and Central Asia":
            options = fao_eca_options
        elif region == "Latin America and the Caribbean":
            options = fao_lac_options
        else:
            options = fao_swp_options
    elif region_country == "World Bank":
        if region == "All":
            options = country_options_swine
        elif region == "Sub-Saharan Africa":
            options = wb_africa_options
        elif region == "Europe & Central Asia":
            options = wb_eca_options
        elif region == "Latin America & the Caribbean":
            options = wb_lac_options
        elif region == "North America":
            options = wb_na_options
        else:
            options = wb_southasia_options

    return options

# Set slider starting values and add reference underneath based on selected country
# Also enable "Reset to Default" button
@gbadsDash.callback(
    Output('dof-slider-swine', 'value'),
    Input(component_id='reset-val-swine', component_property='n_clicks')   # Reset to defaults button
    )
def reset_daysonfeed_swine(reset):
    return dof_swine_default

# @gbadsDash.callback(
#     Output('dof-slider-swine', 'value'),
#     Output('reference-dof-swine', 'children'),
#     Input('select-country-swine', 'value'),
#     Input('select-year-swine', 'value'),
#     Input(component_id='reset-val-swine', component_property='n_clicks')   # Reset to defaults button
#     )
# def show_ref_daysonfeed_swine(country, year, reset):
#     input_df = gbads_pigs_merged_fordash
#     _rowselect = (input_df['country'] == country) & (input_df['year'] == year)
#     datavalue = input_df.loc[_rowselect ,'acc_avgdaysonfeed'].values[0]
#     country_shortname = country_shortnames[country]
#     if pd.isnull(datavalue):
#       slider = dof_swine_default
#       display = '(no data)'
#     else:
#       slider = round(datavalue ,0)
#       display = f'{datavalue:.0f} days'
#     return slider, f'Average for {country_shortname} in {year}: {display}'

# @gbadsDash.callback(
#    Output('feed-slider-swine', 'value'),
#    Output('reference-feedintake-swine', 'children'),
#    Input('select-country-swine', 'value'),
#    Input('select-year-swine', 'value'),
#    Input(component_id='reset-val-swine', component_property='n_clicks')   # Reset to defaults button
#    )
# def show_ref_feedintake_swine(country, year, reset):
#    input_df = gbads_pigs_merged_fordash
#    _rowselect = (input_df['country'] == country) & (input_df['year'] == year)
#    datavalue = input_df.loc[_rowselect ,'acc_avgfeedintake_kgperhd'].values[0]
#    country_shortname = country_shortnames[country]
#    if pd.isnull(datavalue):
#       slider = feed_swine_default
#       display = '(no data)'
#    else:
#       slider = round(datavalue ,1)
#       display = f'{datavalue:.1f} kg'
#    return slider, f'Average for {country_shortname} in {year}: {display}'

@gbadsDash.callback(
    Output('achievable-weight-slider-swine', 'value'),
    Output('reference-liveweight-swine', 'children'),
    Input('select-country-swine', 'value'),
    Input('select-year-swine', 'value'),
    Input(component_id='reset-val-swine', component_property='n_clicks')   # Reset to defaults button
    )
def show_ref_liveweight_swine(country, year, reset):
    input_df = gbads_pigs_merged_fordash
    _rowselect = (input_df['country'] == country) & (input_df['year'] == year)
    datavalue = input_df.loc[_rowselect ,'acc_avgliveweight_kg'].values[0]
    country_shortname = country_shortnames[country]
    if pd.isnull(datavalue):
      slider = achievable_weight_swine_default
      display = '(no data)'
    else:
      slider = round(datavalue * 1.1 ,0)   # 10% higher than actual
      display = f'{datavalue:.1f} kg'
    return slider, f'Average for {country_shortname} in {year}: {display}'

@gbadsDash.callback(
    Output('producer-price-slider-swine', 'value'),
    Output('reference-producerprice-swine', 'children'),
    Input('select-country-swine', 'value'),
    Input('select-year-swine', 'value'),
    Input(component_id='reset-val-swine', component_property='n_clicks')   # Reset to defaults button
    )
def show_ref_producerprice_swine(country, year, reset):
    input_df = gbads_pigs_merged_fordash
    _rowselect = (input_df['country'] == country) & (input_df['year'] == year)
    datavalue = input_df.loc[_rowselect ,'acc_producerprice_usdperkgcarc'].values[0]
    country_shortname = country_shortnames[country]
    if pd.isnull(datavalue):
      slider = producer_price_swine_default
      display = '(no data)'
    else:
      slider = round(datavalue ,2)
      display = f'${datavalue:.2f}'
    return slider, f'Average for {country_shortname} in {year}: {display}'

@gbadsDash.callback(
    Output('ration-price-slider-swine', 'value'),
    Output('reference-feedprice-swine', 'children'),
    Input('select-country-swine', 'value'),
    Input('select-year-swine', 'value'),
    Input(component_id='reset-val-swine', component_property='n_clicks')   # Reset to defaults button
    )
def show_ref_feedprice_swine(country, year, reset):
    input_df = gbads_pigs_merged_fordash
    _rowselect = (input_df['country'] == country) & (input_df['year'] == year)
    datavalue = input_df.loc[_rowselect ,'acc_feedprice_usdpertonne'].values[0]
    country_shortname = country_shortnames[country]
    if pd.isnull(datavalue):
      slider = ration_price_swine_default
      display = '(no data)'
    else:
      slider = round(datavalue ,2)
      display = f'${datavalue:.2f}'
    return slider, f'Average for {country_shortname} in {year}: {display}'

# Using Breed Standard FCR as reference
@gbadsDash.callback(
    Output('fcr-slider-swine', 'value'),
    Output('reference-fcr-swine', 'children'),
    Input('select-country-swine', 'value'),
    Input('dof-slider-swine', 'value'),
    Input(component_id='reset-val-swine', component_property='n_clicks')   # Reset to defaults button
    )
def show_ref_fcr_swine(country, dof, reset):
    breed_label_touse = swine_lookup_breed_from_country[country]
    breed_df_touse = swine_lookup_breed_df[breed_label_touse]
    _rowselect = (breed_df_touse['dayonfeed'] == dof)
    datavalue = breed_df_touse.loc[_rowselect ,'cml_fcr'].values[0]
    if pd.isnull(datavalue):
      slider = fcr_swine_default
      display = '(no data)'
    else:
      slider = round(datavalue ,2)
      display = f'{datavalue:.2f}'
    return slider, f'Breed standard: {display}'

# ------------------------------------------------------------------------------
#### -- Data
# ------------------------------------------------------------------------------
# MUST HAPPEN FIRST: Calculate burden of disease components on core data

# Using Achievable Percent and Days on Feed
#!!! Make sure appropriate sliders are activated in LAYOUT!
# @gbadsDash.callback(
#     Output('core-data-swine','data'),
#     Input('achievable-pct-slider-swine','value'),
#     Input('dof-slider-swine','value')
#     )
# def update_core_data_swine(achievable_pct ,avg_dof):
#     swine_data_withbod = bod_calcs.calc_bod_master_swine(
#       gbads_pigs_merged_fordash
#       ,ACHIEVABLE_PCT_MASTER=achievable_pct
#       ,AVG_DOF_MASTER=avg_dof
#       ,BREED_DF_MASTER=swinebreedstd_pic_growthandfeed   # Data frame with breed reference information. Must contain columns 'dayonfeed' and 'bodyweight_g'.
#       ,AVG_CARC_YIELD_MASTER=0.75                        # Float [0, 1]: average carcass yield in kg meat per kg live weight
#     )
#     swine_data_withbod['year'] = swine_data_withbod['year'].astype(str)   # Change Year type to text
#     return swine_data_withbod.to_json(date_format='iso', orient='split')

# Alternative call using ACHIEVABLE WEIGHT instead of ACHIEVABLE PERCENT
#!!! Make sure appropriate sliders are activated in LAYOUT!
@gbadsDash.callback(
    Output('core-data-swine','data'),
    Input('achievable-weight-slider-swine','value'),
    Input('dof-slider-swine','value'),
    Input('ration-price-slider-swine','value'),
    Input('fcr-slider-swine','value')
    )
def update_core_data_swine(achievable_wt ,avg_dof ,feedprice ,fcr):
    swine_data_withbod = bod.calc_bod_master_swine(
        gbads_pigs_merged_fordash
        ,ACHIEVABLE_WT_KG_MASTER=achievable_wt             # Float: achievable weight without disease
        ,AVG_DOF_MASTER=avg_dof                            # Integer [1, 176]: Average days on feed. Will lookup breed standard weight for this day on feed.
        ,BREED_DF_MASTER=swinebreedstd_pic_growthandfeed   # Data frame with breed reference information. Must contain columns 'dayonfeed' and 'bodyweight_g'.
        ,AVG_CARC_YIELD_MASTER=0.75                        # Float [0, 1]: average carcass yield in kg meat per kg live weight
        ,FEEDPRICE_USDPERTONNE_MASTER=feedprice           # Float
        ,IDEAL_FCR_LIVE_MASTER=fcr                        # Float: ideal FCR per kg live weight
    )
    swine_data_withbod['year'] = swine_data_withbod['year'].astype(str)   # Change Year type to text
    return swine_data_withbod.to_json(date_format='iso', orient='split')

# Alternative call using Feed Intake instead of Days on Feed to determine standard
#!!! Make sure appropriate sliders are activated in LAYOUT!
# @gbadsDash.callback(
#     Output('core-data-swine','data'),
#     Input('achievable-weight-slider-swine','value'),
#     Input('feed-slider-swine','value')
#     )
# def update_core_data_swine(achievable_wt ,avg_feedint):
#     swine_data_withbod = bod.calc_bod_master_swine(
#          gbads_pigs_merged_fordash
#          ,ACHIEVABLE_WT_KG_MASTER=achievable_wt             # Float: achievable weight without disease
#          ,AVG_FEEDINT_KG_MASTER=avg_feedint                 # Float: average feed intake in kg per head
#          ,BREED_DF_MASTER=swinebreedstd_pic_growthandfeed   # Data frame with breed reference information. Must contain columns 'dayonfeed' and 'bodyweight_g'.
#          ,AVG_CARC_YIELD_MASTER=0.75                        # Float [0, 1]: average carcass yield as proportion of live weight
#     )
#     swine_data_withbod['year'] = swine_data_withbod['year'].astype(str)   # Change Year type to text
#     return swine_data_withbod.to_json(date_format='iso', orient='split')

# Can happen in any order after update_core_data
# These update when user changes filtering (country and year)
# Update data table to show user
@gbadsDash.callback(
    Output('swine-background-data', 'children'),
    Input('core-data-swine','data'),
    Input('select-country-swine','value'),
    Input('producer-price-slider-swine','value'),
    Input('ration-price-slider-swine','value'),
    )
def update_background_data_swine(input_json, country ,producerprice ,rationprice):
    # Dash callback input data is a string that names a json file
    # First read it into a dataframe
    input_df = pd.read_json(input_json, orient='split')
    background_data = input_df.loc[(input_df['country'] == country)]

    # Add slider values as columns to display
    background_data['producerprice_usdperkg'] = producerprice
    background_data['rationprice_usdpertonne'] = rationprice
    background_data['bod_totalburden_usd'] = background_data['bod_totalburden_tonnes'] * 1000 \
      * background_data['producerprice_usdperkg']

    columns_to_display_with_labels = {
      'country':'Country'
      ,'year':'Year'

      ,'acc_breedingsows':'Breeding Sows'
      # ,'acc_headfarrowed':'Head Farrowed'
      ,'acc_headweaned':'Head Weaned'
      ,'acc_headplaced':'Head Placed'
      ,'acc_headslaughtered':'Head Slaughtered'
      ,'acc_totalcarcweight_tonnes':'Total Carcass Weight (tonnes)'   # Equal to bod_realizedproduction_tonnes
      ,'acc_avgcarcweight_kg':'Avg. Carcass Weight (kg)'
      # ,'acc_avgliveweight_kg':'Avg Live Weight (kg)'
      # ,'acc_avgdaysonfeed':'Avg Days on Feed'   # Using input value rather than this column
      # ,'acc_feedconsumption_tonnes':'Total Feed Consumed (tonnes)'
      # ,'acc_avgfeedintake_kgperhd':'Avg. Feed Intake (kg per head)'

      ,'bod_dof_used':'Days on Feed'
      # ,'bod_feedint_used':'Feed Intake (kg per hd)'
      ,'bod_breedstdwt_kg':'Breed Standard Live Weight (kg)'
      ,'bod_breedstdyield_prpn':'Breed Standard Carcass Yield'
      ,'bod_breedstdcarcwt_kg':'Breed Standard Carcass Weight (kg)'
      ,'bod_referenceproduction_tonnes':'Breed Standard Potential (tonnes)'
      ,'bod_efficiency_tonnes':'Effect of Feed & Practices (tonnes)'
      ,'bod_gmax_tonnes':'Achievable without Disease (tonnes)'
      ,'bod_deathloss_tonnes':'Mortality & Condemns (tonnes)'
      ,'bod_morbidity_tonnes':'Morbidity (tonnes)'
      ,'bod_realizedproduction_tonnes':'Realised Production (tonnes)'
      ,'bod_totalburden_tonnes':'Total Burden of Disease (tonnes)'

      ,'producerprice_usdperkg':'Producer Price (USD per kg)'
      ,'bod_totalburden_usd':'Total Burden of Disease (USD)'
      # ,'wb_gdp_usd':'GDP (USD)'

      ,'acc_feedcost_usdperkgcarc':'Avg. Feed Cost (USD per kg carcass weight)'
      ,'acc_nonfeedvariablecost_usdperkgcarc':'Avg. Non-feed Variable Costs (USD per kg carcass weight)'
      ,'acc_laborcost_usdperkgcarc':'Avg. Labour Cost (USD per kg carcass weight)'
      ,'acc_landhousingcost_usdperkgcarc':'Avg. Land & Housing Cost (USD per kg carcass weight)'

      ,'ideal_headplaced':'Ideal Head Placed'
      ,'ideal_fcr':'Ideal FCR'
      ,'ideal_feed_tonnes':'Ideal Feed Consumption (tonnes)'
      ,'rationprice_usdpertonne':'Feed Price (USD per tonne)'
      ,'ideal_feedcost_usdperkgcarc':'Ideal Feed Cost (USD per kg carcass weight)'
      ,'ideal_nonfeedvariablecost_usdperkgcarc':'Ideal Non-feed Variable Costs (USD per kg carcass weight)'
      ,'ideal_laborcost_usdperkgcarc':'Ideal Labour Cost (USD per kg carcass weight)'
      ,'ideal_landhousingcost_usdperkgcarc':'Ideal Land & Housing Cost (USD per kg carcass weight)'
    }
    # ------------------------------------------------------------------------------
    # Format data to display in the table
    # ------------------------------------------------------------------------------
    # Order does not matter in these lists
    # Zero decimal places
    background_data.update(background_data[[
      'acc_breedingsows'
      ,'acc_headweaned'
      ,'acc_headplaced'
      ,'acc_headslaughtered'
      ,'acc_totalcarcweight_tonnes'
      # ,'acc_feedconsumption_tonnes'
      ,'bod_referenceproduction_tonnes'
      ,'bod_realizedproduction_tonnes'
      ,'bod_efficiency_tonnes'
      ,'bod_gmax_tonnes'
      ,'bod_deathloss_tonnes'
      ,'bod_morbidity_tonnes'
      ,'bod_totalburden_tonnes'
      ,'wb_gdp_usd'
      ,'ideal_headplaced'
      ,'ideal_feed_tonnes'
    ]].applymap('{:,.0f}'.format))

    # One decimal place
    background_data.update(background_data[[
      'bod_breedstdwt_kg'
      ,'bod_breedstdcarcwt_kg'
      ,'acc_avgcarcweight_kg'
      # ,'acc_avgfeedintake_kgperhd'
    ]].applymap('{:,.1f}'.format))

    # Two decimal places
    background_data.update(background_data[[
      'producerprice_usdperkg'
      ,'bod_totalburden_usd'
      ,'bod_breedstdyield_prpn'
      ,'rationprice_usdpertonne'
      ,'acc_feedcost_usdperkgcarc'
      ,'acc_nonfeedvariablecost_usdperkgcarc'
      ,'acc_laborcost_usdperkgcarc'
      ,'acc_landhousingcost_usdperkgcarc'
      ,'ideal_fcr'
      ,'ideal_feedcost_usdperkgcarc'
      ,'ideal_nonfeedvariablecost_usdperkgcarc'
      ,'ideal_laborcost_usdperkgcarc'
      ,'ideal_landhousingcost_usdperkgcarc'
    ]].applymap('{:,.2f}'.format))

    # ------------------------------------------------------------------------------
    # Hover-over text
    # ------------------------------------------------------------------------------
    # Read last row of data with filters applied to get source of each column.
    # For most countries and columns, source is the same for every year.
    # But if source differs for later years, want to report the latest.
    background_data_lastrow = background_data.iloc[-1 ,:]

    column_tooltips = {
      'acc_breedingsows':f"Source: {background_data_lastrow['acc_breedingsows_src']}"
      # ,"acc_headfarrowed":f"Breeding sows ({background_data_lastrow['acc_headfarrowed_src']}) x (Avg litter size) x (Avg litters per sow per year)"
      ,"acc_headweaned":f"[Breeding Sows] x Pigs weaned per sow per year ({background_data_lastrow['acc_litters_persow_peryear_src']})"
      ,"acc_headplaced":f"[Head Weaned] adjusted for net imports ({background_data_lastrow['acc_netimport_gte50kg_src']})"
      ,"acc_headslaughtered":f"Source: {background_data_lastrow['acc_headslaughtered_src']}"
      ,"acc_totalcarcweight_tonnes":f"Source: {background_data_lastrow['acc_totalcarcweight_tonnes_src']}"
      ,"acc_avgcarcweight_kg":"[Realised Production] / [Head Slaughtered]"
      # ,"acc_feedconsumption_tonnes":f"Source: {background_data_lastrow['acc_feedconsumption_tonnes_src']}"
      ,"acc_avgfeedintake_kgperhd":f"[Total Feed Consumed] / [Head Slaughtered], adjusted for feed consumed by head that died"

      ,"bod_dof_used":"Set by slider: days on feed"
      ,'bod_feedint_used':"Set by slider: average feed intake"
      ,"bod_breedstdwt_kg":"Source: breed standard @ selected days on feed"
      ,"bod_breedstdyield_prpn":"Overall average"
      ,"bod_breedstdcarcwt_kg":"[Breed Standard Live Weight] x [Standard Carcass Yield]"
      ,"bod_referenceproduction_tonnes":"[Head Placed] x [Breed Standard Live Weight] x Avg. carcass yield"
      ,"bod_realizedproduction_tonnes":f"Source: {background_data_lastrow['acc_totalcarcweight_tonnes_src']}"
      ,"bod_efficiency_tonnes":"Adjustment to breed standard potential according to achievable weight (slider)"
      ,"bod_gmax_tonnes":"[Breed Standard Potential] + [Effect of Feed & Practices]"
      ,"bod_deathloss_tonnes":"[Head Placed] - [Head Slaughtered]"
      ,"bod_morbidity_tonnes":"[Achievable without Disease] - [Mortality & Condemns] - [Realised Production]"
      ,"bod_totalburden_tonnes":"[Mortality & Condemns] + [Morbidity]"

      ,"producerprice_usdperkg":"Set by slider: Price to producers"
      ,"bod_totalburden_usd":"[Total Burden of Disease (tonnes)] x 1000 x [Producer Price (USD per kg)]"
      ,"rationprice_usdpertonne":"Set by slider: Ration price"
      ,"wb_gdp_usd":"Source: World Bank"

      ,"acc_feedcost_usdperkgcarc":f"Source: {background_data_lastrow['acc_feedcost_usdperkgcarc_src']}"
      ,"acc_nonfeedvariablecost_usdperkgcarc":f"Source: {background_data_lastrow['acc_nonfeedvariablecost_usdperkgcarc_src']}"
      ,"acc_laborcost_usdperkgcarc":f"Source: {background_data_lastrow['acc_laborcost_usdperkgcarc_src']}"
      ,"acc_landhousingcost_usdperkgcarc":f"Source: {background_data_lastrow['acc_landhousingcost_usdperkgcarc_src']}"

      ,"ideal_headplaced":"Animals required to match realised production if there were no mortality or morbidity"
      ,"ideal_fcr":"Set by slider: ideal feed conversion ratio"
      ,"ideal_feed_tonnes":"Feed required to match realised production at zero mortality and ideal FCR"
      ,"rationprice_usdpertonne":"Set by slider: feed price"
      ,"ideal_feedcost_usdperkgcarc":"[Ideal Feed Consumption] x [Feed Price]"
      ,"ideal_nonfeedvariablecost_usdperkgcarc":"Actual non-feed variable cost reduced proportionally with ideal head placed / actual head placed"
      ,"ideal_landhousingcost_usdperkgcarc":"Actual land & housing cost reduced proportionally with ideal head placed / actual head placed"
      ,"ideal_laborcost_usdperkgcarc":"Actual labor cost reduced proportionally with ideal land & housing cost"
    }

    return [
            html.H4(f"Data for {country}"),
            dash_table.DataTable(
                columns=[{"name": j, "id": i} for i, j in columns_to_display_with_labels.items()],
                data=background_data.to_dict('records'),
                export_format="csv",
                sort_action = 'native',
                style_cell={
                    # 'minWidth': '250px',
                    'font-family':'sans-serif',
                    },
                style_table={'overflowX': 'scroll'},

                # Hover-over for column headers
                tooltip_header=column_tooltips,
                tooltip_delay=1500,
                tooltip_duration=50000,

                # Underline columns with tooltips
                style_header_conditional=[{
                    'if': {'column_id': col},
                    'textDecoration': 'underline',
                    'textDecorationStyle': 'dotted',
                    } for col in list(column_tooltips)],
            )
        ]

@gbadsDash.callback(
    Output('swine-breed-data', 'children'),
    Input('core-data-swine','data')   # Currently only one breed used, so no inputs needed. But Dash wants an input here.
    )
def update_breed_data_swine(breed):
    columns_to_display_with_labels = {
      'dayonfeed':'Day on Feed'
      ,'bodyweight_kg':'Live Weight (kg)'
      ,'cml_feedintake_kg':'Cml Feed Intake (kg)'
      ,'cml_fcr':'FCR'
    }
    breed_data = swinebreedstd_pic_growthandfeed.copy()

    # Subset columns
    breed_data = breed_data[list(columns_to_display_with_labels)]

    # Format numbers
    breed_data.update(breed_data[['dayonfeed']].applymap('{:,.0f}'.format))
    breed_data.update(breed_data[['bodyweight_kg' ,'cml_feedintake_kg']].applymap('{:,.1f}'.format))
    breed_data.update(breed_data[['cml_fcr']].applymap('{:,.2f}'.format))

    return [
            html.H4("PIC Breed Standard"),
            dash_table.DataTable(
                columns=[{"name": j, "id": i} for i, j in columns_to_display_with_labels.items()],
                data=breed_data.to_dict('records'),
                export_format="csv",
                style_cell={
                    # 'minWidth': '250px',
                    'font-family':'sans-serif',
                    },
            )
        ]

# ------------------------------------------------------------------------------
#### -- Figures
# ------------------------------------------------------------------------------
# Update waterfall chart
@gbadsDash.callback(
    Output('swine-waterfall','figure'),
    Input('core-data-swine','data'),
    Input('select-metric-swine', 'value'),
    Input('select-country-swine','value'),
    Input('select-year-swine','value'),
    Input('producer-price-slider-swine','value')
    )
def update_waterfall_swine(input_json, metric, country, year, producerprice):
    # Dash callback input data is a string that names a json file
    # First read it into a dataframe
    input_df = pd.read_json(input_json, orient='split')

    # Structure for plot
    waterfall_df = prep_bod_forwaterfall(input_df ,USDPERKG=producerprice)

    # Apply country and year filters
    waterfall_df = waterfall_df.loc[(waterfall_df['country'] == country) & (waterfall_df['year'] == year)]

    ### JR: Simplified plot spec after calcs moved to prep_bod_forwaterfall()
    x = waterfall_df['Component']
    y = waterfall_df[metric]

    # Burden of disease
    mortality = waterfall_df.loc[waterfall_df['Component'] == 'Mortality & Condemns', metric].iloc[0]
    morbidity = waterfall_df.loc[waterfall_df['Component'] == 'Morbidity', metric].iloc[0]
    BOD = abs(mortality + morbidity)

    if metric.upper() == 'TONNES':
      text = [f"{i:,.0f}" for i in waterfall_df[metric]]
      BOD = '{:,.0f}'.format(BOD)
      BOD = BOD + ' tonnes'
      axis_title = 'Tonnes carcass weight'
      axis_format = ''
    elif metric.upper() == 'US DOLLARS':
      text = [f"${i:,.0f}" for i in waterfall_df[metric]]
      BOD = '${:,.0f} USD'.format(BOD)
      axis_title = 'US dollars'
      axis_format = ''
    elif metric.upper() == 'PERCENT OF GDP':
      text = [f"{i:.3%}" for i in waterfall_df[metric]]
      BOD = '{:,.3%}'.format(BOD)
      BOD = BOD + ' of GDP'
      axis_title = 'Percent of GDP'
      axis_format = '~%'
    elif metric.upper() == 'PERCENT OF BREED STANDARD':
      text = [f"{i:.2%}" for i in waterfall_df[metric]]
      BOD = '{:,.2%}'.format(BOD)
      BOD = BOD + ' of Breed Standard'
      axis_title = 'Percent of Breed Standard'
      axis_format = '~%'
    elif metric.upper() == 'PERCENT OF REALISED PRODUCTION':
      text = [f"{i:.2%}" for i in waterfall_df[metric]]
      BOD = '{:,.2%}'.format(BOD)
      BOD = BOD + ' of Breed Standard'
      axis_title = 'Percent of Realised Production'
      axis_format = '~%'

    fig = create_waterfall(x, y, text)

    fig.update_layout(title_text=f'Swine Production | {country}, {year} <br><sup>Burden of disease: {BOD} lost production (Mortality & Condemns + Morbidity)</sup>'
                      ,font_size=15
                      ,yaxis_title=axis_title
                      ,yaxis_tickformat=axis_format
                      )

    # Adjust color for Effect of Feed and Practices bar if negative
    if (waterfall_df.loc[waterfall_df['Component'] == 'Effect of Feed & Practices', metric].iloc[0]) < 0:
        fig.add_shape(
        type="rect",
        fillcolor="#E84C3D",
        line=dict(color="#E84C3D",
                  width=.5),
        opacity=1,
        x0=0.6,
        x1=1.4,
        xref="x",
        y0=fig.data[0].y[0],
        y1=fig.data[0].y[0] + fig.data[0].y[1],
        yref="y"
        )

    # Adjust color of Breed Standard Potential bar
    fig.add_shape(
    type="rect",
    fillcolor="#3598DB",
    line=dict(color="#3598DB",
              width=.5),
    opacity=1,
    x0=-0.4,
    x1=0.4,
    xref="x",
    y0=0.0,
    y1=fig.data[0].y[0],
    yref="y"
    )

    # Add outline to Realised production bar
    fig.add_shape(
    type="rect",
    fillcolor="#2DCC70",
    line=dict(color="#2DCC70",
              width=.5),
    opacity=1,
    x0=3.6,
    x1=4.4,
    xref="x",
    y0=0.0,
    y1=fig.data[0].y[-1],
    yref="y"
    )

    fig.add_annotation(x=2, xref='x',         # x position is absolute on axis
                      y=0, yref='paper',     # y position is relative [0,1] to work regardless of scale
                      text="Source: GBADs",
                      showarrow=False,
                      yshift=10,
                      font=dict(
                          family="Helvetica",
                          size=18,
                          color="black"
                          )
                      )
    return fig

# # Update Sankey diagram
# @gbadsDash.callback(
#    Output('swine-sankey','figure'),
#    Input('core-data-swine','data'),
#    Input('select-metric-swine', 'value'),
#    Input('select-country-swine','value'),
#    Input('select-year-swine','value'),
#    Input('achievable-weight-slider-swine','value'),
#    Input('feed-slider-swine','value')
#    # Input('dof-slider-swine','value')
#    )
# def update_sankey_swine(input_json, metric, country, year, achievable, dof):
#    # Dash callback input data is a string that names a json file
#    # First read it into a dataframe
#    input_df = pd.read_json(input_json, orient='split')

#    # Structure for plot
#    sankey_df = prep_bod_forsankey(input_df)

#    # Apply country and year filters
#    sankey_df = sankey_df.loc[(sankey_df['country'] == country) & (sankey_df['year'] == year)]

#    ### UPDATE SANKEY ###
#    # This creates indexes to be used in the Sankey diagram
#    label_list = sankey_df['Component'].unique().tolist() + sankey_df['Component Source'].unique().tolist()

#    label_idx_dict = {}
#    for idx, label in enumerate(label_list):
#       label_idx_dict[label] = idx
#    label_idx_dict

#    sankey_df['Component_idx'] = sankey_df['Component'].map(label_idx_dict)
#    sankey_df['Component_Source_idx'] = sankey_df['Component Source'].map(label_idx_dict)

#    # Create source, target, and value lists
#    source = sankey_df['Component_Source_idx'].tolist()
#    target = sankey_df['Component_idx'].tolist()
#    values = sankey_df['Tonnes'].tolist()
#    print('Checking source value')
#    print(source)

#    n = len(sankey_df['Component_Source_idx'])

#    # JR: commenting-out code to set color, x, and y based on inputs
#    color = ("white","white","#5BC0DE","#333333","#A66999","#7A7A7A","#FE9666","#75AC6F","#FFB703")
#    x = [np.nan, np.nan, np.nan, np.nan, np.nan, .47, np.nan]
#    y = [np.nan, np.nan, np.nan, np.nan, np.nan, .95, np.nan]

#    # Define node colors based on feature name and selected achievable % of breed standard
#    if country == 'United Kingdom' and achievable == 100:
#        color = ("white","white","#5BC0DE","#333333","#A66999","#333333","#F7931D","#98C193","#F7C42A")
#        x = [np.nan, np.nan, np.nan, np.nan, np.nan, .47, np.nan]
#        y = [np.nan, np.nan, np.nan, np.nan, np.nan, .95, np.nan]
#    elif country == 'United Kingdom' and achievable < 100:
#        color = ("white","white","#5BC0DE","#333333","#A66999","#333333","#F7931D","#98C193","#F7C42A")
#        x = [.33, np.nan, np.nan, np.nan, np.nan, np.nan, .47]
#        y = [.86, np.nan, np.nan, np.nan, np.nan, np.nan, .95]
#    elif country == 'United States of America' and dof == 60 and achievable < 93:
#        color = ("white","white","#5BC0DE","#333333","#A66999","#333333","#F7931D","#98C193","#F7C42A")
#        x = [np.nan, np.nan, np.nan, np.nan, np.nan, .47]
#        y = [np.nan, np.nan, np.nan, np.nan, np.nan, .95]
#    elif country == 'United States of America' and dof == 60 and achievable < 100:
#        color = ("white","white","#5BC0DE","#333333","#A66999","#333333","#F7931D","#98C193","#F7C42A")
#        x = [.33, np.nan, np.nan, np.nan, np.nan, np.nan, .47]
#        y = [.86, np.nan, np.nan, np.nan, np.nan, np.nan, .95]
#    elif country == 'United States of America' and dof == 60 and achievable == 100:
#        color = ("white","white","#5BC0DE","#333333","#A66999","#333333","#F7931D","#98C193","#F7C42A")
#        x = [np.nan, np.nan, np.nan, np.nan, np.nan, .47]
#        y = [np.nan, np.nan, np.nan, np.nan, np.nan, .95]
#    else:
#        color = ("white","#5BC0DE","#333333","#A66999","#333333","#F7931D","white","#98C193","#F7C42A")
#        x = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, .47]
#        y = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, .95]

#    sankey_fig = create_sankey(label_list, color, x, y, source, target, values, n)
#    sankey_fig.update_layout(title_text=f'Swine | Production and burden of disease in {metric} <br><sup>{country}, {year}</sup>'
#                      ,font_size=15
#                      )

#    return sankey_fig

# Update Stacked bar chart
@gbadsDash.callback(
    Output('swine-stacked-bar','figure'),
    Input('core-data-swine','data'),
    Input('select-country-swine','value'),
    Input('select-year-swine','value'),
    )
def update_stacked_bar_swine(input_json, country, year):

    input_df = pd.read_json(input_json, orient='split')

    # -----------------------------------------------------------------------------
    # Base plot
    # -----------------------------------------------------------------------------
    # Structure for plot
    stackedbar_df = prep_bod_forstackedbar_swine(input_df)

    # Apply country and year filters
    stackedbar_df = stackedbar_df.loc[(stackedbar_df['country'] == country) & (stackedbar_df['year'] == year)]

    x = stackedbar_df['opt_or_act']
    y = stackedbar_df['cost_usdperkgcarc']
    color = stackedbar_df['Cost Item']
    swine_bar_fig = create_stacked_bar_swine(stackedbar_df, x, y, color)

    # Burden of disease
    BOD = stackedbar_df.loc[stackedbar_df['cost_item'] == 'bod_costs' ,'cost_usdperkgcarc'].values[0]

    swine_bar_fig.update_layout(title_text=f'Swine Costs | {country}, {year}<br><sup>Burden of disease: ${BOD :.2f} increased cost per kg carcass weight</sup>',
                                font_size=15)


    # # -----------------------------------------------------------------------------
    # # Add connecting lines
    # # -----------------------------------------------------------------------------
    # optactcost_1_t = costs_swine.set_index('Costs').transpose().reset_index(drop=True)
    # optactcost_1_t_dict = optactcost_1_t.to_dict()

    # for i in range(0,1):
    #     for j, _ in enumerate(optactcost_1_t_dict):
    #         y1 = 0
    #         y2 = 0
    #         for key in list(optactcost_1_t_dict.keys())[:j+1]:
    #             y1 += optactcost_1_t_dict[key][i]
    #             y2 += optactcost_1_t_dict[key][i+1]

    #         swine_bar_fig.add_trace(go.Scatter(
    #             # x=[0.25, 0.75],
    #             x = [optactcost_2['opt_or_act'][i],optactcost_2['opt_or_act'][i+6]],
    #             # x0 = optactcost_2['opt_or_act'][i],
    #             # x1 = optactcost_2['opt_or_act'][i+5],
    #             # x0=swine_bar_fig.data[1].y[0],
    #             y=[y1, y2],
    #             mode="lines",
    #             showlegend=False,
    #             line={'dash': 'dot', 'color': "#7A7A7A"}
    #         ))

    return swine_bar_fig

# ==============================================================================
#### UPDATE ETHIOPIA
# ==============================================================================
# ------------------------------------------------------------------------------
#### -- Controls
# ------------------------------------------------------------------------------
# Update agesex group options based on species
@gbadsDash.callback(
    Output('select-agesex-ecs', 'options'),
    Input('select-species-ecs', 'value'),
    )
def update_age_options_ecs(species):
    if species == "Cattle":
        options = ecs_agesex_options
    else:
        options = ecs_agesex_options.copy()
        for d in options:
            if d['value'] == 'Oxen':
                options.remove(d)
    return options

# Update production system options based on species
@gbadsDash.callback(
    Output('select-prodsys-ecs', 'options'),
    Output('select-prodsys-ecs', 'value'),
    Input('select-species-ecs', 'value'),
    )
def update_prodsys_options_ecs(species):
    # Get unique production systems for selected species
    unique_prodsys = np.sort(ecs_ahle_summary.loc[ecs_ahle_summary['species'] == species ,'production_system'].unique())
    options = [{'label': i, 'value': i} for i in unique_prodsys]
    value = options[0]['value']  # Default is first one
    return options, value

# Remove improvement option from scenario for cattle and poultry while those are misssing
@gbadsDash.callback(
    Output('select-compare-ecs', 'options'),
    Input('select-species-ecs', 'value'),
    )
def update_compare_options_ecs(species):
    if species == "Cattle" or species == 'All Poultry' or species == 'Poultry hybrid' or species == 'Poultry indigenous':
        options = ecs_compare_options.copy()
        for d in options:
            if d['value'] == 'Improvement':
                options.remove(d)
    else:
        options = ecs_compare_options
    return options

# Update hierarchy dropdown filters to remove higher level selections from the options
@gbadsDash.callback(
    Output('select-dd-1-attr-ecs','options'),
    Output('select-dd-1-attr-ecs','value'),
    Input('select-top-lvl-attr-ecs','value'),
    )
def update_dd1_options_ecs(top_lvl_hierarchy):
    options = ecs_hierarchy_dd_attr_options.copy()
    for d in options:
        if d['value'] == top_lvl_hierarchy:
            d['disabled']=True
        else:
            d['disabled']=False

    value='production_system'

    return options, value


@gbadsDash.callback(
    Output('select-dd-2-attr-ecs','options'),
    Input('select-top-lvl-attr-ecs','value'),
    Input('select-dd-1-attr-ecs','value'),
    )
def update_dd2_options_ecs(top_lvl_hierarchy, dd1_hierarchy):
    options = ecs_hierarchy_dd_attr_options
    for d in options:
        if d['value'] != 'None':
            if d['value'] == top_lvl_hierarchy or d['value'] == dd1_hierarchy:
                d['disabled']= True
            else:
                d['disabled']=False
    return options

@gbadsDash.callback(
    Output('select-dd-3-attr-ecs','options'),
    Input('select-top-lvl-attr-ecs','value'),
    Input('select-dd-1-attr-ecs','value'),
    Input('select-dd-2-attr-ecs','value'),
    )
def update_dd3_options_ecs(top_lvl_hierarchy, dd1_hierarchy, dd2_hierarchy):
    options = ecs_hierarchy_dd_attr_options
    for d in options:
        if d['value'] != 'None':
            if d['value'] == top_lvl_hierarchy or d['value'] == dd1_hierarchy or d['value'] == dd2_hierarchy:
                d['disabled']= True
            else:
                d['disabled']=False
    return options

@gbadsDash.callback(
    Output('select-dd-4-attr-ecs','options'),
    Input('select-top-lvl-attr-ecs','value'),
    Input('select-dd-1-attr-ecs','value'),
    Input('select-dd-2-attr-ecs','value'),
    Input('select-dd-3-attr-ecs','value'),
    )
def update_dd4_options_ecs(top_lvl_hierarchy, dd1_hierarchy, dd2_hierarchy, dd3_hierarchy):
    options = ecs_hierarchy_dd_attr_options
    for d in options:
        if d['value'] != 'None':
            if d['value'] == top_lvl_hierarchy or d['value'] == dd1_hierarchy or d['value'] == dd2_hierarchy or d['value'] == dd3_hierarchy:
                d['disabled']= True
            else:
                d['disabled']=False
    return options

# @gbadsDash.callback(
#     Output('select-dd-5-attr-ecs','options'),
#     Input('select-top-lvl-attr-ecs','value'),
#     Input('select-dd-1-attr-ecs','value'),
#     Input('select-dd-2-attr-ecs','value'),
#     Input('select-dd-3-attr-ecs','value'),
#     Input('select-dd-4-attr-ecs','value'),
#     )
# def update_dd5_options_ecs(top_lvl_hierarchy, dd1_hierarchy, dd2_hierarchy, dd3_hierarchy, dd4_hierarchy):
#     options = ecs_hierarchy_dd_attr_options
#     for d in options:
#         if d['value'] != 'None':
#             if d['value'] == top_lvl_hierarchy or d['value'] == dd1_hierarchy or d['value'] == dd2_hierarchy or d['value'] == dd3_hierarchy or d['value'] == dd4_hierarchy:
#                 d['disabled']= True
#             else:
#                 d['disabled']=False
#     return options

# Enable the options for factor/improvement when 'Improvement' selected
@gbadsDash.callback(
    Output('select-factor-ecs','options'),
    Output('select-improve-ecs','options'),
    Input('select-compare-ecs','value'),
    )
def update_improvment_factors(compare):
    options1 = ecs_factor_options.copy()
    options2 = ecs_improve_options.copy()
    for d in options1:
        if compare == 'Improvement':
            if d['value'] != 'Lactation':
                d['disabled']=False
        else:
            d['disabled']=True
    for d in options2:
        if compare == 'Improvement':
            d['disabled']=False
        else:
            d['disabled']=True

    return options1, options2

# ------------------------------------------------------------------------------
#### -- Data
# ------------------------------------------------------------------------------
# # AHLE Data
# @gbadsDash.callback(
#     Output('core-data-ahle-ecs','data'),
#     Input('select-species-ecs','value'),
#     Input('select-prodsys-ecs','value'),
#     # Input('select-age-ecs','value'),
#     # Input('select-sex-ecs','value'),
#     Input('select-agesex-ecs', 'value'),
#     )
# # def update_core_data_ahle_ecs(species, prodsys, age, sex):
# def update_core_data_ahle_ecs(species, prodsys, agesex):
#     input_df = pd.read_csv(os.path.join(ECS_PROGRAM_OUTPUT_FOLDER ,'ahle_all_scensmry.csv'))

#     # Species filter
#     input_df = input_df.loc[(input_df['species'] == species)]

#     # Production System filter
#     # Rename values to match filters
#     input_df['production_system'] = input_df['production_system'].replace({'Overall': 'All Production Systems'})
#     input_df=input_df.loc[(input_df['production_system'] == prodsys)]

#     # Age filter
#     # if age == 'Adult' or age == "Juvenile" or age == "Neonatal" or age == "Oxen":
#     #     input_df=input_df.loc[(input_df['age_group'] == age)]
#     # elif age == "Overall Age":
#     #     input_df=input_df.loc[(input_df['age_group'] == 'Overall')]
#     # else:
#     #     input_df=input_df

#     # Sex filter
#     # if sex == 'Male' or sex == "Female":
#     #     input_df=input_df.loc[(input_df['sex'] == sex)]
#     # elif sex == "Overall Sex":
#     #     input_df=input_df.loc[(input_df['sex'] == 'Overall')]
#     # else:
#     #     input_df=input_df

#     # Age/sex filter
#     input_df=input_df.loc[(input_df['agesex_scenario'] == agesex)]

#     return input_df.to_json(date_format='iso', orient='split')

# AHLE datatable below graphic
# @gbadsDash.callback(
#     Output('ecs-ahle-datatable', 'children'),
#     Input('core-data-ahle-ecs','data'),
#     Input('select-currency-ecs','value'),
# )
# def update_ecs_ahle_data(input_json ,currency):
    # input_df = pd.read_json(input_json, orient='split')
@gbadsDash.callback(
    Output('ecs-ahle-datatable', 'children'),
    Input('select-species-ecs','value'),
    Input('select-prodsys-ecs','value'),
    Input('select-agesex-ecs', 'value'),
    # Input('core-data-ahle-ecs','data'),
    Input('select-currency-ecs','value'),
)
def update_ecs_ahle_data(species, prodsys, agesex, currency):
    input_df = pd.read_csv(os.path.join(ECS_PROGRAM_OUTPUT_FOLDER ,'ahle_all_scensmry.csv'))
    # Species filter
    input_df = input_df.loc[(input_df['species'] == species)]
    # Production System filter
    # Rename values to match filters
    input_df['production_system'] = input_df['production_system'].replace({'Overall': 'All Production Systems'})
    input_df=input_df.loc[(input_df['production_system'] == prodsys)]
    # Age/sex filter
    input_df=input_df.loc[(input_df['agesex_scenario'] == agesex)]




    # If currency is USD, use USD columns
    display_currency = 'Birr'
    if currency == 'USD':
        display_currency = 'USD'

        input_df['mean_current'] = input_df['mean_current_usd']
        input_df['stdev_current'] = input_df['stdev_current_usd']
        input_df['mean_mortality_zero'] = input_df['mean_mortality_zero_usd']
        input_df['stdev_mortality_zero'] = input_df['stdev_mortality_zero_usd']
        input_df['mean_ideal'] = input_df['mean_ideal_usd']
        input_df['stdev_ideal'] = input_df['stdev_ideal_usd']

    # Create AHLE columns
    input_df['mean_AHLE'] = input_df['mean_ideal'] - input_df['mean_current']
    input_df['mean_AHLE_mortality'] = input_df['mean_mortality_zero'] - input_df['mean_current']

    # Format numbers
    input_df.update(input_df[['mean_current',
                              'mean_ideal',
                              'mean_mortality_zero',
                              'mean_AHLE',
                              'mean_AHLE_mortality',]].applymap('{:,.0f}'.format))

    columns_to_display_with_labels = {
      'species':'Species'
      ,'production_system':'Production System'
      ,'item':'Value or Cost'
      # ,'age_group':'Age'
      # ,'sex':'Sex'
      ,'agesex_scenario':'Group'
      ,'mean_current':f'Current Mean ({display_currency})'
      ,'mean_ideal':f'Ideal Mean ({display_currency})'
      ,'mean_mortality_zero':f'Mortality Zero Mean ({display_currency})'
      ,'mean_AHLE':'AHLE (Ideal - Current)'
      ,'mean_AHLE_mortality':'AHLE due to Mortality (Mortality Zero - Current)'
    }

    # Subset columns
    input_df = input_df[list(columns_to_display_with_labels)]

    # Keep only items for the waterfall
    waterfall_plot_values = ('Value of Offtake',
                             'Value of Herd Increase',
                             'Value of draught',
                             'Value of Milk',
                             'Value of Eggs consumed',
                             'Value of Eggs sold',
                             'Value of Manure',
                             'Value of Hides',
                             'Feed Cost',
                             'Labour Cost',
                             'Health Cost',
                             'Capital Cost',
                             'Gross Margin')
    input_df = input_df.loc[input_df['item'].isin(waterfall_plot_values)]


    return [
            html.H4("AHLE Data"),
            dash_table.DataTable(
                columns=[{"name": j, "id": i} for i, j in columns_to_display_with_labels.items()],
                data=input_df.to_dict('records'),
                export_format="csv",
                style_cell={
                    # 'minWidth': '250px',
                    'font-family':'sans-serif',
                    },
                style_table={'overflowX': 'scroll'},
            )
        ]


# Attribution Data
@gbadsDash.callback(
    Output('core-data-attr-ecs','data'),
    Input('select-prodsys-ecs','value'),
    Input('select-species-ecs','value'),
    # Input('select-age-ecs','value'),
    # Input('select-sex-ecs','value'),
    )
# def update_core_data_attr_ecs(prodsys, age, sex):
def update_core_data_attr_ecs(prodsys, species):
    input_df = pd.read_csv(os.path.join(ECS_PROGRAM_OUTPUT_FOLDER ,'ahle_all_withattr.csv'))

    # Production System filter
    # If All production systems, don't filter. Attribution data is not aggregated to that level.
    if prodsys == 'All Production Systems':
        input_df=input_df
    else:
        input_df=input_df.loc[(input_df['production_system'] == prodsys)]

    # Species filter
    # Goat and Sheep do not appear separately. These get all small ruminants results.
    if species == 'Goat' or species == "Sheep":
        input_df=input_df.loc[(input_df['species'] == 'All Small Ruminants')]
    # Poultry subspecies do not appear separately. These get all poultry results.
    elif species == 'Poultry hybrid' or species == "Poultry indigenous":
        input_df=input_df.loc[(input_df['species'] == 'All Poultry')]
    else:
        input_df=input_df.loc[(input_df['species'] == species)]

    # Age filter
    # if age == 'Adult':
    #     if sex == 'Male':
    #         input_df=input_df.loc[(input_df['age_group'] == age)]
    #         input_df=input_df.loc[(input_df['sex'] == sex)]
    #     elif sex == "Female":
    #         input_df=input_df.loc[(input_df['age_group'] == age)]
    #         input_df=input_df.loc[(input_df['sex'] == sex)]
    #     else:
    #         input_df=input_df.loc[(input_df['age_group'] == age)]
    #         input_df=input_df
    # elif age == "Juvenile":
    #     if sex == 'Male':
    #         input_df=input_df.loc[(input_df['age_group'] == age)]
    #         input_df=input_df.loc[(input_df['sex'] == 'Overall')]
    #     elif sex == "Female":
    #         input_df=input_df.loc[(input_df['age_group'] == age)]
    #         input_df=input_df.loc[(input_df['sex'] == 'Overall')]
    #     else:
    #         input_df=input_df.loc[(input_df['age_group'] == age)]
    #         input_df=input_df.loc[(input_df['sex'] == 'Overall')]
    # elif age == "Neonatal":
    #     if sex == 'Male':
    #         input_df=input_df.loc[(input_df['age_group'] == age)]
    #         input_df=input_df.loc[(input_df['sex'] == 'Overall')]
    #     elif sex == "Female":
    #         input_df=input_df.loc[(input_df['age_group'] == age)]
    #         input_df=input_df.loc[(input_df['sex'] == 'Overall')]
    #     else:
    #         input_df=input_df.loc[(input_df['age_group'] == age)]
    #         input_df=input_df.loc[(input_df['sex'] == 'Overall')]
    # else:
    #     if sex == 'Male':
    #         input_df=input_df.loc[(input_df['sex'] == sex)]
    #     elif sex == "Female":
    #         input_df=input_df.loc[(input_df['sex'] == sex)]
    #     else:
    #         input_df=input_df

    # # Attribution filter
    # if attr == 'External':
    #     input_df=input_df.loc[(input_df['cause'] == attr)]
    # elif attr == "Infectious":
    #     input_df=input_df.loc[(input_df['cause'] == attr)]
    # elif attr == "Non-infectious":
    #     input_df=input_df.loc[(input_df['cause'] == attr)]
    # else:
    #     input_df=input_df

    return input_df.to_json(date_format='iso', orient='split')

# Attribution datatable below graphic
@gbadsDash.callback(
    Output('ecs-attr-datatable', 'children'),
    Input('core-data-attr-ecs','data'),   # Currently only one breed used, so no inputs needed. But Dash wants an input here.
    Input('select-currency-ecs','value'),
    )
def update_ecs_attr_data(input_json, currency):
    input_df = pd.read_json(input_json, orient='split')

    # If currency is USD, use USD columns
    display_currency = 'Birr'
    if currency == 'USD':
        display_currency = 'USD'

    # Format numbers
    input_df.update(input_df[['mean',
                              'sd',
                              'lower95',
                              'upper95',
                              ]].applymap('{:,.0f}'.format))
    # input_df.update(input_df[['pct_of_total']].applymap('{:,.2f}%'.format))

    columns_to_display_with_labels = {
      'species':'Species'
      ,'production_system':'Production System'
      ,'age_group':'Age'
      ,'sex':'Sex'
      ,'ahle_component':'AHLE Component'
      ,'cause':'Attribution'
      ,'mean':f'Mean ({display_currency})'
      ,'sd':'Std. Dev.'
      ,'lower95':'Lower 95%'
      ,'upper95':'Upper 95%'
      # ,'pct_of_total':'Percent of Total AHLE'
    }

    # Subset columns
    input_df = input_df[list(columns_to_display_with_labels)]

    return [
            html.H4("Attribution Data"),
            dash_table.DataTable(
                columns=[{"name": j, "id": i} for i, j in columns_to_display_with_labels.items()],
                data=input_df.to_dict('records'),
                export_format="csv",
                style_cell={
                    # 'minWidth': '250px',
                    'font-family':'sans-serif',
                    },
                style_table={'overflowX': 'scroll',
                              'height': '320px',
                              'overflowY': 'auto'},
                page_action='none',
            )
        ]


# ------------------------------------------------------------------------------
#### -- Figures
# ------------------------------------------------------------------------------
# AHLE Waterfall
# @gbadsDash.callback(
#     Output('ecs-ahle-waterfall','figure'),
#     Input('core-data-ahle-ecs','data'),
#     # Input('select-age-ecs','value'),
#     Input('select-agesex-ecs', 'value'),
#     Input('select-species-ecs','value'),
#     Input('select-display-ecs','value'),
#     Input('select-compare-ecs','value'),
#     Input('select-prodsys-ecs','value'),
#     # Input('select-sex-ecs','value'),
#     Input('select-currency-ecs','value'),
#     Input('select-factor-ecs','value'),
#     Input('select-improve-ecs','value'),
#     )
# # def update_ahle_waterfall_ecs(input_json, age, species, display, compare, prodsys, sex, currency, impvmnt_factor, impvmnt_value):
# def update_ahle_waterfall_ecs(input_json, agesex, species, display, compare, prodsys, currency, impvmnt_factor, impvmnt_value):
    # # Data
    # input_df = pd.read_json(input_json, orient='split')
@gbadsDash.callback(
    Output('ecs-ahle-waterfall','figure'),
    # Input('core-data-ahle-ecs','data'),
    Input('select-agesex-ecs', 'value'),
    Input('select-species-ecs','value'),
    Input('select-display-ecs','value'),
    Input('select-compare-ecs','value'),
    Input('select-prodsys-ecs','value'),
    Input('select-currency-ecs','value'),
    Input('select-factor-ecs','value'),
    Input('select-improve-ecs','value'),
    )
def update_ahle_waterfall_ecs(agesex, species, display, compare, prodsys, currency, impvmnt_factor, impvmnt_value):
    input_df = pd.read_csv(os.path.join(ECS_PROGRAM_OUTPUT_FOLDER ,'ahle_all_scensmry.csv'))
    # Species filter
    input_df = input_df.loc[(input_df['species'] == species)]
    # Production System filter
    # Rename values to match filters
    input_df['production_system'] = input_df['production_system'].replace({'Overall': 'All Production Systems'})
    input_df=input_df.loc[(input_df['production_system'] == prodsys)]
    # Age/sex filter
    input_df=input_df.loc[(input_df['agesex_scenario'] == agesex)]



    # Prep the data
    prep_df = prep_ahle_forwaterfall_ecs(input_df)

    # If currency is USD, use USD columns
    display_currency = 'Ethiopian Birr'
    if currency == 'USD':
        display_currency = 'USD'

        prep_df['mean_current']                     = prep_df['mean_current_usd']
        prep_df['mean_mortality_zero']              = prep_df['mean_mortality_zero_usd']
        prep_df['mean_ideal']                       = prep_df['mean_ideal_usd']
        prep_df['mean_AHLE']                        = prep_df['mean_AHLE_usd']
        prep_df['mean_AHLE_mortality']              = prep_df['mean_AHLE_mortality_usd']
        prep_df['mean_all_mort_25_imp']             = prep_df['mean_all_mort_25_imp_usd']
        prep_df['mean_all_mort_50_imp']             = prep_df['mean_all_mort_50_imp_usd']
        prep_df['mean_all_mort_75_imp']             = prep_df['mean_all_mort_75_imp_usd']
        prep_df['mean_all_mort_25_AHLE']            = prep_df['mean_all_mort_25_AHLE_usd']
        prep_df['mean_all_mort_50_AHLE']            = prep_df['mean_all_mort_50_AHLE_usd']
        prep_df['mean_all_mort_75_AHLE']            = prep_df['mean_all_mort_75_AHLE_usd']
        prep_df['mean_current_repro_25_imp']        = prep_df['mean_current_repro_25_imp_usd']
        prep_df['mean_current_repro_50_imp']        = prep_df['mean_current_repro_50_imp_usd']
        prep_df['mean_current_repro_75_imp']        = prep_df['mean_current_repro_75_imp_usd']
        prep_df['mean_current_repro_100_imp']       = prep_df['mean_current_repro_100_imp_usd']
        prep_df['mean_all_current_repro_25_AHLE']   = prep_df['mean_all_current_repro_25_AHLE_usd']
        prep_df['mean_all_current_repro_50_AHLE']   = prep_df['mean_all_current_repro_50_AHLE_usd']
        prep_df['mean_all_current_repro_75_AHLE']   = prep_df['mean_all_current_repro_75_AHLE_usd']
        prep_df['mean_all_current_repro_100_AHLE']  = prep_df['mean_all_current_repro_100_AHLE_usd']
        prep_df['mean_current_growth_25_imp_all']   = prep_df['mean_current_growth_25_imp_all_usd']
        prep_df['mean_current_growth_50_imp_all']   = prep_df['mean_current_growth_50_imp_all_usd']
        prep_df['mean_current_growth_75_imp_all']   = prep_df['mean_current_growth_75_imp_all_usd']
        prep_df['mean_current_growth_100_imp_all']  = prep_df['mean_current_growth_100_imp_all_usd']
        prep_df['mean_all_current_growth_25_AHLE']  = prep_df['mean_all_current_growth_25_AHLE_usd']
        prep_df['mean_all_current_growth_50_AHLE']  = prep_df['mean_all_current_growth_50_AHLE_usd']
        prep_df['mean_all_current_growth_75_AHLE']  = prep_df['mean_all_current_growth_75_AHLE_usd']
        prep_df['mean_all_current_growth_100_AHLE'] = prep_df['mean_all_current_growth_100_AHLE_usd']


    # Filters
    # if age == "Neonatal": # Removing value of hides for neonatal
    #     waterfall_plot_values = ('Value of Offtake',
    #                               'Value of Herd Increase',
    #                               'Value of Manure',
    #                               'Expenditure on Feed',
    #                               'Expenditure on Labour',
    #                               'Expenditure on Health',
    #                               'Expenditure on Housing',
    #                               'Expenditure on Capital',
    #                               'Gross Margin')
    #     prep_df = prep_df.loc[prep_df['item'].isin(waterfall_plot_values)]
    #     measure = ["relative", "relative", "relative", "relative", "relative", "relative", "relative", "relative", "total"]
    # elif age == 'Overall Age' and sex == 'Overall Sex':
    #     if species == "Cattle": # Cattle have draught and milk added for overall groups
    #         waterfall_plot_values = ('Value of Offtake',
    #                                  'Value of Herd Increase',
    #                                  'Value of Draught',
    #                                  'Value of Milk',
    #                                  'Value of Manure',
    #                                  'Value of Hides',
    #                                  'Expenditure on Feed',
    #                                  'Expenditure on Labour',
    #                                  'Expenditure on Health',
    #                                  'Expenditure on Housing',
    #                                  'Expenditure on Capital',
    #                                  'Gross Margin')
    #         prep_df = prep_df.loc[prep_df['item'].isin(waterfall_plot_values)]
    #         measure = ["relative", "relative", "relative", "relative", "relative", "relative", "relative", "relative", "relative", "relative", "relative", "total"]
    #     else: # all species have milk added for overall groups
    #         waterfall_plot_values = ('Value of Offtake',
    #                                  'Value of Herd Increase',
    #                                  'Value of Milk',
    #                                  'Value of Manure',
    #                                  'Value of Hides',
    #                                  'Expenditure on Feed',
    #                                  'Expenditure on Labour',
    #                                  'Expenditure on Health',
    #                                  'Expenditure on Housing',
    #                                  'Expenditure on Capital',
    #                                  'Gross Margin')
    #         prep_df = prep_df.loc[prep_df['item'].isin(waterfall_plot_values)]
    #         measure = ["relative", "relative", "relative", "relative", "relative", "relative", "relative", "relative", "relative", "relative", "total"]
    # else:
    #     measure = ["relative", "relative", "relative", "relative", "relative", "relative", "relative", "relative", "relative", "total"]

    if species == "Cattle":     # Cattle have draught
        waterfall_plot_values = ('Value of Offtake',
                                 'Value of Herd Increase',
                                 'Value of Draught',
                                 'Value of Milk',
                                 'Value of Manure',
                                 'Value of Hides',
                                 'Expenditure on Feed',
                                 'Expenditure on Labour',
                                 'Expenditure on Health',
                                 'Expenditure on Housing',
                                 'Expenditure on Capital',
                                 'Gross Margin')
        prep_df = prep_df.loc[prep_df['item'].isin(waterfall_plot_values)]
        measure = ["relative", "relative", "relative", "relative", "relative", "relative", "relative", "relative", "relative", "relative", "relative", "total"]
    elif 'POULTRY' in species.upper():   # Poultry have value of eggs, do not have manure or hides
        waterfall_plot_values = ('Value of Offtake',
                                 'Value of Herd Increase',
                                 'Value of Eggs consumed',
                                 'Value of Eggs sold',
                                 'Expenditure on Feed',
                                 'Expenditure on Labour',
                                 'Expenditure on Health',
                                 'Expenditure on Housing',
                                 'Expenditure on Capital',
                                 'Gross Margin')
        prep_df = prep_df.loc[prep_df['item'].isin(waterfall_plot_values)]
        measure = ["relative", "relative", "relative", "relative", "relative", "relative", "relative", "relative", "relative", "total"]
    else:
        waterfall_plot_values = ('Value of Offtake',
                                 'Value of Herd Increase',
                                 'Value of Milk',
                                 'Value of Manure',
                                 'Value of Hides',
                                 'Expenditure on Feed',
                                 'Expenditure on Labour',
                                 'Expenditure on Health',
                                 'Expenditure on Housing',
                                 'Expenditure on Capital',
                                 'Gross Margin')
        prep_df = prep_df.loc[prep_df['item'].isin(waterfall_plot_values)]
        measure = ["relative", "relative", "relative", "relative", "relative", "relative", "relative", "relative", "relative", "relative", "total"]


    x = prep_df['item']

    # display and Compare filters
    if display == "Difference (AHLE)":
        # Applying the condition
        prep_df["item"] = np.where(prep_df["item"] == "Gross Margin", "Gross Margin (AHLE)", prep_df["item"])
        x = prep_df['item']
        if compare == 'Ideal':
            y = prep_df['mean_AHLE']
        elif compare == 'Zero Mortality':
            y = prep_df['mean_AHLE_mortality']
        else:
            compare = impvmnt_factor + "- " + impvmnt_value
            if impvmnt_factor == 'Mortality' and impvmnt_value == '25%':
                y = prep_df['mean_all_mort_25_AHLE']
            elif impvmnt_factor == 'Mortality' and impvmnt_value == '50%':
                y = prep_df['mean_all_mort_50_AHLE']
            elif impvmnt_factor == 'Mortality' and impvmnt_value == '75%':
                y = prep_df['mean_all_mort_75_AHLE']
            elif impvmnt_factor == 'Mortality' and impvmnt_value == '100%':
                y = prep_df['mean_AHLE_mortality']
            elif impvmnt_factor == 'Parturition Rate' and impvmnt_value == '25%':
                y = prep_df['mean_all_current_repro_25_AHLE']
            elif impvmnt_factor == 'Parturition Rate' and impvmnt_value == '50%':
                y = prep_df['mean_all_current_repro_50_AHLE']
            elif impvmnt_factor == 'Parturition Rate' and impvmnt_value == '75%':
                y = prep_df['mean_all_current_repro_75_AHLE']
            elif impvmnt_factor == 'Parturition Rate' and impvmnt_value == '100%':
                y = prep_df['mean_all_current_repro_100_AHLE']
            elif impvmnt_factor == 'Live Weight' and impvmnt_value == '25%':
                y = prep_df['mean_all_current_growth_25_AHLE']
            elif impvmnt_factor == 'Live Weight' and impvmnt_value == '50%':
                y = prep_df['mean_all_current_growth_50_AHLE']
            elif impvmnt_factor == 'Live Weight' and impvmnt_value == '75%':
                y = prep_df['mean_all_current_growth_75_AHLE']
            elif impvmnt_factor == 'Live Weight' and impvmnt_value == '100%':
                y = prep_df['mean_all_current_growth_100_AHLE']

        # Create graph
        name = 'AHLE'
        ecs_waterfall_fig = create_ahle_waterfall_ecs(prep_df, name, measure, x, y)
        # Add title
        ecs_waterfall_fig.update_layout(
            # title_text=f'Animal Health Loss Envelope (AHLE) | {species} <br><sup>Difference between {compare} and Current scenario using {prodsys} for {age} and {sex}</sup><br>',
            title_text=f'Values and Costs (Difference) | {species}, {prodsys} <br><sup>Difference between Current and {compare} scenario applied to {agesex}</sup><br>',
            yaxis_title=display_currency,
            font_size=15,
            margin=dict(t=100)
            )
    else:
        if compare == 'Ideal':
            y = prep_df['mean_ideal']
            name = "Ideal (solid)"
            # Create graph
            ecs_waterfall_fig = create_ahle_waterfall_ecs(prep_df, name, measure, x, y)
            # Add current with lag
            ecs_waterfall_fig.add_trace(go.Waterfall(
                name = 'Current (outline)',
                measure = measure,
                x = x,
                y = prep_df['mean_current'],
                decreasing = {"marker":{"color":"white", "line":{"color":"#E84C3D", "width":3}}},
                increasing = {"marker":{"color":"white", "line":{"color":"#3598DB", "width":3}}},
                totals = {"marker":{"color":"white", "line":{"color":"#F7931D", "width":3}}},
                connector = {"line":{"dash":"dot"}},
                customdata=prep_df['mean_current'],
                ))
            ecs_waterfall_fig.update_layout(
                waterfallgroupgap = 0.5,
                )
            # Add title
            ecs_waterfall_fig.update_layout(
                # title_text=f'Animal Health Loss Envelope ({display}) | {species} <br><sup>{compare} and Current scenario using {prodsys} for {age} and {sex}</sup><br>',
                title_text=f'Values and Costs | {species}, {prodsys} <br><sup>Current vs. {compare} scenario applied to {agesex}</sup><br>',
                yaxis_title=display_currency,
                font_size=15,
                margin=dict(t=100),
                legend=dict(orientation="h",
                            xanchor="right",
                            x=1,
                            yanchor="bottom",
                            y=1.02,)
                )

        elif compare == 'Zero Mortality':
            y = prep_df['mean_mortality_zero']
            name = 'Zero Mortality (solid)'
            # Create graph
            ecs_waterfall_fig = create_ahle_waterfall_ecs(prep_df, name, measure, x, y)
            # Add current with lag
            ecs_waterfall_fig.add_trace(go.Waterfall(
                name = 'Current (outline)',
                measure = measure,
                x = x,
                y = prep_df['mean_current'],
                decreasing = {"marker":{"color":"white", "line":{"color":"#E84C3D", "width":3}}},
                increasing = {"marker":{"color":"white", "line":{"color":"#3598DB", "width":3}}},
                totals = {"marker":{"color":"white", "line":{"color":"#F7931D", "width":3}}},
                connector = {"line":{"dash":"dot"}},
                customdata=prep_df['mean_current'],
                ))
            ecs_waterfall_fig.update_layout(
                waterfallgroupgap = 0.5,
                )
            # Add title
            ecs_waterfall_fig.update_layout(
                # title_text=f'Animal Health Loss Envelope ({display}) | {species} <br><sup>{compare} and Current scenario using {prodsys} for {age} and {sex}</sup><br>',
                title_text=f'Values and Costs | {species}, {prodsys} <br><sup>Current vs. {compare} scenario applied to {agesex}</sup><br>',
                yaxis_title=display_currency,
                font_size=15,
                margin=dict(t=100),
                legend=dict(orientation="h",
                            xanchor="right",
                            x=1,
                            yanchor="bottom",
                            y=1.02,)
                )

        else:
            if impvmnt_factor == 'Mortality' and impvmnt_value == '25%':
                y = prep_df['mean_all_mort_25_imp']
            elif impvmnt_factor == 'Mortality' and impvmnt_value == '50%':
                y = prep_df['mean_all_mort_50_imp']
            elif impvmnt_factor == 'Mortality' and impvmnt_value == '75%':
                y = prep_df['mean_all_mort_75_imp']
            elif impvmnt_factor == 'Mortality' and impvmnt_value == '100%':
                y = prep_df['mean_mortality_zero']
            elif impvmnt_factor == 'Parturition Rate' and impvmnt_value == '25%':
                y = prep_df['mean_current_repro_25_imp']
            elif impvmnt_factor == 'Parturition Rate' and impvmnt_value == '50%':
                y = prep_df['mean_current_repro_50_imp']
            elif impvmnt_factor == 'Parturition Rate' and impvmnt_value == '75%':
                y = prep_df['mean_current_repro_75_imp']
            elif impvmnt_factor == 'Parturition Rate' and impvmnt_value == '100%':
                y = prep_df['mean_current_repro_100_imp']
            elif impvmnt_factor == 'Live Weight' and impvmnt_value == '25%':
                y = prep_df['mean_current_growth_25_imp_all']
            elif impvmnt_factor == 'Live Weight' and impvmnt_value == '50%':
                y = prep_df['mean_current_growth_50_imp_all']
            elif impvmnt_factor == 'Live Weight' and impvmnt_value == '75%':
                y = prep_df['mean_current_growth_75_imp_all']
            elif impvmnt_factor == 'Live Weight' and impvmnt_value == '100%':
                y = prep_df['mean_current_growth_100_imp_all']

            name = impvmnt_factor + "- " + impvmnt_value + " (solid)"
            # Create graph
            ecs_waterfall_fig = create_ahle_waterfall_ecs(prep_df, name, measure, x, y)
            # Add current with lag
            ecs_waterfall_fig.add_trace(go.Waterfall(
                name = 'Current (outline)',
                measure = measure,
                x = x,
                y = prep_df['mean_current'],
                decreasing = {"marker":{"color":"white", "line":{"color":"#E84C3D", "width":3}}},
                increasing = {"marker":{"color":"white", "line":{"color":"#3598DB", "width":3}}},
                totals = {"marker":{"color":"white", "line":{"color":"#F7931D", "width":3}}},
                connector = {"line":{"dash":"dot"}},
                customdata=prep_df['mean_current'],
                ))
            ecs_waterfall_fig.update_layout(
                waterfallgroupgap = 0.5,
                )
            # Add title
            ecs_waterfall_fig.update_layout(
                # title_text=f'Animal Health Loss Envelope ({display}) | {species} <br><sup>{compare} and Current scenario using {prodsys} for {age} and {sex}</sup><br>',
                title_text=f'Values and Costs | {species}, {prodsys} <br><sup>Current vs. {compare} scenario applied to {agesex}</sup><br>',
                yaxis_title=display_currency,
                font_size=15,
                margin=dict(t=100),
                legend=dict(orientation="h",
                            xanchor="right",
                            x=1,
                            yanchor="bottom",
                            y=1.02,)
                )

    # Add tooltip
    if currency == 'Birr':
        ecs_waterfall_fig.update_traces(hovertemplate='Category: %{x}'+
                                        '<br>Value: %{customdata:,.0f} Birr<extra></extra>'+
                                        '<br>Cumulative Value: %{y:,.0f} Birr'
                                        )
                                        
    elif currency == 'USD':
        ecs_waterfall_fig.update_traces(hovertemplate='Category: %{x}'+
                                        '<br>Value: %{customdata:,.0f} USD<extra></extra>'+
                                        '<br>Cumulative Value: %{y:,.0f} USD'
                                        )
    else:
        ecs_waterfall_fig.update_traces(hovertemplate='Category: %{x}'+
                                        '<br>Value: %{customdata:,.0f} <extra></extra>'+
                                        '<br>Cumulative Value: %{y:,.0f} '
                                        )

    return ecs_waterfall_fig


# Attribution Treemap
@gbadsDash.callback(
    Output('ecs-attr-treemap','figure'),
    Input('core-data-attr-ecs','data'),
    Input('select-prodsys-ecs','value'),
    Input('select-species-ecs','value'),
    # Input('select-age-ecs','value'),
    # Input('select-sex-ecs','value'),
    Input('select-currency-ecs','value'),
    Input('select-top-lvl-attr-ecs','value'),
    Input('select-dd-1-attr-ecs','value'),
    Input('select-dd-2-attr-ecs','value'),
    Input('select-dd-3-attr-ecs','value'),
    Input('select-dd-4-attr-ecs','value'),
    )
# def update_attr_treemap_ecs(input_json, prodsys, age, sex, currency,
#                             top_lvl_hierarchy, dd1_hierarchy, dd2_hierarchy, dd3_hierarchy, dd4_hierarchy):
def update_attr_treemap_ecs(input_json, prodsys, species, currency,
                            top_lvl_hierarchy, dd1_hierarchy, dd2_hierarchy, dd3_hierarchy, dd4_hierarchy):
    # Data
    input_df = pd.read_json(input_json, orient='split')

    # If currency is USD, use USD columns
    if currency == 'USD':
        input_df['median'] = input_df['median_usd']
        input_df['mean'] = input_df['mean_usd']
        input_df['sd'] = input_df['sd_usd']
        input_df['lower95'] = input_df['lower95_usd']
        input_df['upper95'] = input_df['upper95_usd']

    # Prep data
    input_df = prep_ahle_fortreemap_ecs(input_df)

    # Hiararchy structure
    path = [top_lvl_hierarchy]

    if dd1_hierarchy != 'None':
        path +=[dd1_hierarchy]
    if dd2_hierarchy != 'None':
        path +=[dd2_hierarchy]
    if dd3_hierarchy != 'None':
        path +=[dd3_hierarchy]
    if dd4_hierarchy != 'None':
        path +=[dd4_hierarchy]

    # Set up treemap structure
    ecs_treemap_fig = create_attr_treemap_ecs(input_df, path)

    # Add title
    # Species filter is already in place on input data. Create labels accordingly.
    if species == 'Goat' or species == "Sheep":
        species_label = 'All Small Ruminants'
    elif species == 'Poultry hybrid' or species == "Poultry indigenous":
        species_label = 'All Poultry'
    else:
        species_label = species

    ecs_treemap_fig.update_layout(
        title_text=f'Attribution | {species_label}, {prodsys}',
        font_size=15,
        margin=dict(t=100)
        )

    # Add % of total AHLE
    # ecs_treemap_fig.data[0].texttemplate = "%{label}<br>% of Total AHLE=%{customdata[0]:,.2f}%"

    # Add tooltip
    if currency == 'Birr':
        ecs_treemap_fig.update_traces(root_color="white",
                                      hovertemplate='Attribution=%{label}<br>Value=%{value:,.0f} Birr<extra></extra>')

    elif currency == 'USD':
        ecs_treemap_fig.update_traces(root_color="white",
                                      hovertemplate='Attribution=%{label}<br>Value=%{value:,.0f} USD<extra></extra>')
    else:
        ecs_treemap_fig.update_traces(root_color="white",
                                      hovertemplate='Attribution=%{label}<br>Value=%{value:,.0f}<br><extra></extra>')

    return ecs_treemap_fig

# Update Stacked bar chart
@gbadsDash.callback(
    Output('ahle-stacked-bar-ecs','figure'),
    Input('select-prodsys-ecs','value'),
    Input('select-species-ecs','value'),
    Input('select-currency-ecs','value'),
    Input('select-compare-ecs','value'),
    Input('select-factor-ecs','value'),
    Input('select-improve-ecs','value'),
    )
def update_stacked_bar_ecs(prodsys, species, currency, compare, impvmnt_factor, impvmnt_value):

    # AHLE Summary 2 - for stacked bar
    input_df = pd.read_csv(os.path.join(ECS_PROGRAM_OUTPUT_FOLDER ,'ahle_all_summary2.csv'))

    # Rename values to match filters
    input_df['production_system'] = input_df['production_system'].replace({'Overall': 'All Production Systems'})

    # Set columns for stacked bar based on selections
    # Change y based on selected currency value
    if compare == 'Ideal':
       cols_birr_costs = [
      'ahle_when_nm_ideal_mean'
      ,'ahle_when_nf_ideal_mean'
      ,'ahle_when_jm_ideal_mean'
      ,'ahle_when_jf_ideal_mean'
      ,'ahle_when_am_ideal_mean'
      ,'ahle_when_af_ideal_mean'
      ]
       cols_usd_costs = [
      'ahle_when_nm_ideal_mean_usd'
      ,'ahle_when_nf_ideal_mean_usd'
      ,'ahle_when_jm_ideal_mean_usd'
      ,'ahle_when_jf_ideal_mean_usd'
      ,'ahle_when_am_ideal_mean_usd'
      ,'ahle_when_af_ideal_mean_usd'
      ]
       pretty_ahle_cost_names = {
          'ahle_when_nm_ideal_mean':'Neonatal male'
          ,'ahle_when_nm_ideal_mean_usd':'Neonatal male'

          ,'ahle_when_nf_ideal_mean':'Neonatal female'
          ,'ahle_when_nf_ideal_mean_usd':'Neonatal female'

          ,'ahle_when_jm_ideal_mean':'Juvenile male'
          ,'ahle_when_jm_ideal_mean_usd':'Juvenile male'

          ,'ahle_when_jf_ideal_mean':'Juvenile female'
          ,'ahle_when_jf_ideal_mean_usd':'Juvenile female'

           ,'ahle_when_am_ideal_mean':'Adult male'
           ,'ahle_when_am_ideal_mean_usd':'Adult male'

          ,'ahle_when_af_ideal_mean':'Adult female'
          ,'ahle_when_af_ideal_mean_usd':'Adult female'
       }

    elif compare == 'Zero Mortality':
        cols_birr_costs = [
        'ahle_when_n_mort_imp100_mean'
        ,'ahle_when_j_mort_imp100_mean'
        ,'ahle_when_am_mort_imp100_mean'
        ,'ahle_when_af_mort_imp100_mean'
        ]
        cols_usd_costs = [
        'ahle_when_n_mort_imp100_mean_usd'
        ,'ahle_when_j_mort_imp100_mean_usd'
        ,'ahle_when_am_mort_imp100_mean_usd'
        ,'ahle_when_af_mort_imp100_mean_usd'
        ]
        pretty_ahle_cost_names = {
            'ahle_when_n_mort_imp100_mean':'Neonatal'
            ,'ahle_when_n_mort_imp100_mean_usd':'Neonatal'

            ,'ahle_when_j_mort_imp100_mean':'Juvenile'
            ,'ahle_when_j_mort_imp100_mean_usd':'Juvenile'

            ,'ahle_when_am_mort_imp100_mean':'Adult male'
            ,'ahle_when_am_mort_imp100_mean_usd':'Adult male'

            ,'ahle_when_af_mort_imp100_mean':'Adult female'
            ,'ahle_when_af_mort_imp100_mean_usd':'Adult female'
        }
    else:
        if impvmnt_factor == 'Mortality' and impvmnt_value == '25%':
            cols_birr_costs = [
            'ahle_when_n_mort_imp25_mean'
            ,'ahle_when_j_mort_imp25_mean'
            ,'ahle_when_am_mort_imp25_mean'
            ,'ahle_when_af_mort_imp25_mean'
            ]
            cols_usd_costs = [
            'ahle_when_n_mort_imp25_mean_usd'
            ,'ahle_when_j_mort_imp25_mean_usd'
            ,'ahle_when_am_mort_imp25_mean_usd'
            ,'ahle_when_af_mort_imp25_mean_usd'
            ]
            pretty_ahle_cost_names = {
                'ahle_when_n_mort_imp25_mean':'Neonatal'
                ,'ahle_when_n_mort_imp25_mean_usd':'Neonatal'

                ,'ahle_when_j_mort_imp25_mean':'Juvenile'
                ,'ahle_when_j_mort_imp25_mean_usd':'Juvenile'

                ,'ahle_when_am_mort_imp25_mean':'Adult male'
                ,'ahle_when_am_mort_imp25_mean_usd':'Adult male'

                ,'ahle_when_af_mort_imp25_mean':'Adult female'
                ,'ahle_when_af_mort_imp25_mean_usd':'Adult female'
            }
        elif impvmnt_factor == 'Mortality' and impvmnt_value == '50%':
            cols_birr_costs = [
            'ahle_when_n_mort_imp50_mean'
            ,'ahle_when_j_mort_imp50_mean'
            ,'ahle_when_am_mort_imp50_mean'
            ,'ahle_when_af_mort_imp50_mean'
            ]
            cols_usd_costs = [
            'ahle_when_n_mort_imp50_mean_usd'
            ,'ahle_when_j_mort_imp50_mean_usd'
            ,'ahle_when_am_mort_imp50_mean_usd'
            ,'ahle_when_af_mort_imp50_mean_usd'
            ]
            pretty_ahle_cost_names = {
                'ahle_when_n_mort_imp50_mean':'Neonatal'
                ,'ahle_when_n_mort_imp50_mean_usd':'Neonatal'

                ,'ahle_when_j_mort_imp50_mean':'Juvenile'
                ,'ahle_when_j_mort_imp50_mean_usd':'Juvenile'

                ,'ahle_when_am_mort_imp50_mean':'Adult male'
                ,'ahle_when_am_mort_imp50_mean_usd':'Adult male'

                ,'ahle_when_af_mort_imp50_mean':'Adult female'
                ,'ahle_when_af_mort_imp50_mean_usd':'Adult female'
            }
        elif impvmnt_factor == 'Mortality' and impvmnt_value == '75%':
            cols_birr_costs = [
            'ahle_when_n_mort_imp75_mean'
            ,'ahle_when_j_mort_imp75_mean'
            ,'ahle_when_am_mort_imp75_mean'
            ,'ahle_when_af_mort_imp75_mean'
            ]
            cols_usd_costs = [
            'ahle_when_n_mort_imp75_mean_usd'
            ,'ahle_when_j_mort_imp75_mean_usd'
            ,'ahle_when_am_mort_imp75_mean_usd'
            ,'ahle_when_af_mort_imp75_mean_usd'
            ]
            pretty_ahle_cost_names = {
                'ahle_when_n_mort_imp75_mean':'Neonatal'
                ,'ahle_when_n_mort_imp75_mean_usd':'Neonatal'

                ,'ahle_when_j_mort_imp75_mean':'Juvenile'
                ,'ahle_when_j_mort_imp75_mean_usd':'Juvenile'

                ,'ahle_when_am_mort_imp75_mean':'Adult male'
                ,'ahle_when_am_mort_imp75_mean_usd':'Adult male'

                ,'ahle_when_af_mort_imp75_mean':'Adult female'
                ,'ahle_when_af_mort_imp75_mean_usd':'Adult female'
            }
        elif impvmnt_factor == 'Mortality' and impvmnt_value == '100%':
            cols_birr_costs = [
            'ahle_when_n_mort_imp100_mean'
            ,'ahle_when_j_mort_imp100_mean'
            ,'ahle_when_am_mort_imp100_mean'
            ,'ahle_when_af_mort_imp100_mean'
            ]
            cols_usd_costs = [
            'ahle_when_n_mort_imp100_mean_usd'
            ,'ahle_when_j_mort_imp100_mean_usd'
            ,'ahle_when_am_mort_imp100_mean_usd'
            ,'ahle_when_af_mort_imp100_mean_usd'
            ]
            pretty_ahle_cost_names = {
                'ahle_when_n_mort_imp100_mean':'Neonatal'
                ,'ahle_when_n_mort_imp100_mean_usd':'Neonatal'

                ,'ahle_when_j_mort_imp100_mean':'Juvenile'
                ,'ahle_when_j_mort_imp100_mean_usd':'Juvenile'

                ,'ahle_when_am_mort_imp100_mean':'Adult male'
                ,'ahle_when_am_mort_imp100_mean_usd':'Adult male'

                ,'ahle_when_af_mort_imp100_mean':'Adult female'
                ,'ahle_when_af_mort_imp100_mean_usd':'Adult female'
            }
        elif impvmnt_factor == 'Parturition Rate' and impvmnt_value == '25%':
            cols_birr_costs = [
            'ahle_when_af_repro_imp25_mean'
            ]
            cols_usd_costs = [
            'ahle_when_af_repro_imp25_mean_usd'
            ]
            pretty_ahle_cost_names = {
                'ahle_when_af_repro_imp25_mean':'Adult female'
                ,'ahle_when_af_repro_imp25_mean_usd':'Adult female'
            }
        elif impvmnt_factor == 'Parturition Rate' and impvmnt_value == '50%':
            cols_birr_costs = [
            'ahle_when_af_repro_imp50_mean'
            ]
            cols_usd_costs = [
            'ahle_when_af_repro_imp50_mean_usd'
            ]
            pretty_ahle_cost_names = {
                'ahle_when_af_repro_imp50_mean':'Adult female'
                ,'ahle_when_af_repro_imp50_mean_usd':'Adult female'
            }
        elif impvmnt_factor == 'Parturition Rate' and impvmnt_value == '75%':
            cols_birr_costs = [
            'ahle_when_af_repro_imp75_mean'
            ]
            cols_usd_costs = [
            'ahle_when_af_repro_imp75_mean_usd'
            ]
            pretty_ahle_cost_names = {
                'ahle_when_af_repro_imp75_mean':'Adult female'
                ,'ahle_when_af_repro_imp75_mean_usd':'Adult female'
            }
        elif impvmnt_factor == 'Parturition Rate' and impvmnt_value == '100%':
            cols_birr_costs = [
            'ahle_when_af_repro_imp100_mean'
            ]
            cols_usd_costs = [
            'ahle_when_af_repro_imp100_mean_usd'
            ]
            pretty_ahle_cost_names = {
                'ahle_when_af_repro_imp100_mean':'Adult female'
                ,'ahle_when_af_repro_imp100_mean_usd':'Adult female'
            }
        elif impvmnt_factor == 'Live Weight' and impvmnt_value == '25%':
            cols_birr_costs = [
           'ahle_when_nm_growth_imp25_mean'
           ,'ahle_when_nf_growth_imp25_mean'
           ,'ahle_when_jm_growth_imp25_mean'
           ,'ahle_when_jf_growth_imp25_mean'
           ,'ahle_when_am_growth_imp25_mean'
           ,'ahle_when_af_growth_imp25_mean'
           ]
            cols_usd_costs = [
           'ahle_when_nm_growth_imp25_mean_usd'
           ,'ahle_when_nf_growth_imp25_mean_usd'
           ,'ahle_when_jm_growth_imp25_mean_usd'
           ,'ahle_when_jf_growth_imp25_mean_usd'
           ,'ahle_when_am_growth_imp25_mean_usd'
           ,'ahle_when_af_growth_imp25_mean_usd'
           ]
            pretty_ahle_cost_names = {
               'ahle_when_nm_growth_imp25_mean':'Neonatal male'
               ,'ahle_when_nm_growth_imp25_mean_usd':'Neonatal male'

               ,'ahle_when_nf_growth_imp25_mean':'Neonatal female'
               ,'ahle_when_nf_growth_imp25_mean_usd':'Neonatal female'

               ,'ahle_when_jm_growth_imp25_mean':'Juvenile male'
               ,'ahle_when_jm_growth_imp25_mean_usd':'Juvenile male'

               ,'ahle_when_jf_growth_imp25_mean':'Juvenile female'
               ,'ahle_when_jf_growth_imp25_mean_usd':'Juvenile female'

                ,'ahle_when_am_growth_imp25_mean':'Adult male'
                ,'ahle_when_am_growth_imp25_mean_usd':'Adult male'

               ,'ahle_when_af_growth_imp25_mean':'Adult female'
               ,'ahle_when_af_growth_imp25_mean_usd':'Adult female'
            }

        elif impvmnt_factor == 'Live Weight' and impvmnt_value == '50%':
            cols_birr_costs = [
           'ahle_when_nm_growth_imp50_mean'
           ,'ahle_when_nf_growth_imp50_mean'
           ,'ahle_when_jm_growth_imp50_mean'
           ,'ahle_when_jf_growth_imp50_mean'
           ,'ahle_when_am_growth_imp50_mean'
           ,'ahle_when_af_growth_imp50_mean'
           ]
            cols_usd_costs = [
           'ahle_when_nm_growth_imp50_mean_usd'
           ,'ahle_when_nf_growth_imp50_mean_usd'
           ,'ahle_when_jm_growth_imp50_mean_usd'
           ,'ahle_when_jf_growth_imp50_mean_usd'
           ,'ahle_when_am_growth_imp50_mean_usd'
           ,'ahle_when_af_growth_imp50_mean_usd'
           ]
            pretty_ahle_cost_names = {
               'ahle_when_nm_growth_imp50_mean':'Neonatal male'
               ,'ahle_when_nm_growth_imp50_mean_usd':'Neonatal male'

               ,'ahle_when_nf_growth_imp50_mean':'Neonatal female'
               ,'ahle_when_nf_growth_imp50_mean_usd':'Neonatal female'

               ,'ahle_when_jm_growth_imp50_mean':'Juvenile male'
               ,'ahle_when_jm_growth_imp50_mean_usd':'Juvenile male'

               ,'ahle_when_jf_growth_imp50_mean':'Juvenile female'
               ,'ahle_when_jf_growth_imp50_mean_usd':'Juvenile female'

                ,'ahle_when_am_growth_imp50_mean':'Adult male'
                ,'ahle_when_am_growth_imp50_mean_usd':'Adult male'

               ,'ahle_when_af_growth_imp50_mean':'Adult female'
               ,'ahle_when_af_growth_imp50_mean_usd':'Adult female'
            }
        elif impvmnt_factor == 'Live Weight' and impvmnt_value == '75%':
            cols_birr_costs = [
           'ahle_when_nm_growth_imp75_mean'
           ,'ahle_when_nf_growth_imp75_mean'
           ,'ahle_when_jm_growth_imp75_mean'
           ,'ahle_when_jf_growth_imp75_mean'
           ,'ahle_when_am_growth_imp75_mean'
           ,'ahle_when_af_growth_imp75_mean'
           ]
            cols_usd_costs = [
           'ahle_when_nm_growth_imp75_mean_usd'
           ,'ahle_when_nf_growth_imp75_mean_usd'
           ,'ahle_when_jm_growth_imp75_mean_usd'
           ,'ahle_when_jf_growth_imp75_mean_usd'
           ,'ahle_when_am_growth_imp75_mean_usd'
           ,'ahle_when_af_growth_imp75_mean_usd'
           ]
            pretty_ahle_cost_names = {
               'ahle_when_nm_growth_imp75_mean':'Neonatal male'
               ,'ahle_when_nm_growth_imp75_mean_usd':'Neonatal male'

               ,'ahle_when_nf_growth_imp75_mean':'Neonatal female'
               ,'ahle_when_nf_growth_imp75_mean_usd':'Neonatal female'

               ,'ahle_when_jm_growth_imp75_mean':'Juvenile male'
               ,'ahle_when_jm_growth_imp75_mean_usd':'Juvenile male'

               ,'ahle_when_jf_growth_imp75_mean':'Juvenile female'
               ,'ahle_when_jf_growth_imp75_mean_usd':'Juvenile female'

                ,'ahle_when_am_growth_imp75_mean':'Adult male'
                ,'ahle_when_am_growth_imp75_mean_usd':'Adult male'

               ,'ahle_when_af_growth_imp75_mean':'Adult female'
               ,'ahle_when_af_growth_imp75_mean_usd':'Adult female'
            }
        elif impvmnt_factor == 'Live Weight' and impvmnt_value == '100%':
            cols_birr_costs = [
           'ahle_when_nm_growth_imp100_mean'
           ,'ahle_when_nf_growth_imp100_mean'
           ,'ahle_when_jm_growth_imp100_mean'
           ,'ahle_when_jf_growth_imp100_mean'
           ,'ahle_when_am_growth_imp100_mean'
           ,'ahle_when_af_growth_imp100_mean'
           ]
            cols_usd_costs = [
           'ahle_when_nm_growth_imp100_mean_usd'
           ,'ahle_when_nf_growth_imp100_mean_usd'
           ,'ahle_when_jm_growth_imp100_mean_usd'
           ,'ahle_when_jf_growth_imp100_mean_usd'
           ,'ahle_when_am_growth_imp100_mean_usd'
           ,'ahle_when_af_growth_imp100_mean_usd'
           ]
            pretty_ahle_cost_names = {
               'ahle_when_nm_growth_imp100_mean':'Neonatal male'
               ,'ahle_when_nm_growth_imp100_mean_usd':'Neonatal male'

               ,'ahle_when_nf_growth_imp100_mean':'Neonatal female'
               ,'ahle_when_nf_growth_imp100_mean_usd':'Neonatal female'

               ,'ahle_when_jm_growth_imp100_mean':'Juvenile male'
               ,'ahle_when_jm_growth_imp100_mean_usd':'Juvenile male'

               ,'ahle_when_jf_growth_imp100_mean':'Juvenile female'
               ,'ahle_when_jf_growth_imp100_mean_usd':'Juvenile female'

                ,'ahle_when_am_growth_imp100_mean':'Adult male'
                ,'ahle_when_am_growth_imp100_mean_usd':'Adult male'

               ,'ahle_when_af_growth_imp100_mean':'Adult female'
               ,'ahle_when_af_growth_imp100_mean_usd':'Adult female'
            }

    # -----------------------------------------------------------------------------
    # Base plot
    # -----------------------------------------------------------------------------
    # Structure for plot
    stackedbar_df = prep_ahle_forstackedbar_ecs(input_df, cols_birr_costs, cols_usd_costs, pretty_ahle_cost_names)

    # Apply production system filter
    stackedbar_df = stackedbar_df.loc[(stackedbar_df['production_system'] == prodsys)]

    # Apply species filter
    stackedbar_df = stackedbar_df.loc[(stackedbar_df['species'] == species)]
    x = stackedbar_df['species']

    # Change y based on selected currency value
    yaxis_title = 'Ethiopian Birr'
    y = stackedbar_df['cost_birr']
    text = stackedbar_df['label_birr']
    if currency == 'USD':
        yaxis_title = 'USD'
        y = stackedbar_df['cost_usd']
        text = stackedbar_df['label_usd']

    # Color
    color = stackedbar_df['AHLE Due To']

    # Create Stacked Bar
    ahle_bar_ecs_fig = create_stacked_bar_ecs(stackedbar_df, x, y, text, color, yaxis_title)

    if compare == 'Ideal' or compare == 'Zero Mortality':
        ahle_bar_ecs_fig.update_layout(
            title_text=f'AHLE contributions by Age Group | {species}, {prodsys} <br><sup>{compare} scenario</sup><br>',
            font_size=15
            )
    else:
        ahle_bar_ecs_fig.update_layout(
            title_text=f'AHLE contributions by Age Group | {species}, {prodsys} <br><sup>{impvmnt_factor} {impvmnt_value} improvement scenario</sup><br>',
            font_size=15
            )

    # !!! - STILL WORKING ON THIS
    # # Add tooltip
    # if currency == 'Birr':
    #     ahle_bar_ecs_fig.update_traces(hovertemplate='Category=%{color}<br>Value=%{y:,.0f} Birr<extra></extra>')
    # elif currency == 'USD':
    #     ahle_bar_ecs_fig.update_traces(hovertemplate='Category=%{color}<br>Value=%{y:,.0f} USD<extra></extra>')

    return ahle_bar_ecs_fig

# ==============================================================================
#### UPDATE GLOBAL AGGREGATE
# ==============================================================================
# ------------------------------------------------------------------------------
#### -- Controls
# ------------------------------------------------------------------------------
# Update regions based on region contry aligment selection:
@gbadsDash.callback(
    Output(component_id='select-region-overview-ga', component_property='options'),
    Input(component_id='Region-country-alignment-overview-ga', component_property='value'),
    )
def update_region_overview_options_ga(region_country):
    if region_country == "WOAH":
        options = WOAH_region_options_ga
    elif region_country =="FAO":
        options = fao_region_options_ga
    elif region_country == "World Bank":
        options = wb_region_options_ga
    return options

@gbadsDash.callback(
    Output(component_id='select-region-detail-ga', component_property='options'),
    Input(component_id='Region-country-alignment-detail-ga', component_property='value'),
    )
def update_region_detail_options_ga(region_country):
    if region_country == "WOAH":
        options = WOAH_region_options_ga
    elif region_country =="FAO":
        options = fao_region_options_ga
    elif region_country == "World Bank":
        options = wb_region_options_ga
    return options


# Update country options based on region and income group selection
@gbadsDash.callback(
    Output(component_id='select-country-overview-ga', component_property='options'),
    Input(component_id='Region-country-alignment-overview-ga', component_property='value'),
    Input(component_id='select-region-overview-ga', component_property='value'),
    Input('select-incomegrp-overview-ga','value'),
    )
def update_country_overview_options_ga(region_country, region, income):
    if region_country == "WOAH":
        if region == "All":
            options = country_options_ga
        elif region == "Africa":
            options = WOAH_africa_options_ga
        elif region == "Americas":
            options = WOAH_americas_options_ga
        elif region == "Asia & the Pacific":
            options = WOAH_asia_options_ga
        elif region == "Europe":
            options = WOAH_europe_options_ga
        else:
            options = WOAH_me_options_ga
    elif region_country =="FAO":
        if region == "All":
            options = country_options_ga
        elif region == "Africa":
            options = fao_africa_options_ga
        elif region == "Asia":
            options = fao_asia_options_ga
        elif region == "Europe and Central Asia":
            options = fao_eca_options_ga
        elif region == "Latin America and the Caribbean":
            options = fao_lac_options_ga
        elif region == "Near East and North Africa":
            options = fao_ena_options_ga
        else:
            options = fao_swp_options_ga
    elif region_country == "World Bank":
        if region == "All":
            if income == "All":
                options = country_options_ga
            else:
                options_df = ga_countries_biomass.loc[(ga_countries_biomass['incomegroup'] == income)]
                options = [{'label': "All", 'value': "All"}]
                for i in options_df['country'].unique():
                    str(options.append({'label':i,'value':(i)}))
        else:
            options_df = ga_countries_biomass.loc[(ga_countries_biomass['region'] == region)]
            if income == "All":
                options = [{'label': "All", 'value': "All"}]
                for i in options_df['country'].unique():
                    str(options.append({'label':i,'value':(i)}))
            else:
                options_df = options_df.loc[(options_df['incomegroup'] == income)]
                options = [{'label': "All", 'value': "All"}]
                for i in options_df['country'].unique():
                    str(options.append({'label':i,'value':(i)}))
    else:
        options = country_options_ga

    return options

# Update country options based on region and income group selection
@gbadsDash.callback(
    Output('select-country-detail-ga', 'options'),
    Input('Region-country-alignment-detail-ga', 'value'),
    Input('select-region-detail-ga', 'value'),
    Input('select-incomegrp-detail-ga','value'),
    )
def update_country_detail_options_ga(region_country, region, income):
    if region_country == "WOAH":
        if region == "All":
            options = country_options_ga
        elif region == "Africa":
            options = WOAH_africa_options_ga
        elif region == "Americas":
            options = WOAH_americas_options_ga
        elif region == "Asia & the Pacific":
            options = WOAH_asia_options_ga
        elif region == "Europe":
            options = WOAH_europe_options_ga
        else:
            options = WOAH_me_options_ga
    elif region_country =="FAO":
        if region == "All":
            options = country_options_ga
        elif region == "Africa":
            options = fao_africa_options_ga
        elif region == "Asia":
            options = fao_asia_options_ga
        elif region == "Europe and Central Asia":
            options = fao_eca_options_ga
        elif region == "Latin America and the Caribbean":
            options = fao_lac_options_ga
        elif region == "Near East and North Africa":
            options = fao_ena_options_ga
        else:
            options = fao_swp_options_ga
    elif region_country == "World Bank":
        if region == "All":
            if income == "All":
                options = country_options_ga
            else:
                options_df = ga_countries_biomass.loc[(ga_countries_biomass['incomegroup'] == income)]
                options = [{'label': "All", 'value': "All"}]
                for i in options_df['country'].unique():
                    str(options.append({'label':i,'value':(i)}))
        else:
            options_df = ga_countries_biomass.loc[(ga_countries_biomass['region'] == region)]
            if income == "All":
                options = [{'label': "All", 'value': "All"}]
                for i in options_df['country'].unique():
                    str(options.append({'label':i,'value':(i)}))
            else:
                options_df = options_df.loc[(options_df['incomegroup'] == income)]
                options = [{'label': "All", 'value': "All"}]
                for i in options_df['country'].unique():
                    str(options.append({'label':i,'value':(i)}))
    else:
        options = country_options_ga

    return options

# Update species options based on region and country selections
@gbadsDash.callback(
    Output(component_id='select-species-ga', component_property='options'),
    Input(component_id='select-country-overview-ga', component_property='value'),
    Input(component_id='select-region-overview-ga', component_property='value'),
    )
def update_species_options_ga(country, region):
    if region == 'All':
        if country == "All":
            options = []
            for i in ga_countries_biomass['species'].unique():
                str(options.append({'label':i,'value':(i)}))
        else:
            input_df=ga_countries_biomass.loc[(ga_countries_biomass['country'] == country)]
            options = []
            for i in input_df['species'].unique():
                str(options.append({'label':i,'value':(i)}))
    elif region == "Sub-Saharan Africa":
        if country == 'All':
            country = [[v for k,v in d.items()] for d in wb_africa_options_ga]
            country = [a[1] for a in country]
            input_df = ga_countries_biomass[ga_countries_biomass['country'].isin(country)]
        else:
            input_df=ga_countries_biomass.loc[(ga_countries_biomass['country'] == country)]
        # Set options for species based on the filters for region and country
        options = []
        for i in input_df['species'].unique():
            str(options.append({'label':i,'value':(i)}))
    elif region == "East Asia & Pacific":
        if country == 'All':
            country = [[v for k,v in d.items()] for d in wb_eap_options_ga]
            country = [a[1] for a in country]
            input_df = ga_countries_biomass[ga_countries_biomass['country'].isin(country)]
        else:
            input_df=ga_countries_biomass.loc[(ga_countries_biomass['country'] == country)]
        # Set options for species based on the filters for region and country
        options = []
        for i in input_df['species'].unique():
            str(options.append({'label':i,'value':(i)}))
    elif region == "Europe & Central Asia":
        if country == 'All':
            country = [[v for k,v in d.items()] for d in wb_eca_options_ga]
            country = [a[1] for a in country]
            input_df = ga_countries_biomass[ga_countries_biomass['country'].isin(country)]
        else:
            input_df=ga_countries_biomass.loc[(ga_countries_biomass['country'] == country)]
        # Set options for species based on the filters for region and country
        options = []
        for i in input_df['species'].unique():
            str(options.append({'label':i,'value':(i)}))
    elif region == "Latin America & the Caribbean":
        if country == 'All':
            country = [[v for k,v in d.items()] for d in wb_lac_options_ga]
            country = [a[1] for a in country]
            input_df = ga_countries_biomass[ga_countries_biomass['country'].isin(country)]
        else:
            input_df=ga_countries_biomass.loc[(ga_countries_biomass['country'] == country)]
        # Set options for species based on the filters for region and country
        options = []
        for i in input_df['species'].unique():
            str(options.append({'label':i,'value':(i)}))
    elif region == "Middle East & North Africa":
        if country == 'All':
            country = [[v for k,v in d.items()] for d in wb_mena_options_ga]
            country = [a[1] for a in country]
            input_df = ga_countries_biomass[ga_countries_biomass['country'].isin(country)]
        else:
            input_df=ga_countries_biomass.loc[(ga_countries_biomass['country'] == country)]
        # Set options for species based on the filters for region and country
        options = []
        for i in input_df['species'].unique():
            str(options.append({'label':i,'value':(i)}))
    elif region == "North America":
        if country == 'All':
            country = [[v for k,v in d.items()] for d in wb_na_options_ga]
            country = [a[1] for a in country]
            input_df = ga_countries_biomass[ga_countries_biomass['country'].isin(country)]
        else:
            input_df=ga_countries_biomass.loc[(ga_countries_biomass['country'] == country)]
        # Set options for species based on the filters for region and country
        options = []
        for i in input_df['species'].unique():
            str(options.append({'label':i,'value':(i)}))
    else:
        if country == 'All':
            country = [[v for k,v in d.items()] for d in wb_southasia_options_ga]
            country = [a[1] for a in country]
            input_df = ga_countries_biomass[ga_countries_biomass['country'].isin(country)]
        else:
            input_df=ga_countries_biomass.loc[(ga_countries_biomass['country'] == country)]
        # Set options for species based on the filters for region and country
        options = []
        for i in input_df['species'].unique():
            str(options.append({'label':i,'value':(i)}))

    return options


# ------------------------------------------------------------------------------
#### -- Data
# ------------------------------------------------------------------------------
# Add AHLE calcs to global data
# Updates when user changes mortality, morbidity, or vet & med rates
@gbadsDash.callback(
    Output('core-data-world-ahle','data'),
    Input('base-mortality-rate-ga','value'),
    # Input('base-morbidity-rate-ga','value'),
    # Input('base-vetmed-rate-ga','value'),
    )
def update_core_data_world_ahle(base_mort_rate):# ,base_morb_rate ,base_vetmed_rate):
    world_ahle_withcalcs = ga_countries_biomass.copy()
    # Add mortality, morbidity, and vetmed rate columns
    world_ahle_withcalcs = ga.add_mortality_rate(world_ahle_withcalcs)
    world_ahle_withcalcs = ga.add_morbidity_rate(world_ahle_withcalcs)
    world_ahle_withcalcs = ga.add_vetmed_rates(world_ahle_withcalcs)

    # Apply AHLE calcs
    world_ahle_withcalcs = ga.ahle_calcs_adj_outputs(world_ahle_withcalcs)

    return world_ahle_withcalcs.to_json(date_format='iso', orient='split')

# # World AHLE ABT Data
# @gbadsDash.callback(
#     Output('core-data-world-ahle-abt-ga','data'),
#     Input('select-species-ga','value'),
#     Input('Region-country-alignment-overview-ga','value'),
#     Input('select-region-overview-ga', 'value'),
#     Input('select-country-overview-ga','value'),
#     Input('select-incomegrp-overview-ga','value'),
#     )
# def update_core_data_world_ahle_abt_ga(species,region_country,region,country,income):
#     input_df = ga_countries_biomass.copy()

#     # Filter Region & country
#     if region == "All":
#         if country == 'All':
#             country = [[v for k,v in d.items()] for d in country_options_ga]
#             country = [a[1] for a in country]
#             input_df = ga_countries_biomass[ga_countries_biomass['country'].isin(country)]
#         else:
#             input_df=input_df.loc[(input_df['country'] == country)]
#     elif region == "Sub-Saharan Africa":
#         if country == 'All':
#             country = [[v for k,v in d.items()] for d in wb_africa_options_ga]
#             country = [a[1] for a in country]
#             input_df = ga_countries_biomass[ga_countries_biomass['country'].isin(country)]
#         else:
#             input_df=input_df.loc[(input_df['country'] == country)]
#     elif region == "East Asia & Pacific":
#         if country == 'All':
#             country = [[v for k,v in d.items()] for d in wb_eap_options_ga]
#             country = [a[1] for a in country]
#             input_df = ga_countries_biomass[ga_countries_biomass['country'].isin(country)]
#         else:
#             input_df=input_df.loc[(input_df['country'] == country)]
#     elif region == "Europe & Central Asia":
#         if country == 'All':
#             country = [[v for k,v in d.items()] for d in wb_eca_options_ga]
#             country = [a[1] for a in country]
#             input_df = ga_countries_biomass[ga_countries_biomass['country'].isin(country)]
#         else:
#             input_df=input_df.loc[(input_df['country'] == country)]
#     elif region == "Latin America & the Caribbean":
#         if country == 'All':
#             country = [[v for k,v in d.items()] for d in wb_lac_options_ga]
#             country = [a[1] for a in country]
#             input_df = ga_countries_biomass[ga_countries_biomass['country'].isin(country)]
#         else:
#             input_df=input_df.loc[(input_df['country'] == country)]
#     elif region == "Middle East & North Africa":
#         if country == 'All':
#             country = [[v for k,v in d.items()] for d in wb_mena_options_ga]
#             country = [a[1] for a in country]
#             input_df = ga_countries_biomass[ga_countries_biomass['country'].isin(country)]
#         else:
#             input_df=input_df.loc[(input_df['country'] == country)]
#     elif region == "North America":
#         if country == 'All':
#             country = [[v for k,v in d.items()] for d in wb_na_options_ga]
#             country = [a[1] for a in country]
#             input_df = ga_countries_biomass[ga_countries_biomass['country'].isin(country)]
#         else:
#             input_df=input_df.loc[(input_df['country'] == country)]
#     else:
#         if country == 'All':
#             country = [[v for k,v in d.items()] for d in wb_southasia_options_ga]
#             country = [a[1] for a in country]
#             input_df = ga_countries_biomass[ga_countries_biomass['country'].isin(country)]
#         else:
#             input_df=input_df.loc[(input_df['country'] == country)]

#     # Filter Income Group
#     if income == 'All':
#         input_df = input_df
#     else:
#         input_df = input_df.loc[(input_df['incomegroup'] == income)]

#     # Filter Species
#     input_df = input_df.loc[(input_df['species'] == species)]

#     # Add mortality, morbidity, and vetmed rate columns
#     input_df = ga.add_mortality_rate(input_df)
#     input_df = ga.add_morbidity_rate(input_df)
#     input_df = ga.add_vetmed_rates(input_df)

#     # Apply AHLE calcs
#     input_df = ga.ahle_calcs_adj_outputs(input_df)

#     return input_df.to_json(date_format='iso', orient='split')


# Attribution datatable below graphic
# @gbadsDash.callback(
#     Output('ga-world-abt-datatable', 'children'),
#     Input('core-data-world-ahle-abt-ga','data'),
#     # Input('select-currency-ecs','value'),
#     )
# def update_overview_table_ga(input_json):
#     input_df = pd.read_json(input_json, orient='split')
@gbadsDash.callback(
    Output('ga-world-abt-datatable', 'children'),
    # Input('core-data-world-ahle-abt-ga','data'),
    Input('select-species-ga','value'),
    Input('select-region-overview-ga', 'value'),
    Input('select-country-overview-ga','value'),
    Input('select-incomegrp-overview-ga','value'),
    )
def update_overview_table_ga(species,region,country,income):
    input_df = ga_countries_biomass.copy()
    # Filter Region & country
    if region == "All":
        if country == 'All':
            country = [[v for k,v in d.items()] for d in country_options_ga]
            country = [a[1] for a in country]
            input_df = ga_countries_biomass[ga_countries_biomass['country'].isin(country)]
        else:
            input_df=input_df.loc[(input_df['country'] == country)]
    elif region == "Sub-Saharan Africa":
        if country == 'All':
            country = [[v for k,v in d.items()] for d in wb_africa_options_ga]
            country = [a[1] for a in country]
            input_df = ga_countries_biomass[ga_countries_biomass['country'].isin(country)]
        else:
            input_df=input_df.loc[(input_df['country'] == country)]
    elif region == "East Asia & Pacific":
        if country == 'All':
            country = [[v for k,v in d.items()] for d in wb_eap_options_ga]
            country = [a[1] for a in country]
            input_df = ga_countries_biomass[ga_countries_biomass['country'].isin(country)]
        else:
            input_df=input_df.loc[(input_df['country'] == country)]
    elif region == "Europe & Central Asia":
        if country == 'All':
            country = [[v for k,v in d.items()] for d in wb_eca_options_ga]
            country = [a[1] for a in country]
            input_df = ga_countries_biomass[ga_countries_biomass['country'].isin(country)]
        else:
            input_df=input_df.loc[(input_df['country'] == country)]
    elif region == "Latin America & the Caribbean":
        if country == 'All':
            country = [[v for k,v in d.items()] for d in wb_lac_options_ga]
            country = [a[1] for a in country]
            input_df = ga_countries_biomass[ga_countries_biomass['country'].isin(country)]
        else:
            input_df=input_df.loc[(input_df['country'] == country)]
    elif region == "Middle East & North Africa":
        if country == 'All':
            country = [[v for k,v in d.items()] for d in wb_mena_options_ga]
            country = [a[1] for a in country]
            input_df = ga_countries_biomass[ga_countries_biomass['country'].isin(country)]
        else:
            input_df=input_df.loc[(input_df['country'] == country)]
    elif region == "North America":
        if country == 'All':
            country = [[v for k,v in d.items()] for d in wb_na_options_ga]
            country = [a[1] for a in country]
            input_df = ga_countries_biomass[ga_countries_biomass['country'].isin(country)]
        else:
            input_df=input_df.loc[(input_df['country'] == country)]
    else:
        if country == 'All':
            country = [[v for k,v in d.items()] for d in wb_southasia_options_ga]
            country = [a[1] for a in country]
            input_df = ga_countries_biomass[ga_countries_biomass['country'].isin(country)]
        else:
            input_df=input_df.loc[(input_df['country'] == country)]
    # Filter Income Group
    if income == 'All':
        input_df = input_df
    else:
        input_df = input_df.loc[(input_df['incomegroup'] == income)]
    # Filter Species
    input_df = input_df.loc[(input_df['species'] == species)]
    # Add mortality, morbidity, and vetmed rate columns
    input_df = ga.add_mortality_rate(input_df)
    input_df = ga.add_morbidity_rate(input_df)
    input_df = ga.add_vetmed_rates(input_df)
    # Apply AHLE calcs
    input_df = ga.ahle_calcs_adj_outputs(input_df)
    
    
    
    
    # Format numbers
    input_df.update(input_df[['biomass',
                              'population',
                              'liveweight',
                              'ahle_total_2010usd',
                              ]].applymap('{:,.0f}'.format))

    columns_to_display_with_labels = {
       'country':'Country'
       ,'species':'Species'
       ,'year':'Year'
       ,'incomegroup': 'Income Group'
       ,'ahle_total_2010usd': 'Total AHLE (2010 USD)'
       ,'biomass':'Biomass (kg)'
       ,'population':'Population (head)'
       ,'liveweight':'Average Live Weight (kg)'
    }

    # Subset columns
    input_df = input_df[list(columns_to_display_with_labels)]

    # Hover-over text
    column_tooltips = {
       'incomegroup':'Source: World Bank via GBADs knowledge engine'
       # ,'ahle_total_2010usd': ')'
       ,'biomass':'Source: FAO via GBADs knowledge engine'
       ,'population':'Source: FAO via GBADs knowledge engine'
       ,'liveweight':'Source: FAO via GBADs knowledge engine'
    }
    return [
            html.H4("Global Aggregation Data"),
            dash_table.DataTable(
                columns=[{"name": j, "id": i} for i, j in columns_to_display_with_labels.items()],
                fixed_rows={'headers': True, 'data': 0},
                data=input_df.to_dict('records'),
                export_format="csv",
                style_cell={
                    'font-family':'sans-serif',
                    },
                style_table={'overflowX': 'scroll',
                              'height': '680px',
                              'overflowY': 'auto'},
                page_action='none',

                # Hover-over for column headers
                tooltip_header=column_tooltips,
                tooltip_delay=1500,
                tooltip_duration=50000,

                # Underline columns with tooltips
                style_header_conditional=[{
                    'if': {'column_id': col},
                    'textDecoration': 'underline',
                    'textDecorationStyle': 'dotted',
                    } for col in list(column_tooltips)],
            )
        ]

@gbadsDash.callback(
    Output('ga-detailtab-displaytable', 'children'),
    Input('core-data-world-ahle','data'),
    Input('select-region-detail-ga','value'),
    Input('select-incomegrp-detail-ga','value'),
    Input('select-country-detail-ga','value'),
    )
def update_display_table_ga(input_json ,selected_region ,selected_incgrp ,selected_country):
    # Read data
    input_df = pd.read_json(input_json, orient='split')

    # Apply filters
    input_df_filtered = input_df

    # Region, Country and Income group might not be filtered
    if selected_region == 'All':
        if selected_country == 'All':
            input_df_filtered = input_df_filtered
            # print_selected_country = 'All countries, '
            print_selected_country = 'Global, '

            # Only need to filter income groups if no country selected
            if selected_incgrp == 'All':
                input_df_filtered = input_df_filtered
                print_selected_incgrp = 'all income groups, '
            else:
                input_df_filtered = input_df_filtered.query(f"incomegroup == '{selected_incgrp}'")
                print_selected_incgrp = f'income group {selected_incgrp}, '
        else:
            input_df_filtered = input_df_filtered.query(f"country == '{selected_country}'")
            print_selected_country = f'{selected_country}'
            print_selected_incgrp = ''
    else:
        if selected_country == 'All':
            input_df_filtered = input_df_filtered.query(f"region == '{selected_region}'")
            print_selected_country = f'All {selected_region} countries,'

            # Only need to filter income groups if no country selected
            if selected_incgrp == 'All':
                input_df_filtered = input_df_filtered
                print_selected_incgrp = 'all income groups, '
            else:
                input_df_filtered = input_df_filtered.query(f"incomegroup == '{selected_incgrp}'")
                print_selected_incgrp = f'income group {selected_incgrp}, '
        else:
            input_df_filtered = input_df_filtered.query(f"country == '{selected_country}'")
            print_selected_country = f'{selected_country}'
            print_selected_incgrp = ''

    columns_to_display_with_labels = {
        'region':'Region'
        ,'incomegroup':'Income group'
        ,'country':'Country'
        ,'species':'Species'
        ,'year':'Year'
        ,'population':'Population (head)'
        ,'liveweight':'Average liveweight (kg)'
        ,'biomass':'Biomass (kg)'

        ,'production_eggs_tonnes':'Egg production (tonnes)'
        ,'production_meat_tonnes':'Meat production (tonnes)'
        ,'production_milk_tonnes':'Milk production (tonnes)'
        ,'production_wool_tonnes':'Wool production (tonnes)'

        ,'producer_price_meat_live_usdpertonne_cnst2010':'Liveweight price (USD per tonne)'
        ,'producer_price_eggs_usdpertonne_cnst2010':'Egg price (USD per tonne)'
        ,'producer_price_meat_usdpertonne_cnst2010':'Meat price (USD per tonne)'
        ,'producer_price_milk_usdpertonne_cnst2010':'Milk price (USD per tonne)'
        ,'producer_price_wool_usdpertonne_cnst2010':'Wool price (USD per tonne)'

        ,'biomass_value_2010usd':'Value of biomass (USD)'
        ,'output_value_eggs_2010usd':'Value of Egg production (USD)'
        ,'output_value_meat_2010usd':'Value of Meat production (USD)'
        ,'output_value_milk_2010usd':'Value of Milk production (USD)'
        ,'output_value_wool_2010usd':'Value of Wool production (USD)'

        ,'mortality_rate':'Mortality rate'
        ,'morbidity_rate':'Morbidity rate'

        ,'ideal_biomass_value_2010usd':'Value of ideal biomass (USD)'
        ,'ideal_output_value_eggs_2010usd':'Value of ideal egg production (USD)'
        ,'ideal_output_value_meat_2010usd':'Value of ideal meat production (USD)'
        ,'ideal_output_value_milk_2010usd':'Value of ideal milk production (USD)'
        ,'ideal_output_value_wool_2010usd':'Value of ideal wool production (USD)'

        ,'vetspend_biomass_farm_usdperkgbm':'Producers vet & med cost per kg biomass (USD)'
        ,'vetspend_biomass_public_usdperkgbm':'Public vet & med cost per kg biomass (USD)'
        ,'vetspend_production_usdperkgprod':'Producers vet & med cost per kg production (USD)'
        ,'vetspend_farm_usd':'Total producers vet & med cost (USD)'
        ,'vetspend_public_usd':'Total public vet & med cost (USD)'

        ,'ahle_dueto_reducedoutput_2010usd':'Value of AHLE due to reduced output (USD)'
        ,'ahle_dueto_vetandmedcost_2010usd':'Value of AHLE due to vet & med cost (USD)'
        ,'ahle_total_2010usd':'Total value of AHLE (USD)'
    }
    # ------------------------------------------------------------------------------
    # Format data to display in the table
    # ------------------------------------------------------------------------------
    # Order does not matter in these lists
    # Zero decimal places without comma
    input_df_filtered.update(input_df_filtered[[
        'year'
    ]].applymap('{:.0f}'.format))

    # Zero decimal places
    input_df_filtered.update(input_df_filtered[[
        'population'
        ,'biomass'
        ,'production_eggs_tonnes'
        ,'production_meat_tonnes'
        ,'production_milk_tonnes'
        ,'production_wool_tonnes'
    ]].applymap('{:,.0f}'.format))

    # One decimal place
    input_df_filtered.update(input_df_filtered[[
        'liveweight'
    ]].applymap('{:,.1f}'.format))

    # Two decimal places
    input_df_filtered.update(input_df_filtered[[
        # 'producer_price_meat_live_usdpertonne_cnst2010'
        # ,'producer_price_eggs_usdpertonne_cnst2010'
        # ,'producer_price_meat_usdpertonne_cnst2010'
        # ,'producer_price_milk_usdpertonne_cnst2010'
        # ,'producer_price_wool_usdpertonne_cnst2010'

        'biomass_value_2010usd'
        ,'output_value_eggs_2010usd'
        ,'output_value_meat_2010usd'
        ,'output_value_milk_2010usd'
        ,'output_value_wool_2010usd'

        ,'mortality_rate'
        ,'morbidity_rate'

        ,'ideal_biomass_value_2010usd'
        ,'ideal_output_value_eggs_2010usd'
        ,'ideal_output_value_meat_2010usd'
        ,'ideal_output_value_milk_2010usd'
        ,'ideal_output_value_wool_2010usd'

        ,'vetspend_biomass_farm_usdperkgbm'
        ,'vetspend_biomass_public_usdperkgbm'
        ,'vetspend_production_usdperkgprod'
        ,'vetspend_farm_usd'
        ,'vetspend_public_usd'

        ,'ahle_dueto_reducedoutput_2010usd'
        ,'ahle_dueto_vetandmedcost_2010usd'
        ,'ahle_total_2010usd'

    ]].applymap('{:,.2f}'.format))

    # ------------------------------------------------------------------------------
    # Hover-over text
    # ------------------------------------------------------------------------------
    column_tooltips = {
        'region':'World Bank region'
        ,'incomegroup':'World Bank income group'
        ,'population':'Source: FAO'
        ,'liveweight':'Source: FAO'

        ,'production_eggs_tonnes':'Source: FAO'
        ,'production_meat_tonnes':'Source: FAO'
        ,'production_milk_tonnes':'Source: FAO'
        ,'production_wool_tonnes':'Source: FAO'

        ,'producer_price_meat_live_usdpertonne_cnst2010':'Constant 2010 US dollars. Source: FAO'
        ,'producer_price_eggs_usdpertonne_cnst2010':'Constant 2010 US dollars. Source: FAO'
        ,'producer_price_meat_usdpertonne_cnst2010':'Constant 2010 US dollars. Source: FAO'
        ,'producer_price_milk_usdpertonne_cnst2010':'Constant 2010 US dollars. Source: FAO'
        ,'producer_price_wool_usdpertonne_cnst2010':'Constant 2010 US dollars. Source: FAO'

        ,'biomass_value_2010usd':'Constant 2010 US dollars'
        ,'output_value_eggs_2010usd':'Constant 2010 US dollars'
        ,'output_value_meat_2010usd':'Constant 2010 US dollars'
        ,'output_value_milk_2010usd':'Constant 2010 US dollars'
        ,'output_value_wool_2010usd':'Constant 2010 US dollars'

        # ,'mortality_rate':''
        # ,'morbidity_rate':''

        ,'ideal_biomass_value_2010usd':'Constant 2010 US dollars'
        ,'ideal_output_value_eggs_2010usd':'Constant 2010 US dollars'
        ,'ideal_output_value_meat_2010usd':'Constant 2010 US dollars'
        ,'ideal_output_value_milk_2010usd':'Constant 2010 US dollars'
        ,'ideal_output_value_wool_2010usd':'Constant 2010 US dollars'

        # ,'vetspend_biomass_farm_usdperkgbm':''
        # ,'vetspend_biomass_public_usdperkgbm':''
        # ,'vetspend_production_usdperkgprod':''
        # ,'vetspend_farm_usd':''
        # ,'vetspend_public_usd':''

        ,'ahle_dueto_reducedoutput_2010usd':'Constant 2010 US dollars'
        ,'ahle_dueto_vetandmedcost_2010usd':'Constant 2010 US dollars'
        ,'ahle_total_2010usd':'Constant 2010 US dollars'
    }

    # !!!- Adjust header size based on the column name length
    # # custom width for each column as a workaround for this issue:
    # long_column_names = [{"if": {"column_id": column}, "min-width": "300px"} for column in df.columns if len(column) >= 30]
    # med_column_names = [{"if": {"column_id": column}, "min-width": "225px"} for column in df.columns if (len(column) > 15 and len(column)) < 30]
    # small_column_names = [{"if": {"column_id": column}, "min-width": "100px"} for column in df.columns if len(column) <= 15]

    # adjusted_columns = long_column_names + med_column_names + small_column_names
    return [
        html.H4(f"Detailed data for {print_selected_country}{print_selected_incgrp}"),
        dash_table.DataTable(
            columns=[{"name": j, "id": i} for i, j in columns_to_display_with_labels.items()],
            fixed_rows={'headers': True, 'data': 0},
            data=input_df_filtered.to_dict('records'),
            export_format="csv",
            sort_action = 'native',
            style_cell={'font-family':'sans-serif'},
            style_table={'overflowX': 'scroll',
                          'height': '680px',
                          'overflowY': 'auto'
                          },

            # Hover-over for column headers
            tooltip_header=column_tooltips,
            tooltip_delay=1500,
            tooltip_duration=50000,

            # Underline columns with tooltips
            style_header_conditional=[{
                'if': {'column_id': col},
                'textDecoration': 'underline',
                'textDecorationStyle': 'dotted',
                } for col in list(column_tooltips)],
        )
    ]

# ------------------------------------------------------------------------------
#### -- Figures
# ------------------------------------------------------------------------------
# Biomass Map
# @gbadsDash.callback(
#    Output('ga-map-or-line-select','figure'),
#    Input('core-data-world-ahle-abt-ga','data'),
#    Input('viz-radio-ga','value'),
#    Input('select-species-ga','value'),
#    Input('select-country-overview-ga', 'value'),
#    Input('select-region-overview-ga', 'value'),
#    Input('map-display-radio-ga','value'),
#    # Input('select-currency-ecs','value'),
#    )
# def update_bio_ahle_visual_ga(input_json, viz_selection, species, country_select, region, display):
#    # Data
#    input_df = pd.read_json(input_json, orient='split')
@gbadsDash.callback(
   Output('ga-map-or-line-select','figure'),
   # Input('core-data-world-ahle-abt-ga','data'),
   Input('viz-radio-ga','value'),
   Input('select-species-ga','value'),
   Input('select-country-overview-ga', 'value'),
   Input('select-region-overview-ga', 'value'),
   Input('map-display-radio-ga','value'),
   Input('select-incomegrp-overview-ga','value'),
   # Input('select-currency-ecs','value'),
   )
def update_bio_ahle_visual_ga(viz_selection, species, country, region, display, income):
   input_df = ga_countries_biomass.copy()
   # Filter Region & country
   if region == "All":
       if country == 'All':
           country = [[v for k,v in d.items()] for d in country_options_ga]
           country = [a[1] for a in country]
           input_df = ga_countries_biomass[ga_countries_biomass['country'].isin(country)]
       else:
           input_df=input_df.loc[(input_df['country'] == country)]
   elif region == "Sub-Saharan Africa":
       if country == 'All':
           country = [[v for k,v in d.items()] for d in wb_africa_options_ga]
           country = [a[1] for a in country]
           input_df = ga_countries_biomass[ga_countries_biomass['country'].isin(country)]
       else:
           input_df=input_df.loc[(input_df['country'] == country)]
   elif region == "East Asia & Pacific":
       if country == 'All':
           country = [[v for k,v in d.items()] for d in wb_eap_options_ga]
           country = [a[1] for a in country]
           input_df = ga_countries_biomass[ga_countries_biomass['country'].isin(country)]
       else:
           input_df=input_df.loc[(input_df['country'] == country)]
   elif region == "Europe & Central Asia":
       if country == 'All':
           country = [[v for k,v in d.items()] for d in wb_eca_options_ga]
           country = [a[1] for a in country]
           input_df = ga_countries_biomass[ga_countries_biomass['country'].isin(country)]
       else:
           input_df=input_df.loc[(input_df['country'] == country)]
   elif region == "Latin America & the Caribbean":
       if country == 'All':
           country = [[v for k,v in d.items()] for d in wb_lac_options_ga]
           country = [a[1] for a in country]
           input_df = ga_countries_biomass[ga_countries_biomass['country'].isin(country)]
       else:
           input_df=input_df.loc[(input_df['country'] == country)]
   elif region == "Middle East & North Africa":
       if country == 'All':
           country = [[v for k,v in d.items()] for d in wb_mena_options_ga]
           country = [a[1] for a in country]
           input_df = ga_countries_biomass[ga_countries_biomass['country'].isin(country)]
       else:
           input_df=input_df.loc[(input_df['country'] == country)]
   elif region == "North America":
       if country == 'All':
           country = [[v for k,v in d.items()] for d in wb_na_options_ga]
           country = [a[1] for a in country]
           input_df = ga_countries_biomass[ga_countries_biomass['country'].isin(country)]
       else:
            input_df=input_df.loc[(input_df['country'] == country)]
   else:
       if country == 'All':
           country = [[v for k,v in d.items()] for d in wb_southasia_options_ga]
           country = [a[1] for a in country]
           input_df = ga_countries_biomass[ga_countries_biomass['country'].isin(country)]
       else:
           input_df=input_df.loc[(input_df['country'] == country)]
   # Filter Income Group
   if income == 'All':
       input_df = input_df
   else:
       input_df = input_df.loc[(input_df['incomegroup'] == income)]
   # Filter Species
   input_df = input_df.loc[(input_df['species'] == species)]
   # Add mortality, morbidity, and vetmed rate columns
   input_df = ga.add_mortality_rate(input_df)
   input_df = ga.add_morbidity_rate(input_df)
   input_df = ga.add_vetmed_rates(input_df)
   # Apply AHLE calcs
   input_df = ga.ahle_calcs_adj_outputs(input_df)
   
   
   
   if viz_selection == 'Map':
       # Set values from the data
       iso_alpha3 = input_df['country_iso3']
       country = input_df['country']
       year = input_df['year']

       # # Establish AHLE
       input_df['ahle_total_2010usd'] = input_df['ahle_total_2010usd'].fillna(0)


       # Set value based on map display option
       if display == 'Biomass':
           display_title = 'Biomass (kg)'
           value = input_df['biomass']
       elif display == 'Live Weight':
           display_title = 'Average Live Weight (kg)'
           value = input_df['liveweight']
       elif display == 'Population':
           display_title = 'Population (head)'
           value = input_df['population']
       elif display == 'Animal Health Loss Envelope (AHLE)':
           display_title = 'AHLE (2010 USD)'
           value = input_df['ahle_total_2010usd']
       else:
           display = 'AHLE per kg biomass'
           display_title = 'AHLE (USD per kg biomass)'
           value = input_df['ahle_2010usd_perkgbm']

       # Set up map structure
       ga_biomass_ahle_visual = create_biomass_map_ga(input_df, iso_alpha3, value, country, display_title)

       # # Add title
       # if region == 'All':
       #     if country_select =='All':
       #         ga_biomass_ahle_visual.update_layout(title_text=f'Global {display_title} for {species}',
       #                                       font_size=15,
       #                                       margin=dict(t=100))
       #     else:
       #         ga_biomass_ahle_visual.update_layout(title_text=f'{country_select} {display_title} for {species}',
       #                                       font_size=15,
       #                                       margin=dict(t=100))
       #         ga_biomass_ahle_visual.update_coloraxes(showscale=False)
       # else:
       #       if country_select =='All':
       #           ga_biomass_ahle_visual.update_layout(title_text=f'{region} {display_title} for {species}',
       #                                         font_size=15,
       #                                         margin=dict(t=100))
       #       else:
       #           ga_biomass_ahle_visual.update_layout(title_text=f'{country_select} {display_title} for {species}',
       #                                         font_size=15,
       #                                         margin=dict(t=100))
       #           ga_biomass_ahle_visual.update_coloraxes(showscale=False)

   elif viz_selection == 'Line chart':
       # Specify which columns to keep forline chart
       input_df = input_df[['country', 'year', 'species', 'biomass', 'population', 'liveweight']]

       # Melt data to create facets for line chart
       input_df = input_df.melt(id_vars=['country', 'year', 'species'],
                                value_vars=['biomass', 'population', 'liveweight'],
                                var_name='facet',
                                value_name='value')

       # Set values from the data
       year = input_df['year']
       value = input_df['value']
       country = input_df['country']
       facet = input_df['facet']

       # Set up line plot structure
       ga_biomass_ahle_visual = create_line_chart_ga(input_df, year, value, country, facet)

   return ga_biomass_ahle_visual

# Global AHLE Waterfall
@gbadsDash.callback(
    Output('ga-ahle-waterfall','figure'),
    Input('core-data-world-ahle','data'),
    Input('select-region-detail-ga','value'),
    Input('select-incomegrp-detail-ga','value'),
    Input('select-country-detail-ga','value'),
    Input('select-year-ga','value'),
    Input('select-display-ga','value'),
    )
def update_ahle_waterfall_ga(input_json ,selected_region ,selected_incgrp ,selected_country ,selected_year, display):
    # Read core data
    input_df = pd.read_json(input_json, orient='split')

    # Prep the data
    prep_df = prep_ahle_forwaterfall_ga(input_df)

    # Make costs negative
    _vetmed_rows = (prep_df['item'].str.contains('VET' ,case=False))
    prep_df.loc[_vetmed_rows ,'value_usd_current'] = -1 * prep_df['value_usd_current']

    # Apply user filters
    # There will always be a year filter
    prep_df_filtered = prep_df.query(f"year == {selected_year}")

    # Region, Country and Income group might not be filtered
    if selected_region == 'All':
        if selected_country == 'All':
            prep_df_filtered = prep_df_filtered
            # print_selected_country = 'All countries, '
            print_selected_country = 'Global, '

            # Only need to filter income groups if no country selected
            if selected_incgrp == 'All':
                prep_df_filtered = prep_df_filtered
                print_selected_incgrp = 'all income groups, '
            else:
                prep_df_filtered = prep_df_filtered.query(f"incomegroup == '{selected_incgrp}'")
                print_selected_incgrp = f'income group {selected_incgrp}, '
        else:
            prep_df_filtered = prep_df_filtered.query(f"country == '{selected_country}'")
            print_selected_country = f'{selected_country} '
            print_selected_incgrp = ''
    else:
        if selected_country == 'All':
            prep_df_filtered = prep_df_filtered.query(f"region == '{selected_region}'")
            print_selected_country = f'All {selected_region} countries,'

            # Only need to filter income groups if no country selected
            if selected_incgrp == 'All':
                prep_df_filtered = prep_df_filtered
                print_selected_incgrp = 'all income groups, '
            else:
                prep_df_filtered = prep_df_filtered.query(f"incomegroup == '{selected_incgrp}'")
                print_selected_incgrp = f'income group {selected_incgrp}, '
        else:
            prep_df_filtered = prep_df_filtered.query(f"country == '{selected_country}'")
            print_selected_country = f'{selected_country} '
            print_selected_incgrp = ''

    # Get sum for each item (summing over countries if multiple)
    prep_df_sums = prep_df_filtered.groupby('item')[['value_usd_current' ,'value_usd_ideal']].sum()
    prep_df_sums = prep_df_sums.reset_index()

    # Get total AHLE for printing
    # _netvalue = (prep_df_sums['item'] == 'Net value')
    # current_net_value = prep_df_sums.loc[_netvalue ,'value_usd_current'].values[0]
    # ideal_net_value = prep_df_sums.loc[_netvalue ,'value_usd_ideal'].values[0]
    # total_ahle = ideal_net_value - current_net_value

    # Create AHLE differences bars (ideal - current)
    prep_df_sums['value_usd_ahle_diff'] = prep_df_sums['value_usd_ideal'] - prep_df_sums['value_usd_current']

    # Add vet spend back in
    # prod_vetspend = prep_df_sums[prep_df_sums['item']=='Producers vet & med costs']['value_usd_ahle_diff'].values[0]
    # pub_vetspend = prep_df_sums[prep_df_sums['item']=='Public vet & med costs']['value_usd_ahle_diff'].values[0]

    # prep_df_sums['value_usd_ahle_diff'] = prep_df_sums['value_usd_ahle_diff'] + prep_df_sums[prep_df_sums['item']=='Biomass']
    total_ahle = prep_df_sums[prep_df_sums['item']=='Net value']['value_usd_ahle_diff'].values[0]
    # total_ahle = total_ahle + prod_vetspend + pub_vetspend

    if display =='Side by Side':
        # Create graph with current values
        name = 'Current'
        measure = ["relative", "relative", "relative", "relative", "relative", "relative", "relative", "total"]
        x = prep_df_sums['item']
        y = prep_df_sums['value_usd_current']
        ga_waterfall_fig = create_ahle_waterfall_ga(prep_df_sums, name, measure, x, y)

        # Add ideal values side-by-side
        ga_waterfall_fig.add_trace(go.Waterfall(
            name = 'Ideal',
            measure = measure,
            x = x,
            y = prep_df_sums['value_usd_ideal'],
            decreasing = {"marker":{"color":"white", "line":{"color":"#E84C3D", "width":3}}},
            increasing = {"marker":{"color":"white", "line":{"color":"#3598DB", "width":3}}},
            totals = {"marker":{"color":"white", "line":{"color":"#F7931D", "width":3}}},
            connector = {"line":{"dash":"dot"}},
            ))
        ga_waterfall_fig.update_layout(
            waterfallgroupgap = 0.5,    # Gap between bars
            )

        ga_waterfall_fig.update_layout(title_text=f'Compare Current output values and costs | {print_selected_country}{print_selected_incgrp}{selected_year}<br><sup>Total animal health loss envelope: ${total_ahle :,.0f} in constant 2010 US dollars</sup><br>',
                                        yaxis_title='US Dollars (2010 constant)',
                                        font_size=15)
    else:
        # Create graph with differences
        name = 'AHLE'
        measure = ["relative", "relative", "relative", "relative", "relative", "relative", "relative", "total"]
        x = prep_df_sums['item']
        y = prep_df_sums['value_usd_ahle_diff']
        ga_waterfall_fig = create_ahle_waterfall_ga(prep_df_sums, name, measure, x, y)

        ga_waterfall_fig.update_layout(title_text=f'Ideal minus current output values and costs | {print_selected_country}{print_selected_incgrp}{selected_year}<br><sup>Total animal health loss envelope: ${total_ahle :,.0f} in constant 2010 US dollars</sup><br>',
                                        yaxis_title='US Dollars (2010 constant)',
                                        font_size=15)

    return ga_waterfall_fig

# Global AHLE plot over time
@gbadsDash.callback(
    Output('ga-ahle-over-time','figure'),
    Input('core-data-world-ahle','data'),
    Input('select-region-detail-ga','value'),
    Input('select-incomegrp-detail-ga','value'),
    Input('select-country-detail-ga','value'),
    Input('select-item-ga','value'),
    Input('select-display-ga','value'),
    )
def update_ahle_lineplot_ga(input_json ,selected_region ,selected_incgrp ,selected_country ,selected_item ,display):
    # Read core data
    input_df = pd.read_json(input_json, orient='split')

    # Prep the data
    # Initial data prep is same as waterfall!
    prep_df = prep_ahle_forwaterfall_ga(input_df)

    # Apply user filters
    # There will always be an item filter
    prep_df_filtered = prep_df.query(f"item == '{selected_item}'")
    if selected_item == 'Net value':
        print_selected_item = f'{selected_item} over time'
    else:
        print_selected_item = f'value of {selected_item} over time'

    # Region, Country and Income group might not be filtered
    if selected_region == 'All':
        if selected_country == 'All':
            prep_df_filtered = prep_df_filtered
            print_selected_country = 'Global, '

            # Only need to filter income groups if no country selected
            if selected_incgrp == 'All':
                prep_df_filtered = prep_df_filtered
                print_selected_incgrp = 'all income groups'
            else:
                prep_df_filtered = prep_df_filtered.query(f"incomegroup == '{selected_incgrp}'")
                print_selected_incgrp = f'income group {selected_incgrp}'
        else:
            prep_df_filtered = prep_df_filtered.query(f"country == '{selected_country}'")
            print_selected_country = f'{selected_country}'
            print_selected_incgrp = ''
    else:
        if selected_country == 'All':
            prep_df_filtered = prep_df_filtered.query(f"region == '{selected_region}'")
            print_selected_country = f'All {selected_region} countries, '

            # Only need to filter income groups if no country selected
            if selected_incgrp == 'All':
                prep_df_filtered = prep_df_filtered
                print_selected_incgrp = 'all income groups'
            else:
                prep_df_filtered = prep_df_filtered.query(f"incomegroup == '{selected_incgrp}'")
                print_selected_incgrp = f'income group {selected_incgrp}'
        else:
            prep_df_filtered = prep_df_filtered.query(f"country == '{selected_country}'")
            print_selected_country = f'{selected_country}'
            print_selected_incgrp = ''

    # Create AHLE (dfiierence) value
    prep_df_filtered['value_usd_ahle_diff'] = prep_df_filtered['value_usd_ideal'] - prep_df_filtered['value_usd_current']

    # Get sum for each year
    prep_df_sums = prep_df_filtered.groupby('year')[['value_usd_current' ,'value_usd_ideal', 'value_usd_ahle_diff']].sum()
    prep_df_sums = prep_df_sums.reset_index()


    if display == "Side by Side":
        # Plot current value
        plot_current_value = go.Scatter(
            x=prep_df_sums['year']
            ,y=prep_df_sums['value_usd_current']
            ,name='Current'
            ,line=dict(color='#0028CA')
            )
        # Overlay ideal value
        plot_ideal_value = go.Scatter(
            x=prep_df_sums['year']
            ,y=prep_df_sums['value_usd_ideal']
            ,name='Ideal'
            ,line=dict(color='#00CA0F')
            )

        ga_lineplot_fig = make_subplots()
        ga_lineplot_fig.add_trace(plot_ideal_value)
        ga_lineplot_fig.add_trace(plot_current_value)
        ga_lineplot_fig.update_layout(title_text=f'Current & ideal {print_selected_item} | {print_selected_country}{print_selected_incgrp}<br><sup></sup><br>',
                                      yaxis_title='US Dollars (2010 constant)',
                                      font_size=15,
                                      plot_bgcolor="#ededed",)

    else:
        # Change line color based on if AHLE or cost is selected
        costs = "costs"
        if selected_item == 'Net value':
            # Plot AHLE value
            plot_ahle_value = go.Scatter(
                x=prep_df_sums['year']
                ,y=prep_df_sums['value_usd_ahle_diff']
                ,name=f'{display}'
                ,line=dict(color='#F7931D')
                )
        elif costs in selected_item:
            # Plot AHLE value
            plot_ahle_value = go.Scatter(
                x=prep_df_sums['year']
                ,y=prep_df_sums['value_usd_ahle_diff']
                ,name=f'{display}'
                ,line=dict(color='#E84C3D')
                )
        else:
            # Plot AHLE value
            plot_ahle_value = go.Scatter(
                x=prep_df_sums['year']
                ,y=prep_df_sums['value_usd_ahle_diff']
                ,name=f'{display}'
                ,line=dict(color='#3598DB')
                )

        ga_lineplot_fig = make_subplots()
        ga_lineplot_fig.add_trace(plot_ahle_value)
        ga_lineplot_fig.update_layout(title_text=f'Ideal minus current {print_selected_item} | {print_selected_country}{print_selected_incgrp}<br><sup></sup><br>',
                                      yaxis_title='US Dollars (2010 constant)',
                                      font_size=15,
                                      plot_bgcolor="#ededed",)


    return ga_lineplot_fig

#%% 6. RUN APP
#############################################################################################################

if __name__ == "__main__":
   # NOTE: These statements are not executed when in gunicorn, because in gunicorn this program is loaded as module

   # use_port = fa.get_open_port()  # selects first unused port >= 8050
   use_port = 8050                 # set to fixed fixed number

   fa.run_server(app, use_port, debug=True)
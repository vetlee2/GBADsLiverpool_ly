#%% About
'''
'''
#%% Structure: one row per region, antimicrobial

# -----------------------------------------------------------------------------
# Combine AM usage and importance
# -----------------------------------------------------------------------------
# Modify antimicrobial names in importance data to match
amu_importance_tomerge = amu_importance.copy()

amu_importance_tomerge['antimicrobial_class'] = amu_importance_tomerge['antimicrobial_class'].str.lower() \
   .str.strip().str.replace(' ' ,'_' ,regex=False) \
   .str.replace('/' ,'_' ,regex=False).str.replace('\\' ,'_' ,regex=False) \
   .str.replace('(' ,'_' ,regex=False).str.replace(')' ,'_' ,regex=False) \
   .str.replace('-' ,'_' ,regex=False).str.replace('+' ,'_' ,regex=False) \
   .str.replace('.' ,'_' ,regex=False).str.replace(',' ,'_' ,regex=False) \

recode_classes = {
    'cephalosporins__all_generations_':'cephalosporins__all_generations'
    ,'sulfonamids':'sulfonamides__including_trimethoprim'
    }
amu_importance_tomerge['antimicrobial_class'] = amu_importance_tomerge['antimicrobial_class'].replace(recode_classes)

datainfo(amu_importance_tomerge)

# Merge with AMU
amu2018_combined_tall = pd.merge(
    left=amu2018_m.query("region != 'Global'")
    ,right=amu_importance_tomerge[['antimicrobial_class' ,'importance_ctg']]
    ,on='antimicrobial_class'
    ,how='left'
)

# -----------------------------------------------------------------------------
# Export
# -----------------------------------------------------------------------------
datainfo(amu2018_combined_tall)

amu2018_combined_tall.to_csv(os.path.join(PRODATA_FOLDER ,'amu2018_combined_tall.csv') ,index=False)
amu2018_combined_tall.to_csv(os.path.join(DASH_DATA_FOLDER ,'amu2018_combined_tall.csv') ,index=False)

#%% Structure: one row per region

# -----------------------------------------------------------------------------
# Combine biomass and AM usage
# -----------------------------------------------------------------------------
amu2018_tomerge = amu2018.copy()

rename_region = {'Asia, Far East and Oceania':'Asia'}
amu2018_tomerge['region'] = amu2018_tomerge['region'].replace(rename_region)

# Add prefix to biomass columns
amu2018_biomass_tomerge = amu2018_biomass.add_prefix('biomass_')
amu2018_biomass_tomerge = amu2018_biomass_tomerge.rename(columns={"biomass_region":"region" ,"biomass_segment":"segment"})
datainfo(amu2018_biomass_tomerge)

amu2018_combined_regional = pd.merge(
    left=amu2018_tomerge.query("scope == 'All'").query("region != 'Global'")
    ,right=amu2018_biomass_tomerge.query("segment == 'Countries reporting AMU data'")
    ,on='region'
    ,how='left'
)

# -----------------------------------------------------------------------------
# Find proportion of AM usage going to terrestrial food producing animals
# -----------------------------------------------------------------------------
# Calculate proportion of biomass
biomass_species = [
    'biomass_bovine_kg'
    ,'biomass_swine_kg'
    ,'biomass_poultry_kg'
    ,'biomass_equine_kg'
    ,'biomass_goats_kg'
    ,'biomass_sheep_kg'
    ,'biomass_rabbits_kg'
    ,'biomass_camelids_kg'
    ,'biomass_cervids_kg'
    ,'biomass_cats_kg'
    ,'biomass_dogs_kg'
    ,'biomass_aquaculture_kg'
    ,'biomass_farmed_fish_kg'
]
biomass_tfp_species = [     # Terrestrial Food Producing
    'biomass_bovine_kg'
    ,'biomass_swine_kg'
    ,'biomass_poultry_kg'
    ,'biomass_equine_kg'
    ,'biomass_goats_kg'
    ,'biomass_sheep_kg'
    ,'biomass_rabbits_kg'
    ,'biomass_camelids_kg'
    ,'biomass_cervids_kg'
]

amu2018_combined_regional['biomass_total_kg'] = amu2018_combined_regional[biomass_species].sum(axis=1)
amu2018_combined_regional['biomass_terr_kg'] = amu2018_combined_regional[biomass_tfp_species].sum(axis=1)
amu2018_combined_regional['biomass_terr_prpn'] = amu2018_combined_regional['biomass_terr_kg'] / amu2018_combined_regional['biomass_total_kg']
amu2018_combined_regional['terr_amu_tonnes'] = amu2018_combined_regional['total_antimicrobials_tonnes'] * amu2018_combined_regional['biomass_terr_prpn']

# -----------------------------------------------------------------------------
# Add prices
# -----------------------------------------------------------------------------
amu_prices_ext_tomerge = amu_prices_ext.drop(columns=['adjustment_factor_lower' ,'adjustment_factor_upper'])

amu2018_combined_regional = pd.merge(
    left=amu2018_combined_regional
    ,right=amu_prices_ext_tomerge
    ,on='region'
    ,how='left'
)

# -----------------------------------------------------------------------------
# Export
# -----------------------------------------------------------------------------
datainfo(amu2018_combined_regional)

amu2018_combined_regional.to_csv(os.path.join(PRODATA_FOLDER ,'amu2018_combined_regional.csv') ,index=False)

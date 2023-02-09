#%% About
'''
'''
#%% Structure: one row per region & antimicrobial

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
# Add biomass data
# -----------------------------------------------------------------------------
# Merge
amu2018_combined_tall = pd.merge(
    left=amu2018_combined_tall
    ,right=amu2018_biomass[['region' ,'segment' ,'biomass_total_kg' ,'biomass_total_terr_kg']].query("segment == 'Countries reporting AMU data'")
    ,on='region'
    ,how='left'
)
del amu2018_combined_tall['segment']

# Apply appropriate biomass to each row based on scope
def biomass_for_scope(INPUT_ROW):
    if INPUT_ROW['scope'].upper() == 'ALL':
        OUTPUT = INPUT_ROW['biomass_total_kg']
    elif INPUT_ROW['scope'].upper() == 'TERRESTRIAL FOOD PRODUCING':
        OUTPUT = INPUT_ROW['biomass_total_terr_kg']
    else:
        OUTPUT = np.nan
    return OUTPUT
amu2018_combined_tall['biomass_total_kg'] = amu2018_combined_tall.apply(biomass_for_scope ,axis=1)
del amu2018_combined_tall['biomass_total_terr_kg']

# Calculate AMU per kg biomass
amu2018_combined_tall['amu_mg_perkgbiomass'] = (amu2018_combined_tall['amu_tonnes'] / amu2018_combined_tall['biomass_total_kg']) * 1e9

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
amu2018_combined_regional = pd.merge(
    left=amu2018.query("scope == 'All'").query("region != 'Global'")
    ,right=amu2018_biomass.query("segment == 'Countries reporting AMU data'")
    ,on='region'
    ,how='left'
)

# -----------------------------------------------------------------------------
# Find proportion of AM usage going to terrestrial food producing animals
# -----------------------------------------------------------------------------
# Calculate proportion of biomass
amu2018_combined_regional['biomass_terr_prpn'] = amu2018_combined_regional['biomass_total_terr_kg'] / amu2018_combined_regional['biomass_total_kg']
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

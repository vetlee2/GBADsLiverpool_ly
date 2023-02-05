#%% About
'''
'''
#%% Doit

# -----------------------------------------------------------------------------
# Combine biomass and AM usage
# -----------------------------------------------------------------------------
amu2018_tomerge = amu2018.copy()

rename_region = {'Asia, Far East and Oceania':'Asia'}
amu2018_tomerge['region'] = amu2018_tomerge['region'].replace(rename_region)

amu2018_withbiomass = pd.merge(
    left=amu2018_tomerge.query("scope == 'All'")
    ,right=amu2018_biomass.query("segment == 'Countries reporting AMU data'")
    ,on='region'
    ,how='outer'
)

# -----------------------------------------------------------------------------
# Find proportion of AM usage going to terrestrial food producing animals
# -----------------------------------------------------------------------------
# Calculate proportion of biomass
biomass_species = [
    'bovine_kg'
    ,'swine_kg'
    ,'poultry_kg'
    ,'equine_kg'
    ,'goats_kg'
    ,'sheep_kg'
    ,'rabbits_kg'
    ,'camelids_kg'
    ,'cervids_kg'
    ,'cats_kg'
    ,'dogs_kg'
    ,'aquaculture_kg'
    ,'farmed_fish_kg'
]
biomass_tfp_species = [     # Terrestrial Food Producing
    'bovine_kg'
    ,'swine_kg'
    ,'poultry_kg'
    ,'equine_kg'
    ,'goats_kg'
    ,'sheep_kg'
    ,'rabbits_kg'
    ,'camelids_kg'
    ,'cervids_kg'
]

amu2018_withbiomass['total_kg'] = amu2018_withbiomass[biomass_species].sum(axis=1)
amu2018_withbiomass['terr_kg'] = amu2018_withbiomass[biomass_tfp_species].sum(axis=1)
amu2018_withbiomass['terr_prpn'] = amu2018_withbiomass['terr_kg'] / amu2018_withbiomass['total_kg']
amu2018_withbiomass['terr_amu_tonnes'] = amu2018_withbiomass['total_antimicrobials_tonnes'] * amu2018_withbiomass['terr_prpn']

datainfo(amu2018_withbiomass)

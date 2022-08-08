#%% About
'''
'''
#%% Merge

# =============================================================================
#### Prep UN Geo codes
# =============================================================================
try:
   un_geo_codes.shape
except NameError:
   un_geo_codes = pd.read_pickle(os.path.join(RAWDATA_FOLDER ,'un_geo_codes.pkl.gz'))

un_geo_codes_tomatch = un_geo_codes.copy()

keep_rename_cols_ordered = {
    'shortname':'country'
    ,'iso3':'country_iso3'
    # ,'iso2':'country_iso2'
    }
un_geo_codes_tomatch = un_geo_codes_tomatch[list(keep_rename_cols_ordered)].rename(columns=keep_rename_cols_ordered)

# Add Puerto Rico
add_geo_codes = pd.DataFrame({"country":"Puerto Rico" ,"country_iso3":"PRI"}
                             ,index=[0])
un_geo_codes_tomatch = pd.concat([un_geo_codes_tomatch ,add_geo_codes])

countries_geocodes = list(un_geo_codes_tomatch['country'].unique())

# =============================================================================
#### Prep Base table: biomass
# =============================================================================
try:
   biomass.shape
except NameError:
   biomass = pd.read_pickle(os.path.join(RAWDATA_FOLDER ,'livestock_countries_biomass.pkl.gz'))

countries_biomass = list(biomass['country'].unique())

# Reconcile country names with UN Geo Codes
recode_countries = {
    "China, Hong Kong SAR":"Hong Kong"
    ,"Cte d'Ivoire":"Côte d'Ivoire"
    ,"Sudan (former)":"Sudan"
}
biomass['country'] = biomass['country'].replace(recode_countries)

# Add country iso code
biomass_iso = pd.merge(
    left=biomass
    ,right=un_geo_codes_tomatch
    ,on='country'
    ,how='left'
    )
datainfo(biomass_iso)

biomass_iso_missing = biomass_iso.query("country_iso3.isnull()")

# =============================================================================
#### Prep FAO tables
# =============================================================================
try:
   fao_production_p.shape
except NameError:
   fao_production_p = pd.read_pickle(os.path.join(RAWDATA_FOLDER ,'fao_production.pkl.gz'))

try:
   fao_producerprice_p.shape
except NameError:
   fao_producerprice_p = pd.read_pickle(os.path.join(RAWDATA_FOLDER ,'fao_producerprice.pkl.gz'))

# Combine FAO tables
fao_combo = pd.merge(
    left=fao_production_p
    ,right=fao_producerprice_p
    ,on=['country' ,'year']
    ,how='outer'
    ,indicator='_merge_fao'
    )
fao_combo['_merge_fao'].value_counts()
fao_country_merge_status = fao_combo[['country' ,'_merge_fao']].value_counts()

countries_fao = list(fao_combo['country'].unique())

# Reconcile country names with UN Geo Codes
recode_countries = {
    "China":"China"
    ,"China, Hong Kong SAR":"Hong Kong"
    # ,"China, Macao SAR":""
    ,"China, Taiwan Province of":"Taiwan, Province of China"
    # ,"China, mainland":""
    ,"Sudan (former)":"Sudan"
}
fao_combo['country'] = fao_combo['country'].replace(recode_countries)

# Add country iso code
fao_combo_iso = pd.merge(
    left=fao_combo
    ,right=un_geo_codes_tomatch
    ,on='country'
    ,how='left'
    )
datainfo(fao_combo_iso)

# =============================================================================
#### Prep World Bank tables
# =============================================================================
try:
   wb_income.shape
except NameError:
   wb_income = pd.read_pickle(os.path.join(RAWDATA_FOLDER ,'wb_income.pkl.gz'))

try:
   wb_region.shape
except NameError:
   wb_region = pd.read_pickle(os.path.join(RAWDATA_FOLDER ,'wb_region.pkl.gz'))

try:
   wb_infl_exchg.shape
except NameError:
   wb_infl_exchg = pd.read_pickle(os.path.join(RAWDATA_FOLDER ,'wb_infl_exchg.pkl.gz'))

# Combine World Bank tables
wb_combo = pd.merge(
    left=wb_income
    ,right=wb_region
    ,on='iso3'
    ,how='outer'
    ,indicator='_merge_wb_1'
    )
wb_combo['_merge_wb_1'].value_counts()

wb_combo = pd.merge(
    left=wb_combo
    ,right=wb_infl_exchg
    ,on=['iso3' ,'year']
    ,how='outer'
    ,indicator='_merge_wb_2'
    )
wb_combo['_merge_wb_2'].value_counts()

wb_combo = wb_combo.rename(columns={"iso3":"country_iso3"})

# =============================================================================
#### Merge
# =============================================================================
# FAO onto Biomass
world_ahle_abt = pd.merge(
    left=biomass_iso
    ,right=fao_combo_iso
    ,on=['country_iso3' ,'year']
    ,how='left'
    ,indicator='_merge_1'
    )
world_ahle_abt['_merge_1'].value_counts()

# World Bank
world_ahle_abt = pd.merge(
    left=world_ahle_abt
    ,right=wb_combo
    ,on=['country_iso3' ,'year']
    ,how='left'
    ,indicator='_merge_2'
    )
world_ahle_abt['_merge_2'].value_counts()

# Drop and Rename
world_ahle_abt = world_ahle_abt.drop(columns=[
    'country'
    ,'country_y'
    ,'time_code'
    ,'_merge_fao'
    ,'_merge_1'
    ,'flag_wb'
    ,'_merge_wb_1'
    ,'_merge_wb_2'
    ,'_merge_2'
    ]
    ,errors='ignore')
world_ahle_abt = world_ahle_abt.rename(columns={'country_x':'country' ,'flag_x':'flag_biomass' ,'flag_y':'flag_wb'})

# ----------------------------------------------------------------------------
# Describe and output
# ----------------------------------------------------------------------------
datainfo(world_ahle_abt)

world_ahle_abt.to_csv(os.path.join(PRODATA_FOLDER ,'world_ahle_abt.csv'))
world_ahle_abt.to_pickle(os.path.join(PRODATA_FOLDER ,'world_ahle_abt.pkl.gz'))

#%% Explore

# Missing iso3?
iso3_by_country = world_ahle_abt[['country' ,'country_iso3']].value_counts()
iso3_missing = world_ahle_abt.query("country_iso3.isnull()")
iso3_missing_countries = list(iso3_missing['country'].unique())

#%% Impute

# =============================================================================
#### Production
# =============================================================================
# Fill missings with zero
production_cols = [i for i in list(world_ahle_abt) if 'production' in i]
for COL in production_cols:
    newcol = COL + '_imp'
    world_ahle_abt[newcol] = world_ahle_abt[COL].replace(np.nan ,0)

# =============================================================================
#### Producer Prices
# =============================================================================

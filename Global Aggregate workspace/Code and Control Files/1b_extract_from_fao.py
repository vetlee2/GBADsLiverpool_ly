#%% About
'''
'''
#%% Import FAO tables

# =============================================================================
#### Crops and Livestock
# https://www.fao.org/faostat/en/#data/QCL
# =============================================================================
# ----------------------------------------------------------------------------
# Import
# ----------------------------------------------------------------------------
fao_production = pd.read_csv(os.path.join(RAWDATA_FOLDER ,'FAOSTAT_livestock_products_2000_2020.csv'))
cleancolnames(fao_production)
datainfo(fao_production)

# ----------------------------------------------------------------------------
# Reshape so each element_item_unit is its own column
# ----------------------------------------------------------------------------
fao_production_element_items = fao_production[['element' ,'item' ,'unit']].value_counts()

fao_production_p = fao_production.pivot(
    index=['area' ,'year']          # Column(s) to make new index. If blank, uses existing index.
    ,columns=['element' ,'item' ,'unit']       # Column(s) to make new columns
    ,values='value'        # Column to populate rows. Can pass a list, but will create multi-indexed columns.
)
fao_production_p = indextocolumns(fao_production_p)
fao_production_p = colnames_from_index(fao_production_p)
cleancolnames(fao_production_p)

# Rename columns programmatically
collist = list(fao_production_p)
colname_modifier = pd.DataFrame({'old_name':collist})
colname_modifier['new_name'] = colname_modifier['old_name']
colname_modifier['new_name'] = colname_modifier['new_name'].str.replace('__' ,'_')
colname_modifier['new_name'] = colname_modifier['new_name'].str.replace('area' ,'country')

colname_modifier = colname_modifier.set_index(keys='old_name') 	# Column to become dictionary keys
rename_columns = dict(colname_modifier['new_name'])    # Data Frame Index becomes keys and values of col_b become values
fao_production_p = fao_production_p.rename(columns=rename_columns)

# Drop yield columns
yield_cols = [i for i in list(fao_production_p) if 'yield' in i]
fao_production_p = fao_production_p.drop(columns=yield_cols)

# ----------------------------------------------------------------------------
# Describe and output
# ----------------------------------------------------------------------------
datainfo(fao_production_p)
# datadesc(fao_production_p ,RAWDATA_FOLDER)

fao_production_p.to_csv(os.path.join(RAWDATA_FOLDER ,'fao_production_p.csv'))
fao_production_p.to_pickle(os.path.join(RAWDATA_FOLDER ,'fao_production.pkl.gz'))

# =============================================================================
#### Producer Prices
# https://www.fao.org/faostat/en/#data/PP
# =============================================================================
# ----------------------------------------------------------------------------
# Import
# ----------------------------------------------------------------------------
fao_producerprice_imp = pd.read_csv(os.path.join(RAWDATA_FOLDER ,'FAOSTAT_producer_prices_2000_2021.csv'))
cleancolnames(fao_producerprice_imp)
datainfo(fao_producerprice_imp)

# ----------------------------------------------------------------------------
# Reshape so each element_item_unit is its own column
# ----------------------------------------------------------------------------
fao_producerprice_element_items = fao_producerprice_imp[['element' ,'item' ,'unit']].value_counts()

fao_producerprice_p = fao_producerprice_imp.pivot(
    index=['area' ,'year']          # Column(s) to make new index. If blank, uses existing index.
    ,columns=['element' ,'item' ,'unit']       # Column(s) to make new columns
    ,values='value'        # Column to populate rows. Can pass a list, but will create multi-indexed columns.
    )
fao_producerprice_p = fao_producerprice_p.reset_index(drop=False)
fao_producerprice_p = colnames_from_index(fao_producerprice_p)
cleancolnames(fao_producerprice_p)

# Rename columns programmatically
collist = list(fao_producerprice_p)
colname_modifier = pd.DataFrame({'old_name':collist})
colname_modifier['new_name'] = colname_modifier['old_name']
colname_modifier['new_name'] = colname_modifier['new_name'].str.replace('__' ,'_')
colname_modifier['new_name'] = colname_modifier['new_name'].str.replace('area_' ,'country')
colname_modifier['new_name'] = colname_modifier['new_name'].str.replace('year_' ,'year')
colname_modifier['new_name'] = colname_modifier['new_name'].str.replace('_lcu_tonne_' ,'_')
colname_modifier['new_name'] = colname_modifier['new_name'].str.replace('_slc_tonne_' ,'_')
colname_modifier['new_name'] = colname_modifier['new_name'].str.replace('_usd_tonne_' ,'_')
colname_modifier['new_name'] = colname_modifier['new_name'].str.replace('_lcu' ,'_lcupertonne')
colname_modifier['new_name'] = colname_modifier['new_name'].str.replace('_slc' ,'_slcpertonne')
colname_modifier['new_name'] = colname_modifier['new_name'].str.replace('_usd' ,'_usdpertonne')
colname_modifier['new_name'] = colname_modifier['new_name'].str.replace('live_weight' ,'livewt')

colname_modifier = colname_modifier.set_index(keys='old_name') 	# Column to become dictionary keys
rename_columns = dict(colname_modifier['new_name'])    # Data Frame Index becomes keys and values of col_b become values
fao_producerprice_p = fao_producerprice_p.rename(columns=rename_columns)

# ----------------------------------------------------------------------------
# Describe and output
# ----------------------------------------------------------------------------
datainfo(fao_producerprice_p)
# datadesc(fao_producerprice_p ,RAWDATA_FOLDER)

fao_producerprice_p.to_csv(os.path.join(RAWDATA_FOLDER ,'fao_producerprice.csv'))
fao_producerprice_p.to_pickle(os.path.join(RAWDATA_FOLDER ,'fao_producerprice.pkl.gz'))

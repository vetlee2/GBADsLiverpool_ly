#%% About
'''
Importing and exploring the antimicrobial data
'''
#%% Import Antimicrobial Usage 2018 report

input_amu_report_file = os.path.join(RAWDATA_FOLDER ,'AMU_2018_6th report_GBADs.xlsx')

# =============================================================================
#### Antimicrobial usage
# =============================================================================
# -----------------------------------------------------------------------------
# All
# -----------------------------------------------------------------------------
amu2018_allspec = pd.read_excel(
	input_amu_report_file
	,sheet_name='Antimicrobial Quantities (AQ)'
	,skiprows=7                 # List: row numbers to skip. Integer: count of rows to skip at start of file
    ,nrows=12                    # Total number of rows to read
)
cleancolnames(amu2018_allspec)
amu2018_allspec.columns = amu2018_allspec.columns.str.strip('_')    # Remove trailing underscores

# Clean up region names
amu2018_allspec[['region' ,'count']] = amu2018_allspec['unnamed:_0'].str.split('(' ,expand=True)    # Splitting at hyphen (-). expand=True to return multiple columns.
amu2018_allspec['region'] = amu2018_allspec['region'].str.rstrip()      # Drop trailing blanks

# Drop rows where region is missing - these are summary rows
amu2018_allspec = amu2018_allspec.dropna(subset='region')

# Drop columns
amu2018_allspec = amu2018_allspec.drop(columns=['unnamed:_0' ,'unnamed:_26' ,'count'])

# Reorder columns and sort
cols_first = ['region' ,'number_of_countries']
cols_other = [i for i in list(amu2018_allspec) if i not in cols_first]
amu2018_allspec = amu2018_allspec.reindex(columns=cols_first + cols_other)
amu2018_allspec = amu2018_allspec.sort_values(by=cols_first ,ignore_index=True)

# Add column suffixes
amu2018_allspec = amu2018_allspec.add_suffix('_tonnes')
amu2018_allspec = amu2018_allspec.rename(columns={
    'region_tonnes':'region'
    ,'number_of_countries_tonnes':'number_of_countries'
    ,'total_tonnes_tonnes':'total_antimicrobials_tonnes'
    }
)

# Rename total region
rename_region = {'Total':'Global'}
amu2018_allspec['region'] = amu2018_allspec['region'].replace(rename_region)

datainfo(amu2018_allspec)

# -----------------------------------------------------------------------------
# Terrestrial
# -----------------------------------------------------------------------------
amu2018_ter = pd.read_excel(
	input_amu_report_file
	,sheet_name='AQ-Terrestrial'
	,skiprows=2                 # List: row numbers to skip. Integer: count of rows to skip at start of file
    ,nrows=7                    # Total number of rows to read
)
cleancolnames(amu2018_ter)
amu2018_ter.columns = amu2018_ter.columns.str.strip('_')    # Remove trailing underscores

# Clean up region names
amu2018_ter[['region' ,'count']] = amu2018_ter['unnamed:_0'].str.split('(' ,expand=True)    # Splitting at hyphen (-). expand=True to return multiple columns.
amu2018_ter['region'] = amu2018_ter['region'].str.rstrip()      # Drop trailing blanks

# Drop rows where region is missing - these are summary rows
amu2018_ter = amu2018_ter.dropna(subset='region')

# Drop columns
amu2018_ter = amu2018_ter.drop(columns=['unnamed:_0' ,'total_kg' ,'unnamed:_26' ,'count'])

# Reorder columns and sort
cols_first = ['region' ,'number_of_countries']
cols_other = [i for i in list(amu2018_ter) if i not in cols_first]
amu2018_ter = amu2018_ter.reindex(columns=cols_first + cols_other)
amu2018_ter = amu2018_ter.sort_values(by=cols_first ,ignore_index=True)

# Add column suffixes
amu2018_ter = amu2018_ter.add_suffix('_tonnes')
amu2018_ter = amu2018_ter.rename(columns={'region_tonnes':'region' ,'number_of_countries_tonnes':'number_of_countries'})

# Add Middle East by subtraction
amu2018_ter_t = amu2018_ter.transpose()     # Transpose regions to columns
colnames = list(amu2018_ter_t.iloc[0])      # Get names from desired row
amu2018_ter_t.columns = colnames			# Rename columns
# cleancolnames(amu2018_ter_t)
amu2018_ter_t = amu2018_ter_t.drop(index='region')		# Drop row used for names
amu2018_ter_t = amu2018_ter_t.astype('float')   # Change all columns to numeric
datainfo(amu2018_ter_t)

amu2018_ter_t['Middle East'] = amu2018_ter_t['Global'] - (amu2018_ter_t['Africa'] + amu2018_ter_t['Americas'] + amu2018_ter_t['Asia, Far East and Oceania'] + amu2018_ter_t['Europe'])
amu2018_ter_t['Middle East'] = round(amu2018_ter_t['Middle East'] ,3)

amu2018_ter_t_t = amu2018_ter_t.transpose()
amu2018_ter_t_t = amu2018_ter_t_t.reset_index()
amu2018_ter_t_t = amu2018_ter_t_t.rename(columns={'index':'region'})

datainfo(amu2018_ter_t_t)

# -----------------------------------------------------------------------------
# Growth promotants
# -----------------------------------------------------------------------------
amu2018_agp = pd.read_excel(
	input_amu_report_file
	,sheet_name='AQ-AGPs'
	,skiprows=2                 # List: row numbers to skip. Integer: count of rows to skip at start of file
    ,nrows=6                    # Total number of rows to read
)
cleancolnames(amu2018_agp)
amu2018_agp.columns = amu2018_agp.columns.str.strip('_')    # Remove trailing underscores

# Clean up region names
amu2018_agp[['region' ,'count']] = amu2018_agp['unnamed:_0'].str.split('(' ,expand=True)    # Splitting at hyphen (-). expand=True to return multiple columns.
amu2018_agp['region'] = amu2018_agp['region'].str.rstrip()      # Drop trailing blanks

# Drop rows where region is missing - these are summary rows
amu2018_agp = amu2018_agp.dropna(subset='region')

# Drop columns
amu2018_agp = amu2018_agp.drop(columns=['unnamed:_0' ,'total_kg' ,'unnamed:_26' ,'count'])

# Reorder columns and sort
cols_first = ['region' ,'number_of_countries']
cols_other = [i for i in list(amu2018_agp) if i not in cols_first]
amu2018_agp = amu2018_agp.reindex(columns=cols_first + cols_other)
amu2018_agp = amu2018_agp.sort_values(by=cols_first ,ignore_index=True)

# Add column suffixes
amu2018_agp = amu2018_agp.add_suffix('_tonnes')
amu2018_agp = amu2018_agp.rename(columns={'region_tonnes':'region' ,'number_of_countries_tonnes':'number_of_countries'})

# Rename total region
rename_region = {'Total':'Global'}
amu2018_agp['region'] = amu2018_agp['region'].replace(rename_region)

datainfo(amu2018_agp)

# -----------------------------------------------------------------------------
# Stack and export
# -----------------------------------------------------------------------------
# Add indicator of scope
amu2018_allspec['scope'] = 'All'
amu2018_ter_t_t['scope'] = 'Terrestrial Food Producing'
amu2018_agp['scope'] = 'AGP'

amu2018 = pd.concat(
    [amu2018_allspec ,amu2018_ter_t_t ,amu2018_agp]
	,axis=0              # axis=0: concatenate rows (stack), axis=1: concatenate columns (merge)
	,join='outer'        # 'outer': keep all index values from all data frames
	,ignore_index=True   # True: do not keep index values on concatenation axis
)

# Reorder columns and sort
cols_first = ['scope' ,'region' ,'number_of_countries']
cols_other = [i for i in list(amu2018) if i not in cols_first]
amu2018 = amu2018.reindex(columns=cols_first + cols_other)
amu2018 = amu2018.sort_values(by=cols_first ,ignore_index=True)

datainfo(amu2018)

# Profile
# profile = amu2018.profile_report()
# profile.to_file(os.path.join(PRODATA_FOLDER ,'amu2018_profile.html'))

# Export
amu2018.to_csv(os.path.join(PRODATA_FOLDER ,'amu2018.csv') ,index=False)

# -----------------------------------------------------------------------------
# Reshape
# -----------------------------------------------------------------------------
amu2018_m = amu2018.melt(
	id_vars=['region' ,'scope' ,'number_of_countries']         # Optional: column(s) to use as ID variables
	,var_name='antimicrobial_class'             # Name for new "variable" column
	,value_name='amu_tonnes'              # Name for new "value" column
)
amu2018_m['amu_tonnes'] = amu2018_m['amu_tonnes'].fillna(0)
amu2018_m['antimicrobial_class'] = amu2018_m['antimicrobial_class'].str.replace('_tonnes' ,'')

datainfo(amu2018_m)

# Export
amu2018_m.to_csv(os.path.join(PRODATA_FOLDER ,'amu2018_tall.csv') ,index=False)

# =============================================================================
#### Species
# =============================================================================
# -----------------------------------------------------------------------------
# Detailed species
# -----------------------------------------------------------------------------
amu2018_species_dtl = pd.read_excel(
	input_amu_report_file
	,sheet_name='Species covered'
	,skiprows=3                 # List: row numbers to skip. Integer: count of rows to skip at start of file
    ,nrows=5                    # Total number of rows to read
)
cleancolnames(amu2018_species_dtl)
amu2018_species_dtl.columns = amu2018_species_dtl.columns.str.strip('_')    # Remove trailing underscores

# Rename region column
amu2018_species_dtl = amu2018_species_dtl.rename(columns={'unnamed:_0':'region'})

# Add column suffixes
amu2018_species_dtl = amu2018_species_dtl.add_suffix('_n_countries')
amu2018_species_dtl = amu2018_species_dtl.rename(columns={'region_n_countries':'region'})

datainfo(amu2018_species_dtl)

# Export
amu2018_species_dtl.to_csv(os.path.join(PRODATA_FOLDER ,'amu2018_species_dtl.csv') ,index=False)

# -----------------------------------------------------------------------------
# Species groups
# -----------------------------------------------------------------------------
amu2018_species_grp = pd.read_excel(
	input_amu_report_file
	,sheet_name='Species covered'
	,skiprows=16                 # List: row numbers to skip. Integer: count of rows to skip at start of file
    ,nrows=5                    # Total number of rows to read
)
cleancolnames(amu2018_species_grp)
amu2018_species_grp.columns = amu2018_species_grp.columns.str.strip('_')    # Remove trailing underscores

# Rename region column
amu2018_species_grp = amu2018_species_grp.rename(columns={'unnamed:_0':'region'})

# Add column suffixes
amu2018_species_grp = amu2018_species_grp.add_suffix('_n_countries')
amu2018_species_grp = amu2018_species_grp.rename(columns={'region_n_countries':'region'})

# Drop empty columns
amu2018_species_grp = amu2018_species_grp.dropna(axis=1)    # 0 = drop rows, 1 = drop columns

datainfo(amu2018_species_grp)

# Export
amu2018_species_grp.to_csv(os.path.join(PRODATA_FOLDER ,'amu2018_species_grp.csv') ,index=False)

# =============================================================================
#### Biomass
# =============================================================================
# -----------------------------------------------------------------------------
# Global
# -----------------------------------------------------------------------------
amu2018_biomass_glbl = pd.read_excel(
	input_amu_report_file
	,sheet_name='Animal Biomass'
	,skiprows=3                 # List: row numbers to skip. Integer: count of rows to skip at start of file
    ,nrows=3                    # Total number of rows to read
)
cleancolnames(amu2018_biomass_glbl)

# Rename segment column
amu2018_biomass_glbl = amu2018_biomass_glbl.rename(columns={'unnamed:_1':'segment'})

# Drop rows where segment is missing - these are summary rows
amu2018_biomass_glbl = amu2018_biomass_glbl.dropna(subset='segment')

# Drop columns
dropcols = [i for i in amu2018_biomass_glbl if 'unnamed' in i]
amu2018_biomass_glbl = amu2018_biomass_glbl.drop(columns=dropcols)

# Change column types
amu2018_biomass_glbl[['cats' ,'dogs']] = amu2018_biomass_glbl[['cats' ,'dogs']].astype('float64')

datainfo(amu2018_biomass_glbl)

# -----------------------------------------------------------------------------
# AFRICA
# -----------------------------------------------------------------------------
amu2018_biomass_rgn_af = pd.read_excel(
	input_amu_report_file
	,sheet_name='Animal Biomass'
	,skiprows=12                 # List: row numbers to skip. Integer: count of rows to skip at start of file
    ,nrows=3                    # Total number of rows to read
)
cleancolnames(amu2018_biomass_rgn_af)

# Rename segment column
amu2018_biomass_rgn_af = amu2018_biomass_rgn_af.rename(columns={'2017':'segment'})

# Drop rows where segment is missing - these are summary rows
amu2018_biomass_rgn_af = amu2018_biomass_rgn_af.dropna(subset='segment')

# Drop columns
dropcols = [i for i in amu2018_biomass_rgn_af if 'unnamed' in i]
amu2018_biomass_rgn_af = amu2018_biomass_rgn_af.drop(columns=dropcols)

# Change column types
amu2018_biomass_rgn_af[['cats' ,'dogs']] = amu2018_biomass_rgn_af[['cats' ,'dogs']].astype('float64')

datainfo(amu2018_biomass_rgn_af)

# -----------------------------------------------------------------------------
# AMERICAS
# -----------------------------------------------------------------------------
amu2018_biomass_rgn_am = pd.read_excel(
	input_amu_report_file
	,sheet_name='Animal Biomass'
	,skiprows=21                 # List: row numbers to skip. Integer: count of rows to skip at start of file
    ,nrows=3                    # Total number of rows to read
)
cleancolnames(amu2018_biomass_rgn_am)

# Rename segment column
amu2018_biomass_rgn_am = amu2018_biomass_rgn_am.rename(columns={'2017':'segment'})

# Drop rows where segment is missing - these are summary rows
amu2018_biomass_rgn_am = amu2018_biomass_rgn_am.dropna(subset='segment')

# Drop columns
dropcols = [i for i in amu2018_biomass_rgn_am if 'unnamed' in i]
amu2018_biomass_rgn_am = amu2018_biomass_rgn_am.drop(columns=dropcols)

# Change column types
amu2018_biomass_rgn_am[['cats' ,'dogs']] = amu2018_biomass_rgn_am[['cats' ,'dogs']].astype('float64')

datainfo(amu2018_biomass_rgn_am)

# -----------------------------------------------------------------------------
# ASIA
# -----------------------------------------------------------------------------
amu2018_biomass_rgn_as = pd.read_excel(
	input_amu_report_file
	,sheet_name='Animal Biomass'
	,skiprows=31                 # List: row numbers to skip. Integer: count of rows to skip at start of file
    ,nrows=3                    # Total number of rows to read
)
cleancolnames(amu2018_biomass_rgn_as)

# Rename segment column
amu2018_biomass_rgn_as = amu2018_biomass_rgn_as.rename(columns={'2017':'segment'})

# Drop rows where segment is missing - these are summary rows
amu2018_biomass_rgn_as = amu2018_biomass_rgn_as.dropna(subset='segment')

# Drop columns
dropcols = [i for i in amu2018_biomass_rgn_as if 'unnamed' in i]
amu2018_biomass_rgn_as = amu2018_biomass_rgn_as.drop(columns=dropcols)

# Change column types
amu2018_biomass_rgn_as[['cats' ,'dogs']] = amu2018_biomass_rgn_as[['cats' ,'dogs']].astype('float64')

datainfo(amu2018_biomass_rgn_as)

# -----------------------------------------------------------------------------
# EUROPE
# -----------------------------------------------------------------------------
amu2018_biomass_rgn_eu = pd.read_excel(
	input_amu_report_file
	,sheet_name='Animal Biomass'
	,skiprows=42                 # List: row numbers to skip. Integer: count of rows to skip at start of file
    ,nrows=3                    # Total number of rows to read
)
cleancolnames(amu2018_biomass_rgn_eu)

# Rename segment column
amu2018_biomass_rgn_eu = amu2018_biomass_rgn_eu.rename(columns={'2017':'segment'})

# Drop rows where segment is missing - these are summary rows
amu2018_biomass_rgn_eu = amu2018_biomass_rgn_eu.dropna(subset='segment')

# Drop columns
dropcols = [i for i in amu2018_biomass_rgn_eu if 'unnamed' in i]
amu2018_biomass_rgn_eu = amu2018_biomass_rgn_eu.drop(columns=dropcols)

# Change column types
amu2018_biomass_rgn_eu[['cats' ,'dogs']] = amu2018_biomass_rgn_eu[['cats' ,'dogs']].astype('float64')

datainfo(amu2018_biomass_rgn_eu)

# -----------------------------------------------------------------------------
# MIDDLE EAST
# -----------------------------------------------------------------------------
amu2018_biomass_rgn_me = pd.read_excel(
	input_amu_report_file
	,sheet_name='Animal Biomass'
	,skiprows=53                 # List: row numbers to skip. Integer: count of rows to skip at start of file
    ,nrows=3                    # Total number of rows to read
)
cleancolnames(amu2018_biomass_rgn_me)

# Rename segment column
amu2018_biomass_rgn_me = amu2018_biomass_rgn_me.rename(columns={'2017':'segment'})

# Drop rows where segment is missing - these are summary rows
amu2018_biomass_rgn_me = amu2018_biomass_rgn_me.dropna(subset='segment')

# Drop columns
dropcols = [i for i in amu2018_biomass_rgn_me if 'unnamed' in i]
amu2018_biomass_rgn_me = amu2018_biomass_rgn_me.drop(columns=dropcols)

# Change column types
amu2018_biomass_rgn_me[['cats' ,'dogs']] = amu2018_biomass_rgn_me[['cats' ,'dogs']].astype('float64')

datainfo(amu2018_biomass_rgn_me)

# -----------------------------------------------------------------------------
# Stack and export
# -----------------------------------------------------------------------------
amu2018_biomass_glbl['region'] = 'Global'
amu2018_biomass_rgn_af['region'] = 'Africa'
amu2018_biomass_rgn_am['region'] = 'Americas'
amu2018_biomass_rgn_as['region'] = 'Asia'
amu2018_biomass_rgn_eu['region'] = 'Europe'
amu2018_biomass_rgn_me['region'] = 'Middle East'

amu2018_biomass = pd.concat(
    [amu2018_biomass_glbl
    ,amu2018_biomass_rgn_af
    ,amu2018_biomass_rgn_am
    ,amu2018_biomass_rgn_as
    ,amu2018_biomass_rgn_eu
    ,amu2018_biomass_rgn_me
    ]
	,axis=0              # axis=0: concatenate rows (stack), axis=1: concatenate columns (merge)
	,join='outer'        # 'outer': keep all index values from all data frames
	,ignore_index=True   # True: do not keep index values on concatenation axis
)

# Add column suffixes
amu2018_biomass = amu2018_biomass.add_suffix('_kg')
amu2018_biomass = amu2018_biomass.rename(columns={'region_kg':'region' ,'segment_kg':'segment'})

# Reorder columns and sort
cols_first = ['region' ,'segment']
cols_other = [i for i in list(amu2018_biomass) if i not in cols_first]
amu2018_biomass = amu2018_biomass.reindex(columns=cols_first + cols_other)
amu2018_biomass = amu2018_biomass.sort_values(by=cols_first ,ignore_index=True)

datainfo(amu2018_biomass)

# Profile
# profile = amu2018_biomass.profile_report()
# profile.to_file(os.path.join(PRODATA_FOLDER ,'amu2018_biomass_profile.html'))

# Export
amu2018_biomass.to_csv(os.path.join(PRODATA_FOLDER ,'amu2018_biomass.csv') ,index=False)

#%% Import list of important antibiotics

amu_importance = pd.read_excel(
    os.path.join(RAWDATA_FOLDER ,'WHO CIA and HIA.xlsx')
)
cleancolnames(amu_importance)

# Rename columns
amu_importance = amu_importance.rename(columns={"unnamed:_0":"antimicrobial_class"})

# Ensure all columns are string
amu_importance = amu_importance.astype('str')

# Combine categories into single column
def combine_importance(INPUT_ROW):
    if 'Y' in INPUT_ROW['critically_important_antimicrobials'].upper():
        OUTPUT = 'A: Critically Important'
    elif 'Y' in INPUT_ROW['highly_important_antimicrobials'].upper():
        OUTPUT = 'B: Highly Important'
    else:
        OUTPUT = 'C: Other'
    return OUTPUT
amu_importance['importance_ctg'] = amu_importance.apply(combine_importance ,axis=1)      # Apply to each row of the dataframe (axis=1)

datainfo(amu_importance)

#%% Import price data

# =============================================================================
#### Raw price data
# =============================================================================
amu_prices = pd.read_excel(
    os.path.join(RAWDATA_FOLDER ,'AMU_ euros per ton.xlsx')
	,skiprows=2                 # List: row numbers to skip. Integer: count of rows to skip at start of file
    ,nrows=5                    # Total number of rows to read
)
cleancolnames(amu_prices)

# Rename, drop columns
amu_prices = amu_prices.rename(columns={'unnamed:_0':'category'})
amu_prices = amu_prices.drop(columns=['unnamed:_5' ,'reference_price_europe'])

# Add columns based on metadata
amu_prices['region'] = 'Europe'
amu_prices['n_countries'] = 31
amu_prices['year'] = 2020

datainfo(amu_prices)

# =============================================================================
#### Extended price data
# =============================================================================
amu_prices_ext = pd.read_excel(
    os.path.join(RAWDATA_FOLDER ,'AMU_ euros per ton extended.xlsx')
	,skiprows=2                 # List: row numbers to skip. Integer: count of rows to skip at start of file
    ,nrows=5                    # Total number of rows to read
)
cleancolnames(amu_prices_ext)

datainfo(amu_prices_ext)

#%% Import WOAH regions and countries

woah_regions = pd.read_csv(os.path.join(GLBL_RAWDATA_FOLDER ,'WOAH regions and countries.csv'))
cleancolnames(woah_regions)
datainfo(woah_regions)

woah_regions['world_region'].unique()

#%% Import AMR data

amr = pd.read_csv(os.path.join(RAWDATA_FOLDER ,'SBM_JSA_AMR_livestock.csv'))

# Profile
# profile = amr.profile_report()
# profile.to_file(os.path.join(PRODATA_FOLDER ,'amr_profile.html'))

# =============================================================================
#### Add WOAH regions
# =============================================================================
amr['location_name'] = amr['location_name'].str.upper()
woah_regions['country'] = woah_regions['country'].str.upper()

# import difflib
# amr['country_fuzzy'] = amr['map_id'].apply(
#     lambda x: difflib.get_close_matches(x, woah_regions['country'] ,cutoff=0.2)[0]
# )
# check_countrymatch = amr[['map_id' ,'country_fuzzy']].value_counts()

# woah_regions['iso3_fuzzy'] = woah_regions['country'].apply(
#     lambda x: difflib.get_close_matches(x, amr['map_id'] ,cutoff=0.1)[0]
# )
# check_countrymatch = woah_regions[['country' ,'iso3_fuzzy']].value_counts()

datainfo(amr)

# Rename countries
rename_countries_woah = {
    "CHINA (PEOPLE'S REP. OF)":"CHINA"
    ,"KOREA (REP. OF)":"KOREA"
    }
woah_regions['country_tomatch'] = woah_regions['country'].replace(rename_countries_woah)

woah_add_countries = pd.DataFrame(
    {"country_tomatch":"GRENADA" ,"world_region":"Americas"}
    ,index=[0]
    )
woah_regions = pd.concat([woah_regions ,woah_add_countries])

rename_countries_amr = {
    "BOLIVIA (PLURINATIONAL STATE OF)":"BOLIVIA"
    ,"CZECHIA":"CZECH REPUBLIC"
    ,"IRAN (ISLAMIC REPUBLIC OF)":"IRAN"
    ,"LAO PEOPLE'S DEMOCRATIC REPUBLIC":"LAOS"
    ,"REPUBLIC OF KOREA":"KOREA"
    ,"UNITED REPUBLIC OF TANZANIA":"TANZANIA"
    ,"VENEZUELA (BOLIVARIAN REPUBLIC OF)":"VENEZUELA"
    ,"VIET NAM":"VIETNAM"
    }
amr['country_tomatch'] = amr['location_name'].replace(rename_countries_amr)

# Merge
amr_withrgn = pd.merge(
    left=amr
    ,right=woah_regions
    ,on='country_tomatch'
    ,how='left'
    ,indicator=True
)
print(amr_withrgn['_merge'].value_counts())

amr_withrgn.query("_merge == 'left_only'")['location_name'].unique()

amr_withrgn = amr_withrgn.drop(columns=['country_tomatch' ,'country' ,'_merge'])

# =============================================================================
#### Export
# =============================================================================
amr_withrgn.to_csv(os.path.join(PRODATA_FOLDER ,'amr.csv') ,index=False)

#%% Checks

# =============================================================================
#### Compare to prior biomass data
# =============================================================================
livestock_countries_biomass = pd.read_pickle(os.path.join(GLBL_PRODATA_FOLDER ,'livestock_countries_biomass.pkl.gz'))
biomass_live_weight_fao = pd.read_pickle(os.path.join(GLBL_PRODATA_FOLDER ,'biomass_live_weight_fao.pkl.gz'))

# Global biomass by species
global_biomass_prev = livestock_countries_biomass.groupby(['species' ,'year'])['biomass'].sum()
global_biomass_prev_upd = biomass_live_weight_fao.groupby(['species' ,'year'])['biomass'].sum()

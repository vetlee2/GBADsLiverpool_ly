#%% About
'''
Importing and exploring the antimicrobial data
'''
#%% Import WOAH 2018 report

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
amu2018_allspec[['region' ,'count']] = amu2018_allspec['unnamed:_0'].str.split('(' ,expand=True)
amu2018_allspec['region'] = amu2018_allspec['region'].str.rstrip()      # Drop trailing blanks

# Drop rows where region is missing - these are summary rows
amu2018_allspec = amu2018_allspec.dropna(subset='region')

# Drop columns
amu2018_allspec = amu2018_allspec.drop(columns=['unnamed:_0' ,'total_tonnes' ,'unnamed:_26' ,'count'])

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
    }
)

# Recalculate total
amu_cols = [i for i in amu2018_allspec if '_tonnes' in i]
amu2018_allspec['total_antimicrobials_tonnes'] = amu2018_allspec[amu_cols].sum(axis=1)

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
amu2018_ter[['region' ,'count']] = amu2018_ter['unnamed:_0'].str.split('(' ,expand=True)
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
amu2018_ter = amu2018_ter.rename(columns={
    'region_tonnes':'region'
    ,'number_of_countries_tonnes':'number_of_countries'
    }
)

# Recalculate total
amu_cols = [i for i in amu2018_ter if '_tonnes' in i]
amu2018_ter['total_antimicrobials_tonnes'] = amu2018_ter[amu_cols].sum(axis=1)

# Add Middle East by subtraction
amu2018_ter_t = amu2018_ter.transpose()     # Transpose regions to columns
colnames = list(amu2018_ter_t.iloc[0])      # Get names from desired row
amu2018_ter_t.columns = colnames			# Rename columns
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
amu2018_agp[['region' ,'count']] = amu2018_agp['unnamed:_0'].str.split('(' ,expand=True)
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
amu2018_agp = amu2018_agp.rename(columns={
    'region_tonnes':'region'
    ,'number_of_countries_tonnes':'number_of_countries'
    }
)

# Recalculate total
amu_cols = [i for i in amu2018_agp if '_tonnes' in i]
amu2018_agp['total_antimicrobials_tonnes'] = amu2018_agp[amu_cols].sum(axis=1)

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
amu2018_biomass_rgn_as['region'] = 'Asia, Far East and Oceania'
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

# Add total biomass column
amu2018_biomass['total'] = amu2018_biomass.sum(axis=1)  # Sum all numeric columns

# Add total bimoass for Terrestrial Food Producing animals
tfp_species = [
    'bovine'
    ,'swine'
    ,'poultry'
    ,'equine'
    ,'goats'
    ,'sheep'
    ,'rabbits'
    ,'camelids'
    ,'cervids'
]
amu2018_biomass['total_terr'] = amu2018_biomass[tfp_species].sum(axis=1)

# Add column prefix and suffix
amu2018_biomass = amu2018_biomass.add_prefix('biomass_')
amu2018_biomass = amu2018_biomass.add_suffix('_kg')
amu2018_biomass = amu2018_biomass.rename(columns={'biomass_region_kg':'region' ,'biomass_segment_kg':'segment'})

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

#%% Import antimicrobial importance categories

amu_importance = pd.read_excel(
    os.path.join(RAWDATA_FOLDER ,'Classification of AM per priority.xlsx')
	,skiprows=1
)
cleancolnames(amu_importance)

# Rename columns
amu_importance = amu_importance.rename(columns={"unnamed:_0":"antimicrobial_class"})

# Ensure all columns are string
amu_importance = amu_importance.astype('str')

# Combine categories into single column
def combine_importance(INPUT_ROW):
    # WHO categories
    if 'Y' in INPUT_ROW['who_critically_important_antimicrobials'].upper():
        who_ctg = 'A: Critically Important'
    elif 'Y' in INPUT_ROW['who_highly_important_antimicrobials'].upper():
        who_ctg = 'B: Highly Important'
    else:
        who_ctg = 'C: Other'

    # WOAH categories
    if 'Y' in INPUT_ROW['woah__critically_important'].upper():
        woah_ctg = 'A: Critically Important'
    elif 'Y' in INPUT_ROW['woah_highly_important'].upper():
        woah_ctg = 'B: Highly Important'
    else:
        woah_ctg = 'C: Other'

    # One Health categories
    if 'Y' in INPUT_ROW['one_health'].upper():
        onehealth_ctg = 'Important'
    else:
        onehealth_ctg = 'Other'

    return pd.Series([who_ctg ,woah_ctg ,onehealth_ctg])
amu_importance[['who_importance_ctg' ,'woah_importance_ctg' ,'onehealth_importance_ctg']] = amu_importance.apply(combine_importance ,axis=1)      # Apply to each row of the dataframe (axis=1)
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

#%% Import data from Mulchandani

amu_mulch = pd.read_csv(os.path.join(RAWDATA_FOLDER ,'UsebyCountry_Code_GBADs.csv'))
cleancolnames(amu_mulch)
del amu_mulch['unnamed:_0']
datainfo(amu_mulch)

# =============================================================================
#### Create regional sums
# =============================================================================
# -----------------------------------------------------------------------------
# Add WOAH regions
# -----------------------------------------------------------------------------
woah_regions_formulch = woah_regions.copy()
woah_regions_formulch = woah_regions_formulch.rename(columns={'world_region':'woah_region'})

woah_regions_formulch['country_tomatch'] = woah_regions_formulch['country'].str.upper()
amu_mulch['country_tomatch'] = amu_mulch['country'].str.upper()

# Rename countries to match
# Some minor countries and territories get renamed to their parent country - all I care about is the region
# Using FIJI as a catch-all for Oceania
# Using JAMAICA as a catch-all for Carribbean (Americas)
# Using VENEZUELA as a catch-all for South America (Americas)
# Using SOUTH AFRICA as a catch-all for Africa
rename_countries_mulch = {
    "CÔTE D'IVOIRE":"COTE D'IVOIRE"
    ,'CENTRAL AFRICAN REPUBLIC':"CENTRAL AFRICAN (REP.)"
    ,'CONGO':"CONGO (REP. OF THE)"
    ,'DEMOCRATIC REPUBLIC OF THE CONGO':"CONGO (DEM. REP. OF THE)"
    ,'RÉUNION':"REUNION"
    ,'SAINT HELENA, ASCENSION AND TRISTAN DA CUNHA':"SOUTH AFRICA"
    ,'SAO TOME AND PRINCIPE':"SOUTH AFRICA"
    ,'SEYCHELLES':"SOUTH AFRICA"
    ,'SUDAN (FORMER)':"SUDAN"
    ,'SWAZILAND':"SOUTH AFRICA"
    ,'UNITED REPUBLIC OF TANZANIA':"TANZANIA"
    ,'WESTERN SAHARA':"SOUTH AFRICA"
    ,'SOUTH SUDAN':"SUDAN"
    ,'BRUNEI DARUSSALAM':"FIJI"
    ,'CHINA, HONG KONG SAR':"CHINA (PEOPLE'S REP. OF)"
    ,'CHINA, MACAO SAR':"CHINA (PEOPLE'S REP. OF)"
    ,'CHINA, MAINLAND':"CHINA (PEOPLE'S REP. OF)"
    ,'CHINA, TAIWAN PROVINCE OF':"TAIPEI (CHINESE)"
    ,"DEMOCRATIC PEOPLE'S REPUBLIC OF KOREA":"KOREA (DEM PEOPLE'S REP. OF)"
    ,'IRAN (ISLAMIC REPUBLIC OF)':"IRAN"
    ,"LAO PEOPLE'S DEMOCRATIC REPUBLIC":"LAOS"
    ,'OCCUPIED PALESTINIAN TERRITORY':"PALESTINE"
    ,'REPUBLIC OF KOREA':"KOREA (REP. OF)"
    ,'SYRIAN ARAB REPUBLIC':"SYRIA"
    ,'TIMOR-LESTE':"TIMOR LESTE"
    ,'TURKEY':"TÜRKIYE"
    ,'VIET NAM':"VIETNAM"
    ,'CZECHIA':"CZECH REPUBLIC"
    ,'FAROE ISLANDS':"DENMARK"
    ,'GIBRALTAR':"UNITED KINGDOM"
    ,'HOLY SEE':"ITALY"
    ,'MONACO':"FRANCE"
    ,'REPUBLIC OF MOLDOVA':"MOLDOVA"
    ,'RUSSIAN FEDERATION':"RUSSIA"
    ,'THE FORMER YUGOSLAV REPUBLIC OF MACEDONIA':"CROATIA"
    ,'UNITED KINGDOM OF GREAT BRITAIN AND NORTHERN IRELAND':"UNITED KINGDOM"
    ,'BERMUDA':"JAMAICA"
    ,'GREENLAND':"DENMARK"
    ,'SAINT PIERRE AND MIQUELON':"FRANCE"
    ,'AMERICAN SAMOA':"UNITED STATES OF AMERICA"
    ,'COOK ISLANDS':"FIJI"
    ,'GUAM':"UNITED STATES OF AMERICA"
    ,'KIRIBATI':"FIJI"
    ,'MARSHALL ISLANDS':"FIJI"
    ,'MICRONESIA (FEDERATED STATES OF)':"MICRONESIA (FED. STATES OF)"
    ,'NAURU':"FIJI"
    ,'NIUE':"FIJI"
    ,'NORTHERN MARIANA ISLANDS':"FIJI"
    ,'PALAU':"FIJI"
    ,'SAMOA':"FIJI"
    ,'SOLOMON ISLANDS':"FIJI"
    ,'TOKELAU':"FIJI"
    ,'TONGA':"FIJI"
    ,'TUVALU':"FIJI"
    ,'WALLIS AND FUTUNA ISLANDS':"FIJI"
    ,'ANGUILLA':"JAMAICA"
    ,'ANTIGUA AND BARBUDA':"JAMAICA"
    ,'ARUBA':"JAMAICA"
    ,'BAHAMAS':"JAMAICA"
    ,'BOLIVIA (PLURINATIONAL STATE OF)':"BOLIVIA"
    ,'BRITISH VIRGIN ISLANDS':"JAMAICA"
    ,'DOMINICA':"DOMINICAN (REP.)"
    ,'DOMINICAN REPUBLIC':"DOMINICAN (REP.)"
    ,'FALKLAND ISLANDS (MALVINAS)':"VENEZUELA"
    ,'GRENADA':"JAMAICA"
    ,'GUADELOUPE':"JAMAICA"
    ,'MONTSERRAT':"JAMAICA"
    ,'NETHERLANDS ANTILLES':"JAMAICA"
    ,'PUERTO RICO':"UNITED STATES OF AMERICA"
    ,'SAINT KITTS AND NEVIS':"JAMAICA"
    ,'SAINT LUCIA':"JAMAICA"
    ,'SAINT VINCENT AND THE GRENADINES':"JAMAICA"
    ,'SURINAME':"VENEZUELA"
    ,'TURKS AND CAICOS ISLANDS':"JAMAICA"
    ,'UNITED STATES VIRGIN ISLANDS':"UNITED STATES OF AMERICA"
    ,'VENEZUELA (BOLIVARIAN REPUBLIC OF)':"VENEZUELA"
}
amu_mulch['country_tomatch'] = amu_mulch['country_tomatch'].replace(rename_countries_mulch)

# Merge
amu_mulch_withrgn = pd.merge(
    left=amu_mulch
    ,right=woah_regions_formulch
    ,on='country_tomatch'
    ,how='left'
    ,indicator=True
)
print(amu_mulch_withrgn['_merge'].value_counts())
amu_mulch_withrgn = amu_mulch_withrgn.drop(columns=['country_tomatch' ,'_merge'])
datainfo(amu_mulch_withrgn)

# -----------------------------------------------------------------------------
# Sum to region level
# -----------------------------------------------------------------------------
amu_mulch_regional = amu_mulch_withrgn.pivot_table(
    index='woah_region'
	,values=['tonnes2020' ,'tonnes2030' ,'pcu__kg__2020' ,'pcu__kg__2030']
	,aggfunc='sum'
)

# Recalculate usage per PCU
amu_mulch_regional['mgpcu_2020'] = amu_mulch_regional['tonnes2020'] * 1e9 / amu_mulch_regional['pcu__kg__2020']
amu_mulch_regional['mgpcu_2030'] = amu_mulch_regional['tonnes2030'] * 1e9 / amu_mulch_regional['pcu__kg__2030']
datainfo(amu_mulch_regional)

#%% Import AMR data

amr = pd.read_csv(os.path.join(RAWDATA_FOLDER ,'SBM_JSA_AMR_livestock.csv'))

# Profile
# profile = amr.profile_report()
# profile.to_file(os.path.join(PRODATA_FOLDER ,'amr_profile.html'))

# =============================================================================
#### Add WOAH regions
# =============================================================================
woah_regions_foramr = woah_regions.copy()

amr['location_name'] = amr['location_name'].str.upper()
woah_regions_foramr['country'] = woah_regions_foramr['country'].str.upper()

# import difflib
# amr['country_fuzzy'] = amr['map_id'].apply(
#     lambda x: difflib.get_close_matches(x, woah_regions_foramr['country'] ,cutoff=0.2)[0]
# )
# check_countrymatch = amr[['map_id' ,'country_fuzzy']].value_counts()

# woah_regions_foramr['iso3_fuzzy'] = woah_regions_foramr['country'].apply(
#     lambda x: difflib.get_close_matches(x, amr['map_id'] ,cutoff=0.1)[0]
# )
# check_countrymatch = woah_regions_foramr[['country' ,'iso3_fuzzy']].value_counts()

datainfo(amr)

# Rename countries
rename_countries_woah = {
    "CHINA (PEOPLE'S REP. OF)":"CHINA"
    ,"KOREA (REP. OF)":"KOREA"
    }
woah_regions_foramr['country_tomatch'] = woah_regions_foramr['country'].replace(rename_countries_woah)

woah_add_countries = pd.DataFrame(
    {"country_tomatch":"GRENADA" ,"world_region":"Americas"}
    ,index=[0]
    )
woah_regions_foramr = pd.concat([woah_regions_foramr ,woah_add_countries])

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
    ,right=woah_regions_foramr
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

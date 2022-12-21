#%% About
'''
Importing and exploring the initial antimicrobial usage data
'''
#%% Import

# =============================================================================
#### All antimicrobial usage
# =============================================================================
amu2018_all = pd.read_excel(
	os.path.join(RAWDATA_FOLDER ,'AMU_2018_6th report_GBADs.xlsx')
	,sheet_name='Antimicrobial Quantities (AQ)'
	,skiprows=7                 # List: row numbers to skip. Integer: count of rows to skip at start of file
    ,nrows=10                    # Total number of rows to read
)
cleancolnames(amu2018_all)
amu2018_all.columns = amu2018_all.columns.str.strip('_')    # Remove trailing underscores

# Clean up region names
amu2018_all[['region' ,'count']] = amu2018_all['unnamed:_0'].str.split('(' ,expand=True)    # Splitting at hyphen (-). expand=True to return multiple columns.
amu2018_all['region'] = amu2018_all['region'].str.rstrip()      # Drop trailing blanks

# Drop rows where region is missing - these are summary rows
amu2018_all = amu2018_all.dropna(subset='region')

# Drop columns
amu2018_all = amu2018_all.drop(columns=['unnamed:_0' ,'total_tonnes' ,'unnamed:_26' ,'count'])

# Reorder columns and sort
cols_first = ['region' ,'number_of_countries']
cols_other = [i for i in list(amu2018_all) if i not in cols_first]
amu2018_all = amu2018_all.reindex(columns=cols_first + cols_other)
amu2018_all = amu2018_all.sort_values(by=cols_first ,ignore_index=True)

# Add column suffixes
amu2018_all = amu2018_all.add_suffix('_tonnes')
amu2018_all = amu2018_all.rename(columns={'region_tonnes':'region' ,'number_of_countries_tonnes':'number_of_countries'})

datainfo(amu2018_all)

# =============================================================================
#### Terrestrial antimicrobial usage
# =============================================================================
amu2018_ter = pd.read_excel(
	os.path.join(RAWDATA_FOLDER ,'AMU_2018_6th report_GBADs.xlsx')
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

# TODO: Add Middle East row

datainfo(amu2018_ter)

# =============================================================================
#### Growth promotants
# =============================================================================
amu2018_agp = pd.read_excel(
	os.path.join(RAWDATA_FOLDER ,'AMU_2018_6th report_GBADs.xlsx')
	,sheet_name='AQ-AGPs'
	,skiprows=2                 # List: row numbers to skip. Integer: count of rows to skip at start of file
    ,nrows=5                    # Total number of rows to read
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

datainfo(amu2018_agp)

# =============================================================================
#### Stack and export antimicrobial usage
# =============================================================================
# Add indicator of scope
amu2018_all['scope'] = 'All'
amu2018_ter['scope'] = 'Terrestrial Food Producing'
amu2018_agp['scope'] = 'AGP'

amu2018 = pd.concat(
    [amu2018_all
    ,amu2018_ter
    ,amu2018_agp
    ]
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

# Export
amu2018.to_csv(os.path.join(PRODATA_FOLDER ,'amu2018.csv') ,index=False)

# =============================================================================
#### Species
# =============================================================================
# -----------------------------------------------------------------------------
# Detailed species
# -----------------------------------------------------------------------------
amu2018_species_dtl = pd.read_excel(
	os.path.join(RAWDATA_FOLDER ,'AMU_2018_6th report_GBADs.xlsx')
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
	os.path.join(RAWDATA_FOLDER ,'AMU_2018_6th report_GBADs.xlsx')
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
	os.path.join(RAWDATA_FOLDER ,'AMU_2018_6th report_GBADs.xlsx')
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
	os.path.join(RAWDATA_FOLDER ,'AMU_2018_6th report_GBADs.xlsx')
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
	os.path.join(RAWDATA_FOLDER ,'AMU_2018_6th report_GBADs.xlsx')
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
	os.path.join(RAWDATA_FOLDER ,'AMU_2018_6th report_GBADs.xlsx')
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
	os.path.join(RAWDATA_FOLDER ,'AMU_2018_6th report_GBADs.xlsx')
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
	os.path.join(RAWDATA_FOLDER ,'AMU_2018_6th report_GBADs.xlsx')
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

amu2018_biomass_all = pd.concat(
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

# Reorder columns and sort
cols_first = ['region' ,'segment']
cols_other = [i for i in list(amu2018_biomass_all) if i not in cols_first]
amu2018_biomass_all = amu2018_biomass_all.reindex(columns=cols_first + cols_other)
amu2018_biomass_all = amu2018_biomass_all.sort_values(by=cols_first ,ignore_index=True)

datainfo(amu2018_biomass_all)

# Export
amu2018_biomass_all.to_csv(os.path.join(PRODATA_FOLDER ,'amu2018_biomass.csv') ,index=False)

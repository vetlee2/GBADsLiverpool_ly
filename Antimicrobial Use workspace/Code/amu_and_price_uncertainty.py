#%% About
'''
Experimenting with uncertainty around AM Usage and price
'''
#%% Functions

# Translate a PERT distribution to the equivalent Beta
# Output a dataframe with samples generated from the distribution and a histogram
def generate_pert(MIN ,MODE ,MAX ,LAMBDA=4):
    funcname = inspect.currentframe().f_code.co_name

    mean = (MIN + (LAMBDA * MODE) + MAX) / (LAMBDA + 2)
    alpha = (mean - MIN) * (2*MODE - MIN - MAX) / ((MODE - mean) * (MAX - MIN))
    beta = alpha * (MAX - mean) / (mean - MIN)

    print(f"<{funcname}> PERT distribution: ({MIN}, {MODE}, {MAX}) with lambda={LAMBDA}")
    print(f"<{funcname}> Equivalent Beta distribution: {alpha=:.3f}, {beta=:.3f}")

    # Generate samples
    beta_distr = sps.beta(alpha ,beta)
    generated_df = pd.DataFrame(index=range(10000))
    generated_df['rand_beta'] = beta_distr.rvs(size=generated_df.shape[0])      # Generate random numbers from Beta distribution (on scale 0,1)
    generated_df['rand_pert'] = (generated_df['rand_beta'] * (MAX - MIN)) + MIN   # Translate from (0,1) to scale of PERT

    # Plot
    snplt = sns.displot(
    	data=generated_df
    	,x='rand_pert'
    	,kind='hist'
        ,stat='probability'
        ,bins=20
    )
    plt.title(f"PERT({MIN}, {MODE}, {MAX}) with lambda={LAMBDA}\n Recreated as Beta({alpha:.2f}, {beta:.2f})\n 10k samples")

    return generated_df

pert_samples = generate_pert(1, 8, 10)
pert_samples = generate_pert(18753, 29000, 31900)

# Translate a PERT distribution to the equivalent Beta
# Output the beta distribution object for further processing
def pert_to_beta(MIN ,MODE ,MAX ,LAMBDA=4):
    funcname = inspect.currentframe().f_code.co_name

    mean = (MIN + (LAMBDA * MODE) + MAX) / (LAMBDA + 2)
    alpha = (mean - MIN) * (2*MODE - MIN - MAX) / ((MODE - mean) * (MAX - MIN))
    beta = alpha * (MAX - mean) / (mean - MIN)
    beta_distr = sps.beta(alpha ,beta)

    print(f"<{funcname}> PERT distribution: ({MIN}, {MODE}, {MAX}) with lambda={LAMBDA}")
    print(f"<{funcname}> Equivalent Beta distribution: {alpha=:.3f}, {beta=:.3f}")

    return beta_distr

beta_distr = pert_to_beta(1, 8, 10)

# Endpoints of the range that contains alpha percent of the distribution
beta_distr_ci95 = beta_distr.interval(0.95)
pert_distr_ci95_low = (beta_distr_ci95[0] * (10 - 1)) + 1   # Translate from (0,1) to scale of PERT
pert_distr_ci95_high = (beta_distr_ci95[1] * (10 - 1)) + 1   # Translate from (0,1) to scale of PERT

#%% Do it

# =============================================================================
#### Create data based on spreadsheet from Sara
# =============================================================================
amu_uncertainty_data = pd.DataFrame(
    {"region":['Africa' ,'Americas' ,'Asia, Far East and Oceania' ,'Europe' ,'Middle East']
     ,"n_countries":[24 ,19 ,22 ,41 ,3]

     ,"amu_terrestrial_tonnes_min":[1403 ,18753 ,33387 ,7314 ,34]
     ,"amu_terrestrial_tonnes_mostlikely":[2806 ,29000 ,50080 ,7680 ,198]
     ,"amu_terrestrial_tonnes_max":[3086 ,31900 ,55088 ,8045 ,218]
     ,"amu_terrestrial_tonnes_distr":['Pert' ,'Pert' ,'Pert' ,'Uniform' ,'Pert']

     ,"amu_terrestrial_eurospertonne_min":[20476 ,20476 ,20476 ,145075 ,20476]
     ,"amu_terrestrial_eurospertonne_mostlikely":[176992 ,np.nan ,108806 ,np.nan ,108806]
     ,"amu_terrestrial_eurospertonne_max":[206007 ,145075 ,123314 ,np.nan ,123314]
     ,"amu_terrestrial_eurospertonne_distr":['Modified pert; Ƴ=2.5' ,'Uniform' ,'Modified pert; Ƴ=2.5' ,'' ,'Modified pert; Ƴ=2.5']
     }
)

# Merge in biomass data
amu_uncertainty_data = pd.merge(
    left=amu_uncertainty_data
    ,right=amu2018_biomass.query("segment == 'Total Region'")[['region' ,'biomass_total_terr_kg']]
    ,on='region'
    ,how='left'
)

# =============================================================================
#### Add confidence intervals for usage
# =============================================================================
def add_ci(INPUT_ROW):
    if INPUT_ROW['amu_terrestrial_tonnes_distr'].upper() == 'PERT':
        beta_distr = pert_to_beta(
            INPUT_ROW['amu_terrestrial_tonnes_min']
            ,INPUT_ROW['amu_terrestrial_tonnes_mostlikely']
            ,INPUT_ROW['amu_terrestrial_tonnes_max']
        )
        beta_distr_ci95 = beta_distr.interval(0.95)
        ci95_low = (beta_distr_ci95[0] * (INPUT_ROW['amu_terrestrial_tonnes_max'] - INPUT_ROW['amu_terrestrial_tonnes_min'])) + INPUT_ROW['amu_terrestrial_tonnes_min']   # Translate from (0,1) to scale of PERT
        ci95_high = (beta_distr_ci95[1] * (INPUT_ROW['amu_terrestrial_tonnes_max'] - INPUT_ROW['amu_terrestrial_tonnes_min'])) + INPUT_ROW['amu_terrestrial_tonnes_min']   # Translate from (0,1) to scale of PERT
    elif INPUT_ROW['amu_terrestrial_tonnes_distr'].upper() == 'UNIFORM':
        ci95_low = 0.025*(INPUT_ROW['amu_terrestrial_tonnes_max'] - INPUT_ROW['amu_terrestrial_tonnes_min']) + INPUT_ROW['amu_terrestrial_tonnes_min']
        ci95_high = 0.975*(INPUT_ROW['amu_terrestrial_tonnes_max'] - INPUT_ROW['amu_terrestrial_tonnes_min']) + INPUT_ROW['amu_terrestrial_tonnes_min']
    else:
        ci95_low = None
        ci95_high = None
    return pd.Series([ci95_low ,ci95_high])

amu_uncertainty_data[['ci95_low' ,'ci95_high']] = amu_uncertainty_data.apply(add_ci ,axis=1)

#??? Should intervals be centered on the MOST LIKELY value or the MEAN?
amu_uncertainty_data = amu_uncertainty_data.eval(
    '''
    amu_terrestrial_tonnes_errorlow = amu_terrestrial_tonnes_mostlikely - ci95_low
    amu_terrestrial_tonnes_errorhigh = ci95_high - amu_terrestrial_tonnes_mostlikely
    '''
)

# =============================================================================
#### Add confidence intervals for total expenditure
# =============================================================================
# For each region, resample from Usage and Price distributions, multiplying them to get expenditure
resampled_usage_americas = generate_pert(18753, 29000, 31900)
resampled_price_americas = pd.DataFrame(index=range(10000))
resampled_price_americas['rand_uniform'] = sps.uniform.rvs(loc=20476 ,scale=145075 ,size=resampled_price_americas.shape[0])

# =============================================================================
#### Export
# =============================================================================
amu_uncertainty_data.to_csv(os.path.join(DASH_DATA_FOLDER, "amu_uncertainty_data.csv"))

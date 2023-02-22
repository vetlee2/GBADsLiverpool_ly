#%% About
'''
Experimenting with uncertainty around AM Usage and price
'''
#%% Do it

import plotly.io as pio
pio.renderers.default='browser'

data = pd.DataFrame(
    {"region":['Africa' ,'Americas' ,'Asia, Far East and Oceania' ,'Europe' ,'Middle East']
     ,"n_countries":[24 ,19 ,22 ,41 ,3]

     ,"amu_terrestrial_tonnes_min":[1403 ,18753 ,33387 ,7314 ,34]
     ,"amu_terrestrial_tonnes_mostlikely":[2806 ,29000 ,50080 ,np.nan ,198]
     ,"amu_terrestrial_tonnes_max":[3086 ,31900 ,55088 ,8045 ,218]
     ,"amu_terrestrial_tonnes_distr":['Pert' ,'Pert' ,'Pert' ,'Uniform' ,'Pert']

     ,"amu_terrestrial_eurospertonne_min":[20476 ,20476 ,20476 ,145075 ,20476]
     ,"amu_terrestrial_eurospertonne_mostlikely":[176992 ,np.nan ,108806 ,np.nan ,108806]
     ,"amu_terrestrial_eurospertonne_max":[206007 ,145075 ,123314 ,np.nan ,123314]
     ,"amu_terrestrial_eurospertonne_distr":['Modified pert; Ƴ=2.5' ,'Uniform' ,'Modified pert; Ƴ=2.5' ,'' ,'Modified pert; Ƴ=2.5']
     }
)

# fig = px.bar(
#     data
#     ,x="region"
#     ,y="amu_terrestrial_tonnes_mostlikely"
#     ,error_y="amu_terrestrial_tonnes_max", error_y_minus="amu_terrestrial_tonnes_min"
# )
# fig.show()

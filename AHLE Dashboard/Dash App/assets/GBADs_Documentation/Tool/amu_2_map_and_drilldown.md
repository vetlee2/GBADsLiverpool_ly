# Visualization of Antimicrobial Usage, Resistance and Expenditure in Livestock by Region
<p>
This section shows either a drill down (hierarchical treemap) or a world map. Further options for the chart will appear depending on the chart type and the selection made in the first dropdown box.
</p>

```{figure} ../Images/amu_drilldown_1.png
---
#height: 700px
name: amu_drilldown_1
---
Hierarchical treemap
```

```{figure} ../Images/amu_map_1.png
---
#height: 700px
name: amu_map_1
---
World map
```

<h3>Drill Down</h3>
<p>
The hierarchical treemap displays antimicrobial usage by region and importance category. You can click on any box in this interactive visual to see usage for the individual antimicrobial classes represented in each importance category. There are 2 dropdown boxes to customize the display.
</p>
<p><b>Drill Down Display</b><br />
Select <i>Antimicrobial Usage: tonnes</i> to display usage in tonnes of each antimicrobial group. Select <i>Antimicrobial Usage: mg per kg biomass</i> to display usage in mg per kg biomass, defined for each antimicrobial group and region as (tonnes of antimicrobial) x 1e9 / (kg total biomass for countries reporting in the region).
</p>
<p><b>Importance Categories</b><br />
Determines which importance category definitions are used to group antimicrobial classes within regions. Options are:
<br /><br />
<i>WHO Importance Categories:</i> Groups antimicrobial classes according to the <a href='https://apps.who.int/iris/bitstream/handle/10665/312266/9789241515528-eng.pdf'>World Health Organization's definitions</a> of importance for human health.
<br /><br />
<i>WOAH Importance Categories:</i> Groups antimicrobial classes according to the <a href='https://www.woah.org/app/uploads/2021/06/a-oie-list-antimicrobials-june2021.pdf'>World Organization for Animal Health definitions</a> of importance.
<br /><br />
<i>OneHealth Importance Categories:</i> Groups antimicrobial classes according to the <a href='https://ssrn.com/abstract=4346767'>Venkateswaran et al., 2023 definitions</a> of importance.
</p>

<h3>Map</h3>
<p>
The map can display several different metrics. Options are:
</p>
<b>Antimicrobial Usage</b><br />
Displays a dot for each region sized by total antimicrobial usage. Select either <i>Antimicrobial Usage: tonnes</i> or <i>Antimicrobial Usage: mg per kg biomass</i> to display this as total tonnes or mg per kg biomass.

<b>Biomass</b><br />
Displays a dot for each region sized by total biomass (kg) for countries reporting to WOAH.

<b>Antimicrobial Resistance (country level)</b><br />
Displays country-level antimicrobial resistance from <a href='https://ssrn.com/abstract=4346767'>Venkateswaran et al., 2023</a>. Selecting this option will cause 2 other dropdown boxes to appear: <b>Antimicrobial Class</b> and <b>Pathogen</b>. A dot will appear for each country in the data, sized by the percent of isolates of the selected pathogen that were resistant to the selected antimicrobial class. If a pathogen/antimicrobial class combination is selected for which there is no data, a notification will be displayed.

<b>Drug Resistance Index (region level)</b><br />
Displays the drug resistance index for each region, calculated as follows: for each region, we calculate the average resistance rate of an indicator pathogen (E. coli) across all antimicrobials tested (<a href='https://ssrn.com/abstract=4346767'>Venkateswaran et al., 2023</a>), weighted by the proportion of region-total antimicrobial use that each antimicrobial accounts for in <a href='https://www.woah.org/app/uploads/2022/06/a-sixth-annual-report-amu-final.pdf'>WOAH 2018</a>. This is based on the drug resistance index specified in <a href='https://bmjopen.bmj.com/content/1/2/e000135'>Laxminarayan 2011</a>, except that we use proportion of region-total antimicrobial use in place of a direct measure of the frequency of use of each antimicrobial. We use E. coli as the indicator pathogen consistent with the rationale in <a href='https://www.efsa.europa.eu/en/efsajournal/pub/5017'>EFSA AMR Indicators 2017</a>.

<b>Antimicrobial expenditure</b><br />
Displays the antimicrobial expenditure in each region, calculated using the antimicrobial usage and price values selected in the <i>Regional Veterinary Antimicrobial Expenditure Estimator</i> section. By default, this will use the middle values of usage and price for each region, and will update as the user changes those inputs.
</p>

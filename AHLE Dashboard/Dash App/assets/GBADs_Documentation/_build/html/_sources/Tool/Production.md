# Production

The production chart shows a 5-step waterfall starting with potential production on the left and ending with realised production on the right.

The units displayed are determined by the <i>Metric</i> selector. If <i>Metric</i> is "Tonnes", the chart displays tonnes of carcass weight. If <i>Metric</i> is "US Dollars", the chart displays dollar values by applying the price specified by the <i>Producer price</i> slider. If <i>Metric</i> is "Percent of GDP", the chart displays dollar values as a percentage of GDP for the selected country and year.

<b>Breed Standard Potential</b><br />
The total that would be produced if all the animals placed survived and reached the breed standard weight for the specified days on feed. The breed is determined by the country selected. Days on feed are determined by the <i>Days on feed</i> slider.

<b>Effect of Feed & Practices</b><br />
An adjustment to the breed standard potential based on the feed and practices available in a country. This captures the expected loss or boost to growth due to the quality of feed, housing,  climate, and other regional factors that are not due to disease. This is determined by the <i>Achievable % of breed standard</i> slider.

<b>Mortality & Condemns</b><br />
The total lost production due to the death of animals. Calculated as the difference between head placed and head slaughtered multiplied by the average carcass weight for the selected country and year.

<b>Morbidity</b><br />
The total lost production due to animals failing to reach their potential weight. Calculated as the remainder required to reach the realised production after accounting for the breed standard potential, the effect of feed and practices, and the mortality.

<b>Realised Production</b><br />
The total actual production for the selected country and year.

```{figure} ../Images/poultry_production_1.png
---
#height: 700px
name: poultry_production_1
---
Example production chart
```

# Production chart
<p>
The production chart shows a 5-step waterfall with potential production on the left and realised production on the right, with the middle bars representing the effects of feed and practices and the losses due to the burden of disease.
</p>

```{figure} ../Images/poultry_production_1.png
---
#height: 700px
name: poultry_production_1
---
Example production chart
```

<p>
The units displayed are determined by the <i>Metric</i> selector in the top row of controls. Options are:
<ul>
	<li>Tonnes: metric tonnes of carcass weight</li>
	<li>US Dollars: value of carcass weight in US dollars according to the carcass price set by the <i>Producer price</i> slider</li>
	<li>Percent of GDP: value of carcass weight as percent of GDP for the selected country and year</li>
	<li>Percent of Breed Standard: carcass weight as percent of the breed standard potential</li>
	<li>Percent of Realized Production: carcass weight as percent of the realised production</li>
</ul>
</p>
<p><b>Breed Standard Potential</b><br />
The total that would be produced if all the animals placed survived and reached the breed standard weight for the specified days on feed. The breed is determined by the country selected. Days on feed are determined by the <i>Days on feed</i> slider.
</p>
<p><b>Effect of Feed & Practices</b><br />
An adjustment to the breed standard potential based on the feed and practices available in a country. This captures the expected loss or increased growth due to the quality of feed, housing, climate, and other regional factors that are not due to disease. This is determined by the <i>Achievable % of breed standard</i> slider.
</p>
<p><b>Mortality & Condemns</b><br />
The total lost production due to the death of animals. Calculated as the difference between head placed and head slaughtered multiplied by the average carcass weight for the selected country and year.
</p>
<p><b>Morbidity</b><br />
The total lost production due to animals failing to reach their potential weight. Calculated as the remainder required to reach the realised production after accounting for the breed standard potential, the effect of feed and practices, and the mortality.
</p>
<p><b>Realised Production</b><br />
The total actual production for the selected country and year.
</p>

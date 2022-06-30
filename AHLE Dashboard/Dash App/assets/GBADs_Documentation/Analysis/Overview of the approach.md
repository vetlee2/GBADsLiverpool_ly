# Overview of the approach
<p>
The burden of disease on animal production is represented in the conceptual flow below.
</p>

```{figure} ../Images/sankey_basic_1.png
---
#height: 700px
name: fig_sankey_basic_1
---
Conceptual flow of production losses
```

<p>
We endeavor to estimate each component of this flow in terms of carcass weight. Some components are known based on readily-available data. The others are estimated as described here. For the estimates that rely on assumptions, we provide controls in the dashboard to adjust those assumptions.
</p>

<p><b>Ideal production</b><br />
Estimated based on a breed standard weight at an assumed growout time. We use the breed standard for the most common breed in each country and the average growout time based on data to estimate the ideal weight per animal. We then multiply by the number of head placed to estimate the ideal total production.
</p>
<p><b>Achievable without disease</b><br />
The proportion of ideal production that is considered to be achievable without disease, given the quality of feed, housing, climate and other non-disease factors. A dashboard control allows adjustment of this as a percentage of the breed standard potential.
</p>
<p><b>Realized production</b><br />
The actual production of total carcass weight. Readily-available data for most species and countries.
</p>
<p><b>Burden of disease</b><br />
We consider the burden of disease in the broadest sense, including losses due to infectious, non-infectious, and external causes (such as predation). This is split into 3 categories: Condemns, Mortality & Culls, and Reduced Growth.
</p>
<p><b>Condemns</b><br />
The burden of disease in terms of condemned animals. Data is available for some countries. Currently, we make the simplifying assumption that all condemns happen before slaughter, and they are included with Mortality & Culls as all-cause mortality.
</p>
<p><b>Mortality & Culls</b><br />
The burden of disease in terms of dead animals. We calculate this as the difference between head placed and head slaughtered, multiplied by the average weight of the animals that were slaughtered to estimate the total lost carcass weight due to mortality.
</p>
<p><b>Reduced growth</b><br />
The burden of disease in terms of animals that failed to reach their full potential weight. Estimated as the remainder after accounting for all other components.
</p>
<p><b>Suboptimal feed & practices</b><br />
Accounts for any shortfall in animal weight due to poor quality feed, housing, climate or other non-disease factors. Default value is zero but can be adjusted in the dashboard.
</p>

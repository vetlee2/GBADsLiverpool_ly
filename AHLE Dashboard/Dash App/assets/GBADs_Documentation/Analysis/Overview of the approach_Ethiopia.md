# Overview of the approach
<p>
The Animal Health Loss Envelope (AHLE), which represents the farm level overall disease burden, is the difference in income from livestock populations under the current state of health and under an idealized perfect health situation where there are no health or nutritional problems (such as disease, predation, acute feed shortage or micronutrient deficiency). 

The flow of inputs and outputs under the current state of health and the ideal is represented in the conceptual flow below.
</p>

```{figure} ../Images/ECS_Sanky_diagram_from_Gemma.png
---
name: fig_sankey_ethiopia_1
---
Conceptual flow of inputs, outputs, and production losses
```
<p>
The AHLE for Ethiopia was calculated using gross margin as a measure of income, which was simulated using a herd dynamics model. This herd dynamics model is a compartmental model in which the herd (livestock population) are divided by sex and age classes. Each sex class (male and female) is classified into three age groups (neonate, juvenile and adult) resulting in six sex-age groups. The model simulates the herd dynamics based on demographic (birth and death rates) and offtake rates in a monthly time step for one year. The simulation of the model produces annual production offtakes (live animal, milk, draft power, hides, manure etc.) and their respective monetary values (revenue) based on prices for these production outputs. It also estimates the change in total expenditure on production inputs: feed, labor and animal health care. The revenue and costs from the herd model enable the calculation of gross margins for the simulated populations. The gross margin is calculated for different scenarios formed by combination of sex-age groups, production systems and incremental improvement in health statuses.
</p>
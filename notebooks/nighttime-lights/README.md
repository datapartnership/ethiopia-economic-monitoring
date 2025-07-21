# Nighttime Lights Trends

In a world marked by diverse forms of conflict, from armed confrontations to civil unrest, [NASA's Black Marble Nighttime Lights](https://blackmarble.gsfc.nasa.gov) dataset offers an unconventional yet powerful tool for understanding the ripple effects of these conflicts on human settlements and infrastructure. By tracking nighttime light variations and disruptions, we can unearth insights into population displacement, economic destabilization, and the societal impacts of conflict. This analysis explores the potential of a nighttime lights dataset to not only detect areas affected by conflict but also to quantify the extent of its influence on livelihoods and on the economy, providing a valuable perspective on the multifaceted consequences of conflict.

## Data 

This analysis used Nighttime Lights data from NASA BlackMarble and shapefiles from GADM (which is slightly different from the shapefiles used in the analysis for Air Pollution). In the next version of the analysis, the shapefiles will be changed so the analysis can become more comparable. 

### NASA Black Marble 

[NASA's Black Marble](https://blackmarble.gsfc.nasa.gov) product suite represents a remarkable advancement in our ability to monitor and understand nocturnal light emissions on a global scale. By utilizing cutting-edge satellite technology and image processing techniques, the Black Marble VIIRS dataset offers a comprehensive and high-resolution view of the Earth's nighttime illumination patterns. To obtain the raster data conveniently and calculate zonal statistics, we use the [BlackMarblePy](https://worldbank.github.io/blackmarblepy/README.html) {cite}`10.5281/zenodo.10667925` package developed by the World Bank.

```{important}
The [VNP46A2 Daily Moonlight-adjusted Nighttime Lights (NTL) Product](https://blackmarble.gsfc.nasa.gov/VNP46A2.html) is [available daily](datahttps://ladsweb.modaps.eosdis.nasa.gov/missions-and-measurements/products/VNP46A2/#data-availability). However, due data quality, cloud cover or other factors, the data may not be available always at a specific location.
```

(nighttime-lights-limitations)=

## Limitations

Using nighttime lights to estimate macroeconomic indicators during conflict may be a valuable approach, but it comes with several assumptions and limitations. Here's a list of some of the key assumptions and limitations:

```{caution}
**Assumptions:**

- **Luminosity Reflects Economic Activity:** The approach assumes that the level of nighttime lights is a reliable proxy for economic activity. It presupposes that areas with brighter lights correspond to higher economic productivity.

- **Baseline Data Availability:** It assumes the availability of baseline nighttime lights data before the onset of the conflict. The accuracy of the estimates depends on the quality and relevance of this baseline data.

- **Spatial Distribution:** The method assumes that nighttime lights are evenly distributed within a given geographic area and that changes in luminosity accurately reflect changes in economic activity across all locations.


**Limitations:**

- **Confounding Factors and Data Interpretation:** The approach may require subjective interpretation, as it may not distinguish between reduced lighting due to conflict and reduced lighting due to other factors. Changes in nighttime lights can be influenced by factors other than economic activity, such as energy conservation measures, urban development, or seasonal variations.

- **Generalization:** The approach might lead to overgeneralization, as a reduction in nighttime lights can be associated with various economic outcomes, from minor disruptions to severe economic downturns.

- **Alternative Explanations:** Changes in nighttime lights can result from factors other than conflict, such as urban development, changes in economic activities, or natural disasters. Therefore, it may not always be clear whether a decline in nighttime lights is solely due to conflict.

- **Geopolitical Factors:** The dataset may be subject to geopolitical biases, with some areas having less comprehensive coverage due to political reasons.

- **Data Lag:** There can be a significant time lag between the occurrence of a conflict event and its reflection in the nighttime lights dataset. This lag may limit the dataset's utility for real-time conflict monitoring.

- **Resolution and Urban Bias:** The dataset's spatial resolution may not be fine enough to capture small villages or isolated conflict events. It may also have an urban bias, making it less suitable for analyzing rural or remote conflicts.
```

To address these assumptions and limitations, it is crucial to complement nighttime lights data analysis with other sources of information and adopt a cautious and context-aware approach when interpreting the findings.

## References

{cite:empty}`ROMAN2018113`

```{bibliography}
:filter: docname in docnames
:style: plain
```
# Crop Productivity and EVI

The relationship between crop yields and the Enhanced Vegetation Index (EVI), a vegetation index derived from satellite imagery that is particularly effective in monitoring vegetation health and productivity, has been extensively studied. Johnson (2016) provides a comprehensive overview of the use of EVI in agricultural yield prediction, highlighting its advantages over other indices like the Normalized Difference Vegetation Index (NDVI). The study concluded that EVI was among the best overall performer in predicting crop yields, showing the highest correlation in five out of nine crops studied, excluding rice. Numerous studies have successfully utilized EVI to predict yields of various crops, including maize, soybeans, and rice. For instance, Bolton and Friedl (2013) created  a linear model using EVI to forecast soybean and maize yields in the Central United States. Their findings demonstrate that EVI exhibits a stronger correlation with maize yield and yield anomalies than other vegetation indices, and incorporating phenological data significantly enhances the model’s performance. A similar finding by Ji et al. (2022) showed that their model framework based on EVI and crop phenology can improve the accuracy of yield predictions of corn and soybean in the United States. Furthermore, Son et al. (2013) used MODIS EVI data for rice yield prediction in the Vietnamese Mekong Delta, reporting high correlation coefficients (R2 of 0.70 for spring-winter and 0.74 for autumn-summer in 2013, and 0.62-0.71 and 0.4-0.56 in 2014, respectively). 

## Satellite and Ground-Based Approaches

Compared to ground-based methods, such as field interviews and crop cuttings, Remote sensing approach has several advantages on estimating crop yields:

- Timeliness and Rapid Assessment: Remote sensing offers real-time or near real-time assessment of crop conditions and potential yields, which is crucial for situations like natural disasters or conflicts (Deininger et al. 2023; Doraiswamy et al. 2003).
- Extensive Spatial Coverage and Granularity: Satellite imagery can consistently cover large geographic areas, providing granular, field, and village-level data that can be aggregated to higher administrative levels, such as districts or provinces (Azzari, Jain, and Lobell 2017; Becker-Reshef et al. 2010).
- Cost-Effectiveness: Remote sensing is generally more cost-effective for collecting agricultural data over large areas compared to ground-based methods (Johnson 2016; Rahman et al. 2009).
- Accessibility in Difficult or Dangerous Areas: Remote sensing provides a reliable option for data collection in zones that are difficult, dangerous, or inaccessible for in-situ surveys, such as conflict areas (Jaafar et al. 2015).
However, remote sensing also has several limitations:
- Spatial Resolution Limitations: While modern sensors offer higher resolutions, coarse resolution data may not accurately reflect ground situations for small agricultural clusters, small parcels, or low-intensity agriculture (Kibret, Marohn, and Cadisch 2020).
- Significant Computational Demands: Analyzing high-resolution imagery requires massive amounts of computational power and storage, which can be expensive and time-consuming (Petersen 2018).
- Interpretability and Bias Concerns: Satellite-derived metrics may not fully capture all determinants of crop production and may not quantitatively interpret crop growth status (Wu et al. 2023)

While remote sensing offers timely, broad-scale, and cost-effective monitoring, particularly in data-scarce or inaccessible regions, it faces challenges with resolution limitations, computational demands, and potential biases in interpreting crop conditions.

## EVI and Other Vegetation Indices
Within the remote sensing approach itself, multiple vegetation indices have been utilized to enhance the accuracy of yield predictions. Compared to other vegetation indices, EVI offers several advantages over other vegetation indices:
- Reduced saturation: EVI does not saturate as quickly as NDVI at higher crop
leaf area or in areas with large amounts of biomass, providing improved sensitivity in dense vegetation conditions (Huete et al. 2002). This is crucial as high saturation in indicators like NDVI can lead to unreliable yield estimates (Son et al. 2013).
- Atmospheric and Soil Correction: EVI incorporates a soil adjustment factor and corrections for the red band due to aerosol scattering, making it more resistant to atmospheric influences and soil background noise compared to NDVI (Jurečka et al. 2018).

On the other hand, EVI also has some limitations compared to other vegetation indices:

- Temporal Resolution and Latency: While EVI is disseminated at 250m resolution, it may only be available at 16-day time steps, compared to NDVI’s 8-day availability, which could introduce latency issues for real-time monitoring (Johnson 2016)
- Mixed Pixel Problems: Coarse spatial resolution of MODIS EVI (250m or 500m) can limit performance in regions with small, fragmented parcels (Kibret, Marohn, and Cadisch 2020).

## Climate influenced on EVI

EVI values are influenced by several environmental factors. EVI is sensitive to rainfall patterns, as the variations of phenological stages of crops, such as the timing of planting and harvesting, are closely linked to rainfall (Kibret, Marohn, and Cadisch 2020). Additionally, while EVI is designed to be resistant to atmospheric aerosols, cloud contamination, particularly during wet seasons, can affect vegetation greenness signals and lower the accuracy of yield predictions (Son et al. 2013).

## Modelling Approaches of EVI

Several modeling approaches have been successfully employed with EVI data for crop yield prediction. Statistical models, particularly linear and quadratic regression, are widely used due to their fewer data requirements and assumptions compared to biophysical models (Ji et al. 2022). Linear regression models are frequently applied, with EVI generally performing well and showing more linear relationships with yields than NDVI for certain crops (Tiruneh et al. 2023). Machine learning approaches have also proven effective, with Kibret, Marohn, and Cadisch (2020) applied Random Forest algorithm to MODIS EVI time series for agricultural land use classification and cropping system identification. Pham et al. (2022) demonstrated that integrating Principal Component Analysis (PCA) with machine learning methods (PCA-ML) on VCI data effectively addresses spatial variability and redundant data issues, enhancing prediction accuracy by up to 45% in rice yield forecasting for Vietnam.

## References

- D. M. Johnson, “A comprehensive assessment of the correlations between field crop yields and commonly used MODIS products,” International Journal of Applied Earth Observation and Geoinformation, vol. 52, pp. 65–81, Oct. 2016, doi: 10.1016/j.jag.2016.05.010.
-  D. K. Bolton and M. A. Friedl, “Forecasting crop yield using remotely sensed vegetation indices and crop phenology metrics,” Agricultural and Forest Meteorology, vol. 173, pp. 74–84, May 2013, doi: 10.1016/j.agrformet.2013.01.007.
-  Z. Ji, Y. Pan, X. Zhu, D. Zhang, and J. Wang, “A generalized model to predict large-scale crop yields integrating satellite-based vegetation index time series and phenology metrics,” Ecological Indicators, vol. 137, p. 108759, Apr. 2022, doi: 10.1016/j.ecolind.2022.108759.
-  N. T. Son, C. F. Chen, C. R. Chen, L. Y. Chang, H. N. Duc, and L. D. Nguyen, “Prediction of rice crop yield using MODIS EVI−LAI data in the Mekong Delta, Vietnam,” International Journal of Remote Sensing, vol. 34, no. 20, pp.
7275–7292, Oct. 2013, doi: 10.1080/01431161.2013.818258.
-  P. C. Doraiswamy, S. Moulin, P. W. Cook, and A. Stern, “Crop Yield Assessment from Remote Sensing,” Photogrammetric Engineering & Remote Sensing, vol. 69, no. 6, pp. 665–674, Jun. 2003, doi: 10.14358/PERS.69.6.665.
-  K. Deininger, D. A. Ali, N. Kussul, A. Shelestov, G. Lemoine, and H. Yailimova, “Quantifying war-induced crop losses in Ukraine in near real time to strengthen local and global food security,” Food Policy, vol. 115, p. 102418, Feb. 2023, doi: 10.1016/j.foodpol.2023.102418.
-  I. Becker-Reshef, E. Vermote, M. Lindeman, and C. Justice, “A generalized regression-based model for forecasting winter wheat yields in Kansas and Ukraine using MODIS data,” Remote Sensing of Environment, vol. 114, no. 6, pp. 1312–1323, Jun. 2010, doi: 10.1016/j.rse.2010.01.010.
-  G. Azzari, M. Jain, and D. B. Lobell, “Towards fine resolution global maps of crop yields: Testing multiple methods and satellites in three countries,” Remote Sensing of Environment, vol. 202, pp. 129–141, Dec. 2017, doi: 10.1016/j.rse.2017.04.014.
-  A. Rahman, L. Roytman, N. Y. Krakauer, M. Nizamuddin, and M. Goldberg, “Use of Vegetation Health Data for Estimation of Aus Rice Yield in Bangladesh,” Sensors, vol. 9, no. 4, pp. 2968–2975, Apr. 2009, doi: 10.3390/s90402968.
-  H. H. Jaafar, R. Zurayk, C. King, F. Ahmad, and R. Al-Outa, “Impact of the Syrian conflict on irrigated agriculture in the Orontes Basin,” International Journal of Water Resources Development, vol. 31, no. 3, pp. 436–449, Jul. 2015, doi: 10.1080/07900627.2015.1023892.
-  K. S. Kibret, C. Marohn, and G. Cadisch, “Use of MODIS EVI to map crop phenology, identify cropping systems, detect land use change and drought risk in Ethiopia – an application of Google Earth Engine,” European Journal of Remote Sensing, vol. 53, no. 1, pp. 176–191, Jan. 2020, doi: 10.1080/22797254.2020.1786466.
-  L. K. Petersen, “Real-Time Prediction of Crop Yields From MODIS Relative Vegetation Health: A Continent-Wide Analysis of Africa,” Remote Sensing, vol. 10, no. 11, p. 1726, Nov. 2018, doi: 10.3390/rs10111726.
-  B. Wu et al., “Challenges and opportunities in remote sensing-based crop monitoring: a review,” National Science Review, vol. 10, no. 4, p. nwac290, Mar. 2023, doi: 10.1093/nsr/nwac290.
-  A. Huete, K. Didan, T. Miura, E. Rodriguez, X. Gao, and L. Ferreira, “Overview of the radiometric and biophysical performance of the MODIS vegetation indices,” Remote Sensing of Environment, vol. 83, no. 1, pp. 195–213, Nov. 2002, doi: 10.1016/S0034-4257(02)00096-2.
-  F. Jurečka, V. Lukas, P. Hlavinka, D. Semerádová, Z. Žalud, and M. Trnka, “Estimating Crop Yields at the Field Level Using Landsat and MODIS Products,” Acta Universitatis Agriculturae et Silviculturae Mendelianae Brunensis, vol. 66, no. 5, pp. 1141–1150, Oct. 2018, doi: 10.11118/actaun201866051141.
-  G. A. Tiruneh et al., “Mapping crop yield spatial variability using Sentinel-2 vegetation indices in Ethiopia,” Arabian Journal of Geosciences, vol. 16, no. 11, p. 631, Nov. 2023, doi: 10.1007/s12517-023-11754-x.
-  H. T. Pham, J. Awange, M. Kuhn, B. V. Nguyen, and L. K. Bui, “Enhancing Crop Yield Prediction Utilizing Machine Learning on Satellite-Based Vegetation Health Indices,” Sensors, vol. 22, no. 3, p. 719, Jan. 2022, doi: 10.3390/s22030719.
-  S. Hishe et al., “The impacts of armed conflict on vegetation cover degradation in Tigray, northern Ethiopia,” International Soil and Water Conservation Research, vol. 12, no. 3, pp. 635–649, Sep. 2024, doi: 10.1016/j.iswcr.2023.11.003.
-  Z. Guo, H. Abushama, K. Siddig, O. K. Kirui, K. Abay, and L. You, “Monitoring Indicators of Economic Activities in Sudan Amidst Ongoing Conflict Using Satellite Data,” Defence and Peace Economics, vol. 35, no. 8, pp. 992–1008, Nov. 2024, doi: 10.1080/10242694.2023.2290474.
-  B. N. Duncan et al., “A space‐based, high‐resolution view of notable changes in urban NO_{\textrm{x}} pollution around the world (2005–2014)”, Journal of Geophysical Research: Atmospheres, vol. 121, no. 2, pp. 976–996, Jan. 2016, doi: 10.1002/2015JD024121.
-  L. Malytska, A. Ladstätter&Weißenmayer, E. Galytska, and J. P. Burrows, “Assessment of environmental consequences of hostilities: Tropospheric NO2 vertical column amounts in the atmosphere over Ukraine in 2019–2022,” Atmospheric Environment, vol. 318, p. 120281, Feb. 2024, doi: 10.1016/j.atmosenv.2024.120281.
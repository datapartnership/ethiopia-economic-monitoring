# Summary of Datasets & Data Products

## Datasets

**Datasets** refer to **all** datasets used in the analytics prepared for a project. The **Datasets** table includes a description of the data and their update frequency, as well as access links and contact information for questions about use and access. Users should not require any datasets not included in this table to complete the analytical work for the Data Good.

The following is the list of all Datasets used in this Data Good:

```{note}
**Project Sharepoint** links are only accessible to the project team. For permissions to access these data, please write to the contact provided. The **Development Data Hub** is the World Bank's central data catalogue and includes meta-data and license information.Where feasible, all datasets that can be obtained through the Development Data Hub have been placed in a special collection: [Ethiopia Economic Monitoring Data Collection](https://datacatalog.worldbank.org/int/search/collections/sem).
```

```{table}
:name: datasets

| **ID** | **Name**                                      | **License**            | **Description**                                                                                                       | **Update Frequency**                                              | **Access**                                                                            | **Contact**                                  |
|--------|-----------------------------------------------|------------------------|-----------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------|---------------------------------------------------------------------------------------|----------------------------------------------|
| 1      | Ethiopia Admin Boundaries                        | Open                   | Admin boundaries up to level 3                                                                                        | No Planned Update (Last updated in December 2021)                                      | [Open Access Point (UNOCHA)](https://data.humdata.org/dataset/cod-ab-eth)                                     | [Dunstan Matekenya](mailto:dmatekenya@worldbankgroup.org), Data Lab                     |

| 2      | Population Data                               | Open   and Proprietary | Population with demographic information from Meta (2019) and population from WorldPop (2020)                          | No Planned Update (Data available for 2019 and 2020)                                                      | [Project SharePoint](https://worldbankgroup.sharepoint.com/:f:/r/teams/DevelopmentDataPartnershipCommunity-WBGroup/Shared%20Documents/Projects/Data%20Lab/Ethiopia%20Reform%20Monitoring%20Program/Data/population?csf=1&web=1&e=SnElbx)                                  | [Sahiti Sarva](mailto:dmatekenya@worldbankgroup.org), Data Lab                     |
| 3      | Places and Points of Interest (POIs)                            | Open | Open Street Map(OSM) and Overture Maps                         | OSM has frequent updates (last updated October, 2024); Overture Maps, last updated in September 2024| [Project SharePoint](https://worldbankgroup.sharepoint.com/:f:/r/teams/DevelopmentDataPartnershipCommunity-WBGroup/Shared%20Documents/Projects/Data%20Lab/Ethiopia%20Reform%20Monitoring%20Program/Data/osm?csf=1&web=1&e=yQC5Xe); [Overture Maps](https://docs.overturemaps.org)                                | [Dunstan Matekenya](mailto:dmatekenya@worldbankgroup.org), Data Lab                     |

| 4      | Overture Buildings                           | Open | Overture Maps                         | Overture Maps, last updated in September 2024| [Project SharePoint](https://worldbankgroup.sharepoint.com/:f:/r/teams/DevelopmentDataPartnershipCommunity-WBGroup/Shared%20Documents/Projects/Data%20Lab/Ethiopia%20Reform%20Monitoring%20Program/Data/overture?csf=1&web=1&e=iOcpeR);                              | [Dunstan Matekenya](mailto:dmatekenya@worldbankgroup.org), Data Lab                     |

| 5      | Ethiopia Road network                          | Open | Road network                         | No planned updated(Last updated in September 2024)| [Open Access Point (UNOCHA)](https://data.humdata.org/dataset/ethiopia-transportation-authority-roads); [Project SharePoint](https://worldbankgroup.sharepoint.com/:f:/r/teams/DevelopmentDataPartnershipCommunity-WBGroup/Shared%20Documents/Projects/Data%20Lab/Ethiopia%20Reform%20Monitoring%20Program/Data/hdx-roads?csf=1&web=1&e=7OJlhj);                              | [Dunstan Matekenya](mailto:dmatekenya@worldbankgroup.org), Data Lab                     |


| 6      | ACLED Conflict Data                           | Open                   | Timestamped, geolocated points where conflict took place collected based on news and   crowdsourced data              | Daily                                                             | [Project SharePoint](https://worldbankgroup.sharepoint.com/:f:/t/DevelopmentDataPartnershipCommunity-WBGroup/EvRbLR06KSZPlfIAgb1h5zkBviiwlWJGJqyrE21fmTumFA?e=nfxPja); [Development Data Hub](https://datacatalog.worldbank.org/int/search/dataset/0061835/acled---middle-east)                                              | [Andres Chamorro](mailto:achamorroelizond@worldbank.org), GOST                        |
| 7      | PlumeLabs Pollution Data                              | Development Data Partnership                   | Pollutants (e.g., PM2.5, PM19, NO2) measurements                                                                             | Daily                                           | [Project SharePoint](https://worldbankgroup.sharepoint.com/:f:/r/teams/DevelopmentDataPartnershipCommunity-WBGroup/Shared%20Documents/Projects/Data%20Lab/Ethiopia%20Reform%20Monitoring%20Program/Data/air_pollution?csf=1&web=1&e=1YCKVC)                                              | [Sahit Sarva](mailto:ssarva@worldbank.org), Data Lab |

| 8      | Google Trends                              | Development Data Partnership                   | Trending Search Terms on Google Search Engine                                                                           | Daily                                           | [Project SharePoint](https://worldbankgroup.sharepoint.com/:f:/r/teams/DevelopmentDataPartnershipCommunity-WBGroup/Shared%20Documents/Projects/Data%20Lab/Ethiopia%20Reform%20Monitoring%20Program/Data/google_trends?csf=1&web=1&e=W1Ws7b)                                              | [Sahit Sarva](mailto:ssarva@worldbank.org), Data Lab |

| 9      | Premise Crowd Sourced Surveys                              | Development Data Partnership                   | Survey Results from Premise                                                                           | No Planned Update (Last updated in January 2024)                                           | [Project SharePoint](https://worldbankgroup.sharepoint.com/:f:/r/teams/DevelopmentDataPartnershipCommunity-WBGroup/Shared%20Documents/Projects/Data%20Lab/Ethiopia%20Reform%20Monitoring%20Program/Data/survey/premise?csf=1&web=1&e=7aRGuN)                                              | [Sahit Sarva](mailto:ssarva@worldbank.org), Data Lab |


```

## Data Products Summary

**Data Products** are produced using the **Datasets** and can be further used to generate indicators and insights. All Data Products include documentation, references to original data sources (and/or information on how to access them), and a description of their limitations.

Following is a summary of Data Products used in this Data Good:

```{table}
:name: data_products

| **ID** | **Name**                                                                                       | **Description**                                                                                                       | **Limitations**                                                                                                                                                                                  | **Foundational Datasets Used (ID#)** |
|---------------|-------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------|
|     A         |     Urban Air Pollution and Economic Activity                                                                |     Analyse trends in pollution as a proxy to economic activity; profile air pollution along major road corridors                                                  |     No economic activity data, so no certain way to correlate pollution                                                                                        |     5,7                        |
|     B         |     Sentiments Towards Major Policy Announcements (e.g., Devaluation) |     Google Trends top searches; trends in searches in reference to specific points in time                       |     Google Trends only provides data based on population with access to internet, other population sectors not covered                                                                                                                                                   |     8                     |
```

# Content Engagement: Cross-Over Titles

* The more detailed write-up is below
* A summary slide deck is found [here](SnowflakeOptimization-CrossoverTitles.pptx)

## Business Use Case
Business Users want to know 

The crossover titles pipeline/process results in a [looker dashboard](https://looker.disneystreaming.com/dashboards/534?Title=Hawkeye+%282021%29&Country=HK&Streaming+Service=disney) to show `Content Engagement: Cross-Over Titles` for a given target title. The following visualizations shown:
- Top Over/Under Indexed Titles
    1. split all accounts into two groups: those that have watched this title, and those who havent
    2. for each group, calculate the % of accounts that have watched every other title in the catalog
    3. rank titiles by the difference between these two groups
- most viewed titles for watchers and non-watchers
    1. split all accounts into two groups: those that have watched this title and those who havent
    2. for each group, calculate the % of accounts that have watched every other title in the catalog
    3. rank titles by that %
- cross-over metric

example screenshots of the dashboard can be found [here](2_Content%20Engagement%20Cross-Over%20Titles%202021-11-17T1633.pdf)


## Problem Statement
After running the [topBigQueries.sql](../topBigQueries.sql) crossover titles was identified as the most expensive query as demonstrated by the `Oct2021` tab in the [excel workbook](bigQueries-2021001-20211101.xlsx).  The first row identifies the crossover titles queries and that it's total job credits for Oct2021 were 3X of the next largest query. (9725 credits for ~$20k).  We engaged with Lian Jian and Ravi Gupta on the Content Analytics team to understand context and look at a path toward reducing cost.

The key to the `topBigQueries sql` is a regex which parses the sql text.  The purpouse is to group similar queries together. Identifying the 'death by 1000 cuts' problems.  The regex used is

```
    ,regexp_replace( qh.query_text, '''[^'']*''|[0-9]+|{[^{}]+}', '<value>', 1, 0, 'ims' ) as adj_query_text
```

## Technical Components
1. Databricks Notebooks run on a weekly basis that issue sql queries to snowflake.
   1. parent notebooks contain queries to identify which target titles need a crossover analysis run for a list of countries
   2. child notebook (which is imported into parent) contains the CTE query to run the crossover analysis on a single target title
2. Snowflake queries insert records into an output table.
3. Looker Dashboard displays contents of output table

## Snowflake Tables 
* Source Tables
  * dss_prod.disney_plus.dim_account_series_level_engagement
  * dss_prod.disney_plus.dim_content_metadata
  * dss_prod.disney_plus.dim_content_metadata_content_unit_id_mapping_v
  * dss_prod.disney_plus.dim_daily_account_engagement
  * dss_prod.disney_plus.fact_content_boxart
* Destination Tables
  * over_under_indexed_titles_prod


#### Databricks Notebooks
URL's
  * [Original Workbooks](https://dss-dsa-prod-us-east-1.cloud.databricks.com/?o=3066777196544896#folder/2874931126136494) 
  * [Refactored Workbooks](https://dss-dsa-prod-us-east-1.cloud.databricks.com/?o=3066777196544896#folder/1794774354825814)

1. The "job" notebooks like `crossover_titles_{REGION}` run on a weekly schedule (staggered by country) and build a list of region-titles to process.  
2. Each `crossover_titles_{REGION}` notebook imports the `crossover_functions` notebook which contains the CTE queries for crossover titles
3. The `crossover_titles_{REGION}` notebook loops over a list of countries and calls a crossover_function for a given country/title

#### Looker Dashboard
* see description in `Business Use Case` section
* example screenshots of the dashboard can be found [here](2_Content%20Engagement%20Cross-Over%20Titles%202021-11-17T1633.pdf)
* [looker dashboard URL](https://looker.disneystreaming.com/dashboards/534?Title=Hawkeye+%282021%29&Country=HK&Streaming+Service=disney)

### Initial Observations
The CTE query in the original process to calculate crossover titles for a single specified title is already decently optimized.  Any gains found there would be small compared to the gap.  So we need to look at the process itself.

When this process was first delivered it was for a narrow set of countries/titles and was able to be completed within a reasonable time.  Once released, there was interest from stakeholders to increase the scope to other countries, streaming services, and titles.  The existing solution has not scaled well as demonstrated by the `Oct2021` tab in the [excel workbook](./bigQueries-2021001-20211101.xlsx).  

The approach is to refactor the sql and databricks notebooks so that the pipeline is run at the country level (with all target titles that belong to it) instead of the single target title level.  The expectation is that it will eliminate duplicate queries and I/O in a significant way.

## Actions Taken
1. gain access to snowflake with needed access
2. gain access to databricks with needed access
3. rewrote sql query to
   1. do batch queries that handle all target titles for a given country insead of just one
   2. save data to transient tables at key points instead of using pure CTE's
   3. changed queries to use raw tables instead of views
4. validated results
5. incorporated sql queries into new databricks notebooks
   1. parent notebook no longer loops over target titles
   2. consolidated 3 crossover_functions notebooks into one
   3. unified code to remove duplication and increase maintainablility
6. worked with ravi gupta to validate notebook runs in dev
7. productionalized notebooks with logging, error handling, country metrics, and query tags
8. worked with ravi gupta to validate and schedule notebook runs in prod

## Results of Enhancements

#### Runtime Improvements

Context Info:
* number of countries processed: 22
* total number of titles (across all countries): 15k

Metrics:
* See [slide seven for Mitigation Results](./SnowflakeOptimization-CrossoverTitles.pptx)

Snowflake Credits Improvements
- original credits: 10002 credits/month
- new credits: ~240 credits/month
- cost per credit: ~$2
- savings: ~$19k per month

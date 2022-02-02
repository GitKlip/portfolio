# Tagging snowflake queries

On databricks spark jobs you can (and should) add a tag to your snowflake connection.  This will allow all queries in the notebook/job to be identified.  This allows you to identify queries that belong to the job and see the sequence of queries that were called for the job.

A tag can be a simple string or a json string (allowing for multiple pieces of info)

```python
def extract_notebook_path() -> str :
    "Extracts the notebook path from the currently executing context"
    context_j = dbutils.notebook.entry_point.getDbutils().notebook().getContext()
    nb_path = context_j.notebookPath().value()
    return nb_path

nb_path = extract_notebook_path()
SNOWFLAKE_QUERY_TAG = f'{nb_path}{PROJECT_NAME_SUFFIX}'
print(f'{SNOWFLAKE_QUERY_TAG=}')


connection = {
  "sfUrl": "disneystreaming.us-east-1.snowflakecomputing.com",
  "sfUser": "DPLUS_ANALYTICS_PROD_ETL",
  "sfPassword": dbutils.secrets.get(scope="dplus", key="analytics_key"),
  "sfDatabase": "DSS_PROD",
  "sfSchema": "DPLUS_ANALYTICS",
  "sfWarehouse": "DPLUS_ANALYTICS_PROD_WH"
  "query_tag" = SNOWFLAKE_QUERY_TAG
}
```


# Thoughts on Cacheing (in databricks)

- When you cache a DataFrame create a new variable for it cachedDF = df.cache().
- Unpersist the DataFrame after it is no longer needed using cachedDF.unpersist().
- Before you cache, make sure you are caching only what you will need in your queries. 
- Use the caching only if it makes sense. That is if the cached computation will be used multiple times.

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pyspark.sql.functions as F
from pyspark.sql.functions import lit
from pyspark.sql.types import *
import time
from pprint import pprint

notebook_path = dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()
notebook_name = pathlib.PurePath(notebook_path).name

connection = {
  "sfUrl": "mycompany.us-east-1.snowflakecomputing.com",
  "sfUser": "SOME_USER_NAME",
  "sfPassword": dbutils.secrets.get(scope="dplus", key="snowflake_key"),
  "sfDatabase": "MY_DB",
  "sfSchema": "MY_SCHEMA",
  "sfWarehouse": "ecornelsen_warehouse"
  "query_tag": notebook_path
}


temp_tables = dict(
    alpha = f"{connection['sfDatabase']}.{connection['sfSchema']}.of_the_pack",
    bravo = f"{connection['sfDatabase']}.{connection['sfSchema']}.way_to_go",
    charlie = f"{connection['sfDatabase']}.{connection['sfSchema']}.brown",
)

# Function to run ddl queries
def spark_sf_ddl(connection: dict, query:str, print_sql:bool = False) -> None:
    Utils = spark._jvm.net.snowflake.spark.snowflake.Utils
    print(f"Executing Query: [{query.lstrip()[0:100].rstrip()} ....]")
    if print_sql:
        print(query)
    beg = time.perf_counter()
    Utils.runQuery(connection, query)
    duration_min = (time.perf_counter() - beg)/60
    print(f" completed. duration={duration_min:0.2f}m")

# function to run sql queries that return a result
def spark_sf_query(connection:dict, sql:str, print_sql:bool = False) -> DataFrame:
    spark_df = spark.read \
      .format("snowflake") \
      .options(**connection) \
      .option("query",  sql) \
      .load()
    
    if print_sql:
        print("spark_sf_query:")
        print(sql)
    return spark_df

## FIND TRANSIENT TABLES THAT MAY NEED TO BE CLEANED UP
def find_transient_snowflake_tables(connection: dict, table_name_query_str: str = None):
    if table_name_query_str:
      table_name_filter = f" and table_name like '{table_name_query_str}' "
    else:
      table_name_filter = ""

    sql = f"""
        select 
            table_catalog,
            table_schema, 
            table_name, 
            table_type,
            is_transient,
            row_count,
            table_owner,
            created as create_date,
            last_altered as modify_date,
            CONCAT('drop table ',table_catalog,'.',table_schema,'.',table_name,';') as drop_sql
        from information_schema.tables 
        where 1=1
          {table_name_filter}
        order by 1,2,3
        ; 
    """
    print(sql)
    df = spark_sf_query(connection, sql)
    display(df)
    
## Cleanup Transinet Tables
def cleanup_transient_snowflake_tables(connection: dict, table_names: dict) -> None:
    for k, v in table_names.items():
        print(f"dropping table {k} = [{v}]")
        spark_sf_ddl(connection, f"drop table {v};")



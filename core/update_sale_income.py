import pandas as pd
import numpy as np
import psycopg2
import os
from dotenv import load_dotenv
from core.models import Sale
load_dotenv()

# DB CONNECT

host = os.getenv("DB_HOST")
dbname = os.getenv("DB_NAME")
user = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")

conn_string = "host={0} user={1} dbname={2} password={3}".format(host, user, dbname, password)
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

query_products = "SELECT * FROM core_product;"
query_products_sales = "SELECT * FROM core_productsale;"
query_sales = "SELECT * FROM core_sale;"
df_product = pd.read_sql(query_products, conn)
df_product_sales = pd.read_sql(query_products_sales, conn)
df_sales = pd.read_sql(query_sales, conn)

df_product.drop(columns=["description", "presentation", "cost", "image", "cost_currency",
                "price_1_currency", "price_2_currency", "price_3_currency", "code", "brand"], inplace=True)

df_product["mean_price"] = df_product[[
    'price_1', 'price_2', 'price_3']].mean(axis=1)
df_product.drop(columns=["price_1", "price_2", "price_3"], inplace=True)

df_sales.drop(columns=["status", "description",
              "income_currency", "income"], inplace=True)

merged_products = pd.merge(df_product, df_product_sales, left_on="id",
                           right_on="product_id", suffixes=["_product", "_product_sales"])

df_merged_products_with_sales = pd.merge(
    merged_products, df_sales, left_on="sale_id", right_on="id", suffixes=["_merged", "_sales"])
df_merged_products_with_sales.drop(
    df_merged_products_with_sales[df_merged_products_with_sales["name"] == "NONE"].index, inplace=True)

df_merged_products_with_sales["income"] = df_merged_products_with_sales.apply(
    lambda row: row["mean_price"] * row["quantity"], axis=1)

unique_sales_id = df_merged_products_with_sales["sale_id"].unique()
income_by_sales = []
unique_sales_id_series = pd.Series(unique_sales_id)

incomes = unique_sales_id_series.apply(
    lambda sale_id: df_merged_products_with_sales[df_merged_products_with_sales["sale_id"] == sale_id]["income"].sum())

data_df = pd.DataFrame({"sale_id": unique_sales_id, "income": incomes})

l = len(data_df)
i = 0

for row in data_df.itertuples():
    i += 1
    print(f"{i}/{l}")
    sale = Sale.objects.get(pk=row.sale_id)
    sale.income = round(row.income, 2)
    sale.save()

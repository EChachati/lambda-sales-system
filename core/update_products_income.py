import pandas as pd
import numpy as np
import psycopg2
import os
from dotenv import load_dotenv
from core.models import Sale, ProductSale
load_dotenv()

# DB CONNECT

host = os.getenv("DB_HOST")
dbname = os.getenv("DB_NAME")
user = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")

conn_string = "host={0} user={1} dbname={2} password={3}".format(
    host, user, dbname, password)
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

merged_products['income'] = merged_products['quantity'] * \
    merged_products['mean_price']

l = len(merged_products)
i = 0

for ps in merged_products.itertuples():
    i += 1
    print(f"{i}/{l}")
    product_sales = ProductSale.objects.get(pk=ps.id_product_sales)
    product_sales.income = ps.income
    product_sales.save()

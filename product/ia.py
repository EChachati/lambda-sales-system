import pandas as pd
import numpy as np
from dotenv import load_dotenv
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor
from django.db import connection as conn
from core.utils import save_model


def get_grouped_product_data(to_dict=False):
    df_productsales = pd.read_sql("SELECT * FROM core_productsale;", conn)
    df_products = pd.read_sql("SELECT * FROM core_product;", conn)
    df_sales = pd.read_sql("SELECT * FROM core_sale;", conn)

    df_merged = pd.merge(df_productsales, df_products, left_on="product_id",
                         right_on="id", suffixes=("_productsale", "_product"))
    df_merged.drop(columns=["brand", "image", "cost_currency", "price_1_currency", "price_2_currency", "price_3_currency",
                   "code", "price_1", "price_2", "price_3", "description", "presentation", "income_currency"], inplace=True)
    df_merged.set_index("id_product", inplace=True)

    df_merged_sales_with_products = pd.merge(
        df_merged, df_sales, left_on="sale_id", right_on="id", suffixes=("_productsale", "_sale"))
    df_merged_sales_with_products["year"] = df_merged_sales_with_products.apply(
        lambda row: row["date"].year, axis=1)
    df_merged_sales_with_products["month"] = df_merged_sales_with_products.apply(
        lambda row: row["date"].month, axis=1)
    df_merged_sales_with_products.drop(
        columns=["id", "description", "income_currency", "status", "date"], inplace=True)

    df_groupby_products = df_merged_sales_with_products.groupby(
        ["year", "month", "product_id"])
    sales_data = {
        'income': df_groupby_products['income_productsale'].sum(),
        'count': df_groupby_products['quantity'].sum(),
        'name': df_groupby_products['name'].first(),
    }

    df_machine_learning = pd.DataFrame(sales_data)
    df_machine_learning.reset_index(inplace=True)

    if to_dict:
        d = {}
        for row in df_machine_learning.itertuples():
            if row.product_id not in d.keys():
                d[row.product_id] = {'name': row.name}
            if row.year not in d[row.product_id].keys():
                d[row.product_id][row.year] = {}
            if row.month not in d[row.product_id][row.year].keys():
                d[row.product_id][row.year][row.month] = {
                    'income': row.income, 'count': row.count}
        return d
    return df_machine_learning


def train_model_product(income=False):
    df_machine_learning = get_grouped_product_data()

    df_machine_learning.drop(
        df_machine_learning[df_machine_learning['name'] == "NONE"].index, inplace=True)

    df_machine_learning["sales_next_month"] = df_machine_learning.groupby("product_id")[
        "income"].shift(-1)
    df_machine_learning["sales_next_month_count"] = df_machine_learning.groupby(
        "product_id")["count"].shift(-1)
    df_machine_learning.dropna(inplace=True)
    features = ["income", "count"]
    imputer = SimpleImputer()
    Xtr_per_month = imputer.fit_transform(df_machine_learning[features])

    if income == True:
        ytr_per_month = df_machine_learning['sales_next_month']
        model_type = 'income'
    else:
        ytr_per_month = df_machine_learning['sales_next_month_count']
        model_type = 'count'

    model = RandomForestRegressor(n_estimators=100, random_state=0, n_jobs=6)
    model.fit(Xtr_per_month, ytr_per_month)

    save_model(model, f"product_{model_type}_per_month_model")
    print(f"product_{model_type}_per_month_model")
    return model


def get_grouped_category_data(to_dict=False):
    df_productsales = pd.read_sql("SELECT * FROM core_productsale;", conn)
    df_products = pd.read_sql("SELECT * FROM core_product;", conn)
    df_sales = pd.read_sql("SELECT * FROM core_sale;", conn)
    df_categories = pd.read_sql("SELECT * FROM core_category;", conn)

    df_merged_products_productsales = pd.merge(
        df_productsales, df_products, left_on="product_id", right_on="id", suffixes=("_productsale", "_product"))
    df_merged_products_productsales.drop(columns=["brand", "image", "cost_currency", "price_1_currency", "price_2_currency",
                                         "price_3_currency", "code", "price_1", "price_2", "price_3", "description", "presentation", "income_currency"], inplace=True)
    df_merged_products_productsales.set_index("id_product", inplace=True)

    df_merged_sales_with_products = pd.merge(
        df_merged_products_productsales, df_sales, left_on="sale_id", right_on="id", suffixes=("_productsale", "_sale"))
    df_merged_sales_with_products["year"] = df_merged_sales_with_products.apply(
        lambda row: row["date"].year, axis=1)
    df_merged_sales_with_products["month"] = df_merged_sales_with_products.apply(
        lambda row: row["date"].month, axis=1)
    df_merged_sales_with_products.drop(
        columns=["id", "description", "income_currency", "status", "date"], inplace=True)

    df_merged_with_categories = pd.merge(df_merged_sales_with_products, df_categories,
                                         left_on="category_id", right_on="id", suffixes=("_productsale", "_category"))

    df_groupby_categories = df_merged_with_categories.groupby(
        ["category_id", "year", "month"])

    sales_data = {
        'income': df_groupby_categories['income_productsale'].sum(),
        'count': df_groupby_categories['quantity'].sum(),
        'name': df_groupby_categories['name_category'].first(),
    }

    df = pd.DataFrame(sales_data)
    df.reset_index(inplace=True)
    if to_dict:
        d = {}
        for row in df.itertuples():
            if row.category_id not in d.keys():
                d[row.category_id] = {'name': row.name}
            if row.year not in d[row.category_id].keys():
                d[row.category_id][row.year] = {}
            if row.month not in d[row.category_id][row.year].keys():
                d[row.category_id][row.year][row.month] = {
                    'income': row.income, 'count': row.count}
        return d

    return df


def train_model_category(income=False):
    df = get_grouped_category_data()

    df["sales_next_month"] = df.groupby("category_id")["income"].shift(-1)
    df["sales_next_month_count"] = df.groupby("category_id")["count"].shift(-1)
    df.dropna(inplace=True)

    features = ["income", "count"]
    imputer = SimpleImputer()
    Xtr_per_month = imputer.fit_transform(df[features])
    if income:
        ytr_per_month = df['sales_next_month']
        model_type = 'income'
    else:
        ytr_per_month = df['sales_next_month_count']
        model_type = 'count'

    model = RandomForestRegressor(n_estimators=100, random_state=0, n_jobs=6)
    model.fit(Xtr_per_month, ytr_per_month)

    save_model(model, f"category_{model_type}_per_month_model")
    print(f"category_{model_type}_per_month_model")
    return model

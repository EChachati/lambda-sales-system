import pandas as pd
import numpy as np
from dotenv import load_dotenv
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor
from django.db import connection as conn
from core.utils import save_model


def get_grouped_data(to_dict=False):
    df_clients = pd.read_sql_query("SELECT * FROM core_client", conn)
    df_sales = pd.read_sql("SELECT * FROM core_sale;", conn)

    df_clients.drop(columns=['address', 'phone', 'image'], inplace=True)

    df_merged = pd.merge(df_clients, df_sales, left_on='id',
                         right_on='client_id', suffixes=('_client', '_sale'))
    df_merged.drop(columns=['id_client', 'salesman_id',
                   'income_currency', 'status', 'description'], inplace=True)

    df_merged['year'] = df_merged.apply(lambda row: row['date'].year, axis=1)
    df_merged['month'] = df_merged.apply(lambda row: row['date'].month, axis=1)
    df_merged.drop(columns=['date'], inplace=True)

    df_groupby = df_merged.groupby(["client_id", 'year', 'month'])
    sales_data = {
        'income': df_groupby['income'].sum(),
        'count': df_groupby['client_id'].count(),
        'name': df_groupby['name'].first(),
    }

    df_sales_per_month = pd.DataFrame(sales_data)
    df_sales_per_month.reset_index(inplace=True)

    if to_dict:
        d = {}
        for row in df_sales_per_month.itertuples():
            if row.client_id not in d.keys():
                d[row.client_id] = {'name': row.name}
            if row.year not in d[row.client_id].keys():
                d[row.client_id][row.year] = {}
            if row.month not in d[row.client_id][row.year].keys():
                d[row.client_id][row.year][row.month] = {
                    'income': row.income, 'count': row.count}
        return d

    df = df_sales_per_month
    df["sales_next_month"] = df.groupby("client_id")["income"].shift(-1)
    df["sales_next_month_count"] = df.groupby("client_id")["count"].shift(-1)
    df.dropna(inplace=True)
    df["diff_sales_next_month"] = df.groupby("client_id")["income"].diff(1)
    df["diff_sales_next_month_count"] = df.groupby("client_id")[
        "count"].diff(1)
    df['last_sale_next_month'] = df.groupby("client_id")['income'].shift(1)
    df['last_sale_next_month_count'] = df.groupby("client_id")[
        'count'].shift(1)

    return df


def train_model(income=False):
    df = get_grouped_data()

    model_type = 'income' if income else 'count'

    features = [
        "income",
        "count",
        "client_id",
        "month",
        "diff_sales_next_month",
        "diff_sales_next_month_count",
        "last_sale_next_month",
        "last_sale_next_month_count"
    ]

    imputer = SimpleImputer()
    Xtr_per_month = imputer.fit_transform(df[features])

    if income:
        ytr_per_month = df['sales_next_month']
    else:
        ytr_per_month = df['sales_next_month_count']

    model = RandomForestRegressor(n_estimators=100, random_state=0, n_jobs=6)
    model.fit(Xtr_per_month, ytr_per_month)

    save_model(model, f"client_{model_type}_per_month_model")
    print(f"client_{model_type}_per_month_model")
    return model


def sales_realized_per_salesman(client_id=None):
    df_clients = pd.read_sql_query("SELECT * FROM core_client", conn)
    df_sales = pd.read_sql("SELECT * FROM core_sale;", conn)
    df_salesmans = pd.read_sql("SELECT * FROM core_salesman;", conn)
    df_merged = pd.merge(df_sales, df_salesmans, left_on='salesman_id',
                         right_on='id', suffixes=('_sale', '_salesman'))
    df_merged_clients = pd.merge(
        df_merged, df_clients, left_on='client_id', right_on='id', suffixes=('_sale', '_client'))
    df_merged_clients.drop(columns=['id_sale', 'id_salesman', 'date', 'status', 'income_currency', 'description', 'identity_card_sale',
                           'image_sale', 'phone_1', 'phone_2', 'address_sale', 'identity_card_client', 'phone', 'address_client', 'image_client'], inplace=True)
    df_merged_clients.rename(
        columns={'name_sale': 'name_salesman'}, inplace=True)
    df_merged_clients.set_index(
        ['client_id', 'salesman_id', 'name_salesman'], inplace=True)
    df_merged_clients["count"] = df_merged_clients.groupby(
        ['client_id', 'salesman_id'])['id'].count()
    df_merged_clients["total_income"] = df_merged_clients.groupby(
        ['client_id', 'salesman_id'])['income'].sum()
    df_merged_clients.reset_index(inplace=True)
    data = {
        "name_salesman": df_merged_clients.groupby(['client_id', 'salesman_id'])['name_salesman'].first(),
        "name_client": df_merged_clients.groupby(['client_id', 'salesman_id'])['name_client'].first(),
        "count": df_merged_clients.groupby(['client_id', 'salesman_id'])['count'].first(),
        'total_income': df_merged_clients.groupby(['client_id', 'salesman_id'])['total_income'].first()
    }
    df_aux = pd.DataFrame(data)
    df = df_aux.reset_index()
    if client_id:
        df = df[df['client_id'] == client_id]

    dict = {}
    for row in df.itertuples():
        if row.client_id not in dict.keys():
            dict[row.client_id] = {'name': row.name_client, 'salesman': {}}
        if row.salesman_id not in dict[row.client_id]['salesman'].keys():
            dict[row.client_id]['salesman'][row.salesman_id] = {
                'name': row.name_salesman,
                'count': row.count,
                'total_income': row.total_income
            }

    return dict


def sales_realized_per_category(client_id=None):
    df_clients = pd.read_sql_query("SELECT * FROM core_client", conn)
    df_sales = pd.read_sql("SELECT * FROM core_sale;", conn)
    df_categories = pd.read_sql("SELECT * FROM core_category;", conn)
    df_products = pd.read_sql("SELECT * FROM core_product;", conn)
    df_productsales = pd.read_sql("SELECT * FROM core_productsale;", conn)

    df_merged_sales = pd.merge(df_sales, df_productsales, left_on='id',
                               right_on='sale_id', suffixes=('_sale', '_productsales'))
    df_merged_with_products = pd.merge(
        df_merged_sales, df_products, left_on='product_id', right_on='id', suffixes=('_sales', '_products'))
    df_merged_with_categories = pd.merge(df_merged_with_products, df_categories,
                                         left_on='category_id', right_on='id', suffixes=('_products', '_categories'))
    df_final_merged = pd.merge(df_merged_with_categories, df_clients,
                               left_on='client_id', right_on='id', suffixes=('_categories', '_client'))
    df_final_merged.drop(columns=['date', 'description_sales', 'income_currency_sale', 'status',
                                  'price_1_currency', 'price_2_currency', 'price_3_currency',
                                  'price_1', 'price_2', 'price_3',
                                  'code', 'identity_card', 'image_client',
                                  'address', 'phone', 'presentation',
                                  'income_currency_productsales', 'cost',
                                  'brand', 'cost_currency', 'description_products',
                                  'image_categories', 'id', 'id_categories', 'salesman_id',
                                  'income_sale', 'id_sale', 'id_products'
                                  ], inplace=True)
    df_final_merged.set_index(['client_id', 'category_id'], inplace=True)
    df_final_merged['count'] = df_final_merged.groupby(
        ['client_id', 'category_id'])['quantity'].sum()
    df_final_merged['total_income'] = df_final_merged.groupby(
        ['client_id', 'category_id'])['income_productsales'].sum()
    df_final_merged.reset_index(inplace=True)
    data = {
        "name_client": df_final_merged.groupby(['client_id', 'category_id'])['name'].first(),
        "name_category": df_final_merged.groupby(['client_id', 'category_id'])['name_categories'].first(),
        "client_id": df_final_merged.groupby(['client_id', 'category_id'])['client_id'].first(),
        "category_id": df_final_merged.groupby(['client_id', 'category_id'])['category_id'].first(),
        "count": df_final_merged.groupby(['client_id', 'category_id'])['count'].first(),
        "total_income": df_final_merged.groupby(['client_id', 'category_id'])['total_income'].first()
    }

    df = pd.DataFrame(data)
    df.drop(columns=['category_id', 'client_id'], inplace=True)
    df.reset_index(inplace=True)
    if client_id:
        df = df[df['client_id'] == client_id]

    dict = {}
    for row in df.itertuples():
        if row.client_id not in dict.keys():
            dict[row.client_id] = {'name': row.name_client, 'categories': {}}
        if row.category_id not in dict[row.client_id]['categories'].keys():
            dict[row.client_id]['categories'][row.category_id] = {
                'name': row.name_category,
                'count': row.count,
                'total_income': row.total_income
            }

    return dict


def sales_realized_per_product(client_id=None):
    df_clients = pd.read_sql_query("SELECT * FROM core_client", conn)
    df_sales = pd.read_sql("SELECT * FROM core_sale;", conn)
    df_products = pd.read_sql("SELECT * FROM core_product;", conn)
    df_productsales = pd.read_sql("SELECT * FROM core_productsale;", conn)

    df_merged_sales = pd.merge(df_sales, df_productsales, left_on='id',
                               right_on='sale_id', suffixes=('_sale', '_productsales'))
    df_merged_with_products = pd.merge(
        df_merged_sales, df_products, left_on='product_id', right_on='id', suffixes=('_sales', '_products'))
    df_final_merged = pd.merge(df_merged_with_products, df_clients, left_on='client_id',
                               right_on='id', suffixes=('_sales_products', '_client'))
    df_final_merged.drop(columns=['date', 'description_sales', 'income_currency_sale', 'status',
                                  'price_1_currency', 'price_2_currency', 'price_3_currency',
                                  'price_1', 'price_2', 'price_3',
                                  'code', 'identity_card', 'image_client',
                                  'address', 'phone', 'presentation',
                                  'income_currency_productsales', 'cost',
                                  'brand', 'cost_currency', 'description_products',
                                  'salesman_id', 'income_sale', 'id_sale', 'image_sales_products',
                                  'category_id', 'id_sales_products', 'id_productsales'
                                  ], inplace=True)
    df_final_merged.set_index(['client_id', 'product_id'], inplace=True)
    df_final_merged['count'] = df_final_merged.groupby(
        ['client_id', 'product_id'])['quantity'].sum()
    df_final_merged['total_income'] = df_final_merged.groupby(
        ['client_id', 'product_id'])['income_productsales'].sum()

    df = df_final_merged.reset_index()
    df.rename(columns={'name_sales_products': 'name_products'}, inplace=True)

    if client_id:
        df = df[df['client_id'] == client_id]

    dict = {}
    for row in df.itertuples():
        if row.client_id not in dict.keys():
            dict[row.client_id] = {'name': row.name_client, 'products': {}}
        if row.product_id not in dict[row.client_id]['products'].keys():
            dict[row.client_id]['products'][row.product_id] = {
                'name': row.name_products,
                'count': row.count,
                'total_income': row.total_income
            }

    return dict

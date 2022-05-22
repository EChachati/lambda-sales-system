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

    return df_sales_per_month


def train_model(income=False):
    df = get_grouped_data()

    model_type = 'income' if income else 'count'

    df["sales_next_month"] = df.groupby("client_id")["income"].shift(-1)
    df["sales_next_month_count"] = df.groupby("client_id")["count"].shift(-1)
    df.dropna(inplace=True)
    features = ["income", "count"]  # , "client_id", "month"]
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

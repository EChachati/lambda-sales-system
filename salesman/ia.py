import pandas as pd
import numpy as np
from dotenv import load_dotenv
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor
from django.db import connection as conn
from core.utils import save_model


def get_grouped_data(to_dict=False):
    df_salesmans = pd.read_sql_query("SELECT * FROM core_salesman", conn)
    df_sales = pd.read_sql("SELECT * FROM core_sale;", conn)

    df_merged = pd.merge(df_salesmans, df_sales, left_on='id',
                         right_on='salesman_id', suffixes=('_salesman', '_sale'))
    df_merged.drop(columns=['client_id', 'income_currency', 'status',
                   'description', 'address', 'phone_1', 'phone_2', 'image'], inplace=True)

    df_merged['year'] = df_merged.apply(lambda row: row['date'].year, axis=1)
    df_merged['month'] = df_merged.apply(lambda row: row['date'].month, axis=1)
    df_merged.drop(columns=['date'], inplace=True)

    df_groupby = df_merged.groupby(["salesman_id", 'year', 'month'])
    sales_data = {
        'income': df_groupby['income'].sum(),
        'count': df_groupby['salesman_id'].count(),
        'name': df_groupby['name'].first(),
    }

    df_sales_per_month = pd.DataFrame(sales_data)
    df_sales_per_month.reset_index(inplace=True)

    if to_dict:
        d = {}
        for row in df_sales_per_month.itertuples():
            if row.salesman_id not in d.keys():
                d[row.salesman_id] = {'name': row.name}
            if row.year not in d[row.salesman_id].keys():
                d[row.salesman_id][row.year] = {}
            if row.month not in d[row.salesman_id][row.year].keys():
                d[row.salesman_id][row.year][row.month] = {
                    'income': row.income, 'count': row.count}
        return d

    return df_sales_per_month


def train_model(income=False):
    df = get_grouped_data()

    model_type = 'income' if income else 'count'

    df["sales_next_month"] = df.groupby("salesman_id")["income"].shift(-1)
    df["sales_next_month_count"] = df.groupby("salesman_id")["count"].shift(-1)
    df.dropna(inplace=True)
    features = ["income", "count"]
    imputer = SimpleImputer()
    Xtr_per_month = imputer.fit_transform(df[features])

    if income:
        ytr_per_month = df["sales_next_month"]
    else:
        ytr_per_month = df["sales_next_month_count"]


    model = RandomForestRegressor(n_estimators=100)
    model.fit(Xtr_per_month, df["sales_next_month"])

    save_model(model, f"salesman_{model_type}_per_month_model")
    print(f"salesman_{model_type}_per_month_model")
    return model
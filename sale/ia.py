import pandas as pd
import numpy as np
import psycopg2
import os
from dotenv import load_dotenv
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor
import pickle
from typing import List
load_dotenv()


def get_connection():
    # DB Connection for IA
    host = os.getenv("HOST")
    dbname = os.getenv("DB_NAME")
    user = os.getenv("DB_USERNAME")
    password = os.getenv("DATABASE_PASSWORD")

    conn_string = "host={0} user={1} dbname={2} password={3}".format(
        host, user, dbname, password)
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    return conn, cursor


conn, cursor = get_connection()


def get_grouped_data(month=True, to_dict=False):
    query = "SELECT * FROM core_sale;"
    df_sales_copy = pd.read_sql(query, conn)
    df_sales_copy["year"] = df_sales_copy.apply(
        lambda row: row["date"].year, axis=1)
    df_sales_copy["month"] = df_sales_copy.apply(
        lambda row: row["date"].month, axis=1)
    df_sales_copy["day"] = df_sales_copy.apply(
        lambda row: row["date"].day, axis=1)
    df_sales_copy.drop(
        columns=["date", "description", "status", "income_currency"], inplace=True)

    df_sales_copy.set_index(['year', 'month', 'day'], inplace=True)

    group_by_list = ['year', 'month'] if month else ['year']

    df_groupby_sales = df_sales_copy.groupby(group_by_list)
    sales_data = {
        'income': df_groupby_sales['income'].sum(),
        'count': df_groupby_sales['id'].count()
    }

    if to_dict:
        # Get the historic data from the database
        # It is a dataframe with the historic data
        # send it by dict wit h this strructure:
        """
        {
            2022: {
                11: {
                    income: #####,
                    count: #####,
                    }
                12: {
                    income: #####,
                    count: #####,
                    },
            2023: { ...
        }
        """
        pass
    df = pd.DataFrame(sales_data)
    df.reset_index(inplace=True)
    return df


def train_model(month=True, income=True, group_by=None):
    time_range = 'month' if month else 'year'
    df = get_grouped_data(month=month)
    if group_by:
        df[f"sales_next_{time_range}"] = df.groupby(group_by)[
            "income"].shift(-1)
        df[f"sales_next_{time_range}_count"] = df.groupby(group_by)[
            "count"].shift(-1)
    else:
        df[f"sales_next_{time_range}"] = df["income"].shift(-1)
        df[f"sales_next_{time_range}_count"] = df["count"].shift(-1)

    df.dropna(inplace=True)

    print(df)

    features = ["income", "count"]  # month
    imputer = SimpleImputer()

    Xtr = imputer.fit_transform(df[features])
    if income:
        ytr = df[f'sales_next_{time_range}']
        model_type = "income"
    else:  # count
        ytr = df[f'sales_next_{time_range}_count']
        model_type = "count"

    model = RandomForestRegressor(n_estimators=100, random_state=0, n_jobs=6)
    model.fit(Xtr, ytr)

    save_model(
        model, f"sale_{model_type}_{time_range}_grouped_by_{group_by}_model")

    return model


def save_model(model, name):
    with open(f"core/models_ia/{name}.pkl", "wb") as f:
        pickle.dump(model, f)


def load_model(name):
    try:
        with open(f"core/models_ia/{name}.pkl", "rb") as f:
            model = pickle.load(f)
        return model
    except:
        return None


def predict(model, income: List, count: List):

    count = [595, 872, 777, 710, 739, 745, 876, 816, 908, 1114, 1106, 838]
    income = [158706.08, 257297.47, 192503.59, 206944.43, 166545.74, 166283.13,
              158943.72, 138120.65, 175135.81, 279933.26, 272847.04, 222096.95]
    data = SimpleImputer().fit_transform(
        pd.DataFrame({'income': income, 'count': count})
    )
    return model.predict(data)

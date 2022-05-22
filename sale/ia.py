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
    """
    It connects to the database and returns a connection and cursor object
    :return: A tuple of two objects: a connection object and a cursor object.
    """
    # DB Connection for IA
    host = os.getenv("DB_HOST")
    dbname = os.getenv("DB_NAME")
    user = os.getenv("DB_USERNAME")
    password = os.getenv("DB_PASSWORD")

    conn_string = "host={0} user={1} dbname={2} password={3}".format(
        host, user, dbname, password)
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    return conn, cursor


conn, cursor = get_connection()


def get_grouped_data(month=True, to_dict=False):
    """
    It takes a SQL query, converts it to a dataframe, groups it by year and month, and returns the
    grouped dataframe

    :param month: If True, the data will be grouped by month. If False, the data will be grouped by
    year, defaults to True (optional)
    :param to_dict: If True, the function will return a dictionary instead of a dataframe, defaults to
    False (optional)
    :return: A dataframe or a dictionary with the following structure:
    {
        year: {
            month: {
                'income': income,
                'count': count
            }
        }
    }
    """
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
    df = pd.DataFrame(sales_data)
    df.reset_index(inplace=True)
    if to_dict:
        # Converting the dataframe to a dictionary.
        d = {}
        for row in df.itertuples():
            if row.year not in d.keys():
                d[row.year] = {}
            if row.month not in d[row.year].keys():
                d[row.year][row.month] = {
                    'income': row.income, 'count': row.count}
        return d
    return df


def train_model(month=True, income=True, group_by=None):
    """
    It takes in a dataframe, and returns a trained model

    :param month: True if you want to train the model on monthly data, False if you want to train the
    model on yearly data, defaults to True (optional)
    :param income: True if you want to predict income, False if you want to predict count, defaults to
    True (optional)
    :param group_by: the column to group by. If None, then no grouping is done, can be month or year
    :return: The model is being returned.
    """
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
    print(f"sale_{model_type}_{time_range}_grouped_by_{group_by}_model")
    return model


def save_model(model, name):
    """
    It takes a model and a name, and saves the model as a pickle file with the name you gave it

    :param model: The model you want to save
    :param name: The name of the model
    """
    with open(f"core/models_ia/{name}.pkl", "wb") as f:
        pickle.dump(model, f)


def load_model(name):
    """
    It loads a model from a file

    :param name: The name of the model
    :return: The model is being returned. None if it doesn't exist
    """
    try:
        with open(f"core/models_ia/{name}.pkl", "rb") as f:
            model = pickle.load(f)
        return model
    except:
        return None


def predict(model, income: List, count: List):
    """
    It takes in a model, a list of incomes, and a list of counts, and returns a list of predictions

    :param model: The model you want to use to predict the data
    :param income: List of income values
    :type income: List
    :param count: The number of people in the household
    :type count: List
    :return: The predicted values for the given data.
    """
    data = SimpleImputer().fit_transform(
        pd.DataFrame({'income': income, 'count': count})
    )
    return model.predict(data)

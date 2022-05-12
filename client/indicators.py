import pandas as pd
from django.db import connection
from typing import List
from core.models import Category, Client, Product, ProductSale, Sale, Salesman


def get_sales_df(client_id=None, salesman_id=None):
    """
    > This function returns a pandas dataframe of sales data, optionally filtered by client_id and/or
    salesman_id

    :param client_id: the id of the client you want to filter by
    :param salesman_id: The id of the salesman you want to get the sales for
    :return: A dataframe with the columns id, income, date, client_id, salesman_id
    """
    query = """
    SELECT id, income, date, client_id, salesman_id FROM core_sale
    """
    if client_id and salesman_id:
        query += f"WHERE client_id = {client_id} AND salesman_id = {salesman_id}"
    elif client_id and not salesman_id:
        query += f"WHERE client_id = {client_id}"
    elif not client_id and salesman_id:
        query += f"WHERE salesman_id = {salesman_id}"

    df = pd.read_sql(query, connection)
    return df


def get_productsales_df(sale_id: List = None, product_id: List = None):
    """
    > This function returns a dataframe of all the productsales in the database, or a subset of them if
    the sale_id and/or product_id parameters are passed

    :param sale_id: List = None, product_id: List = None
    :type sale_id: List
    :param product_id: List = None, sale_id: List = None
    :type product_id: List
    :return: A dataframe with the columns id, sale_id, product_id, quantity, income
    """
    query = "SELECT id, sale_id, product_id, quantity, income FROM core_productsale"

    if sale_id and product_id:
        query += f" WHERE sale_id IN ({str(set(sale_id)).replace('{', '').replace('}', '')}) AND product_id IN ({str(set(product_id)).replace('{', '').replace('}', '')})"
    elif sale_id:
        query += f" WHERE sale_id IN ({str(set(sale_id)).replace('{', '').replace('}', '')})"
    elif product_id:
        query += f" WHERE product_id IN ({str(set(product_id)).replace('{', '').replace('}', '')})"

    return pd.read_sql(query, connection)


def get_products_df(product_id: List = None):
    """
    > This function returns a dataframe of all products in the database, or a subset of products if a
    list of product IDs is passed in

    :param product_id: List = None
    :type product_id: List
    :return: A dataframe with all the products in the database.
    """
    query = "SELECT * FROM core_product"

    if product_id:
        query += f" WHERE id IN ({str(set(product_id)).replace('{', '').replace('}', '')})"

    return pd.read_sql(query, connection)

    """
    It takes three dataframes, merges them, groups them, calculates some series, and returns a dataframe

    :param df_product: The product dataframe
    :param df_productsale: DataFrame with the product sales
    :param df_sale: the sales dataframe
    :return: A dataframe with the following columns:
        - client_id
        - product_id
        - quantity
        - income
        - percentage_income
        - percentage_quantity
    """


def get_products_per_clients_df(df_product, df_productsale, df_sale):
    # Merge Dataframes
    df_product = df_product[["id", 'name', 'category_id']]
    df = pd.merge(df_product, df_productsale, left_on="id",
                  right_on="product_id", suffixes=("_product", "_ps"))
    df = pd.merge(df, df_sale, left_on="sale_id",
                  right_on="id", suffixes=("_ps", "_sale"))
    df.drop(columns=['id_product', 'id'], inplace=True)

    # Group DataFrames
    group_by_client_product = df.groupby(
        ['client_id', 'product_id'])  # .groups
    group_by_client = df.groupby(['client_id'])

    # Totals series
    total_client_income = group_by_client['income_ps'].sum()
    total_client_quantity = group_by_client['quantity'].sum()

    # Calculate final series
    group_by_client_product['income_ps'].sum()
    quantity_product = group_by_client_product['quantity'].sum()
    income_product = group_by_client_product['income_ps'].sum()
    client_product_percentage_income = round(
        income_product / total_client_income, 4)
    client_product_percentage_quantity = round(
        quantity_product / total_client_quantity, 4)

    # Create final DF
    d = {'quantity': quantity_product, 'income': income_product, 'percentage_income':
         client_product_percentage_income, 'percentage_quantity': client_product_percentage_quantity}
    return pd.DataFrame(d).reset_index()


def get_category_per_clients_df(df_product, df_productsale, df_sale):
    """
    We merge the dataframes, group them by client and category, calculate the totals, and then calculate
    the percentages

    :param df_product: The product dataframe
    :param df_productsale: DataFrame with the product sales
    :param df_sale: the sales dataframe
    :return: A dataframe with the following columns:
        - client_id
        - category_id
        - quantity
        - income
        - percentage_income
        - percentage_quantity
    """
    # Merge Dataframes
    df_product = df_product[["id", 'name', 'category_id']]
    df = pd.merge(df_product, df_productsale, left_on="id",
                  right_on="product_id", suffixes=("_product", "_ps"))
    df = pd.merge(df, df_sale, left_on="sale_id",
                  right_on="id", suffixes=("_ps", "_sale"))
    df.drop(columns=['id_product', 'id'], inplace=True)

    # Group DataFrames
    group_by_client_category = df.groupby(['client_id', 'category_id'])
    group_by_client = df.groupby(['client_id'])

    # Totals series
    total_client_income = group_by_client['income_ps'].sum()
    total_client_quantity = group_by_client['quantity'].sum()

    # Calculate final series
    category_quantity = group_by_client_category['quantity'].sum()
    category_income = group_by_client_category['income_ps'].sum()
    client_category_percentage_income = round(
        category_income / total_client_income, 4)
    client_category_percentage_quantity = round(
        category_quantity / total_client_quantity, 4)

    # Create final DF
    d_cc = {'quantity': category_quantity, 'income': category_income, 'percentage_income':
            client_category_percentage_income, 'percentage_quantity': client_category_percentage_quantity}
    return pd.DataFrame(d_cc).reset_index()


def get_salesman_per_clients_df(df_product, df_productsale, df_sale):
    """
    > It merges the three dataframes, groups them by client and salesman, and then calculates the
    percentage of income and quantity for each salesman per client

    :param df_product: The product dataframe
    :param df_productsale: Dataframe with the product sales
    :param df_sale: DataFrame with the sales data
    :return: A dataframe with the following columns:
        - client_id
        - salesman_id
        - quantity
        - income
        - percentage_income
        - percentage_quantity
    """
    # Merge Dataframes
    df_product = df_product[["id", 'name', 'category_id']]
    df = pd.merge(df_product, df_productsale, left_on="id",
                  right_on="product_id", suffixes=("_product", "_ps"))
    df = pd.merge(df, df_sale, left_on="sale_id",
                  right_on="id", suffixes=("_ps", "_sale"))
    df.drop(columns=['id_product', 'id'], inplace=True)

    # Group DataFrames
    group_by_client = df.groupby(['client_id'])
    group_by_client_salesman = df.groupby(['client_id', 'salesman_id'])

    # Totals series
    total_client_income = group_by_client['income_ps'].sum()
    total_client_quantity = group_by_client['quantity'].sum()

    # Calculate final series
    salesman_quantity = group_by_client_salesman['quantity'].sum()
    salesman_income = group_by_client_salesman['income_ps'].sum()
    client_salesman_percentage_income = round(
        salesman_income / total_client_income, 4)
    client_salesman_percentage_quantity = round(
        salesman_quantity / total_client_quantity, 4)

    # Create final DF
    d_sc = {'quantity': salesman_quantity, 'income': salesman_income, 'percentage_income':
            client_salesman_percentage_income, 'percentage_quantity': client_salesman_percentage_quantity}
    return pd.DataFrame(d_sc).reset_index()


def get_indicators(client_id):
    df_sales = get_sales_df(client_id)
    df_productsales = get_productsales_df(list(df_sales['id'].values))
    df_product = get_products_df(
        list(set(list(df_productsales['product_id'].values))))

    products_per_client = get_products_per_clients_df(
        df_product, df_productsales, df_sales)
    category_per_client = get_category_per_clients_df(
        df_product, df_productsales, df_sales)
    salesman_per_client = get_salesman_per_clients_df(
        df_product, df_productsales, df_sales)

    client = Client.objects.get(pk=client_id)
    d = client.to_dict()
    d['products'] = {}
    d['categories'] = {}
    d['salesmans'] = {}
    for row in products_per_client.itertuples():
        if not row.product_id in d['products'].keys():
            d['products'][row.product_id] = {
                'name': Product.objects.get(pk=row.product_id).name,
                'quantity': row.quantity,
                'income': row.income,
                'percentage_income': row.percentage_income,
                'percentage_quantity': row.percentage_quantity
            }

    for row in category_per_client.itertuples():
        if not row.category_id in d['categories'].keys():
            d['categories'][row.category_id] = {
                'name': Category.objects.get(pk=row.category_id).name,
                'quantity': row.quantity,
                'income': row.income,
                'percentage_income': row.percentage_income,
                'percentage_quantity': row.percentage_quantity
            }

    for row in salesman_per_client.itertuples():
        if not row.salesman_id in d['salesmans'].keys():
            d['salesmans'][row.salesman_id] = {
                'name': Salesman.objects.get(pk=row.salesman_id).name,
                'quantity': row.quantity,
                'income': row.income,
                'percentage_income': row.percentage_income,
                'percentage_quantity': row.percentage_quantity
            }

    return d

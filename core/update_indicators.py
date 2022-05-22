from core.models import (
    SalesmanIndicators,
    Sale,
    ClientIndicator,
    Client,
    Salesman
)
import pandas as pd
import psycopg2
import os


host = os.getenv("DB_HOST")
dbname = os.getenv("DB_NAME")
user = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")


conn_string = "host={0} user={1} dbname={2} password={3}".format(
    host, user, dbname, password)
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

query_sales = "SELECT * FROM core_sale;"
df = pd.read_sql(query_sales, conn)
df = df[['id', 'income', 'date', 'client_id', 'salesman_id', 'income_currency']]
"""
get total income, average income and how many purchases per client id
"""
dfg = df.groupby(by=['client_id'])


biggest = []
for i in dfg.indices.keys():
    _df = df.loc[df['client_id'] == i]
    _id = _df['id'][_df['income'] == _df['income'].max()]
    if not _id.empty:
        biggest.append(_id.values[0])
biggest

clients_data = {
    'client_id': dfg.indices.keys(),
    'total_income': dfg['income'].sum(),
    'average_income': dfg['income'].mean(),
    'biggest_sale': biggest,
    'purchases': dfg['id'].count(),
    'first_sale': dfg['date'].min(),
    'last_sale': dfg['date'].max()
}

clients_df = pd.DataFrame(clients_data, index=clients_data['client_id'])

"""
get total income, average income and how many purchases per client id
"""
dfg = df.groupby(by=['salesman_id'])


biggest = []
for i in dfg.indices.keys():
    _df = df.loc[df['salesman_id'] == i]
    _id = _df['id'][_df['income'] == _df['income'].max()]
    if not _id.empty:
        biggest.append(_id.values[0])


salesman_data = {
    'salesman_id': dfg.indices.keys(),
    'total_income': dfg['income'].sum(),
    'average_income': dfg['income'].mean(),
    'biggest_sale': biggest,
    'purchases': dfg['id'].count(),
    'first_sale': dfg['date'].min(),
    'last_sale': dfg['date'].max()
}

salesman_df = pd.DataFrame(salesman_data, index=salesman_data['salesman_id'])


l_s = len(Salesman.objects.all())
l_c = len(Client.objects.all())
i_s = 0
i_c = 0

for salesman in salesman_df.itertuples():
    i_s += 1
    print(f'Salesman {i_s} of {l_s}')
    salesman_indicator = SalesmanIndicators.objects.get(
        salesman=Salesman.objects.get(pk=salesman.Index)
    )

    salesman_indicator.purchases = salesman.purchases
    salesman_indicator.money_generated = salesman.total_income
    salesman_indicator.biggest_sale = Sale.objects.get(
        pk=salesman.biggest_sale)
    salesman_indicator.save()

for client in clients_df.itertuples():
    i_c += 1
    print(f'Client {i_c} of {l_c}')
    client_indicator = ClientIndicator.objects.get(
        client=Client.objects.get(pk=client.Index)
    )
    client_indicator.purchases = client.purchases
    client_indicator.money_generated = client.total_income
    client_indicator.biggest_sale = Sale.objects.get(pk=client.biggest_sale)
    client_indicator.save()
print('DONE')

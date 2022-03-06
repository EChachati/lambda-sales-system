import pdb
import pandas as pd
from core.models import *
import requests
import base64
import json
import os


#os.system("rm db.sqlite3")
os.system("python3 manage.py makemigrations")
os.system("python3 manage.py migrate")
"""
user = User(
    email='chachati28@gmail.com',
    name='Edkar',
    identity_card='123456789',
    password='mailto.01'
).save()
"""
token = "7cb314eada11bc3995f57c6d8dd42e795a4d2f2d"
Salesman.objects.all().delete()
Client.objects.all().delete()
Product.objects.all().delete()
Barcode.objects.all().delete()
Category.objects.all().delete()
Sale.objects.all().delete()
ProductSale.objects.all().delete()
SalesmanIndicators.objects.all().delete()
ClientIndicator.objects.all().delete()
User.objects.all().delete()

"""
READ AND CREATE SALESMANS
"""

df_salesman = pd.read_csv('core/csv/salesman.csv', encoding='latin-1', sep='|')
df_salesman['Telef'] = '0' + \
    df_salesman['Telef'].astype('string').str.replace('.0', '', regex=False)
df_salesman['Movil'] = '0' + \
    df_salesman['Movil'].astype(
        'string').str.replace('.0', '', regex=False)
df_salesman.rename(
    columns={
        'Descrip': 'name',
        'Telef': 'phone_1',
        'Movil': 'phone_2',
        'CodVend': 'ide',
        'Direc1': 'address',
        'ID3': 'identity_card'
    }, inplace=True
)
df_salesman = df_salesman[
    ['ide', 'identity_card', 'name', 'phone_1', 'phone_2', 'address']
]
df_salesman.sort_values(by=['ide'], inplace=True)

for index, row in df_salesman.iterrows():
    salesman = Salesman(
        identity_card=row['identity_card'],
        name=row['name'],
        phone_1=row['phone_1'],
        phone_2=row['phone_2'],
        address=row['address']
    )
    salesman.save()
    indicators = SalesmanIndicators.objects.create(salesman=salesman)
    indicators.save()

print('Salesman created')

"""
READ AND CREATE CLIENTS
"""
df_clients = pd.read_csv('core/csv/clients.csv',
                         encoding='latin-1', sep='|', engine='python')
df_clients.rename(columns={
    'CodClie': 'identity_card',
    'Descrip': 'name',
    'Telef': 'phone_1',
    'Movil': 'phone_2',
}, inplace=True)
df_clients['identity_card'] = df_clients['identity_card'].apply(
    lambda x: x.upper().replace('J-', 'J').replace('V-', 'V'))
df_clients['address'] = df_clients['Direc1'] + '\n\n' + df_clients['Direc2']
df_clients['name'] = df_clients['name'].apply(
    lambda x: x.upper().replace('Ï¿½', 'Ñ'))
df_clients[['identity_card', 'name', 'phone_1', 'phone_2', 'address']]

for i, row in df_clients.iterrows():
    client = Client(
        identity_card=row['identity_card'],
        name=row['name'],
        phone=row['phone_1'],
        address=row['address']
    )
    client.save()
    indicators = ClientIndicator.objects.create(client=client)
    indicators.save()
print('Clients created')

"""
READ AND CREATE CATEGORIES
"""
df_category = pd.read_csv('core/csv/category.csv', encoding='latin-1', sep='|')
df_category.rename(columns={
    'CodInst': '_id',
    'Descrip': 'name',
}, inplace=True)
df_category['name'] = df_category['name'].apply(lambda x: x.upper().replace('A-', '').replace('B-', '').replace(
    'C-', '').replace('1-', '').replace('2-', '').replace('3-', '').replace('4-', '').replace('5-', '').strip())
df_category[['_id', 'name']]

for i, row in df_category.iterrows():
    category = Category(
        id=row['_id'],
        name=row['name']
    )
    category.save()
print('Categories created')

"""
READ AND CREATE PRODUCTS
"""
df_products = pd.read_csv('core/csv/products.csv', encoding='latin-1', sep='|')
df_prices = pd.read_csv('core/csv/products_price.csv',
                        encoding='latin-1', sep='|')
df_images = pd.read_csv('core/csv/products_image.csv',
                        encoding='latin-1', sep='|')

# Products CSV

df_products.rename(columns={
    'CodProd': '_id',
    'Descrip': 'name',
    'Descrip2': 'description',
    'CodInst': 'category_id',
    'Marca': 'brand',
    'Unidad': 'presentation'}, inplace=True)

df_products['name'] = df_products['name'].apply(lambda x: x.upper())
df_products['description'] = df_products['description'].apply(
    lambda x: str(x).capitalize())
df_products['brand'] = df_products['brand'].apply(
    lambda x: str(x).capitalize())
df_products['presentation'] = df_products['presentation'].apply(
    lambda x: str(x).upper())
df_products['category_id'] = df_products['category_id'].apply(
    lambda x: str(x).replace('.0', ''))
df_products = df_products[['_id', 'name', 'description',
                           'category_id', 'brand', 'presentation']]

# Prices CSV

df_prices.rename(columns={
    'CodProd': '_id',
    'Costo_USD': 'cost',
    'Precio_1': 'price_1',
    'Precio_2': 'price_2',
    'Precio_3': 'price_3', }, inplace=True)

# Images CSV

df_images.rename(columns={
    'CodProd': '_id',
    'Imagen': 'image'}, inplace=True)

# Merge Data
df_products_clean = pd.merge(df_products, df_prices, how='outer', on='_id')
df_products_clean = df_products_clean[(df_products_clean['name'].notnull())]
df_products_clean = pd.merge(
    df_products_clean, df_images, how='outer', on='_id')

# Clean NAN cost of dataframe
df_products_clean['cost'] = df_products_clean['cost'].fillna(0)
df_products_clean['price_1'] = df_products_clean['price_1'].fillna(0)
df_products_clean['price_2'] = df_products_clean['price_2'].fillna(0)
df_products_clean['price_3'] = df_products_clean['price_3'].fillna(0)

print('Products cleaned')

for i, row in df_products_clean.iterrows():

    # Load Image in IMGBB
    data = row.image
    url = "https://api.imgbb.com/1/upload?key=77643199c4393578689646652b98080a"
    if type(data) != 'float':  # NaN
        image_url = 'https://i.ibb.co/SrMrfyV/pngwing-com.png'
    else:
        response = requests.post(url, data={'image': data})
        image_url = json.loads(response.text)['data']['image']['url']

    # Create Product
    product = Product(
        # code=row['_id'],
        name=row['name'],
        description=row['description'],
        # Category.objects.get(pk=row['category_id']),
        category_id=row['category_id'],
        brand=row['brand'],
        presentation=row['presentation'],
        price_1=row['price_1'],
        price_2=row['price_2'],
        price_3=row['price_3'],
        cost=row['cost'],
        image=image_url
    )
    product.code = row['_id']
    # product.save()
    try:
        product.save()
    except:
        print('Product not saved')
        print(product.name)

none_product = Product.objects.create(code='none', name='NONE', category=Category.objects.get(
    pk=1056), brand='NONE', presentation='NAN')
none_product.save()

print('products created')

for i in range(1, Product.objects.count()):
    print(i)
    print(Product.objects.get(pk=i))


"""
Create Barcodes
"""

df_barcodes = pd.read_csv('core/csv/codebars.csv', encoding='latin-1', sep='|')
df_barcodes.rename(columns={
    'CodProd': 'product',
    'CodAlte': 'code'}, inplace=True)

for i, row in df_barcodes.iterrows():
    if row['product'] != row['code']:
        barcode = Barcode(
            product=Product.objects.get(code=row['product']),
            code=row['code']
        )
        barcode.save()

print('Barcodes created')

"""
Create Sales
"""
df_sales = pd.read_csv('core/csv/sales.csv', encoding='latin-1', sep='|')
df_sales.rename(columns={
    'NumeroD': '_id',
    'CodClie': 'client',
    'CodVend': 'salesman',
    'FechaE': 'date',
    'MtoTotal': 'income'
}, inplace=True)
df_sales['date'] = pd.to_datetime(df_sales['date'], format='%Y-%m-%d')
df_sales['salesman'] = df_sales['salesman'].apply(
    lambda x: str(x).replace('.0', ''))
df_sales['client'] = df_sales['client'].apply(
    lambda x: str(x).upper().replace('J-', 'J').replace('V-', 'V'))

nan = df_sales['salesman'].unique()[14]
df_sales = df_sales[df_sales['salesman'] != nan]


df_sales = df_sales[['_id', 'client', 'salesman', 'date', 'income']]

for i, row in df_sales.iterrows():
    try:
        sale = Sale(
            id=row['_id'],
            client=Client.objects.get(identity_card=row['client']),
            salesman=Salesman.objects.get(pk=row['salesman']),
            date=row['date'],
            income=row['income']
        )
        sale.save()
    except:
        print(f'Failed register of Sale at {row["_id"]} ')
        sale = Sale(
            id=row['_id'],
            client=Client.objects.get(identity_card=row['client']),
            salesman=Salesman.objects.get(pk=row['salesman']),
            date=row['date'],
            income=row['income']
        )
        sale.save()
print('Sales created')

"""
Create Products Sales
"""

df_ps = pd.read_csv(
    'core/csv/product_sale.csv', encoding='latin-1', sep='|', dtype='str')
df_ps.rename(columns={
    'CodItem': 'product',
    'NumeroD': 'sale',
    'Cantidad': 'quantity',
    'TotalItem': 'income'
}, inplace=True)
# df_ps = df_ps[['product', 'sale', 'quantity', 'income']]
for i, row in df_ps.iterrows():
    try:
        # print(row)
        product = Product.objects.get(code=row['product'])
        sale = Sale.objects.get(id=row['sale'])

        product_sale = ProductSale(
            # row['product'],  # Product.objects.get(id=row['product']),
            product_id=product.id,
            sale_id=sale.id,  # row['sale'],
            quantity=row['quantity'],
            income=row['income']
        )
        product_sale.save()
    except Product.DoesNotExist:
        print(
            f'Failed register of ProductSale at {i}. PRODUCT DOES NOT EXIST'
        )
        """
        Create Product if doesn't exists
        """
        sale = Sale.objects.get(id=row['sale'])
        product_sale = ProductSale(
            # row['product'],  # Product.objects.get(id=row['product']),
            product_id=none_product.id,
            sale_id=sale.id,  # row['sale'],
            quantity=row['quantity'],
            income=row['income']
        )
        product_sale.save()

    except Sale.DoesNotExist:
        print(
            f'Failed register of ProductSale at {i}. SALE DOES NOT EXIST')

print('Products Sales created')

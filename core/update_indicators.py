from core.models import (
    SalesmanIndicators,
    Sale,
    ClientIndicator,
    Client,
    Salesman
)

print('Updating indicators...')

sales = Sale.objects.all()
salesmans = Salesman.objects.all()
clients = Client.objects.all()
l = len(sales)
i = 0

for salesman in salesmans:
    salesman_indicator = SalesmanIndicators.objects.get(pk=salesman)
    salesman_indicator.purchases = 0
    salesman_indicator.money_generated = 0
    salesman_indicator.save()

for client in clients:
    client_indicator = ClientIndicator.objects.get(pk=client)
    client_indicator.purchases = 0
    client_indicator.money_generated = 0
    client_indicator.save()


for sale in sales:
    salesman = sale.salesman
    client = sale.client
    salesman_indicators = SalesmanIndicators.objects.get(salesman=salesman)
    client_indicators = ClientIndicator.objects.get(client=client)
    i += 1
    print(f'Processing sale #{sale.id} indicators... ({i}/{l})')

    salesman_indicators.purchases += 1
    salesman_indicators.money_generated += sale.income

    if not salesman_indicators.biggest_sale or sale.income > salesman_indicators.biggest_sale.income:
        salesman_indicators.biggest_sale = sale

        print(f'New biggest sale for Salesman: {salesman.name}!')

    client_indicators.purchases += 1
    client_indicators.money_generated += sale.income

    if not client_indicators.biggest_sale or sale.income > client_indicators.biggest_sale.income:
        client_indicators.biggest_sale = sale
        print(f'New biggest sale for Client: {client.name}!')

    salesman_indicators.save()
    client_indicators.save()

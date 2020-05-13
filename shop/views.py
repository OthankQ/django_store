from django.shortcuts import render

from django.http import HttpResponse
from .models import User, Item
import json

def GetPostUser(request):
    if request.method == 'GET':

        # Query for all Users
        Users = User.objects.all().order_by().values()

        # Create empty array to store data
        data = [None] * len(Users)

        # For each entry, create a dictionary and insert it into data array
        for i in range(0, len(Users)):
            data[i] = {'user_id': Users[i]['user_id'], 'user_name': Users[i]
                       ['name'], 'phone': Users[i]['phone_number']}

        # Convert python dictionary to passable json data
        data = json.dumps(data)

        # Return the queried and converted data
        return HttpResponse(data, content_type='application/json')

    elif request.method == 'POST':

        data = json.loads(request.body)
        user_id = data['user_id']
        user_name = data['user_name']
        phone = data['phone_number']
        password = data['password']
        etc = data['etc']

        parsed_data = models.User(
            user_id=user_id, name=user_name, password=password, phone_number=phone, etc=etc)

        parsed_data.save()

        print('User has been added successfully')


def GetPostItem(request):
    if request.method == 'GET':

        Items = Item.objects.all().order_by().values()

        data = [None] * len(Items)

        for i in range(0, len(Items)):

            data[i] = {'item_id': Items[i]['item_id'], 'item_name': Items[i]
                       ['name'], 'price': str(Items[i]['price']), 'stock': Items[i]['stock']}

        data = json.dumps(data)

        return HttpResponse(data, content_type='application/json')

    elif request.method == 'POST':

        data = json.loads(request.body)
        item_id = data['item_id']
        name = data['name']
        desc = data['desc']
        price = data['price']
        image_id = data['image_id']
        stock = data['stock']

        parsed_data = models.Item(
            item_id=item_id, name=name, desc=desc, password=password, phone_number=phone, etc=etc)

        parsed_data.save()

        print('Item has been added successfully')


def GetPostInvoice(request):
    if request.method == 'GET':

        Invoices = Item.objects.all().order_by().values()

        data = [None] * len(Invoices)

        for i in range(0, len(Invoices)):

            data[i] = {'invoice_id': Items[i]['invoice_id'], 'user_id': Items[i]
                       ['user_id'], 'date': Items[i]['date'], 'status': Items[i]['status']}

        data = json.dumps(data)

        return HttpResponse(data, content_type='application/json')

    elif request.method == 'POST':

        data = json.loads(request.body)
        invoice_id = data['invoice_id']
        user_id = data['user_id']
        date = data['date']
        status = data['status']

        parsed_data = models.Item(
            invoice_id=invoice_id, user_id=user_id, date=date, status=status)

        parsed_data.save()

        print('Invoice has been added successfully')


def GetPostLineItem(request):

    if request.method == 'GET':

        LineItems = Item.objects.all().order_by().values()

        data = [None] * len(LineItems)

        for i in range(0, len(LineItems)):

            data[i] = {'line_item_id': Items[i]['line_item_id'], 'item_id': Items[i]['item_id'], 'line_item_name': Items[i]
                       ['line_item_name'], 'line_item_price': str(Item[i]['line_item_price']), 'quantity': Item[i]['quantity']}

        data = json.dumps(data)

        print('Successfully fetched line items')

        return HttpResponse(data, content_type='application/json')

    elif request.method == 'POST':

        data = json.loads(request.body)
        line_item_id = data['line_item_id']
        item_id = data['item_id']
        line_item_name = data['line_item_name']
        line_item_price = data['line_item_price']
        quantity = data['quantity']

        parsed_data = models.Item(
            line_item_id=line_item_id, item_id=item_id, line_item_name=line_item_name, line_item_price=line_item_price, quantity=quantity)

        parsed_data.save()

        print('LineItem has been added successfully')

from django.shortcuts import render

from django.http import HttpResponse
from .models import User, Item, Invoice, LineItem
import json


def UpdateLineItemPrice(quantity, item_id):
    # query for that specific line item using item_id
    # print('up to here')
    print(item_id)
    item = Item.objects.filter(item_id=item_id).values()
    print(item)

    # query for current item price of that item and store it in a variable
    current_item_price = item[0]['price']

    # calculate the total price of the line item and store it in a variable
    calculated_line_item_price = current_item_price * quantity
    print(calculated_line_item_price)
    # Save that price into the existing row
    return calculated_line_item_price


def GetPostUser(request):
    if request.method == 'GET':

        # When query string exists
        if request.GET.get('id'):

            # Extract the parameter and save it to requested_id
            requested_id = request.GET.get('id')

            # Query for the row that matches the criteria
            requested_user = User.objects.filter(user_id=requested_id).values()

            # Create a dict with the values retrieved from the queried data point
            data = {'user_id': requested_user[0]['user_id'],
                    'name': requested_user[0]['name'], 'phone': requested_user[0]['phone_number']}

            # Convet the data to transferable json
            data = json.dumps(data)

            # Return that data
            return HttpResponse(data, content_type='application/json')

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

        parsed_data = User(
            user_id=user_id, name=user_name, password=password, phone_number=phone)

        parsed_data.save()

        print('User has been added successfully')

        return HttpResponse('success', content_type='text/plain')


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
        # desc = data['desc']
        price = data['price']
        # image_id = data['image_id']
        stock = data['stock']

        parsed_data = Item(
            item_id=item_id, name=name, price=price, stock=stock)

        parsed_data.save()

        print('Item has been added successfully')

        return HttpResponse('success', content_type='text/plain')


def GetPostInvoice(request):
    if request.method == 'GET':

        Invoices = Invoice.objects.all().order_by().values()

        data = [None] * len(Invoices)

        for i in range(0, len(Invoices)):

            data[i] = {'invoice_id': Invoices[i]['invoice_id'],
                       'user_id': Invoices[i]['user_id'], 'date': str(Invoices[i]['date']),
                       'status': Invoices[i]['status_id']}

        data = json.dumps(data)

        return HttpResponse(data, content_type='application/json')

    elif request.method == 'POST':

        data = json.loads(request.body)
        invoice_id = data['invoice_id']
        user_id = data['user_id']
        date = data['date']
        status = data['status']

        parsed_data = Invoice(
            invoice_id=invoice_id, user_id=user_id, date=date, status=status)

        parsed_data.save()

        print('Invoice has been added successfully')

        return HttpResponse('success', content_type='text/plain')


def GetPostLineItem(request):

    if request.method == 'GET':

        LineItems = LineItem.objects.all().order_by().values()

        data = [None] * len(LineItems)

        for i in range(0, len(LineItems)):

            data[i] = {'line_item_id': LineItems[i]['line_item'], 'invoice_id': LineItems[i]['invoice_id'], 'item_id': LineItems[i]
                       ['item_id'], 'line_item_price': float(LineItems[i]['line_item_price']), 'quantity': LineItems[i]['quantity']}

        data = json.dumps(data)

        print('Successfully fetched line items')

        return HttpResponse(data, content_type='application/json')

    elif request.method == 'POST':
        data = json.loads(request.body)
        invoice_id = data['invoice_id']
        # line_item_id = data['line_item_id']
        item_id = data['item_id']
        quantity = data['quantity']

        line_item_price = UpdateLineItemPrice(quantity, item_id)

        parsed_data = LineItem(
            invoice_id=invoice_id, item_id=item_id, line_item_price=line_item_price, quantity=quantity)

        # problem: if I try to assign invoice_id, it doesn't let me because it is not an instance of an Invoice.
        # However if I get rid of it, I can't add it either because in the lineitem model, invoice_id is a foreign key and I cannot have it as null
        parsed_data.save()

        print('LineItem has been added successfully')

        return HttpResponse('success', content_type='text/plain')

from django.shortcuts import render

from django.http import HttpResponse
from .models import UserAdditionalInfo, Item, Invoice, LineItem, InvoiceStatus
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
import json


def UpdateLineItemPrice(quantity, item_id):
    # query for that specific line item using item_id
    item = Item.objects.filter(item_id=item_id).values()

    # query for current item price of that item and store it in a variable
    current_item_price = item[0]['price']

    # calculate the total price of the line item and store it in a variable
    calculated_line_item_price = current_item_price * quantity
    print(calculated_line_item_price)
    # Save that price into the existing row
    return calculated_line_item_price


def GetUserInfo(request):
    if request.method == 'GET':
        print(request.session)

        # When query string exists
        if request.GET.get('username'):

            # Extract the parameter and save it to requested_id
            requested_username = request.GET.get('username')

            # Query for the row that matches the criteria
            requested_user = User.objects.get(
                username=requested_username)

            if requested_user:

                # Create a dict with the values retrieved from the queried data point
                data = {'id': requested_user.id,
                        'username': requested_user.username, 'date_joined': str(requested_user.date_joined), 'last_login': str(requested_user.last_login)}

                # Convet the data to transferable json
                data = json.dumps(data)

                # Return that data
                return HttpResponse(data, content_type='application/json')

            else:

                return HttpResponse('-1', content_type='text/plain')

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

    # Registration


def RegisterUser(request):

    data = json.loads(request.body)

    username = data['username']
    email = data['email']
    password = data['password']

    new_user = User.objects.create_user(username, email, password)
    new_user.save()

    print('User has been registered successfully')

    # Create Cart

    # Query for the id of the just created user's id number
    new_user_value = User.objects.filter(username=username).values()
    new_user_id = new_user_value[0]['id']
    new_user_registered_time = new_user_value[0]['date_joined']

    new_cart_status = InvoiceStatus.objects.filter(status='cart')[0]

    # Use that id number to create new invoice(cart)
    new_cart = Invoice(user=new_user, status=new_cart_status,
                       date=new_user_registered_time)

    new_cart.save()

    return HttpResponse('0', content_type='text/plain')


def UserLogin(request):
    try:
        data = json.loads(request.body)

        username = data['username']
        password = data['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:

            # Save user info to session

            login(request, user)
            return HttpResponse('0', content_type='text/plain')

        else:
            return HttpResponse('-1', content_type='text/plain')
    except(KeyError):
        print("Key error")
        return HttpResponse('-1', content_type='text/plain')


# User Logout
def UserLogout(request):
    logout(request)
    return HttpResponse('0', content_type='text/plain')


# Retrieve or add Item data
def GetPostItem(request):

    if request.method == 'GET':

        # If user is searching based on users
        if request.GET.get('user_id'):

            requested_user_id = request.GET.get('user_id')

            Items = list(Item.objects.filter(
                user_id=requested_user_id).values())

            try:

                if Items:

                    data = [None] * len(Items)

                    for i in range(0, len(Items)):

                        data[i] = {'item_id': Items[i]['item_id'], 'item_name': Items[i]['name'], 'price':
                                   str(Items[i]['price']), 'stock': Items[i]['stock']}

                    print(data)

                    data = json.dumps(data)

                    return HttpResponse(data, content_type='text/plain')

            except(KeyError):

                return HttpResponse('-1', content_type='text/plain')

        # If a user is searching with item name:
        elif request.GET.get('item_id'):

            requested_item_id = request.GET.get('item_id')
            Items = list(Item.objects.filter(
                item_id=requested_item_id).values())

            try:

                if Items:

                    data = [None] * len(Items)

                    for i in range(0, len(Items)):

                        data[i] = {'item_id': Items[i]['item_id'], 'item_name': Items[i]['name'], 'price':
                                   str(Items[i]['price']), 'stock': Items[i]['stock']}

                    print(data)

                    data = json.dumps(data)

                    return HttpResponse(data, content_type='text/plain')

            except(KeyError):

                return HttpResponse('-1', content_type='text/plain')

        Items = Item.objects.order_by().values()

        data = [None] * len(Items)

        for i in range(0, len(Items)):

            data[i] = {'item_id': Items[i]['item_id'], 'item_name': Items[i]
                       ['name'], 'price': str(Items[i]['price']), 'stock': Items[i]['stock']}

        data = json.dumps(data)

        return HttpResponse(data, content_type='application/json')

    elif request.method == 'POST':

        if not request.user.is_authenticated:

            return HttpResponse('-1', content_type='text/plain')

        # Parse in the data sent by user
        data = json.loads(request.body)

        # Check if there are any existing with matching item_id
        original_entry = Item.objects.filter(
            item_id=data['item_id']).values()

        # Update
        if len(original_entry) > 0:

            indexable_original_entry = list(original_entry)[0]

            if 'stock' in data.keys():
                indexable_original_entry['stock'] = data['stock']

            if 'name' in data.keys():
                indexable_original_entry['name'] = data['name']

            if 'desc' in data.keys():
                indexable_original_entry['desc'] = data['desc']

            if 'price' in data.keys():
                indexable_original_entry['price'] = data['price']

            stock = indexable_original_entry['stock']
            name = indexable_original_entry['name']
            item_id = indexable_original_entry['item_id']
            price = indexable_original_entry['price']
            user_id = request.user.id

            parsed_data = Item(
                item_id=item_id, stock=stock, name=name, price=price, user_id=user_id)

        # Post
        else:

            item_id = data['item_id']
            name = data['name']
            user_id = request.user.id
            # desc = data['desc']
            price = data['price']
            # image_id = data['image_id']
            stock = data['stock']

            parsed_data = Item(
                item_id=item_id, name=name, price=price, stock=stock)

        parsed_data.save()

        print('Item has been added successfully')

        return HttpResponse('0', content_type='text/plain')


# Retreive or add invoice data
def GetPostInvoice(request):
    if request.method == 'GET':
        # BLAIR CODE!!!
        if request.user.is_authenticated:
            # Check if this dude is logged in
            requested_invoices = Invoice.objects.filter(
                user_id=request.user.id)
            # Query for all the invoice under this user's id
            invoice_array = list()
            for invoice in requested_invoices:
                data = {'invoice_id': invoice.invoice_id,
                        'user_id': invoice.user_id, 'date_created': str(invoice.date), 'status': str(invoice.status)}
                # Convert the data to transferable json
                # data = json.dumps(data)
                invoice_array.append(data)
            invoice_json = json.dumps(invoice_array)
            return HttpResponse(invoice_json, content_type='application/json')

        else:
            # User is not logged in
            return HttpResponse('-1', content_type='text/plain')

        # When there is a specified query string
        if request.GET.get('id'):
            requested_user_id = request.GET.get('id')
            requested_invoices = Invoice.objects.filter(
                user_id=requested_user_id)
            print(requested_invoices)

            if requested_invoices:

                invoice_array = list()

                for invoice in requested_invoices:

                    data = {'invoice_id': invoice.invoice_id,
                            'user_id': invoice.user_id, 'date_created': str(invoice.date), 'status': str(invoice.status)}

                    # Convert the data to transferable json
                    # data = json.dumps(data)

                    invoice_array.append(data)

                print(invoice_array)

                invoice_json = json.dumps(invoice_array)

                return HttpResponse(invoice_json, content_type='application/json')

            else:

                return HttpResponse('-1', content_type='text/plain')

        Invoices = Invoice.objects.all().order_by().values()

        data = [None] * len(Invoices)

        for i in range(0, len(Invoices)):

            data[i] = {'invoice_id': Invoices[i]['invoice_id'],
                       'user_id': Invoices[i]['user_id'], 'date': str(Invoices[i]['date']),
                       'status': Invoices[i]['status_id']}

        data = json.dumps(data)

        return HttpResponse(data, content_type='application/json')

    elif request.method == 'POST':

        try:
            data = json.loads(request.body)
            invoice_id = data['invoice_id']
            user_id = data['user_id']
            date = data['date']
            status = data['status']

            parsed_data = Invoice(
                invoice_id=invoice_id, user_id=user_id, date=date, status=status)

            parsed_data.save()

            print('Invoice has been added successfully')

            return HttpResponse('0', content_type='text/plain')

        except(KeyError):
            print("Key error")
            return HttpResponse('-1', content_type='text/plain')


# Retrieve or add lineitem data
def GetPostLineItem(request):

    if request.method == 'GET':

        try:

            LineItems = LineItem.objects.all().order_by().values()

            data = [None] * len(LineItems)

            for i in range(0, len(LineItems)):

                data[i] = {'line_item_id': LineItems[i]['line_item'], 'invoice_id': LineItems[i]['invoice_id'], 'item_id': LineItems[i]
                           ['item_id'], 'line_item_price': float(LineItems[i]['line_item_price']), 'quantity': LineItems[i]['quantity']}

            data = json.dumps(data)

            print('Successfully fetched line items')

            return HttpResponse(data, content_type='application/json')

        except:

            return HttpResponse('-1', content_type='text/plain')

    elif request.method == 'POST':

        try:
            # Retrieve data from user request

            data = json.loads(request.body)

            # Check if there is already an entry with  line_item_id of the data sent by the user
            # If there is already one, query for that data

            # Cart

            original_entry = LineItem.objects.filter(
                item_id=data['item_id']).values()

            # Update
            if len(original_entry) > 0:

                indexable_original_entry = list(original_entry)[0]

                if 'quantity' in data.keys():

                    indexable_original_entry['quantity'] = data['quantity']

                line_item = indexable_original_entry['line_item']
                quantity = indexable_original_entry['quantity']
                item_id = indexable_original_entry['item_id']
                invoice_id = indexable_original_entry['invoice_id']

                line_item_price = UpdateLineItemPrice(quantity, item_id)

                parsed_data = LineItem(
                    line_item=line_item, invoice_id=invoice_id, item_id=item_id, line_item_price=line_item_price, quantity=quantity)

            # Post

            # There is no line_item with the same line_item_id

            else:
                invoice_id = data['invoice_id']
                # line_item_id = data['line_item_id']
                item_id = data['item_id']
                quantity = data['quantity']

                line_item_price = UpdateLineItemPrice(quantity, item_id)

                parsed_data = LineItem(
                    invoice_id=invoice_id, item_id=item_id, line_item_price=line_item_price, quantity=quantity)

            parsed_data.save()

            print('LineItem has been added successfully')

            return HttpResponse('0', content_type='text/plain')

        except(KeyError):
            print("Key error")
            return HttpResponse('-1', content_type='text/plain')

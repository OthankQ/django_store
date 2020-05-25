from django.shortcuts import render

from django.http import HttpResponse
from .models import UserAdditionalInfo, Item, Invoice, LineItem, InvoiceStatus, LineItemStatus
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from datetime import datetime
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

    try:

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

    except(KeyError):

        return HttpResponse('-1', content_type='text/plain')


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
def GetPostCart(request):

    if not request.user.is_authenticated:

        return HttpResponse('-1', content_type='text/plain')

    if request.method == 'GET':

        try:

            # Query for the 'cart' status invoice
            cart_status = InvoiceStatus.objects.filter(id=1).values()[0]

            cart = Invoice.objects.filter(
                status_id=cart_status, user_id=request.user.id).values()
            # print(cart)

            lineItems = LineItem.objects.all().order_by().values()

            data = [None] * len(lineItems)

            for i in range(0, len(lineItems)):

                data[i] = {'line_item_id': lineItems[i]['line_item'], 'invoice_id': lineItems[i]['invoice_id'], 'item_id': lineItems[i]
                           ['item_id'], 'line_item_price': float(lineItems[i]['line_item_price']), 'quantity': lineItems[i]['quantity']}

            data = json.dumps(data)

            print('Successfully fetched line items')

            return HttpResponse(data, content_type='application/json')

        except(KeyError):

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

                # Query for this user's cart

                cart = Invoice.objects.filter(
                    status_id=1, user_id=request.user.id).values()[0]

                invoice_id = cart['invoice_id']
                # line_item_id = data['line_item_id']
                item_id = data['item_id']
                quantity = data['quantity']

                line_item_price = UpdateLineItemPrice(quantity, item_id)

                parsed_data = LineItem(status_id=1,
                                       invoice_id=invoice_id, item_id=item_id, line_item_price=line_item_price, quantity=quantity)

            parsed_data.save()

            print('LineItem has been added successfully')

            return HttpResponse('0', content_type='text/plain')

        except(KeyError):

            print("There was a key error")
            return HttpResponse('-1', content_type='text/plain')


def SubmitCart(request):

    # Check if a user is logged in
    if not request.user.is_authenticated:

        return HttpResponse('-1', content_type='text/plain')

    # Query and check if there are more item stocks than requested quantity of the line item

    # Query and change the status for every line item that was in the cart to 2

    # Get the id of current cart
    current_cart_id = Invoice.objects.filter(
        status_id=1, user_id=request.user.id).values()[0]['invoice_id']

    line_items_in_cart = LineItem.objects.filter(
        invoice=current_cart_id).values()

    for line_item in line_items_in_cart:

        # Query for the item of the line_item
        item_id = line_item['item_id']
        quantity = line_item['quantity']

        item_stock = Item.objects.filter(item_id).values()[0]['stock']
        # If there are more stocks than requested quantity, go through with changing the status

        # If there are fewer stocks than requested quantity, stop the whole process of updating the line_item status, return -1 with a notification to the user
        if item_stock < quantity:

            # Create and save notification item for this user

            return HttpResponse('-1', content_type='text/plain')

        line_item_id = line_item['line_item']
        line_item_price = line_item['line_item_price']
        # quantity = line_item['quantity']
        invoice_id = line_item['invoice_id']
        # item_id = line_item['item_id']
        status_id = 2

        submitted_item = LineItem(line_item=line_item_id, line_item_price=line_item_price,
                                  quantity=quantity, invoice_id=invoice_id, item_id=item_id, status_id=status_id)

        submitted_item.save()

     # Query for the invoice with status of cart(1) and switch the status to paid(2)

    cart = Invoice.objects.filter(
        status_id=1, user_id=request.user.id).values()[0]

    submitted_cart = Invoice(
        date=cart['date'], invoice_id=cart['invoice_id'], status_id=2, user_id=request.user.id)

    submitted_cart.save()

    # Create a new cart under this user's user_id

    new_cart = Invoice(user=request.user, status_id=1,
                       date=datetime.now())

    new_cart.save()

    return HttpResponse('0', content_type='text/plain')


# Method that is fired when seller puts an item into a locker
def PutInLocker(request):

    # Check if seller is logged in

    if not request.user.is_authenticated:

        return HttpResponse('-1', content_type='text/plain')

    # line item id will be posted by the seller

    data = json.loads(request.body)
    line_item = data['line_item']

    # check if the user that is associated with the line_item and the logged in user is the same user

    line_item_seller_id = LineItem.objects.filter(
        user=request.user.id).values()[0]['user']

    # If the requested item's seller is not the same as user, exit with -1

    if not line_item_seller_id == request.user.id:

        return HttpResponse('-1', cotent_type='text/plain')

    # With the line item id, query for the line item and change its status from 2 to 3

    line_item = LineItem.objects.filter(line_item=line_item).values()[0]

    # line_item_id = line_item['line_item']
    # user = line_item['user']
    # line_item_price = line_item['line_item_price']
    # quantity = line_item['quantity']
    # invoice_id = line_item['invoice_id']
    # item_id = line_item['item_id']
    # status_id = 3a
    line_item['status_id'] = LineItemStatus.objects.filter(id=3)[0]

    # item_put_in_locker = LineItem(line_item=line_item_id, line_item_price=line_item_price,
    #   quantity=quantity, invoice_id=invoice_id, item_id=item_id, status_id=status_id)

    line_item.save()

    return HttpResponse('0', content_type='text/plain')


# Method to check of other lineitems in that spcific data are all picked up or not
# This method will be run everytime an order has been picked up by a buyer

def CheckLineItemStatus(invoice_id):

    ready_for_completion = True

    # Query for that invoice this line_item is in

    # invoice = Invoice.objects.filter(invoice_id=invoice_id).values()[0]

    # Using that invoice_id, query all the line_items in that invoice

    other_line_items = LineItem.objects.filter(invoice_id=invoice_id).values()

    # Loop through all the queried line items and see if their statuses are all 3

    for line_item in other_line_items:

        if not line_item['status_id'] == 2:

            ready_for_completion = False

    # If so, switch the status of that invoice to 3

    if ready_for_completion:

        invoice = Invoice.objects.filter(invoice_id=invoice_id).values()[0]

        invoice_id = invoice['invoice_id']
        date = invoice['date']
        status_id = 3
        user_id = invoice['user_id']

        new_status_invoice = Invoice(
            invoice_id=invoice_id, date=date, status_id=status_id, user_id=user_id)

        new_status_invoice.save()


def PickUpItem(request):

    # Check if buyer is logged in

    if not request.user.is_authenticated:

        return HttpResponse('-1', content_type='text/plain')

    # line item id will be posted by the buyer

    data = json.loads(request.body)
    line_item = data['line_item']

    # check if the user that is associated with the line_item(buyer) and the logged in user is the same user

    line_item_buyer_id = LineItem.objects.filter(
        user=request.user.id).values()[0]['user']

    # If the requested item's buyer is not the same as user, exit with -1
    # I imagine this part of the code is where it will be decided whether the buyer will be able to open the locker door or not

    if not line_item_buyer_id == request.user.id:

        return HttpResponse('-1', cotent_type='text/plain')

    # With the line item id, query for the line item and change its status from 2 to 3

    line_item = LineItem.objects.filter(line_item=line_item).values()

    line_item_id = line_item['line_item']
    user = line_item['user']
    line_item_price = line_item['line_item_price']
    quantity = line_item['quantity']
    invoice_id = line_item['invoice_id']
    item_id = line_item['item_id']
    status_id = 4

    item_picked_up = LineItem(line_item=line_item_id, line_item_price=line_item_price,
                              quantity=quantity, invoice_id=invoice_id, item_id=item_id, status_id=status_id)

    item_picked_up.save()

    # This is where method that checks if there are other line items in invoice that are incompleted
    CheckLineItemStatus(invoice_id)

    return HttpResponse('0', content_type='text/plain')

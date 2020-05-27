from django.shortcuts import render

from django.http import HttpResponse
from .models import UserAdditionalInfo, Item, Invoice, LineItem, InvoiceStatus, LineItemStatus, Notification
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from datetime import datetime
import json


def GetUserInfo(request):
    if request.method == 'GET':

        # When query string exists
        if request.GET.get('username'):

            # Extract the parameter and save it to requested_id
            requested_username = request.GET.get('username')

            # Query for the data that matches the criteria
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

            # When the query matched no data
            else:

                return HttpResponse('-5', content_type='text/plain')

        # Query for all Users when there were no params given
        Users = User.objects.all().order_by()

        # Create empty array to store data
        data = [None] * len(Users)

        # For each entry, create a dictionary and insert it into data array
        for i in range(0, len(Users)):
            data[i] = {'user_id': Users[i].user_id, 'user_name': Users[i]
                       .name, 'phone': Users[i].phone_number}

        # Convert python dictionary to passable json data
        data = json.dumps(data)

        # Return the queried and converted data
        return HttpResponse(data, content_type='application/json')


# Registration
def RegisterUser(request):

    # Load passed json into python dict
    data = json.loads(request.body)

    try:

        email = data['email']
        # Check if user has entered wrong datatype for email
        if not type(email) == str:
            return HttpResponse('-7', content_type='text/plain')

        # Check if there is a duplicate email address

        # Query for any user with the entered email address
        existing_user_with_same_email = User.objects.get(email=email)

        # Exit the method and return a message if there are any users with that email already
        if existing_user_with_same_email:
            return HttpResponse('-8', content_type='text/plain')

        username = data['username']
        # Check if user has entered wrong datatype for username
        if not type(username) == str:
            return HttpResponse('-7', content_type='text/plain')

        password = data['password']

        new_user = User.objects.create_user(username, email, password)
        new_user.save()

        print('User has been registered successfully')

        # Create Cart

        # Query for the id of the just created user's id number
        new_user = User.objects.filter(username=username)[0]
        new_user_id = new_user.id
        new_user_registered_time = new_user.date_joined

        new_cart_status = InvoiceStatus.objects.filter(id=1)[0]

        # Use that id number to create new invoice(cart)
        new_cart = Invoice(user=new_user, status=new_cart_status,
                           date=new_user_registered_time)

        new_cart.save()

        return HttpResponse('0', content_type='text/plain')

    except(KeyError):

        return HttpResponse('-1', content_type='text/plain')

    # Throw an exception when there is a same registered username
    except(IntegrityError):

        return HttpResponse('-8', content_type='text/plain')


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

            Items = Item.objects.filter(
                user_id=requested_user_id)

            try:

                data = [None] * len(Items)

                for i in range(0, len(Items)):

                    data[i] = {'item_id': Items[i].item_id, 'item_name': Items[i].name, 'price':
                               str(Items[i].price), 'stock': Items[i].stock}

                data = json.dumps(data)

                return HttpResponse(data, content_type='text/plain')

            except(KeyError):

                return HttpResponse('-6', content_type='text/plain')

        # If a user is searching with item name:
        elif request.GET.get('item_id'):

            # Pull item_id from passed in GET params
            requested_item_id = request.GET.get('item_id')

            # If param is not int, exit method and return error message
            if not type(requested_item_id) == int:
                return HttpResponse('-7', content_type='text/plain')

            # Query for any item that has the same item_id as the passed in params
            Items = Item.objects.filter(
                item_id=requested_item_id)

            try:
                # Create an empty array that has the length of number of queried data
                data = [None] * len(Items)

                # Create an array of dict for each queried data
                for i in range(0, len(Items)):

                    data[i] = {'item_id': Items[i].item_id, 'item_name': Items[i].name, 'price':
                               str(Items[i].price), 'stock': Items[i].stock}

                data = json.dumps(data)

                return HttpResponse(data, content_type='text/plain')

            except(KeyError):

                return HttpResponse('-6', content_type='text/plain')

        # If there is no GET params given, return all the existing items
        Items = Item.objects.order_by()

        data = [None] * len(Items)

        for i in range(0, len(Items)):

            data[i] = {'item_id': Items[i].item_id, 'item_name': Items[i]
                       .name, 'price': str(Items[i].price), 'stock': Items[i].stock}

        data = json.dumps(data)

        return HttpResponse(data, content_type='application/json')

    # POST method (insert or update)
    elif request.method == 'POST':

        # Check if user is logged in. If not, exit and return -1
        if not request.user.is_authenticated:

            return HttpResponse('-1', content_type='text/plain')

        # Parse in the data sent by user
        data = json.loads(request.body)

        # Check if there are any existing item with matching item_id

        # Update

        # If there is item_id within passed data, it is an update
        if 'item_id' in data.keys():

            original_entry = Item.objects.get(
                item_id=data['item_id'])

            # Check if the owner of this item and the logged-in user is the same user_id
            item_owner_id = original_entry.user_id

            if not item_owner_id == request.user.id:

                return HttpResponse('-3', content_type='text/plain')

            # Iterate through the posted data to see which part of the data the user wishes to change.
            # Only change the field of a data that has been passed in
            if 'stock' in data.keys():
                original_entry.stock = data['stock']

            if 'name' in data.keys():
                original_entry.name = data['name']

            if 'desc' in data.keys():
                original_entry.desc = data['desc']

            if 'price' in data.keys():
                original_entry.price = data['price']

            original_entry.save()

        # Post new item
        else:

            name = data['name']
            user_id = request.user.id
            price = data['price']
            # image_id = data['image_id']
            stock = data['stock']

            new_item = Item(name=name, price=price,
                            stock=stock, user_id=user_id)

            new_item.save()

        print('A New item has been added successfully')

        return HttpResponse('0', content_type='text/plain')


# Retreive or add invoice data
def GetPostInvoice(request):
    if request.method == 'GET':
        # BLAIR CODE!!!

        # Check if this dude is logged in
        if request.user.is_authenticated:

            # Query for all the invoice under this user's id
            requested_invoices = Invoice.objects.filter(
                user_id=request.user.id)

            # Create an empty array with the length that is equivalent to the number of queried requested_invoices
            invoice_array = [None] * len(requested_invoices)

            # For each queried invoices, create a dict and append them to the empty array created above
            for invoice in requested_invoices:

                data = {'invoice_id': invoice.invoice_id,
                        'user_id': invoice.user_id, 'date_created': str(invoice.date), 'status': str(invoice.status)}

                invoice_array.append(data)

            # Convert array of dict to transferable json
            invoice_json = json.dumps(invoice_array)

            # Return the json
            return HttpResponse(invoice_json, content_type='application/json')

        else:
            # User is not logged in
            return HttpResponse('-1', content_type='text/plain')

        # When there is a specified query string(Is this necessary?? Ability to look at other people's invoice history??)
        if request.GET.get('id'):
            requested_user_id = request.GET.get('id')
            requested_invoices = Invoice.objects.filter(
                user_id=requested_user_id)

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

        Invoices = Invoice.objects.all().order_by()

        data = [None] * len(Invoices)

        for i in range(0, len(Invoices)):

            data[i] = {'invoice_id': Invoices[i].invoice_id,
                       'user_id': Invoices[i].user_id, 'date': str(Invoices[i].date),
                       'status': Invoices[i].status_id}

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


def QueryCart(request):

    if not request.user.is_authenticated:

        return HttpResponse('-1', content_type='text/plain')

    current_cart = Invoice.objects.get(
        user_id=request.user.id, status_id=1)

    return current_cart


def UpdateLineItemPrice(quantity, item_id):

    # query for that specific line item using item_id
    item = Item.objects.get(item_id=item_id)

    # query for current item price of that item and store it in a variable
    current_item_price = item.price

    # calculate the total price of the line item and store it in a variable
    calculated_line_item_price = current_item_price * quantity

    # Save that price into the existing row
    return calculated_line_item_price


# Retrieve or add lineitem data from cart(1) status invoice
def GetPostCart(request):

    # User needs to be logged in, or exits the method and returns -1
    if not request.user.is_authenticated:

        return HttpResponse('-1', content_type='text/plain')

    if request.method == 'GET':

        try:

            # Query for the 'cart' status invoice
            cart = Invoice.objects.get(
                status_id=1, user_id=request.user.id)

            # Query for every item existing in the cart
            lineItems = LineItem.objects.filter(
                invoice_id=cart.invoice_id)

            # Create an empty array with the length equivalent to existing line items in cart
            data = [None] * len(lineItems)

            # Create dict of line items in cart and append them to the empty array created above
            for i in range(0, len(lineItems)):

                data[i] = {'line_item_id': lineItems[i].line_item, 'invoice_id': lineItems[i].invoice_id, 'item_id': lineItems[i].item_id,
                           'line_item_price': float(lineItems[i].line_item_price), 'quantity': lineItems[i].quantity, 'status': lineItems[i].status_id}

            # Convert the array into transferable json data
            data = json.dumps(data)

            print('Successfully fetched line items from current cart')

            # Return the json data
            return HttpResponse(data, content_type='application/json')

        except(KeyError):

            return HttpResponse('-1', content_type='text/plain')

    elif request.method == 'POST':

        try:

            # Retrieve data from user request
            data = json.loads(request.body)

            # Cart
            current_cart = QueryCart(request)

            # Check if item_id input is of the right data type: int
            if not type(data['item_id']) == int:

                return HttpResponse('-7', content_type='text/plain')

            # Check if there is already an entry with  line_item_id of the data sent by the user
            original_entry_list = LineItem.objects.filter(
                item_id=data['item_id'], invoice_id=current_cart.invoice_id)

            # If there is already a same lineitem existing in cart, this is an update to quantity
            # Update
            if len(original_entry_list) > 0:

                original_entry = original_entry_list[0]

                if 'quantity' in data.keys():

                    # Check if quantity input is of right data type: int
                    if not type(data['quantity']) == int:

                        return HttpResponse('-7', content_type='text/plain')

                    original_entry.quantity = data['quantity']

                original_entry.line_item_price = UpdateLineItemPrice(
                    original_entry.quantity, original_entry.item_id)

                original_entry.save()

            # If there is no line_item with the same line_item_id in cart, it's a post

             # Post(Putting items into your cart)
            else:

                # Query for this user's cart
                cart = Invoice.objects.get(
                    status_id=1, user_id=request.user.id)

                invoice_id = cart.invoice_id
                item_id = data['item_id']
                quantity = data['quantity']

                # Check if both of the passed in data are of the right type: int
                if not type(item_id) == int or not type(quantity) == int:

                    return HttpResponse('-7', content_type='text/plain')

                # Calculate the total line_item_price
                line_item_price = UpdateLineItemPrice(quantity, item_id)

                # Create and save new lineitem data
                new_line_item = LineItem(status_id=1,
                                         invoice_id=invoice_id, item_id=item_id, line_item_price=line_item_price, quantity=quantity)

                new_line_item.save()

            print('The lineItem has been added to the cart successfully')

            return HttpResponse('0', content_type='text/plain')

        except(KeyError):

            print("There was a key error")
            return HttpResponse('-1', content_type='text/plain')


def SubmitCart(request):

    # Check if a user is logged in
    if not request.user.is_authenticated:

        return HttpResponse('login required', content_type='text/plain')

    # Query and check if there are more item stocks than requested quantity of the line item

    # Query and change the status for every line item that was in the cart to 2

    # Get the id of current cart
    current_cart_id = Invoice.objects.filter(
        status_id=1, user_id=request.user.id)[0].invoice_id

    line_items_in_cart = LineItem.objects.filter(
        invoice=current_cart_id)

    # Do stock check first here and return -1 error if stock is less than quantity
    for line_item in line_items_in_cart:

        item_id = line_item.item_id
        quantity = line_item.quantity

        item_stock = Item.objects.get(item_id=item_id).stock

        if item_stock < quantity:

            # Create and save notification item for this user

            new_notification = Notification(
                notification_body="There are not enough stocks of this item.", user=request.user)

            new_notification.save()

            return HttpResponse('-2', content_type='text/plain')

    # Change status for lineitem and stocks for item
    for line_item in line_items_in_cart:

        # Query for the item of the line_item
        item_id = line_item.item_id
        quantity = line_item.quantity

        item = Item.objects.get(item_id=item_id)

        # If there are more stocks than requested quantity, go through with changing the status

        line_item.status_id = 2

        line_item.save()

        # update the stock for the item_stock
        item.stock = item.stock - quantity
        item.save()

     # Query for the invoice with status of cart(1) and switch the status to paid(2)

    cart = Invoice.objects.get(
        status_id=1, user_id=request.user.id)

    cart.status_id = 2

    cart.save()

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

    data = json.loads(request.body)
    line_item = LineItem.objects.filter(line_item=data['line_item'])[0]

    # check if the user that is associated with the line_item and the logged in user is the same user
    # Pull the user id from the item object that is associated with this lineitem
    item = Item.objects.filter(item_id=line_item.item_id)[0]
    item_seller_id = item.user_id
    # Pull the invoice with this user's id
    # Lineitem will not have user fk

    # If the requested item's seller is not the same as user, exit with -1

    if not item_seller_id == request.user.id:

        return HttpResponse('-3', content_type='text/plain')

    # With the line item id, query for the line item and change its status from 2 to 3

    line_item = LineItem.objects.filter(line_item=line_item.line_item)[0]

    line_item.status_id = 3

    line_item.save()

    return HttpResponse('0', content_type='text/plain')


# Method to check of other lineitems in that specific data are all picked up or not
# This method will be run everytime an order has been picked up by a buyer

def CheckLineItemStatus(invoice_id):

    ready_for_completion = True

    # Query for that invoice this line_item is in

    # Using that invoice_id, query all the line_items in that invoice
    other_line_items = LineItem.objects.filter(invoice_id=invoice_id)

    # Loop through all the queried line items and see if their statuses are all 3

    for line_item in other_line_items:

        if not line_item.status_id == 4:

            ready_for_completion = False

    # If so, switch the status of that invoice to 3

    if ready_for_completion:

        invoice = Invoice.objects.filter(invoice_id=invoice_id)[0]

        invoice.status_id = 3

        invoice.save()


def PickUpItem(request):

    # Check if buyer is logged in

    if not request.user.is_authenticated:

        return HttpResponse('-1', content_type='text/plain')

    # line item id will be posted by the buyer

    data = json.loads(request.body)
    line_item = LineItem.objects.filter(line_item=data['line_item'])[0]

    # check if the user that is associated with the line_item(buyer) and the logged in user is the same user
    # Get Buyer id from invoice object attached to the line_item
    invoice = Invoice.objects.filter(invoice_id=line_item.invoice_id)[0]
    item_buyer_id = invoice.user_id

    # If the requested item's buyer is not the same as user, exit with -1
    # I imagine this part of the code is where it will be decided whether the buyer will be able to open the locker door or not

    if not item_buyer_id == request.user.id:

        return HttpResponse('-4', content_type='text/plain')

    # With the line item id, query for the line item and change its status from 2 to 3

    line_item.status_id = 4

    line_item.save()

    # This is where method that checks if there are other line items in invoice that are incomplete
    CheckLineItemStatus(invoice.invoice_id)

    return HttpResponse('0', content_type='text/plain')

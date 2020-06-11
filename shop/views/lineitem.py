from django.shortcuts import render

from django.http import HttpResponse
from shop.models import UserAdditionalInfo, Item, Invoice, LineItem, InvoiceStatus, LineItemStatus, Notification, Message, PassKey
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from datetime import datetime
from .invoice import queryCart
import json


def updateLineItemPrice(quantity, item_id):

    # query for that specific line item using item_id
    item = Item.objects.get(item_id=item_id)

    # query for current item price of that item and store it in a variable
    current_item_price = item.price

    # calculate the total price of the line item and store it in a variable
    calculated_line_item_price = current_item_price * quantity

    # Save that price into the existing row
    return calculated_line_item_price


# Method that is fired when seller puts an item into a locker
def putInLocker(request):

    # Check if seller is logged in
    if not request.user.is_authenticated:

        return HttpResponse('{"status_code": -1, "message": "Login required"}', content_type='application/json')

    data = json.loads(request.body)
    line_item = LineItem.objects.get(line_item=data['line_item'])

    # check if the user that is associated with the line_item and the logged in user is the same user
    # Pull the user id from the item object that is associated with this lineitem
    item = Item.objects.filter(item_id=line_item.item_id)[0]
    item_seller_id = item.user_id
    # Pull the invoice with this user's id
    # Lineitem will not have user fk

    # If the requested item's seller is not the same as user, exit with -1

    if not item_seller_id == request.user.id:

        return HttpResponse('{"status_code": -3, "message": "User id does not match the item seller id"}', content_type='application/json')

    # With the line item id, query for the line item and change its status from 2 to 3

    line_item = LineItem.objects.get(line_item=line_item.line_item)

    buyer_id = Invoice.objects.get(invoice_id=line_item.invoice_id).user_id

    line_item.status_id = 3

    line_item.save()

    # Create and save notification that is linked to the buyer's id and line_item, telling them the item has been dropped off
    dropped_off_notification = Notification(
        notification_body="This item has been dropped off.", user_id=buyer_id, line_item_id=line_item.line_item)

    return HttpResponse('{"status_code": 0, "message": "Success"}', content_type='application/json')


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

        invoice = Invoice.objects.get(invoice_id=invoice_id)

        invoice.status_id = 3

        invoice.save()


def pickUpItem(request):

    # Check if buyer is logged in

    if not request.user.is_authenticated:

        return HttpResponse('{"status_code": -1, "message": "Login required"}', content_type='application/json')

    # line item id will be posted by the buyer

    data = json.loads(request.body)
    line_item = LineItem.objects.get(line_item=data['line_item'])
    # item = Item.objects.get(item_id=line_item.item_id)
    # seller_id = User.objects.get(id=item.user_id).id

    # Combining above two lines of query code into one line
    seller_id = User.objects.filter(item__item_id=line_item.item_id)[0]

    # check if the user that is associated with the line_item(buyer) and the logged in user is the same user
    # Get Buyer id from invoice object attached to the line_item
    invoice = Invoice.objects.get(invoice_id=line_item.invoice_id)
    item_buyer_id = invoice.user_id

    # If the requested item's buyer is not the same as user, exit with -1
    # I imagine this part of the code is where it will be decided whether the buyer will be able to open the locker door or not

    if not item_buyer_id == request.user.id:

        return HttpResponse('{"status_code": -4, "message": "User id does not match the item buyer id"}', content_type='application/json')

    # With the line item id, query for the line item and change its status from 3 to 4

    line_item.status_id = 4

    line_item.save()

    # Send a notification to the seller that the item has been picked up
    picked_up_notification = Notification(
        notification_body="This item has been picked up.", user_id=seller_id, line_item_id=line_item.line_item)

    # This is where method that checks if there are other line items in invoice that are incomplete
    CheckLineItemStatus(invoice.invoice_id)

    return HttpResponse('{"status_code": 0, "message": "Success"}', content_type='application/json')


# Retrieve or add lineitem data from cart(1) status invoice
def getPostCart(request):

    # User needs to be logged in, or exits the method and returns -1
    if not request.user.is_authenticated:

        return HttpResponse('{"status_code": -1, "message": "Login required"}', content_type='application/json')

    if request.method == 'GET':

        try:

            # Query for the 'cart' status invoice. If there isn't one, create one
            cart_list = Invoice.objects.filter(
                status_id=1, user_id=request.user.id)

            if len(cart) == 0:
                cart = Invoice(date=datetime.now(),
                               user_id=request.user.id, status_id=1)
            # If there is an existing cart, use that
            else:
                cart = cart_list[0]

            # Query for every item existing in the cart
            lineItems = LineItem.objects.filter(
                invoice_id=cart.invoice_id)

            # Create an empty array with the length equivalent to existing line items in cart
            data = [None] * len(lineItems)

            # Create dict of line items in cart and append them to the empty array created above
            for i in range(0, len(lineItems)):

                # Per one item, query for its item name and item image
                item = Item.objects.get(item_id=lineItems[i].item_id)
                item_name = item.name
                item_image = item.image

                data[i] = {'line_item_id': lineItems[i].line_item, 'invoice_id': lineItems[i].invoice_id, 'item_id': lineItems[i].item_id, 'item_name': item_name, 'item_image': str(item_image),
                           'line_item_price': float(lineItems[i].line_item_price), 'quantity': lineItems[i].quantity, 'status': lineItems[i].status_id}

            # Convert the array into transferable json data
            data = json.dumps(data)

            print('Successfully fetched line items from current cart')

            # Return the json data
            return HttpResponse(data, content_type='application/json')

        except(KeyError):

            return HttpResponse('{"status_code": -6, "message": "Key error"}', content_type='application/json')

    elif request.method == 'POST':

        try:

            # Retrieve data from user request
            data = json.loads(request.body)

            # Cart
            current_cart = queryCart(request)

            # Check if the picked item belongs to the current logged in user. If so, terminate process and throw an error code
            item_id = data['item_id']
            item_owner_id = Item.objects.get(item_id=item_id).user_id
            current_user_id = request.user.id

            if item_owner_id == current_user_id:
                return HttpResponse('{"status_code": -10, "message": "Attempted to add own item into cart"}', content_type='application/json')

            # Check if item_id input is of the right data type: int

            # try:
            #     int(data['item_id'])
            # except:
            #     return HttpResponse('-7', content_type='application/json')

            if not type(data['item_id']) == int:

                return HttpResponse('{"status_code": -7, "message": "Wrong data type input"}', content_type='application/json')

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

                        return HttpResponse('{"status_code": -7, "message": "Wrong data type input"}', content_type='application/json')

                    original_entry.quantity = data['quantity']

                original_entry.line_item_price = updateLineItemPrice(
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

                    return HttpResponse('{"status_code": -7, "message": "Wrong data type input"}', content_type='application/json')

                # Calculate the total line_item_price
                line_item_price = updateLineItemPrice(quantity, item_id)

                # Create and save new lineitem data
                new_line_item = LineItem(status_id=1,
                                         invoice_id=invoice_id, item_id=item_id, line_item_price=line_item_price, quantity=quantity)

                new_line_item.save()

            print('The lineItem has been added to the cart successfully')

            return HttpResponse('{"status_code": 0, "message": "Success"}', content_type='application/json')

        except(KeyError):

            print("There was a key error")

            return HttpResponse('{"status_code": -6, "message": "Key error"}', content_type='application/json')


# Method to remove item from cart
def deleteLineItem(request):

    # If the method is not POST, exit with a status code of -15
    if not request.method == 'POST':
        return HttpResponse('{"status_code": -15, "message": "Wrong method"}', content_type='application/json')

    # Check if a user is logged in
    if not request.user.is_authenticated:

        return HttpResponse('{"status_code": -1, "message": "Login required"}', content_type='application/json')

    data = json.loads(request.body)

    # If line_item is given, and when the logged in user id matches the buyer's id, delete that one item
    if 'line_item_id' in data.keys():

        # Query for the lineitem using line_item and current cart(invoice) id
        line_item = LineItem.objects.get(
            line_item=data['line_item_id'], status_id=1)
        invoice = Invoice.objects.get(invoice_id=line_item.invoice_id)
        buyer = invoice.user_id

        if not invoice.user_id == request.user.id:
            return HttpResponse('{"status_code": -1, "message": "Login required"}', content_type='application/json')

        line_item.delete()

    else:

        # If no line_item is given , query and delete everything in cart

        # Check if logged in user and invoice's user id matches
        logged_in_user_cart = Invoice.objects.get(
            user_id=request.user.id, status_id=1)

        # Query everything in this user's invoice with a status of 1(cart)
        line_items = LineItem.objects.filter(
            status_id=1, invoice_id=logged_in_user_cart.invoice_id)

        # Use a for loop to iterate through all the line_items and delete them
        for line_item in line_items:
            line_item.delete()

    return HttpResponse('{"status_code": 0, "message": "Success"}', content_type='application/json')


# Method to flag different line items for 'save for later' status
def toggleSave(request):

    if request.method == 'GET':
        return HttpResponse('{"status_code": -15, "message": "Invalid method"}', content_type='application/json')

    data = json.loads(request.body)

    if not 'line_item_id' in data.keys():

        return HttpResponse('{"status_code": -13, "message": "Data not provided"}', content_type='application/json')

    line_item_id = data['line_item_id']

    # Check if the user is logged in. If not, return -1 and exit
    if not request.user.is_authenticated:
        return HttpResponse('{"status_code": -1, "message": "Login required"}', content_type='application/json')

    # Query for the invoice_id of the current cart
    cart = Invoice.objects.get(user_id=request.user.id, status_id=1)

    # Query for the user of the line item using invoice
    cart_owner = cart.user_id

    # Check if the two user_ids match
    if not request.user.id == cart_owner:
        return HttpResponse('{"status_code": -4, "message": "User id does not match the item buyer id"}', content_type='application/json')

    line_item = LineItem.objects.get(line_item=line_item_id)
    # if the status of the lineitem is 1, switch to 6
    print(line_item)
    if line_item.status_id == 1:
        line_item.status_id = 5

    # else if the status of the lineitem is 6, switch to 1
    elif line_item.status_id == 5:
        line_item.status_id = 1

    # Update and save the data
    line_item.save()

    return HttpResponse('{"status_code": 0, "message": "Success"}', content_type='application/json')


def submittedLineItem(request):

    # Needed data = logged in user_id
    # Check if user is logged in
    if not request.user.is_authenticated:
        return HttpResponse('{"status_code": -1, "message": "Login required"}', content_type='application/json')

    # logged in user's id
    user_id = request.user.id

    # Pull line items that is linked to an item that is linked to this user's user id that has a status of 2 or higher
    # How to reach out to seller id with line item
    # line_item -> item -> user_id

    # How to reach out to buyer id with line item
    # line_item -> invoice -> user_id
    # How do I present buyer_id to each line_item_submitted?

    # All items that have been submitted(status >= 2)
    line_items_submitted = LineItem.objects.filter(
        item__user_id=user_id, status_id__gte=2)

    data = [None] * len(line_items_submitted)

    for i in range(0, len(line_items_submitted)):

        # This part was written to get buyer id from each line_item
        invoice_id = line_items_submitted[i].invoice_id
        buyer_id = Invoice.objects.get(invoice_id=invoice_id).user_id

        data[i] = {'line_item_id': line_items_submitted[i].line_item, 'item_id': line_items_submitted[i].item_id,
                   'requested_quantity': line_items_submitted[i].quantity, 'status_id': line_items_submitted[i].status_id, 'buyer_id': buyer_id}

    data = json.dumps(data)

    return HttpResponse(data, content_type='application/json')

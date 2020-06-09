from django.shortcuts import render

from django.http import HttpResponse
from shop.models import UserAdditionalInfo, Item, Invoice, LineItem, InvoiceStatus, LineItemStatus, Notification, Message, PassKey
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from datetime import datetime
import json


# Retreive or add invoice data
def getPostInvoice(request):
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
            return HttpResponse('{"status_code": -1, "message": "Login required"}', content_type='application/json')

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

                return HttpResponse('{"status_code": -1, "message": "Login required"}', content_type='application/json')

        Invoices = Invoice.objects.all().order_by()

        data = [None] * len(Invoices)

        for i in range(0, len(Invoices)):

            data[i] = {'invoice_id': Invoices[i].invoice_id,
                       'user_id': Invoices[i].user_id, 'date': str(Invoices[i].date),
                       'status': Invoices[i].status_id}

        data = json.dumps(data)

        return HttpResponse(data, content_type='application/json')

    # Commenting out POST request for invoice. There is no need.

    # elif request.method == 'POST':

    #     try:
    #         data = json.loads(request.body)
    #         invoice_id = data['invoice_id']
    #         user_id = data['user_id']
    #         date = data['date']
    #         status = data['status']

    #         parsed_data = Invoice(
    #             invoice_id=invoice_id, user_id=user_id, date=date, status=status)

    #         parsed_data.save()

    #         print('Invoice has been added successfully')

    #         return HttpResponse('0', content_type='application/json')

    #     except(KeyError):
    #         print("Key error")
    #         return HttpResponse('-1', content_type='application/json')


def queryCart(request):

    if not request.user.is_authenticated:

        return HttpResponse('{"status_code": -1, "message": "Login required"}', content_type='application/json')

    current_cart = Invoice.objects.get(
        user_id=request.user.id, status_id=1)

    return current_cart


def submitCart(request):

    # Check if a user is logged in
    if not request.user.is_authenticated:

        return HttpResponse('{"status_code": -1, "message": "Login required"}', content_type='application/json')

    # Query and check if there are more item stocks than requested quantity of the line item

    # Query and change the status for every line item that was in the cart to 2

    # Get the id of current cart
    current_cart_id = Invoice.objects.get(
        status_id=1, user_id=request.user.id).invoice_id

    line_items_in_cart = LineItem.objects.filter(
        invoice=current_cart_id)

    # Query for line items that has a status of 2(not saved)
    line_items_in_cart_not_saved = LineItem.objects.filter(
        invoice=current_cart_id, status_id=1)

    # If there are no items ready for purchase in the cart, abort submitting
    if len(line_items_in_cart_not_saved) == 0:

        return HttpResponse('{"status_code": -11, "message": "No line item with status 1 to submit"}', content_type='application/json')

    # Do stock check first here and return -1 error if stock is less than quantity
    for line_item in line_items_in_cart:

        item_id = line_item.item_id
        quantity = line_item.quantity

        item_stock = Item.objects.get(item_id=item_id).stock

        if item_stock < quantity:

            # Create and save notification item for this user

            new_notification = Notification(
                notification_body="There are not enough stocks of this item.", user=request.user, line_item_id=line_item.line_item)

            new_notification.save()

            return HttpResponse('{"status_code": -2, "message": "Not enough stock"}', content_type='application/json')

    # Create a new cart under this user's user_id

    new_cart = Invoice(user=request.user, status_id=1,
                       date=datetime.now())

    new_cart.save()

    # Change status for lineitem and stocks for item
    for line_item in line_items_in_cart:

        # Query for the item of the line_item
        item_id = line_item.item_id
        quantity = line_item.quantity
        status = line_item.status_id

        item = Item.objects.get(item_id=item_id)
        seller_id = item.user_id

        # If there are more stocks than requested quantity,
        # and the status of the item is 1,
        # go through with changing the status and calculating the item stocks
        if status == 1:
            line_item.status_id = 2

            # Create a notification and send it to the seller of the item
            seller_notification = Notification(
                user_id=seller_id, notification_body="A buyer would like to purchase this item.", line_item_id=line_item.line_item)

            seller_notification.save()

            line_item.save()

            # update the stock of the item and save the item
            item.stock = item.stock - quantity
            item.save()

        # Change invoice_id of the line_item with a status of 6 to the one of the new cart
        elif status == 5:

            # Newly created cart
            new_cart = Invoice.objects.filter(
                user_id=request.user.id, status_id=1).order_by('-invoice_id')[0]
            line_item.invoice_id = new_cart.invoice_id
            line_item.save()

    # Query for the invoice with status of cart(1) and switch the status to paid(2)
    # Don't exactly now why this query gets more than 1? Maybe it didn't?
    cart = Invoice.objects.get(
        status_id=1, user_id=request.user.id, invoice_id=current_cart_id)

    cart.status_id = 2

    cart.save()

    return HttpResponse('{"status_code": 0, "message": "Success"}', content_type='application/json')

from django.shortcuts import render

from django.http import HttpResponse
from shop.models import UserAdditionalInfo, Item, Invoice, LineItem, InvoiceStatus, LineItemStatus, Notification, Message, PassKey
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from datetime import datetime
import json


def getPostMessage(request):

    # Check if user is logged in
    if not request.user.is_authenticated:
        return HttpResponse('{"status_code": -1, "message": "Login required"}', content_type='application/json')

    if request.method == 'GET':

        # Extract info needed from GET params
        line_item_id = request.GET.get('line_item')
        user_id = request.user.id

        line_item = LineItem.objects.get(line_item=line_item_id)
        item = Item.objects.get(item_id=line_item.item_id)
        invoice = Invoice.objects.get(invoice_id=line_item.invoice_id)
        buyer_id = invoice.user_id
        seller_id = item.user_id

        # Check if the requesting user id and the line_item buyer's id or seller's id matches
        # And only fetches the messages if they do
        if request.user.id == buyer_id or request.user.id == seller_id:

            # Query for all the existing messages with this user and line_item
            # And order them by desc date_created
            messages = Message.objects.filter(
                line_item_id=line_item.line_item).order_by('-date_created')

            data = [None] * len(messages)

            for i in range(0, len(messages)):

                data[i] = {'message_body': messages[i].message_body, 'date_created': str(messages[i].date_created),
                           'image_id': str(messages[i].image), 'user_id': messages[i].user_id}

            data = json.dumps(data)

            return HttpResponse(data, content_type='application/json')

        else:

            return HttpResponse('{"status_code": -9, "message": "The logged in user does not have the authority"}', content_type='application/json')

    elif request.method == 'POST':

        # Extract data from passed in json
        data = json.loads(request.body)

        line_item_id = data['line_item_id']
        user_id = request.user.id

        line_item = LineItem.objects.get(line_item=line_item_id)
        item = Item.objects.get(item_id=line_item.item_id)
        invoice = Invoice.objects.get(invoice_id=line_item.invoice_id)
        buyer_id = invoice.user_id
        seller_id = item.user_id

        # Check if the user is either the buyer or the seller of this lineitem
        if request.user.id == buyer_id or request.user.id == seller_id:

            # Extract message_body from passed in json and create a message object
            message = data['message_body']
            new_message = Message(message_body=message, date_created=datetime.now(
            ), line_item_id=line_item_id, user_id=request.user.id)

            # Save the newly created message object
            new_message.save()

            return HttpResponse('{"status_code": 0, "message": "Success"}', content_type='application/json')

        else:

            return HttpResponse('{"status_code": -9, "message": "The logged in user does not have the authority"}', content_type='application/json')

from django.shortcuts import render

from django.http import HttpResponse
from shop.models import UserAdditionalInfo, Item, Invoice, LineItem, InvoiceStatus, LineItemStatus, Notification, Message, PassKey
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from datetime import datetime
import json


def getUserInfo(request):
    if request.method == 'GET':

        # When query string exists
        if request.GET.get('username'):

            # Extract the parameter and save it to requested_id
            requested_username = request.GET.get('username')

            # Query for the data that matches the criteria
            requested_user = User.objects.get(
                username=requested_username)
            requested_user_id = requested_user.id
            requested_user_additional_info = UserAdditionalInfo.objects.get(
                user_id=requested_user_id)

            if requested_user:

                # Create a dict with the values retrieved from the queried data point
                data = {'id': requested_user.id,
                        'username': requested_user.username, 'date_joined': str(requested_user.date_joined), 'last_login': str(requested_user.last_login), 'thumbs_up': requested_user_additional_info.thumbs_up, 'thumbs_down': requested_user_additional_info.thumbs_down, 'image': str(requested_user_additional_info.image)}

                # Convet the data to transferable json
                data = json.dumps(data)

                # Return that data
                return HttpResponse(data, content_type='application/json')

            # When the query matched no data
            else:

                return HttpResponse('{"status_code": -5, "message": "No info retrieved"}', content_type='application/json')

        # When no GET params are given
        else:

            return HttpResponse('{"status_code": -13, "message": "Data not provided"}', content_type='application/json')

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


# Fetch currently logged in user's info
def getLoggedInUserInfo(request):

    # Check if someone is logged in
    if not request.user.is_authenticated:
        return HttpResponse('{"status_code": -1, "message": "Login required"}', content_type='application/json')

    # Get currently logged in user object
    user = request.user

    user_id = request.user.id
    username = request.user.username
    first_name = request.user.first_name
    last_name = request.user.last_name
    email = request.user.email
    date_joined = request.user.date_joined
    last_login = request.user.last_login

    data = {'user_id': user_id, 'username': username, 'first_name': first_name,
            'last_name': last_name, 'email': email, 'date_joined': str(date_joined), 'last_login': str(last_login)}

    data = json.dumps(data)

    return HttpResponse(data, content_type='application/json')


# Method to rate the user based on the transaction. POST method
def rateUser(request):

    # Check if user is logged in
    if not request.user.is_authenticated:
        return HttpResponse('{"status_code": -1, "message": "Login required"}', content_type='application/json')

    data = json.loads(request.body)

    line_item_id = data['line_item_id']  # int
    rating = data['rating']  # boolean

    line_item = LineItem.objects.get(line_item=line_item_id)
    item_id = line_item.item_id
    item = Item.objects.get(item_id=item_id)
    item_owner_id = item.user_id
    item_owner_additional_info = UserAdditionalInfo.objects.get(
        user_id=item_owner_id)

    invoice_id = line_item.invoice_id
    invoice = Invoice.objects.get(invoice_id=invoice_id)
    invoice_owner_id = invoice.user_id
    # print(invoice_owner_id)
    invoice_owner_additional_info = UserAdditionalInfo.objects.get(
        user_id=invoice_owner_id)

    user_id = request.user.id

    # if the current user matches the item(retrieved from line_item) owner, this user is the seller.
    # Therefore the rating will count towards the buyer's rating
    if user_id == item_owner_id:
        invoice_owner = User.objects.get(id=invoice_owner_id)

        if rating:  # If the rating is true
            # Create UserAdditionalInfo object with FK of the buyer's id
            invoice_owner_additional_info.thumbs_up += 1
            invoice_owner_additional_info.save()
        else:
            invoice_owner_additional_info.thumbs_down += 1
            invoice_owner_additional_info.save()

    # If that is not the case, the user is the buyer,
    # Therefore the rating should count towards the seller's rating
    else:
        item_owner = User.objects.get(id=item_owner_id)

        if rating:  # If the rating is true
            item_owner_additional_info.thumbs_up += 1
            item_owner_additional_info.save()
        else:
            item_owner_additional_info.thumbs_down += 1
            item_owner_additional_info.save()

    return HttpResponse('{"status_code": 0, "message": "Success"}', content_type='application/json')


def getPostUserImage(request):
    for file in request.FILES:
        user_info = UserAdditionalInfo.objects.get(user_id=request.user)
        user_info.image = request.Files[file].read()
        user_info.save()
        break
    return HttpResponse('{"status_code": 0, "message": "Success"}', content_type='application/json')

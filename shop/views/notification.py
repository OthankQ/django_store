from django.shortcuts import render

from django.http import HttpResponse
from shop.models import UserAdditionalInfo, Item, Invoice, LineItem, InvoiceStatus, LineItemStatus, Notification, Message, PassKey
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from datetime import datetime
import json


def getNotification(request):

    # Check if the user is logged in
    if not request.user.is_authenticated:
        return HttpResponse('{"status_code": -1, "message": "Login required"}', content_type='application/json')

    # Query for all the notification data with the logged in user's user id
    notifications = Notification.objects.filter(user_id=request.user.id)

    # Make an empty array and populate it with the dict of queried notification data
    data = [None] * len(notifications)

    for i in range(0, len(notifications)):
        data[i] = {'notification_body': notifications[i].notification_body,
                   'read': notifications[i].read}

    # Convert the array into transferable data
    data = json.dumps(data)

    # Return the converted data
    return HttpResponse(data, content_type='application/json')


# Method for deleting notifications
def deleteNotification(request):

    # Check if the user is logged in
    if not request.user.is_authenticated:
        return HttpResponse('{"status_code": -1, "message": "Login required"}', content_type='application/json')

    data = json.loads(request.body)

    # if a notification id is given, query the notification using the id and delete only that notification
    if 'notification_id' in data.keys():
        notification = Notification.objects.get(
            id=data['notification_id'], user_id=request.user.id)
        notification.delete()

    # if not, fetch all notifications under this user's id and delete all of them
    else:
        notifications = Notification.objects.filter(user_id=request.user.id)

        for notification in notifications:
            notification.delete()

    return HttpResponse('{"status_code": 0, "message": "Success"}', content_type='application/json')

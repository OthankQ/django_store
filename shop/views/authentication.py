from django.shortcuts import render

from django.http import HttpResponse
from shop.models import UserAdditionalInfo, Item, Invoice, LineItem, InvoiceStatus, LineItemStatus, Notification, Message, PassKey
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from datetime import datetime
from shop.email import send_mail
import json
import random


# Registration
def registerUser(request):

    # Load passed json into python dict

    if request.method == 'GET':
        return HttpResponse('{"status_code": -15, "message": "Invalid method"}', content_type='application/json')

    data = json.loads(request.body)

    try:

        # If any of the required data is not provided, exit with code -13
        if not 'email' in data.keys() or not 'username' in data.keys() or not 'password' in data.keys():

            return HttpResponse('{"status_code": -13, "message": "Data not provided"}', content_type='application/json')

        if data['email'] == "" or data['username'] == "" or data['password'] == "":

            return HttpResponse('{"status_code": -13, "message": "Data not provided"}', content_type='application/json')

        email = data['email']
        # Check if user has entered wrong datatype for email
        if not type(email) == str:
            return HttpResponse('{"status_code": -7, "message": "Wrong data type input"}', content_type='application/json')

        # Convert email to lower case so it will not be case sensitive
        email = email.lower()

        # Check if there is a duplicate email address
        # Query for any user with the entered email address
        existing_user_with_same_email = User.objects.filter(email=email)

        # Exit the method and return a message if there are any users with that email already
        if len(existing_user_with_same_email) > 0:
            return HttpResponse('{"status_code": -8, "message": "Duplicate entry(username, email)"}', content_type='application/json')

        username = data['username']
        # Check if user has entered wrong datatype for username
        if not type(username) == str:
            return HttpResponse('{"status_code": -7, "message": "Wrong data type input"}', content_type='application/json')

        # Convert username to lower case so it will not be case sensitive
        username = username.lower()

        password = data['password']

        new_user = User.objects.create_user(username, email, password)

        new_user_additionalInfo = UserAdditionalInfo(user_id=new_user.id)

        # This is where we have to send the newly registered user verification emails
        characters = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

        url_key = ''

        for i in range(0, 10):
            url_key += random.choice(characters)

        user_id = new_user.id
        user_email = new_user.email

        new_user.save()
        new_user_additionalInfo.save()

        pass_key_object = PassKey(
            user_id=user_id, url_key=url_key)

        # This url_key_object will get destroyed after user verifies
        pass_key_object.save()

        send_mail(
            new_user.email,
            'Verification Email',
            f'Click the link to verify your email.<html><body><a href="http://localhost:8000/api/user/verify?key={url_key}"></body></html>'
        )

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

        return HttpResponse('{"status_code": 0, "message": "Success"}', content_type='application/json')

    except(KeyError):

        return HttpResponse('{"status_code": -1, "message": "Login required"}', content_type='application/json')

    # Throw an exception when there is a same registered username
    except(IntegrityError):

        return HttpResponse('{"status_code": -8, "message": "Duplicate entry(username, email)"}', content_type='application/json')


# Method to verify user's email account
def verify(request):

    # GET request containing pass code as a param
    url_key = request.GET.get('key')
    pass_key_object = PassKey.objects.get(url_key=url_key)
    user_id = pass_key_object.user_id

    # Do a check if there are any previously generated pass_key_objects associated with this user
    previous_pass_keys = PassKey.objects.exclude(
        url_key=pass_key_object.url_key).filter(user_id=user_id)

    # If there are any, delete them one by one
    if len(previous_pass_keys) > 0:
        for i in range(0, len(previous_pass_keys)):
            previous_pass_keys[i].delete()

    # Query for the user's verified field on userAdditionalInfo table
    user_additional_info = UserAdditionalInfo.objects.get(
        user_id=pass_key_object.user_id)

    # Change the verified status to True and save
    user_additional_info.verified = 1
    user_additional_info.save()

    # get rid of url_key_object
    pass_key_object.delete()

    return HttpResponse('User\'s email has been verified', content_type='text/plain')


# Method to do a simple check before verifying if there is any PassKey associated with the currently generated PassKey
# def reVerify(request):


def userLogin(request):

    if request.method == 'GET':
        return HttpResponse('{"status_code": -15, "message": "Invalid method"}', content_type='application/json')

    try:
        data = json.loads(request.body)

        if not 'username' in data.keys() or not 'password' in data.keys():

            return HttpResponse('{"status_code": -13, "message": "Data not provided"}', content_type='application/json')

        if data['username'] == "" or data['password'] == "":

            return HttpResponse('{"status_code": -13, "message": "Data not provided"}', content_type='application/json')

        username = data['username']
        password = data['password']

        # send back 'not verified' if the user is not verified

        # Fetch user using username
        user = User.objects.filter(username=username)

        # Check if there are any users with that username
        if len(user) == 0:
            return HttpResponse('{"status_code": -14, "message": "No matching user"}', content_type='application/json')
        else:
            user = user[0]

        # Fetch user additional info using user id
        user_additional_info = UserAdditionalInfo.objects.get(
            user_id=user.id)

        verified = user_additional_info.verified
        password_resetting = user_additional_info.password_resetting

        if not verified:

            return HttpResponse('{"status_code": -12, "message": "This user is not verified"}', content_type='application/json')

        if password_resetting:

            return HttpResponse('{"status_code": -17, "message": "This user is in the process of resetting the password"}', content_type='application/json')

        if user is not None:
            # Verify the credentials
            user = authenticate(request, username=username, password=password)

            if user is None:
                return HttpResponse('{"status_code": -19, "message": "Wrong password"}', content_type='application/json')

            # Save user info to session
            login(request, user)
            return HttpResponse('{"status_code": 0, "message": "Success"}', content_type='application/json')

        else:
            return HttpResponse('{"status_code": -1, "message": "Login required"}', content_type='application/json')

    except(KeyError):

        return HttpResponse('{"status_code": -1, "message": "Login required"}', content_type='application/json')


# User Logout
def userLogout(request):
    logout(request)
    return HttpResponse('{"status_code": 0, "message": "Success"}', content_type='application/json')


def forgotPassword(request):

    # Send an email to the address entered by the user if that email address matches any in the user table
    data = json.loads(request.body)
    email = data['email']

    # Check if retrieved email matches any in the user db
    user = User.objects.filter(email=email)
    user_additional_info = UserAdditionalInfo.objects.get(user_id=user[0].id)

    # Set a checkpoint to see if this user is verified
    if user_additional_info.verified == 0:

        return HttpResponse('{"status_code": -12, "message": "This user is not verified"}', content_type='application/json')

    # If there is no match, send a status code

    if len(user) == 0:

        return HttpResponse('{"status_code": 0, "message": "Success"}', content_type='application/json')

    # If there is a match, set password_resetting to 1
    elif len(user) > 0:
        print(user_additional_info.password_resetting)
        user_additional_info.password_resetting = True
        user_additional_info.save()

        # Create a random 10 digit PassKey, create PassKey object linked to this user's user id, then embed it into the link being sent
        # Create a second pass code, embed it into the text of the email

        characters = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

        url_key = ''

        text_key = ''

        for i in range(0, 10):
            url_key += random.choice(characters)
            text_key += random.choice(characters)

        user_id = user[0].id
        user_email = user[0].email

        pass_key_object = PassKey(
            user_id=user_id, url_key=url_key, text_key=text_key)

        # Delete any passkey object if there has been one before
        # Only the ones that belong to this user
        previous_pass_keys = PassKey.objects.exclude(
            url_key=pass_key_object.url_key).filter(user_id=user_id)

        # If there are any, delete them one by one
        if len(previous_pass_keys) > 0:
            for i in range(0, len(previous_pass_keys)):
                previous_pass_keys[i].delete()

        pass_key_object.save()

        # send a link to reset password
        # Also, set the password_resetting field to true
        send_mail(
            user_email,
            'Password Reset Email',
            f'Click the link and enter {text_key} along with your new password to reset your password.<html><body><a href="http://localhost:8000/api/user/password/reset?key={url_key}"></body></html>'
        )

        return HttpResponse('{"status_code": 0, "message": "Success"}', content_type='application/json')


# Resending verification
def resendVerification(request):

    data = json.loads(request.body)

    if 'username' in data.keys():

        username = data['username']

        user = User.objects.filter(username=username)

        if len(user) == 0:

            return HttpResponse('{"status_code": 0, "message": "Success"}', content_type='application/json')

        user = user[0]

    if 'email' in data.keys():

        email = data['email']

        user = User.objects.filter(email=email)

        if len(user) == 0:

            return HttpResponse('{"status_code": 0, "message": "Success"}', content_type='application/json')

        user = user[0]

    user_id = user.id

    user_additional_info = UserAdditionalInfo.objects.get(user_id=user_id)

    if user_additional_info.verified == True:

        return HttpResponse('{"status_code": 0, "message": "Success"}', content_type='application/json')

    user_email = user.email

    # Generate new url_key
    characters = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

    url_key = ''

    for i in range(0, 10):
        url_key += random.choice(characters)

    pass_key_object = PassKey(
        user_id=user_id, url_key=url_key)

    # This url_key_object will get destroyed after user verifies
    pass_key_object.save()

    send_mail(
        'Verification Email',
        f'Click the link to verify your email.<html><body><a href="http://localhost:8000/api/user/verify?key={url_key}"></body></html>',
        'admin@shibastudios.net',
        [f'{user_email}'],
        fail_silently=False
    )

    return HttpResponse('{"status_code": 0, "message": "Success"}', content_type='application/json')


def resetPassword(request):

    if request.method == 'GET':
        # Check if the clicked link is still valid

        # This is where all the variables above are being set
        # Retrieve the PassKey object using the param
        url_key = request.GET.get('key')
        pass_key_object = PassKey.objects.get(url_key=url_key)
        user_additional_info = UserAdditionalInfo.objects.get(
            user_id=pass_key_object.user_id)

        request.session['text_key'] = pass_key_object.text_key

        return HttpResponse('{"status_code": 0, "message": "Success"}', content_type='application/json')

    if request.method == 'POST':

        # print(request.session['text_key'])

        # Pull text_key from session and delete that session data
        text_key_from_session = request.session['text_key']

        # Pull pass_key object using text key from session
        pass_key_object = PassKey.objects.get(text_key=text_key_from_session)
        user_id = pass_key_object.user_id
        user_additional_info = UserAdditionalInfo.objects.get(user_id=user_id)

        data = json.loads(request.body)

        new_password = data['new_password']
        # password_confirm = data['password_confirm']
        text_key = data['text_key']

        if not text_key == pass_key_object.text_key:

            if pass_key_object.attempts < 4:

                pass_key_object.attempts += 1

                pass_key_object.save()

                return HttpResponse('wrong passcode', content_type='text/plain')

            elif pass_key_object.attempts >= 4:

                pass_key_object.delete()

                del request.session['text_key']

                # Needs to disable the submit button, or needs to redirect the user to the homepage

                return HttpResponse('{"status_code": -18, "message": "Exceeded the limits of possible attempts"}', content_type='application/json')

            # pass_key_object.save()

        # When new password and confirm do not match, send an error
        # if not new_password == password_confirm:

        #     return HttpResponse('{"status_code": -16, "message": "Password confirm does not match"}', content_type='application/json')

        # When they do match, fetch the user with user_id and change the password
        user = User.objects.get(id=user_id)
        user.set_password(new_password)
        del request.session['text_key']
        user.save()

        # Set password_resetting status to False and save

        user_additional_info.password_resetting = False
        user_additional_info.save()

        # Delete the url_key_object when password reset is successful
        pass_key_object.delete()

        return HttpResponse('{"status_code": 0, "message": "Success"}', content_type='application/json')

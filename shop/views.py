from django.shortcuts import render

from django.http import HttpResponse
from .models import User

def GetPostUser(request):
    if request.method == 'GET':

        # Query for all Users
        Users = User.objects.all().order_by().values()

        # Create empty array to store data
        data = [None] * len(Users)

        # For each entry, create a dictionary and insert it into data array
        for i in range(0, len(Users)):
            data[i] = {'user_id': Users[i]['user_id'], 'user_name': Users[i]['name'], 'phone': Users[i]['phone_number']}

        # Convert python dictionary to passable json data
        data = json.dumps(data)

        # Return the queried and converted data
        return HttpResponse(data, content_type='application/json')

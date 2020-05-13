# from rest_framework import routers
# from .api import UserViewSet, ItemViewSet
from django.urls import path, include
from .views import GetPostUser

urlpatterns = [
    path('user/', GetPostUser, name='name')
]


# router = routers.DefaultRouter()
# router.register('api/user', UserViewSet, 'user')
# router.register('api/item', ItemViewSet, 'item')

# urlpatterns = router.urls
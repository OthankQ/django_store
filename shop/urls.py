# from rest_framework import routers
# from .api import UserViewSet, ItemViewSet
from django.urls import path, include
from .views import GetPostUser, UserLogin, GetPostItem, GetPostInvoice, GetPostLineItem

urlpatterns = [
    path('user/', GetPostUser, name='name'),
    path('login/', UserLogin, name='login'),
    path('item/', GetPostItem, name='item'),
    path('invoice/', GetPostInvoice, name='invoice'),
    path('lineitem/', GetPostLineItem, name='line_item')
]


# router = routers.DefaultRouter()
# router.register('api/user', UserViewSet, 'user')
# router.register('api/item', ItemViewSet, 'item')

# urlpatterns = router.urls

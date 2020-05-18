# from rest_framework import routers
# from .api import UserViewSet, ItemViewSet
from django.urls import path, include
from .views import GetUserInfo, RegisterUser, UserLogin, UserLogout, GetPostItem, GetPostInvoice, GetPostLineItem

urlpatterns = [
    path('user/info/', GetUserInfo, name='user'),
    path('user/register/', RegisterUser, name='register'),
    path('login/', UserLogin, name='login'),
    path('logout/', UserLogout, name='logout'),
    path('item/', GetPostItem, name='item'),
    path('invoice/', GetPostInvoice, name='invoice'),
    path('lineitem/', GetPostLineItem, name='line_item')
]


# router = routers.DefaultRouter()
# router.register('api/user', UserViewSet, 'user')
# router.register('api/item', ItemViewSet, 'item')

# urlpatterns = router.urls

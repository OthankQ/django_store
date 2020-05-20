# from rest_framework import routers
# from .api import UserViewSet, ItemViewSet
from django.urls import path, include
from .views import GetUserInfo, RegisterUser, UserLogin, UserLogout, GetPostItem, GetPostInvoice, GetPostCart, SubmitCart

urlpatterns = [
    path('user/info/', GetUserInfo, name='user'),
    path('user/register/', RegisterUser, name='register'),
    path('login/', UserLogin, name='login'),
    path('logout/', UserLogout, name='logout'),
    path('item/', GetPostItem, name='item'),
    path('invoice/', GetPostInvoice, name='invoice'),
    path('cart/', GetPostCart, name='line_item'),
    path('submit/', SubmitCart, name='submit')
]


# router = routers.DefaultRouter()
# router.register('api/user', UserViewSet, 'user')
# router.register('api/item', ItemViewSet, 'item')

# urlpatterns = router.urls

# from rest_framework import routers
# from .api import UserViewSet, ItemViewSet
from django.urls import path, include
from .views import getUserInfo, registerUser, userLogin, userLogout, getPostItem, getPostInvoice, getPostCart, submitCart, putInLocker, pickUpItem, toggleSave, getNotification, deleteNotification, getPostMessage, submittedLineItem, rateUser, getLoggedInUserInfo

urlpatterns = [
    path('user/info/', getUserInfo, name='user'),
    path('user/register/', registerUser, name='register'),
    path('loggedInUser/', getLoggedInUserInfo, name='loggedInUserInfo'),
    path('login/', userLogin, name='login'),
    path('logout/', userLogout, name='logout'),
    path('item/', getPostItem, name='item'),
    path('invoice/', getPostInvoice, name='invoice'),
    path('cart/', getPostCart, name='cart'),
    path('submit/', submitCart, name='submit'),
    path('dropoff/', putInLocker, name='dropoff'),
    path('pickup/', pickUpItem, name='pickup'),
    path('save/', toggleSave, name='save'),
    path('notification/', getNotification, name='getNotification'),
    path('deleteNotification/', deleteNotification, name='deleteNotification'),
    path('message/', getPostMessage, name='getPostMessage'),
    path('submittedLineItem/', submittedLineItem, name='submittedLineItem'),
    path('rateUser/', rateUser, name='rateUser'),
]


# router = routers.DefaultRouter()
# router.register('api/user', UserViewSet, 'user')
# router.register('api/item', ItemViewSet, 'item')

# urlpatterns = router.urls

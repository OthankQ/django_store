# from rest_framework import routers
# from .api import UserViewSet, ItemViewSet
from django.urls import path, include
from .views import getUserInfo, registerUser, userLogin, userLogout, getPostItem, getPostInvoice, getPostCart, submitCart, putInLocker, pickUpItem, toggleSave, getNotification, deleteNotification, getPostMessage, submittedLineItem, rateUser, getLoggedInUserInfo, verify, deleteItem, deleteLineItem, forgotPassword, resetPassword, resendVerification, getPostUserImage

urlpatterns = [
    path('user/info/', getUserInfo, name='user'),
    path('user/register/', registerUser, name='register'),
    path('user/current/', getLoggedInUserInfo, name='loggedInUserInfo'),
    path('user/rate/', rateUser, name='rateUser'),
    path('user/verify/', verify, name='verify'),
    path('user/verify/resend/', resendVerification, name='resendVerification'),
    path('user/password/recover/', forgotPassword, name='forgotPassword'),
    path('user/login/', userLogin, name='login'),
    path('user/logout/', userLogout, name='logout'),
    path('user/password/reset/', resetPassword, name='resetPassword'),
    path('user/image/', getPostUserImage, name="getPostUserImage"),
    path('item/', getPostItem, name='item'),
    path('item/delete/', deleteItem, name='deleteItem'),
    path('invoice/', getPostInvoice, name='invoice'),
    path('invoice/cart/', getPostCart, name='cart'),
    path('invoice/cart/submit/', submitCart, name='submit'),
    path('lineitem/dropoff/', putInLocker, name='dropoff'),
    path('lineitem/pickup/', pickUpItem, name='pickup'),
    path('lineitem/save/', toggleSave, name='save'),
    path('lineitem/submitted/', submittedLineItem, name='submittedLineItem'),
    path('lineitem/delete/', deleteLineItem, name='deleteLineItem'),
    path('notification/', getNotification, name='getNotification'),
    path('notification/delete/', deleteNotification, name='deleteNotification'),
    path('message/', getPostMessage, name='getPostMessage'),
]


# router = routers.DefaultRouter()
# router.register('api/user', UserViewSet, 'user')
# router.register('api/item', ItemViewSet, 'item')

# urlpatterns = router.urls

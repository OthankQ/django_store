from rest_framework import routers
from .api import UserViewSet, ItemViewSet

router = routers.DefaultRouter()
router.register('api/user', UserViewSet, 'user')
router.register('api/item', ItemViewSet, 'item')

urlpatterns = router.urls
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from WMS import views

router = DefaultRouter()
router.register('tags', views.TagViewSet)
router.register('categories', views.CategoryViewSet)
router.register('products', views.ProductViewSet)
router.register('deliveryorders', views.DeliveryOrderViewSet)
router.register('stocks', views.StockViewSet)

app_name = 'WMS'

urlpatterns = [
    path('', include(router.urls))
]

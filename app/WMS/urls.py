from django.urls import path, include
from rest_framework.routers import DefaultRouter

from WMS import views

router = DefaultRouter()
router.register('tags', views.TagViewSet)

app_name = 'WMS'

urlpatterns = [
    path('', include(router.urls))
]

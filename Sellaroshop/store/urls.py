from django.urls import path
from . import views

urlpatterns = [
    path('api/stores/', views.get_store_locations, name='store_locations'),
    path('api/stores/nearby/', views.find_nearby_stores, name='nearby_stores'),
    path('api/stores/<int:store_id>/', views.get_store_by_id, name='store_detail'),
]

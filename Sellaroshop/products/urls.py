from django.urls import path
from . import views

urlpatterns = [
    path('api/visual-search/', views.visual_search, name='visual_search'),
    path('api/extract-features/', views.extract_product_features, name='extract_features'),
    path('api/products/', views.get_products, name='get_products'),
]
